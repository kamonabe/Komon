def load_thresholds(config: dict) -> dict:
    """設定から閾値を取得する"""
    return config.get("thresholds", {})


def analyze_usage(usage: dict, thresholds: dict) -> list:
    """実測値と閾値を比較して警戒情報を返す"""
    alerts = []

    for key in ["cpu", "mem", "disk"]:
        actual = usage.get(key)
        limit = thresholds.get(key)

        if actual is not None and limit is not None:
            if actual >= limit:
                alerts.append(f"{key.upper()} 使用率 {actual:.1f}% が閾値 {limit}% を超過")

    return alerts
