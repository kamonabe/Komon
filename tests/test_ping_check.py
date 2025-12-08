"""
Tests for ping check module.
"""

import subprocess
from unittest.mock import patch, MagicMock
import pytest

from komon.net.ping_check import check_ping


class TestPingCheck:
    """Tests for check_ping function."""
    
    @patch('subprocess.run')
    def test_ping_success(self, mock_run):
        """Test successful ping."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = check_ping("8.8.8.8", timeout=3)
        
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ping" in args
        assert "8.8.8.8" in args
    
    @patch('subprocess.run')
    def test_ping_failure(self, mock_run):
        """Test failed ping."""
        mock_run.return_value = MagicMock(returncode=1)
        
        result = check_ping("192.168.255.255", timeout=3)
        
        assert result is False
    
    @patch('subprocess.run')
    def test_ping_timeout(self, mock_run):
        """Test ping timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="ping", timeout=3)
        
        result = check_ping("10.0.0.1", timeout=3)
        
        assert result is False
    
    @patch('subprocess.run')
    def test_ping_exception(self, mock_run):
        """Test ping with exception."""
        mock_run.side_effect = Exception("Network error")
        
        result = check_ping("example.com", timeout=3)
        
        assert result is False
    
    def test_ping_invalid_host(self):
        """Test ping with invalid host."""
        result = check_ping("", timeout=3)
        
        assert result is False
    
    def test_ping_none_host(self):
        """Test ping with None host."""
        result = check_ping(None, timeout=3)
        
        assert result is False
    
    @patch('subprocess.run')
    def test_ping_custom_timeout(self, mock_run):
        """Test ping with custom timeout."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = check_ping("8.8.8.8", timeout=10)
        
        assert result is True
        args = mock_run.call_args[0][0]
        assert "10" in args  # timeout value
    
    @patch('subprocess.run')
    def test_ping_default_timeout(self, mock_run):
        """Test ping with default timeout."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = check_ping("8.8.8.8")
        
        assert result is True
        args = mock_run.call_args[0][0]
        assert "3" in args  # default timeout
    
    @patch('subprocess.run')
    def test_ping_ipv4_address(self, mock_run):
        """Test ping with IPv4 address."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = check_ping("192.168.1.1", timeout=3)
        
        assert result is True
    
    @patch('subprocess.run')
    def test_ping_hostname(self, mock_run):
        """Test ping with hostname."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = check_ping("google.com", timeout=3)
        
        assert result is True
