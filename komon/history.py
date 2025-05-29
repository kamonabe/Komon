import os
import json
from datetime import datetime

HISTORY_FILE = "usage_history.json"
MAX_GENERATIONS = 95

def rotate_history(file_path=HISTORY_FILE, generations=MAX_GENERATIONS):
    for i in reversed(range(1, generations + 1)):
        older = f"{file_path}.{i}"
        newer = f"{file_path}.{i - 1}" if i > 1 else file_path

        if os.path.exists(older):
            os.remove(older)
        if os.path.exists(newer):
            os.rename(newer, older)

def save_current_usage(usage, file_path=HISTORY_FILE):
    data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        **usage
    }
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
