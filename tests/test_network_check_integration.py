"""
Integration tests for network check functionality.
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from komon.net import check_ping, check_http, NetworkStateManager


class TestNetworkCheckIntegration:
    """Integration tests for network check."""
    
    @patch('subprocess.run')
    def test_ping_check_with_state_manager(self, mock_run, tmp_path):
        """Test ping check with state manager integration."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        # First check: OK
        mock_run.return_value = MagicMock(returncode=0)
        is_ok = check_ping("8.8.8.8", timeout=3)
        state_change = manager.check_state_change("ping", "8.8.8.8", is_ok)
        
        assert is_ok is True
        assert state_change is None
        
        # Second check: NG (failure)
        mock_run.return_value = MagicMock(returncode=1)
        is_ok = check_ping("8.8.8.8", timeout=3)
        state_change = manager.check_state_change("ping", "8.8.8.8", is_ok)
        
        assert is_ok is False
        assert state_change == "ok_to_ng"
        
        # Third check: NG (still failing)
        mock_run.return_value = MagicMock(returncode=1)
        is_ok = check_ping("8.8.8.8", timeout=3)
        state_change = manager.check_state_change("ping", "8.8.8.8", is_ok)
        
        assert is_ok is False
        assert state_change is None
        
        # Fourth check: OK (recovery)
        mock_run.return_value = MagicMock(returncode=0)
        is_ok = check_ping("8.8.8.8", timeout=3)
        state_change = manager.check_state_change("ping", "8.8.8.8", is_ok)
        
        assert is_ok is True
        assert state_change == "ng_to_ok"
    
    @patch('requests.request')
    def test_http_check_with_state_manager(self, mock_request, tmp_path):
        """Test HTTP check with state manager integration."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        # First check: OK
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        is_ok = check_http("https://example.com", timeout=10)
        state_change = manager.check_state_change("http", "https://example.com", is_ok)
        
        assert is_ok is True
        assert state_change is None
        
        # Second check: NG (failure)
        mock_response.status_code = 500
        is_ok = check_http("https://example.com", timeout=10)
        state_change = manager.check_state_change("http", "https://example.com", is_ok)
        
        assert is_ok is False
        assert state_change == "ok_to_ng"
    
    @patch('subprocess.run')
    @patch('requests.request')
    def test_mixed_ping_and_http_checks(self, mock_request, mock_run, tmp_path):
        """Test mixed ping and HTTP checks."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        # Ping check: NG
        mock_run.return_value = MagicMock(returncode=1)
        is_ok = check_ping("192.168.1.1", timeout=3)
        state_change = manager.check_state_change("ping", "192.168.1.1", is_ok)
        
        assert state_change == "ok_to_ng"
        
        # HTTP check: NG
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        is_ok = check_http("https://api.example.com", timeout=10)
        state_change = manager.check_state_change("http", "https://api.example.com", is_ok)
        
        assert state_change == "ok_to_ng"
        
        # Check NG count
        assert manager.get_ng_count() == 2
        
        # Ping recovery
        mock_run.return_value = MagicMock(returncode=0)
        is_ok = check_ping("192.168.1.1", timeout=3)
        state_change = manager.check_state_change("ping", "192.168.1.1", is_ok)
        
        assert state_change == "ng_to_ok"
        assert manager.get_ng_count() == 1
    
    def test_state_persistence(self, tmp_path):
        """Test state persistence across manager instances."""
        state_file = tmp_path / "state.json"
        
        # First manager: create NG state
        manager1 = NetworkStateManager(str(state_file), retention_hours=24)
        manager1.check_state_change("ping", "8.8.8.8", False)
        
        # Second manager: load existing state
        manager2 = NetworkStateManager(str(state_file), retention_hours=24)
        
        assert manager2.get_ng_count() == 1
        assert "net.ping:8.8.8.8" in manager2.get_ng_targets()
    
    def test_notification_message_formatting(self, tmp_path):
        """Test notification message formatting."""
        state_file = tmp_path / "state.json"
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        # Ping failure
        message = manager.format_notification_message(
            "ping", "8.8.8.8", "ok_to_ng", "Google DNS"
        )
        assert "❌" in message
        assert "Ping失敗" in message
        
        # Ping recovery
        message = manager.format_notification_message(
            "ping", "8.8.8.8", "ng_to_ok", "Google DNS"
        )
        assert "✅" in message
        assert "Ping復旧" in message
        
        # HTTP failure
        message = manager.format_notification_message(
            "http", "https://example.com", "ok_to_ng", "Example API"
        )
        assert "❌" in message
        assert "HTTP失敗" in message
        
        # HTTP recovery
        message = manager.format_notification_message(
            "http", "https://example.com", "ng_to_ok", "Example API"
        )
        assert "✅" in message
        assert "HTTP復旧" in message
    
    def test_empty_state_file(self, tmp_path):
        """Test handling of empty state file."""
        state_file = tmp_path / "state.json"
        state_file.write_text("")
        
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        assert manager.state == {}
        assert manager.get_ng_count() == 0
    
    def test_corrupted_state_file(self, tmp_path):
        """Test handling of corrupted state file."""
        state_file = tmp_path / "state.json"
        state_file.write_text("invalid json {")
        
        manager = NetworkStateManager(str(state_file), retention_hours=24)
        
        assert manager.state == {}
        assert manager.get_ng_count() == 0
