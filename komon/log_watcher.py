import os
import pickle
from pathlib import Path
from typing import Dict, List
import yaml


class LogWatcher:
    def __init__(self, settings_path: str = "settings.yml"):
        self.settings = self._load_settings(settings_path)
        self.logstats_dir = Path("data/logstats")
        self.logstats_dir.mkdir(parents=True, exist_ok=True)

    def _load_settings(self, path: str) -> Dict:
        """YAML設定ファイルを読み込む"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _get_log_identifier(self, path: str) -> str:
        """ログファイルのパスを識別子（ファイル名）に変換"""
        if path == "systemd journal":
            return "systemd_journal"
        return path.strip("/").replace("/", "_")

    def _get_stat_path(self, path: str) -> Path:
        """差分保存ファイルのパスを取得"""
        identifier = self._get_log_identifier(path)
        return self.logstats_dir / f"{identifier}.pkl"

    def save_log_stat(self, path: str, stat: Dict):
        """現在のログ状態（inode・最終行数）を保存"""
        stat_path = self._get_stat_path(path)
        with open(stat_path, 'wb') as f:
            pickle.dump(stat, f)

    def load_log_stat(self, path: str) -> Dict:
        """前回保存されたログ状態を読み込み"""
        stat_path = self._get_stat_path(path)
        if not stat_path.exists():
            return {}
        with open(stat_path, 'rb') as f:
            return pickle.load(f)

    def get_monitor_targets(self) -> Dict[str, bool]:
        """監視対象のログファイル一覧を取得"""
        return self.settings.get("log_monitor_targets", {})

    def _get_inode(self, filepath: str) -> int:
        """ファイルのinode番号を取得"""
        return os.stat(filepath).st_ino

    def read_log_diff(self, path: str) -> List[str]:
        """指定ログの新規行のみ返す（差分）"""
        if path == "systemd journal":
            print(f"[{path}] systemd journalの差分取得は未実装です")
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                inode = self._get_inode(path)
                last_state = self.load_log_stat(path)
                last_inode = last_state.get("inode")
                last_line = last_state.get("last_line", 0)

                if last_inode == inode:
                    for _ in range(last_line):
                        f.readline()
                    new_lines = f.readlines()
                    print(f"[{path}] {len(new_lines)} new lines.")
                    self.save_log_stat(path, {"inode": inode, "last_line": last_line + len(new_lines)})
                    return new_lines
                else:
                    # ログローテ or 初回起動
                    lines = f.readlines()
                    print(f"[{path}] (rotated or first-time) {len(lines)} lines.")
                    self.save_log_stat(path, {"inode": inode, "last_line": len(lines)})
                    return lines

        except FileNotFoundError:
            print(f"[{path}] File not found.")
        except PermissionError:
            print(f"[{path}] Permission denied.")
        except Exception as e:
            print(f"[{path}] Unexpected error: {e}")

        return []

    def watch_logs(self) -> Dict[str, int]:
        """
        監視対象のログファイルすべてをチェックし、
        差分行数を辞書で返す（例：{'/var/log/messages': 10}）
        """
        result = {}
        targets = self.get_monitor_targets()
        for path, enabled in targets.items():
            if enabled:
                new_lines = self.read_log_diff(path)
                result[path] = len(new_lines)
        return result
