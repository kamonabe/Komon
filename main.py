import yaml
from komon.monitor import collect_usage
from komon.analyzer import load_thresholds, analyze_usage
from komon.history import rotate_history, save_current_usage
from komon.notification import send_slack_alert, send_email_alert

# 設定ファイル読み込み
with open("settings.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 使用状況取得
usage = collect_usage()

# 閾値ロード＆判定
thresholds = load_thresholds(config)
alerts = analyze_usage(usage, thresholds)

# 履歴保存
rotate_history()
save_current_usage(usage)

# 警戒情報の表示
if alerts:
    print("⚠️ 警戒情報:")
    for alert in alerts:
        print(f"- {alert}")

    # 通知処理
    notification_cfg = config.get("notifications", {})

    if notification_cfg.get("slack", {}).get("enabled"):
        webhook_url = notification_cfg["slack"]["webhook_url"]
        slack_msg = "⚠️ Komon 警戒情報:\n" + "\n".join(f"- {a}" for a in alerts)
        send_slack_alert(slack_msg, webhook_url)

    if notification_cfg.get("email", {}).get("enabled"):
        email_cfg = notification_cfg["email"]
        email_msg = "⚠️ Komon 警戒情報:\n" + "\n".join(f"- {a}" for a in alerts)
        send_email_alert(email_msg, email_cfg)

else:
    print("✅ 警戒情報はありません。")
