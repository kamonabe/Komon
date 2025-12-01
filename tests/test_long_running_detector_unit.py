"""
長時間実行プロセス検出のユニットテスト

**Feature: long-running-detector**

このテストは、長時間実行プロセス検出機能の個別関数を検証します。
"""

import pytest
from komon.long_running_detector import (
    _extract_script_name,
    _format_duration
)


class TestExtractScriptName:
    """スクリプト名抽出のテスト"""
    
    def test_extract_script_name_python(self):
        """
        Pythonスクリプトの抽出
        
        **検証要件: AC-001**
        """
        cmdline = ['python', '/path/to/script.py', 'arg1', 'arg2']
        result = _extract_script_name(cmdline, ['.py'])
        assert result == 'script.py'
    
    def test_extract_script_name_shell(self):
        """
        シェルスクリプトの抽出
        
        **検証要件: AC-001**
        """
        cmdline = ['/bin/bash', '/path/to/script.sh']
        result = _extract_script_name(cmdline, ['.sh'])
        assert result == 'script.sh'
    
    def test_extract_script_name_no_extension(self):
        """
        拡張子なしの場合
        
        **検証要件: AC-001**
        """
        cmdline = ['python', '/path/to/script', 'arg1']
        result = _extract_script_name(cmdline, ['.py'])
        assert result is None
    
    def test_extract_script_name_module_execution(self):
        """
        モジュール実行（python -m module）の場合
        
        **検証要件: AC-001**
        """
        cmdline = ['python', '-m', 'pytest', 'tests/']
        result = _extract_script_name(cmdline, ['.py'])
        assert result is None
    
    def test_extract_script_name_empty_cmdline(self):
        """
        空のコマンドラインの場合
        
        **検証要件: AC-001**
        """
        cmdline = []
        result = _extract_script_name(cmdline, ['.py'])
        assert result is None


class TestFormatDuration:
    """時間フォーマットのテスト"""
    
    def test_format_duration_seconds(self):
        """
        秒のみの場合
        
        **検証要件: AC-003**
        """
        assert _format_duration(0) == '0秒'
        assert _format_duration(30) == '30秒'
        assert _format_duration(59) == '59秒'
    
    def test_format_duration_minutes(self):
        """
        分の場合
        
        **検証要件: AC-003**
        """
        assert _format_duration(60) == '1分'
        assert _format_duration(90) == '1分30秒'
        assert _format_duration(3599) == '59分59秒'
    
    def test_format_duration_hours(self):
        """
        時間の場合
        
        **検証要件: AC-003**
        """
        assert _format_duration(3600) == '1時間'
        assert _format_duration(3660) == '1時間1分'
        assert _format_duration(7200) == '2時間'
        assert _format_duration(7380) == '2時間3分'
    
    def test_format_duration_days(self):
        """
        日の場合
        
        **検証要件: AC-003**
        """
        assert _format_duration(86400) == '1日'
        assert _format_duration(90000) == '1日1時間'
        assert _format_duration(90060) == '1日1時間1分'
        assert _format_duration(172800) == '2日'
    
    def test_format_duration_zero(self):
        """
        0秒の場合
        
        **検証要件: AC-003**
        """
        assert _format_duration(0) == '0秒'
    
    def test_format_duration_negative(self):
        """
        負の値の場合
        
        **検証要件: AC-003**
        """
        assert _format_duration(-100) == '0秒'
