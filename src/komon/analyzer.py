"""
分析モジュール

リソース使用率の閾値判定とアラート生成を行います。
"""


def load_thresholds(config: dict) -> dict:
    """
    設定ファイルから閾値を読み込みます。
    
    Args:
        config: 設定ファイルの内容
        
    Returns:
        dict: 各リソースの閾値
    """
    thresholds = config.get("thresholds", {})
    return {
        "cpu": thresholds.get("cpu", 85),
        "mem": thresholds.get("mem", 80),
        "disk": thresholds.get("disk", 80),
        "proc_cpu": thresholds.get("proc_cpu", 20)
    }


def analyze_usage(usage: dict, thresholds: dict) -> list:
    """
    リソース使用率を分析し、閾値を超えた項目のアラートを生成します。
    
    Args:
        usage: リソース使用率データ
        thresholds: 閾値設定
        
    Returns:
        list: アラートメッセージのリスト
    """
    alerts = []
    
    if usage.get("cpu", 0) >= thresholds.get("cpu", 85):
        alerts.append(
            f"💬 ちょっと気になることがあります\n\n"
            f"CPUが頑張りすぎてるみたいです（{usage['cpu']:.1f}%）。\n"
            f"何か重い処理走ってます？"
        )
    
    if usage.get("mem", 0) >= thresholds.get("mem", 80):
        alerts.append(
            f"💬 ちょっと気になることがあります\n\n"
            f"メモリ使用量が結構増えてますね（{usage['mem']:.1f}%）。\n"
            f"使ってないプロセスとかありませんか？"
        )
    
    if usage.get("disk", 0) >= thresholds.get("disk", 80):
        alerts.append(
            f"💬 ちょっと気になることがあります\n\n"
            f"ディスクの空きが少なくなってきました（{usage['disk']:.1f}%）。\n"
            f"古いログやキャッシュが溜まってるかもしれません。"
        )
    
    return alerts
