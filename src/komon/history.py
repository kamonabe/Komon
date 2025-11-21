"""
履歴管理モジュール

リソース使用履歴の保存とローテーション機能を提供します。
"""

import os
import csv
import json
from datetime import datetime
from pathlib import Path


HISTORY_DIR = "data/usage_history"
MAX_HISTORY_FILES = 95


def rotate_history():
    """
    履歴ファイルをローテーションします。
    最大95世代まで保持し、古いファイルは自動削除されます。
    """
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    # 既存ファイルの取得
    history_files = sorted(
        Path(HISTORY_DIR).glob("usage_*.csv"),
        key=lambda p: p.stat().st_mtime
    )
    
    # 古いファイルを削除
    if len(history_files) >= MAX_HISTORY_FILES:
        for old_file in history_files[:len(history_files) - MAX_HISTORY_FILES + 1]:
            try:
                old_file.unlink()
                print(f"🗑️ 古い履歴ファイルを削除: {old_file.name}")
            except Exception as e:
                print(f"⚠️ ファイル削除エラー: {e}")


def save_current_usage(usage: dict):
    """
    現在のリソース使用状況を履歴ファイルに保存します。
    
    Args:
        usage: リソース使用率データ
    """
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{HISTORY_DIR}/usage_{timestamp}.csv"
    
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "cpu", "mem", "disk"])
            writer.writerow([
                datetime.now().isoformat(),
                usage.get("cpu", 0),
                usage.get("mem", 0),
                usage.get("disk", 0)
            ])
            
            # プロセス情報も追記
            if "cpu_by_process" in usage:
                writer.writerow([])
                writer.writerow(["CPU上位プロセス"])
                writer.writerow(["name", "cpu_percent"])
                for proc in usage["cpu_by_process"]:
                    writer.writerow([proc["name"], proc["cpu"]])
            
            if "mem_by_process" in usage:
                writer.writerow([])
                writer.writerow(["メモリ上位プロセス"])
                writer.writerow(["name", "mem_mb"])
                for proc in usage["mem_by_process"]:
                    writer.writerow([proc["name"], proc["mem"]])
        
        print(f"📝 使用履歴を保存: {filename}")
        
    except Exception as e:
        print(f"❌ 履歴保存エラー: {e}")


def get_history(limit: int = 10) -> list:
    """
    過去の使用履歴を取得します。
    
    Args:
        limit: 取得する履歴の件数
        
    Returns:
        list: 履歴データのリスト
    """
    if not os.path.exists(HISTORY_DIR):
        return []
    
    history_files = sorted(
        Path(HISTORY_DIR).glob("usage_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:limit]
    
    history_data = []
    for file_path in history_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    history_data.append(row)
                    break  # 最初の行のみ
        except Exception:
            pass
    
    return history_data
