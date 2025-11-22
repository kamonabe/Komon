"""
cli.py のテスト

CLIエントリーポイントのテストを行います。
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from komon.cli import main, print_usage


class TestPrintUsage:
    """print_usage関数のテスト"""
    
    def test_print_usage_output(self, capsys):
        """使用方法が正しく表示される"""
        print_usage()
        
        captured = capsys.readouterr()
        assert "Komon" in captured.out
        assert "komon initial" in captured.out
        assert "komon status" in captured.out
        assert "komon advise" in captured.out
        assert "komon guide" in captured.out


class TestMain:
    """main関数のテスト"""
    
    @patch('sys.argv', ['komon'])
    def test_main_no_arguments(self, capsys):
        """引数なしで実行した場合、使用方法が表示される"""
        main()
        
        captured = capsys.readouterr()
        assert "使用方法" in captured.out or "Komon" in captured.out
    
    @patch('sys.argv', ['komon', 'initial'])
    @patch('komon.cli.subprocess.run')
    @patch('komon.cli.os.path.exists')
    @patch('komon.cli.os.getcwd')
    def test_main_initial_command(self, mock_getcwd, mock_exists, mock_run):
        """initialコマンドが正しく実行される"""
        mock_getcwd.return_value = "/test/path"
        mock_exists.return_value = True
        
        main()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "initial.py" in call_args[-1]
    
    @patch('sys.argv', ['komon', 'status'])
    @patch('komon.cli.subprocess.run')
    @patch('komon.cli.os.path.exists')
    @patch('komon.cli.os.getcwd')
    def test_main_status_command(self, mock_getcwd, mock_exists, mock_run):
        """statusコマンドが正しく実行される"""
        mock_getcwd.return_value = "/test/path"
        mock_exists.return_value = True
        
        main()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "status.py" in call_args[-1]
    
    @patch('sys.argv', ['komon', 'advise'])
    @patch('komon.cli.subprocess.run')
    @patch('komon.cli.os.path.exists')
    @patch('komon.cli.os.getcwd')
    def test_main_advise_command(self, mock_getcwd, mock_exists, mock_run):
        """adviseコマンドが正しく実行される"""
        mock_getcwd.return_value = "/test/path"
        mock_exists.return_value = True
        
        main()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "advise.py" in call_args[-1]
    
    @patch('sys.argv', ['komon', 'guide'])
    @patch('komon.cli.subprocess.run')
    @patch('komon.cli.os.path.exists')
    @patch('komon.cli.os.getcwd')
    def test_main_guide_command(self, mock_getcwd, mock_exists, mock_run):
        """guideコマンドが正しく実行される"""
        mock_getcwd.return_value = "/test/path"
        mock_exists.return_value = True
        
        main()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "komon_guide.py" in call_args[-1]
    
    @patch('sys.argv', ['komon', 'unknown'])
    @patch('komon.cli.os.path.exists')
    @patch('komon.cli.os.getcwd')
    def test_main_unknown_command(self, mock_getcwd, mock_exists, capsys):
        """不明なコマンドの場合、エラーメッセージが表示される"""
        mock_getcwd.return_value = "/test/path"
        mock_exists.return_value = True
        
        main()
        
        captured = capsys.readouterr()
        assert "不明なコマンド" in captured.out or "unknown" in captured.out
    
    @patch('sys.argv', ['komon', 'initial'])
    @patch('komon.cli.os.path.exists')
    @patch('komon.cli.os.getcwd')
    def test_main_scripts_dir_not_found(self, mock_getcwd, mock_exists, capsys):
        """scriptsディレクトリが見つからない場合、エラーメッセージが表示される"""
        mock_getcwd.return_value = "/test/path"
        mock_exists.return_value = False
        
        main()
        
        captured = capsys.readouterr()
        assert "scriptsディレクトリが見つかりません" in captured.out
    
    @patch('sys.argv', ['komon', 'initial'])
    @patch('komon.cli.subprocess.run')
    @patch('komon.cli.os.path.exists')
    @patch('komon.cli.os.getcwd')
    def test_main_script_file_not_found(self, mock_getcwd, mock_exists, mock_run, capsys):
        """スクリプトファイルが見つからない場合、エラーメッセージが表示される"""
        mock_getcwd.return_value = "/test/path"
        
        # scriptsディレクトリは存在するが、スクリプトファイルは存在しない
        def exists_side_effect(path):
            if "scripts" in path and not path.endswith(".py"):
                return True
            return False
        
        mock_exists.side_effect = exists_side_effect
        
        main()
        
        captured = capsys.readouterr()
        assert "スクリプトが見つかりません" in captured.out
        mock_run.assert_not_called()
    
    @patch('sys.argv', ['komon', 'initial'])
    @patch('komon.cli.subprocess.run')
    @patch('komon.cli.os.path.exists')
    @patch('komon.cli.os.getcwd')
    @patch('sys.executable', '/usr/bin/python3')
    def test_main_uses_sys_executable(self, mock_getcwd, mock_exists, mock_run):
        """sys.executableが正しく使用される"""
        mock_getcwd.return_value = "/test/path"
        mock_exists.return_value = True
        
        main()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == '/usr/bin/python3'
