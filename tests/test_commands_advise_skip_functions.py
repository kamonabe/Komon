"""
src/komon/commands/advise.py のスキップ機能関連のテスト

スキップ機能（should_skip, record_skip, skippable_advice）をテストします。
"""

import unittest
import tempfile
import json
import os
import datetime
from unittest.mock import patch, MagicMock
from pathlib import Path
from io import StringIO

from src.komon.commands.advise import (
    get_skip_file_path,
    should_skip,
    record_skip,
    skippable_advice
)


class TestSkipFunctions(unittest.TestCase):
    """スキップ機能のテスト"""
    
    def setUp(self):
        """テスト用の一時ディレクトリを作成"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_skip_file_path(self):
        """スキップファイルパスの取得テスト"""
        expected_path = self.config_dir / "data" / "komon_data" / "skip_advices.json"
        actual_path = get_skip_file_path(self.config_dir)
        
        self.assertEqual(actual_path, expected_path)
    
    def test_should_skip_no_file(self):
        """スキップファイルが存在しない場合のテスト"""
        result = should_skip("test_key", self.config_dir)
        self.assertFalse(result)
    
    def test_should_skip_empty_file(self):
        """空のスキップファイルの場合のテスト"""
        skip_file = get_skip_file_path(self.config_dir)
        skip_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 空のJSONファイルを作成
        with open(skip_file, "w") as f:
            json.dump({}, f)
        
        result = should_skip("test_key", self.config_dir)
        self.assertFalse(result)
    
    def test_should_skip_key_not_found(self):
        """キーが存在しない場合のテスト"""
        skip_file = get_skip_file_path(self.config_dir)
        skip_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 他のキーのデータを作成
        data = {
            "other_key": {
                "skipped_at": datetime.datetime.now().isoformat()
            }
        }
        with open(skip_file, "w") as f:
            json.dump(data, f)
        
        result = should_skip("test_key", self.config_dir)
        self.assertFalse(result)
    
    def test_should_skip_recent_skip(self):
        """最近スキップされた場合のテスト"""
        skip_file = get_skip_file_path(self.config_dir)
        skip_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 1日前のタイムスタンプを作成
        recent_time = datetime.datetime.now() - datetime.timedelta(days=1)
        data = {
            "test_key": {
                "skipped_at": recent_time.isoformat()
            }
        }
        with open(skip_file, "w") as f:
            json.dump(data, f)
        
        result = should_skip("test_key", self.config_dir, days=7)
        self.assertTrue(result)
    
    def test_should_skip_old_skip(self):
        """古いスキップの場合のテスト"""
        skip_file = get_skip_file_path(self.config_dir)
        skip_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 8日前のタイムスタンプを作成
        old_time = datetime.datetime.now() - datetime.timedelta(days=8)
        data = {
            "test_key": {
                "skipped_at": old_time.isoformat()
            }
        }
        with open(skip_file, "w") as f:
            json.dump(data, f)
        
        result = should_skip("test_key", self.config_dir, days=7)
        self.assertFalse(result)
    
    def test_should_skip_invalid_timestamp(self):
        """無効なタイムスタンプの場合のテスト"""
        skip_file = get_skip_file_path(self.config_dir)
        skip_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 無効なタイムスタンプを作成
        data = {
            "test_key": {
                "skipped_at": "invalid_timestamp"
            }
        }
        with open(skip_file, "w") as f:
            json.dump(data, f)
        
        result = should_skip("test_key", self.config_dir)
        self.assertFalse(result)
    
    def test_should_skip_corrupted_file(self):
        """破損したJSONファイルの場合のテスト"""
        skip_file = get_skip_file_path(self.config_dir)
        skip_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 無効なJSONを作成
        with open(skip_file, "w") as f:
            f.write("invalid json content")
        
        result = should_skip("test_key", self.config_dir)
        self.assertFalse(result)
    
    def test_record_skip_new_file(self):
        """新しいスキップファイルの作成テスト"""
        record_skip("test_key", self.config_dir)
        
        skip_file = get_skip_file_path(self.config_dir)
        self.assertTrue(skip_file.exists())
        
        with open(skip_file, "r") as f:
            data = json.load(f)
        
        self.assertIn("test_key", data)
        self.assertIn("skipped_at", data["test_key"])
    
    def test_record_skip_existing_key(self):
        """既存キーのスキップ記録テスト"""
        # 最初の記録
        record_skip("test_key", self.config_dir)
        
        # 2回目の記録
        record_skip("test_key", self.config_dir)
        
        skip_file = get_skip_file_path(self.config_dir)
        with open(skip_file, "r") as f:
            data = json.load(f)
        
        # 2回目の記録でタイムスタンプが更新されることを確認
        self.assertIn("test_key", data)
        self.assertIn("skipped_at", data["test_key"])
    
    def test_record_skip_multiple_keys(self):
        """複数キーのスキップ記録テスト"""
        record_skip("key1", self.config_dir)
        record_skip("key2", self.config_dir)
        
        skip_file = get_skip_file_path(self.config_dir)
        with open(skip_file, "r") as f:
            data = json.load(f)
        
        self.assertIn("key1", data)
        self.assertIn("key2", data)
        self.assertIn("skipped_at", data["key1"])
        self.assertIn("skipped_at", data["key2"])
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_record_skip_permission_error(self, mock_stdout):
        """権限エラーの場合のテスト"""
        # 読み取り専用ディレクトリを作成
        readonly_dir = Path(self.temp_dir) / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)
        
        try:
            record_skip("test_key", readonly_dir)
            
            output = mock_stdout.getvalue()
            self.assertIn("スキップ記録に失敗しました", output)
        finally:
            # クリーンアップのために権限を戻す
            os.chmod(readonly_dir, 0o755)
    
    @patch('src.komon.commands.advise.should_skip')
    def test_skippable_advice_should_skip(self, mock_should_skip):
        """スキップすべき場合のテスト"""
        mock_should_skip.return_value = True
        
        action_called = False
        def test_action():
            nonlocal action_called
            action_called = True
        
        skippable_advice("test_key", "Test question?", test_action, self.config_dir)
        
        # アクションが呼ばれないことを確認
        self.assertFalse(action_called)
        mock_should_skip.assert_called_once_with("test_key", self.config_dir)
    
    @patch('src.komon.commands.advise.should_skip')
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('src.komon.commands.advise.record_skip')
    def test_skippable_advice_user_says_yes(self, mock_record_skip, mock_ask_yes_no, mock_should_skip):
        """ユーザーがYesと答えた場合のテスト"""
        mock_should_skip.return_value = False
        mock_ask_yes_no.return_value = True
        
        action_called = False
        def test_action():
            nonlocal action_called
            action_called = True
        
        skippable_advice("test_key", "Test question?", test_action, self.config_dir)
        
        # アクションが呼ばれることを確認
        self.assertTrue(action_called)
        mock_ask_yes_no.assert_called_once_with("Test question?")
        mock_record_skip.assert_not_called()
    
    @patch('src.komon.commands.advise.should_skip')
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('src.komon.commands.advise.record_skip')
    def test_skippable_advice_user_says_no(self, mock_record_skip, mock_ask_yes_no, mock_should_skip):
        """ユーザーがNoと答えた場合のテスト"""
        mock_should_skip.return_value = False
        mock_ask_yes_no.return_value = False
        
        action_called = False
        def test_action():
            nonlocal action_called
            action_called = True
        
        skippable_advice("test_key", "Test question?", test_action, self.config_dir)
        
        # アクションが呼ばれないことを確認
        self.assertFalse(action_called)
        mock_ask_yes_no.assert_called_once_with("Test question?")
        mock_record_skip.assert_called_once_with("test_key", self.config_dir)


if __name__ == '__main__':
    unittest.main()