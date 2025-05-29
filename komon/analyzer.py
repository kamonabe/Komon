# komon/analyzer.py

import yaml

def load_thresholds(path="settings.yml") -> dict:
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("thresholds", {})

def analyze_usage(usage: dict, thresholds: dict) -> dict:
    alerts = {}
    for k in usage:
        if usage[k] >= thresholds.get(k, 100):  # デフォルト100なら警告なし
            alerts[k] = usage[k]
    return alerts
