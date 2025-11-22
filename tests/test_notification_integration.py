"""
通知システム統合のユニットテスト

既存の通知機能と履歴保存機能の統合をテストします。
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from komon.notification import send_slack_alert, send_email_alert


class TestNotificationIntegration(unittest.TestCase):
    """通知システムと履歴保存の統合テスト"""
    
    def setUp(self):
        """各テストの前に実行"""
        self.temp_dir = tempfile.mkdtemp()
        self.queue_file = os.path.join(self.temp_dir, "queue.json")
    
    def tearDown(self):
        """各テストの後に実行"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('komon.notification.requests.post')
    def test_slack_notification_saves_history_on_success(self, mock_post):
        """
        Slack通知が成功した場合、履歴が保存されることを確認
        Validates: Requirements 4.1
        """
        # Slack APIのモック（成功）
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # メタデータ付きで通知送信
        metadata = {
            "metric_type": "cpu",
            "metric_value": 90.5
        }
        
        # save_notification を直接パッチして、テスト用のqueue_fileを使用
        from komon.notification_history import save_notification as real_save
        
        def mock_save(metric_type, metric_value, message, queue_file=None):
            return real_save(metric_type, metric_value, message, self.queue_file)
        
        with patch('komon.notification_history.save_notification', side_effect=mock_save):
            result = send_slack_alert(
                message="Test alert",
                webhook_url="https://hooks.slack.com/test",
                metadata=metadata
            )
        
        # 通知が成功したことを確認
        self.assertTrue(result)
        
        # 履歴ファイルが作成されたことを確認
        self.assertTrue(os.path.exists(self.queue_file))
        
        # 履歴の内容を確認
        with open(self.queue_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["metric_type"], "cpu")
        self.assertAlmostEqual(history[0]["metric_value"], 90.5, places=1)
        self.assertEqual(history[0]["message"], "Test alert")
    
    @patch('komon.notification.requests.post')
    def test_slack_notification_continues_when_history_save_fails(self, mock_post):
        """
        履歴保存が失敗しても、Slack通知は正常に動作することを確認
        Validates: Requirements 4.2
        """
        # Slack APIのモック（成功）
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # 無効なパスで履歴保存を失敗させる
        invalid_queue_file = "/invalid/path/queue.json"
        
        metadata = {
            "metric_type": "mem",
            "metric_value": 85.0
        }
        
        with patch('komon.notification_history.DEFAULT_QUEUE_FILE', invalid_queue_file):
            # 例外が発生せず、通知が成功することを確認
            result = send_slack_alert(
                message="Test alert",
                webhook_url="https://hooks.slack.com/test",
                metadata=metadata
            )
        
        # 通知は成功している
        self.assertTrue(result)
        # Slack APIが呼ばれたことを確認
        mock_post.assert_called_once()
    
    @patch('komon.notification.requests.post')
    def test_slack_notification_without_metadata(self, mock_post):
        """
        メタデータなしでも通知が正常に動作することを確認（後方互換性）
        Validates: Requirements 4.1
        """
        # Slack APIのモック（成功）
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # メタデータなしで通知送信
        result = send_slack_alert(
            message="Test alert without metadata",
            webhook_url="https://hooks.slack.com/test"
        )
        
        # 通知が成功したことを確認
        self.assertTrue(result)
        # Slack APIが呼ばれたことを確認
        mock_post.assert_called_once()
        
        # 履歴ファイルは作成されない（メタデータがないため）
        self.assertFalse(os.path.exists(self.queue_file))
    
    @patch('komon.notification.smtplib.SMTP')
    def test_email_notification_saves_history_on_success(self, mock_smtp):
        """
        メール通知が成功した場合、履歴が保存されることを確認
        Validates: Requirements 4.1
        """
        # SMTPのモック
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email_config = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "from": "komon@example.com",
            "to": "admin@example.com",
            "username": "user",
            "password": "pass"
        }
        
        metadata = {
            "metric_type": "disk",
            "metric_value": 88.0
        }
        
        # save_notification を直接パッチして、テスト用のqueue_fileを使用
        from komon.notification_history import save_notification as real_save
        
        def mock_save(metric_type, metric_value, message, queue_file=None):
            return real_save(metric_type, metric_value, message, self.queue_file)
        
        with patch('komon.notification_history.save_notification', side_effect=mock_save):
            result = send_email_alert(
                message="Test email alert",
                email_config=email_config,
                metadata=metadata
            )
        
        # 通知が成功したことを確認
        self.assertTrue(result)
        
        # 履歴ファイルが作成されたことを確認
        self.assertTrue(os.path.exists(self.queue_file))
        
        # 履歴の内容を確認
        with open(self.queue_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["metric_type"], "disk")
        self.assertAlmostEqual(history[0]["metric_value"], 88.0, places=1)
    
    @patch('komon.notification.smtplib.SMTP')
    def test_email_notification_continues_when_history_save_fails(self, mock_smtp):
        """
        履歴保存が失敗しても、メール通知は正常に動作することを確認
        Validates: Requirements 4.2
        """
        # SMTPのモック
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email_config = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "from": "komon@example.com",
            "to": "admin@example.com"
        }
        
        # 無効なパスで履歴保存を失敗させる
        invalid_queue_file = "/invalid/path/queue.json"
        
        metadata = {
            "metric_type": "log",
            "metric_value": 1000.0
        }
        
        with patch('komon.notification_history.DEFAULT_QUEUE_FILE', invalid_queue_file):
            # 例外が発生せず、通知が成功することを確認
            result = send_email_alert(
                message="Test email alert",
                email_config=email_config,
                metadata=metadata
            )
        
        # 通知は成功している
        self.assertTrue(result)
        # SMTPが呼ばれたことを確認
        mock_smtp.assert_called_once()
    
    @patch('komon.notification.requests.post')
    def test_metadata_is_correctly_passed_and_saved(self, mock_post):
        """
        メタデータが正しく渡され、保存されることを確認
        Validates: Requirements 4.1
        """
        # Slack APIのモック（成功）
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # 様々なメタデータでテスト
        test_cases = [
            {"metric_type": "cpu", "metric_value": 95.5},
            {"metric_type": "mem", "metric_value": 82.3},
            {"metric_type": "disk", "metric_value": 91.0},
            {"metric_type": "log", "metric_value": 500.0}
        ]
        
        # save_notification を直接パッチして、テスト用のqueue_fileを使用
        from komon.notification_history import save_notification as real_save
        
        def mock_save(metric_type, metric_value, message, queue_file=None):
            return real_save(metric_type, metric_value, message, self.queue_file)
        
        with patch('komon.notification_history.save_notification', side_effect=mock_save):
            for metadata in test_cases:
                send_slack_alert(
                    message=f"Test {metadata['metric_type']} alert",
                    webhook_url="https://hooks.slack.com/test",
                    metadata=metadata
                )
        
        # 履歴を確認
        with open(self.queue_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 4件保存されていることを確認
        self.assertEqual(len(history), 4)
        
        # 各メタデータが正しく保存されていることを確認（新しい順）
        for i, expected in enumerate(reversed(test_cases)):
            self.assertEqual(history[i]["metric_type"], expected["metric_type"])
            self.assertAlmostEqual(
                history[i]["metric_value"],
                expected["metric_value"],
                places=1
            )


if __name__ == '__main__':
    unittest.main()
