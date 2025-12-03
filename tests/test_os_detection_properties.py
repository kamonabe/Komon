"""
Property-Based Tests for OS Detection Module

このモジュールは、OS検出機能の正確性プロパティを検証します。
"""

import pytest
from hypothesis import given, strategies as st, assume
from unittest.mock import patch, mock_open
from src.komon.os_detection import OSDetector


class TestOSDetectionProperties:
    """OS検出機能のプロパティベーステスト"""
    
    @given(st.sampled_from(['rhel', 'debian', 'suse', 'arch', 'unknown']))
    def test_property_os_detection_consistency(self, os_family):
        """
        **Feature: os-detection-multi-distro, Property 1: OS Detection Consistency**
        
        同じ設定で複数回呼び出しても、同じOS判定結果が返される
        
        **検証要件: AC-001, AC-002**
        """
        config = {'system': {'os_family': os_family}}
        detector = OSDetector(config)
        
        # 複数回呼び出し
        result1 = detector.detect_os_family()
        result2 = detector.detect_os_family()
        result3 = detector.detect_os_family()
        
        # 一貫性の検証
        assert result1 == result2 == result3
        assert result1 == os_family
    
    @given(st.sampled_from(['rhel', 'debian', 'suse', 'arch', 'unknown']))
    def test_property_configuration_override_precedence(self, os_family):
        """
        **Feature: os-detection-multi-distro, Property 2: Configuration Override Precedence**
        
        設定ファイルで明示的に指定されたOS判定は、自動判定より優先される
        
        **検証要件: AC-003**
        """
        config = {'system': {'os_family': os_family}}
        detector = OSDetector(config)
        
        # 設定値が優先される
        result = detector.detect_os_family()
        assert result == os_family
    
    @given(st.text(min_size=1, max_size=100))
    def test_property_windows_detection_determinism(self, mock_version):
        """
        **Feature: os-detection-multi-distro, Property 3: Windows Detection Determinism**
        
        同じ/proc/versionの内容に対して、WSL判定は常に同じ結果を返す
        
        **検証要件: AC-004**
        """
        detector = OSDetector()
        
        with patch('builtins.open', mock_open(read_data=mock_version)):
            result1 = detector.is_wsl()
            # キャッシュをクリア
            detector._is_wsl = None
            result2 = detector.is_wsl()
        
        # 一貫性の検証
        assert result1 == result2
        
        # 'microsoft'が含まれる場合はTrue
        if 'microsoft' in mock_version.lower():
            assert result1 is True
        else:
            assert result1 is False
    
    def test_property_wsl_linux_treatment(self):
        """
        **Feature: os-detection-multi-distro, Property 4: WSL Linux Treatment**
        
        WSL環境では、Linux扱いで処理が続行される
        
        **検証要件: AC-005**
        """
        detector = OSDetector()
        
        # WSL環境をシミュレート
        with patch('sys.platform', 'win32'):
            with patch.object(detector, 'is_wsl', return_value=True):
                # エラーで終了しないことを確認
                try:
                    detector.check_windows()
                    # 正常に続行
                    assert True
                except SystemExit:
                    pytest.fail("WSL environment should not exit")
    
    @given(st.sampled_from(['rhel', 'debian', 'suse', 'arch', 'unknown']))
    def test_property_package_manager_command_correctness(self, os_family):
        """
        **Feature: os-detection-multi-distro, Property 5: Package Manager Command Correctness**
        
        各OSファミリに対して、正しいパッケージ管理コマンドが返される
        
        **検証要件: AC-006, AC-007**
        """
        config = {'system': {'os_family': os_family}}
        detector = OSDetector(config)
        
        command = detector.get_package_manager_command()
        
        # 期待されるコマンド
        expected_commands = {
            'rhel': 'sudo dnf update --security',
            'debian': 'sudo apt update && sudo apt upgrade',
            'suse': 'sudo zypper update',
            'arch': 'sudo pacman -Syu',
            'unknown': None
        }
        
        assert command == expected_commands[os_family]
    
    @given(st.sampled_from(['rhel', 'debian', 'suse', 'arch', 'unknown']))
    def test_property_log_path_consistency(self, os_family):
        """
        **Feature: os-detection-multi-distro, Property 6: Log Path Consistency**
        
        各OSファミリに対して、一貫したログパスが返される
        
        **検証要件: AC-009, AC-010**
        """
        config = {'system': {'os_family': os_family}}
        detector = OSDetector(config)
        
        log_path = detector.get_log_path()
        
        # 期待されるログパス
        expected_paths = {
            'rhel': '/var/log/messages',
            'debian': '/var/log/syslog',
            'suse': '/var/log/messages',
            'arch': '/var/log/syslog',
            'unknown': None
        }
        
        assert log_path == expected_paths[os_family]
    
    @given(st.sampled_from(['rhel', 'debian', 'suse', 'arch', 'unknown']))
    def test_property_package_advice_suppression(self, os_family):
        """
        **Feature: os-detection-multi-distro, Property 7: Package Advice Suppression**
        
        RHEL系以外では、パッケージアドバイスが抑制される
        
        **検証要件: AC-011**
        """
        config = {'system': {'os_family': os_family}}
        detector = OSDetector(config)
        
        should_show = detector.should_show_package_advice()
        
        # RHEL系のみTrue
        if os_family == 'rhel':
            assert should_show is True
        else:
            assert should_show is False
