"""
src/komon/commands/advise.py のユーティリティ関数テスト

カバレッジ改善のため、簡単にテストできる関数をテストします。
"""

import unittest
from pathlib import Path
import tempfile
import os

from src.komon.commands.advise import (
    generate_progress_bar,
    get_skip_file_path,
    get_status_info,
    load_config
)


class TestAdviseUtils(unittest.TestCase):
    """advise.pyのユーティリティ関数テスト"""
    
    def test_generate_progress_bar_normal_values(self):
        """正常な値でのプログレスバー生成テスト"""
        # 0%
        result = generate_progress_bar(0, 10)
        self.assertEqual(result, "[░░░░░░░░░░]")
        
        # 50%
        result = generate_progress_bar(50, 10)
        self.assertEqual(result, "[█████░░░░░]")
        
        # 100%
        result = generate_progress_bar(100, 10)
        self.assertEqual(result, "[██████████]")
    
    def test_generate_progress_bar_edge_cases(self):
        """エッジケースでのプログレスバー生成テスト"""
        # 負の値
        result = generate_progress_bar(-10, 10)
        self.assertEqual(result, "[░░░░░░░░░░]")
        
        # 100%超過
        result = generate_progress_bar(150, 10)
        self.assertEqual(result, "[██████████]")
        
        # 小数点
        result = generate_progress_bar(33.3, 10)
        self.assertEqual(result, "[███░░░░░░░]")
    
    def test_generate_progress_bar_different_widths(self):
        """異なる幅でのプログレスバー生成テスト"""
        # 幅5
        result = generate_progress_bar(60, 5)
        self.assertEqual(result, "[███░░]")
        
        # 幅20
        result = generate_progress_bar(25, 20)
        self.assertEqual(result, "[█████░░░░░░░░░░░░░░░]")
    
    def test_get_skip_file_path(self):
        """スキップファイルパス取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            result = get_skip_file_path(config_dir)
            
            expected = config_dir / "data" / "komon_data" / "skip_advices.json"
            self.assertEqual(result, expected)
            
            # パスの型確認
            self.assertIsInstance(result, Path)
    
    def test_get_status_info_normal_thresholds(self):
        """正常な閾値でのステータス情報取得テスト"""
        thresholds = {"warning": 70, "alert": 85, "critical": 95}
        
        # 正常範囲
        icon, status = get_status_info(50, thresholds)
        self.assertEqual((icon, status), ("✅", "正常"))
        
        # 警告範囲
        icon, status = get_status_info(75, thresholds)
        self.assertEqual((icon, status), ("⚠️", "警告"))
        
        # 警戒範囲
        icon, status = get_status_info(90, thresholds)
        self.assertEqual((icon, status), ("⚠️", "警戒"))
        
        # 危険範囲
        icon, status = get_status_info(98, thresholds)
        self.assertEqual((icon, status), ("🔥", "危険"))
    
    def test_get_status_info_edge_cases(self):
        """エッジケースでのステータス情報取得テスト"""
        thresholds = {"warning": 80, "alert": 90, "critical": 95}
        
        # 境界値テスト
        icon, status = get_status_info(80, thresholds)  # 警告の境界
        self.assertEqual((icon, status), ("⚠️", "警告"))
        
        icon, status = get_status_info(90, thresholds)  # 警戒の境界
        self.assertEqual((icon, status), ("⚠️", "警戒"))
        
        icon, status = get_status_info(95, thresholds)  # 危険の境界
        self.assertEqual((icon, status), ("🔥", "危険"))
    
    def test_get_status_info_default_thresholds(self):
        """デフォルト閾値でのステータス情報取得テスト"""
        # 空の閾値辞書（デフォルト値を使用）
        thresholds = {}
        
        # デフォルト値: warning=80, alert=90, critical=95
        icon, status = get_status_info(70, thresholds)
        self.assertEqual((icon, status), ("✅", "正常"))
        
        icon, status = get_status_info(85, thresholds)
        self.assertEqual((icon, status), ("⚠️", "警告"))
        
        icon, status = get_status_info(92, thresholds)
        self.assertEqual((icon, status), ("⚠️", "警戒"))
        
        icon, status = get_status_info(97, thresholds)
        self.assertEqual((icon, status), ("🔥", "危険"))
    
    def test_load_config_with_valid_file(self):
        """有効な設定ファイルの読み込みテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            # テスト用設定ファイルを作成
            config_content = """
notifications:
  slack:
    enabled: true
    webhook_url: "test_url"
thresholds:
  cpu: 80
  mem: 85
"""
            config_file.write_text(config_content)
            
            # 設定読み込みテスト
            config = load_config(config_dir)
            
            self.assertIsInstance(config, dict)
            self.assertEqual(config["notifications"]["slack"]["enabled"], True)
            self.assertEqual(config["thresholds"]["cpu"], 80)
    
    def test_load_config_with_missing_file(self):
        """設定ファイルが存在しない場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # SystemExitが投げられることを確認
            with self.assertRaises(SystemExit):
                load_config(config_dir)
    
    def test_load_config_with_invalid_yaml(self):
        """無効なYAMLファイルの場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            # 無効なYAMLを作成
            config_file.write_text("invalid: yaml: content: [")
            
            # SystemExitが投げられることを確認
            with self.assertRaises(SystemExit):
                load_config(config_dir)


if __name__ == '__main__':
    unittest.main()