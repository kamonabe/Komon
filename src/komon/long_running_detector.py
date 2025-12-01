"""
継続実行中プロセスの検出モジュール

特定スクリプトが長時間実行されている場合に検出し、
継続稼働を助言表示する機能を提供します。
"""

import logging
import time
from typing import List, Dict, Any, Optional
import psutil

logger = logging.getLogger(__name__)

# 対象とするスクリプト拡張子
TARGET_EXTENSIONS = ('.py', '.sh', '.rb', '.pl')


def detect_long_running_processes(
    threshold_seconds: int = 3600,
    target_extensions: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    長時間実行プロセスを検出
    
    Args:
        threshold_seconds: 閾値（秒）。この時間以上実行されているプロセスを検出
        target_extensions: 対象拡張子のリスト。Noneの場合はデフォルト値を使用
    
    Returns:
        長時間実行プロセスのリスト
        [
            {
                'script': 'backup.py',
                'pid': 1234,
                'runtime_seconds': 7200,
                'runtime_formatted': '2時間'
            },
            ...
        ]
    """
    # 閾値の検証
    if not isinstance(threshold_seconds, int) or threshold_seconds < 1:
        logger.warning(
            "Invalid threshold_seconds value: %s, using default (3600)",
            threshold_seconds
        )
        threshold_seconds = 3600
    
    # 対象拡張子の設定
    if target_extensions is None:
        target_extensions = list(TARGET_EXTENSIONS)
    
    # 現在時刻を取得
    current_time = time.time()
    
    # 長時間実行プロセスを検出
    long_running = []
    
    try:
        for proc in psutil.process_iter(['pid', 'cmdline', 'create_time']):
            try:
                cmdline = proc.info['cmdline']
                if not cmdline:
                    continue
                
                # スクリプト名を抽出
                script_name = _extract_script_name(cmdline, target_extensions)
                if not script_name:
                    continue
                
                # 実行時間を計算
                create_time = proc.info['create_time']
                runtime_seconds = int(current_time - create_time)
                
                # 閾値以上なら結果に追加
                if runtime_seconds >= threshold_seconds:
                    long_running.append({
                        'script': script_name,
                        'pid': proc.info['pid'],
                        'runtime_seconds': runtime_seconds,
                        'runtime_formatted': _format_duration(runtime_seconds)
                    })
            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # プロセスが終了した、またはアクセス拒否された場合はスキップ
                continue
            except Exception as e:
                logger.debug("Error processing process: %s", e)
                continue
    
    except Exception as e:
        logger.error(
            "Failed to iterate processes: %s",
            e,
            exc_info=True
        )
        return []
    
    # 実行時間の降順でソート
    long_running.sort(key=lambda x: x['runtime_seconds'], reverse=True)
    
    logger.debug(
        "Detected %d long-running processes (threshold: %d seconds)",
        len(long_running),
        threshold_seconds
    )
    
    return long_running


def _extract_script_name(
    cmdline: List[str],
    target_extensions: List[str]
) -> Optional[str]:
    """
    コマンドラインからスクリプト名を抽出
    
    Args:
        cmdline: コマンドライン引数
        target_extensions: 対象拡張子のリスト
    
    Returns:
        スクリプト名（拡張子付き）、または None
    
    Examples:
        ['python', '/path/to/script.py', 'arg1'] → 'script.py'
        ['/bin/bash', '/path/to/script.sh'] → 'script.sh'
        ['python', '-m', 'module'] → None（モジュール実行は対象外）
    """
    if not cmdline or len(cmdline) == 0:
        return None
    
    # モジュール実行（python -m module）は対象外
    if '-m' in cmdline:
        return None
    
    # コマンドライン引数を走査
    for arg in cmdline:
        # 対象拡張子を持つファイルを探す
        for ext in target_extensions:
            if arg.endswith(ext):
                # ファイル名のみを抽出（パスを除去）
                import os
                return os.path.basename(arg)
    
    return None


def _format_duration(seconds: int) -> str:
    """
    秒数を人間に読みやすい形式に変換
    
    Args:
        seconds: 秒数
    
    Returns:
        フォーマットされた文字列
    
    Examples:
        30 → '30秒'
        90 → '1分30秒'
        3661 → '1時間1分'
        86400 → '1日'
        90061 → '1日1時間1分'
    """
    if seconds < 0:
        return '0秒'
    
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    
    if days > 0:
        parts.append(f'{days}日')
    if hours > 0:
        parts.append(f'{hours}時間')
    if minutes > 0:
        parts.append(f'{minutes}分')
    if secs > 0 and days == 0 and hours == 0:
        # 日・時間がない場合のみ秒を表示
        parts.append(f'{secs}秒')
    
    if not parts:
        return '0秒'
    
    return ''.join(parts)
