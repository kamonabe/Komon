import yaml
from komon.monitor import collect_detailed_resource_usage
from komon.analyzer import analyze_usage_with_levels, load_thresholds
from komon.notification import send_slack_alert, send_email_alert, send_discord_alert, send_teams_alert, NotificationThrottle, send_notification_with_fallback
from komon.history import rotate_history, save_current_usage
from komon.settings_validator import validate_threshold_config, ValidationError

def load_config(path: str = "settings.yml") -> dict:
    """
    YAML形式の設定ファイルを読み込み、辞書として返す。
    Args:
        path (str): 設定ファイルのパス
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
        
        # プロセス情報を追加
        process_info = _get_process_info_for_metric(metric_type, usage)
        if process_info:
            message += f"\n\n📊 上位プロセス:\n{process_info}"
        
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
        
        # 通知送信（統一Webhook方式 + フォールバック）
        sent = send_notification_with_fallback(
            message=message,
            settings=config,
            metadata=metadata,
            title="Komon 警戒情報",
            level="warning" if threshold_level == "warning" else "error"
        )
        
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


def _get_process_info_for_metric(metric_type: str, usage: dict) -> str:
    """
    指定されたメトリクスに対応するプロセス情報を取得する
    
    Args:
        metric_type: メトリクスタイプ（cpu, memory, disk）
        usage: リソース使用率データ（プロセス情報を含む）
        
    Returns:
        str: フォーマットされたプロセス情報（上位3プロセス）
    """
    if metric_type == "cpu":
        processes = usage.get("cpu_by_process", [])
        if not processes:
            return ""
        
        lines = []
        for i, proc in enumerate(processes[:3], 1):
            lines.append(f"{i}. {proc['name']}: {proc['cpu']:.1f}%")
        return "\n".join(lines)
    
    elif metric_type == "memory":
        processes = usage.get("mem_by_process", [])
        if not processes:
            return ""
        
        lines = []
        for i, proc in enumerate(processes[:3], 1):
            lines.append(f"{i}. {proc['name']}: {proc['mem']:.1f}MB")
        return "\n".join(lines)
    
    # ディスクの場合はプロセス情報は表示しない（ディスク使用量はプロセス単位で取得困難）
    return ""


def main():
    config = load_config()
    if not config:
        return
    
    # 閾値設定の検証
    try:
        thresholds = validate_threshold_config(config)
    except ValidationError as e:
        print(f"❌ 設定エラー: {e}")
        return

    usage = collect_detailed_resource_usage()
    alerts, levels = analyze_usage_with_levels(usage, thresholds)

    rotate_history()
    save_current_usage(usage)

    if alerts:
        handle_alerts(alerts, levels, config, usage)
    else:
        print("✅ 警戒情報はありません。")

if __name__ == "__main__":
    main()
