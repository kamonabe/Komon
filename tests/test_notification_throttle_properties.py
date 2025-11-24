"""
通知頻度制御のプロパティベーステスト

hypothesis を使用して、通知頻度制御の正確性プロパティを検証します。
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from hypothesis import given, strategies as st
import pytest

from komon.notification import NotificationThrottle


class TestNotificationThrottleProperties:
    """NotificationThrottleクラスのプロパティベーステスト"""
    
    @given(
        metric_type=st.sampled_from(['cpu', 'memory', 'disk']),
        threshold_level=st.sampled_from(['warning', 'alert', 'critical']),
        interval_minutes=st.integers(min_value=1, max_value=120)
    )
    def test_throttle_interval_property(self, metric_type, threshold_level, interval_minutes):
        """
        P1: 通知抑制の正確性
        同一メトリクスの通知が、設定された間隔内に2回以上送信されない
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': interval_minutes},
                history_file=history_file
            )
            
            # 1回目の通知
            should_send_1, reason_1 = throttle.should_send_notification(
                metric_type, threshold_level, 80.0
            )
            assert should_send_1 is True
            assert reason_1 == "first"
            
            throttle.record_notification(metric_type, threshold_level, 80.0)
            
            # 間隔内の2回目の通知（同じレベル）
            should_send_2, reason_2 = throttle.should_send_notification(
                metric_type, threshold_level, 81.0
            )
            assert should_send_2 is False
            assert reason_2 == "throttled"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    @given(
        metric_type=st.sampled_from(['cpu', 'memory', 'disk']),
        previous_level=st.sampled_from(['warning', 'alert']),
        interval_minutes=st.integers(min_value=1, max_value=120)
    )
    def test_level_escalation_immediate_property(self, metric_type, previous_level, interval_minutes):
        """
        P2: 閾値レベル上昇時の即時通知
        閾値レベルが上昇した場合、通知間隔に関わらず即座に通知される
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': interval_minutes},
                history_file=history_file
            )
            
            # 1回目の通知
            throttle.record_notification(metric_type, previous_level, 75.0)
            
            # レベルが上昇した場合（間隔内でも通知される）
            next_level = 'critical' if previous_level == 'alert' else 'alert'
            should_send, reason = throttle.should_send_notification(
                metric_type, next_level, 85.0
            )
            assert should_send is True
            assert reason == "level_up"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    @given(
        notifications=st.lists(
            st.tuples(
                st.sampled_from(['cpu', 'memory', 'disk']),
                st.sampled_from(['warning', 'alert', 'critical']),
                st.floats(min_value=0.0, max_value=100.0)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_history_persistence_property(self, notifications):
        """
        P4: 履歴ファイルの整合性
        履歴ファイルの読み書きが正しく行われ、データが失われない
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 複数の通知を記録
            for metric_type, threshold_level, value in notifications:
                throttle.record_notification(metric_type, threshold_level, value)
            
            # 新しいインスタンスで履歴を読み込み
            throttle2 = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            history = throttle2._load_history()
            
            # 最後の通知が正しく記録されている
            # 同じメトリクスタイプの最後の通知のみが保存される
            last_notifications = {}
            for metric_type, threshold_level, value in notifications:
                last_notifications[metric_type] = (threshold_level, value)
            
            for metric_type, (expected_level, expected_value) in last_notifications.items():
                assert metric_type in history
                assert history[metric_type]['threshold_level'] == expected_level
                # 浮動小数点の比較は近似値で
                assert abs(history[metric_type]['value'] - expected_value) < 0.01
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    @given(
        metric_type=st.sampled_from(['cpu', 'memory', 'disk']),
        threshold_level=st.sampled_from(['warning', 'alert', 'critical']),
        notification_count=st.integers(min_value=1, max_value=10)
    )
    def test_throttle_disabled_property(self, metric_type, threshold_level, notification_count):
        """
        P5: 設定無効時の動作
        頻度制御が無効の場合、全ての通知が送信される
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': False, 'interval_minutes': 60},
                history_file=history_file
            )
            
            for i in range(notification_count):
                should_send, reason = throttle.should_send_notification(
                    metric_type, threshold_level, 80.0 + i
                )
                assert should_send is True
                assert reason == "disabled"
                throttle.record_notification(metric_type, threshold_level, 80.0 + i)
        
        finally:
            if history_file.exists():
                history_file.unlink()
