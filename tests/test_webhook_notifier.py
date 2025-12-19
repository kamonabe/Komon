"""
WebhookNotifierクラスのテスト

TASK-020: Webhook通知統一化 Phase 2のテスト
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from src.komon.webhook_notifier import WebhookNotifier


class TestWebhookNotifier:
    """WebhookNotifierクラスのテスト"""
    
    def test_init_empty_webhooks(self):
        """空のWebhook設定での初期化テスト"""
        notifier = WebhookNotifier([])
        assert notifier.webhooks == []
        assert notifier.active_webhooks == []
    
    def test_init_with_webhooks(self):
        """Webhook設定ありでの初期化テスト"""
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True},
            {"name": "discord", "url": "https://discord.com/api/webhooks/test", "kind": "discord", "enabled": False}
        ]
        notifier = WebhookNotifier(webhooks)
        assert len(notifier.webhooks) == 2
        assert len(notifier.active_webhooks) == 1  # enabledがTrueのもののみ
        assert notifier.active_webhooks[0]["name"] == "slack"
    
    def test_init_enabled_default_true(self):
        """enabled未指定時のデフォルト動作テスト"""
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack"}  # enabledなし
        ]
        notifier = WebhookNotifier(webhooks)
        assert len(notifier.active_webhooks) == 1  # デフォルトでenabled=True
    
    @patch('requests.post')
    def test_send_success_single_webhook(self, mock_post):
        """単一Webhook送信成功テスト"""
        # モックの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # テスト実行
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True}
        ]
        notifier = WebhookNotifier(webhooks)
        
        notification = {
            "message": "テストメッセージ",
            "title": "テストタイトル",
            "level": "info"
        }
        
        result = notifier.send(notification)
        
        # 検証
        assert result["success_count"] == 1
        assert result["error_count"] == 0
        assert len(result["results"]) == 1
        assert result["results"][0]["success"] is True
        assert result["results"][0]["webhook_name"] == "slack"
        
        # requests.postが正しく呼ばれたか確認
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/test"
        assert call_args[1]["timeout"] == 10
    
    @patch('requests.post')
    def test_send_success_multiple_webhooks(self, mock_post):
        """複数Webhook送信成功テスト"""
        # モックの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # テスト実行
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True},
            {"name": "discord", "url": "https://discord.com/api/webhooks/test", "kind": "discord", "enabled": True}
        ]
        notifier = WebhookNotifier(webhooks)
        
        notification = {"message": "テストメッセージ"}
        result = notifier.send(notification)
        
        # 検証
        assert result["success_count"] == 2
        assert result["error_count"] == 0
        assert len(result["results"]) == 2
        assert mock_post.call_count == 2
    
    @patch('requests.post')
    def test_send_http_error(self, mock_post):
        """HTTP エラー時のテスト"""
        # モックの設定
        mock_post.side_effect = requests.exceptions.RequestException("HTTP Error")
        
        # テスト実行
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True}
        ]
        notifier = WebhookNotifier(webhooks)
        
        notification = {"message": "テストメッセージ"}
        result = notifier.send(notification)
        
        # 検証
        assert result["success_count"] == 0
        assert result["error_count"] == 1
        assert result["results"][0]["success"] is False
        assert "HTTP Error" in result["results"][0]["error"]
    
    @patch('requests.post')
    def test_send_timeout_error(self, mock_post):
        """タイムアウトエラー時のテスト"""
        # モックの設定
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")
        
        # テスト実行
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True}
        ]
        notifier = WebhookNotifier(webhooks)
        
        notification = {"message": "テストメッセージ"}
        result = notifier.send(notification)
        
        # 検証
        assert result["success_count"] == 0
        assert result["error_count"] == 1
        assert result["results"][0]["success"] is False
        assert "Timeout" in result["results"][0]["error"]
    
    def test_send_no_active_webhooks(self):
        """アクティブなWebhookがない場合のテスト"""
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": False}
        ]
        notifier = WebhookNotifier(webhooks)
        
        notification = {"message": "テストメッセージ"}
        result = notifier.send(notification)
        
        # 検証
        assert result["success_count"] == 0
        assert result["error_count"] == 0
        assert result["results"] == []
    
    def test_send_missing_webhook_url(self):
        """Webhook URLが未設定の場合のテスト"""
        webhooks = [
            {"name": "slack", "kind": "slack", "enabled": True}  # urlなし
        ]
        notifier = WebhookNotifier(webhooks)
        
        notification = {"message": "テストメッセージ"}
        result = notifier.send(notification)
        
        # 検証
        assert result["success_count"] == 0
        assert result["error_count"] == 1
        assert result["results"][0]["success"] is False
        assert "Webhook URL not configured" in result["results"][0]["error"]
    
    @patch('requests.post')
    def test_send_mixed_results(self, mock_post):
        """成功と失敗が混在する場合のテスト"""
        # モックの設定（1回目成功、2回目失敗）
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.raise_for_status.return_value = None
        
        mock_post.side_effect = [
            mock_response_success,
            requests.exceptions.RequestException("Error")
        ]
        
        # テスト実行
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True},
            {"name": "discord", "url": "https://discord.com/api/webhooks/test", "kind": "discord", "enabled": True}
        ]
        notifier = WebhookNotifier(webhooks)
        
        notification = {"message": "テストメッセージ"}
        result = notifier.send(notification)
        
        # 検証
        assert result["success_count"] == 1
        assert result["error_count"] == 1
        assert len(result["results"]) == 2
    
    @patch('requests.post')
    def test_test_webhooks(self, mock_post):
        """Webhook接続テスト機能のテスト"""
        # モックの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # テスト実行
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True}
        ]
        notifier = WebhookNotifier(webhooks)
        
        result = notifier.test_webhooks()
        
        # 検証
        assert result["success_count"] == 1
        assert result["error_count"] == 0
        
        # テストメッセージが送信されたか確認
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        # フォーマッターによって形式は異なるが、テストメッセージが含まれているはず
        assert "テスト" in str(payload)
    
    def test_get_webhook_status(self):
        """Webhook設定状況取得のテスト"""
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True},
            {"name": "discord", "url": "https://discord.com/api/webhooks/test", "kind": "discord", "enabled": False},
            {"name": "teams", "url": "https://outlook.office.com/webhook/test", "kind": "teams", "enabled": True}
        ]
        notifier = WebhookNotifier(webhooks)
        
        status = notifier.get_webhook_status()
        
        # 検証
        assert status["total_webhooks"] == 3
        assert status["active_webhooks"] == 2
        assert set(status["webhook_kinds"]) == {"slack", "teams"}
        assert set(status["webhook_names"]) == {"slack", "teams"}
    
    @patch('src.komon.webhook_notifier.logger')
    def test_logging(self, mock_logger):
        """ログ出力のテスト"""
        webhooks = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True}
        ]
        notifier = WebhookNotifier(webhooks)
        
        # 初期化時のログ確認
        mock_logger.info.assert_called_with("WebhookNotifier initialized with 1 active webhooks")