import psutil
import time
from collections import defaultdict

def collect_resource_usage() -> dict:
    """
    現在のリソース使用率（CPU・メモリ・ディスク）を収集して返す。

    Returns:
        dict: 使用率をまとめた辞書（%単位）
    """
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
    except Exception as e:
        print(f"❌ リソース使用率の取得に失敗しました: {e}")
        return {"cpu": None, "mem": None, "disk": None}

    return {
        "cpu": cpu,
        "mem": mem,
        "disk": disk
    }

def get_top_process_usage(attr: str, unit_scale: float = 1.0, top_n: int = 5) -> list:
    usage = defaultdict(float)

    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(0.5)

    for proc in psutil.process_iter(attrs=['name', attr]):
        try:
            name = proc.info['name'] or 'unknown'
            val = proc.info.get(attr, 0.0)

            if attr == 'memory_info' and hasattr(val, 'rss'):
                val = val.rss

            if isinstance(val, (int, float)) and val > 0:
                usage[name] += val
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
    key_name = 'cpu' if attr == 'cpu_percent' else 'mem'
    return [
        {"name": name, key_name: round(val / unit_scale, 1)}
        for name, val in sorted_usage[:top_n]
    ]

def get_cpu_by_process(top_n=5):
    return get_top_process_usage('cpu_percent', unit_scale=1.0, top_n=top_n)

def get_mem_by_process(top_n=5):
    return get_top_process_usage('memory_info', unit_scale=1024 * 1024, top_n=top_n)

def collect_detailed_resource_usage():
    base = collect_resource_usage()
    base["cpu_by_process"] = get_cpu_by_process()
    base["mem_by_process"] = get_mem_by_process()
    return base
