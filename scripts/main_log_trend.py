import yaml
from komon.log_trends import analyze_log_trend
from komon.notification import send_slack_alert, send_email_alert, send_discord_alert, send_teams_alert, send_notification_with_fallback

def main():
    # 設定ファイルの読み込み
    try:
        with open("settings.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ settings.yml の読み込みに失敗しました: {e}")
        return

    # 監視対象ログを取得
    monitor_targets = config.get("log_monitor_targets", {})
    log_ids = [path.strip("/").replace("/", "_") if path != "systemd journal" else "systemd_journal"
               for path, enabled in monitor_targets.items() if enabled]

    if not log_ids:
        print("⚠️ 有効なログ監視対象が設定されていません。")
        return

    # 閾値取得（なければデフォルト）
    threshold = config.get("log_trend_threshold", 30)

    # ログ傾向分析の実行
    print("🔍 ログ傾向分析を開始します")
    alerts = []
    for log_id in log_ids:
        result = analyze_log_trend(log_id, threshold_percent=threshold)
        print(result)
        if "急増の可能性" in result:
            alerts.append(result)

    # 通知が必要な場合のみ送信
    if alerts:
        message = "⚠️ Komon ログ傾向警戒情報:\n" + "\n".join(alerts)
        notification_cfg = config.get("notifications", {})

        # 統一Webhook通知（新形式 + フォールバック）
        send_notification_with_fallback(
            message=message,
            settings=config,
            metadata=None,
            title="Komon ログ傾向警戒情報",
            level="warning"
        )

    else:
        print("✅ 異常な傾向は検出されませんでした。")

if __name__ == "__main__":
    main()
