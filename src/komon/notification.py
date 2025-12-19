"""
通知モジュール

Slack、メールなどの通知機能を提供します。
統一Webhook機能（TASK-020）と旧形式の両方をサポートします。
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
import logging

import requests

logger = logging.getLogger(__name__)


def send_slack_alert(message: str, webhook_url: str, metadata: dict = None) -> bool:
    """
    Slackに通知を送信し、履歴に保存します。
    
    Args:
        message: 送信するメッセージ
        webhook_url: Slack Incoming Webhook URL（env:で始まる場合は環境変数から読み込み）
        metadata: 通知メタデータ（metric_type, metric_value等）
        
    Returns:
        bool: 送信成功時True
    """
    try:
        # 環境変数からWebhook URLを読み込む
        if webhook_url.startswith("env:"):
            env_var = webhook_url.split(":", 1)[1]
            webhook_url = os.getenv(env_var, "")
            if not webhook_url:
                print(f"⚠️ 環境変数 {env_var} が設定されていません")
                return False
        
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Slack通知を送信しました")
            success = True
        else:
            print(f"⚠️ Slack通知の送信に失敗しました: {response.status_code}")
            success = False
    except Exception as e:
        print(f"❌ Slack通知エラー: {e}")
        success = False
    
    # 履歴に保存（失敗しても通知は継続）
    if metadata:
        try:
            from komon.notification_history import save_notification
            save_notification(
                metric_type=metadata.get("metric_type", "unknown"),
                metric_value=metadata.get("metric_value", 0),
                message=message
            )
        except Exception as e:
            print(f"⚠️ 通知履歴の保存に失敗: {e}")
    
    return success


def send_discord_alert(message: str, webhook_url: str, metadata: dict = None) -> bool:
    """
    Discordに通知を送信し、履歴に保存します。
    
    Args:
        message: 送信するメッセージ
        webhook_url: Discord Webhook URL（env:で始まる場合は環境変数から読み込み）
        metadata: 通知メタデータ（metric_type, metric_value等）
        
    Returns:
        bool: 送信成功時True
    """
    try:
        # 環境変数からWebhook URLを読み込む
        if webhook_url.startswith("env:"):
            env_var = webhook_url.split(":", 1)[1]
            webhook_url = os.getenv(env_var, "")
            if not webhook_url:
                print(f"⚠️ 環境変数 {env_var} が設定されていません")
                return False
        
        payload = {"content": message}
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 204:  # Discordは204を返す
            print("✅ Discord通知を送信しました")
            success = True
        else:
            print(f"⚠️ Discord通知の送信に失敗しました: {response.status_code}")
            success = False
    except Exception as e:
        print(f"❌ Discord通知エラー: {e}")
        success = False
    
    # 履歴に保存（失敗しても通知は継続）
    if metadata:
        try:
            from komon.notification_history import save_notification
            save_notification(
                metric_type=metadata.get("metric_type", "unknown"),
                metric_value=metadata.get("metric_value", 0),
                message=message
            )
        except Exception as e:
            print(f"⚠️ 通知履歴の保存に失敗: {e}")
    
    return success


def send_teams_alert(message: str, webhook_url: str, metadata: dict = None) -> bool:
    """
    Microsoft Teamsに通知を送信し、履歴に保存します。
    
    Args:
        message: 送信するメッセージ
        webhook_url: Teams Webhook URL（env:で始まる場合は環境変数から読み込み）
        metadata: 通知メタデータ（metric_type, metric_value等）
        
    Returns:
        bool: 送信成功時True
    """
    try:
        # 環境変数からWebhook URLを読み込む
        if webhook_url.startswith("env:"):
            env_var = webhook_url.split(":", 1)[1]
            webhook_url = os.getenv(env_var, "")
            if not webhook_url:
                print(f"⚠️ 環境変数 {env_var} が設定されていません")
                return False
        
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Teams通知を送信しました")
            success = True
        else:
            print(f"⚠️ Teams通知の送信に失敗しました: {response.status_code}")
            success = False
    except Exception as e:
        print(f"❌ Teams通知エラー: {e}")
        success = False
    
    # 履歴に保存（失敗しても通知は継続）
    if metadata:
        try:
            from komon.notification_history import save_notification
            save_notification(
                metric_type=metadata.get("metric_type", "unknown"),
                metric_value=metadata.get("metric_value", 0),
                message=message
            )
        except Exception as e:
            print(f"⚠️ 通知履歴の保存に失敗: {e}")
    
    return success


def send_email_alert(message: str, email_config: dict, metadata: dict = None) -> bool:
    """
    メールで通知を送信し、履歴に保存します。
    
    Args:
        message: 送信するメッセージ
        email_config: メール設定（smtp_server, smtp_port, from, to, username, password等）
        metadata: 通知メタデータ（metric_type, metric_value等）
        
    Returns:
        bool: 送信成功時True
    """
    try:
        smtp_server = email_config.get("smtp_server")
        smtp_port = email_config.get("smtp_port", 587)
        from_addr = email_config.get("from")
        to_addr = email_config.get("to")
        username = email_config.get("username")
        password = email_config.get("password", "")
        
        # 環境変数からパスワードを読み込む
        if password.startswith("env:"):
            env_var = password.split(":", 1)[1]
            password = os.getenv(env_var, "")
        
        # メッセージ作成
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Subject"] = "Komon 警戒情報"
        msg.attach(MIMEText(message, "plain", "utf-8"))
        
        # SMTP送信
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if email_config.get("use_tls", True):
                server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(msg)
        
        print("✅ メール通知を送信しました")
        success = True
        
    except Exception as e:
        print(f"❌ メール通知エラー: {e}")
        success = False
    
    # 履歴に保存（失敗しても通知は継続）
    if metadata:
        try:
            from komon.notification_history import save_notification
            save_notification(
                metric_type=metadata.get("metric_type", "unknown"),
                metric_value=metadata.get("metric_value", 0),
                message=message
            )
        except Exception as e:
            print(f"⚠️ 通知履歴の保存に失敗: {e}")
    
    return success


def send_unified_webhook_notification(
    message: str,
    webhooks_config: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
    title: Optional[str] = None,
    level: str = "info"
) -> bool:
    """
    統一Webhook方式で通知を送信します（TASK-020新機能）
    
    Args:
        message: 送信するメッセージ
        webhooks_config: Webhook設定のリスト
        metadata: 通知メタデータ（metric_type, metric_value等）
        title: 通知タイトル（オプション）
        level: 通知レベル（info, warning, error）
        
    Returns:
        bool: 少なくとも1つのWebhookが成功した場合True
    """
    try:
        from .webhook_notifier import WebhookNotifier
        
        # WebhookNotifierを初期化
        notifier = WebhookNotifier(webhooks_config)
        
        # 通知データを作成
        notification = {
            "message": message,
            "title": title,
            "level": level
        }
        
        # 通知送信
        result = notifier.send(notification)
        
        # 結果を表示
        if result["success_count"] > 0:
            print(f"✅ 統一Webhook通知を送信しました ({result['success_count']}件成功)")
            success = True
        else:
            print(f"⚠️ 統一Webhook通知の送信に失敗しました ({result['error_count']}件失敗)")
            success = False
            
        # エラーがあった場合は詳細を表示
        if result["error_count"] > 0:
            for res in result["results"]:
                if not res["success"]:
                    print(f"  - {res['webhook_name']}: {res.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ 統一Webhook通知エラー: {e}")
        success = False
    
    # 履歴に保存（失敗しても通知は継続）
    if metadata and success:
        try:
            from komon.notification_history import save_notification
            save_notification(
                metric_type=metadata.get("metric_type", "unknown"),
                metric_value=metadata.get("metric_value", 0),
                message=message
            )
        except Exception as e:
            print(f"⚠️ 通知履歴の保存に失敗: {e}")
    
    return success


def send_notification_with_fallback(
    message: str,
    settings: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    title: Optional[str] = None,
    level: str = "info"
) -> bool:
    """
    統一Webhook方式と旧形式のフォールバック機能付き通知送信
    
    新形式（notifiers.webhooks）が設定されていれば新方式を使用、
    未設定なら旧形式（notifications）を使用します。
    
    Args:
        message: 送信するメッセージ
        settings: 設定辞書
        metadata: 通知メタデータ
        title: 通知タイトル
        level: 通知レベル
        
    Returns:
        bool: 通知送信成功時True
    """
    # 新形式の設定を確認
    notifiers_config = settings.get("notifiers", {})
    webhooks_config = notifiers_config.get("webhooks", [])
    
    if webhooks_config:
        # 新形式（統一Webhook）を使用
        logger.info("Using unified webhook notification system")
        return send_unified_webhook_notification(
            message=message,
            webhooks_config=webhooks_config,
            metadata=metadata,
            title=title,
            level=level
        )
    else:
        # 旧形式（個別関数）を使用
        logger.info("Using legacy notification system (fallback)")
        return _send_legacy_notifications(message, settings, metadata)


def _send_legacy_notifications(
    message: str,
    settings: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    旧形式の通知送信（フォールバック用）
    
    Args:
        message: 送信するメッセージ
        settings: 設定辞書
        metadata: 通知メタデータ
        
    Returns:
        bool: 少なくとも1つの通知が成功した場合True
    """
    notifications_config = settings.get("notifications", {})
    success_count = 0
    
    # Slack通知
    slack_config = notifications_config.get("slack", {})
    if slack_config.get("enabled", False):
        webhook_url = slack_config.get("webhook_url", "")
        if send_slack_alert(message, webhook_url, metadata):
            success_count += 1
    
    # Discord通知
    discord_config = notifications_config.get("discord", {})
    if discord_config.get("enabled", False):
        webhook_url = discord_config.get("webhook_url", "")
        if send_discord_alert(message, webhook_url, metadata):
            success_count += 1
    
    # Teams通知
    teams_config = notifications_config.get("teams", {})
    if teams_config.get("enabled", False):
        webhook_url = teams_config.get("webhook_url", "")
        if send_teams_alert(message, webhook_url, metadata):
            success_count += 1
    
    # メール通知
    email_config = notifications_config.get("email", {})
    if email_config.get("enabled", False):
        if send_email_alert(message, email_config, metadata):
            success_count += 1
    
    return success_count > 0


import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Dict, Optional

logger = logging.getLogger(__name__)


class NotificationThrottle:
    """通知頻度制御を管理するクラス"""
    
    # 閾値レベルの順序定義
    LEVEL_ORDER = {
        'warning': 1,
        'alert': 2,
        'critical': 3
    }
    
    def __init__(self, config: dict, history_file: Optional[Path] = None):
        """
        Args:
            config: settings.ymlのthrottle設定
            history_file: 履歴ファイルのパス（テスト用）
        """
        self.enabled = config.get('enabled', True)
        self.interval_minutes = config.get('interval_minutes', 60)
        self.escalation_minutes = config.get('escalation_minutes', 180)
        
        # 履歴ファイルのパス
        if history_file:
            self.history_file = history_file
        else:
            self.history_file = Path("data/notifications/throttle.json")
        
        # ディレクトリが存在しない場合は作成
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def should_send_notification(
        self,
        metric_type: str,
        threshold_level: str,
        current_value: float
    ) -> Tuple[bool, str]:
        """
        通知を送信すべきかを判定する
        
        Args:
            metric_type: メトリクスタイプ（'cpu', 'memory', 'disk'）
            threshold_level: 閾値レベル（'warning', 'alert', 'critical'）
            current_value: 現在の値
            
        Returns:
            (送信すべきか, 理由)
            理由: "first", "level_up", "escalation", "normal", "throttled"
        """
        # 頻度制御が無効の場合は常に送信
        if not self.enabled:
            return True, "disabled"
        
        # 履歴を読み込み
        history = self._load_history()
        
        # 該当メトリクスの履歴がない場合は初回通知
        if metric_type not in history:
            return True, "first"
        
        metric_history = history[metric_type]
        previous_level = metric_history.get('threshold_level')
        last_notification_time_str = metric_history.get('last_notification_time')
        first_occurrence_time_str = metric_history.get('first_occurrence_time')
        
        # 閾値レベルが上昇した場合は即座に通知
        if self._is_level_escalated(previous_level, threshold_level):
            return True, "level_up"
        
        # 前回通知からの経過時間を計算
        try:
            last_notification_time = datetime.fromisoformat(last_notification_time_str)
            elapsed_minutes = (datetime.now() - last_notification_time).total_seconds() / 60
        except (ValueError, TypeError):
            # パースエラーの場合は通知を送信
            return True, "parse_error"
        
        # 通知間隔未満の場合は抑制
        if elapsed_minutes < self.interval_minutes:
            return False, "throttled"
        
        # エスカレーション判定
        try:
            first_occurrence_time = datetime.fromisoformat(first_occurrence_time_str)
            total_elapsed_minutes = (datetime.now() - first_occurrence_time).total_seconds() / 60
            
            if total_elapsed_minutes >= self.escalation_minutes:
                return True, "escalation"
        except (ValueError, TypeError):
            pass
        
        # 通常の通知
        return True, "normal"
    
    def record_notification(
        self,
        metric_type: str,
        threshold_level: str,
        current_value: float
    ) -> None:
        """
        通知を記録する
        
        Args:
            metric_type: メトリクスタイプ（'cpu', 'memory', 'disk'）
            threshold_level: 閾値レベル（'warning', 'alert', 'critical'）
            current_value: 現在の値
        """
        history = self._load_history()
        
        now = datetime.now().isoformat()
        
        # 既存の履歴がある場合
        if metric_type in history:
            previous_level = history[metric_type].get('threshold_level')
            first_occurrence_time = history[metric_type].get('first_occurrence_time')
            
            # 閾値レベルが変わった場合は初回発生時刻をリセット
            if previous_level != threshold_level:
                first_occurrence_time = now
        else:
            # 新規の場合
            first_occurrence_time = now
        
        # 履歴を更新
        history[metric_type] = {
            'last_notification_time': now,
            'threshold_level': threshold_level,
            'value': current_value,
            'first_occurrence_time': first_occurrence_time
        }
        
        self._save_history(history)
    
    def get_duration_message(self, metric_type: str) -> Optional[str]:
        """
        継続時間のメッセージを取得する
        
        Args:
            metric_type: メトリクスタイプ
            
        Returns:
            継続時間のメッセージ（例: "3時間"）、履歴がない場合はNone
        """
        history = self._load_history()
        
        if metric_type not in history:
            return None
        
        first_occurrence_time_str = history[metric_type].get('first_occurrence_time')
        
        try:
            first_occurrence_time = datetime.fromisoformat(first_occurrence_time_str)
            elapsed = datetime.now() - first_occurrence_time
            
            hours = int(elapsed.total_seconds() / 3600)
            if hours >= 1:
                return f"{hours}時間"
            else:
                minutes = int(elapsed.total_seconds() / 60)
                return f"{minutes}分"
        except (ValueError, TypeError):
            return None
    
    def _load_history(self) -> Dict:
        """履歴ファイルを読み込む"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError, IsADirectoryError) as e:
            logger.warning(f"履歴ファイルの読み込みに失敗: {e}")
            # 破損している場合は削除して新規作成
            if self.history_file.exists():
                try:
                    if self.history_file.is_dir():
                        self.history_file.rmdir()
                    else:
                        self.history_file.unlink()
                except (OSError, PermissionError):
                    # 削除に失敗しても継続
                    pass
        
        return {}
    
    def _save_history(self, history: Dict) -> None:
        """履歴ファイルに保存する"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"履歴ファイルの保存に失敗: {e}")
    
    def _is_level_escalated(
        self,
        previous_level: Optional[str],
        current_level: str
    ) -> bool:
        """
        閾値レベルが上昇したかを判定する
        
        Args:
            previous_level: 前回の閾値レベル
            current_level: 現在の閾値レベル
            
        Returns:
            上昇した場合True
        """
        if previous_level is None:
            return False
        
        prev_order = self.LEVEL_ORDER.get(previous_level, 0)
        curr_order = self.LEVEL_ORDER.get(current_level, 0)
        
        return curr_order > prev_order
