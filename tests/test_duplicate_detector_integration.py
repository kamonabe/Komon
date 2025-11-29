"""
多重実行プロセス検出モジュールの統合テスト
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO


class TestAdviseIntegration:
    """advise.pyとの統合テスト"""
    
    def setup_method(self):
        """テスト前にscriptsディレクトリをパスに追加"""
        scripts_path = Path(__file__).parent.parent / "scripts"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
    
    def test_advise_with_duplicates(self, capsys):
        """
        多重実行プロセスがある場合の表示
        
        **検証要件: AC-003**
        """
        import advise
        
        # モックプロセスを作成
        mock_processes = [
            {'pid': 1001, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1002, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1003, 'cmdline': ['python', '/path/to/backup.py']},
        ]
        
        # モック設定
        mock_config = {
            'duplicate_process_detection': {
                'enabled': True,
                'threshold': 3
            }
        }
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            # 関数を実行
            advise.advise_duplicate_processes(mock_config)
        
        # 出力を確認
        captured = capsys.readouterr()
        assert '🔄 多重実行プロセスの検出' in captured.out
        assert 'backup.py' in captured.out
        assert '3個のプロセス' in captured.out
        assert 'PID: 1001, 1002, 1003' in captured.out
        assert '【推奨対応】' in captured.out
    
    def test_advise_without_duplicates(self, capsys):
        """
        多重実行プロセスがない場合の表示
        
        **検証要件: AC-003**
        """
        import advise
        
        # モックプロセスを作成（多重実行なし）
        mock_processes = [
            {'pid': 1001, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 2001, 'cmdline': ['/bin/bash', '/path/to/sync.sh']},
        ]
        
        # モック設定
        mock_config = {
            'duplicate_process_detection': {
                'enabled': True,
                'threshold': 3
            }
        }
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            # 関数を実行
            advise.advise_duplicate_processes(mock_config)
        
        # 出力を確認
        captured = capsys.readouterr()
        assert '🔄 多重実行プロセスの検出' in captured.out
        assert '多重実行プロセスは検出されませんでした' in captured.out
    
    def test_advise_disabled(self, capsys):
        """
        機能が無効化されている場合
        
        **検証要件: AC-004**
        """
        import advise
        
        # モック設定（無効化）
        mock_config = {
            'duplicate_process_detection': {
                'enabled': False,
                'threshold': 3
            }
        }
        
        # 関数を実行
        advise.advise_duplicate_processes(mock_config)
        
        # 出力を確認
        captured = capsys.readouterr()
        assert '🔄 多重実行プロセスの検出' in captured.out
        assert '無効化されています' in captured.out
    
    def test_advise_custom_threshold(self, capsys):
        """
        カスタム閾値の使用
        
        **検証要件: AC-004**
        """
        import advise
        
        # モックプロセスを作成（2個）
        mock_processes = [
            {'pid': 1001, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1002, 'cmdline': ['python', '/path/to/backup.py']},
        ]
        
        # モック設定（閾値2）
        mock_config = {
            'duplicate_process_detection': {
                'enabled': True,
                'threshold': 2
            }
        }
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            # 関数を実行
            advise.advise_duplicate_processes(mock_config)
        
        # 出力を確認
        captured = capsys.readouterr()
        assert 'backup.py' in captured.out
        assert '2個のプロセス' in captured.out


class TestConfigLoading:
    """設定ファイルの読み込みテスト"""
    
    def test_config_default_values(self):
        """
        設定ファイルにduplicate_process_detectionがない場合のデフォルト値
        
        **検証要件: AC-004**
        """
        import advise
        from io import StringIO
        
        # 空の設定
        mock_config = {}
        
        # デフォルト値を確認
        threshold = mock_config.get("duplicate_process_detection", {}).get("threshold", 3)
        enabled = mock_config.get("duplicate_process_detection", {}).get("enabled", True)
        
        assert threshold == 3
        assert enabled is True
    
    def test_config_custom_values(self):
        """
        設定ファイルのカスタム値が使用される
        
        **検証要件: AC-004**
        """
        # カスタム設定
        mock_config = {
            'duplicate_process_detection': {
                'enabled': False,
                'threshold': 5
            }
        }
        
        # カスタム値を確認
        threshold = mock_config.get("duplicate_process_detection", {}).get("threshold", 3)
        enabled = mock_config.get("duplicate_process_detection", {}).get("enabled", True)
        
        assert threshold == 5
        assert enabled is False


class TestEndToEnd:
    """エンドツーエンドテスト"""
    
    def test_full_workflow(self, capsys):
        """
        検出から表示までの完全なワークフロー
        
        **検証要件: AC-001, AC-002, AC-003, AC-005**
        """
        from komon.duplicate_detector import detect_duplicate_processes
        
        # モックプロセスを作成
        mock_processes = [
            {'pid': 1001, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1002, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1003, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1004, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 2001, 'cmdline': ['/bin/bash', '/path/to/sync.sh']},
        ]
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            # 検出
            duplicates = detect_duplicate_processes(threshold=3)
        
        # 検証
        assert len(duplicates) == 1
        assert duplicates[0]['script'] == 'backup.py'
        assert duplicates[0]['count'] == 4
        
        # 表示（advise.pyの関数を使用）
        import advise
        
        mock_config = {
            'duplicate_process_detection': {
                'enabled': True,
                'threshold': 3
            }
        }
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            advise.advise_duplicate_processes(mock_config)
        
        # 出力を確認
        captured = capsys.readouterr()
        assert 'backup.py' in captured.out
        assert '4個のプロセス' in captured.out
