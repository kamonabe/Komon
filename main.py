import yaml
from komon.monitor import collect_detailed_resource_usage
from komon.analyzer import analyze_usage, load_thresholds
from komon.notification import send_slack_alert, send_email_alert
from komon.history import rotate_history, save_current_usage
from komon.settings_validator import validate_settings

def load_config(path: str = "settings.yml") -> dict:
    """
    YAML形式の設定ファイルを読み込み、辞書として返す。
    Args:
        path (str): 設定ファイルのパス
    Returns:
        dict: 読み込まれた設定内容
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ settings.yml の読み込みに失敗しました: {e}")
        return {}

def handle_alerts(alerts: list, config: dict):
    """
    警戒情報が存在する場合にSlackやメールで通知を送信する。
    Args:
        alerts (list): 警戒メッセージのリスト
        config (dict): 設定ファイルの内容
    """
    print("⚠️ 警戒情報:")
    for alert in alerts:
        print(f"- {alert}")

    message = "⚠️ Komon 警戒情報:\n" + "\n".join(f"- {a}" for a in alerts)
    notification_cfg = config.get("notifications", {})

    if notification_cfg.get("slack", {}).get("enabled"):
        send_slack_alert(message, notification_cfg["slack"].get("webhook_url", ""))

    if notification_cfg.get("email", {}).get("enabled"):
        send_email_alert(message, notification_cfg["email"])

def main():
    if not validate_settings("settings.yml"):
        print("❌ settings.yml に問題があります。log/komon_error.log を確認してください。")
        return

    config = load_config()
    if not config:
        return

    usage = collect_detailed_resource_usage()
    thresholds = load_thresholds(config)
    alerts = analyze_usage(usage, thresholds)

    rotate_history()
    save_current_usage(usage)

    if alerts:
        handle_alerts(alerts, config)
    else:
        print("✅ 警戒情報はありません。")

if __name__ == "__main__":
    main()
