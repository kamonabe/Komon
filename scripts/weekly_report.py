"""
週次健全性レポートスクリプト

システムの週次健全性レポートを生成し、Slack/メールで送信します。
"""

import yaml
from komon.weekly_data import collect_weekly_data
from komon.report_formatter import format_weekly_report
from komon.notification import send_slack_alert, send_email_alert, send_discord_alert, send_teams_alert


def load_config(path: str = "settings.yml") -> dict:
    """
    YAML形式の設定ファイルを読み込みます。
    
    Args:
        path: 設定ファイルのパス
        
    Returns:
        dict: 読み込まれた設定内容
    """
    import sys
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ {path} が見つかりません")
        print("")
        print("初回セットアップを実行してください：")
        print("  python scripts/initial.py")
        print("")
        print("または、サンプルファイルをコピー：")
        print("  cp config/settings.yml.sample settings.yml")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ {path} の形式が不正です: {e}")
        print("")
        print("config/settings.yml.sampleを参考に修正してください")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


def generate_weekly_report(config: dict) -> str:
    """
    週次健全性レポートメッセージを生成します。
    
    Args:
        config: 設定ファイルの内容
        
    Returns:
        str: レポートメッセージ
    """
    try:
        # データ収集
        data = collect_weekly_data()
        
        # メッセージフォーマット
        message = format_weekly_report(data)
        
        return message
        
    except Exception as e:
        error_msg = f"❌ レポート生成エラー: {e}"
        print(error_msg)
        return error_msg


def send_report(message: str, config: dict):
    """
    レポートを設定された通知チャネルに送信します。
    
    Args:
        message: 送信するレポートメッセージ
        config: 設定ファイルの内容
    """
    notification_cfg = config.get("notifications", {})
    weekly_report_cfg = config.get("weekly_report", {})
    
    # 週次レポートの通知設定を取得（デフォルトは通常の通知設定を使用）
    report_notifications = weekly_report_cfg.get("notifications", {})
    
    # Slack通知
    slack_enabled = report_notifications.get("slack", notification_cfg.get("slack", {}).get("enabled", False))
    if slack_enabled:
        webhook_url = notification_cfg.get("slack", {}).get("webhook_url", "")
        if webhook_url:
            # 週次レポートは通知履歴に保存しない（メタデータなし）
            send_slack_alert(message, webhook_url)
        else:
            print("⚠️ Slack Webhook URLが設定されていません")
    
    # Discord通知
    discord_enabled = report_notifications.get("discord", notification_cfg.get("discord", {}).get("enabled", False))
    if discord_enabled:
        webhook_url = notification_cfg.get("discord", {}).get("webhook_url", "")
        if webhook_url:
            # 週次レポートは通知履歴に保存しない（メタデータなし）
            send_discord_alert(message, webhook_url)
        else:
            print("⚠️ Discord Webhook URLが設定されていません")
    
    # Teams通知
    teams_enabled = report_notifications.get("teams", notification_cfg.get("teams", {}).get("enabled", False))
    if teams_enabled:
        webhook_url = notification_cfg.get("teams", {}).get("webhook_url", "")
        if webhook_url:
            # 週次レポートは通知履歴に保存しない（メタデータなし）
            send_teams_alert(message, webhook_url)
        else:
            print("⚠️ Teams Webhook URLが設定されていません")
    
    # メール通知
    email_enabled = report_notifications.get("email", notification_cfg.get("email", {}).get("enabled", False))
    if email_enabled:
        email_cfg = notification_cfg.get("email", {})
        if email_cfg:
            # 週次レポートは通知履歴に保存しない（メタデータなし）
            send_email_alert(message, email_cfg)
        else:
            print("⚠️ メール設定が不完全です")


def main():
    """
    週次レポート生成のメインエントリーポイント
    """
    print("📊 週次健全性レポートを生成中...")
    
    # 設定読み込み
    config = load_config()
    if not config:
        print("❌ 設定ファイルの読み込みに失敗しました")
        return
    
    # 週次レポートが有効かチェック
    weekly_report_cfg = config.get("weekly_report", {})
    if not weekly_report_cfg.get("enabled", True):
        print("ℹ️ 週次レポートは無効になっています")
        return
    
    # レポート生成
    message = generate_weekly_report(config)
    
    # コンソール出力
    print("\n" + "="*60)
    print(message)
    print("="*60 + "\n")
    
    # 通知送信
    send_report(message, config)
    
    print("✅ 週次レポート生成完了")


if __name__ == "__main__":
    main()
