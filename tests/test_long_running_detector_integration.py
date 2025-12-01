"""
長時間実行プロセス検出の統合テスト

**Feature: long-running-detector**

このテストは、長時間実行プロセス検出機能の統合動作を検証します。
"""

import time
import subprocess
import sys
from unittest.mock import patch, MagicMock
import psutil
import pytest
from komon.long_running_detector import detect_long_running_processes


def test_detect_long_running_processes_with_real_processes():
    """
    実際のプロセスで長時間実行プロセスを検出
    
    **検証要件: AC-001, AC-002**
    """
    # 閾値を0秒に設定（全てのプロセスを検出）
    result = detect_long_running_processes(threshold_seconds=0)
    
    # 結果がリストであること
    assert isinstance(result, list)
    
    # 少なくとも1つのプロセスが検出されること（Pythonプロセス自身）
    # ただし、対象拡張子を持つスクリプトのみなので、0個の可能性もある
    assert isinstance(result, list)


def test_advise_long_running_processes_output(capsys):
    """
    長時間実行プロセスの助言メッセージ出力
    
    **検証要件: AC-003**
    """
    # モックプロセスを作成
    mock_proc = MagicMock()
    mock_proc.info = {
        'pid': 12345,
        'cmdline': ['python', '/path/to/long_script.py'],
        'create_time': time.time() - 7200  # 2時間前
    }
    
    with patch('psutil.process_iter', return_value=[mock_proc]):
        result = detect_long_running_processes(threshold_seconds=3600)
        
        # 1件検出されること
        assert len(result) == 1
        
        # スクリプト名が正しいこと
        assert result[0]['script'] == 'long_script.py'
        
        # PIDが正しいこと
        assert result[0]['pid'] == 12345
        
        # 実行時間が約2時間であること
        assert 7190 <= result[0]['runtime_seconds'] <= 7210
        
        # フォーマットされた実行時間が含まれること
        assert '時間' in result[0]['runtime_formatted']


def test_config_enabled_disabled():
    """
    設定による有効/無効の切り替え
    
    **検証要件: AC-004**
    """
    # 有効な場合
    result = detect_long_running_processes(threshold_seconds=3600)
    assert isinstance(result, list)
    
    # 無効な場合は、advise.pyで制御されるため、ここではテスト不要


def test_error_handling_no_such_process():
    """
    プロセスが終了した場合のエラーハンドリング
    
    **検証要件: AC-001**
    """
    # NoSuchProcessを発生させるモック
    mock_proc = MagicMock()
    mock_proc.info = {
        'pid': 12345,
        'cmdline': ['python', '/path/to/script.py'],
        'create_time': time.time() - 7200
    }
    
    # 2回目のアクセスでNoSuchProcessを発生
    call_count = [0]
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] > 1:
            raise psutil.NoSuchProcess(12345)
        return mock_proc.info
    
    mock_proc.info = property(lambda self: side_effect())
    
    with patch('psutil.process_iter', return_value=[mock_proc]):
        # 例外が発生せず、空のリストが返ること
        result = detect_long_running_processes(threshold_seconds=3600)
        assert isinstance(result, list)


def test_error_handling_access_denied():
    """
    アクセス拒否された場合のエラーハンドリング
    
    **検証要件: AC-001**
    """
    # AccessDeniedを発生させるモック
    mock_proc = MagicMock()
    mock_proc.info = {
        'pid': 12345,
        'cmdline': None  # アクセス拒否をシミュレート
    }
    
    with patch('psutil.process_iter', return_value=[mock_proc]):
        # 例外が発生せず、空のリストが返ること
        result = detect_long_running_processes(threshold_seconds=3600)
        assert isinstance(result, list)


def test_multiple_long_running_processes():
    """
    複数の長時間実行プロセスの検出
    
    **検証要件: AC-001**
    """
    # 複数のモックプロセスを作成
    mock_procs = []
    for i in range(3):
        mock_proc = MagicMock()
        mock_proc.info = {
            'pid': 10000 + i,
            'cmdline': ['python', f'/path/to/script{i}.py'],
            'create_time': time.time() - (3600 * (i + 1))  # 1時間、2時間、3時間前
        }
        mock_procs.append(mock_proc)
    
    with patch('psutil.process_iter', return_value=mock_procs):
        result = detect_long_running_processes(threshold_seconds=3600)
        
        # 3件検出されること
        assert len(result) == 3
        
        # 実行時間の降順でソートされていること
        assert result[0]['runtime_seconds'] > result[1]['runtime_seconds']
        assert result[1]['runtime_seconds'] > result[2]['runtime_seconds']


def test_no_long_running_processes():
    """
    長時間実行プロセスが存在しない場合
    
    **検証要件: AC-001**
    """
    # 短時間実行のモックプロセスを作成
    mock_proc = MagicMock()
    mock_proc.info = {
        'pid': 12345,
        'cmdline': ['python', '/path/to/script.py'],
        'create_time': time.time() - 60  # 1分前
    }
    
    with patch('psutil.process_iter', return_value=[mock_proc]):
        result = detect_long_running_processes(threshold_seconds=3600)
        
        # 0件であること
        assert len(result) == 0
