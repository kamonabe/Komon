"""
src/komon/commands/status.py のテスト

ステータスコマンドの関数をテストします。
"""

import unittest
import tempfile
import io
import yaml
from unittest.mock import patch, mock_open
from pathlib import Path
from io import StringIO

from src.komon.commands.status import (
    load_config,
    run_status
)


class TestStatusCommands(unittest.TestCase):
    """status.pyの関数テスト"""
    
    def test_load_config_with_valid_file(self):
        """有効な設定ファイルの読み込みテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            # テスト用設定ファイルを作成
            config_content = {
                'thresholds': {
                    'cpu': 80,
                    'mem': 85,
                    'disk': 90
                },
                'notifications': {
                    'slack': {
                        'enabled': True,
                        'webhook_url': 'test_url'
                    }
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_content, f)
            
            # 設定読み込みテスト
            config = load_config(config_dir)
            
            self.assertIsInstance(config, dict)
            self.assertEqual(config['thresholds']['cpu'], 80)
            self.assertEqual(config['notifications']['slack']['enabled'], True)
    
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
            
            # SystemExitが発生することを確認
            with self.assertRaises(SystemExit):
                load_config(config_dir)
    
    def test_load_config_empty_file(self):
        """空のファイルの場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            # 空のファイルを作成
            config_file.write_text("")
            
            # 空の設定が返されることを確認
            config = load_config(config_dir)
            self.assertIsNone(config)  # yaml.safe_load("")はNoneを返す


    def test_load_config_empty_file_duplicate(self):
        """空のファイルの場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            # 空のファイルを作成
            config_file.write_text("")
            
            result = load_config(config_dir)
            self.assertIsNone(result)

    @patch('src.komon.commands.status.collect_resource_usage')
    @patch('src.komon.commands.status.load_thresholds')
    def test_run_status_full_config(self, mock_load_thresholds, mock_collect_resource_usage):
        """完全な設定でのステータス表示テスト"""
        # モックの設定
        mock_collect_resource_usage.return_value = {
            "cpu": 45.2,
            "mem": 67.8,
            "disk": 23.1
        }
        mock_load_thresholds.return_value = {
            "cpu": 80,
            "mem": 85,
            "disk": 90
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            # 完全な設定ファイルを作成
            config = {
                "notifications": {
                    "slack": {"enabled": True},
                    "email": {"enabled": False}
                },
                "log_monitor_targets": {
                    "/var/log/syslog": True,
                    "/var/log/auth.log": False
                }
            }
            
            with open(config_file, "w") as f:
                yaml.dump(config, f)
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                run_status(config_dir)
            
            output = captured_output.getvalue()
            
            # リソース使用率の表示を確認
            self.assertIn("CPU: 45.2%", output)
            self.assertIn("MEM: 67.8%", output)
            self.assertIn("DISK: 23.1%", output)
            
            # 通知設定の表示を確認
            self.assertIn("Slack通知: 有効", output)
            self.assertIn("メール通知: 無効", output)
            
            # ログ監視対象の表示を確認
            self.assertIn("/var/log/syslog: ✅ 有効", output)
            self.assertIn("/var/log/auth.log: ❌ 無効", output)

    @patch('src.komon.commands.status.collect_resource_usage')
    @patch('src.komon.commands.status.load_thresholds')
    def test_run_status_minimal_config(self, mock_load_thresholds, mock_collect_resource_usage):
        """最小限の設定でのステータス表示テスト"""
        # モックの設定
        mock_collect_resource_usage.return_value = {
            "cpu": 10.0,
            "mem": 20.0,
            "disk": 30.0
        }
        mock_load_thresholds.return_value = {
            "cpu": 70,
            "mem": 80,
            "disk": 90
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            # 最小限の設定ファイルを作成
            config = {}
            
            with open(config_file, "w") as f:
                yaml.dump(config, f)
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                run_status(config_dir)
            
            output = captured_output.getvalue()
            
            # リソース使用率の表示を確認
            self.assertIn("CPU: 10.0%", output)
            self.assertIn("MEM: 20.0%", output)
            self.assertIn("DISK: 30.0%", output)
            
            # 通知設定の表示を確認（デフォルト値）
            self.assertIn("Slack通知: 無効", output)
            self.assertIn("メール通知: 無効", output)
            
            # ログ監視対象の表示を確認（なし）
            self.assertIn("監視対象なし", output)

    @patch('src.komon.commands.status.collect_resource_usage')
    @patch('src.komon.commands.status.load_thresholds')
    def test_run_status_no_log_targets(self, mock_load_thresholds, mock_collect_resource_usage):
        """ログ監視対象がない場合のテスト"""
        # モックの設定
        mock_collect_resource_usage.return_value = {
            "cpu": 15.5,
            "mem": 25.3,
            "disk": 35.7
        }
        mock_load_thresholds.return_value = {
            "cpu": 75,
            "mem": 85,
            "disk": 95
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            # ログ監視対象が空の設定ファイルを作成
            config = {
                "notifications": {
                    "slack": {"enabled": False},
                    "email": {"enabled": True}
                },
                "log_monitor_targets": {}
            }
            
            with open(config_file, "w") as f:
                yaml.dump(config, f)
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                run_status(config_dir)
            
            output = captured_output.getvalue()
            
            # 通知設定の表示を確認
            self.assertIn("Slack通知: 無効", output)
            self.assertIn("メール通知: 有効", output)
            
            # ログ監視対象の表示を確認
            self.assertIn("監視対象なし", output)

    def test_load_config_exception_handling(self):
        """予期しない例外の処理テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # 存在しないディレクトリを指定してSystemExitが発生することを確認
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with self.assertRaises(SystemExit):
                    load_config(config_dir)

    @patch('src.komon.commands.status.collect_resource_usage')
    @patch('src.komon.commands.status.load_thresholds')
    def test_run_status_header_display(self, mock_load_thresholds, mock_collect_resource_usage):
        """ステータス表示のヘッダーテスト"""
        # モックの設定
        mock_collect_resource_usage.return_value = {"cpu": 0, "mem": 0, "disk": 0}
        mock_load_thresholds.return_value = {"cpu": 80, "mem": 80, "disk": 80}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "settings.yml"
            
            config = {}
            with open(config_file, "w") as f:
                yaml.dump(config, f)
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                run_status(config_dir)
            
            output = captured_output.getvalue()
            
            # ヘッダーとセクションの表示を確認
            self.assertIn("📊 Komon ステータス", output)
            self.assertIn("【リソース使用率】", output)
            self.assertIn("【通知設定】", output)
            self.assertIn("【ログ監視対象】", output)


if __name__ == '__main__':
    unittest.main()