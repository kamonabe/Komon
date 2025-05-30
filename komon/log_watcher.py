import os
import pickle
from pathlib import Path
from typing import Dict
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

    def _get_inode(self, filepath: str) -> int:
        return os.stat(filepath).st_ino

    def read_log_diff(self, path: str):
        if path == "systemd journal":
            print(f"[{path}] systemd journalの差分取得は未実装です")
            return

        try:
            with open(path, "r") as f:
                inode = self._get_inode(path)
                last_state = self.load_log_stat(path)
                last_inode = last_state.get("inode")
                last_line = last_state.get("last_line", 0)

                if last_inode == inode:
                    # 差分取得
                    for _ in range(last_line):
                        f.readline()
                    new_lines = f.readlines()
                    print(f"[{path}] {len(new_lines)} new lines.")
                    self.save_log_stat(path, {"inode": inode, "last_line": last_line + len(new_lines)})
                else:
                    # ログローテ or 初回
                    lines = f.readlines()
                    print(f"[{path}] (rotated or first-time) {len(lines)} lines.")
                    self.save_log_stat(path, {"inode": inode, "last_line": len(lines)})
        except FileNotFoundError:
            print(f"[{path}] File not found.")

    def watch_logs(self):
        targets = self.get_monitor_targets()
        for path, enabled in targets.items():
            if enabled:
                self.read_log_diff(path)
