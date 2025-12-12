"""
src/komon/commands/advise.py の追加関数テスト

カバレッジ90%達成のため、さらに多くの関数をテストします。
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import io
import sys

from src.komon.commands.advise import (
    advise_uptime,
    advise_email_disabled,
    advise_process_breakdown,
    advise_process_details
)


class TestAdviseAdditionalFunctions(unittest.TestCase):
    """advise.pyの追加関数テスト"""
    
    def test_advise_uptime_long_uptime_production(self):
        """長時間稼働（本番環境）のテスト"""
        with patch('builtins.open', mock_open(read_data="604800.0 987654.32\n")):
            with patch('src.komon.commands.advise.ask_yes_no', return_value=True) as mock_ask_yes_no:
                profile = {"usage": "production"}
                
                captured_output = io.StringIO()
                with patch('sys.stdout', captured_output):
                    advise_uptime(profile)
                
                output = captured_output.getvalue()
                
                # 本番環境向けのメッセージが表示されることを確認
                self.assertIn("本番環境では定期的な再起動も", output)
                mock_ask_yes_no.assert_called_once()
    
    def test_advise_uptime_long_uptime_development(self):
        """長時間稼働（開発環境）のテスト"""
        with patch('builtins.open', mock_open(read_data="604800.0 1000000.0\n")):
            with patch('src.komon.commands.advise.ask_yes_no', return_value=True) as mock_ask_yes_no:
                profile = {"usage": "development"}
                
                captured_output = io.StringIO()
                with patch('sys.stdout', captured_output):
                    advise_uptime(profile)
                
                output = captured_output.getvalue()
                
                # 開発環境向けのメッセージが表示されることを確認
                self.assertIn("長期間の稼働は不安定化の要因", output)
                mock_ask_yes_no.assert_called_once()
    
    def test_advise_uptime_short_uptime(self):
        """短時間稼働のテスト"""
        with patch('builtins.open', mock_open(read_data="86400.0 200000.0\n")):
            with patch('src.komon.commands.advise.ask_yes_no') as mock_ask_yes_no:
                profile = {"usage": "production"}
                
                captured_output = io.StringIO()
                with patch('sys.stdout', captured_output):
                    advise_uptime(profile)
                
                output = captured_output.getvalue()
                
                # 短時間稼働では何も表示されない
                self.assertEqual(output.strip(), "")
                mock_ask_yes_no.assert_not_called()
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_advise_uptime_file_not_found(self, mock_open):
        """uptimeファイルが見つからない場合のテスト"""
        profile = {"usage": "production"}
        
        # 例外が発生してもクラッシュしないことを確認
        try:
            advise_uptime(profile)
        except Exception as e:
            self.fail(f"advise_uptime raised an exception: {e}")
    
    @patch('src.komon.commands.advise.skippable_advice')
    def test_advise_email_disabled_email_disabled(self, mock_skippable_advice):
        """メール通知が無効な場合のテスト"""
        config = {
            "notifications": {
                "email": {
                    "enabled": False
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            advise_email_disabled(config, config_dir)
            
            # skippable_adviceが呼ばれることを確認
            mock_skippable_advice.assert_called_once()
            args = mock_skippable_advice.call_args[0]
            self.assertEqual(args[0], "email_disabled")
            self.assertIn("メール通知が無効です", args[1])
    
    @patch('src.komon.commands.advise.skippable_advice')
    def test_advise_email_disabled_email_enabled(self, mock_skippable_advice):
        """メール通知が有効な場合のテスト"""
        config = {
            "notifications": {
                "email": {
                    "enabled": True
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            advise_email_disabled(config, config_dir)
            
            # skippable_adviceが呼ばれないことを確認
            mock_skippable_advice.assert_not_called()
    
    @patch('src.komon.commands.advise.skippable_advice')
    def test_advise_email_disabled_no_email_config(self, mock_skippable_advice):
        """メール設定がない場合のテスト"""
        config = {
            "notifications": {}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            advise_email_disabled(config, config_dir)
            
            # デフォルトでFalseなのでskippable_adviceが呼ばれる
            mock_skippable_advice.assert_called_once()
    
    def test_advise_process_breakdown_with_processes(self):
        """プロセス情報ありの場合のテスト"""
        usage = {
            "cpu_by_process": [
                {"name": "python", "cpu": 25.5},
                {"name": "chrome", "cpu": 15.2},
                {"name": "code", "cpu": 8.1}
            ],
            "mem_by_process": [
                {"name": "chrome", "mem": 1024},
                {"name": "python", "mem": 512},
                {"name": "code", "mem": 256}
            ]
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_process_breakdown(usage)
        
        output = captured_output.getvalue()
        
        # CPU使用率の内訳が表示されることを確認
        self.assertIn("📌 CPU使用率の内訳：", output)
        self.assertIn("python: 25.5%", output)
        self.assertIn("chrome: 15.2%", output)
        
        # メモリ使用率の内訳が表示されることを確認
        self.assertIn("📌 メモリ使用率の内訳：", output)
        self.assertIn("chrome: 1024 MB", output)
        self.assertIn("python: 512 MB", output)
    
    def test_advise_process_breakdown_no_processes(self):
        """プロセス情報なしの場合のテスト"""
        usage = {}
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_process_breakdown(usage)
        
        output = captured_output.getvalue()
        
        # 何も表示されないことを確認
        self.assertEqual(output.strip(), "")
    
    def test_advise_process_breakdown_cpu_only(self):
        """CPU情報のみの場合のテスト"""
        usage = {
            "cpu_by_process": [
                {"name": "python", "cpu": 25.5}
            ]
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_process_breakdown(usage)
        
        output = captured_output.getvalue()
        
        # CPU情報のみ表示されることを確認
        self.assertIn("📌 CPU使用率の内訳：", output)
        self.assertNotIn("📌 メモリ使用率の内訳：", output)
    
    @patch('komon.contextual_advisor.get_contextual_advice')
    def test_advise_process_details_contextual_enabled(self, mock_get_contextual_advice):
        """コンテキストアドバイス有効時のテスト"""
        # モックの設定
        mock_get_contextual_advice.return_value = {
            "top_processes": [{"name": "python", "cpu": 25.0}],
            "formatted_message": "高負荷プロセス: python (25.0%)"
        }
        
        thresholds = {"proc_cpu": 20}
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "detailed"
            }
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_process_details(thresholds, config)
        
        output = captured_output.getvalue()
        
        # コンテキストアドバイスが表示されることを確認
        self.assertIn("🧐 高負荷プロセスの詳細情報", output)
        self.assertIn("高負荷プロセス: python", output)
        mock_get_contextual_advice.assert_called_once_with("cpu", config, "detailed")
    
    @patch('komon.contextual_advisor.get_contextual_advice')
    def test_advise_process_details_contextual_no_processes(self, mock_get_contextual_advice):
        """コンテキストアドバイス有効だが高負荷プロセスなしのテスト"""
        mock_get_contextual_advice.return_value = {
            "top_processes": [],
            "formatted_message": ""
        }
        
        thresholds = {"proc_cpu": 20}
        config = {
            "contextual_advice": {
                "enabled": True
            }
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_process_details(thresholds, config)
        
        output = captured_output.getvalue()
        
        # 高負荷プロセスなしのメッセージが表示されることを確認
        self.assertIn("現在、高負荷なプロセスは検出されていません", output)
    
    def test_advise_process_details_contextual_disabled(self):
        """コンテキストアドバイス無効時のテスト"""
        thresholds = {"proc_cpu": 20}
        config = {
            "contextual_advice": {
                "enabled": False
            }
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_process_details(thresholds, config)
        
        output = captured_output.getvalue()
        
        # 基本的なヘッダーが表示されることを確認
        self.assertIn("🧐 高負荷プロセスの詳細情報", output)
    
    def test_advise_process_details_no_config(self):
        """設定なしの場合のテスト"""
        thresholds = {"proc_cpu": 20}
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_process_details(thresholds)
        
        output = captured_output.getvalue()
        
        # 設定なしでも動作することを確認
        self.assertIn("🧐 高負荷プロセスの詳細情報", output)
    
    @patch('komon.contextual_advisor.get_contextual_advice')
    @patch('src.komon.commands.advise.logger')
    def test_advise_process_details_contextual_error(self, mock_logger, mock_get_contextual_advice):
        """コンテキストアドバイス取得エラー時のテスト"""
        mock_get_contextual_advice.side_effect = Exception("Test error")
        
        thresholds = {"proc_cpu": 20}
        config = {
            "contextual_advice": {
                "enabled": True
            }
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_process_details(thresholds, config)
        
        output = captured_output.getvalue()
        
        # エラーメッセージが表示されることを確認
        self.assertIn("コンテキストアドバイスの取得に失敗しました", output)
        mock_logger.error.assert_called_once()


if __name__ == '__main__':
    unittest.main()