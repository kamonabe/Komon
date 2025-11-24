"""
通知頻度制御のユニットテスト

NotificationThrottleクラスの各メソッドをテストします。
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from komon.notification import NotificationThrottle


class TestNotificationThrottle:
    """NotificationThrottleクラスのユニットテスト"""
    
    def test_init_default_config(self):
        """デフォルト設定での初期化"""
        throttle = NotificationThrottle({})
        
        assert throttle.enabled is True
        assert throttle.interval_minutes == 60
        assert throttle.escalation_minutes == 180
    
    def test_init_custom_config(self):
        """カスタム設定での初期化"""
        config = {
            'enabled': False,
            'interval_minutes': 30,
            'escalation_minutes': 120
        }
        throttle = NotificationThrottle(config)
        
        assert throttle.enabled is False
        assert throttle.interval_minutes == 30
        assert throttle.escalation_minutes == 120
    
    def test_first_notification(self):
        """初回通知は常に送信される"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 75.0)
            
            assert should_send is True
            assert reason == "first"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_throttled_notification(self):
        """間隔内の通知は抑制される"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 1回目の通知
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # 2回目の通知（間隔内）
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 76.0)
            
            assert should_send is False
            assert reason == "throttled"
        
        finally:
            if history_file.exists():
                history_file.unlink()

    
    def test_level_escalation(self):
        """閾値レベルが上昇した場合は即座に通知"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 1回目の通知（warning）
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # 2回目の通知（alert）- レベルが上昇
            should_send, reason = throttle.should_send_notification('cpu', 'alert', 85.0)
            
            assert should_send is True
            assert reason == "level_up"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_level_same(self):
        """閾値レベルが同じ場合は通常の抑制ルール"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 1回目の通知（alert）
            throttle.record_notification('cpu', 'alert', 85.0)
            
            # 2回目の通知（alert）- レベルが同じ
            should_send, reason = throttle.should_send_notification('cpu', 'alert', 86.0)
            
            assert should_send is False
            assert reason == "throttled"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_level_down(self):
        """閾値レベルが下がった場合は通常の抑制ルール"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 1回目の通知（critical）
            throttle.record_notification('cpu', 'critical', 95.0)
            
            # 2回目の通知（alert）- レベルが下がった
            should_send, reason = throttle.should_send_notification('cpu', 'alert', 85.0)
            
            assert should_send is False
            assert reason == "throttled"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_record_notification(self):
        """通知記録が正しく保存される"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # 履歴を読み込んで確認
            history = throttle._load_history()
            
            assert 'cpu' in history
            assert history['cpu']['threshold_level'] == 'warning'
            assert history['cpu']['value'] == 75.0
            assert 'last_notification_time' in history['cpu']
            assert 'first_occurrence_time' in history['cpu']
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_record_notification_level_change(self):
        """閾値レベルが変わった場合、初回発生時刻がリセットされる"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 1回目の通知（warning）
            throttle.record_notification('cpu', 'warning', 75.0)
            history1 = throttle._load_history()
            first_occurrence_1 = history1['cpu']['first_occurrence_time']
            
            # 2回目の通知（alert）- レベルが変わった
            throttle.record_notification('cpu', 'alert', 85.0)
            history2 = throttle._load_history()
            first_occurrence_2 = history2['cpu']['first_occurrence_time']
            
            # 初回発生時刻が更新されている
            assert first_occurrence_1 != first_occurrence_2
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_get_duration_message(self):
        """継続時間メッセージの取得"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 通知を記録
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # 継続時間メッセージを取得
            duration = throttle.get_duration_message('cpu')
            
            assert duration is not None
            # 直後なので「0分」または「1分」程度
            assert '分' in duration or '時間' in duration
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_get_duration_message_no_history(self):
        """履歴がない場合はNoneを返す"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            duration = throttle.get_duration_message('cpu')
            
            assert duration is None
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_load_history_file_not_exists(self):
        """履歴ファイルが存在しない場合は空の辞書を返す"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        # ファイルを削除
        history_file.unlink()
        
        throttle = NotificationThrottle(
            {'enabled': True, 'interval_minutes': 60},
            history_file=history_file
        )
        
        history = throttle._load_history()
        
        assert history == {}
    
    def test_load_history_corrupted_file(self):
        """破損した履歴ファイルは削除して空の辞書を返す"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
            f.write("invalid json content")
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            history = throttle._load_history()
            
            assert history == {}
            # ファイルが削除されている
            assert not history_file.exists()
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_is_level_escalated(self):
        """閾値レベル上昇判定のテスト"""
        throttle = NotificationThrottle({'enabled': True})
        
        # warning -> alert: 上昇
        assert throttle._is_level_escalated('warning', 'alert') is True
        
        # warning -> critical: 上昇
        assert throttle._is_level_escalated('warning', 'critical') is True
        
        # alert -> critical: 上昇
        assert throttle._is_level_escalated('alert', 'critical') is True
        
        # alert -> warning: 下降
        assert throttle._is_level_escalated('alert', 'warning') is False
        
        # warning -> warning: 同じ
        assert throttle._is_level_escalated('warning', 'warning') is False
        
        # None -> warning: 初回（上昇ではない）
        assert throttle._is_level_escalated(None, 'warning') is False
    
    def test_multiple_metrics(self):
        """複数のメトリクスが独立して管理される"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # CPU通知を記録
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # メモリ通知は初回扱い
            should_send, reason = throttle.should_send_notification('memory', 'warning', 75.0)
            assert should_send is True
            assert reason == "first"
            
            # CPU通知は抑制される
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 76.0)
            assert should_send is False
            assert reason == "throttled"
        
        finally:
            if history_file.exists():
                history_file.unlink()

    
    def test_get_duration_message_hours(self):
        """継続時間が1時間以上の場合、時間単位で表示される"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 3時間前の通知を記録
            from datetime import datetime, timedelta
            three_hours_ago = (datetime.now() - timedelta(hours=3)).isoformat()
            
            history = {
                'cpu': {
                    'last_notification_time': three_hours_ago,
                    'threshold_level': 'warning',
                    'value': 75.0,
                    'first_occurrence_time': three_hours_ago
                }
            }
            throttle._save_history(history)
            
            # 継続時間メッセージを取得
            duration = throttle.get_duration_message('cpu')
            
            assert duration is not None
            assert '時間' in duration
        
        finally:
            if history_file.exists():
                history_file.unlink()

    
    def test_parse_error_in_last_notification_time(self):
        """最終通知時刻のパースエラー時は通知を送信"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 不正な日時形式の履歴を作成
            history = {
                'cpu': {
                    'last_notification_time': 'invalid-datetime',
                    'threshold_level': 'warning',
                    'value': 75.0,
                    'first_occurrence_time': 'invalid-datetime'
                }
            }
            throttle._save_history(history)
            
            # パースエラーが発生するが、通知は送信される
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 76.0)
            
            assert should_send is True
            assert reason == "parse_error"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_parse_error_in_first_occurrence_time(self):
        """初回発生時刻のパースエラー時はエスカレーション判定をスキップ"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 1, 'escalation_minutes': 1},
                history_file=history_file
            )
            
            # 最終通知時刻は正常、初回発生時刻は不正
            from datetime import datetime, timedelta
            two_hours_ago = (datetime.now() - timedelta(hours=2)).isoformat()
            
            history = {
                'cpu': {
                    'last_notification_time': two_hours_ago,
                    'threshold_level': 'warning',
                    'value': 75.0,
                    'first_occurrence_time': 'invalid-datetime'
                }
            }
            throttle._save_history(history)
            
            # エスカレーション判定はスキップされ、通常の通知として扱われる
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 76.0)
            
            assert should_send is True
            assert reason == "normal"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_save_history_io_error(self):
        """履歴保存時のIOエラーをログに記録"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # ファイルを削除してディレクトリに置き換える（書き込み不可にする）
            history_file.unlink()
            history_file.mkdir(parents=True, exist_ok=True)
            
            # IOエラーが発生するが、例外は発生しない
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # エラーが発生しても処理は継続される
            assert True
        
        finally:
            # クリーンアップ
            if history_file.exists():
                if history_file.is_dir():
                    history_file.rmdir()
                else:
                    history_file.unlink()

    
    def test_escalation_after_long_duration(self):
        """長時間経過後にエスカレーション通知が送信される"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60, 'escalation_minutes': 180},
                history_file=history_file
            )
            
            # 4時間前の通知を記録
            from datetime import datetime, timedelta
            four_hours_ago = (datetime.now() - timedelta(hours=4)).isoformat()
            
            history = {
                'cpu': {
                    'last_notification_time': four_hours_ago,
                    'threshold_level': 'warning',
                    'value': 75.0,
                    'first_occurrence_time': four_hours_ago
                }
            }
            throttle._save_history(history)
            
            # エスカレーション通知が送信される
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 76.0)
            
            assert should_send is True
            assert reason == "escalation"
        
        finally:
            if history_file.exists():
                history_file.unlink()
