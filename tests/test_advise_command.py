"""
adviseコマンド拡張のユニットテスト

通知履歴表示機能のテストを行います。
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

from scripts.advise import advise_notification_history


class TestAdviseCommandExtension(unittest.TestCase):
    """adviseコマンドの履歴表示機能テスト"""
    
    def setUp(self):
        """各テストの前に実行"""
        self.temp_dir = tempfile.mkdtemp()
        self.queue_file = os.path.join(self.temp_dir, "queue.json")
    
    def tearDown(self):
        """各テストの後に実行"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_display_with_no_history(self):
        """
        履歴がない場合、適切なメッセージが表示されることを確認
        Validates: Requirements 2.4
        """
        # 空の履歴を返すようにモック
        with patch('scripts.advise.load_notification_history', return_value=[]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                advise_notification_history()
                output = fake_out.getvalue()
        
        self.assertIn("📜 通知履歴", output)
        self.assertIn("通知履歴はありません", output)
    
    def test_display_with_corrupted_file(self):
        """
        破損したファイルの場合、エラーメッセージが表示されクラッシュしないことを確認
        Validates: Requirements 2.5
        """
        # load_notification_historyが例外を投げるようにモック
        with patch('scripts.advise.load_notification_history', side_effect=Exception("File corrupted")):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                # クラッシュせずに実行されることを確認
                try:
                    advise_notification_history()
                    output = fake_out.getvalue()
                    self.assertIn("📜 通知履歴", output)
                    self.assertIn("読み込みに失敗", output)
                except Exception as e:
                    self.fail(f"Should not crash with corrupted file, but got: {e}")
    
    def test_history_limit_option(self):
        """
        --history N オプションで指定した件数のみ表示されることを確認
        Validates: Requirements 2.2
        """
        # テスト用の履歴を作成（10件）
        history = [
            {
                "timestamp": f"2025-11-22T10:{i:02d}:00.000000",
                "metric_type": "cpu",
                "metric_value": 80.0 + i,
                "message": f"Test message {i}"
            }
            for i in range(10)
        ]
        
        # load_notification_historyをモックして、limit=3の時は3件だけ返す
        def mock_load(queue_file=None, limit=None):
            if limit:
                return history[:limit]
            return history
        
        with patch('scripts.advise.load_notification_history', side_effect=mock_load):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                advise_notification_history(limit=3)
                output = fake_out.getvalue()
        
        # 3件のメッセージが含まれていることを確認
        self.assertIn("Test message 0", output)
        self.assertIn("Test message 1", output)
        self.assertIn("Test message 2", output)
        # 4件目以降は含まれていないことを確認
        self.assertNotIn("Test message 3", output)
    
    def test_display_all_history_without_limit(self):
        """
        limitを指定しない場合、全履歴が表示されることを確認
        Validates: Requirements 2.1
        """
        # テスト用の履歴を作成
        history = [
            {
                "timestamp": f"2025-11-22T10:{i:02d}:00.000000",
                "metric_type": "mem",
                "metric_value": 70.0 + i,
                "message": f"Memory alert {i}"
            }
            for i in range(5)
        ]
        
        # load_notification_historyをモックして全件返す
        with patch('scripts.advise.load_notification_history', return_value=history):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                advise_notification_history()
                output = fake_out.getvalue()
        
        # 全5件のメッセージが含まれていることを確認
        for i in range(5):
            self.assertIn(f"Memory alert {i}", output)
    
    def test_formatted_output_contains_required_fields(self):
        """
        表示される履歴に必要なフィールドが全て含まれることを確認
        Validates: Requirements 2.3
        """
        # テスト用の履歴を作成
        history = [{
            "timestamp": "2025-11-22T10:30:45.123456",
            "metric_type": "disk",
            "metric_value": 88.5,
            "message": "Disk usage is high"
        }]
        
        # load_notification_historyをモック
        with patch('scripts.advise.load_notification_history', return_value=history):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                advise_notification_history()
                output = fake_out.getvalue()
        
        # 必要なフィールドが含まれていることを確認
        self.assertIn("2025-11-22", output)  # タイムスタンプ
        self.assertIn("DISK", output)  # メトリクスタイプ（大文字）
        self.assertIn("88.5", output)  # メトリクス値
        self.assertIn("Disk usage is high", output)  # メッセージ


if __name__ == '__main__':
    unittest.main()
