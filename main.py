import yaml
from komon.monitor import get_resource_usage
from komon.analyzer import analyze_usage, load_thresholds
from komon.notification import send_slack_alert, send_email_alert
from settings_validator import validate_settings


def main():
    # 設定ファイルのバリデーション
    if not validate_settings("settings.yml"):
        print("❌ settings.yml に問題があります。log/komon_error.log を確認してください。")
        return

    # 設定ファイルの読み込み
    try:
        with open("settings.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ settings.yml の読み込みに失敗しました: {e}")
        return

    # 使用状況の取得と解析
    usage = get_resource_usage()
    thresholds = load_thresholds(config)
    alerts = analyze_usage(usage, thresholds)

    # 警戒がある場合は通知
    if alerts:
        message = "⚠️ Komon 警戒情報:\n" + "\n".join(f"- {a}" for a in alerts)
        notification_cfg = config.get("notifications", {})

        if notification_cfg.get("slack", {}).get("enabled"):
            webhook_url = notification_cfg["slack"]["webhook_url"]
            send_slack_alert(message, webhook_url)

        if notification_cfg.get("email", {}).get("enabled"):
            email_cfg = notification_cfg["email"]
            send_email_alert(message, email_cfg)
    else:
        print("✅ 閾値を超えるリソース使用はありません。")


if __name__ == "__main__":
    main()
