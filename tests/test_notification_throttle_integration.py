"""
通知頻度制御の統合テスト

既存の通知機能との統合をテストします。
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from komon.notification import NotificationThrottle


class TestNotificationThrottleIntegration:
    """通知頻度制御の統合テスト"""
    
    def test_integration_with_settings(self):
        """設定ファイルからの読み込みテスト"""
        config = {
            'enabled': True,
            'interval_minutes': 30,
            'escalation_minutes': 120
        }
        
        throttle = NotificationThrottle(config)
        
        assert throttle.enabled is True
        assert throttle.interval_minutes == 30
        assert throttle.escalation_minutes == 120
    
    def test_integration_missing_config(self):
        """設定が欠けている場合のデフォルト値"""
        config = {}
        
        throttle = NotificationThrottle(config)
        
        assert throttle.enabled is True
        assert throttle.interval_minutes == 60
        assert throttle.escalation_minutes == 180
    
    def test_integration_partial_config(self):
        """一部の設定のみ指定された場合"""
        config = {
            'enabled': False
        }
        
        throttle = NotificationThrottle(config)
        
        assert throttle.enabled is False
        assert throttle.interval_minutes == 60
        assert throttle.escalation_minutes == 180
    
    def test_workflow_first_alert(self):
        """初回アラートのワークフロー"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 初回アラート
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 75.0)
            assert should_send is True
            assert reason == "first"
            
            # 通知を記録
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # 履歴が保存されている
            history = throttle._load_history()
            assert 'cpu' in history
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_workflow_repeated_alert(self):
        """繰り返しアラートのワークフロー"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 1回目
            should_send, _ = throttle.should_send_notification('cpu', 'warning', 75.0)
            assert should_send is True
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # 2回目（抑制される）
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 76.0)
            assert should_send is False
            assert reason == "throttled"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_workflow_level_escalation(self):
        """レベル上昇のワークフロー"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 1回目（warning）
            should_send, _ = throttle.should_send_notification('cpu', 'warning', 75.0)
            assert should_send is True
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # 2回目（alert）- レベル上昇
            should_send, reason = throttle.should_send_notification('cpu', 'alert', 85.0)
            assert should_send is True
            assert reason == "level_up"
            throttle.record_notification('cpu', 'alert', 85.0)
            
            # 3回目（alert）- 同じレベル（抑制される）
            should_send, reason = throttle.should_send_notification('cpu', 'alert', 86.0)
            assert should_send is False
            assert reason == "throttled"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_workflow_disabled(self):
        """頻度制御無効時のワークフロー"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': False, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # 1回目
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 75.0)
            assert should_send is True
            assert reason == "disabled"
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # 2回目（無効なので送信される）
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 76.0)
            assert should_send is True
            assert reason == "disabled"
        
        finally:
            if history_file.exists():
                history_file.unlink()
    
    def test_workflow_multiple_metrics(self):
        """複数メトリクスのワークフロー"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            history_file = Path(f.name)
        
        try:
            throttle = NotificationThrottle(
                {'enabled': True, 'interval_minutes': 60},
                history_file=history_file
            )
            
            # CPU通知
            should_send, _ = throttle.should_send_notification('cpu', 'warning', 75.0)
            assert should_send is True
            throttle.record_notification('cpu', 'warning', 75.0)
            
            # メモリ通知（独立して初回扱い）
            should_send, reason = throttle.should_send_notification('memory', 'warning', 75.0)
            assert should_send is True
            assert reason == "first"
            throttle.record_notification('memory', 'warning', 75.0)
            
            # ディスク通知（独立して初回扱い）
            should_send, reason = throttle.should_send_notification('disk', 'alert', 85.0)
            assert should_send is True
            assert reason == "first"
            throttle.record_notification('disk', 'alert', 85.0)
            
            # CPU通知（抑制される）
            should_send, reason = throttle.should_send_notification('cpu', 'warning', 76.0)
            assert should_send is False
            assert reason == "throttled"
            
            # メモリ通知（抑制される）
            should_send, reason = throttle.should_send_notification('memory', 'warning', 76.0)
            assert should_send is False
            assert reason == "throttled"
        
        finally:
            if history_file.exists():
                history_file.unlink()
