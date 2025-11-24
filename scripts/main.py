import yaml
from komon.monitor import collect_detailed_resource_usage
from komon.analyzer import analyze_usage_with_levels, load_thresholds
from komon.notification import send_slack_alert, send_email_alert, NotificationThrottle
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

def handle_alerts(alerts: list, levels: dict, config: dict, usage: dict):
    """
    警戒情報が存在する場合にSlackやメールで通知を送信する。
    Args:
        alerts (list): 警戒メッセージのリスト
        levels (dict): 閾値レベル情報 {"cpu": ("warning", 75.0), ...}
        config (dict): 設定ファイルの内容
        usage (dict): リソース使用率データ
    """
    print("⚠️ 警戒情報:")
    for alert in alerts:
        print(f"- {alert}")

    # 通知頻度制御の初期化
    throttle_config = config.get("throttle", {})
    throttle = NotificationThrottle(throttle_config)
    
    # 各メトリクスについて通知判定
    notification_cfg = config.get("notifications", {})
    
    for metric_type, (threshold_level, current_value) in levels.items():
        # 通知すべきかを判定
        should_send, reason = throttle.should_send_notification(
            metric_type, threshold_level, current_value
        )
        
        if not should_send:
            print(f"ℹ️ {metric_type}の通知を抑制しました（理由: {reason}）")
            continue
        
        # メッセージを作成
        metric_alert = next((a for a in alerts if _is_metric_alert(a, metric_type)), None)
        if not metric_alert:
            continue
        
        message = f"⚠️ Komon 警戒情報:\n{metric_alert}"
        
        # エスカレーションメッセージを追加
        if reason == "escalation":
            duration = throttle.get_duration_message(metric_type)
            if duration:
                message += f"\n\n⏰ {duration}経過しましたが、まだ高い状態が続いています"
        
        # メタデータを作成
        metadata = {
            "metric_type": metric_type,
            "metric_value": current_value
        }
        
        # 通知送信
        sent = False
        if notification_cfg.get("slack", {}).get("enabled"):
            sent = send_slack_alert(message, notification_cfg["slack"].get("webhook_url", ""), metadata) or sent
        
        if notification_cfg.get("email", {}).get("enabled"):
            sent = send_email_alert(message, notification_cfg["email"], metadata) or sent
        
        # 送信成功時に履歴を記録
        if sent:
            throttle.record_notification(metric_type, threshold_level, current_value)
            print(f"✅ {metric_type}の通知を送信しました（理由: {reason}）")


def _is_metric_alert(alert: str, metric_type: str) -> bool:
    """
    アラートメッセージが特定のメトリクスに関するものかを判定する
    
    Args:
        alert: アラートメッセージ
        metric_type: メトリクスタイプ（cpu, memory, disk）
        
    Returns:
        bool: 該当する場合True
    """
    metric_names = {
        "cpu": "CPU",
        "memory": "メモリ",
        "disk": "ディスク"
    }
    
    metric_name = metric_names.get(metric_type, "")
    return metric_name in alert


def main():
    if not validate_settings("settings.yml"):
        print("❌ settings.yml に問題があります。log/komon_error.log を確認してください。")
        return

    config = load_config()
    if not config:
        return

    usage = collect_detailed_resource_usage()
    thresholds = load_thresholds(config)
    alerts, levels = analyze_usage_with_levels(usage, thresholds)

    rotate_history()
    save_current_usage(usage)

    if alerts:
        handle_alerts(alerts, levels, config, usage)
    else:
        print("✅ 警戒情報はありません。")

if __name__ == "__main__":
    main()
