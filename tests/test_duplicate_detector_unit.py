"""
多重実行プロセス検出モジュールのユニットテスト
"""

import pytest
from unittest.mock import MagicMock, patch
from komon.duplicate_detector import detect_duplicate_processes, _extract_script_name


class TestDetectDuplicateProcesses:
    """detect_duplicate_processes()のテスト"""
    
    def test_detect_duplicate_processes_normal(self):
        """
        正常系: 多重実行プロセスが検出される
        
        **検証要件: AC-001**
        """
        # モックプロセスを作成
        mock_processes = [
            {'pid': 1001, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1002, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1003, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1004, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 2001, 'cmdline': ['/bin/bash', '/path/to/sync.sh']},
            {'pid': 2002, 'cmdline': ['/bin/bash', '/path/to/sync.sh']},
            {'pid': 2003, 'cmdline': ['/bin/bash', '/path/to/sync.sh']},
        ]
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            result = detect_duplicate_processes(threshold=3)
        
        # 検証
        assert len(result) == 2
        
        # backup.py
        backup = next(r for r in result if r['script'] == 'backup.py')
        assert backup['count'] == 4
        assert backup['pids'] == [1001, 1002, 1003, 1004]
        
        # sync.sh
        sync = next(r for r in result if r['script'] == 'sync.sh')
        assert sync['count'] == 3
        assert sync['pids'] == [2001, 2002, 2003]
    
    def test_detect_duplicate_processes_no_duplicates(self):
        """
        正常系: 多重実行プロセスがない場合
        
        **検証要件: AC-001**
        """
        mock_processes = [
            {'pid': 1001, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 2001, 'cmdline': ['/bin/bash', '/path/to/sync.sh']},
        ]
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            result = detect_duplicate_processes(threshold=3)
        
        # 検証: 閾値未満なので空リスト
        assert result == []
    
    def test_detect_duplicate_processes_threshold(self):
        """
        閾値判定のテスト
        
        **検証要件: AC-002**
        """
        mock_processes = [
            {'pid': 1001, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1002, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1003, 'cmdline': ['python', '/path/to/backup.py']},
        ]
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            # 閾値3: 3個なので検出される
            result = detect_duplicate_processes(threshold=3)
            assert len(result) == 1
            assert result[0]['count'] == 3
            
            # 閾値4: 3個なので検出されない
            result = detect_duplicate_processes(threshold=4)
            assert result == []
    
    def test_detect_duplicate_processes_invalid_threshold(self):
        """
        不正な閾値の場合、デフォルト値（3）を使用
        
        **検証要件: AC-002**
        """
        mock_processes = [
            {'pid': 1001, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1002, 'cmdline': ['python', '/path/to/backup.py']},
            {'pid': 1003, 'cmdline': ['python', '/path/to/backup.py']},
        ]
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            # 不正な閾値（0以下）
            result = detect_duplicate_processes(threshold=0)
            assert len(result) == 1  # デフォルト値3で検出
            
            # 不正な閾値（文字列）
            result = detect_duplicate_processes(threshold="invalid")
            assert len(result) == 1  # デフォルト値3で検出
    
    def test_detect_duplicate_processes_error_handling(self):
        """
        エラーハンドリング: プロセス走査中のエラー
        
        **検証要件: AC-005**
        """
        with patch('psutil.process_iter') as mock_iter:
            # プロセス走査でエラー発生
            mock_iter.side_effect = Exception("Process iteration failed")
            
            result = detect_duplicate_processes()
        
        # 検証: エラー時は空リストを返す
        assert result == []


class TestExtractScriptName:
    """_extract_script_name()のテスト"""
    
    def test_extract_script_name_python(self):
        """
        Pythonスクリプトの抽出
        
        **検証要件: AC-001**
        """
        cmdline = ['python', '/path/to/script.py', 'arg1', 'arg2']
        result = _extract_script_name(cmdline)
        assert result == 'script.py'
    
    def test_extract_script_name_python3(self):
        """
        Python3スクリプトの抽出
        
        **検証要件: AC-001**
        """
        cmdline = ['python3', '/home/user/backup.py']
        result = _extract_script_name(cmdline)
        assert result == 'backup.py'
    
    def test_extract_script_name_shell(self):
        """
        シェルスクリプトの抽出
        
        **検証要件: AC-001**
        """
        cmdline = ['/bin/bash', '/path/to/sync.sh']
        result = _extract_script_name(cmdline)
        assert result == 'sync.sh'
    
    def test_extract_script_name_ruby(self):
        """
        Rubyスクリプトの抽出
        
        **検証要件: AC-001**
        """
        cmdline = ['ruby', '/path/to/script.rb']
        result = _extract_script_name(cmdline)
        assert result == 'script.rb'
    
    def test_extract_script_name_perl(self):
        """
        Perlスクリプトの抽出
        
        **検証要件: AC-001**
        """
        cmdline = ['perl', '/path/to/script.pl']
        result = _extract_script_name(cmdline)
        assert result == 'script.pl'
    
    def test_extract_script_name_no_script(self):
        """
        スクリプトがない場合
        
        **検証要件: AC-001**
        """
        cmdline = ['ls', '-la', '/tmp']
        result = _extract_script_name(cmdline)
        assert result is None
    
    def test_extract_script_name_module_execution(self):
        """
        モジュール実行（python -m module）は対象外
        
        **検証要件: AC-001**
        """
        cmdline = ['python', '-m', 'http.server', '8000']
        result = _extract_script_name(cmdline)
        assert result is None
    
    def test_extract_script_name_empty_cmdline(self):
        """
        空のコマンドライン
        
        **検証要件: AC-001**
        """
        result = _extract_script_name([])
        assert result is None
    
    def test_extract_script_name_none_cmdline(self):
        """
        Noneのコマンドライン
        
        **検証要件: AC-001**
        """
        result = _extract_script_name(None)
        assert result is None
    
    def test_extract_script_name_unsupported_extension(self):
        """
        対象外の拡張子
        
        **検証要件: AC-001**
        """
        cmdline = ['java', '-jar', '/path/to/app.jar']
        result = _extract_script_name(cmdline)
        assert result is None
