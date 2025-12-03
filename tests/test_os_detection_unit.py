"""
Unit Tests for OS Detection Module

このモジュールは、OS検出機能の個別関数をテストします。
"""

import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.komon.os_detection import OSDetector, get_os_detector


class TestOSDetectorUnit:
    """OSDetectorクラスのユニットテスト"""
    
    def test_init_with_config(self):
        """設定付きで初期化できることを確認"""
        config = {'system': {'os_family': 'rhel'}}
        detector = OSDetector(config)
        
        assert detector.config == config
        assert detector._os_family is None
        assert detector._is_wsl is None
    
    def test_init_without_config(self):
        """設定なしで初期化できることを確認"""
        detector = OSDetector()
        
        assert detector.config == {}
        assert detector._os_family is None
        assert detector._is_wsl is None
    
    def test_detect_os_family_with_config(self):
        """設定ファイルで指定されたOS判定が使用されることを確認"""
        config = {'system': {'os_family': 'debian'}}
        detector = OSDetector(config)
        
        result = detector.detect_os_family()
        
        assert result == 'debian'
    
    def test_detect_os_family_auto_rhel(self):
        """RHEL系の自動判定が正しく動作することを確認"""
        detector = OSDetector()
        
        os_release_content = """
NAME="AlmaLinux"
VERSION="9.3 (Shamrock Pampas Cat)"
ID="almalinux"
ID_LIKE="rhel centos fedora"
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            result = detector.detect_os_family()
        
        assert result == 'rhel'
    
    def test_detect_os_family_auto_debian(self):
        """Debian系の自動判定が正しく動作することを確認"""
        detector = OSDetector()
        
        os_release_content = """
NAME="Ubuntu"
VERSION="22.04.3 LTS (Jammy Jellyfish)"
ID=ubuntu
ID_LIKE=debian
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            result = detector.detect_os_family()
        
        assert result == 'debian'
    
    def test_detect_os_family_auto_raspberry_pi(self):
        """Raspberry Pi OSの自動判定が正しく動作することを確認"""
        detector = OSDetector()
        
        os_release_content = """
PRETTY_NAME="Raspbian GNU/Linux 11 (bullseye)"
NAME="Raspbian GNU/Linux"
VERSION_ID="11"
VERSION="11 (bullseye)"
ID=raspbian
ID_LIKE=debian
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            result = detector.detect_os_family()
        
        assert result == 'debian'
    
    def test_detect_os_family_auto_amazon_linux(self):
        """Amazon Linux 2023の自動判定が正しく動作することを確認"""
        detector = OSDetector()
        
        os_release_content = """
NAME="Amazon Linux"
VERSION="2023"
ID="amzn"
ID_LIKE="fedora"
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            result = detector.detect_os_family()
        
        assert result == 'rhel'
    
    def test_detect_os_family_auto_suse(self):
        """SUSE系の自動判定が正しく動作することを確認"""
        detector = OSDetector()
        
        os_release_content = """
NAME="openSUSE Leap"
VERSION="15.5"
ID="opensuse-leap"
ID_LIKE="suse opensuse"
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            result = detector.detect_os_family()
        
        assert result == 'suse'
    
    def test_detect_os_family_auto_arch(self):
        """Arch系の自動判定が正しく動作することを確認"""
        detector = OSDetector()
        
        os_release_content = """
NAME="Arch Linux"
ID=arch
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            result = detector.detect_os_family()
        
        assert result == 'arch'
    
    def test_detect_os_family_auto_unknown(self):
        """不明なOSの自動判定が正しく動作することを確認"""
        detector = OSDetector()
        
        os_release_content = """
NAME="Unknown OS"
ID=unknown
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            result = detector.detect_os_family()
        
        assert result == 'unknown'
    
    def test_detect_os_family_file_not_found(self):
        """/etc/os-releaseが存在しない場合、unknownを返すことを確認"""
        detector = OSDetector()
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = detector.detect_os_family()
        
        assert result == 'unknown'
    
    def test_detect_os_family_invalid_config(self):
        """不正な設定値の場合、自動判定にフォールバックすることを確認"""
        config = {'system': {'os_family': 'invalid'}}
        detector = OSDetector(config)
        
        os_release_content = """
NAME="AlmaLinux"
ID_LIKE="rhel"
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            result = detector.detect_os_family()
        
        assert result == 'rhel'
    
    def test_is_wsl_true(self):
        """WSL環境の判定が正しく動作することを確認"""
        detector = OSDetector()
        
        proc_version = "Linux version 5.10.16.3-microsoft-standard-WSL2"
        
        with patch('builtins.open', mock_open(read_data=proc_version)):
            result = detector.is_wsl()
        
        assert result is True
    
    def test_is_wsl_false(self):
        """非WSL環境の判定が正しく動作することを確認"""
        detector = OSDetector()
        
        proc_version = "Linux version 5.14.0-362.8.1.el9_3.x86_64"
        
        with patch('builtins.open', mock_open(read_data=proc_version)):
            result = detector.is_wsl()
        
        assert result is False
    
    def test_is_wsl_file_not_found(self):
        """/proc/versionが存在しない場合、Falseを返すことを確認"""
        detector = OSDetector()
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = detector.is_wsl()
        
        assert result is False
    
    def test_check_windows_native(self):
        """Windows native環境でエラー終了することを確認"""
        detector = OSDetector()
        
        with patch('sys.platform', 'win32'):
            with patch.object(detector, 'is_wsl', return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    detector.check_windows()
                
                assert exc_info.value.code == 1
    
    def test_check_windows_wsl(self):
        """WSL環境では正常に続行することを確認"""
        detector = OSDetector()
        
        with patch('sys.platform', 'win32'):
            with patch.object(detector, 'is_wsl', return_value=True):
                # エラーで終了しない
                detector.check_windows()
    
    def test_check_windows_linux(self):
        """Linux環境では正常に続行することを確認"""
        detector = OSDetector()
        
        with patch('sys.platform', 'linux'):
            # エラーで終了しない
            detector.check_windows()
    
    def test_get_package_manager_command_rhel(self):
        """RHEL系のパッケージ管理コマンドが正しく返されることを確認"""
        config = {'system': {'os_family': 'rhel'}}
        detector = OSDetector(config)
        
        result = detector.get_package_manager_command()
        
        assert result == 'sudo dnf update --security'
    
    def test_get_package_manager_command_debian(self):
        """Debian系のパッケージ管理コマンドが正しく返されることを確認"""
        config = {'system': {'os_family': 'debian'}}
        detector = OSDetector(config)
        
        result = detector.get_package_manager_command()
        
        assert result == 'sudo apt update && sudo apt upgrade'
    
    def test_get_package_manager_command_unknown(self):
        """不明なOSの場合、Noneが返されることを確認"""
        config = {'system': {'os_family': 'unknown'}}
        detector = OSDetector(config)
        
        result = detector.get_package_manager_command()
        
        assert result is None
    
    def test_get_log_path_rhel(self):
        """RHEL系のログパスが正しく返されることを確認"""
        config = {'system': {'os_family': 'rhel'}}
        detector = OSDetector(config)
        
        result = detector.get_log_path()
        
        assert result == '/var/log/messages'
    
    def test_get_log_path_debian(self):
        """Debian系のログパスが正しく返されることを確認"""
        config = {'system': {'os_family': 'debian'}}
        detector = OSDetector(config)
        
        result = detector.get_log_path()
        
        assert result == '/var/log/syslog'
    
    def test_get_log_path_unknown(self):
        """不明なOSの場合、Noneが返されることを確認"""
        config = {'system': {'os_family': 'unknown'}}
        detector = OSDetector(config)
        
        result = detector.get_log_path()
        
        assert result is None
    
    def test_should_show_package_advice_rhel(self):
        """RHEL系ではパッケージアドバイスを表示することを確認"""
        config = {'system': {'os_family': 'rhel'}}
        detector = OSDetector(config)
        
        result = detector.should_show_package_advice()
        
        assert result is True
    
    def test_should_show_package_advice_debian(self):
        """Debian系ではパッケージアドバイスを抑制することを確認"""
        config = {'system': {'os_family': 'debian'}}
        detector = OSDetector(config)
        
        result = detector.should_show_package_advice()
        
        assert result is False
    
    def test_should_show_package_advice_unknown(self):
        """不明なOSではパッケージアドバイスを抑制することを確認"""
        config = {'system': {'os_family': 'unknown'}}
        detector = OSDetector(config)
        
        result = detector.should_show_package_advice()
        
        assert result is False


class TestGetOSDetector:
    """get_os_detector関数のユニットテスト"""
    
    def test_get_os_detector_singleton(self):
        """シングルトンパターンが正しく動作することを確認"""
        # グローバルインスタンスをリセット
        import src.komon.os_detection as os_detection_module
        os_detection_module._detector_instance = None
        
        detector1 = get_os_detector()
        detector2 = get_os_detector()
        
        # 同じインスタンスが返される
        assert detector1 is detector2
    
    def test_get_os_detector_with_config(self):
        """設定付きでインスタンスを取得できることを確認"""
        # グローバルインスタンスをリセット
        import src.komon.os_detection as os_detection_module
        os_detection_module._detector_instance = None
        
        config = {'system': {'os_family': 'rhel'}}
        detector = get_os_detector(config)
        
        assert detector.config == config
