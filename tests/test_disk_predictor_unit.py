"""
ディスク使用量予測のユニットテスト

エッジケースや特定のシナリオをテストします。
"""

import pytest
import os
import tempfile
import csv
from datetime import datetime, date, timedelta
from pathlib import Path

from komon.disk_predictor import (
    load_disk_history,
    calculate_daily_average,
    predict_disk_trend,
    detect_rapid_change,
    format_prediction_message,
    HISTORY_DIR
)


# ========================================
# データ読み込みのユニットテスト
# ========================================

def test_load_disk_history_no_directory():
    """
    ディレクトリが存在しない場合、空リストを返す
    
    **検証要件: 1.2**
    """
    # 存在しないディレクトリを指定
    import komon.disk_predictor as dp
    original_dir = dp.HISTORY_DIR
    dp.HISTORY_DIR = "/nonexistent/directory"
    
    try:
        result = load_disk_history()
        assert result == [], "存在しないディレクトリの場合、空リストを返すべき"
    finally:
        dp.HISTORY_DIR = original_dir


def test_calculate_daily_average_empty_data():
    """
    データが空の場合、空リストを返す
    
    **検証要件: 1.2**
    """
    result = calculate_daily_average([])
    assert result == [], "空データの場合、空リストを返すべき"


def test_calculate_daily_average_single_day():
    """
    1日分のデータの場合、その日の平均を返す
    """
    data = [
        (datetime(2025, 11, 25, 9, 0), 65.0),
        (datetime(2025, 11, 25, 12, 0), 70.0),
        (datetime(2025, 11, 25, 15, 0), 68.0),
    ]
    
    result = calculate_daily_average(data)
    
    assert len(result) == 1
    assert result[0][0] == date(2025, 11, 25)
    expected_avg = (65.0 + 70.0 + 68.0) / 3
    assert abs(result[0][1] - expected_avg) < 0.0001


def test_calculate_daily_average_multiple_days():
    """
    複数日のデータの場合、各日の平均を返す
    """
    data = [
        (datetime(2025, 11, 24, 9, 0), 60.0),
        (datetime(2025, 11, 24, 15, 0), 62.0),
        (datetime(2025, 11, 25, 9, 0), 65.0),
        (datetime(2025, 11, 25, 15, 0), 67.0),
    ]
    
    result = calculate_daily_average(data)
    
    assert len(result) == 2
    assert result[0][0] == date(2025, 11, 24)
    assert abs(result[0][1] - 61.0) < 0.0001
    assert result[1][0] == date(2025, 11, 25)
    assert abs(result[1][1] - 66.0) < 0.0001



# ========================================
# 予測ロジックのユニットテスト
# ========================================

def test_predict_disk_trend_insufficient_data():
    """
    データが2件未満の場合、ValueErrorを発生させる
    
    **検証要件: 1.2**
    """
    data = [(date(2025, 11, 25), 65.0)]
    
    with pytest.raises(ValueError, match="最低2件のデータが必要"):
        predict_disk_trend(data)


def test_predict_disk_trend_all_same_values():
    """
    全て同一値の場合、傾きがゼロになる
    
    **検証要件: 1.3**
    """
    data = [
        (date(2025, 11, 20), 65.0),
        (date(2025, 11, 21), 65.0),
        (date(2025, 11, 22), 65.0),
        (date(2025, 11, 23), 65.0),
    ]
    
    result = predict_disk_trend(data)
    
    assert abs(result['slope']) < 0.01, "全て同一値の場合、傾きはゼロになるべき"
    assert result['trend'] == 'stable'
    assert result['days_to_90'] is None


def test_predict_disk_trend_negative_slope():
    """
    傾きが負の値（減少傾向）の場合、90%到達予測は「該当なし」
    
    **検証要件: 2.3**
    """
    data = [
        (date(2025, 11, 20), 70.0),
        (date(2025, 11, 21), 68.0),
        (date(2025, 11, 22), 66.0),
        (date(2025, 11, 23), 64.0),
    ]
    
    result = predict_disk_trend(data)
    
    assert result['slope'] < 0, "減少傾向の場合、傾きは負になるべき"
    assert result['trend'] == 'decreasing'
    assert result['days_to_90'] is None
    assert result['prediction_date'] is None


def test_predict_disk_trend_already_above_90():
    """
    現在のディスク使用率が既に90%以上の場合
    
    **検証要件: 2.4**
    """
    data = [
        (date(2025, 11, 20), 88.0),
        (date(2025, 11, 21), 90.0),
        (date(2025, 11, 22), 92.0),
        (date(2025, 11, 23), 94.0),
    ]
    
    result = predict_disk_trend(data)
    
    assert result['current_usage'] >= 90.0
    # 既に90%以上なので、予測日は計算されない
    assert result['days_to_90'] is None


def test_predict_disk_trend_very_slow_increase():
    """
    予測日が100年以上先の場合、「当面は安全」として処理
    
    **検証要件: 2.5**
    """
    data = [
        (date(2025, 11, 20), 50.0),
        (date(2025, 11, 21), 50.001),  # 非常に遅い増加
        (date(2025, 11, 22), 50.002),
        (date(2025, 11, 23), 50.003),
    ]
    
    result = predict_disk_trend(data)
    
    # 増加傾向だが、非常に遅い
    assert result['slope'] > 0
    # 100年以上先なので、予測日は None
    assert result['days_to_90'] is None
    assert result['prediction_date'] is None



# ========================================
# 急激な変化検出のユニットテスト
# ========================================

def test_detect_rapid_change_decreasing():
    """
    減少傾向の場合、急激な変化として検出されない
    
    **検証要件: 3.4**
    """
    data = [
        (date(2025, 11, 24), 80.0),
        (date(2025, 11, 25), 65.0),  # -15%の減少
    ]
    
    result = detect_rapid_change(data)
    
    assert result['is_rapid'] is False, "減少傾向は急激な変化として検出されないべき"
    assert result['change_percent'] < 0


def test_detect_rapid_change_no_previous_data():
    """
    前日のデータが存在しない場合、前日比の計算をスキップ
    
    **検証要件: 3.5**
    """
    data = [(date(2025, 11, 25), 65.0)]
    
    result = detect_rapid_change(data)
    
    assert result['is_rapid'] is False
    assert result['change_percent'] == 0.0


def test_detect_rapid_change_exactly_10_percent():
    """
    ちょうど10%の増加の場合、急激な変化として検出される
    """
    data = [
        (date(2025, 11, 24), 70.0),
        (date(2025, 11, 25), 80.0),  # +10%
    ]
    
    result = detect_rapid_change(data)
    
    assert result['is_rapid'] is True
    assert abs(result['change_percent'] - 10.0) < 0.0001


def test_detect_rapid_change_just_below_threshold():
    """
    10%未満の増加の場合、急激な変化として検出されない
    """
    data = [
        (date(2025, 11, 24), 70.0),
        (date(2025, 11, 25), 79.9),  # +9.9%
    ]
    
    result = detect_rapid_change(data)
    
    assert result['is_rapid'] is False



# ========================================
# メッセージ生成のユニットテスト
# ========================================

def test_format_prediction_message_safe_state():
    """
    安全な状態のメッセージ
    
    **検証要件: 4.5**
    """
    prediction = {
        'slope': 0.3,
        'intercept': 60.0,
        'current_usage': 65.0,
        'days_to_90': None,
        'prediction_date': None,
        'trend': 'stable'
    }
    
    rapid_change = {
        'is_rapid': False,
        'change_percent': 2.0,
        'previous_usage': 63.0,
        'current_usage': 65.0
    }
    
    message = format_prediction_message(prediction, rapid_change)
    
    assert '✅' in message or '安定' in message
    assert '問題ありません' in message or '当面は問題' in message


def test_format_prediction_message_rapid_with_prediction():
    """
    急激な変化 + 90%到達予測のパターン
    """
    prediction = {
        'slope': 4.0,
        'intercept': 60.0,
        'current_usage': 87.5,
        'days_to_90': 3,
        'prediction_date': '2025-11-28',
        'trend': 'increasing'
    }
    
    rapid_change = {
        'is_rapid': True,
        'change_percent': 12.5,
        'previous_usage': 75.0,
        'current_usage': 87.5
    }
    
    message = format_prediction_message(prediction, rapid_change)
    
    assert '⚠️' in message or '急激' in message
    assert '90%に到達' in message
    assert '3日' in message
    assert '推奨アクション' in message or 'journalctl' in message


def test_format_prediction_message_rapid_only():
    """
    急激な変化のみのパターン
    """
    prediction = {
        'slope': 1.0,
        'intercept': 50.0,
        'current_usage': 71.0,
        'days_to_90': None,
        'prediction_date': None,
        'trend': 'increasing'
    }
    
    rapid_change = {
        'is_rapid': True,
        'change_percent': 11.0,
        'previous_usage': 60.0,
        'current_usage': 71.0
    }
    
    message = format_prediction_message(prediction, rapid_change)
    
    assert '⚠️' in message or '急激' in message
    assert '余裕があります' in message or '注意が必要' in message


def test_format_prediction_message_normal_increase_with_prediction():
    """
    通常の増加 + 90%到達予測のパターン
    """
    prediction = {
        'slope': 1.2,
        'intercept': 70.0,
        'current_usage': 82.5,
        'days_to_90': 6,
        'prediction_date': '2025-12-01',
        'trend': 'increasing'
    }
    
    rapid_change = {
        'is_rapid': False,
        'change_percent': 2.0,
        'previous_usage': 80.5,
        'current_usage': 82.5
    }
    
    message = format_prediction_message(prediction, rapid_change)
    
    assert '📊' in message or 'トレンド' in message
    assert '90%に到達' in message
    assert '6日' in message
    assert '推奨アクション' in message or 'journalctl' in message
