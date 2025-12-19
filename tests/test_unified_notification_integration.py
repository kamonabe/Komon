"""
統一Webhook通知システムの統合テスト

TASK-020: Webhook通知統一化 Phase 2の統合テスト
"""

import pytest
import yaml
from unittest.mock import Mock, patch, MagicMock
from src.komon.notification import (
    send_unified_webhook_notification,
    send_notification_with_fallback,
    _send_legacy_notifications
)


class TestUnifiedWebhookNotification:
    """統一Webhook通知のテスト"""
    
    @patch('src.komon.webhook_notifier.WebhookNotifier')
    def test_send_unified_webhook_notification_success(self, mock_notifier_class):
        """統一Webhook通知成功のテスト"""
        # モックの設定
        mock_notifier = Mock()
        mock_notifier.send.return_value = {
            "success_count": 2,
            "error_count": 0,
            "results": [
                {"webhook_name": "slack", "success": True},
                {"webhook_name": "discord", "success": True}
            ]
        }
        mock_notifier_class.return_value = mock_notifier
        
        # テスト実行
        webhooks_config = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True},
            {"name": "discord", "url": "https://discord.com/api/webhooks/test", "kind": "discord", "enabled": True}
        ]
        
        result = send_unified_webhook_notification(
            message="テストメッセージ",
            webhooks_config=webhooks_config,
            title="テストタイトル",
            level="warning"
        )
        
        # 検証
        assert result is True
        mock_notifier_class.assert_called_once_with(webhooks_config)
        mock_notifier.send.assert_called_once()
        
        # 送信された通知データを確認
        call_args = mock_notifier.send.call_args[0][0]
        assert call_args["message"] == "テストメッセージ"
        assert call_args["title"] == "テストタイトル"
        assert call_args["level"] == "warning"
    
    @patch('src.komon.webhook_notifier.WebhookNotifier')
    def test_send_unified_webhook_notification_failure(self, mock_notifier_class):
        """統一Webhook通知失敗のテスト"""
        # モックの設定
        mock_notifier = Mock()
        mock_notifier.send.return_value = {
            "success_count": 0,
            "error_count": 2,
            "results": [
                {"webhook_name": "slack", "success": False, "error": "Connection failed"},
                {"webhook_name": "discord", "success": False, "error": "Timeout"}
            ]
        }
        mock_notifier_class.return_value = mock_notifier
        
        # テスト実行
        webhooks_config = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True}
        ]
        
        result = send_unified_webhook_notification(
            message="テストメッセージ",
            webhooks_config=webhooks_config
        )
        
        # 検証
        assert result is False
    
    @patch('src.komon.webhook_notifier.WebhookNotifier')
    def test_send_unified_webhook_notification_exception(self, mock_notifier_class):
        """統一Webhook通知で例外が発生した場合のテスト"""
        # モックの設定
        mock_notifier_class.side_effect = Exception("Import error")
        
        # テスト実行
        webhooks_config = [
            {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True}
        ]
        
        result = send_unified_webhook_notification(
            message="テストメッセージ",
            webhooks_config=webhooks_config
        )
        
        # 検証
        assert result is False


class TestNotificationWithFallback:
    """フォールバック機能付き通知のテスト"""
    
    @patch('src.komon.notification.send_unified_webhook_notification')
    def test_fallback_uses_unified_when_configured(self, mock_unified):
        """新形式が設定されている場合は統一Webhookを使用するテスト"""
        # モックの設定
        mock_unified.return_value = True
        
        # 新形式の設定
        settings = {
            "notifiers": {
                "webhooks": [
                    {"name": "slack", "url": "https://hooks.slack.com/test", "kind": "slack", "enabled": True}
                ]
            },
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/old"}
            }
        }
        
        # テスト実行
        result = send_notification_with_fallback(
            message="テストメッセージ",
            settings=settings,
            title="テストタイトル",
            level="info"
        )
        
        # 検証
        assert result is True
        mock_unified.assert_called_once_with(
            message="テストメッセージ",
            webhooks_config=settings["notifiers"]["webhooks"],
            metadata=None,
            title="テストタイトル",
            level="info"
        )
    
    @patch('src.komon.notification._send_legacy_notifications')
    def test_fallback_uses_legacy_when_no_unified(self, mock_legacy):
        """新形式が未設定の場合は旧形式を使用するテスト"""
        # モックの設定
        mock_legacy.return_value = True
        
        # 旧形式のみの設定
        settings = {
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/old"}
            }
        }
        
        # テスト実行
        result = send_notification_with_fallback(
            message="テストメッセージ",
            settings=settings
        )
        
        # 検証
        assert result is True
        mock_legacy.assert_called_once_with("テストメッセージ", settings, None)
    
    @patch('src.komon.notification._send_legacy_notifications')
    def test_fallback_uses_legacy_when_empty_unified(self, mock_legacy):
        """新形式が空の場合は旧形式を使用するテスト"""
        # モックの設定
        mock_legacy.return_value = True
        
        # 新形式が空の設定
        settings = {
            "notifiers": {
                "webhooks": []  # 空
            },
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/old"}
            }
        }
        
        # テスト実行
        result = send_notification_with_fallback(
            message="テストメッセージ",
            settings=settings
        )
        
        # 検証
        assert result is True
        mock_legacy.assert_called_once()


class TestLegacyNotifications:
    """旧形式通知のテスト"""
    
    @patch('src.komon.notification.send_slack_alert')
    @patch('src.komon.notification.send_discord_alert')
    @patch('src.komon.notification.send_teams_alert')
    @patch('src.komon.notification.send_email_alert')
    def test_legacy_notifications_all_enabled(self, mock_email, mock_teams, mock_discord, mock_slack):
        """全ての旧形式通知が有効な場合のテスト"""
        # モックの設定
        mock_slack.return_value = True
        mock_discord.return_value = True
        mock_teams.return_value = True
        mock_email.return_value = True
        
        # 設定
        settings = {
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/test"},
                "discord": {"enabled": True, "webhook_url": "https://discord.com/api/webhooks/test"},
                "teams": {"enabled": True, "webhook_url": "https://outlook.office.com/webhook/test"},
                "email": {"enabled": True, "smtp_server": "smtp.example.com"}
            }
        }
        
        # テスト実行
        result = _send_legacy_notifications("テストメッセージ", settings)
        
        # 検証
        assert result is True
        mock_slack.assert_called_once()
        mock_discord.assert_called_once()
        mock_teams.assert_called_once()
        mock_email.assert_called_once()
    
    @patch('src.komon.notification.send_slack_alert')
    def test_legacy_notifications_partial_enabled(self, mock_slack):
        """一部の旧形式通知のみ有効な場合のテスト"""
        # モックの設定
        mock_slack.return_value = True
        
        # 設定（Slackのみ有効）
        settings = {
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/test"},
                "discord": {"enabled": False, "webhook_url": "https://discord.com/api/webhooks/test"},
                "teams": {"enabled": False, "webhook_url": "https://outlook.office.com/webhook/test"},
                "email": {"enabled": False}
            }
        }
        
        # テスト実行
        result = _send_legacy_notifications("テストメッセージ", settings)
        
        # 検証
        assert result is True
        mock_slack.assert_called_once()
    
    @patch('src.komon.notification.send_slack_alert')
    def test_legacy_notifications_all_disabled(self, mock_slack):
        """全ての旧形式通知が無効な場合のテスト"""
        # 設定（全て無効）
        settings = {
            "notifications": {
                "slack": {"enabled": False},
                "discord": {"enabled": False},
                "teams": {"enabled": False},
                "email": {"enabled": False}
            }
        }
        
        # テスト実行
        result = _send_legacy_notifications("テストメッセージ", settings)
        
        # 検証
        assert result is False
        mock_slack.assert_not_called()
    
    @patch('src.komon.notification.send_slack_alert')
    def test_legacy_notifications_some_failures(self, mock_slack):
        """一部の旧形式通知が失敗した場合のテスト"""
        # モックの設定（失敗）
        mock_slack.return_value = False
        
        # 設定
        settings = {
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/test"}
            }
        }
        
        # テスト実行
        result = _send_legacy_notifications("テストメッセージ", settings)
        
        # 検証
        assert result is False
        mock_slack.assert_called_once()


class TestConfigurationCompatibility:
    """設定の互換性テスト"""
    
    def test_yaml_config_parsing_new_format(self):
        """新形式のYAML設定パースのテスト"""
        yaml_content = """
notifiers:
  webhooks:
    - name: "slack"
      url: "https://hooks.slack.com/test"
      kind: "slack"
      enabled: true
    - name: "discord"
      url: "https://discord.com/api/webhooks/test"
      kind: "discord"
      enabled: false
"""
        config = yaml.safe_load(yaml_content)
        
        # 検証
        assert "notifiers" in config
        assert "webhooks" in config["notifiers"]
        webhooks = config["notifiers"]["webhooks"]
        assert len(webhooks) == 2
        assert webhooks[0]["name"] == "slack"
        assert webhooks[0]["enabled"] is True
        assert webhooks[1]["name"] == "discord"
        assert webhooks[1]["enabled"] is False
    
    def test_yaml_config_parsing_legacy_format(self):
        """旧形式のYAML設定パースのテスト"""
        yaml_content = """
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/test"
  discord:
    enabled: false
    webhook_url: "https://discord.com/api/webhooks/test"
"""
        config = yaml.safe_load(yaml_content)
        
        # 検証
        assert "notifications" in config
        assert "slack" in config["notifications"]
        assert config["notifications"]["slack"]["enabled"] is True
        assert config["notifications"]["discord"]["enabled"] is False