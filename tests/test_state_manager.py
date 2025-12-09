"""
Tests for network state manager.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import pytest

from komon.net.state_manager import NetworkStateManager


class TestNetworkStateManager:
    """Tests for NetworkStateManager class."""
    
    def test_init_with_new_file(self, tmp_path):
        """Test initialization with new state file."""
        state_file = tmp_path / "state.json"
        
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        assert manager.state == {}
        assert manager.retention_hours == 24
    
    def test_init_with_existing_file(self, tmp_path):
        """Test initialization with existing state file."""
        state_file = tmp_path / "state.json"
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
        initial_state = {
            "net.ping:8.8.8.8": {
                "first_detected_at": recent_time
            }
        }
        state_file.write_text(json.dumps(initial_state))
        
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        assert len(manager.state) == 1
        assert "net.ping:8.8.8.8" in manager.state
    
    def test_check_state_change_ok_to_ng(self, tmp_path):
        """Test state change from OK to NG."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        result = manager.check_state_change("ping", "8.8.8.8", False)
        
        assert result == "ok_to_ng"
        assert "net.ping:8.8.8.8" in manager.state
    
    def test_check_state_change_ng_to_ok(self, tmp_path):
        """Test state change from NG to OK."""
        state_file = tmp_path / "state.json"
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
        initial_state = {
            "net.ping:8.8.8.8": {
                "first_detected_at": recent_time
            }
        }
        state_file.write_text(json.dumps(initial_state))
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        result = manager.check_state_change("ping", "8.8.8.8", True)
        
        assert result == "ng_to_ok"
        assert "net.ping:8.8.8.8" not in manager.state
    
    def test_check_state_change_ok_to_ok(self, tmp_path):
        """Test no state change (OK to OK)."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        result = manager.check_state_change("ping", "8.8.8.8", True)
        
        assert result is None
        assert "net.ping:8.8.8.8" not in manager.state
    
    def test_check_state_change_ng_to_ng(self, tmp_path):
        """Test no state change (NG to NG)."""
        state_file = tmp_path / "state.json"
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
        initial_state = {
            "net.ping:8.8.8.8": {
                "first_detected_at": recent_time
            }
        }
        state_file.write_text(json.dumps(initial_state))
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        result = manager.check_state_change("ping", "8.8.8.8", False)
        
        assert result is None
        assert "net.ping:8.8.8.8" in manager.state
    
    def test_cleanup_expired_states(self, tmp_path):
        """Test cleanup of expired NG states."""
        state_file = tmp_path / "state.json"
        old_time = (datetime.now() - timedelta(hours=25)).isoformat() + "Z"
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
        
        initial_state = {
            "net.ping:old.example.com": {
                "first_detected_at": old_time
            },
            "net.ping:recent.example.com": {
                "first_detected_at": recent_time
            }
        }
        state_file.write_text(json.dumps(initial_state))
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        # Trigger cleanup by checking state
        manager.check_state_change("ping", "test.example.com", True)
        
        assert "net.ping:old.example.com" not in manager.state
        assert "net.ping:recent.example.com" in manager.state
    
    def test_get_ng_count(self, tmp_path):
        """Test getting NG count."""
        state_file = tmp_path / "state.json"
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
        initial_state = {
            "net.ping:8.8.8.8": {
                "first_detected_at": recent_time
            },
            "net.http:https://example.com": {
                "first_detected_at": recent_time
            }
        }
        state_file.write_text(json.dumps(initial_state))
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        count = manager.get_ng_count()
        
        assert count == 2
    
    def test_get_ng_targets(self, tmp_path):
        """Test getting NG targets."""
        state_file = tmp_path / "state.json"
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
        initial_state = {
            "net.ping:8.8.8.8": {
                "first_detected_at": recent_time
            },
            "net.http:https://example.com": {
                "first_detected_at": recent_time
            }
        }
        state_file.write_text(json.dumps(initial_state))
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        targets = manager.get_ng_targets()
        
        assert len(targets) == 2
        assert "net.ping:8.8.8.8" in targets
        assert "net.http:https://example.com" in targets
    
    def test_format_notification_message_ping_ok_to_ng(self, tmp_path):
        """Test formatting notification message for ping OK to NG."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        message = manager.format_notification_message(
            "ping", "8.8.8.8", "ok_to_ng", "Google DNS"
        )
        
        assert "❌" in message
        assert "Ping失敗" in message
        assert "Google DNS" in message
        assert "8.8.8.8" in message
    
    def test_format_notification_message_ping_ng_to_ok(self, tmp_path):
        """Test formatting notification message for ping NG to OK."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        message = manager.format_notification_message(
            "ping", "8.8.8.8", "ng_to_ok", "Google DNS"
        )
        
        assert "✅" in message
        assert "Ping復旧" in message
        assert "Google DNS" in message
        assert "8.8.8.8" in message
    
    def test_format_notification_message_http_ok_to_ng(self, tmp_path):
        """Test formatting notification message for HTTP OK to NG."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        message = manager.format_notification_message(
            "http", "https://example.com", "ok_to_ng", "Example API"
        )
        
        assert "❌" in message
        assert "HTTP失敗" in message
        assert "Example API" in message
        assert "https://example.com" in message
    
    def test_format_notification_message_http_ng_to_ok(self, tmp_path):
        """Test formatting notification message for HTTP NG to OK."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        message = manager.format_notification_message(
            "http", "https://example.com", "ng_to_ok", "Example API"
        )
        
        assert "✅" in message
        assert "HTTP復旧" in message
        assert "Example API" in message
        assert "https://example.com" in message
    
    def test_format_notification_message_no_description(self, tmp_path):
        """Test formatting notification message without description."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        message = manager.format_notification_message(
            "ping", "8.8.8.8", "ok_to_ng"
        )
        
        assert "8.8.8.8" in message
        assert "(" not in message  # No parentheses when no description
