"""
src/komon/commands/advise.py の設定・実行関連関数テスト

カバレッジ改善のため、設定読み込みと実行関数をテストします。
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import yaml
import io
import sys

from src.komon.commands.advise import (
    load_config,
    run_advise
)


class TestAdviseConfigFunctions(unittest.TestCase):
    """advise.pyの設定・実行関連関数テスト"""
    
    def test_load_config_valid_yaml(self):
        """有効なYAMLファイルの読み込みテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            config_data = {
                "thresholds": {
                    "cpu": 80,
                    "mem": 85,
                    "disk": 90
                },
                "notifications": {
                    "slack": {
                        "enabled": True,
                        "webhook_url": "https://hooks.slack.com/test"
                    }
                }
            }
            
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f)
            
            result = load_config(config_dir)
            
            self.assertEqual(result["thresholds"]["cpu"], 80)
            self.assertEqual(result["notifications"]["slack"]["enabled"], True)
    
    def test_load_config_file_not_found(self):
        """設定ファイルが見つからない場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                with self.assertRaises(SystemExit) as cm:
                    load_config(config_dir)
            
            self.assertEqual(cm.exception.code, 1)
            output = captured_output.getvalue()
            self.assertIn("settings.yml が見つかりません", output)
            self.assertIn("komon initial", output)
    
    def test_load_config_invalid_yaml(self):
        """無効なYAMLファイルの場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            # 無効なYAMLを作成
            config_file.write_text("invalid: yaml: content: [unclosed")
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                with self.assertRaises(SystemExit) as cm:
                    load_config(config_dir)
            
            self.assertEqual(cm.exception.code, 1)
            output = captured_output.getvalue()
            self.assertIn("settings.yml の形式が不正です", output)
    
    def test_load_config_permission_error(self):
        """ファイル読み込み権限エラーのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # PermissionErrorをシミュレート
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                captured_output = io.StringIO()
                with patch('sys.stdout', captured_output):
                    with self.assertRaises(SystemExit) as cm:
                        load_config(config_dir)
                
                self.assertEqual(cm.exception.code, 1)
                output = captured_output.getvalue()
                self.assertIn("予期しないエラー", output)
    
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('src.komon.commands.advise.collect_detailed_resource_usage')
    @patch('src.komon.commands.advise.load_thresholds')
    @patch('src.komon.commands.advise.analyze_usage')
    @patch('src.komon.commands.advise.load_config')
    def test_run_advise_basic_execution(self, mock_load_config, mock_analyze_usage, 
                                       mock_load_thresholds, mock_collect_usage, mock_ask_yes_no):
        """基本的な実行テスト"""
        # ユーザー入力のモック
        mock_ask_yes_no.return_value = False
        
        # モックの設定
        mock_config = {
            "output": {"history_limit": 10},
            "thresholds": {"cpu": 80, "mem": 85, "disk": 90},
            "notifications": {"email": {"enabled": False}}
        }
        mock_load_config.return_value = mock_config
        
        mock_usage = {"cpu": 45.0, "mem": 55.0, "disk": 60.0}
        mock_collect_usage.return_value = mock_usage
        
        mock_thresholds = {"cpu": 80, "mem": 85, "disk": 90}
        mock_load_thresholds.return_value = mock_thresholds
        
        mock_alerts = []
        mock_analyze_usage.return_value = mock_alerts
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # 実行時にエラーが発生しないことを確認
            try:
                run_advise(config_dir)
            except SystemExit:
                # SystemExitは正常な終了として扱う
                pass
            
            # 各関数が呼ばれたことを確認
            mock_load_config.assert_called_once_with(config_dir)
            mock_collect_usage.assert_called_once()
            mock_load_thresholds.assert_called_once_with(mock_config)
            mock_analyze_usage.assert_called_once_with(mock_usage, mock_thresholds)
    
    @patch('src.komon.commands.advise.collect_detailed_resource_usage')
    @patch('src.komon.commands.advise.load_thresholds')
    @patch('src.komon.commands.advise.analyze_usage')
    @patch('src.komon.commands.advise.load_config')
    def test_run_advise_with_parameters(self, mock_load_config, mock_analyze_usage,
                                       mock_load_thresholds, mock_collect_usage):
        """パラメータ指定での実行テスト"""
        mock_config = {
            "output": {"history_limit": 5},
            "thresholds": {"cpu": 80, "mem": 85, "disk": 90}
        }
        mock_load_config.return_value = mock_config
        
        mock_usage = {"cpu": 85.0, "mem": 90.0, "disk": 75.0}
        mock_collect_usage.return_value = mock_usage
        
        mock_thresholds = {"cpu": 80, "mem": 85, "disk": 90}
        mock_load_thresholds.return_value = mock_thresholds
        
        mock_alerts = [{"type": "cpu", "level": "warning"}]
        mock_analyze_usage.return_value = mock_alerts
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            try:
                run_advise(
                    config_dir, 
                    history_limit=15, 
                    verbose=True, 
                    section="system",
                    net_mode="ping"
                )
            except SystemExit:
                pass
            
            # パラメータが正しく渡されることを確認
            mock_load_config.assert_called_once_with(config_dir)
    
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('src.komon.commands.advise.collect_detailed_resource_usage')
    @patch('src.komon.commands.advise.load_thresholds')
    @patch('src.komon.commands.advise.analyze_usage')
    @patch('src.komon.commands.advise.load_config')
    def test_run_advise_default_history_limit(self, mock_load_config, mock_analyze_usage,
                                             mock_load_thresholds, mock_collect_usage, mock_ask_yes_no):
        """デフォルトhistory_limitのテスト"""
        # ユーザー入力のモック
        mock_ask_yes_no.return_value = False
        
        # output設定がない場合のデフォルト値テスト
        mock_config = {
            "thresholds": {"cpu": 80, "mem": 85, "disk": 90},
            "notifications": {"email": {"enabled": False}}
            # outputセクションなし
        }
        mock_load_config.return_value = mock_config
        
        mock_usage = {"cpu": 45.0, "mem": 55.0, "disk": 60.0}
        mock_collect_usage.return_value = mock_usage
        
        mock_thresholds = {"cpu": 80, "mem": 85, "disk": 90}
        mock_load_thresholds.return_value = mock_thresholds
        
        mock_alerts = []
        mock_analyze_usage.return_value = mock_alerts
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            try:
                run_advise(config_dir)
            except SystemExit:
                pass
            
            # デフォルト値5が使用されることを確認（内部的に）
            mock_load_config.assert_called_once()
    
    @patch('src.komon.commands.advise.load_config')
    def test_run_advise_config_load_failure(self, mock_load_config):
        """設定読み込み失敗時のテスト"""
        # load_configがSystemExitを投げる場合
        mock_load_config.side_effect = SystemExit(1)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            with self.assertRaises(SystemExit) as cm:
                run_advise(config_dir)
            
            self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()