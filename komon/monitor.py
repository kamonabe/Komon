import psutil

def collect_resource_usage() -> dict:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    return {
        "cpu": cpu,
        "mem": mem,
        "disk": disk
    }
