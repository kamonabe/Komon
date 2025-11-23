"""
設定バリデータモジュール

閾値設定の検証と正規化を行います。
"""

from enum import Enum
from typing import Dict, Union


class ThresholdLevel(Enum):
    """閾値レベルの列挙型"""
    NORMAL = "normal"      # 正常
    WARNING = "warning"    # 警告（黄色）
    ALERT = "alert"        # 警戒（オレンジ）
    CRITICAL = "critical"  # 緊急（赤）


class ValidationError(Exception):
    """設定検証エラー"""
    pass


def validate_threshold_config(config: dict) -> dict:
    """
    閾値設定を検証し、正規化する。
    
    従来の単一値形式と新しい3段階形式の両方をサポート。
    単一値の場合は、3段階形式に正規化する。
    
    Args:
        config: 設定ファイルの内容
        
    Returns:
        dict: 正規化された3段階閾値設定
        
    Raises:
        ValidationError: 設定が無効な場合
    """
    thresholds = config.get("thresholds", {})
    normalized = {}
    
    for metric in ["cpu", "mem", "disk"]:
        threshold_value = thresholds.get(metric)
        
        if threshold_value is None:
            # デフォルト値を使用
            normalized[metric] = _get_default_thresholds(metric)
        elif isinstance(threshold_value, dict):
            # 3段階形式
            normalized[metric] = _validate_three_tier(metric, threshold_value)
        elif isinstance(threshold_value, (int, float)):
            # 従来の単一値形式 → 3段階に正規化
            normalized[metric] = _normalize_single_threshold(threshold_value)
        else:
            raise ValidationError(
                f"閾値 '{metric}' の形式が無効です。数値または辞書形式で指定してください。"
            )
    
    return normalized


def _get_default_thresholds(metric: str) -> dict:
    """
    デフォルトの3段階閾値を返す。
    
    Args:
        metric: メトリクス名（cpu, mem, disk）
        
    Returns:
        dict: デフォルトの3段階閾値
    """
    defaults = {
        "cpu": {"warning": 70, "alert": 85, "critical": 95},
        "mem": {"warning": 70, "alert": 80, "critical": 90},
        "disk": {"warning": 70, "alert": 80, "critical": 90},
    }
    return defaults.get(metric, {"warning": 70, "alert": 80, "critical": 90})


def _normalize_single_threshold(value: Union[int, float]) -> dict:
    """
    単一閾値を3段階形式に正規化する。
    
    従来の単一閾値Tを、以下のように変換：
    - warning: T - 10
    - alert: T
    - critical: T + 10
    
    Args:
        value: 単一閾値
        
    Returns:
        dict: 3段階閾値
    """
    return {
        "warning": max(0, value - 10),
        "alert": value,
        "critical": min(100, value + 10)
    }


def _validate_three_tier(metric: str, thresholds: dict) -> dict:
    """
    3段階閾値の妥当性を検証する。
    
    Args:
        metric: メトリクス名
        thresholds: 3段階閾値の辞書
        
    Returns:
        dict: 検証済みの3段階閾値
        
    Raises:
        ValidationError: 閾値が無効な場合
    """
    required_keys = ["warning", "alert", "critical"]
    
    # 必須キーの存在確認
    for key in required_keys:
        if key not in thresholds:
            raise ValidationError(
                f"閾値 '{metric}' に '{key}' が指定されていません。"
            )
    
    warning = thresholds["warning"]
    alert = thresholds["alert"]
    critical = thresholds["critical"]
    
    # 数値型の確認
    for key, value in [("warning", warning), ("alert", alert), ("critical", critical)]:
        if not isinstance(value, (int, float)):
            raise ValidationError(
                f"閾値 '{metric}.{key}' は数値で指定してください（現在: {type(value).__name__}）。"
            )
    
    # 範囲の確認（0-200: CPUバーストを考慮）
    for key, value in [("warning", warning), ("alert", alert), ("critical", critical)]:
        if not (0 <= value <= 200):
            raise ValidationError(
                f"閾値 '{metric}.{key}' は 0-200 の範囲で指定してください（現在: {value}）。"
            )
    
    # 順序の確認
    if not (warning < alert < critical):
        raise ValidationError(
            f"閾値 '{metric}' の順序が無効です。warning < alert < critical である必要があります。\n"
            f"現在: warning={warning}, alert={alert}, critical={critical}"
        )
    
    return {
        "warning": warning,
        "alert": alert,
        "critical": critical
    }


def determine_threshold_level(value: float, thresholds: dict) -> ThresholdLevel:
    """
    値と3段階閾値に基づいて閾値レベルを判定する。
    
    Args:
        value: 判定対象の値
        thresholds: 3段階閾値の辞書（warning, alert, critical）
        
    Returns:
        ThresholdLevel: 判定されたレベル
    """
    if value < 0:
        # 負の値は正常として扱う
        return ThresholdLevel.NORMAL
    
    if value >= thresholds["critical"]:
        return ThresholdLevel.CRITICAL
    elif value >= thresholds["alert"]:
        return ThresholdLevel.ALERT
    elif value >= thresholds["warning"]:
        return ThresholdLevel.WARNING
    else:
        return ThresholdLevel.NORMAL
