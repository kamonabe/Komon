"""
段階的通知メッセージのプロパティベーステスト

Hypothesisを使用して、段階的メッセージ機能の正確性プロパティを検証します。
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
import pytest

from src.komon.progressive_message import (
    get_notification_count,
    generate_progressive_message,
    DEFAULT_TEMPLATES
)


# テスト用の戦略
metric_types = st.sampled_from(["cpu", "mem", "disk"])
metric_values = st.floats(min_value=0.0, max_value=100.0)
notification_counts = st.integers(min_value=1, max_value=10)
time_window_hours = st.integers(min_value=1, max_value=48)


@given(
    metric_type=metric_types,
    time_window_hours=time_window_hours,
    notification_count=st.integers(min_value=0, max_value=10)
)
@settings(max_examples=100, deadline=None)
def test_property_notification_count_accuracy(metric_type, time_window_hours, notification_count):
    """
    プロパティ1: 通知回数の正確性
    
    任意のメトリクスタイプと時間窓について、get_notification_count()は
    指定された時間窓内の同一メトリクスタイプの通知回数を正確に返すこと
    
    検証対象: 要件 AC-001.1, AC-001.2, AC-001.3
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        queue_file = f.name
        
        try:
            # テストデータを作成
            now = datetime.now()
            history = []
            
            # 時間窓内の通知を作成（境界を避けるため、少し余裕を持たせる）
            for i in range(notification_count):
                # 時間窓の半分以内に収める
                hours_ago = i * (time_window_hours / (notification_count + 2))
                timestamp = now - timedelta(hours=hours_ago)
                history.append({
                    "timestamp": timestamp.isoformat(),
                    "metric_type": metric_type,
                    "metric_value": 80.0,
                    "message": "Test message"
                })
            
            # 時間窓外の通知を追加（カウントされないはず）
            old_timestamp = now - timedelta(hours=time_window_hours + 1)
            history.append({
                "timestamp": old_timestamp.isoformat(),
                "metric_type": metric_type,
                "metric_value": 80.0,
                "message": "Old message"
            })
            
            # 異なるメトリクスタイプの通知を追加（カウントされないはず）
            other_metric = "mem" if metric_type != "mem" else "cpu"
            history.append({
                "timestamp": now.isoformat(),
                "metric_type": other_metric,
                "metric_value": 80.0,
                "message": "Other metric"
            })
            
            # ファイルに保存
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(history, f)
            
            # 通知回数を取得
            count = get_notification_count(metric_type, time_window_hours, queue_file)
            
            # 検証: 時間窓内の同一メトリクスタイプの通知のみカウントされる
            assert count == notification_count, \
                f"Expected {notification_count}, got {count}"
        
        finally:
            # クリーンアップ
            if os.path.exists(queue_file):
                os.unlink(queue_file)


@given(
    metric_type=metric_types,
    metric_value=metric_values,
    notification_count=notification_counts
)
@settings(max_examples=100, deadline=None)
def test_property_progressive_message_consistency(metric_type, metric_value, notification_count):
    """
    プロパティ2: 段階的メッセージの一貫性
    
    任意の通知回数（1, 2, 3以上）について、generate_progressive_message()は
    対応するテンプレートを使用してメッセージを生成すること
    
    検証対象: 要件 AC-002.1, AC-002.2, AC-002.3
    """
    # メッセージを生成
    message = generate_progressive_message(
        metric_type, metric_value, 90.0, notification_count
    )
    
    # 検証: メッセージが生成される
    assert isinstance(message, str)
    assert len(message) > 0
    
    # 検証: メトリクス値が含まれる
    assert str(metric_value) in message or f"{metric_value:.1f}" in message
    
    # 検証: 適切なテンプレートが使用される
    template_key = min(notification_count, 3)
    expected_template = DEFAULT_TEMPLATES[template_key]
    
    # テンプレートの一部が含まれることを確認
    if notification_count == 1:
        assert "ちょっと気になる" in message
    elif notification_count == 2:
        assert "まだ続いてます" in message
    else:  # 3以上
        assert "そろそろ見た方がいいかも" in message


@given(
    metric_type=metric_types,
    time_window_hours=st.integers(min_value=1, max_value=48)
)
@settings(max_examples=100, deadline=None)
def test_property_time_window_reset(metric_type, time_window_hours):
    """
    プロパティ3: 時間窓のリセット
    
    任意のメトリクスタイプについて、時間窓外の通知はカウントされないこと
    
    検証対象: 要件 AC-004.1, AC-004.2
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        queue_file = f.name
        
        try:
            # テストデータを作成
            now = datetime.now()
            history = []
            
            # 時間窓外の通知のみを作成
            for i in range(5):
                timestamp = now - timedelta(hours=time_window_hours + i + 1)
                history.append({
                    "timestamp": timestamp.isoformat(),
                    "metric_type": metric_type,
                    "metric_value": 80.0,
                    "message": "Old message"
                })
            
            # ファイルに保存
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(history, f)
            
            # 通知回数を取得
            count = get_notification_count(metric_type, time_window_hours, queue_file)
            
            # 検証: 時間窓外の通知はカウントされない
            assert count == 0, f"Expected 0, got {count}"
        
        finally:
            # クリーンアップ
            if os.path.exists(queue_file):
                os.unlink(queue_file)


@given(
    metric_type1=metric_types,
    metric_type2=metric_types,
    count1=st.integers(min_value=0, max_value=5),
    count2=st.integers(min_value=0, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_property_metric_type_independence(metric_type1, metric_type2, count1, count2):
    """
    プロパティ4: メトリクスタイプの独立性
    
    任意の2つの異なるメトリクスタイプについて、
    一方の通知回数は他方に影響しないこと
    
    検証対象: 要件 AC-001.4, AC-004.3
    """
    # 同じメトリクスタイプの場合はスキップ
    if metric_type1 == metric_type2:
        return
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        queue_file = f.name
        
        try:
            # テストデータを作成
            now = datetime.now()
            history = []
            
            # metric_type1の通知を作成
            for i in range(count1):
                history.append({
                    "timestamp": (now - timedelta(hours=i)).isoformat(),
                    "metric_type": metric_type1,
                    "metric_value": 80.0,
                    "message": "Test message 1"
                })
            
            # metric_type2の通知を作成
            for i in range(count2):
                history.append({
                    "timestamp": (now - timedelta(hours=i)).isoformat(),
                    "metric_type": metric_type2,
                    "metric_value": 80.0,
                    "message": "Test message 2"
                })
            
            # ファイルに保存
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(history, f)
            
            # 各メトリクスタイプの通知回数を取得
            count_result1 = get_notification_count(metric_type1, 24, queue_file)
            count_result2 = get_notification_count(metric_type2, 24, queue_file)
            
            # 検証: 各メトリクスタイプが独立してカウントされる
            assert count_result1 == count1, \
                f"Expected {count1} for {metric_type1}, got {count_result1}"
            assert count_result2 == count2, \
                f"Expected {count2} for {metric_type2}, got {count_result2}"
        
        finally:
            # クリーンアップ
            if os.path.exists(queue_file):
                os.unlink(queue_file)


@given(metric_type=metric_types)
@settings(max_examples=100, deadline=None)
def test_property_error_handling_default_behavior(metric_type):
    """
    プロパティ5: エラー時のデフォルト動作
    
    任意のエラー状態（履歴ファイル不在、破損等）について、
    get_notification_count()は0を返し、デフォルトメッセージが生成されること
    
    検証対象: 要件 AC-005.1, AC-005.2, AC-005.3
    """
    # ケース1: ファイルが存在しない
    non_existent_file = "/tmp/non_existent_file_12345.json"
    count = get_notification_count(metric_type, 24, non_existent_file)
    assert count == 0, f"Expected 0 for non-existent file, got {count}"
    
    # ケース2: 破損したファイル
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        queue_file = f.name
        f.write("invalid json content {{{")
    
    try:
        count = get_notification_count(metric_type, 24, queue_file)
        assert count == 0, f"Expected 0 for corrupted file, got {count}"
    finally:
        if os.path.exists(queue_file):
            os.unlink(queue_file)
    
    # ケース3: デフォルトメッセージが生成される
    message = generate_progressive_message(metric_type, 80.0, 90.0, 1)
    assert isinstance(message, str)
    assert len(message) > 0
