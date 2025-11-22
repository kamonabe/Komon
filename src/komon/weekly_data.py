"""
週次データ収集モジュール

週次健全性レポートのためのデータ収集と分析機能を提供します。
"""

import os
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from komon.notification_history import load_notification_history


HISTORY_DIR = "data/usage_history"


def collect_weekly_data() -> dict:
    """
    過去7日間のリソース使用率データを収集し、先週比を計算します。
    
    Returns:
        dict: {
            'period': {'start': '2025-11-18', 'end': '2025-11-24'},
            'resources': {
                'cpu': {'current': 45.2, 'previous': 43.1, 'change': +2.1, 'trend': 'stable'},
                'mem': {'current': 62.8, 'previous': 64.3, 'change': -1.5, 'trend': 'stable'},
                'disk': {'current': 68.5, 'previous': 65.3, 'change': +3.2, 'trend': 'increasing'}
            },
            'alerts': [...]
        }
    """
    # 期間の計算
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # 今週のデータ（直近7日）
    current_data = calculate_average_usage(days=7)
    
    # 先週のデータ（8-14日前）
    previous_data = calculate_average_usage(days=7, offset_days=7)
    
    # 警戒履歴の取得
    alerts = get_alert_history(days=7)
    
    # リソースごとのデータを構築
    resources = {}
    for resource in ['cpu', 'mem', 'disk']:
        current = current_data.get(resource, 0)
        previous = previous_data.get(resource, 0)
        
        # 変化率の計算
        if previous > 0:
            change = ((current - previous) / previous) * 100
        else:
            change = 0
        
        # トレンド分析
        trend = analyze_trend(current, previous)
        
        resources[resource] = {
            'current': round(current, 1),
            'previous': round(previous, 1),
            'change': round(change, 1),
            'trend': trend
        }
    
    return {
        'period': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        },
        'resources': resources,
        'alerts': alerts
    }


def calculate_average_usage(days: int = 7, offset_days: int = 0) -> dict:
    """
    指定期間のリソース使用率の平均値を計算します。
    
    Args:
        days: 計算する日数
        offset_days: 何日前から計算するか（0=今日から、7=7日前から）
        
    Returns:
        dict: {'cpu': 45.2, 'mem': 62.8, 'disk': 68.5}
    """
    if not os.path.exists(HISTORY_DIR):
        return {'cpu': 0, 'mem': 0, 'disk': 0}
    
    # 対象期間の計算
    end_date = datetime.now() - timedelta(days=offset_days)
    start_date = end_date - timedelta(days=days)
    
    # 履歴ファイルの取得
    history_files = sorted(
        Path(HISTORY_DIR).glob("usage_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # データの収集
    cpu_values = []
    mem_values = []
    disk_values = []
    
    for file_path in history_files:
        try:
            # ファイル名から日時を取得（usage_20251122_093000.csv）
            filename = file_path.stem
            date_str = filename.replace('usage_', '')
            file_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
            
            # 期間内のファイルのみ処理
            if start_date <= file_date <= end_date:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            cpu_values.append(float(row.get('cpu', 0)))
                            mem_values.append(float(row.get('mem', 0)))
                            disk_values.append(float(row.get('disk', 0)))
                            break  # 最初の行のみ
                        except (ValueError, KeyError):
                            continue
        except (ValueError, Exception):
            continue
    
    # 平均値の計算
    result = {
        'cpu': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
        'mem': sum(mem_values) / len(mem_values) if mem_values else 0,
        'disk': sum(disk_values) / len(disk_values) if disk_values else 0
    }
    
    return result


def get_alert_history(days: int = 7) -> list:
    """
    過去N日間の警戒通知を取得します。
    
    Args:
        days: 取得する日数
        
    Returns:
        list: [
            {'timestamp': '2025-11-20 15:30', 'type': 'cpu', 'message': '...'},
            ...
        ]
    """
    # 通知履歴を全件取得
    all_notifications = load_notification_history()
    
    # 対象期間の計算
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # 期間内の通知をフィルタリング
    filtered_alerts = []
    for notification in all_notifications:
        try:
            timestamp_str = notification.get('timestamp', '')
            notification_date = datetime.fromisoformat(timestamp_str)
            
            if notification_date >= cutoff_date:
                # フォーマットを整える
                formatted_time = notification_date.strftime('%m/%d %H:%M')
                filtered_alerts.append({
                    'timestamp': formatted_time,
                    'type': notification.get('metric_type', 'unknown'),
                    'message': notification.get('message', '')
                })
        except (ValueError, AttributeError):
            continue
    
    return filtered_alerts


def analyze_trend(current: float, previous: float, threshold: float = 5.0) -> str:
    """
    リソース使用率のトレンドを分析します。
    
    Args:
        current: 現在の値
        previous: 前回の値
        threshold: 変化の閾値（%）
        
    Returns:
        str: 'stable', 'increasing', または 'decreasing'
    """
    if previous == 0:
        return 'stable'
    
    change_percent = ((current - previous) / previous) * 100
    
    if change_percent >= threshold:
        return 'increasing'
    elif change_percent <= -threshold:
        return 'decreasing'
    else:
        return 'stable'
