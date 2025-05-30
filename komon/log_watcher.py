import os
import pickle
import hashlib

SAVE_DIR = "komon_data/logstate"
os.makedirs(SAVE_DIR, exist_ok=True)

def get_inode(filepath):
    return os.stat(filepath).st_ino

def get_save_path(filepath):
    # ファイルパスをハッシュ化して保存名に変換（衝突対策）
    hash_name = hashlib.md5(filepath.encode()).hexdigest()
    return os.path.join(SAVE_DIR, f"{hash_name}.pkl")

def load_last_state(filepath):
    save_path = get_save_path(filepath)
    if os.path.exists(save_path):
        with open(save_path, "rb") as f:
            return pickle.load(f)
    return None

def save_current_state(filepath, inode, last_line):
    state = {
        "inode": inode,
        "last_line": last_line
    }
    save_path = get_save_path(filepath)
    with open(save_path, "wb") as f:
        pickle.dump(state, f)

def read_log_diff(filepath):
    try:
        with open(filepath, "r") as f:
            inode = get_inode(filepath)
            last_state = load_last_state(filepath)
            if last_state and last_state["inode"] == inode:
                # 差分読み取り
                for _ in range(last_state["last_line"]):
                    f.readline()
                new_lines = f.readlines()
                new_line_count = len(new_lines)
                print(f"[{filepath}] {new_line_count} new lines.")
                save_current_state(filepath, inode, last_state["last_line"] + new_line_count)
            else:
                # ローテーション or 初回読み取り
                lines = f.readlines()
                print(f"[{filepath}] (rotated or first-time) {len(lines)} lines.")
                save_current_state(filepath, inode, len(lines))
    except FileNotFoundError:
        print(f"[{filepath}] File not found.")
