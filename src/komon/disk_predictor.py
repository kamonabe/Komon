"""
ディスク使用量の増加トレンド予測モジュール

過去のディスク使用率データから線形回帰により将来の使用量を予測し、
ディスク容量が90%に到達する予測日を算出します。
また、前日比で10%以上の急激な増加を検出し、早期警告を発します。
"""

import os
import csv
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional


# 定数定義
HISTORY_DIR = "data/usage_history"
RAPID_CHANGE_THRESHOLD = 10.0  # 急激な変化の閾値（%）
TARGET_USAGE = 90.0  # 予測対象のディスク使用率（%）
SAFE_PREDICTION_DAYS = 36500  # 100年（当面は安全とみなす日数）



def load_disk_history(days: int = 7) -> list[tuple[datetime, float]]:
    """
    過去N日分のディスク使用率データを読み込みます。
    
    Args:
        days: 読み込む日数（デフォルト: 7）
        
    Returns:
        list[tuple[datetime, float]]: [(日時, ディスク使用率), ...]
        
    エラーハンドリング:
        - ディレクトリが存在しない場合: 空リストを返す
        - ファイルが読めない場合: そのファイルをスキップ
        - 数値変換エラー: そのレコードをスキップ
    """
    if not os.path.exists(HISTORY_DIR):
        return []
    
    # 対象期間の計算
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 履歴ファイルの取得
    history_files = sorted(
        Path(HISTORY_DIR).glob("usage_*.csv"),
        key=lambda p: p.stat().st_mtime
    )
    
    # データの収集
    data = []
    
    for file_path in history_files:
        try:
            # ファイル名から日時を取得（usage_20251122_093000.csv）
            filename = file_path.stem
            date_str = filename.replace('usage_', '')
            file_datetime = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
            
            # 期間内のファイルのみ処理
            if start_date <= file_datetime <= end_date:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            disk_usage = float(row.get('disk', 0))
                            data.append((file_datetime, disk_usage))
                            break  # 最初の行のみ
                        except (ValueError, KeyError):
                            # 数値変換エラーはスキップ
                            continue
        except (ValueError, Exception):
            # ファイル読み込みエラーはスキップ
            continue
    
    # 日時でソート
    data.sort(key=lambda x: x[0])
    
    return data



def calculate_daily_average(data: list[tuple[datetime, float]]) -> list[tuple[date, float]]:
    """
    時系列データから日次平均値を計算します。
    
    Args:
        data: [(日時, ディスク使用率), ...]
        
    Returns:
        list[tuple[date, float]]: [(日付, 平均使用率), ...]
    """
    if not data:
        return []
    
    # 日付でグループ化
    daily_data = {}
    for dt, usage in data:
        day = dt.date()
        if day not in daily_data:
            daily_data[day] = []
        daily_data[day].append(usage)
    
    # 各日の平均値を計算
    daily_averages = []
    for day, usages in daily_data.items():
        avg_usage = sum(usages) / len(usages)
        daily_averages.append((day, avg_usage))
    
    # 日付でソート
    daily_averages.sort(key=lambda x: x[0])
    
    return daily_averages



def predict_disk_trend(daily_data: list[tuple[date, float]]) -> dict:
    """
    線形回帰により将来のディスク使用量を予測します。
    
    Args:
        daily_data: [(日付, 平均使用率), ...]
        
    Returns:
        dict: {
            'slope': float,              # 傾き（%/日）
            'intercept': float,          # 切片
            'current_usage': float,      # 現在の使用率
            'days_to_90': int | None,    # 90%到達までの日数
            'prediction_date': str | None, # 90%到達予測日（YYYY-MM-DD形式）
            'trend': str                 # 'increasing', 'stable', 'decreasing'
        }
        
    Raises:
        ValueError: データ件数が2件未満の場合
    """
    if len(daily_data) < 2:
        raise ValueError("予測には最低2件のデータが必要です")
    
    # データを数値に変換（日付を0からの日数に変換）
    base_date = daily_data[0][0]
    x_values = [(d - base_date).days for d, _ in daily_data]
    y_values = [usage for _, usage in daily_data]
    
    n = len(x_values)
    
    # 最小二乗法で傾きと切片を計算
    # slope = (n * Σxy - Σx * Σy) / (n * Σx² - (Σx)²)
    # intercept = (Σy - slope * Σx) / n
    
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x_squared = sum(x * x for x in x_values)
    
    denominator = n * sum_x_squared - sum_x * sum_x
    
    if denominator == 0:
        # 全てのx値が同じ（1日分のデータ）
        slope = 0.0
        intercept = sum_y / n
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
    
    # 現在の使用率（最新日のデータ）
    current_usage = y_values[-1]
    
    # トレンド判定
    if slope > 0.01:
        trend = 'increasing'
    elif slope < -0.01:
        trend = 'decreasing'
    else:
        trend = 'stable'
    
    # 90%到達予測日の計算
    days_to_90 = None
    prediction_date = None
    
    if slope > 0.001 and current_usage < TARGET_USAGE:
        # 増加傾向で、まだ90%未満の場合
        try:
            days_to_90_float = (TARGET_USAGE - current_usage) / slope
            
            # infinityやNaNのチェック
            if days_to_90_float > SAFE_PREDICTION_DAYS or days_to_90_float != days_to_90_float:
                # 100年以上先またはNaNの場合は「当面は安全」
                days_to_90 = None
                prediction_date = None
            else:
                days_to_90 = int(days_to_90_float)
                # 予測日を計算
                latest_date = daily_data[-1][0]
                pred_date = latest_date + timedelta(days=days_to_90)
                prediction_date = pred_date.strftime('%Y-%m-%d')
        except (OverflowError, ValueError):
            # オーバーフローやエラーの場合は予測なし
            days_to_90 = None
            prediction_date = None
    
    return {
        'slope': slope,
        'intercept': intercept,
        'current_usage': current_usage,
        'days_to_90': days_to_90,
        'prediction_date': prediction_date,
        'trend': trend
    }



def detect_rapid_change(daily_data: list[tuple[date, float]]) -> dict:
    """
    前日比で急激な変化を検出します。
    
    Args:
        daily_data: [(日付, 平均使用率), ...]
        
    Returns:
        dict: {
            'is_rapid': bool,           # 急激な変化があるか
            'change_percent': float,    # 前日比の変化率（%）
            'previous_usage': float,    # 前日の使用率
            'current_usage': float      # 現在の使用率
        }
    """
    # データが2件未満の場合
    if len(daily_data) < 2:
        return {
            'is_rapid': False,
            'change_percent': 0.0,
            'previous_usage': 0.0,
            'current_usage': daily_data[0][1] if daily_data else 0.0
        }
    
    # 最新日と前日のデータを取得
    previous_usage = daily_data[-2][1]
    current_usage = daily_data[-1][1]
    
    # 前日比を計算
    change_percent = current_usage - previous_usage
    
    # 10%以上の増加の場合、急激な変化とする
    is_rapid = change_percent >= RAPID_CHANGE_THRESHOLD
    
    return {
        'is_rapid': is_rapid,
        'change_percent': change_percent,
        'previous_usage': previous_usage,
        'current_usage': current_usage
    }



def format_prediction_message(prediction: dict, rapid_change: dict) -> str:
    """
    予測結果を分かりやすいメッセージに変換します。
    
    Args:
        prediction: 予測結果
        rapid_change: 急激な変化の検出結果
        
    Returns:
        str: フォーマットされたメッセージ
    """
    messages = []
    
    # 優先度1: 急激な変化の警告
    if rapid_change['is_rapid']:
        messages.append("⚠️ ディスク使用量が急激に増加しています！")
        messages.append(
            f"前日比: +{rapid_change['change_percent']:.1f}%"
            f"（{rapid_change['previous_usage']:.1f}% → {rapid_change['current_usage']:.1f}%）"
        )
        messages.append("")
    
    # 優先度2: 90%到達予測
    if prediction['days_to_90'] is not None:
        # 急激な変化がない場合は、トレンド情報も表示
        if not rapid_change['is_rapid']:
            messages.append("📊 ディスク使用量の増加トレンド")
            messages.append(f"現在の使用率: {prediction['current_usage']:.1f}%")
            messages.append(f"増加率: +{prediction['slope']:.2f}%/日")
            messages.append("")
        
        messages.append(f"このままだと、あと{prediction['days_to_90']}日で90%に到達する見込みです。")
        messages.append(f"予測到達日: {prediction['prediction_date']}")
        messages.append("")
        
        # 推奨アクション
        messages.append("💡 推奨アクション：")
        messages.append("- 古いログファイルを削除: journalctl --vacuum-time=7d")
        messages.append("- 不要なファイルを確認: du -sh /* | sort -h")
    elif rapid_change['is_rapid']:
        # 急激な変化はあるが、90%到達予測がない場合
        messages.append("現在の増加率では90%到達まで余裕がありますが、")
        messages.append("急激な変化が続く場合は注意が必要です。")
    else:
        # 優先度3: 通常の増加トレンド
        if prediction['trend'] == 'increasing':
            messages.append("📊 ディスク使用量の増加トレンド")
            messages.append(f"現在の使用率: {prediction['current_usage']:.1f}%")
            messages.append(f"増加率: +{prediction['slope']:.2f}%/日")
            messages.append("")
            messages.append("当面は問題ありませんが、定期的な確認をお勧めします。")
        elif prediction['trend'] == 'decreasing':
            messages.append("✅ ディスク使用量は減少傾向です")
            messages.append(f"現在の使用率: {prediction['current_usage']:.1f}%")
            messages.append(f"減少率: {prediction['slope']:.2f}%/日")
            messages.append("")
            messages.append("問題ありません。")
        else:
            # 安全な状態
            messages.append("✅ ディスク使用量は安定しています")
            messages.append(f"現在の使用率: {prediction['current_usage']:.1f}%")
            messages.append(f"増加率: +{prediction['slope']:.2f}%/日")
            messages.append("")
            messages.append("当面は問題ありません。")
    
    return "\n".join(messages)
