"""
src/komon/commands/advise.py のメモリ詳細表示関数テスト

カバレッジ改善のため、メモリ使用量詳細表示部分をテストします。
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import sys

from src.komon.commands.advise import (
    advise_resource_usage
)


class TestAdviseMemoryDetails(unittest.TestCase):
    """advise.pyのメモリ詳細表示テスト"""
    
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('psutil.process_iter')
    def test_advise_resource_usage_memory_details_yes(self, mock_process_iter, mock_ask_yes_no):
        """メモリ詳細表示（ユーザーがyesを選択）のテスト"""
        mock_ask_yes_no.return_value = True  # ユーザーがyesを選択
        
        # モックプロセス情報を作成
        mock_processes = [
            {
                'pid': 1234,
                'name': 'chrome',
                'memory_percent': 15.5,
                'username': 'testuser',
                'cmdline': ['chrome', '--no-sandbox']
            },
            {
                'pid': 5678,
                'name': 'python',
                'memory_percent': 8.2,
                'username': 'testuser',
                'cmdline': ['python', 'script.py']
            },
            {
                'pid': 9012,
                'name': 'code',
                'memory_percent': 6.1,
                'username': 'testuser',
                'cmdline': ['code', '--no-sandbox']
            }
        ]
        
        # process_iterのモック設定
        mock_proc_objects = []
        for proc_info in mock_processes:
            mock_proc = MagicMock()
            mock_proc.info = proc_info
            mock_proc_objects.append(mock_proc)
        
        mock_process_iter.return_value = mock_proc_objects
        
        usage = {
            "cpu": 45.0,
            "mem": 85.0,  # 閾値超過
            "disk": 60.0
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
        
        # メモリ詳細情報が表示されることを確認
        self.assertIn("上位メモリ使用プロセス", output)
        self.assertIn("chrome", output)
        self.assertIn("python", output)
        self.assertIn("15.5%", output)
        self.assertIn("PID: 1234", output)
        mock_ask_yes_no.assert_called()
    
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('psutil.process_iter')
    def test_advise_resource_usage_memory_details_exception(self, mock_process_iter, mock_ask_yes_no):
        """メモリ詳細表示でプロセス情報取得エラーのテスト"""
        mock_ask_yes_no.return_value = True  # ユーザーがyesを選択
        
        # psutil.process_iterで例外を発生させる
        mock_process_iter.side_effect = Exception("Process access denied")
        
        usage = {
            "cpu": 45.0,
            "mem": 85.0,  # 閾値超過
            "disk": 60.0
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
        
        # エラーメッセージが表示されることを確認
        self.assertIn("プロセス情報の取得中にエラーが発生", output)
        self.assertIn("Process access denied", output)
        mock_ask_yes_no.assert_called()
    
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('psutil.process_iter')
    def test_advise_resource_usage_memory_details_empty_cmdline(self, mock_process_iter, mock_ask_yes_no):
        """コマンドラインが空のプロセスのテスト"""
        mock_ask_yes_no.return_value = True  # ユーザーがyesを選択
        
        # コマンドラインが空のプロセス情報
        mock_processes = [
            {
                'pid': 1234,
                'name': 'kernel_task',
                'memory_percent': 5.5,
                'username': 'root',
                'cmdline': []  # 空のコマンドライン
            },
            {
                'pid': 5678,
                'name': None,  # 名前がNone
                'memory_percent': 3.2,
                'username': None,  # ユーザー名がNone
                'cmdline': None  # コマンドラインがNone
            }
        ]
        
        # process_iterのモック設定
        mock_proc_objects = []
        for proc_info in mock_processes:
            mock_proc = MagicMock()
            mock_proc.info = proc_info
            mock_proc_objects.append(mock_proc)
        
        mock_process_iter.return_value = mock_proc_objects
        
        usage = {
            "cpu": 45.0,
            "mem": 85.0,  # 閾値超過
            "disk": 60.0
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
        
        # 空の値やNoneが適切に処理されることを確認
        self.assertIn("(不明)", output)
        self.assertIn("kernel_task", output)
        mock_ask_yes_no.assert_called()
    
    @patch('src.komon.commands.advise.ask_yes_no')
    def test_advise_resource_usage_high_cpu(self, mock_ask_yes_no):
        """高CPU使用量でのアドバイステスト"""
        mock_ask_yes_no.return_value = True  # ユーザーがyesを選択
        
        usage = {
            "cpu": 90.0,  # 閾値超過
            "mem": 55.0,
            "disk": 60.0
        }
        
        thresholds = {
            "cpu": 85,
            "mem": 80,
            "disk": 80
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_resource_usage(usage, thresholds)
        
        output = captured_output.getvalue()
        
        # CPU使用量が高い場合のアドバイスが含まれることを確認
        self.assertIn("top", output)
        self.assertIn("ps aux", output)
        mock_ask_yes_no.assert_called()
    
    @patch('src.komon.commands.advise.ask_yes_no')
    def test_advise_resource_usage_high_disk_yes(self, mock_ask_yes_no):
        """高ディスク使用量でのアドバイステスト（ユーザーがyesを選択）"""
        mock_ask_yes_no.return_value = True  # ユーザーがyesを選択
        
        usage = {
            "cpu": 45.0,
            "mem": 55.0,
            "disk": 90.0  # 閾値超過
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
        
        # ディスク使用量が高い場合のアドバイスが含まれることを確認
        self.assertIn("du -sh", output)
        self.assertIn("journalctl --vacuum-time", output)
        mock_ask_yes_no.assert_called()
    
    @patch('src.komon.commands.advise.ask_yes_no')
    def test_advise_resource_usage_multiple_high_resources(self, mock_ask_yes_no):
        """複数のリソースが高い場合のテスト"""
        mock_ask_yes_no.return_value = False  # 全てnoを選択
        
        usage = {
            "cpu": 90.0,  # 閾値超過
            "mem": 85.0,  # 閾値超過
            "disk": 90.0  # 閾値超過
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
        
        # 複数のリソースについてアドバイスが表示されることを確認
        # ask_yes_noが3回呼ばれることを確認
        self.assertEqual(mock_ask_yes_no.call_count, 3)


if __name__ == '__main__':
    unittest.main()