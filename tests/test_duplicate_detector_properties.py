"""
多重実行プロセス検出モジュールのプロパティテスト
"""

import pytest
from hypothesis import given, strategies as st, assume
from unittest.mock import patch, MagicMock
from komon.duplicate_detector import detect_duplicate_processes, _extract_script_name


class TestPropertyCountAccuracy:
    """
    **Feature: duplicate-process-detection, Property 1: プロセスカウントの正確性**
    
    任意のプロセスリストについて、同一スクリプトのプロセス数は実際の実行数と一致すること
    
    **検証要件: AC-001**
    """
    
    @given(
        st.lists(
            st.tuples(
                st.integers(min_value=1000, max_value=9999),  # PID
                st.sampled_from(['backup.py', 'sync.sh', 'test.rb', 'script.pl'])  # スクリプト名
            ),
            min_size=1,
            max_size=20
        )
    )
    def test_property_count_accuracy(self, process_list):
        """
        任意のプロセスリストに対して、カウント結果が正確であること
        """
        # プロセスリストから期待値を計算
        expected_counts = {}
        for pid, script in process_list:
            if script not in expected_counts:
                expected_counts[script] = []
            expected_counts[script].append(pid)
        
        # モックプロセスを作成
        mock_processes = [
            {'pid': pid, 'cmdline': ['python', f'/path/to/{script}']}
            for pid, script in process_list
        ]
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            # 閾値1で全て検出
            result = detect_duplicate_processes(threshold=1)
        
        # 検証: カウント数が一致
        for dup in result:
            script = dup['script']
            assert dup['count'] == len(expected_counts[script])
            assert sorted(dup['pids']) == sorted(expected_counts[script])


class TestPropertyThresholdAccuracy:
    """
    **Feature: duplicate-process-detection, Property 2: 閾値判定の正確性**
    
    任意の閾値Tとプロセス数Nについて、N >= Tの場合のみ警告対象となること
    
    **検証要件: AC-002**
    """
    
    @given(
        threshold=st.integers(min_value=1, max_value=10),
        process_count=st.integers(min_value=1, max_value=15)
    )
    def test_property_threshold_accuracy(self, threshold, process_count):
        """
        任意の閾値とプロセス数に対して、閾値判定が正確であること
        """
        # モックプロセスを作成
        mock_processes = [
            {'pid': 1000 + i, 'cmdline': ['python', '/path/to/test.py']}
            for i in range(process_count)
        ]
        
        with patch('psutil.process_iter') as mock_iter:
            mock_iter.return_value = [
                MagicMock(info=proc) for proc in mock_processes
            ]
            
            result = detect_duplicate_processes(threshold=threshold)
        
        # 検証: 閾値判定が正確
        if process_count >= threshold:
            assert len(result) == 1
            assert result[0]['count'] == process_count
        else:
            assert len(result) == 0


class TestPropertyScriptExtractionAccuracy:
    """
    **Feature: duplicate-process-detection, Property 3: スクリプト名抽出の正確性**
    
    任意のコマンドライン形式について、対象拡張子(.py, .sh等)を持つスクリプト名が正しく抽出されること
    
    **検証要件: AC-001**
    """
    
    @given(
        script_name=st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd')),
            min_size=1,
            max_size=20
        ),
        extension=st.sampled_from(['.py', '.sh', '.rb', '.pl'])
    )
    def test_property_script_extraction_accuracy(self, script_name, extension):
        """
        任意のスクリプト名と拡張子に対して、正しく抽出されること
        """
        # 不正な文字を除外
        assume(script_name.isalnum())
        
        full_script = f"{script_name}{extension}"
        cmdline = ['python', f'/path/to/{full_script}', 'arg1']
        
        result = _extract_script_name(cmdline)
        
        # 検証: スクリプト名が正しく抽出される
        assert result == full_script
    
    @given(
        cmdline=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd')),
                min_size=1,
                max_size=10
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_property_no_script_returns_none(self, cmdline):
        """
        対象拡張子を持たないコマンドラインはNoneを返すこと
        """
        # 対象拡張子を含まないことを確認
        target_extensions = ('.py', '.sh', '.rb', '.pl')
        assume(not any(arg.endswith(ext) for arg in cmdline for ext in target_extensions))
        
        result = _extract_script_name(cmdline)
        
        # 検証: Noneが返される
        assert result is None
    
    @given(
        st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd')),
                min_size=1,
                max_size=10
            ),
            min_size=2,
            max_size=5
        )
    )
    def test_property_module_execution_returns_none(self, cmdline):
        """
        モジュール実行（-mオプション）はNoneを返すこと
        """
        # -mオプションを含むコマンドラインを作成
        cmdline_with_m = cmdline[:1] + ['-m'] + cmdline[1:]
        
        result = _extract_script_name(cmdline_with_m)
        
        # 検証: Noneが返される
        assert result is None
