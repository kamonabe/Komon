import psutil


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
