"""
フォーマッタークラスのテスト

TASK-020: Webhook通知統一化 Phase 2のテスト
"""

import pytest
from src.komon.formatters import (
    GenericFormatter, SlackFormatter, DiscordFormatter, 
    TeamsFormatter, FormatterFactory
)


class TestGenericFormatter:
    """GenericFormatterのテスト"""
    
    def test_format_message_only(self):
        """メッセージのみの場合のテスト"""
        formatter = GenericFormatter()
        notification = {"message": "テストメッセージ"}
        
        result = formatter.format(notification)
        
        assert result == {"text": "テストメッセージ"}
    
    def test_format_with_title(self):
        """タイトル付きの場合のテスト"""
        formatter = GenericFormatter()
        notification = {
            "message": "テストメッセージ",
            "title": "テストタイトル"
        }
        
        result = formatter.format(notification)
        
        assert result == {"text": "**テストタイトル**\nテストメッセージ"}
    
    def test_format_empty_message(self):
        """空メッセージの場合のテスト"""
        formatter = GenericFormatter()
        notification = {"message": ""}
        
        result = formatter.format(notification)
        
        assert result == {"text": ""}


class TestSlackFormatter:
    """SlackFormatterのテスト"""
    
    def test_format_info_level(self):
        """infoレベルの場合のテスト"""
        formatter = SlackFormatter()
        notification = {
            "message": "テストメッセージ",
            "title": "テストタイトル",
            "level": "info"
        }
        
        result = formatter.format(notification)
        
        assert result["text"] == "テストタイトル"
        assert len(result["attachments"]) == 1
        assert result["attachments"][0]["color"] == "#36a64f"  # 緑
        assert result["attachments"][0]["text"] == "テストメッセージ"
    
    def test_format_warning_level(self):
        """warningレベルの場合のテスト"""
        formatter = SlackFormatter()
        notification = {
            "message": "警告メッセージ",
            "level": "warning"
        }
        
        result = formatter.format(notification)
        
        assert result["text"] == "Komon通知"  # デフォルトタイトル
        assert result["attachments"][0]["color"] == "#ff9500"  # オレンジ
    
    def test_format_error_level(self):
        """errorレベルの場合のテスト"""
        formatter = SlackFormatter()
        notification = {
            "message": "エラーメッセージ",
            "level": "error"
        }
        
        result = formatter.format(notification)
        
        assert result["attachments"][0]["color"] == "#ff0000"  # 赤
    
    def test_format_unknown_level(self):
        """不明なレベルの場合のテスト"""
        formatter = SlackFormatter()
        notification = {
            "message": "テストメッセージ",
            "level": "unknown"
        }
        
        result = formatter.format(notification)
        
        assert result["attachments"][0]["color"] == "#36a64f"  # デフォルト（緑）


class TestDiscordFormatter:
    """DiscordFormatterのテスト"""
    
    def test_format_info_level(self):
        """infoレベルの場合のテスト"""
        formatter = DiscordFormatter()
        notification = {
            "message": "テストメッセージ",
            "title": "テストタイトル",
            "level": "info"
        }
        
        result = formatter.format(notification)
        
        assert "embeds" in result
        assert len(result["embeds"]) == 1
        embed = result["embeds"][0]
        assert embed["title"] == "テストタイトル"
        assert embed["description"] == "テストメッセージ"
        assert embed["color"] == 0x36a64f  # 緑
    
    def test_format_warning_level(self):
        """warningレベルの場合のテスト"""
        formatter = DiscordFormatter()
        notification = {
            "message": "警告メッセージ",
            "level": "warning"
        }
        
        result = formatter.format(notification)
        
        embed = result["embeds"][0]
        assert embed["title"] == "Komon通知"  # デフォルトタイトル
        assert embed["color"] == 0xff9500  # オレンジ
    
    def test_format_error_level(self):
        """errorレベルの場合のテスト"""
        formatter = DiscordFormatter()
        notification = {
            "message": "エラーメッセージ",
            "level": "error"
        }
        
        result = formatter.format(notification)
        
        embed = result["embeds"][0]
        assert embed["color"] == 0xff0000  # 赤


class TestTeamsFormatter:
    """TeamsFormatterのテスト"""
    
    def test_format_info_level(self):
        """infoレベルの場合のテスト"""
        formatter = TeamsFormatter()
        notification = {
            "message": "テストメッセージ",
            "title": "テストタイトル",
            "level": "info"
        }
        
        result = formatter.format(notification)
        
        assert result["@type"] == "MessageCard"
        assert result["@context"] == "https://schema.org/extensions"
        assert result["summary"] == "テストタイトル"
        assert result["themeColor"] == "good"
        assert len(result["sections"]) == 1
        section = result["sections"][0]
        assert section["activityTitle"] == "テストタイトル"
        assert section["activityText"] == "テストメッセージ"
        assert section["markdown"] is True
    
    def test_format_warning_level(self):
        """warningレベルの場合のテスト"""
        formatter = TeamsFormatter()
        notification = {
            "message": "警告メッセージ",
            "level": "warning"
        }
        
        result = formatter.format(notification)
        
        assert result["themeColor"] == "warning"
    
    def test_format_error_level(self):
        """errorレベルの場合のテスト"""
        formatter = TeamsFormatter()
        notification = {
            "message": "エラーメッセージ",
            "level": "error"
        }
        
        result = formatter.format(notification)
        
        assert result["themeColor"] == "attention"


class TestFormatterFactory:
    """FormatterFactoryのテスト"""
    
    def test_get_slack_formatter(self):
        """Slackフォーマッター取得のテスト"""
        factory = FormatterFactory()
        formatter = factory.get_formatter("slack")
        
        assert isinstance(formatter, SlackFormatter)
    
    def test_get_discord_formatter(self):
        """Discordフォーマッター取得のテスト"""
        factory = FormatterFactory()
        formatter = factory.get_formatter("discord")
        
        assert isinstance(formatter, DiscordFormatter)
    
    def test_get_teams_formatter(self):
        """Teamsフォーマッター取得のテスト"""
        factory = FormatterFactory()
        formatter = factory.get_formatter("teams")
        
        assert isinstance(formatter, TeamsFormatter)
    
    def test_get_generic_formatter(self):
        """汎用フォーマッター取得のテスト"""
        factory = FormatterFactory()
        formatter = factory.get_formatter("generic")
        
        assert isinstance(formatter, GenericFormatter)
    
    def test_get_unknown_formatter(self):
        """不明なフォーマッター取得のテスト"""
        factory = FormatterFactory()
        formatter = factory.get_formatter("unknown")
        
        # 不明な場合は汎用フォーマッターを返す
        assert isinstance(formatter, GenericFormatter)
    
    def test_get_formatter_case_insensitive(self):
        """大文字小文字を区別しないテスト"""
        factory = FormatterFactory()
        formatter1 = factory.get_formatter("SLACK")
        formatter2 = factory.get_formatter("Slack")
        formatter3 = factory.get_formatter("slack")
        
        assert isinstance(formatter1, SlackFormatter)
        assert isinstance(formatter2, SlackFormatter)
        assert isinstance(formatter3, SlackFormatter)
    
    def test_get_supported_kinds(self):
        """サポートされているサービス種別取得のテスト"""
        factory = FormatterFactory()
        kinds = factory.get_supported_kinds()
        
        expected_kinds = ['slack', 'discord', 'teams', 'generic']
        assert set(kinds) == set(expected_kinds)
    
    @pytest.mark.parametrize("kind,expected_class", [
        ("slack", SlackFormatter),
        ("discord", DiscordFormatter),
        ("teams", TeamsFormatter),
        ("generic", GenericFormatter),
    ])
    def test_formatter_types(self, kind, expected_class):
        """各フォーマッタータイプのテスト"""
        factory = FormatterFactory()
        formatter = factory.get_formatter(kind)
        assert isinstance(formatter, expected_class)