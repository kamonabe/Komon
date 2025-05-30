import os
import json
from datetime import datetime

# 保存先ディレクトリとファイル名
HISTORY_DIR = "history"
HISTORY_FILE = os.path.join(HISTORY_DIR, "usage_history.json")
MAX_GENERATIONS = 95


def rotate_history(file_path=HISTORY_FILE, max_generations=MAX_GENERATIONS):
    """古い履歴ファイルをローテーション"""
    os.makedirs(HISTORY_DIR, exist_ok=True)

    for i in reversed(range(1, max_generations + 1)):
        older = f"{file_path}.{i}"
        newer = f"{file_path}.{i - 1}" if i > 1 else file_path

        if os.path.exists(older):
            os.remove(older)
        if os.path.exists(newer):
            os.rename(newer, older)


def save_current_usage(usage, file_path=HISTORY_FILE):
    """現在の使用状況をJSONで保存"""
    os.makedirs(HISTORY_DIR, exist_ok=True)

    data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        **usage
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 任意：確認用ログ
    print(f"📝 使用履歴を保存しました: {file_path}")
