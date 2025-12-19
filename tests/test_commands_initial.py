"""
src/komon/commands/initial.py のテスト

初期セットアップコマンドのユーティリティ関数をテストします。
"""

import unittest
import tempfile
import io
import subprocess
import yaml
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from io import StringIO

from src.komon.commands.initial import (
    get_input,
    run_initial_setup
)


class TestInitialCommands(unittest.TestCase):
    """initial.pyのユーティリティ関数テスト"""
    
    @patch('builtins.input')
    def test_get_input_default_string(self, mock_input):
        """デフォルト値（文字列）のテスト"""
        mock_input.return_value = ""
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = get_input("テスト項目", "default_value", "str")
        
        self.assertEqual(result, "default_value")
        output = captured_output.getvalue()
        self.assertIn("default_value のまま（デフォルト）", output)
    
    @patch('builtins.input')
    def test_get_input_custom_string(self, mock_input):
        """カスタム値（文字列）のテスト"""
        mock_input.return_value = "custom_value"
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = get_input("テスト項目", "default_value", "str")
        
        self.assertEqual(result, "custom_value")
        output = captured_output.getvalue()
        self.assertIn("custom_value に設定しました", output)
    
    @patch('builtins.input')
    def test_get_input_default_int(self, mock_input):
        """デフォルト値（整数）のテスト"""
        mock_input.return_value = ""
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = get_input("テスト項目", 80, "int")
        
        self.assertEqual(result, 80)
        output = captured_output.getvalue()
        self.assertIn("80 のまま（デフォルト）", output)
    
    @patch('builtins.input')
    def test_get_input_custom_int(self, mock_input):
        """カスタム値（整数）のテスト"""
        mock_input.return_value = "90"
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = get_input("テスト項目", 80, "int")
        
        self.assertEqual(result, 90)
        output = captured_output.getvalue()
        self.assertIn("90 に設定しました", output)
    
    @patch('builtins.input')
    def test_get_input_invalid_int(self, mock_input):
        """無効な整数入力のテスト"""
        mock_input.return_value = "invalid"
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = get_input("テスト項目", 80, "int")
        
        self.assertEqual(result, 80)  # デフォルト値が返される
        output = captured_output.getvalue()
        self.assertIn("入力形式が正しくありません", output)
    
    @patch('builtins.input')
    def test_get_input_default_bool(self, mock_input):
        """デフォルト値（真偽値）のテスト"""
        mock_input.return_value = ""
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = get_input("テスト項目", True, "bool")
        
        self.assertEqual(result, True)
        output = captured_output.getvalue()
        self.assertIn("True のまま（デフォルト）", output)
    
    @patch('builtins.input')
    def test_get_input_bool_true_values(self, mock_input):
        """真偽値の真値のテスト"""
        true_values = ["true", "yes", "y", "1", "TRUE", "YES"]
        
        for value in true_values:
            with self.subTest(value=value):
                mock_input.return_value = value
                
                captured_output = io.StringIO()
                with patch('sys.stdout', captured_output):
                    result = get_input("テスト項目", False, "bool")
                
                self.assertEqual(result, True)
    
    @patch('builtins.input')
    def test_get_input_bool_false_values(self, mock_input):
        """真偽値の偽値のテスト"""
        false_values = ["false", "no", "n", "0", "FALSE", "NO"]
        
        for value in false_values:
            with self.subTest(value=value):
                mock_input.return_value = value
                
                captured_output = io.StringIO()
                with patch('sys.stdout', captured_output):
                    result = get_input("テスト項目", True, "bool")
                
                self.assertEqual(result, False)
    
    @patch('builtins.input')
    def test_get_input_invalid_bool(self, mock_input):
        """無効な真偽値入力のテスト"""
        mock_input.return_value = "invalid"
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = get_input("テスト項目", True, "bool")
        
        self.assertEqual(result, False)  # 無効な値はFalseになる
        output = captured_output.getvalue()
        self.assertIn("False に設定しました", output)

    @patch('builtins.input')
    def test_run_initial_setup_existing_file(self, mock_input):
        """既存のsettings.ymlがある場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            settings_file = config_dir / "settings.yml"
            
            # 既存ファイルを作成
            settings_file.write_text("existing: config")
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                run_initial_setup(config_dir)
            
            output = captured_output.getvalue()
            self.assertIn("すでに存在します", output)
            self.assertIn("スキップされました", output)
            
            # inputが呼ばれないことを確認
            mock_input.assert_not_called()

    @patch('builtins.input')
    @patch('subprocess.run')
    def test_run_initial_setup_sample_not_found(self, mock_subprocess, mock_input):
        """settings.yml.sampleが見つからない場合のテスト"""
        # subprocess.runが空の結果を返すようにモック
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = ""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # Path.existsをモックして、すべてのパスでFalseを返す
            with patch('pathlib.Path.exists', return_value=False):
                captured_output = io.StringIO()
                with patch('sys.stdout', captured_output):
                    run_initial_setup(config_dir)
            
            output = captured_output.getvalue()
            self.assertIn("settings.yml.sample が見つかりません", output)
            
            # inputが呼ばれないことを確認
            mock_input.assert_not_called()

    @patch('builtins.input')
    def test_run_initial_setup_full_workflow(self, mock_input):
        """完全なセットアップワークフローのテスト"""
        # ユーザー入力をモック
        mock_input.side_effect = [
            "true",  # Slack enabled
            "https://hooks.slack.com/test",  # Slack webhook
            "false",  # Email disabled
            "true",  # Network check enabled
            "true",  # Throttle enabled
            "true",  # Progressive notification enabled
            "true",  # Contextual advice enabled
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # サンプル設定ファイルを実際に作成
            sample_config = {
                "notifications": {
                    "slack": {
                        "enabled": False,
                        "webhook_url": "YOUR_SLACK_WEBHOOK_URL"
                    },
                    "email": {
                        "enabled": False,
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "from": "your-email@example.com",
                        "to": "admin@example.com"
                    }
                },
                "network_check": {
                    "enabled": False
                },
                "throttle": {
                    "enabled": True
                },
                "progressive_notification": {
                    "enabled": True
                },
                "contextual_advice": {
                    "enabled": True
                }
            }
            
            # 既存のconfig/settings.yml.sampleをバックアップ
            sample_file = Path("config/settings.yml.sample")
            backup_content = None
            if sample_file.exists():
                with open(sample_file, "r") as f:
                    backup_content = f.read()
            
            # テスト用の設定でファイルを上書き
            sample_file.parent.mkdir(parents=True, exist_ok=True)
            with open(sample_file, "w") as f:
                yaml.dump(sample_config, f)
            
            try:
                captured_output = io.StringIO()
                with patch('sys.stdout', captured_output):
                    run_initial_setup(config_dir)
                
                output = captured_output.getvalue()
                self.assertIn("初期設定を開始します", output)
                self.assertIn("を作成しました", output)
                
                # 作成されたファイルを確認
                settings_file = config_dir / "settings.yml"
                self.assertTrue(settings_file.exists())
                
                with open(settings_file) as f:
                    created_config = yaml.safe_load(f)
                
                # 設定が正しく反映されていることを確認
                self.assertTrue(created_config["notifications"]["slack"]["enabled"])
                self.assertEqual(created_config["notifications"]["slack"]["webhook_url"], "https://hooks.slack.com/test")
                self.assertFalse(created_config["notifications"]["email"]["enabled"])
            
            finally:
                # 元のファイルを復元
                if backup_content is not None:
                    with open(sample_file, "w") as f:
                        f.write(backup_content)
                elif sample_file.exists():
                    sample_file.unlink()
                    # 空のディレクトリも削除
                    if sample_file.parent.exists() and not any(sample_file.parent.iterdir()):
                        sample_file.parent.rmdir()

    def test_get_input_type_conversion(self):
        """型変換のテスト"""
        with patch('builtins.input', return_value="42"):
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                result = get_input("テスト項目", 10, "int")
            
            self.assertEqual(result, 42)
            self.assertIsInstance(result, int)


if __name__ == '__main__':
    unittest.main()