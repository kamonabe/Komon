import os
import yaml
import datetime

ERROR_LOG_FILE = "log/komon_error.log"


def log_error(message: str):
    os.makedirs("log", exist_ok=True)
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")


def validate_settings(filepath="settings.yml") -> bool:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        log_error(f"settings.yml 読み込みエラー: {e}")
        return False

    valid = True

    # 必須セクションの存在チェック
    required_sections = ["thresholds", "notifications", "log_monitor_targets"]
    for section in required_sections:
        if section not in config:
            log_error(f"設定ファイルに `{section}` セクションが見つかりません。")
            valid = False

    # 閾値の型チェック
    thresholds = config.get("thresholds", {})
    for key in ["cpu", "mem", "disk"]:
        value = thresholds.get(key)
        if not isinstance(value, (int, float)):
            log_error(f"`thresholds.{key}` は数値である必要があります。")
            valid = False

    # 通知設定チェック
    notifications = config.get("notifications", {})
    for method in ["slack", "email"]:
        if method in notifications:
            enabled = notifications[method].get("enabled")
            if not isinstance(enabled, bool):
                log_error(f"`notifications.{method}.enabled` は true または false で指定してください。")
                valid = False

    return valid
