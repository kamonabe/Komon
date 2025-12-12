"""
src/komon/commands/advise.py のメイン関数テスト

カバレッジ改善のため、主要な関数をテストします。
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import tempfile
import json
import datetime
import io
import sys

from src.komon.commands.advise import (
    display_system_status,
    ask_yes_no,
    should_skip,
    record_skip,
    skippable_advice,
    advise_os_update
)


class TestAdviseMainFunctions(unittest.TestCase):
    """advise.pyのメイン関数テスト"""
    
    def test_display_system_status_normal_usage(self):
        """正常なシステム状態表示テスト"""
        usage = {
            "cpu": 45.5,
            "mem": 62.3,
            "disk": 78.9,
            "cpu_by_process": [
                {"name": "python", "cpu": 15.2},
                {"name": "chrome", "cpu": 8.1},
                {"name": "code", "cpu": 5.3}
            ],
            "mem_by_process": [
                {"name": "chrome", "mem": 512},
                {"name": "python", "mem": 256},
                {"name": "code", "mem": 128}
            ]
        }
        
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 75, "alert": 90, "critical": 95},
            "disk": {"warning": 80, "alert": 90, "critical": 95}
        }
        
        # 標準出力をキャプチャ
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            display_system_status(usage, thresholds)
        
        output = captured_output.getvalue()
        
        # 基本的な出力内容を確認
        self.assertIn("📊 現在のシステム状態", output)
        self.assertIn("CPU:", output)
        self.assertIn("メモリ:", output)
        self.assertIn("ディスク:", output)
        self.assertIn("45.5%", output)  # CPU使用率
        self.assertIn("62.3%", output)  # メモリ使用率
        self.assertIn("78.9%", output)  # ディスク使用率
    
    def test_display_system_status_high_usage_verbose(self):
        """高使用率時の詳細表示テスト"""
        usage = {
            "cpu": 85.0,  # 警告レベル超過
            "mem": 92.0,  # 警告レベル超過
            "disk": 65.0,
            "cpu_by_process": [
                {"name": "heavy_process", "cpu": 45.0},
                {"name": "medium_process", "cpu": 25.0}
            ],
            "mem_by_process": [
                {"name": "memory_hog", "mem": 1024},
                {"name": "normal_app", "mem": 512}
            ]
        }
        
        thresholds = {
            "cpu": 80,  # 単純な数値形式
            "mem": 80,
            "disk": 80
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            display_system_status(usage, thresholds, verbose=True)
        
        output = captured_output.getvalue()
        
        # 詳細情報が表示されることを確認
        self.assertIn("📌 上位プロセス:", output)
        self.assertIn("CPU:", output)
        self.assertIn("メモリ:", output)
        self.assertIn("heavy_process", output)
        self.assertIn("memory_hog", output)
    
    @patch('builtins.input')
    def test_ask_yes_no_yes_responses(self, mock_input):
        """yes応答のテスト"""
        # 様々なyes応答をテスト
        test_cases = ["y", "yes", "Y", "YES"]
        
        for response in test_cases:
            with self.subTest(response=response):
                mock_input.return_value = response
                result = ask_yes_no("テスト質問")
                self.assertTrue(result)
    
    @patch('builtins.input')
    def test_ask_yes_no_no_responses(self, mock_input):
        """no応答のテスト"""
        test_cases = ["n", "no", "N", "NO"]
        
        for response in test_cases:
            with self.subTest(response=response):
                mock_input.return_value = response
                result = ask_yes_no("テスト質問")
                self.assertFalse(result)
    
    @patch('builtins.input')
    def test_ask_yes_no_invalid_then_valid(self, mock_input):
        """無効な入力後に有効な入力のテスト"""
        # 最初に無効な入力、次にyを入力
        mock_input.side_effect = ["invalid", "maybe", "y"]
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = ask_yes_no("テスト質問")
        
        self.assertTrue(result)
        output = captured_output.getvalue()
        # エラーメッセージが2回表示されることを確認
        self.assertEqual(output.count("→ y または n で答えてください。"), 2)
    
    def test_should_skip_no_file(self):
        """スキップファイルが存在しない場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            result = should_skip("test_key", config_dir)
            self.assertFalse(result)
    
    def test_should_skip_within_period(self):
        """スキップ期間内のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            skip_file = config_dir / "data" / "komon_data" / "skip_advices.json"
            skip_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 2日前にスキップした記録を作成
            skip_data = {
                "test_key": {
                    "skipped_at": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat()
                }
            }
            
            with open(skip_file, "w", encoding="utf-8") as f:
                json.dump(skip_data, f)
            
            # 7日以内なのでTrueが返される
            result = should_skip("test_key", config_dir, days=7)
            self.assertTrue(result)
    
    def test_should_skip_outside_period(self):
        """スキップ期間外のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            skip_file = config_dir / "data" / "komon_data" / "skip_advices.json"
            skip_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 10日前にスキップした記録を作成
            skip_data = {
                "test_key": {
                    "skipped_at": (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()
                }
            }
            
            with open(skip_file, "w", encoding="utf-8") as f:
                json.dump(skip_data, f)
            
            # 7日を超えているのでFalseが返される
            result = should_skip("test_key", config_dir, days=7)
            self.assertFalse(result)
    
    def test_should_skip_corrupted_file(self):
        """破損したスキップファイルのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            skip_file = config_dir / "data" / "komon_data" / "skip_advices.json"
            skip_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 無効なJSONを作成
            skip_file.write_text("invalid json content")
            
            # 例外が発生してもFalseが返される
            result = should_skip("test_key", config_dir)
            self.assertFalse(result)
    
    def test_record_skip_new_file(self):
        """新しいスキップファイルの作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            record_skip("test_key", config_dir)
            
            skip_file = config_dir / "data" / "komon_data" / "skip_advices.json"
            self.assertTrue(skip_file.exists())
            
            with open(skip_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.assertIn("test_key", data)
            self.assertIn("skipped_at", data["test_key"])
    
    def test_record_skip_existing_file(self):
        """既存のスキップファイルへの追記テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            skip_file = config_dir / "data" / "komon_data" / "skip_advices.json"
            skip_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 既存データを作成
            existing_data = {
                "existing_key": {
                    "skipped_at": "2023-01-01T00:00:00"
                }
            }
            
            with open(skip_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f)
            
            # 新しいキーを追加
            record_skip("new_key", config_dir)
            
            with open(skip_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 既存データと新しいデータの両方が存在することを確認
            self.assertIn("existing_key", data)
            self.assertIn("new_key", data)
    
    @patch('builtins.input')
    def test_skippable_advice_already_skipped(self, mock_input):
        """既にスキップされたアドバイスのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # スキップ記録を作成
            record_skip("test_advice", config_dir)
            
            # アクション関数のモック
            mock_action = MagicMock()
            
            # スキップ済みなので何も実行されない
            skippable_advice("test_advice", "実行しますか？", mock_action, config_dir)
            
            # inputが呼ばれず、actionも実行されない
            mock_input.assert_not_called()
            mock_action.assert_not_called()
    
    @patch('builtins.input')
    def test_skippable_advice_user_accepts(self, mock_input):
        """ユーザーがアドバイスを受け入れるテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            mock_input.return_value = "y"
            
            mock_action = MagicMock()
            
            skippable_advice("new_advice", "実行しますか？", mock_action, config_dir)
            
            # アクションが実行される
            mock_action.assert_called_once()
    
    @patch('builtins.input')
    def test_skippable_advice_user_declines(self, mock_input):
        """ユーザーがアドバイスを拒否するテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            mock_input.return_value = "n"
            
            mock_action = MagicMock()
            
            skippable_advice("decline_advice", "実行しますか？", mock_action, config_dir)
            
            # アクションは実行されず、スキップが記録される
            mock_action.assert_not_called()
            
            # スキップが記録されたことを確認
            result = should_skip("decline_advice", config_dir)
            self.assertTrue(result)
    
    @patch('src.komon.commands.advise.subprocess.run')
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('src.komon.commands.advise.get_os_detector')
    def test_advise_os_update_rhel_security(self, mock_get_detector, mock_ask_yes_no, mock_subprocess):
        """RHEL系でのセキュリティ更新アドバイステスト"""
        # OS検出器のモック設定
        mock_detector = MagicMock()
        mock_detector.should_show_package_advice.return_value = True
        mock_detector.detect_os_family.return_value = "rhel"
        mock_get_detector.return_value = mock_detector
        
        # subprocess.runのモック設定
        mock_result = MagicMock()
        mock_result.stdout = "RHSA-2023:1234: Important: security update\nRHSA-2023:5678: Critical: security update"
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # ユーザー入力のモック
        mock_ask_yes_no.return_value = False
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_os_update()
        
        output = captured_output.getvalue()
        
        # セキュリティ更新のアドバイスが表示されることを確認
        self.assertIn("① セキュリティパッチの確認", output)
        self.assertIn("セキュリティ更新が", output)
    
    @patch('src.komon.commands.advise.subprocess.run')
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('src.komon.commands.advise.get_os_detector')
    def test_advise_os_update_with_config(self, mock_get_detector, mock_ask_yes_no, mock_subprocess):
        """設定ありでのOS更新アドバイステスト"""
        mock_detector = MagicMock()
        mock_detector.should_show_package_advice.return_value = True
        mock_detector.detect_os_family.return_value = "debian"
        mock_get_detector.return_value = mock_detector
        
        # ユーザー入力のモック
        mock_ask_yes_no.return_value = False
        
        config = {
            "os_detection": {
                "package_advice": True
            }
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_os_update(config)
        
        output = captured_output.getvalue()
        
        # パッケージ更新のアドバイスが表示されることを確認
        self.assertIn("① パッケージ更新の確認", output)
        self.assertIn("Debian系Linux", output)
    
    @patch('src.komon.commands.advise.get_os_detector')
    def test_advise_os_update_suppressed(self, mock_get_detector):
        """OS更新アドバイスが抑制される場合のテスト"""
        mock_detector = MagicMock()
        mock_detector.should_show_package_advice.return_value = False
        mock_detector.detect_os_family.return_value = "unknown"
        mock_detector.get_package_manager_command.return_value = "package-manager update"
        mock_get_detector.return_value = mock_detector
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_os_update()
        
        output = captured_output.getvalue()
        
        # 抑制されたアドバイスが表示されることを確認
        self.assertIn("① パッケージ更新の確認", output)
        self.assertIn("OSファミリが不明なため", output)


if __name__ == '__main__':
    unittest.main()