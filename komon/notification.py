import os
import requests
import smtplib
from email.message import EmailMessage


def send_slack_alert(message: str, webhook_url: str):
    """Slackに通知を送る"""
    payload = {
        "text": message
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[Slack通知エラー] {e} (HTTP {getattr(e.response, 'status_code', '?')})")
    except Exception as e:
        print(f"[Slack通知エラー（その他）] {e}")


def send_email_alert(message: str, email_config: dict):
    """メールで通知を送る"""
    try:
        # パスワードの取得（env:環境変数対応）
        password_value = email_config["password"]
        if password_value.startswith("env:"):
            env_var = password_value.split("env:")[1]
            password = os.getenv(env_var)
        else:
            password = password_value

        # メールメッセージ作成
        msg = EmailMessage()
        msg["Subject"] = "Komon 警戒情報"
        msg["From"] = email_config["from"]
        msg["To"] = email_config["to"]
        msg.set_content(message)

        with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
            if email_config.get("use_tls", True):  # デフォルトはTrue
                server.starttls()
            server.login(email_config["username"], password)
            server.send_message(msg)

    except Exception as e:
        print(f"[メール通知エラー] {e}")
