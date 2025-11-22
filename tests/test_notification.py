"""
notification.py のテスト

通知機能（Slack、メール）のテストを行います。
"""

import pytest
from unittest.mock import patch, MagicMock
from komon.notification import send_slack_alert, send_email_alert


class TestSendSlackAlert:
    """Slack通知のテスト"""
    
    @patch('komon.notification.requests.post')
    def test_send_slack_success(self, mock_post):
        """Slack通知が成功する場合"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_slack_alert(
            message="テストメッセージ",
            webhook_url="https://hooks.slack.com/services/TEST"
        )
        
        assert result is True
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/services/TEST"
        assert call_args[1]['json'] == {"text": "テストメッセージ"}
    
    @patch('komon.notification.requests.post')
    def test_send_slack_failure_status_code(self, mock_post):
        """Slack通知が失敗する場合（ステータスコードエラー）"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        
        result = send_slack_alert(
            message="テストメッセージ",
            webhook_url="https://hooks.slack.com/services/INVALID"
        )
        
        assert result is False
    
    @patch('komon.notification.requests.post')
    def test_send_slack_exception(self, mock_post):
        """Slack通知で例外が発生する場合"""
        mock_post.side_effect = Exception("Network error")
        
        result = send_slack_alert(
            message="テストメッセージ",
            webhook_url="https://hooks.slack.com/services/TEST"
        )
        
        assert result is False
    
    @patch('komon.notification.requests.post')
    def test_send_slack_timeout(self, mock_post):
        """Slack通知でタイムアウトが発生する場合"""
        import requests
        mock_post.side_effect = requests.Timeout("Request timeout")
        
        result = send_slack_alert(
            message="テストメッセージ",
            webhook_url="https://hooks.slack.com/services/TEST"
        )
        
        assert result is False


class TestSendEmailAlert:
    """メール通知のテスト"""
    
    @patch('komon.notification.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """メール通知が成功する場合"""
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
        
        result = send_email_alert("テストメッセージ", email_config)
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user", "pass")
        mock_server.send_message.assert_called_once()
    
    @patch('komon.notification.smtplib.SMTP')
    def test_send_email_without_auth(self, mock_smtp):
        """認証なしでメール通知が成功する場合"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email_config = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 25,
            "from": "komon@example.com",
            "to": "admin@example.com",
            "use_tls": False
        }
        
        result = send_email_alert("テストメッセージ", email_config)
        
        assert result is True
        mock_server.starttls.assert_not_called()
        mock_server.login.assert_not_called()
        mock_server.send_message.assert_called_once()
    
    @patch('komon.notification.smtplib.SMTP')
    @patch('komon.notification.os.getenv')
    def test_send_email_with_env_password(self, mock_getenv, mock_smtp):
        """環境変数からパスワードを読み込む場合"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_getenv.return_value = "secret_password"
        
        email_config = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "from": "komon@example.com",
            "to": "admin@example.com",
            "username": "user",
            "password": "env:SMTP_PASSWORD"
        }
        
        result = send_email_alert("テストメッセージ", email_config)
        
        assert result is True
        mock_getenv.assert_called_once_with("SMTP_PASSWORD", "")
        mock_server.login.assert_called_once_with("user", "secret_password")
    
    @patch('komon.notification.smtplib.SMTP')
    def test_send_email_exception(self, mock_smtp):
        """メール送信で例外が発生する場合"""
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        email_config = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "from": "komon@example.com",
            "to": "admin@example.com"
        }
        
        result = send_email_alert("テストメッセージ", email_config)
        
        assert result is False
    
    @patch('komon.notification.smtplib.SMTP')
    def test_send_email_default_port(self, mock_smtp):
        """デフォルトポート（587）が使用される場合"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email_config = {
            "smtp_server": "smtp.example.com",
            "from": "komon@example.com",
            "to": "admin@example.com"
        }
        
        result = send_email_alert("テストメッセージ", email_config)
        
        assert result is True
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
