"""
設定ファイル検証モジュール

settings.ymlの妥当性をチェックします。
"""

import os
import yaml


def validate_settings(settings_path: str = "settings.yml") -> bool:
    """
    設定ファイルの妥当性を検証します。
    
    Args:
        settings_path: 設定ファイルのパス
        
    Returns:
        bool: 検証成功時True
    """
    if not os.path.exists(settings_path):
        _log_error(f"設定ファイルが見つかりません: {settings_path}")
        return False
    
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        _log_error(f"YAML読み込みエラー: {e}")
        return False
    
    # 必須項目のチェック
    if "thresholds" not in config:
        _log_error("thresholds セクションが見つかりません")
        return False
    
    thresholds = config["thresholds"]
    for key in ["cpu", "mem", "disk"]:
        if key not in thresholds:
            _log_error(f"thresholds.{key} が設定されていません")
            return False
        
        value = thresholds[key]
        if not isinstance(value, (int, float)) or value < 0 or value > 100:
            _log_error(f"thresholds.{key} の値が不正です: {value}")
            return False
    
    # 通知設定のチェック
    if "notifications" in config:
        notifications = config["notifications"]
        
        if "slack" in notifications:
            slack = notifications["slack"]
            if slack.get("enabled") and not slack.get("webhook_url"):
                _log_error("Slack通知が有効ですが、webhook_urlが設定されていません")
                return False
        
        if "email" in notifications:
            email = notifications["email"]
            if email.get("enabled"):
                required_fields = ["smtp_server", "from", "to"]
                for field in required_fields:
                    if not email.get(field):
                        _log_error(f"メール通知が有効ですが、{field}が設定されていません")
                        return False
    
    return True


def _log_error(message: str):
    """エラーログを記録"""
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)
    
    try:
        with open(f"{log_dir}/komon_error.log", "a", encoding="utf-8") as f:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass
    
    print(f"❌ {message}")
