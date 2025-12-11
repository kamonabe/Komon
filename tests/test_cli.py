"""
cli.py のテスト

CLIエントリーポイントのテストを行います。
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from komon.cli import main


class TestMain:
    """main関数のテスト"""
    
    @patch('sys.argv', ['komon'])
    def test_main_no_arguments(self, capsys):
        """引数なしで実行した場合、ヘルプが表示される"""
        main()
        
        captured = capsys.readouterr()
        assert "usage:" in captured.out
        assert "komon" in captured.out
    
    @patch('sys.argv', ['komon', 'initial'])
    @patch('komon.commands.initial.run_initial_setup')
    @patch('komon.cli.ensure_config_dir')
    def test_main_initial_command(self, mock_ensure_config_dir, mock_run_initial):
        """initialコマンドが正しく実行される"""
        from pathlib import Path
        mock_ensure_config_dir.return_value = Path("/test/config")
        
        main()
        
        mock_run_initial.assert_called_once_with(Path("/test/config"))
    
    @patch('sys.argv', ['komon', 'status'])
    @patch('komon.commands.status.run_status')
    @patch('komon.cli.ensure_config_dir')
    def test_main_status_command(self, mock_ensure_config_dir, mock_run_status):
        """statusコマンドが正しく実行される"""
        from pathlib import Path
        mock_ensure_config_dir.return_value = Path("/test/config")
        
        main()
        
        mock_run_status.assert_called_once_with(Path("/test/config"))
    
    @patch('sys.argv', ['komon', 'advise'])
    @patch('komon.commands.advise.run_advise')
    @patch('komon.cli.ensure_config_dir')
    def test_main_advise_command(self, mock_ensure_config_dir, mock_run_advise):
        """adviseコマンドが正しく実行される"""
        from pathlib import Path
        mock_ensure_config_dir.return_value = Path("/test/config")
        
        main()
        
        mock_run_advise.assert_called_once_with(
            config_dir=Path("/test/config"),
            history_limit=None,
            verbose=False,
            section=None,
            net_mode=None
        )
    
    @patch('sys.argv', ['komon', 'advise', '--history', '5'])
    @patch('komon.commands.advise.run_advise')
    @patch('komon.cli.ensure_config_dir')
    def test_main_advise_command_with_history(self, mock_ensure_config_dir, mock_run_advise):
        """adviseコマンドが履歴オプション付きで正しく実行される"""
        from pathlib import Path
        mock_ensure_config_dir.return_value = Path("/test/config")
        
        main()
        
        mock_run_advise.assert_called_once_with(
            config_dir=Path("/test/config"),
            history_limit=5,
            verbose=False,
            section=None,
            net_mode=None
        )
    
    @patch('sys.argv', ['komon', 'guide'])
    @patch('komon.commands.guide.run_guide')
    @patch('komon.cli.ensure_config_dir')
    def test_main_guide_command(self, mock_ensure_config_dir, mock_run_guide):
        """guideコマンドが正しく実行される"""
        from pathlib import Path
        mock_ensure_config_dir.return_value = Path("/test/config")
        
        main()
        
        mock_run_guide.assert_called_once_with(Path("/test/config"))
    
    @patch('sys.argv', ['komon', 'unknown'])
    def test_main_unknown_command(self, capsys):
        """不明なコマンドの場合、エラーメッセージが表示される"""
        with pytest.raises(SystemExit):
            main()
        
        captured = capsys.readouterr()
        assert "invalid choice" in captured.err
        assert "unknown" in captured.err
    
    @patch('sys.argv', ['komon', '--version'])
    def test_main_version_command(self, capsys):
        """--versionオプションでバージョンが表示される"""
        with pytest.raises(SystemExit):
            main()
        
        captured = capsys.readouterr()
        assert "1.25.5" in captured.out


class TestConfigDir:
    """設定ディレクトリ関連のテスト"""
    
    @patch.dict('os.environ', {'KOMON_CONFIG_DIR': '/custom/config'})
    def test_get_config_dir_env_var(self):
        """環境変数KOMON_CONFIG_DIRが設定されている場合"""
        from komon.cli import get_config_dir
        from pathlib import Path
        
        result = get_config_dir()
        
        assert result == Path("/custom/config")
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_config_dir_current_dir(self):
        """カレントディレクトリにsettings.ymlがある場合"""
        from komon.cli import get_config_dir
        from pathlib import Path
        
        with patch('pathlib.Path.cwd') as mock_cwd, \
             patch('pathlib.Path.exists') as mock_exists:
            
            mock_cwd.return_value = Path("/current/dir")
            mock_exists.return_value = True  # settings.ymlが存在する
            
            result = get_config_dir()
            
            assert result == Path("/current/dir")
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('pathlib.Path.cwd')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.home')
    def test_get_config_dir_home_dir(self, mock_home, mock_exists, mock_cwd):
        """ホームディレクトリの.komonを使用する場合"""
        from komon.cli import get_config_dir
        from pathlib import Path
        
        mock_cwd.return_value = Path("/current/dir")
        mock_home.return_value = Path("/home/user")
        mock_exists.return_value = False  # settings.ymlが存在しない
        
        result = get_config_dir()
        
        assert result == Path("/home/user/.komon")
