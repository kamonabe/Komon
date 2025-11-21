# komon/status.py

import yaml
from komon.monitor import collect_resource_usage
from komon.analyzer import load_thresholds

def show_status():
    print("📊 Komon ステータス")

    try:
        with open("settings.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ settings.yml の読み込みに失敗しました: {e}")
        return

    usage = collect_resource_usage()
    thresholds = load_thresholds(config)

    print("\n【リソース使用率】")
    for key in ["cpu", "mem", "disk"]:
        val = usage.get(key)
        th = thresholds.get(key)
        print(f" - {key.upper()}: {val:.1f}%（閾値: {th}％）")

    print("\n【通知設定】")
    notifications = config.get("notifications", {})
    slack = notifications.get("slack", {}).get("enabled", False)
    email = notifications.get("email", {}).get("enabled", False)
    print(f" - Slack通知: {'有効' if slack else '無効'}")
    print(f" - メール通知: {'有効' if email else '無効'}")

    print("\n【ログ監視対象】")
    logs = config.get("log_monitor_targets", {})
    if not logs:
        print(" - 監視対象なし")
    for log, enabled in logs.items():
        print(f" - {log}: {'✅ 有効' if enabled else '❌ 無効'}")


def show():
    show_status()


if __name__ == "__main__":
    show_status()

