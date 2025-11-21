"""
history.py のテスト

履歴管理機能のテストを行います。
"""

import pytest
import os
import csv
from pathlib import Path
from datetime import datetime
from komon.history import (
    rotate_history,
    save_current_usage,
    get_history,
    HISTORY_DIR,
    MAX_HISTORY_FILES
)


@pytest.fixture
def temp_history_dir(tmp_path, monkeypatch):
    """テスト用の一時履歴ディレクトリ"""
    test_dir = tmp_path / "test_history"
    monkeypatch.setattr('komon.history.HISTORY_DIR', str(test_dir))
    return test_dir


class TestRotateHistory:
    """rotate_history関数のテスト"""
    
    def test_create_history_dir_if_not_exists(self, temp_history_dir):
        """履歴ディレクトリが存在しない場合に作成される"""
        assert not temp_history_dir.exists()
        rotate_history()
        assert temp_history_dir.exists()
    
    def test_no_deletion_when_under_limit(self, temp_history_dir):
        """ファイル数が上限未満の場合は削除されない"""
        temp_history_dir.mkdir(parents=True)
        
        # 10個のファイルを作成
        for i in range(10):
            (temp_history_dir / f"usage_{i:03d}.csv").touch()
        
        rotate_history()
        
        files = list(temp_history_dir.glob("usage_*.csv"))
        assert len(files) == 10
    
    def test_delete_old_files_when_over_limit(self, temp_history_dir, monkeypatch):
        """ファイル数が上限を超える場合に古いファイルが削除される"""
        temp_history_dir.mkdir(parents=True)
        monkeypatch.setattr('komon.history.MAX_HISTORY_FILES', 5)
        
        # 10個のファイルを作成（古い順）
        import time
        for i in range(10):
            file_path = temp_history_dir / f"usage_{i:03d}.csv"
            file_path.touch()
            time.sleep(0.01)  # ファイル作成時刻を確実に異ならせる
        
        rotate_history()
        
        files = list(temp_history_dir.glob("usage_*.csv"))
        assert len(files) <= 5


class TestSaveCurrentUsage:
    """save_current_usage関数のテスト"""
    
    def test_save_basic_usage(self, temp_history_dir):
        """基本的な使用率データの保存"""
        usage = {
            "cpu": 45.5,
            "mem": 60.2,
            "disk": 75.8
        }
        
        save_current_usage(usage)
        
        # ファイルが作成されたことを確認
        files = list(temp_history_dir.glob("usage_*.csv"))
        assert len(files) == 1
        
        # ファイル内容を確認
        with open(files[0], 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert rows[0] == ["timestamp", "cpu", "mem", "disk"]
            assert float(rows[1][1]) == 45.5
            assert float(rows[1][2]) == 60.2
            assert float(rows[1][3]) == 75.8
    
    def test_save_with_process_info(self, temp_history_dir):
        """プロセス情報を含むデータの保存"""
        usage = {
            "cpu": 50.0,
            "mem": 60.0,
            "disk": 70.0,
            "cpu_by_process": [
                {"name": "python", "cpu": 25.5},
                {"name": "chrome", "cpu": 15.2}
            ],
            "mem_by_process": [
                {"name": "python", "mem": 100.5},
                {"name": "chrome", "mem": 200.3}
            ]
        }
        
        save_current_usage(usage)
        
        files = list(temp_history_dir.glob("usage_*.csv"))
        assert len(files) == 1
        
        # プロセス情報が保存されていることを確認
        with open(files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            assert "CPU上位プロセス" in content
            assert "メモリ上位プロセス" in content
            assert "python" in content
            assert "chrome" in content
    
    def test_filename_format(self, temp_history_dir):
        """ファイル名が正しい形式で生成される"""
        usage = {"cpu": 10.0, "mem": 20.0, "disk": 30.0}
        
        save_current_usage(usage)
        
        files = list(temp_history_dir.glob("usage_*.csv"))
        assert len(files) == 1
        
        # ファイル名が usage_YYYYMMDD_HHMMSS.csv の形式か確認
        filename = files[0].name
        assert filename.startswith("usage_")
        assert filename.endswith(".csv")
        assert len(filename) == len("usage_20231201_123456.csv")


class TestGetHistory:
    """get_history関数のテスト"""
    
    def test_empty_history(self, temp_history_dir):
        """履歴が存在しない場合は空リストを返す"""
        result = get_history()
        assert result == []
    
    def test_get_recent_history(self, temp_history_dir):
        """最近の履歴を取得できる"""
        temp_history_dir.mkdir(parents=True)
        
        # 3つの履歴ファイルを作成
        import time
        for i in range(3):
            file_path = temp_history_dir / f"usage_{i:03d}.csv"
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "cpu", "mem", "disk"])
                writer.writerow([datetime.now().isoformat(), 10+i, 20+i, 30+i])
            time.sleep(0.01)
        
        result = get_history(limit=10)
        
        assert len(result) == 3
        assert "cpu" in result[0]
    
    def test_limit_history_count(self, temp_history_dir):
        """limit パラメータで取得件数を制限できる"""
        temp_history_dir.mkdir(parents=True)
        
        # 10個の履歴ファイルを作成
        import time
        for i in range(10):
            file_path = temp_history_dir / f"usage_{i:03d}.csv"
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "cpu", "mem", "disk"])
                writer.writerow([datetime.now().isoformat(), 10, 20, 30])
            time.sleep(0.01)
        
        result = get_history(limit=5)
        
        assert len(result) == 5
