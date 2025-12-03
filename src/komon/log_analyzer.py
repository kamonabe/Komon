"""
ログ分析モジュール

ログの異常検知を行います。
"""

import logging
from typing import Optional
from .os_detection import OSDetector

logger = logging.getLogger(__name__)


def check_log_anomaly(log_path: str, line_count: int, config: dict) -> str:
    """
    ログの急増を検知します。
    
    Args:
        log_path: ログファイルのパス
        line_count: 差分行数
        config: 設定ファイルの内容
        
    Returns:
        str: 警告メッセージ（異常がない場合は空文字列）
    """
    # 閾値の取得（デフォルト: 100行）
    threshold = config.get("log_analysis", {}).get("line_threshold", 100)
    
    if line_count > threshold:
        return f"{log_path} で {line_count} 行の増加を検出（閾値: {threshold}行）"
    
    return ""


def get_recommended_log_path(config: dict) -> Optional[str]:
    """
    OS別の推奨ログパスを取得します。
    
    Args:
        config: 設定ファイルの内容
        
    Returns:
        Optional[str]: 推奨ログパス（unknown OSの場合はNone）
    """
    detector = OSDetector(config)
    os_family = detector.detect_os_family()
    
    log_path = detector.get_log_path()
    
    if os_family == 'unknown':
        logger.info("Unknown OS detected, log path recommendation suppressed")
        return None
    
    logger.debug("Recommended log path for %s: %s", os_family, log_path)
    return log_path


def should_show_log_advice(config: dict) -> bool:
    """
    ログアドバイスを表示すべきかどうかを判定します。
    
    Args:
        config: 設定ファイルの内容
        
    Returns:
        bool: ログアドバイスを表示すべき場合はTrue
    """
    detector = OSDetector(config)
    os_family = detector.detect_os_family()
    
    # unknown OSではログアドバイスを抑制
    if os_family == 'unknown':
        logger.info("Unknown OS detected, log advice suppressed")
        return False
    
    return True
