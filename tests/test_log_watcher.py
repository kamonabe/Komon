"""
log_watcher.py のテスト

ログ監視機能のテストを行います。
"""

import pytest
import os
from pathlib import Path
from komon.log_watcher import LogWatcher


@pytest.fixture
def temp_log_dir(tmp_path):
    """テスト用の一時ログディレクトリ"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def temp_state_dir(tmp_path):
    """テスト用の一時状態ディレクトリ"""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    return state_dir


@pytest.fixture
def log_watcher(temp_state_dir):
    """テスト用のLogWatcherインスタンス"""
    return LogWatcher(state_dir=str(temp_state_dir))


class TestLogWatcher:
    """LogWatcherクラスのテスト"""
    
    def test_init_creates_state_dir(self, tmp_path):
        """初期化時に状態ディレクトリが作成される"""
        state_dir = tmp_path / "new_state"
        assert not state_dir.exists()
        
        watcher = LogWatcher(state_dir=str(state_dir))
        
        assert state_dir.exists()
    
    def test_watch_logs_first_run(self, log_watcher, temp_log_dir):
        """初回実行時は全行が差分として検出される"""
        log_file = temp_log_dir / "test.log"
        log_file.write_text("line1\nline2\nline3\n")
        
        results = log_watcher.watch_logs([str(log_file)])
        
        assert str(log_file) in results
        assert results[str(log_file)] == 3
    
    def test_watch_logs_no_change(self, log_watcher, temp_log_dir):
        """ログファイルに変更がない場合、差分は0"""
        log_file = temp_log_dir / "test.log"
        log_file.write_text("line1\nline2\n")
        
        # 1回目の実行
        log_watcher.watch_logs([str(log_file)])
        
        # 2回目の実行（変更なし）
        results = log_watcher.watch_logs([str(log_file)])
        
        assert results[str(log_file)] == 0
    
    def test_watch_logs_with_new_lines(self, log_watcher, temp_log_dir):
        """新しい行が追加された場合、差分が検出される"""
        log_file = temp_log_dir / "test.log"
        log_file.write_text("line1\nline2\n")
        
        # 1回目の実行
        log_watcher.watch_logs([str(log_file)])
        
        # ログに行を追加
        log_file.write_text("line1\nline2\nline3\nline4\n")
        
        # 2回目の実行
        results = log_watcher.watch_logs([str(log_file)])
        
        assert results[str(log_file)] == 2
    
    def test_watch_logs_file_truncated(self, log_watcher, temp_log_dir):
        """ログファイルが切り詰められた場合、差分は0"""
        log_file = temp_log_dir / "test.log"
        log_file.write_text("line1\nline2\nline3\n")
        
        # 1回目の実行
        log_watcher.watch_logs([str(log_file)])
        
        # ログファイルを切り詰め
        log_file.write_text("line1\n")
        
        # 2回目の実行
        results = log_watcher.watch_logs([str(log_file)])
        
        # 行数が減った場合は差分0として扱う
        assert results[str(log_file)] == 0
    
    def test_watch_logs_multiple_files(self, log_watcher, temp_log_dir):
        """複数のログファイルを同時に監視できる"""
        log_file1 = temp_log_dir / "test1.log"
        log_file2 = temp_log_dir / "test2.log"
        log_file1.write_text("line1\nline2\n")
        log_file2.write_text("line1\nline2\nline3\n")
        
        results = log_watcher.watch_logs([str(log_file1), str(log_file2)])
        
        assert str(log_file1) in results
        assert str(log_file2) in results
        assert results[str(log_file1)] == 2
        assert results[str(log_file2)] == 3
    
    def test_watch_logs_file_not_found(self, log_watcher, capsys):
        """存在しないログファイルの場合、警告が表示される"""
        results = log_watcher.watch_logs(["/nonexistent/log.log"])
        
        captured = capsys.readouterr()
        assert "ログファイルが見つかりません" in captured.out
        assert "/nonexistent/log.log" not in results
    
    def test_watch_logs_default_path(self, log_watcher):
        """ログパスを指定しない場合、デフォルトパスが使用される"""
        # デフォルトパス /var/log/messages は存在しない可能性が高いので
        # 警告が出ることを確認
        results = log_watcher.watch_logs()
        
        # エラーが発生せず、空の結果または警告が出ることを確認
        assert isinstance(results, dict)
    
    def test_watch_logs_empty_file(self, log_watcher, temp_log_dir):
        """空のログファイルの場合"""
        log_file = temp_log_dir / "empty.log"
        log_file.write_text("")
        
        results = log_watcher.watch_logs([str(log_file)])
        
        assert results[str(log_file)] == 0
    
    def test_state_file_naming(self, log_watcher):
        """状態ファイル名が正しく生成される"""
        log_path = "/var/log/messages"
        state_file = log_watcher._get_state_file(log_path)
        
        # スラッシュがアンダースコアに置き換えられる
        assert "var_log_messages" in state_file
        assert state_file.endswith(".pkl")
    
    def test_watch_logs_with_unicode(self, log_watcher, temp_log_dir):
        """Unicode文字を含むログファイルを処理できる"""
        log_file = temp_log_dir / "unicode.log"
        log_file.write_text("日本語ログ\n中文日志\n한국어 로그\n", encoding="utf-8")
        
        results = log_watcher.watch_logs([str(log_file)])
        
        assert results[str(log_file)] == 3
