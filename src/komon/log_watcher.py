"""
ログ監視モジュール

ログファイルの差分行数を監視します。
"""

import os
import pickle
from pathlib import Path


STATE_DIR = "data/logstats"


class LogWatcher:
    """ログファイルの差分を監視するクラス"""
    
    def __init__(self, state_dir: str = STATE_DIR):
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)
    
    def _get_state_file(self, log_path: str) -> str:
        """ログパスから状態ファイルのパスを生成"""
        safe_name = log_path.strip("/").replace("/", "_")
        return f"{self.state_dir}/{safe_name}.pkl"
    
    def _load_last_position(self, log_path: str) -> int:
        """前回の読み取り位置を取得"""
        state_file = self._get_state_file(log_path)
        if os.path.exists(state_file):
            try:
                with open(state_file, "rb") as f:
                    return pickle.load(f)
            except Exception:
                pass
        return 0
    
    def _save_position(self, log_path: str, position: int):
        """現在の読み取り位置を保存"""
        state_file = self._get_state_file(log_path)
        try:
            with open(state_file, "wb") as f:
                pickle.dump(position, f)
        except Exception as e:
            print(f"⚠️ 状態保存エラー ({log_path}): {e}")
    
    def watch_logs(self, log_paths: list = None) -> dict:
        """
        ログファイルの差分行数を取得します。
        
        Args:
            log_paths: 監視対象のログファイルパスリスト
            
        Returns:
            dict: {ログパス: 差分行数}
        """
        if log_paths is None:
            log_paths = ["/var/log/messages"]
        
        results = {}
        
        for log_path in log_paths:
            if not os.path.exists(log_path):
                print(f"⚠️ ログファイルが見つかりません: {log_path}")
                continue
            
            try:
                # 現在の行数を取得
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    current_lines = sum(1 for _ in f)
                
                # 前回の行数を取得
                last_lines = self._load_last_position(log_path)
                
                # 差分を計算
                diff = max(0, current_lines - last_lines)
                results[log_path] = diff
                
                # 現在の位置を保存
                self._save_position(log_path, current_lines)
                
            except Exception as e:
                print(f"❌ ログ監視エラー ({log_path}): {e}")
        
        return results
