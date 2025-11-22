"""
通知履歴機能のプロパティベーステスト

Feature: notification-history
"""

import json
import os
import tempfile
import shutil
from datetime import datetime
from hypothesis import given, strategies as st, settings
from hypothesis import assume

from komon.notification_history import (
    save_notification,
    load_notification_history,
    format_notification,
    MAX_QUEUE_SIZE
)


# カスタム戦略: 有効なメトリクスタイプ
metric_types = st.sampled_from(["cpu", "mem", "disk", "log"])

# カスタム戦略: メトリクス値（0.0から100.0の範囲）
metric_values = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)

# カスタム戦略: メッセージ（空でない文字列）
messages = st.text(min_size=1, max_size=200)


class TestNotificationPersistence:
    """
    Property 1: Notification persistence
    Feature: notification-history, Property 1: Notification persistence
    """
    
    @settings(max_examples=100)
    @given(
        metric_type=metric_types,
        metric_value=metric_values,
        message=messages
    )
    def test_saved_notification_is_retrievable(self, metric_type, metric_value, message):
        """
        For any notification with valid metric_type, metric_value, and message,
        calling save_notification should result in that notification being present
        in the queue file.
        
        Validates: Requirements 1.1, 1.2
        """
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "queue.json")
            
            # 通知を保存
            result = save_notification(metric_type, metric_value, message, queue_file)
            assert result is True, "save_notification should return True"
            
            # 保存された通知を読み込み
            history = load_notification_history(queue_file)
            
            # 通知が存在することを確認
            assert len(history) > 0, "History should contain at least one notification"
            
            # 最新の通知（先頭）が保存したものと一致することを確認
            latest = history[0]
            assert latest["metric_type"] == metric_type
            assert abs(latest["metric_value"] - metric_value) < 0.01  # 浮動小数点の比較
            assert latest["message"] == message
            assert "timestamp" in latest


class TestMaximumQueueSize:
    """
    Property 2: Maximum queue size invariant
    Feature: notification-history, Property 2: Maximum queue size invariant
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        num_notifications=st.integers(min_value=1, max_value=150)
    )
    def test_queue_never_exceeds_max_size(self, num_notifications):
        """
        For any sequence of save operations, the queue file should never contain
        more than 100 notifications.
        
        Validates: Requirements 1.4, 3.1
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "queue.json")
            
            # 指定された数の通知を保存
            for i in range(num_notifications):
                save_notification(
                    metric_type="cpu",
                    metric_value=float(i % 100),
                    message=f"Test message {i}",
                    queue_file=queue_file
                )
            
            # 履歴を読み込み
            history = load_notification_history(queue_file)
            
            # 最大サイズを超えていないことを確認
            assert len(history) <= MAX_QUEUE_SIZE, \
                f"Queue size {len(history)} should not exceed {MAX_QUEUE_SIZE}"
            
            # 100件以上保存した場合は、ちょうど100件になっているはず
            if num_notifications >= MAX_QUEUE_SIZE:
                assert len(history) == MAX_QUEUE_SIZE, \
                    f"Queue should contain exactly {MAX_QUEUE_SIZE} notifications"


class TestChronologicalOrder:
    """
    Property 3: Chronological order preservation
    Feature: notification-history, Property 3: Chronological order preservation
    """
    
    @settings(max_examples=100, deadline=500)
    @given(
        num_notifications=st.integers(min_value=2, max_value=50)
    )
    def test_chronological_order_is_preserved(self, num_notifications):
        """
        For any queue state, after adding a new notification, all remaining
        notifications should maintain their chronological order (newest first).
        
        Validates: Requirements 3.2
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "queue.json")
            
            # 複数の通知を順番に保存
            for i in range(num_notifications):
                save_notification(
                    metric_type="mem",
                    metric_value=float(i),
                    message=f"Message {i}",
                    queue_file=queue_file
                )
            
            # 履歴を読み込み
            history = load_notification_history(queue_file)
            
            # タイムスタンプが新しい順（降順）になっていることを確認
            timestamps = [datetime.fromisoformat(n["timestamp"]) for n in history]
            
            for i in range(len(timestamps) - 1):
                assert timestamps[i] >= timestamps[i + 1], \
                    "Timestamps should be in descending order (newest first)"
            
            # メッセージの順序も確認（最新が先頭）
            # 最後に保存したものが先頭にあるはず
            assert history[0]["message"] == f"Message {num_notifications - 1}"


class TestHistoryRetrievalWithLimit:
    """
    Property 4: History retrieval with limit
    Feature: notification-history, Property 4: History retrieval with limit
    """
    
    @settings(max_examples=100, deadline=500)
    @given(
        num_notifications=st.integers(min_value=1, max_value=50),
        limit=st.integers(min_value=1, max_value=30)
    )
    def test_limit_returns_correct_number(self, num_notifications, limit):
        """
        For any queue with N notifications and limit value L,
        load_notification_history(limit=L) should return exactly min(N, L)
        most recent notifications.
        
        Validates: Requirements 2.2
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "queue.json")
            
            # 通知を保存
            for i in range(num_notifications):
                save_notification(
                    metric_type="disk",
                    metric_value=float(i),
                    message=f"Notification {i}",
                    queue_file=queue_file
                )
            
            # limit指定で読み込み
            history = load_notification_history(queue_file, limit=limit)
            
            # 期待される件数を確認
            expected_count = min(num_notifications, limit)
            assert len(history) == expected_count, \
                f"Should return {expected_count} notifications, got {len(history)}"
            
            # 最新のものから順に返されていることを確認
            if len(history) > 0:
                # 最新の通知が先頭にあるはず
                assert history[0]["message"] == f"Notification {num_notifications - 1}"


class TestFormatCompleteness:
    """
    Property 5: Format completeness
    Feature: notification-history, Property 5: Format completeness
    """
    
    @settings(max_examples=100)
    @given(
        metric_type=metric_types,
        metric_value=metric_values,
        message=messages
    )
    def test_formatted_string_contains_all_fields(self, metric_type, metric_value, message):
        """
        For any valid notification, format_notification should produce a string
        containing the timestamp, metric_type, metric_value, and message.
        
        Validates: Requirements 2.3
        """
        # 通知データを作成
        notification = {
            "timestamp": datetime.now().isoformat(),
            "metric_type": metric_type,
            "metric_value": metric_value,
            "message": message
        }
        
        # フォーマット
        formatted = format_notification(notification)
        
        # すべてのフィールドが含まれていることを確認
        assert isinstance(formatted, str), "Formatted output should be a string"
        assert len(formatted) > 0, "Formatted output should not be empty"
        
        # メトリクスタイプが含まれている（大文字変換される）
        assert metric_type.upper() in formatted, \
            f"Formatted string should contain metric type '{metric_type.upper()}'"
        
        # メトリクス値が含まれている
        assert str(metric_value) in formatted or f"{metric_value:.1f}" in formatted, \
            "Formatted string should contain metric value"
        
        # メッセージが含まれている
        assert message in formatted, "Formatted string should contain message"
        
        # タイムスタンプの一部が含まれている（年だけでも確認）
        year = datetime.now().year
        assert str(year) in formatted, "Formatted string should contain timestamp"


class TestGracefulErrorHandling:
    """
    Property 6: Graceful error handling
    Feature: notification-history, Property 6: Graceful error handling
    """
    
    @settings(max_examples=100)
    @given(
        corrupted_content=st.one_of(
            st.just("not json"),
            st.just("{invalid json}"),
            st.just("[1, 2, 3"),
            st.just('{"key": "value"'),
            st.just(""),
            st.just("null"),
            st.just("123"),
            st.just('{"not": "a list"}')
        )
    )
    def test_corrupted_file_does_not_crash(self, corrupted_content):
        """
        For any corrupted or invalid queue file, load_notification_history
        should not crash and should return an empty list or raise a handled exception.
        
        Validates: Requirements 2.5, 3.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "queue.json")
            
            # 破損したファイルを作成
            os.makedirs(os.path.dirname(queue_file), exist_ok=True)
            with open(queue_file, "w", encoding="utf-8") as f:
                f.write(corrupted_content)
            
            # 読み込みを試みる（クラッシュしないことを確認）
            try:
                history = load_notification_history(queue_file)
                # 空のリストが返されるはず
                assert isinstance(history, list), "Should return a list"
                assert len(history) == 0, "Should return empty list for corrupted file"
            except Exception as e:
                # 例外が発生した場合は、適切にハンドリングされているか確認
                # （実装では例外を握りつぶして空リストを返すので、ここには来ないはず）
                assert False, f"Should not raise exception, but got: {e}"
    
    def test_missing_file_returns_empty_list(self):
        """
        存在しないファイルを読み込んでも、空のリストが返されることを確認
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "nonexistent.json")
            
            history = load_notification_history(queue_file)
            
            assert isinstance(history, list), "Should return a list"
            assert len(history) == 0, "Should return empty list for missing file"
