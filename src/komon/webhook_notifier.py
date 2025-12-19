"""
統一Webhook通知システム

このモジュールは、複数の通知サービス（Slack、Discord、Teams等）に
統一されたインターフェースで通知を送信する機能を提供します。

TASK-020: Webhook通知統一化 Phase 2の実装
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from .formatters import FormatterFactory


logger = logging.getLogger(__name__)


class WebhookNotifier:
    """統一Webhook通知クラス
    
    複数のWebhookサービスに対して統一されたインターフェースで
    通知を送信する機能を提供します。
    
    Features:
    - 複数サービス対応（Slack、Discord、Teams等）
    - サービス別フォーマッター自動選択
    - エラーハンドリングと再試行
    - 設定による有効/無効制御
    """
    
    def __init__(self, webhooks: List[Dict[str, Any]]):
        """WebhookNotifierを初期化
        
        Args:
            webhooks: Webhook設定のリスト
                例: [
                    {
                        "name": "slack",
                        "url": "https://hooks.slack.com/...",
                        "kind": "slack",
                        "enabled": True
                    }
                ]
        """
        self.webhooks = webhooks or []
        self.formatter_factory = FormatterFactory()
        
        # 有効なWebhookのみをフィルタリング
        self.active_webhooks = [
            webhook for webhook in self.webhooks
            if webhook.get('enabled', True)
        ]
        
        logger.info(f"WebhookNotifier initialized with {len(self.active_webhooks)} active webhooks")
    
    def send(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """統一通知送信
        
        Args:
            notification: 通知データ
                例: {
                    "message": "通知メッセージ",
                    "title": "タイトル（オプション）",
                    "level": "info|warning|error"
                }
        
        Returns:
            Dict[str, Any]: 送信結果
                {
                    "success_count": 2,
                    "error_count": 0,
                    "results": [...]
                }
        """
        if not self.active_webhooks:
            logger.warning("No active webhooks configured")
            return {
                "success_count": 0,
                "error_count": 0,
                "results": []
            }
        
        results = []
        success_count = 0
        error_count = 0
        
        for webhook in self.active_webhooks:
            try:
                result = self._send_to_webhook(webhook, notification)
                results.append(result)
                
                if result["success"]:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"Unexpected error sending to {webhook.get('name', 'unknown')}: {e}")
                results.append({
                    "webhook_name": webhook.get('name', 'unknown'),
                    "success": False,
                    "error": str(e)
                })
                error_count += 1
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "results": results
        }
    
    def _send_to_webhook(self, webhook: Dict[str, Any], notification: Dict[str, Any]) -> Dict[str, Any]:
        """個別Webhookへの送信
        
        Args:
            webhook: Webhook設定
            notification: 通知データ
        
        Returns:
            Dict[str, Any]: 送信結果
        """
        webhook_name = webhook.get('name', 'unknown')
        webhook_url = webhook.get('url')
        webhook_kind = webhook.get('kind', 'generic')
        
        if not webhook_url:
            return {
                "webhook_name": webhook_name,
                "success": False,
                "error": "Webhook URL not configured"
            }
        
        try:
            # フォーマッターを取得してペイロードを作成
            formatter = self.formatter_factory.get_formatter(webhook_kind)
            payload = formatter.format(notification)
            
            # HTTP送信
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            # レスポンス確認
            response.raise_for_status()
            
            logger.info(f"Successfully sent notification to {webhook_name} ({webhook_kind})")
            return {
                "webhook_name": webhook_name,
                "success": True,
                "status_code": response.status_code
            }
            
        except requests.exceptions.Timeout:
            error_msg = f"Timeout sending to {webhook_name}"
            logger.error(error_msg)
            return {
                "webhook_name": webhook_name,
                "success": False,
                "error": error_msg
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP error sending to {webhook_name}: {e}"
            logger.error(error_msg)
            return {
                "webhook_name": webhook_name,
                "success": False,
                "error": error_msg
            }
    
    def test_webhooks(self) -> Dict[str, Any]:
        """Webhook接続テスト
        
        Returns:
            Dict[str, Any]: テスト結果
        """
        test_notification = {
            "message": "Webhook接続テスト - この通知は正常に送信されました",
            "title": "Komon統一Webhook テスト",
            "level": "info"
        }
        
        return self.send(test_notification)
    
    def get_webhook_status(self) -> Dict[str, Any]:
        """Webhook設定状況の取得
        
        Returns:
            Dict[str, Any]: 設定状況
        """
        return {
            "total_webhooks": len(self.webhooks),
            "active_webhooks": len(self.active_webhooks),
            "webhook_kinds": [w.get('kind', 'unknown') for w in self.active_webhooks],
            "webhook_names": [w.get('name', 'unknown') for w in self.active_webhooks]
        }