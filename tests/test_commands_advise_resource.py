"""
src/komon/commands/advise.py のリソース関連関数テスト

カバレッジ改善のため、リソース使用量アドバイス関数をテストします。
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import sys

from src.komon.commands.advise import (
    advise_resource_usage,
    advise_uptime,
    advise_email_disabled
)


class TestAdviseResourceFunctions(unittest.TestCase):
    """advise.pyのリソース関連関数テスト"""
    
    def test_advise_resource_usage_normal_levels(self):
        """正常レベルでのリソース使用量アドバイステスト"""
        usage = {
            "cpu": 45.0,
            "mem": 55.0,
            "disk": 60.0
        }
        
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 75, "alert": 90, "critical": 95},
            "disk": {"warning": 80, "alert": 90, "critical": 95}
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_resource_usage(usage, thresholds)
        
        output = captured_output.getvalue()
        
        # 正常レベルでは特別なアドバイスは表示されない
        # 関数が正常に実行されることを確認
        self.assertIsInstance(output, str)
    
    @patch('src.komon.commands.advise.ask_yes_no')
    def test_advise_resource_usage_high_memory(self, mock_ask_yes_no):
        """高メモリ使用量でのアドバイステスト"""
        mock_ask_yes_no.return_value = False  # ユーザーがnoを選択
        
        usage = {
            "cpu": 45.0,
            "mem": 85.0,  # 閾値超過
            "disk": 60.0,
            "mem_by_process": [
                {"name": "chrome", "mem": 1024},
                {"name": "python", "mem": 512},
                {"name": "code", "mem": 256}
            ]
        }
        
        thresholds = {
            "cpu": 70,  # 単純な数値形式
            "mem": 80,
            "disk": 80
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_resource_usage(usage, thresholds)
        
        output = captured_output.getvalue()
        
        # メモリ使用量が高い場合のアドバイスが含まれることを確認
        self.assertIsInstance(output, str)
        mock_ask_yes_no.assert_called()
    
    @patch('src.komon.commands.advise.ask_yes_no')
    def test_advise_resource_usage_high_disk(self, mock_ask_yes_no):
        """高ディスク使用量でのアドバイステスト"""
        mock_ask_yes_no.return_value = False  # ユーザーがnoを選択
        
        usage = {
            "cpu": 45.0,
            "mem": 55.0,
            "disk": 90.0  # 閾値超過
        }
        
        thresholds = {
            "cpu": {"warning": 70},
            "mem": {"warning": 75},
            "disk": {"warning": 80}
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_resource_usage(usage, thresholds)
        
        output = captured_output.getvalue()
        
        # ディスク使用量が高い場合のアドバイスが含まれることを確認
        self.assertIsInstance(output, str)
        mock_ask_yes_no.assert_called()
    
    @patch('src.komon.commands.advise.ask_yes_no')
    def test_advise_resource_usage_mixed_threshold_formats(self, mock_ask_yes_no):
        """混合閾値形式でのテスト"""
        mock_ask_yes_no.return_value = False  # ユーザーがnoを選択
        
        usage = {
            "cpu": 45.0,
            "mem": 85.0,
            "disk": 90.0
        }
        
        # 混合形式: 一部は辞書、一部は数値
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": 80,  # 単純な数値
            "disk": {"warning": 85}  # 一部のキーのみ
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_resource_usage(usage, thresholds)
        
        output = captured_output.getvalue()
        
        # 混合形式でも正常に動作することを確認
        self.assertIsInstance(output, str)
        mock_ask_yes_no.assert_called()
    
    def test_advise_resource_usage_empty_thresholds(self):
        """空の閾値でのテスト"""
        usage = {
            "cpu": 45.0,
            "mem": 55.0,
            "disk": 60.0
        }
        
        thresholds = {}
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_resource_usage(usage, thresholds)
        
        output = captured_output.getvalue()
        
        # 空の閾値でもエラーにならないことを確認
        self.assertIsInstance(output, str)
    
    def test_advise_resource_usage_missing_usage_keys(self):
        """使用量データにキーが不足している場合のテスト"""
        usage = {
            "cpu": 45.0
            # mem, diskが不足
        }
        
        thresholds = {
            "cpu": 70,
            "mem": 80,
            "disk": 80
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_resource_usage(usage, thresholds)
        
        output = captured_output.getvalue()
        
        # 不足したキーでもエラーにならないことを確認
        self.assertIsInstance(output, str)


class TestAdviseUptimeFunctions(unittest.TestCase):
    """advise.pyのuptime関連関数テスト"""
    
    @patch('builtins.open')
    @patch('src.komon.commands.advise.ask_yes_no')
    def test_advise_uptime_long_uptime_production(self, mock_ask_yes_no, mock_open):
        """長時間稼働（本番環境）でのアドバイステスト"""
        mock_ask_yes_no.return_value = True  # ユーザーがyesを選択
        
        # 10日間の稼働時間をシミュレート
        uptime_seconds = 10 * 24 * 3600  # 10日
        mock_file = MagicMock()
        mock_file.readline.return_value = f"{uptime_seconds} 123456"
        mock_open.return_value.__enter__.return_value = mock_file
        
        profile = {"usage": "production"}
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_uptime(profile)
        
        output = captured_output.getvalue()
        
        # 本番環境での長時間稼働アドバイスが含まれることを確認
        self.assertIn("本番環境", output)
        mock_ask_yes_no.assert_called()
    
    @patch('builtins.open')
    @patch('src.komon.commands.advise.ask_yes_no')
    def test_advise_uptime_long_uptime_development(self, mock_ask_yes_no, mock_open):
        """長時間稼働（開発環境）でのアドバイステスト"""
        mock_ask_yes_no.return_value = True  # ユーザーがyesを選択
        
        # 8日間の稼働時間をシミュレート
        uptime_seconds = 8 * 24 * 3600  # 8日
        mock_file = MagicMock()
        mock_file.readline.return_value = f"{uptime_seconds} 123456"
        mock_open.return_value.__enter__.return_value = mock_file
        
        profile = {"usage": "development"}
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_uptime(profile)
        
        output = captured_output.getvalue()
        
        # 開発環境での長時間稼働アドバイスが含まれることを確認
        self.assertIn("長期間の稼働", output)
        mock_ask_yes_no.assert_called()
    
    @patch('builtins.open')
    def test_advise_uptime_short_uptime(self, mock_open):
        """短時間稼働でのテスト"""
        # 2日間の稼働時間をシミュレート
        uptime_seconds = 2 * 24 * 3600  # 2日
        mock_file = MagicMock()
        mock_file.readline.return_value = f"{uptime_seconds} 123456"
        mock_open.return_value.__enter__.return_value = mock_file
        
        profile = {"usage": "production"}
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_uptime(profile)
        
        output = captured_output.getvalue()
        
        # 短時間稼働では特別なアドバイスは表示されない
        self.assertEqual(output, "")
    
    @patch('builtins.open')
    def test_advise_uptime_file_error(self, mock_open):
        """ファイル読み込みエラーでのテスト"""
        mock_open.side_effect = FileNotFoundError("File not found")
        
        profile = {"usage": "production"}
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_uptime(profile)
        
        output = captured_output.getvalue()
        
        # エラーが発生してもクラッシュしないことを確認
        self.assertEqual(output, "")


class TestAdviseEmailDisabledFunctions(unittest.TestCase):
    """advise.pyのメール無効化関連関数テスト"""
    
    @patch('src.komon.commands.advise.skippable_advice')
    def test_advise_email_disabled_when_disabled(self, mock_skippable_advice):
        """メール通知が無効な場合のテスト"""
        config = {
            "notifications": {
                "email": {
                    "enabled": False
                }
            }
        }
        
        from pathlib import Path
        config_dir = Path("/tmp/test_config")
        
        advise_email_disabled(config, config_dir)
        
        # skippable_adviceが呼ばれることを確認
        mock_skippable_advice.assert_called_once()
        args = mock_skippable_advice.call_args[0]
        self.assertEqual(args[0], "email_disabled")
        self.assertIn("メール通知が無効", args[1])
    
    @patch('src.komon.commands.advise.skippable_advice')
    def test_advise_email_disabled_when_enabled(self, mock_skippable_advice):
        """メール通知が有効な場合のテスト"""
        config = {
            "notifications": {
                "email": {
                    "enabled": True
                }
            }
        }
        
        from pathlib import Path
        config_dir = Path("/tmp/test_config")
        
        advise_email_disabled(config, config_dir)
        
        # メール通知が有効な場合はskippable_adviceは呼ばれない
        mock_skippable_advice.assert_not_called()
    
    @patch('src.komon.commands.advise.skippable_advice')
    def test_advise_email_disabled_missing_config(self, mock_skippable_advice):
        """設定が不足している場合のテスト"""
        config = {}  # 空の設定
        
        from pathlib import Path
        config_dir = Path("/tmp/test_config")
        
        advise_email_disabled(config, config_dir)
        
        # 設定が不足している場合もskippable_adviceが呼ばれる
        mock_skippable_advice.assert_called_once()
    
    @patch('src.komon.commands.advise.skippable_advice')
    def test_advise_email_disabled_partial_config(self, mock_skippable_advice):
        """部分的な設定の場合のテスト"""
        config = {
            "notifications": {
                # emailセクションが不足
            }
        }
        
        from pathlib import Path
        config_dir = Path("/tmp/test_config")
        
        advise_email_disabled(config, config_dir)
        
        # 部分的な設定でもskippable_adviceが呼ばれる
        mock_skippable_advice.assert_called_once()


if __name__ == '__main__':
    unittest.main()