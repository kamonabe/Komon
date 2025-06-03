import subprocess
import re

def get_security_updates():
    """
    AlmaLinux環境でセキュリティアップデートがあるかどうかを確認する。
    `dnf updateinfo` コマンドを使う。
    
    Returns:
        dict: {'available': bool, 'count': int, 'list': [str]}
    """
    try:
        result = subprocess.run(
            ["dnf", "updateinfo", "list", "security"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            encoding="utf-8"
        )
        output = result.stdout

        lines = [line for line in output.splitlines() if line.strip() and not line.startswith("Last metadata expiration")]
        packages = [line.strip() for line in lines if re.match(r'^\S+\s+\S+', line)]

        return {
            "available": len(packages) > 0,
            "count": len(packages),
            "list": packages
        }
    except Exception as e:
        return {
            "available": False,
            "count": 0,
            "list": [],
            "error": str(e)
        }

def reboot_required():
    """
    AlmaLinuxでは /var/run/reboot-required が使われる場合があるが、
    ここでは常に False を返す（標準では使われていない）。
    """
    return False

