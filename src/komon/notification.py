"""
通知モジュール

Slack、メールなどの通知機能を提供します。
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests


def send_slack_alert(message: str, webhook_url: str) -> bool:
    """
    Slackに通知を送信します。
    
    Args:
        message: 送信するメッセージ
        webhook_url: Slack Incoming Webhook URL
        
    Returns:
        bool: 送信成功時True
    """
    try:
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Slack通知を送信しました")
            return True
        else:
            print(f"⚠️ Slack通知の送信に失敗しました: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Slack通知エラー: {e}")
        return False


def send_email_alert(message: str, email_config: dict) -> bool:
    """
    メールで通知を送信します。
    
    Args:
        message: 送信するメッセージ
        email_config: メール設定（smtp_server, smtp_port, from, to, username, password等）
        
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
        return True
        
    except Exception as e:
        print(f"❌ メール通知エラー: {e}")
        return False
