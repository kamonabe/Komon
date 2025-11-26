"""
分析モジュール

リソース使用率の閾値判定とアラート生成を行います。
"""

from .settings_validator import (
    validate_threshold_config,
    determine_threshold_level,
    ThresholdLevel
)
from .progressive_message import get_notification_count, generate_progressive_message


# レベル別メッセージテンプレート
MESSAGE_TEMPLATES = {
    ThresholdLevel.WARNING: {
        "emoji": "💛",
        "prefix": "そろそろ気にかけておいた方がいいかも",
    },
    ThresholdLevel.ALERT: {
        "emoji": "🧡",
        "prefix": "ちょっと気になる水準です",
    },
    ThresholdLevel.CRITICAL: {
        "emoji": "❤️",
        "prefix": "かなり逼迫しています！",
    },
}


def load_thresholds(config: dict) -> dict:
    """
    設定ファイルから閾値を読み込みます。
    
    3段階閾値形式と従来の単一値形式の両方をサポート。
    
    Args:
        config: 設定ファイルの内容
        
    Returns:
        dict: 各リソースの閾値（3段階形式に正規化）
    """
    # 3段階閾値の検証と正規化
    normalized_thresholds = validate_threshold_config(config)
    
    # proc_cpuは従来通り単一値
    thresholds_config = config.get("thresholds", {})
    normalized_thresholds["proc_cpu"] = thresholds_config.get("proc_cpu", 20)
    
    return normalized_thresholds


def analyze_usage(usage: dict, thresholds: dict, use_progressive: bool = False) -> list:
    """
    リソース使用率を分析し、閾値を超えた項目のアラートを生成します。
    
    3段階閾値（警告/警戒/緊急）に基づいてレベル別のメッセージを生成。
    段階的通知メッセージ機能が有効な場合、通知回数に応じてメッセージを変化させます。
    
    Args:
        usage: リソース使用率データ
        thresholds: 閾値設定（3段階形式）
        use_progressive: 段階的メッセージを使用するか（デフォルト: True）
        
    Returns:
        list: アラートメッセージのリスト
    """
    alerts = []
    
    # CPU使用率のチェック
    cpu_value = usage.get("cpu", 0)
    cpu_thresholds = thresholds.get("cpu", {})
    if isinstance(cpu_thresholds, dict):
        cpu_level = determine_threshold_level(cpu_value, cpu_thresholds)
        if cpu_level != ThresholdLevel.NORMAL:
            if use_progressive:
                # 段階的メッセージを使用
                count = get_notification_count("cpu")
                message = generate_progressive_message(
                    "cpu", cpu_value, 
                    cpu_thresholds.get("critical", 90),
                    count + 1  # 現在の通知を含める
                )
                alerts.append(message)
            else:
                # 従来のメッセージを使用
                alerts.append(_generate_message("CPU", cpu_value, cpu_level))
    
    # メモリ使用率のチェック
    mem_value = usage.get("mem", 0)
    mem_thresholds = thresholds.get("mem", {})
    if isinstance(mem_thresholds, dict):
        mem_level = determine_threshold_level(mem_value, mem_thresholds)
        if mem_level != ThresholdLevel.NORMAL:
            if use_progressive:
                # 段階的メッセージを使用
                count = get_notification_count("mem")
                message = generate_progressive_message(
                    "mem", mem_value,
                    mem_thresholds.get("critical", 90),
                    count + 1  # 現在の通知を含める
                )
                alerts.append(message)
            else:
                # 従来のメッセージを使用
                alerts.append(_generate_message("メモリ", mem_value, mem_level))
    
    # ディスク使用率のチェック
    disk_value = usage.get("disk", 0)
    disk_thresholds = thresholds.get("disk", {})
    if isinstance(disk_thresholds, dict):
        disk_level = determine_threshold_level(disk_value, disk_thresholds)
        if disk_level != ThresholdLevel.NORMAL:
            if use_progressive:
                # 段階的メッセージを使用
                count = get_notification_count("disk")
                message = generate_progressive_message(
                    "disk", disk_value,
                    disk_thresholds.get("critical", 90),
                    count + 1  # 現在の通知を含める
                )
                alerts.append(message)
            else:
                # 従来のメッセージを使用
                alerts.append(_generate_message("ディスク", disk_value, disk_level))
    
    return alerts


def analyze_usage_with_levels(usage: dict, thresholds: dict) -> tuple:
    """
    リソース使用率を分析し、アラートと閾値レベル情報を返します。
    
    Args:
        usage: リソース使用率データ
        thresholds: 閾値設定（3段階形式）
        
    Returns:
        tuple: (アラートメッセージのリスト, レベル情報の辞書)
        レベル情報: {"cpu": ("warning", 75.0), "mem": ("alert", 85.0), ...}
    """
    alerts = []
    levels = {}
    
    # CPU使用率のチェック
    cpu_value = usage.get("cpu", 0)
    cpu_thresholds = thresholds.get("cpu", {})
    if isinstance(cpu_thresholds, dict):
        cpu_level = determine_threshold_level(cpu_value, cpu_thresholds)
        if cpu_level != ThresholdLevel.NORMAL:
            alerts.append(_generate_message("CPU", cpu_value, cpu_level))
            levels["cpu"] = (cpu_level.value, cpu_value)
    
    # メモリ使用率のチェック
    mem_value = usage.get("mem", 0)
    mem_thresholds = thresholds.get("mem", {})
    if isinstance(mem_thresholds, dict):
        mem_level = determine_threshold_level(mem_value, mem_thresholds)
        if mem_level != ThresholdLevel.NORMAL:
            alerts.append(_generate_message("メモリ", mem_value, mem_level))
            levels["memory"] = (mem_level.value, mem_value)
    
    # ディスク使用率のチェック
    disk_value = usage.get("disk", 0)
    disk_thresholds = thresholds.get("disk", {})
    if isinstance(disk_thresholds, dict):
        disk_level = determine_threshold_level(disk_value, disk_thresholds)
        if disk_level != ThresholdLevel.NORMAL:
            alerts.append(_generate_message("ディスク", disk_value, disk_level))
            levels["disk"] = (disk_level.value, disk_value)
    
    return alerts, levels


def _generate_message(metric_name: str, value: float, level: ThresholdLevel) -> str:
    """
    レベルに応じたアラートメッセージを生成する。
    
    Args:
        metric_name: メトリクス名（CPU、メモリ、ディスク）
        value: 現在の値
        level: 閾値レベル
        
    Returns:
        str: フォーマットされたアラートメッセージ
    """
    template = MESSAGE_TEMPLATES[level]
    emoji = template["emoji"]
    prefix = template["prefix"]
    
    # メトリクス別の詳細メッセージ
    detail_messages = {
        "CPU": {
            ThresholdLevel.WARNING: "CPUが少し頑張り始めてます。",
            ThresholdLevel.ALERT: "CPUが頑張りすぎてるみたいです。何か重い処理走ってます？",
            ThresholdLevel.CRITICAL: "CPUがかなり高負荷です！早めに確認した方がいいかもしれません。",
        },
        "メモリ": {
            ThresholdLevel.WARNING: "メモリ使用量が増えてきました。",
            ThresholdLevel.ALERT: "メモリ使用量が結構増えてますね。使ってないプロセスとかありませんか？",
            ThresholdLevel.CRITICAL: "メモリがかなり逼迫しています！不要なプロセスを停止することをお勧めします。",
        },
        "ディスク": {
            ThresholdLevel.WARNING: "ディスクの空きが少しずつ減ってきました。",
            ThresholdLevel.ALERT: "ディスクの空きが少なくなってきました。古いログやキャッシュが溜まってるかもしれません。",
            ThresholdLevel.CRITICAL: "ディスクの空きがほとんどありません！早急にクリーンアップが必要です。",
        },
    }
    
    detail = detail_messages.get(metric_name, {}).get(
        level,
        f"{metric_name}が高い状態です。"
    )
    
    return (
        f"{emoji} {prefix}\n\n"
        f"{metric_name}使用率: {value:.1f}%\n"
        f"{detail}"
    )
