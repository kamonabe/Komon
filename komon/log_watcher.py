import os
import pickle
from pathlib import Path
from typing import Dict, Optional
import yaml

class LogWatcher:
    def __init__(self, settings_path: str = "settings.yml"):
        self.settings = self._load_settings(settings_path)
        self.logstats_dir = Path("data/logstats")
        self.logstats_dir.mkdir(parents=True, exist_ok=True)

    def _load_settings(self, path: str) -> Dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _get_log_identifier(self, path: str) -> str:
        if path == "systemd journal":
            return "systemd_journal"
        return path.strip("/").replace("/", "_")

    def _get_stat_path(self, path: str) -> Path:
        identifier = self._get_log_identifier(path)
        return self.logstats_dir / f"{identifier}.pkl"

    def save_log_stat(self, path: str, stat: Dict):
        stat_path = self._get_stat_path(path)
        with open(stat_path, 'wb') as f:
            pickle.dump(stat, f)

    def load_log_stat(self, path: str) -> Dict:
        stat_path = self._get_stat_path(path)
        if not stat_path.exists():
            return {}
        with open(stat_path, 'rb') as f:
            return pickle.load(f)

    def get_monitor_targets(self) -> Dict[str, bool]:
        return self.settings.get("log_monitor_targets", {})

    def get_inode(self, filepath: str) -> Optional[int]:
        try:
            return os.stat(filepath).st_ino
        except FileNotFoundError:
            return None

    def read_log_diff(self, filepath: str):
        try:
            with open(filepath, "r") as f:
                inode = self.get_inode(filepath)
                if inode is None:
                    print(f"[{filepath}] File not found.")
                    return

                last_state = self.load_log_stat(filepath)
                if last_state and last_state.get("inode") == inode:
                    # 差分読み取り
                    for _ in range(last_state["last_line"]):
                        f.readline()
                    new_lines = f.readlines()
                    new_line_count = len(new_lines)
                    print(f"[{filepath}] {new_line_count} new lines.")
                    self.save_log_stat(filepath, {
                        "inode": inode,
                        "last_line": last_state["last_line"] + new_line_count
                    })
                else:
                    # ローテーション or 初回読み取り
                    lines = f.readlines()
                    print(f"[{filepath}] (rotated or first-time) {len(lines)} lines.")
                    self.save_log_stat(filepath, {
                        "inode": inode,
                        "last_line": len(lines)
                    })
        except Exception as e:
            print(f"[{filepath}] Error reading file: {e}")
