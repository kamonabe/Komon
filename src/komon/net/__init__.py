"""
Network connectivity check module for Komon.

This module provides lightweight network connectivity checks (ping/http)
as an opt-in feature for Komon's advisory capabilities.
"""

from .ping_check import check_ping
from .http_check import check_http
from .state_manager import NetworkStateManager

__all__ = [
    'check_ping',
    'check_http',
    'NetworkStateManager',
]
