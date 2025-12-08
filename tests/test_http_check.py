"""
Tests for HTTP check module.
"""

import requests
from unittest.mock import patch, MagicMock
import pytest

from komon.net.http_check import check_http


class TestHttpCheck:
    """Tests for check_http function."""
    
    @patch('requests.request')
    def test_http_success(self, mock_request):
        """Test successful HTTP request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = check_http("https://example.com", timeout=10)
        
        assert result is True
        mock_request.assert_called_once_with(
            "GET",
            "https://example.com",
            timeout=10,
            allow_redirects=True
        )
    
    @patch('requests.request')
    def test_http_failure_404(self, mock_request):
        """Test HTTP request with 404 error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        result = check_http("https://example.com/notfound", timeout=10)
        
        assert result is False
    
    @patch('requests.request')
    def test_http_failure_500(self, mock_request):
        """Test HTTP request with 500 error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_request.return_value = mock_response
        
        result = check_http("https://example.com", timeout=10)
        
        assert result is False
    
    @patch('requests.request')
    def test_http_timeout(self, mock_request):
        """Test HTTP request timeout."""
        mock_request.side_effect = requests.exceptions.Timeout()
        
        result = check_http("https://slow.example.com", timeout=10)
        
        assert result is False
    
    @patch('requests.request')
    def test_http_connection_error(self, mock_request):
        """Test HTTP request with connection error."""
        mock_request.side_effect = requests.exceptions.ConnectionError()
        
        result = check_http("https://unreachable.example.com", timeout=10)
        
        assert result is False
    
    @patch('requests.request')
    def test_http_exception(self, mock_request):
        """Test HTTP request with exception."""
        mock_request.side_effect = Exception("Network error")
        
        result = check_http("https://example.com", timeout=10)
        
        assert result is False
    
    def test_http_invalid_url(self):
        """Test HTTP request with invalid URL."""
        result = check_http("", timeout=10)
        
        assert result is False
    
    def test_http_none_url(self):
        """Test HTTP request with None URL."""
        result = check_http(None, timeout=10)
        
        assert result is False
    
    @patch('requests.request')
    def test_http_post_method(self, mock_request):
        """Test HTTP POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = check_http("https://api.example.com", timeout=10, method="POST")
        
        assert result is True
        mock_request.assert_called_once_with(
            "POST",
            "https://api.example.com",
            timeout=10,
            allow_redirects=True
        )
    
    @patch('requests.request')
    def test_http_custom_timeout(self, mock_request):
        """Test HTTP request with custom timeout."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = check_http("https://example.com", timeout=30)
        
        assert result is True
        assert mock_request.call_args[1]['timeout'] == 30
