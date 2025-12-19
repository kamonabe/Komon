"""
Webhook通知フォーマッター

各通知サービス（Slack、Discord、Teams等）に応じた
メッセージフォーマットを提供します。

TASK-020: Webhook通知統一化 Phase 2の実装
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any


logger = logging.getLogger(__name__)


class BaseFormatter(ABC):
    """フォーマッターの基底クラス"""
    
    @abstractmethod
    def format(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """通知データをサービス固有の形式にフォーマット
        
        Args:
            notification: 統一通知データ
        
        Returns:
            Dict[str, Any]: サービス固有のペイロード
        """
        pass


class GenericFormatter(BaseFormatter):
    """汎用フォーマッター
    
    不明なサービスや基本的な形式に対応
    """
    
    def format(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """汎用フォーマット
        
        Args:
            notification: 統一通知データ
        
        Returns:
            Dict[str, Any]: 汎用ペイロード
        """
        message = notification.get('message', '')
        title = notification.get('title', '')
        
        # タイトルがある場合は結合
        if title:
            full_message = f"**{title}**\n{message}"
        else:
            full_message = message
        
        return {
            "text": full_message
        }


class SlackFormatter(BaseFormatter):
    """Slack用フォーマッター
    
    Slack Webhook APIの形式に対応
    """
    
    def format(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Slack形式にフォーマット
        
        Args:
            notification: 統一通知データ
        
        Returns:
            Dict[str, Any]: Slackペイロード
        """
        message = notification.get('message', '')
        title = notification.get('title', '')
        level = notification.get('level', 'info')
        
        # レベルに応じた色設定
        color_map = {
            'info': '#36a64f',      # 緑
            'warning': '#ff9500',   # オレンジ
            'error': '#ff0000'      # 赤
        }
        color = color_map.get(level, '#36a64f')
        
        # Slack形式のペイロード
        payload = {
            "text": title or "Komon通知",
            "attachments": [
                {
                    "color": color,
                    "text": message,
                    "mrkdwn_in": ["text"]
                }
            ]
        }
        
        return payload


class DiscordFormatter(BaseFormatter):
    """Discord用フォーマッター
    
    Discord Webhook APIの形式に対応
    """
    
    def format(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Discord形式にフォーマット
        
        Args:
            notification: 統一通知データ
        
        Returns:
            Dict[str, Any]: Discordペイロード
        """
        message = notification.get('message', '')
        title = notification.get('title', '')
        level = notification.get('level', 'info')
        
        # レベルに応じた色設定（16進数の整数値）
        color_map = {
            'info': 0x36a64f,      # 緑
            'warning': 0xff9500,   # オレンジ
            'error': 0xff0000      # 赤
        }
        color = color_map.get(level, 0x36a64f)
        
        # Discord Embed形式
        embed = {
            "title": title or "Komon通知",
            "description": message,
            "color": color,
            "timestamp": None  # 現在時刻は自動設定される
        }
        
        payload = {
            "embeds": [embed]
        }
        
        return payload


class TeamsFormatter(BaseFormatter):
    """Microsoft Teams用フォーマッター
    
    Teams Webhook APIの形式に対応
    """
    
    def format(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Teams形式にフォーマット
        
        Args:
            notification: 統一通知データ
        
        Returns:
            Dict[str, Any]: Teamsペイロード
        """
        message = notification.get('message', '')
        title = notification.get('title', '')
        level = notification.get('level', 'info')
        
        # レベルに応じたテーマカラー
        color_map = {
            'info': 'good',      # 緑
            'warning': 'warning', # オレンジ
            'error': 'attention'  # 赤
        }
        theme_color = color_map.get(level, 'good')
        
        # Teams MessageCard形式
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": title or "Komon通知",
            "themeColor": theme_color,
            "sections": [
                {
                    "activityTitle": title or "Komon通知",
                    "activityText": message,
                    "markdown": True
                }
            ]
        }
        
        return payload


class FormatterFactory:
    """フォーマッターファクトリー
    
    サービス種別に応じて適切なフォーマッターを提供
    """
    
    def __init__(self):
        """ファクトリーを初期化"""
        self._formatters = {
            'slack': SlackFormatter(),
            'discord': DiscordFormatter(),
            'teams': TeamsFormatter(),
            'generic': GenericFormatter()
        }
    
    def get_formatter(self, kind: str) -> BaseFormatter:
        """フォーマッターを取得
        
        Args:
            kind: サービス種別（slack, discord, teams, generic）
        
        Returns:
            BaseFormatter: 対応するフォーマッター
        """
        formatter = self._formatters.get(kind.lower())
        
        if formatter is None:
            logger.warning(f"Unknown formatter kind: {kind}, using generic formatter")
            formatter = self._formatters['generic']
        
        return formatter
    
    def get_supported_kinds(self) -> list:
        """サポートされているサービス種別を取得
        
        Returns:
            list: サポートされているサービス種別のリスト
        """
        return list(self._formatters.keys())