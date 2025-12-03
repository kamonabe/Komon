"""
Integration Tests for OS Detection Module

このモジュールは、OS検出機能と他のモジュールとの統合をテストします。
"""

import pytest
from unittest.mock import patch, mock_open
from src.komon.os_detection import OSDetector, get_os_detector


class TestOSDetectionIntegration:
    """OS検出機能の統合テスト"""
    
    def test_integration_rhel_package_command_generation(self):
        """
        RHEL系でのパッケージ管理コマンド生成を確認
        
        **検証要件: AC-006**
        """
        os_release_content = """
NAME="AlmaLinux"
VERSION="9.3"
ID="almalinux"
ID_LIKE="rhel centos fedora"
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            detector = OSDetector()
            os_family = detector.detect_os_family()
            
            assert os_family == 'rhel'
            
            # セキュリティパッチコマンド
            security_cmd = detector.get_package_manager_command('security')
            assert security_cmd == 'sudo dnf update --security'
            
            # 全パッケージ更新コマンド
            all_cmd = detector.get_package_manager_command('all')
            assert all_cmd == 'sudo dnf update'
    
    def test_integration_debian_package_command_generation(self):
        """
        Debian系でのパッケージ管理コマンド生成を確認
        
        **検証要件: AC-007**
        """
        os_release_content = """
NAME="Ubuntu"
VERSION="22.04.3 LTS"
ID=ubuntu
ID_LIKE=debian
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            detector = OSDetector()
            os_family = detector.detect_os_family()
            
            assert os_family == 'debian'
            
            # パッケージ管理コマンド
            cmd = detector.get_package_manager_command()
            assert cmd == 'sudo apt update && sudo apt upgrade'
    
    def test_integration_unknown_generic_advice(self):
        """
        unknown OSでの汎用アドバイス生成を確認
        
        **検証要件: AC-008**
        """
        os_release_content = """
NAME="Unknown OS"
ID=unknown
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            detector = OSDetector()
            os_family = detector.detect_os_family()
            
            assert os_family == 'unknown'
            
            # コマンドはNone
            cmd = detector.get_package_manager_command()
            assert cmd is None
    
    def test_integration_rhel_package_advice_display(self):
        """
        RHEL系でのパッケージアドバイス表示を確認
        
        **検証要件: AC-011**
        """
        config = {'system': {'os_family': 'rhel'}}
        detector = OSDetector(config)
        
        # RHEL系ではパッケージアドバイスを表示
        assert detector.should_show_package_advice() is True
    
    def test_integration_debian_package_advice_suppression(self):
        """
        Debian系でのパッケージアドバイス抑制を確認
        
        **検証要件: AC-011**
        """
        config = {'system': {'os_family': 'debian'}}
        detector = OSDetector(config)
        
        # Debian系ではパッケージアドバイスを抑制
        assert detector.should_show_package_advice() is False
    
    def test_integration_unknown_package_advice_suppression(self):
        """
        unknown OSでのパッケージアドバイス抑制を確認
        
        **検証要件: AC-011**
        """
        config = {'system': {'os_family': 'unknown'}}
        detector = OSDetector(config)
        
        # unknown OSではパッケージアドバイスを抑制
        assert detector.should_show_package_advice() is False
    
    def test_integration_rhel_log_path(self):
        """
        RHEL系での/var/log/messages使用を確認
        
        **検証要件: AC-009**
        """
        config = {'system': {'os_family': 'rhel'}}
        detector = OSDetector(config)
        
        log_path = detector.get_log_path()
        assert log_path == '/var/log/messages'
    
    def test_integration_debian_log_path(self):
        """
        Debian系での/var/log/syslog使用を確認
        
        **検証要件: AC-010**
        """
        config = {'system': {'os_family': 'debian'}}
        detector = OSDetector(config)
        
        log_path = detector.get_log_path()
        assert log_path == '/var/log/syslog'
    
    def test_integration_unknown_log_advice_suppression(self):
        """
        unknown OSでのログアドバイス抑制を確認
        
        **検証要件: AC-010**
        """
        config = {'system': {'os_family': 'unknown'}}
        detector = OSDetector(config)
        
        log_path = detector.get_log_path()
        assert log_path is None
    
    def test_integration_config_and_detection(self):
        """
        設定ファイルとOS自動判定の統合を確認
        """
        # 設定でautoを指定
        config = {'system': {'os_family': 'auto'}}
        
        os_release_content = """
NAME="AlmaLinux"
ID_LIKE="rhel"
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            detector = OSDetector(config)
            os_family = detector.detect_os_family()
            
            # 自動判定が動作
            assert os_family == 'rhel'
    
    def test_integration_config_override(self):
        """
        設定ファイルでの手動上書きを確認
        """
        # 設定でdebianを指定
        config = {'system': {'os_family': 'debian'}}
        
        os_release_content = """
NAME="AlmaLinux"
ID_LIKE="rhel"
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            detector = OSDetector(config)
            os_family = detector.detect_os_family()
            
            # 設定が優先される
            assert os_family == 'debian'
    
    def test_integration_amazon_linux_2023_as_rhel(self):
        """
        Amazon Linux 2023がRHEL系として扱われることを確認
        
        **検証要件: AC-002**
        """
        os_release_content = """
NAME="Amazon Linux"
VERSION="2023"
ID="amzn"
ID_LIKE="fedora"
VERSION_ID="2023"
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            detector = OSDetector()
            os_family = detector.detect_os_family()
            
            # RHEL系として判定
            assert os_family == 'rhel'
            
            # RHEL系のコマンドが使用される
            cmd = detector.get_package_manager_command('security')
            assert cmd == 'sudo dnf update --security'
            
            # パッケージアドバイスが表示される
            assert detector.should_show_package_advice() is True
