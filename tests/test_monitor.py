"""
monitor.py のテスト

リソース監視機能のテストを行います。
"""

import pytest
import psutil
from unittest.mock import patch, MagicMock
from komon.monitor import collect_resource_usage, collect_detailed_resource_usage


class TestCollectResourceUsage:
    """collect_resource_usage関数のテスト"""
    
    @patch('komon.monitor.psutil')
    def test_collect_basic_usage(self, mock_psutil):
        """基本的なリソース使用率の収集"""
        # モックの設定
        mock_psutil.cpu_percent.return_value = 45.5
        mock_psutil.virtual_memory.return_value = MagicMock(percent=60.2)
        mock_psutil.disk_usage.return_value = MagicMock(percent=75.8)
        
        result = collect_resource_usage()
        
        assert result["cpu"] == 45.5
        assert result["mem"] == 60.2
        assert result["disk"] == 75.8
        mock_psutil.cpu_percent.assert_called_once_with(interval=1)
    
    @patch('komon.monitor.psutil')
    def test_collect_usage_returns_dict(self, mock_psutil):
        """戻り値が辞書型であることを確認"""
        mock_psutil.cpu_percent.return_value = 10.0
        mock_psutil.virtual_memory.return_value = MagicMock(percent=20.0)
        mock_psutil.disk_usage.return_value = MagicMock(percent=30.0)
        
        result = collect_resource_usage()
        
        assert isinstance(result, dict)
        assert "cpu" in result
        assert "mem" in result
        assert "disk" in result


class TestCollectDetailedResourceUsage:
    """collect_detailed_resource_usage関数のテスト"""
    
    @patch('komon.monitor.psutil')
    def test_collect_with_process_info(self, mock_psutil):
        """プロセス情報を含む詳細な使用率の収集"""
        # 基本使用率のモック
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = MagicMock(percent=60.0)
        mock_psutil.disk_usage.return_value = MagicMock(percent=70.0)
        
        # プロセス情報のモック
        mock_proc1 = MagicMock()
        mock_proc1.info = {'name': 'python', 'cpu_percent': 25.5, 'memory_info': MagicMock(rss=100*1024*1024)}
        
        mock_proc2 = MagicMock()
        mock_proc2.info = {'name': 'chrome', 'cpu_percent': 15.2, 'memory_info': MagicMock(rss=200*1024*1024)}
        
        mock_psutil.process_iter.return_value = [mock_proc1, mock_proc2]
        
        result = collect_detailed_resource_usage()
        
        assert "cpu" in result
        assert "mem" in result
        assert "disk" in result
        assert "cpu_by_process" in result
        assert "mem_by_process" in result
        assert len(result["cpu_by_process"]) <= 5
        assert len(result["mem_by_process"]) <= 5
    
    @patch('komon.monitor.psutil')
    def test_process_sorting_by_cpu(self, mock_psutil):
        """CPU使用率でプロセスがソートされることを確認"""
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = MagicMock(percent=60.0)
        mock_psutil.disk_usage.return_value = MagicMock(percent=70.0)
        
        # CPU使用率が異なる3つのプロセス
        procs = []
        for name, cpu in [('low', 5.0), ('high', 30.0), ('mid', 15.0)]:
            mock_proc = MagicMock()
            mock_proc.info = {
                'name': name,
                'cpu_percent': cpu,
                'memory_info': MagicMock(rss=100*1024*1024)
            }
            procs.append(mock_proc)
        
        mock_psutil.process_iter.return_value = procs
        
        result = collect_detailed_resource_usage()
        
        # CPU使用率の降順でソートされているか確認
        cpu_procs = result["cpu_by_process"]
        assert cpu_procs[0]['name'] == 'high'
        assert cpu_procs[1]['name'] == 'mid'
        assert cpu_procs[2]['name'] == 'low'
    
    @patch('komon.monitor.psutil')
    def test_handle_empty_process_list(self, mock_psutil):
        """プロセスリストが空の場合のハンドリング"""
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = MagicMock(percent=60.0)
        mock_psutil.disk_usage.return_value = MagicMock(percent=70.0)
        
        # プロセスが存在しない場合
        mock_psutil.process_iter.return_value = []
        
        # エラーが発生せず、空のリストが返されることを確認
        result = collect_detailed_resource_usage()
        assert "cpu_by_process" in result
        assert "mem_by_process" in result
        assert result["cpu_by_process"] == []
        assert result["mem_by_process"] == []
    
    @patch('komon.monitor.psutil.cpu_percent')
    @patch('komon.monitor.psutil.virtual_memory')
    @patch('komon.monitor.psutil.disk_usage')
    @patch('komon.monitor.psutil.process_iter')
    def test_handle_process_access_denied_exception(self, mock_process_iter, mock_disk, mock_mem, mock_cpu):
        """プロセスアクセス拒否例外が適切に処理される"""
        mock_cpu.return_value = 50.0
        mock_mem.return_value = MagicMock(percent=60.0)
        mock_disk.return_value = MagicMock(percent=70.0)
        
        # process_iterが2回呼ばれる（CPU用とメモリ用）ので、それぞれに対応
        def mock_process_iter_func(attrs):
            # 正常なプロセス
            mock_proc_ok = MagicMock()
            if 'cpu_percent' in attrs:
                mock_proc_ok.info = {'name': 'python', 'cpu_percent': 25.5, 'pid': 100}
            else:
                mock_proc_ok.info = {'name': 'python', 'memory_info': MagicMock(rss=100*1024*1024), 'pid': 100}
            
            # AccessDenied例外を発生させるプロセス
            mock_proc_denied = MagicMock()
            mock_proc_denied.info = MagicMock()
            mock_proc_denied.info.__getitem__ = MagicMock(side_effect=psutil.AccessDenied("Access denied"))
            
            return [mock_proc_ok, mock_proc_denied]
        
        mock_process_iter.side_effect = mock_process_iter_func
        
        # 例外が発生しても処理が継続し、正常なプロセスは取得できる
        result = collect_detailed_resource_usage()
        assert "cpu_by_process" in result
        assert "mem_by_process" in result
        assert len(result["cpu_by_process"]) >= 1
        assert result["cpu_by_process"][0]['name'] == 'python'
    
    @patch('komon.monitor.psutil.cpu_percent')
    @patch('komon.monitor.psutil.virtual_memory')
    @patch('komon.monitor.psutil.disk_usage')
    @patch('komon.monitor.psutil.process_iter')
    def test_handle_process_no_such_process_exception(self, mock_process_iter, mock_disk, mock_mem, mock_cpu):
        """プロセスが消えた場合の例外が適切に処理される"""
        mock_cpu.return_value = 50.0
        mock_mem.return_value = MagicMock(percent=60.0)
        mock_disk.return_value = MagicMock(percent=70.0)
        
        # process_iterが2回呼ばれる（CPU用とメモリ用）ので、それぞれに対応
        def mock_process_iter_func(attrs):
            # 正常なプロセス
            mock_proc_ok = MagicMock()
            if 'cpu_percent' in attrs:
                mock_proc_ok.info = {'name': 'chrome', 'cpu_percent': 15.2, 'pid': 200}
            else:
                mock_proc_ok.info = {'name': 'chrome', 'memory_info': MagicMock(rss=200*1024*1024), 'pid': 200}
            
            # NoSuchProcess例外を発生させるプロセス
            mock_proc_gone = MagicMock()
            mock_proc_gone.info = MagicMock()
            mock_proc_gone.info.__getitem__ = MagicMock(side_effect=psutil.NoSuchProcess(pid=999))
            
            return [mock_proc_ok, mock_proc_gone]
        
        mock_process_iter.side_effect = mock_process_iter_func
        
        # 例外が発生しても処理が継続し、正常なプロセスは取得できる
        result = collect_detailed_resource_usage()
        assert "cpu_by_process" in result
        assert "mem_by_process" in result
        assert len(result["cpu_by_process"]) >= 1
        assert result["cpu_by_process"][0]['name'] == 'chrome'
