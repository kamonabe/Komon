"""
通知モジュール

Slack、メールなどの通知機能を提供します。
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests


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
