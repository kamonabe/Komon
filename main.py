import yaml
from komon.monitor import collect_detailed_resource_usage
from komon.analyzer import analyze_usage, load_thresholds
from komon.notification import send_slack_alert, send_email_alert
from komon.history import rotate_history, save_current_usage
from komon.settings_validator import validate_settings


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

    # 使用状況の取得
    usage = collect_detailed_resource_usage()

    # 閾値読み込みと解析
    thresholds = load_thresholds(config)
    alerts = analyze_usage(usage, thresholds)

    # 使用履歴の保存（最大95世代）
    rotate_history()
    save_current_usage(usage)

    # 通知処理
    if alerts:
        print("⚠️ 警戒情報:")
        for alert in alerts:
            print(f"- {alert}")

        message = "⚠️ Komon 警戒情報:\n" + "\n".join(f"- {a}" for a in alerts)
        notification_cfg = config.get("notifications", {})

        if notification_cfg.get("slack", {}).get("enabled"):
            webhook_url = notification_cfg["slack"]["webhook_url"]
            send_slack_alert(message, webhook_url)

        if notification_cfg.get("email", {}).get("enabled"):
            email_cfg = notification_cfg["email"]
            send_email_alert(message, email_cfg)
    else:
        print("✅ 警戒情報はありません。")


if __name__ == "__main__":
    main()
