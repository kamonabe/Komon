"""
段階的通知メッセージモジュール

通知履歴を活用して、同一問題の繰り返し回数に応じて
段階的にメッセージを変化させる機能を提供します。
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from komon.notification_history import load_notification_history


logger = logging.getLogger(__name__)


# デフォルトテンプレート
DEFAULT_TEMPLATES = {
    1: "ちょっと気になることがあります。{metric_name}が {value}{unit} になっています。",
    2: "まだ続いてますね。{metric_name}が {value}{unit} のままです。",
    3: "そろそろ見た方がいいかも。{metric_name}が {value}{unit} の状態が続いています。"
}


# メトリクス名のマッピング
METRIC_NAMES = {
    "cpu": "CPU使用率",
    "mem": "メモリ使用率",
    "disk": "ディスク使用率"
}


# 単位のマッピング
METRIC_UNITS = {
    "cpu": "%",
    "mem": "%",
    "disk": "%"
}


def get_notification_count(
    metric_type: str,
    time_window_hours: int = 24,
    queue_file: str = "data/notifications/queue.json"
) -> int:
    """
    指定された時間窓内の同一メトリクスタイプの通知回数を取得します。
    
    Args:
        metric_type: メトリクスの種類 (cpu, mem, disk)
        time_window_hours: 時間窓（時間）
        queue_file: 通知履歴ファイルパス
        
    Returns:
        int: 通知回数（0以上）
    """
    try:
        # 通知履歴を読み込む
        history = load_notification_history(queue_file=queue_file)
        
        # 時間窓を計算
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # 同一メトリクスタイプの通知をカウント
        count = 0
        for notification in history:
            try:
                # タイムスタンプをパース
                timestamp_str = notification.get("timestamp", "")
                timestamp = datetime.fromisoformat(timestamp_str)
                
                # 時間窓内かつ同一メトリクスタイプ
                if timestamp >= cutoff_time and notification.get("metric_type") == metric_type:
                    count += 1
                    
            except (ValueError, AttributeError) as e:
                # タイムスタンプのパースエラーはスキップ
                logger.debug("Failed to parse timestamp: %s", e)
                continue
        
        return count
        
    except Exception as e:
        # エラー時は0を返す（デフォルトメッセージ）
        logger.warning("Failed to get notification count: %s", e)
        return 0


def generate_progressive_message(
    metric_type: str,
    metric_value: float,
    threshold: float,
    notification_count: int,
    templates: Optional[dict] = None
) -> str:
    """
    通知回数に応じた段階的メッセージを生成します。
    
    Args:
        metric_type: メトリクスの種類 (cpu, mem, disk)
        metric_value: 現在の値
        threshold: 閾値
        notification_count: 通知回数（1, 2, 3以上）
        templates: カスタムテンプレート（Noneの場合はデフォルト）
        
    Returns:
        str: 生成されたメッセージ
    """
    try:
        # テンプレートの選択
        if templates is None:
            templates = DEFAULT_TEMPLATES
        
        # 通知回数に応じたテンプレートを選択（3以上は3のテンプレート）
        template_key = min(notification_count, 3)
        template = templates.get(template_key, templates[1])
        
        # メトリクス名と単位を取得
        metric_name = METRIC_NAMES.get(metric_type, metric_type.upper())
        unit = METRIC_UNITS.get(metric_type, "")
        
        # メッセージを生成
        message = template.format(
            metric_name=metric_name,
            value=metric_value,
            unit=unit
        )
        
        return message
        
    except Exception as e:
        # エラー時はシンプルなメッセージを返す
        logger.error("Failed to generate progressive message: %s", e)
        return f"{metric_type.upper()}が {metric_value} になっています。"
