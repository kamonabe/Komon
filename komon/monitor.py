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
        cpu = psutil.cpu_percent(interval=1)             # 1秒平均のCPU使用率
        mem = psutil.virtual_memory().percent            # メモリ使用率
        disk = psutil.disk_usage("/").percent            # ルートディスク使用率
    except Exception as e:
        print(f"❌ リソース使用率の取得に失敗しました: {e}")
        return {"cpu": None, "mem": None, "disk": None}

    return {
        "cpu": cpu,
        "mem": mem,
        "disk": disk
    }


def get_cpu_by_process(top_n=3):
    usage = defaultdict(float)

    # 初期スキャン（0.0%にならないよう1回呼ぶ）
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(0.5)  # ← 少し待つと2回目で正しい数値が出る

    for proc in psutil.process_iter(attrs=['name', 'cpu_percent']):
        try:
            name = proc.info['name'] or 'unknown'
            cpu = proc.info['cpu_percent']
            if cpu > 0:
                usage[name] += cpu
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
    return [{"name": name, "cpu": round(val, 1)} for name, val in sorted_usage[:top_n]]



def collect_detailed_resource_usage():
    """
    通常のリソース使用率に加えて、プロセスごとのCPU使用率も含めた詳細版を返す。
    """
    base = collect_resource_usage()
    base["cpu_by_process"] = get_cpu_by_process()
    return base

