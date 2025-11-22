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

def handle_alerts(alerts: list, config: dict, usage: dict):
    """
    警戒情報が存在する場合にSlackやメールで通知を送信する。
    Args:
        alerts (list): 警戒メッセージのリスト
        config (dict): 設定ファイルの内容
        usage (dict): リソース使用率データ
    """
    print("⚠️ 警戒情報:")
    for alert in alerts:
        print(f"- {alert}")

    message = "⚠️ Komon 警戒情報:\n" + "\n".join(f"- {a}" for a in alerts)
    notification_cfg = config.get("notifications", {})
    
    # メタデータを作成（最も高い使用率のメトリクスを記録）
    metadata = _extract_metadata_from_usage(usage)

    if notification_cfg.get("slack", {}).get("enabled"):
        send_slack_alert(message, notification_cfg["slack"].get("webhook_url", ""), metadata)

    if notification_cfg.get("email", {}).get("enabled"):
        send_email_alert(message, notification_cfg["email"], metadata)


def _extract_metadata_from_usage(usage: dict) -> dict:
    """
    使用率データから通知メタデータを抽出します。
    最も使用率が高いメトリクスを選択します。
    
    Args:
        usage: リソース使用率データ
        
    Returns:
        dict: メタデータ（metric_type, metric_value）
    """
    metrics = [
        ("cpu", usage.get("cpu", 0)),
        ("mem", usage.get("mem", 0)),
        ("disk", usage.get("disk", 0))
    ]
    
    # 最も使用率が高いメトリクスを選択
    metric_type, metric_value = max(metrics, key=lambda x: x[1])
    
    return {
        "metric_type": metric_type,
        "metric_value": metric_value
    }

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
        handle_alerts(alerts, config, usage)
    else:
        print("✅ 警戒情報はありません。")

if __name__ == "__main__":
    main()
