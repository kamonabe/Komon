"""
ログ解析モジュールの統合テスト

**Feature: os-detection-multi-distro**
"""

import pytest
from src.komon.log_analyzer import (
    get_recommended_log_path,
    should_show_log_advice
)


class TestLogPathSwitching:
    """ログパス切替の統合テスト"""
    
    def test_rhel_log_path(self):
        """
        RHEL系では /var/log/messages を推奨
        
        **検証要件: AC-009**
        """
        config = {'system': {'os_family': 'rhel'}}
        
        log_path = get_recommended_log_path(config)
        
        assert log_path == '/var/log/messages'
    
    def test_debian_log_path(self):
        """
        Debian系では /var/log/syslog を推奨
        
        **検証要件: AC-009**
        """
        config = {'system': {'os_family': 'debian'}}
        
        log_path = get_recommended_log_path(config)
        
        assert log_path == '/var/log/syslog'
    
    def test_unknown_log_path_suppressed(self):
        """
        unknown OSではログパス推奨を抑制
        
        **検証要件: AC-010**
        """
        config = {'system': {'os_family': 'unknown'}}
        
        log_path = get_recommended_log_path(config)
        
        assert log_path is None
    
    def test_should_show_log_advice_rhel(self):
        """
        RHEL系ではログアドバイスを表示
        
        **検証要件: AC-009**
        """
        config = {'system': {'os_family': 'rhel'}}
        
        result = should_show_log_advice(config)
        
        assert result is True
    
    def test_should_show_log_advice_debian(self):
        """
        Debian系ではログアドバイスを表示
        
        **検証要件: AC-009**
        """
        config = {'system': {'os_family': 'debian'}}
        
        result = should_show_log_advice(config)
        
        assert result is True
    
    def test_should_show_log_advice_unknown(self):
        """
        unknown OSではログアドバイスを抑制
        
        **検証要件: AC-010**
        """
        config = {'system': {'os_family': 'unknown'}}
        
        result = should_show_log_advice(config)
        
        assert result is False
