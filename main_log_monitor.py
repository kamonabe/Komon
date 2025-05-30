import yaml
from komon.log_watcher import LogWatcher
from komon.log_analyzer import check_log_anomaly
from komon.notification import send_slack_alert, send_email_alert


def main():
    # 設定ファイルの読み込み
    try:
        with open("settings.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ settings.yml の読み込みに失敗しました: {e}")
        return

    # ログ監視と差分行数取得
    watcher = LogWatcher()
    diff_results = watcher.watch_logs()  # {'/var/log/messages': 50, ...}

    alerts = []
    for path, line_count in diff_results.items():
        alert = check_log_anomaly(path, line_count, config)
        if alert:
            print(f"⚠️ {alert}")
            alerts.append(alert)

    # 警戒がある場合は通知
    if alerts:
        message = "⚠️ Komon ログ警戒情報:\n" + "\n".join(f"- {a}" for a in alerts)
        notification_cfg = config.get("notifications", {})

        if notification_cfg.get("slack", {}).get("enabled"):
            webhook_url = notification_cfg["slack"]["webhook_url"]
            send_slack_alert(message, webhook_url)

        if notification_cfg.get("email", {}).get("enabled"):
            email_cfg = notification_cfg["email"]
            send_email_alert(message, email_cfg)

    else:
        print("✅ ログに異常はありません。")


if __name__ == "__main__":
    main()
