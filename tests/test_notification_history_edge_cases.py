"""
通知履歴のエッジケーステスト

エラーハンドリングや特殊なケースをテストします。
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from komon.notification_history import (
    save_notification,
    load_notification_history,
    format_notification
)


class TestNotificationHistoryEdgeCases:
    """通知履歴のエッジケーステスト"""
    
    def test_save_notification_with_invalid_queue_data(self):
        """キューファイルが不正な形式の場合、新規作成される"""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "queue.json")
            
            # 不正な形式（リストではなく辞書）のファイルを作成
            with open(queue_file, "w", encoding="utf-8") as f:
                json.dump({"invalid": "data"}, f)
            
            # 通知を保存
            result = save_notification(
                metric_type="cpu",
                metric_value=75.0,
                message="Test",
                queue_file=queue_file
            )
            
            assert result is True
            
            # 正しいリスト形式で保存されている
            with open(queue_file, "r", encoding="utf-8") as f:
                queue = json.load(f)
            
            assert isinstance(queue, list)
            assert len(queue) == 1
    
    def test_save_notification_with_io_error(self):
        """IOエラーが発生した場合、Falseを返す"""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "subdir", "queue.json")
            
            # ディレクトリの代わりにファイルを作成（書き込み不可にする）
            subdir = os.path.join(tmpdir, "subdir")
            with open(subdir, "w") as f:
                f.write("dummy")
            
            result = save_notification(
                metric_type="cpu",
                metric_value=75.0,
                message="Test",
                queue_file=queue_file
            )
            
            # IOエラーが発生するが、例外は発生せずFalseを返す
            assert result is False
    
    def test_load_notification_history_with_corrupted_file(self):
        """破損したファイルの場合、空のリストを返す"""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "queue.json")
            
            # 破損したJSONファイルを作成
            with open(queue_file, "w", encoding="utf-8") as f:
                f.write("invalid json content")
            
            # 空のリストが返される
            history = load_notification_history(queue_file=queue_file)
            
            assert history == []
    
    def test_load_notification_history_with_io_error(self):
        """IOエラーが発生した場合、空のリストを返す"""
        # 読み込み権限のないファイルをシミュレート
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "queue.json")
            
            # ファイルを作成
            with open(queue_file, "w", encoding="utf-8") as f:
                json.dump([{"test": "data"}], f)
            
            # 読み込み権限を削除（Linuxのみ）
            try:
                os.chmod(queue_file, 0o000)
                
                # IOエラーが発生するが、空のリストが返される
                history = load_notification_history(queue_file=queue_file)
                assert history == []
            finally:
                # 権限を戻す
                os.chmod(queue_file, 0o644)
    
    def test_format_notification_with_missing_fields(self):
        """フィールドが欠けている通知の場合、デフォルト値を使用"""
        notification = {
            "timestamp": "2025-11-24 10:00:00",
            "metric_type": "cpu"
            # metric_valueとmessageが欠けている
        }
        
        formatted = format_notification(notification)
        
        assert "cpu" in formatted.lower()
        assert "2025-11-24 10:00:00" in formatted
    
    def test_format_notification_with_empty_message(self):
        """メッセージが空の場合"""
        notification = {
            "timestamp": "2025-11-24 10:00:00",
            "metric_type": "cpu",
            "metric_value": 75.0,
            "message": ""
        }
        
        formatted = format_notification(notification)
        
        assert "cpu" in formatted.lower()
        assert "75.0" in formatted

    
    def test_load_notification_history_with_non_dict_entries(self):
        """辞書でないエントリが含まれる場合、スキップされる"""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_file = os.path.join(tmpdir, "queue.json")
            
            # 辞書でないエントリを含むファイルを作成
            queue = [
                {
                    "timestamp": "2025-11-24 10:00:00",
                    "metric_type": "cpu",
                    "metric_value": 75.0,
                    "message": "Valid entry"
                },
                "invalid string entry",  # 辞書ではない
                123,  # 辞書ではない
                ["list", "entry"],  # 辞書ではない
                {
                    "timestamp": "2025-11-24 11:00:00",
                    "metric_type": "memory",
                    "metric_value": 85.0,
                    "message": "Another valid entry"
                }
            ]
            
            with open(queue_file, "w", encoding="utf-8") as f:
                json.dump(queue, f)
            
            # 有効なエントリのみが返される
            history = load_notification_history(queue_file=queue_file)
            
            assert len(history) == 2
            assert all(isinstance(entry, dict) for entry in history)
