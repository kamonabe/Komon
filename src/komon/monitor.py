"""
リソース監視モジュール

CPU、メモリ、ディスク使用率の収集と、
プロセス別の詳細情報取得を行います。
"""

import psutil


def collect_resource_usage() -> dict:
    """
    基本的なリソース使用率を収集します。
    
    Returns:
        dict: cpu, mem, disk の使用率（%）
    """
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    return {
        "cpu": cpu,
        "mem": mem,
        "disk": disk
    }


def collect_detailed_resource_usage() -> dict:
    """
    プロセス別の詳細情報を含むリソース使用率を収集します。
    
    Returns:
        dict: 基本使用率 + プロセス別CPU/メモリ情報
    """
    usage = collect_resource_usage()
    
    # CPU使用率上位5プロセス
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append({
                'name': proc.info['name'],
                'cpu': proc.info['cpu_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    processes.sort(key=lambda x: x['cpu'], reverse=True)
    usage['cpu_by_process'] = processes[:5]
    
    # メモリ使用量上位5プロセス
    mem_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
            mem_processes.append({
                'name': proc.info['name'],
                'mem': round(mem_mb, 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    mem_processes.sort(key=lambda x: x['mem'], reverse=True)
    usage['mem_by_process'] = mem_processes[:5]
    
    return usage
