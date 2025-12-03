"""
advise.pyのOS判定統合テスト

**検証要件: AC-006, AC-007, AC-008, AC-011**
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO


class TestAdviseOSIntegration:
    """advise.pyのOS判定統合テスト"""
    
    def test_advise_os_update_rhel(self, capsys):
        """
        RHEL系でのパッケージ更新アドバイス
        
        **検証要件: AC-006**
        """
        from scripts.advise import advise_os_update
        
        config = {
            'system': {
                'os_family': 'rhel'
            }
        }
        
        # dnfコマンドが成功する場合
        with patch('subprocess.run') as mock_run:
            # セキュリティ更新なし
            mock_run.return_value = MagicMock(
                stdout="",
                returncode=0
            )
            
            advise_os_update(config)
            
            captured = capsys.readouterr()
            assert "セキュリティパッチの確認" in captured.out
            assert "セキュリティ更新はありません" in captured.out
    
    def test_advise_os_update_debian(self, capsys):
        """
        Debian系でのパッケージ更新アドバイス抑制
        
        **検証要件: AC-007, AC-011**
        """
        from scripts.advise import advise_os_update
        from komon.os_detection import OSDetector
        
        config = {
            'system': {
                'os_family': 'debian'
            }
        }
        
        # OSDetectorをモック
        with patch('scripts.advise.get_os_detector') as mock_detector:
            mock_instance = MagicMock(spec=OSDetector)
            mock_instance.detect_os_family.return_value = 'debian'
            mock_instance.should_show_package_advice.return_value = False
            mock_instance.get_package_manager_command.return_value = 'sudo apt update && sudo apt upgrade'
            mock_detector.return_value = mock_instance
            
            advise_os_update(config)
            
            captured = capsys.readouterr()
            assert "パッケージ更新の確認" in captured.out
            assert "debian系OSでは" in captured.out
            assert "パッケージ名の違いにより" in captured.out
            assert "sudo apt update && sudo apt upgrade" in captured.out
    
    def test_advise_os_update_unknown(self, capsys):
        """
        unknown OSでの汎用アドバイス
        
        **検証要件: AC-008**
        """
        from scripts.advise import advise_os_update
        from komon.os_detection import OSDetector
        
        config = {
            'system': {
                'os_family': 'unknown'
            }
        }
        
        # OSDetectorをモック
        with patch('scripts.advise.get_os_detector') as mock_detector:
            mock_instance = MagicMock(spec=OSDetector)
            mock_instance.detect_os_family.return_value = 'unknown'
            mock_instance.should_show_package_advice.return_value = False
            mock_instance.get_package_manager_command.return_value = None
            mock_detector.return_value = mock_instance
            
            advise_os_update(config)
            
            captured = capsys.readouterr()
            assert "パッケージ更新の確認" in captured.out
            assert "OSファミリが不明なため" in captured.out
            assert "具体的なアドバイスを控えています" in captured.out
    
    def test_advise_os_update_auto_detection(self, capsys):
        """
        自動判定でのパッケージ更新アドバイス
        
        **検証要件: AC-001**
        """
        from scripts.advise import advise_os_update
        
        config = {
            'system': {
                'os_family': 'auto'
            }
        }
        
        # /etc/os-releaseをモック（RHEL系）
        os_release_content = """
NAME="AlmaLinux"
VERSION="9.3 (Shamrock Pampas Cat)"
ID="almalinux"
ID_LIKE="rhel centos fedora"
"""
        
        with patch('builtins.open', mock_open(read_data=os_release_content)):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="",
                    returncode=0
                )
                
                advise_os_update(config)
                
                captured = capsys.readouterr()
                assert "セキュリティパッチの確認" in captured.out
    
    def test_advise_os_update_suse(self, capsys):
        """
        SUSE系でのパッケージ更新アドバイス抑制
        
        **検証要件: AC-011**
        """
        from scripts.advise import advise_os_update
        from komon.os_detection import OSDetector
        
        config = {
            'system': {
                'os_family': 'suse'
            }
        }
        
        # OSDetectorをモック
        with patch('scripts.advise.get_os_detector') as mock_detector:
            mock_instance = MagicMock(spec=OSDetector)
            mock_instance.detect_os_family.return_value = 'suse'
            mock_instance.should_show_package_advice.return_value = False
            mock_instance.get_package_manager_command.return_value = 'sudo zypper update'
            mock_detector.return_value = mock_instance
            
            advise_os_update(config)
            
            captured = capsys.readouterr()
            assert "パッケージ更新の確認" in captured.out
            assert "suse系OSでは" in captured.out
            assert "sudo zypper update" in captured.out
    
    def test_advise_os_update_arch(self, capsys):
        """
        Arch系でのパッケージ更新アドバイス抑制
        
        **検証要件: AC-011**
        """
        from scripts.advise import advise_os_update
        from komon.os_detection import OSDetector
        
        config = {
            'system': {
                'os_family': 'arch'
            }
        }
        
        # OSDetectorをモック
        with patch('scripts.advise.get_os_detector') as mock_detector:
            mock_instance = MagicMock(spec=OSDetector)
            mock_instance.detect_os_family.return_value = 'arch'
            mock_instance.should_show_package_advice.return_value = False
            mock_instance.get_package_manager_command.return_value = 'sudo pacman -Syu'
            mock_detector.return_value = mock_instance
            
            advise_os_update(config)
            
            captured = capsys.readouterr()
            assert "パッケージ更新の確認" in captured.out
            assert "arch系OSでは" in captured.out
            assert "sudo pacman -Syu" in captured.out
    
    def test_advise_os_update_rhel_with_security_updates(self, capsys):
        """
        RHEL系でセキュリティ更新がある場合
        
        **検証要件: AC-006**
        """
        from scripts.advise import advise_os_update
        
        config = {
            'system': {
                'os_family': 'rhel'
            }
        }
        
        # セキュリティ更新あり
        security_output = """
RHSA-2024:0001 Important/Sec. kernel-5.14.0-362.8.1.el9_3.x86_64
RHSA-2024:0002 Important/Sec. glibc-2.34-60.el9_3.7.x86_64
"""
        
        with patch('subprocess.run') as mock_run:
            with patch('scripts.advise.ask_yes_no', return_value=False):
                mock_run.return_value = MagicMock(
                    stdout=security_output,
                    returncode=0
                )
                
                advise_os_update(config)
                
                captured = capsys.readouterr()
                assert "セキュリティ更新が 2 件あります" in captured.out
                assert "RHSA-2024:0001" in captured.out
    
    def test_advise_os_update_rhel_dnf_not_found(self, capsys):
        """
        RHEL系でdnfコマンドが見つからない場合
        
        **検証要件: AC-006**
        """
        from scripts.advise import advise_os_update
        
        config = {
            'system': {
                'os_family': 'rhel'
            }
        }
        
        with patch('subprocess.run', side_effect=FileNotFoundError):
            advise_os_update(config)
            
            captured = capsys.readouterr()
            assert "dnf が見つかりません" in captured.out
            assert "RHEL系Linux" in captured.out



class TestAdviseOSUpdateDebianIntegration:
    """advise_os_updateのDebian系アドバイス出し分け統合テスト"""
    
    def test_debian_package_advice_simple(self, capsys):
        """
        Debian系でのシンプルなパッケージアドバイス
        
        **検証要件: AC-003**
        """
        from scripts.advise import advise_os_update
        from komon.os_detection import OSDetector
        
        config = {
            'system': {
                'os_family': 'debian'
            }
        }
        
        # Debian系のOS情報をモック
        with patch('scripts.advise.get_os_detector') as mock_detector:
            mock_os = MagicMock(spec=OSDetector)
            mock_os.detect_os_family.return_value = 'debian'
            mock_os.should_show_package_advice.return_value = True
            mock_os.get_package_manager_command.return_value = 'sudo apt update && sudo apt upgrade'
            mock_detector.return_value = mock_os
            
            # ask_yes_noをモック（常にNo）
            with patch('scripts.advise.ask_yes_no', return_value=False):
                advise_os_update(config)
            
            captured = capsys.readouterr()
            
            # Debian系のメッセージが表示される
            assert '① パッケージ更新の確認' in captured.out
            assert 'sudo apt update' in captured.out
            assert 'sudo apt upgrade' in captured.out
    
    def test_debian_package_advice_with_execution(self, capsys):
        """
        Debian系でのパッケージ更新実行
        
        **検証要件: AC-003**
        """
        from scripts.advise import advise_os_update
        from komon.os_detection import OSDetector
        
        config = {
            'system': {
                'os_family': 'debian'
            }
        }
        
        # Debian系のOS情報をモック
        with patch('scripts.advise.get_os_detector') as mock_detector:
            mock_os = MagicMock(spec=OSDetector)
            mock_os.detect_os_family.return_value = 'debian'
            mock_os.should_show_package_advice.return_value = True
            mock_os.get_package_manager_command.return_value = 'sudo apt update && sudo apt upgrade'
            mock_detector.return_value = mock_os
            
            # aptコマンドをモック
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                
                # ask_yes_noをモック（Yes）
                with patch('scripts.advise.ask_yes_no', return_value=True):
                    advise_os_update(config)
                
                captured = capsys.readouterr()
                
                # 更新実行のメッセージが表示される
                assert 'パッケージ更新を実行します' in captured.out
                assert 'パッケージ更新が完了しました' in captured.out
                
                # aptコマンドが2回呼ばれる（update + upgrade）
                assert mock_run.call_count == 2
    
    def test_debian_apt_not_found(self, capsys):
        """
        Debian系でaptコマンドが見つからない場合
        
        **検証要件: AC-003**
        """
        from scripts.advise import advise_os_update
        from komon.os_detection import OSDetector
        
        config = {
            'system': {
                'os_family': 'debian'
            }
        }
        
        # Debian系のOS情報をモック
        with patch('scripts.advise.get_os_detector') as mock_detector:
            mock_os = MagicMock(spec=OSDetector)
            mock_os.detect_os_family.return_value = 'debian'
            mock_os.should_show_package_advice.return_value = True
            mock_os.get_package_manager_command.return_value = 'sudo apt update && sudo apt upgrade'
            mock_detector.return_value = mock_os
            
            # aptコマンドが見つからない
            with patch('subprocess.run', side_effect=FileNotFoundError):
                # ask_yes_noをモック（Yes）
                with patch('scripts.advise.ask_yes_no', return_value=True):
                    advise_os_update(config)
                
                captured = capsys.readouterr()
                
                # エラーメッセージが表示される
                assert 'apt が見つかりません' in captured.out
                assert 'Debian系Linux' in captured.out
