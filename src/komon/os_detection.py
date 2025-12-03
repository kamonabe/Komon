"""
OS Detection Module

このモジュールは、実行環境のOS判定とOS別の設定を提供します。

主な機能:
- OSファミリの自動判定（rhel / debian / suse / arch / unknown）
- Windows/WSL検出
- OS別のパッケージ管理コマンド取得
- OS別のログパス取得
- OS別のアドバイス出し分け判定
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class OSDetector:
    """OS検出と設定を管理するクラス"""
    
    # サポートするOSファミリ
    SUPPORTED_FAMILIES = ['rhel', 'debian', 'suse', 'arch', 'unknown']
    
    # OSファミリ別のパッケージ管理コマンド
    PACKAGE_MANAGERS = {
        'rhel': 'sudo dnf update --security',
        'debian': 'sudo apt update && sudo apt upgrade',
        'suse': 'sudo zypper update',
        'arch': 'sudo pacman -Syu',
        'unknown': None
    }
    
    # OSファミリ別のログパス
    LOG_PATHS = {
        'rhel': '/var/log/messages',
        'debian': '/var/log/syslog',
        'suse': '/var/log/messages',
        'arch': '/var/log/syslog',
        'unknown': None
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        OSDetectorを初期化
        
        Args:
            config: 設定辞書（system.os_familyを含む）
        """
        self.config = config or {}
        self._os_family = None
        self._is_wsl = None
    
    def detect_os_family(self) -> str:
        """
        OSファミリを判定
        
        設定ファイルで明示的に指定されている場合はそれを使用し、
        そうでない場合は自動判定を行う。
        
        Returns:
            OSファミリ名（rhel / debian / suse / arch / unknown）
        """
        if self._os_family is not None:
            return self._os_family
        
        # 設定ファイルからの読み込み
        configured_family = self.config.get('system', {}).get('os_family', 'auto')
        
        if configured_family != 'auto':
            # 設定値の検証
            if configured_family in self.SUPPORTED_FAMILIES:
                logger.info("Using configured OS family: %s", configured_family)
                self._os_family = configured_family
                return self._os_family
            else:
                logger.warning(
                    "Invalid os_family in config: %s, falling back to auto-detection",
                    configured_family
                )
        
        # 自動判定
        self._os_family = self._auto_detect_os_family()
        logger.info("Auto-detected OS family: %s", self._os_family)
        return self._os_family
    
    def _auto_detect_os_family(self) -> str:
        """
        /etc/os-releaseを読み取ってOSファミリを自動判定
        
        Returns:
            OSファミリ名（rhel / debian / suse / arch / unknown）
        """
        try:
            with open('/etc/os-release', 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            # RHEL系の判定
            if any(keyword in content for keyword in [
                'rhel', 'red hat', 'fedora', 'centos', 
                'rocky', 'almalinux', 'amazon linux'
            ]):
                return 'rhel'
            
            # Debian系の判定
            if any(keyword in content for keyword in [
                'debian', 'ubuntu', 'raspbian', 'raspberry'
            ]):
                return 'debian'
            
            # SUSE系の判定
            if any(keyword in content for keyword in ['suse', 'opensuse']):
                return 'suse'
            
            # Arch系の判定
            if any(keyword in content for keyword in ['arch', 'manjaro']):
                return 'arch'
            
            logger.warning("Unknown OS family from /etc/os-release")
            return 'unknown'
            
        except FileNotFoundError:
            logger.warning("/etc/os-release not found, OS family is unknown")
            return 'unknown'
        except Exception as e:
            logger.error("Failed to read /etc/os-release: %s", e)
            return 'unknown'
    
    def is_wsl(self) -> bool:
        """
        WSL（Windows Subsystem for Linux）環境かどうかを判定
        
        Returns:
            WSL環境の場合True
        """
        if self._is_wsl is not None:
            return self._is_wsl
        
        try:
            # /proc/versionにMicrosoftが含まれていればWSL
            with open('/proc/version', 'r', encoding='utf-8') as f:
                version = f.read().lower()
                self._is_wsl = 'microsoft' in version
                return self._is_wsl
        except FileNotFoundError:
            self._is_wsl = False
            return False
        except Exception as e:
            logger.error("Failed to check WSL: %s", e)
            self._is_wsl = False
            return False
    
    def check_windows(self) -> None:
        """
        Windows native環境をチェックし、該当する場合はエラーで終了
        
        WSLの場合はLinux扱いで続行する。
        """
        if sys.platform == 'win32':
            # WSLかどうかを確認
            if self.is_wsl():
                logger.info("Running on WSL, treating as Linux")
                print("ℹ️  WSL環境を検出しました。Linux扱いで動作します。")
                return
            
            # Windows native
            print("❌ Komonは現在Windows環境をサポートしていません")
            print("   WSL（Windows Subsystem for Linux）での実行を推奨します。")
            print("   詳細: https://docs.microsoft.com/ja-jp/windows/wsl/install")
            logger.error("Windows native is not supported")
            sys.exit(1)
    
    def get_package_manager_command(self) -> Optional[str]:
        """
        OS別のパッケージ管理コマンドを取得
        
        Returns:
            パッケージ管理コマンド文字列、またはNone（unknown OS）
        """
        os_family = self.detect_os_family()
        return self.PACKAGE_MANAGERS.get(os_family)
    
    def get_log_path(self) -> Optional[str]:
        """
        OS別のシステムログパスを取得
        
        Returns:
            ログファイルパス、またはNone（unknown OS）
        """
        os_family = self.detect_os_family()
        return self.LOG_PATHS.get(os_family)
    
    def should_show_package_advice(self) -> bool:
        """
        パッケージ系のアドバイスを表示すべきかどうかを判定
        
        Debian系ではパッケージ名の違いにより誤ったアドバイスを
        してしまう可能性があるため、パッケージ系アドバイスを抑制する。
        
        Returns:
            アドバイスを表示すべき場合True
        """
        os_family = self.detect_os_family()
        
        # RHEL系のみパッケージアドバイスを表示
        return os_family == 'rhel'


# グローバルインスタンス（シングルトン）
_detector_instance: Optional[OSDetector] = None


def get_os_detector(config: Optional[Dict[str, Any]] = None) -> OSDetector:
    """
    OSDetectorのグローバルインスタンスを取得
    
    Args:
        config: 設定辞書（初回呼び出し時のみ使用）
    
    Returns:
        OSDetectorインスタンス
    """
    global _detector_instance
    
    if _detector_instance is None:
        _detector_instance = OSDetector(config)
    
    return _detector_instance
