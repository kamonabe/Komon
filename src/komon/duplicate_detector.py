"""
多重実行プロセスの検出モジュール

cronなどによる同一スクリプトの多重起動を検出し、
リソース圧迫の原因として助言する機能を提供します。
"""

import logging
from typing import List, Dict, Any, Optional
import psutil

logger = logging.getLogger(__name__)

# 対象とするスクリプト拡張子
TARGET_EXTENSIONS = ('.py', '.sh', '.rb', '.pl')


def detect_duplicate_processes(threshold: int = 3) -> List[Dict[str, Any]]:
    """
    多重実行プロセスを検出
    
    Args:
        threshold: 警告閾値（この数以上で警告）
    
    Returns:
        多重実行プロセスのリスト
        [
            {
                'script': 'backup.py',
                'count': 5,
                'pids': [1234, 1235, 1236, 1237, 1238]
            },
            ...
        ]
    """
    # 閾値の検証
    if not isinstance(threshold, int) or threshold < 1:
        logger.warning(
            "Invalid threshold value: %s, using default (3)",
            threshold
        )
        threshold = 3
    
    # スクリプト名ごとのプロセス情報を集計
    script_processes: Dict[str, List[int]] = {}
    
    try:
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if not cmdline:
                    continue
                
                # スクリプト名を抽出
                script_name = _extract_script_name(cmdline)
                if script_name:
                    if script_name not in script_processes:
                        script_processes[script_name] = []
                    script_processes[script_name].append(proc.info['pid'])
            
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
    
    # 閾値を超えるプロセスを抽出
    duplicates = []
    for script, pids in script_processes.items():
        if len(pids) >= threshold:
            duplicates.append({
                'script': script,
                'count': len(pids),
                'pids': sorted(pids)
            })
    
    # スクリプト名でソート
    duplicates.sort(key=lambda x: x['script'])
    
    logger.debug(
        "Detected %d duplicate processes (threshold: %d)",
        len(duplicates),
        threshold
    )
    
    return duplicates


def _extract_script_name(cmdline: List[str]) -> Optional[str]:
    """
    コマンドラインからスクリプト名を抽出
    
    Args:
        cmdline: コマンドライン引数
    
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
        for ext in TARGET_EXTENSIONS:
            if arg.endswith(ext):
                # ファイル名のみを抽出（パスを除去）
                import os
                return os.path.basename(arg)
    
    return None
