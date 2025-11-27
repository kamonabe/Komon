"""
contextual_advisor.py のユニットテスト

個別関数の正常系・異常系・エッジケースを検証する
"""

import pytest
from unittest.mock import MagicMock, patch
from src.komon.contextual_advisor import (
    get_contextual_advice,
    _get_top_processes,
    _match_pattern,
    _format_advice,
    DEFAULT_PATTERNS
)


class TestGetTopProcesses:
    """_get_top_processes()のテスト"""
    
    def test_get_top_processes_cpu(self):
        """
        CPU使用率で上位プロセスを取得
        
        **検証要件: AC-001**
        """
        processes = _get_top_processes("cpu", 3)
        
        assert isinstance(processes, list)
        assert len(processes) <= 3
        
        # 各プロセスが必要なフィールドを持つ
        for proc in processes:
            assert "name" in proc
            assert "pid" in proc
            assert "cpu_percent" in proc
            assert "memory_percent" in proc
            assert "cmdline" in proc
    
    def test_get_top_processes_memory(self):
        """
        メモリ使用率で上位プロセスを取得
        
        **検証要件: AC-001**
        """
        processes = _get_top_processes("memory", 3)
        
        assert isinstance(processes, list)
        assert len(processes) <= 3
        
        # メモリ使用率で降順にソートされている
        for i in range(len(processes) - 1):
            assert processes[i]["memory_percent"] >= processes[i + 1]["memory_percent"]
    
    def test_get_top_processes_empty(self):
        """
        プロセスが0件の場合（モック使用）
        
        **検証要件: AC-001**
        """
        with patch('src.komon.contextual_advisor.psutil.process_iter', return_value=[]):
            processes = _get_top_processes("cpu", 3)
            assert processes == []
    
    def test_get_top_processes_less_than_count(self):
        """
        プロセス数がcount未満の場合
        
        **検証要件: AC-001**
        """
        # 実際のプロセス数に依存するため、countを大きくする
        processes = _get_top_processes("cpu", 1000)
        
        # 取得できた分だけ返される
        assert isinstance(processes, list)
        assert len(processes) <= 1000
    
    def test_get_top_processes_error_handling(self):
        """
        エラーハンドリング（プロセスが途中で終了）
        
        **検証要件: AC-001**
        """
        import psutil
        
        # プロセスが途中で終了する場合をシミュレート
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'test',
            'pid': 12345,
            'memory_percent': 10.0,
            'cmdline': ['test']
        }
        mock_proc.cpu_percent.side_effect = psutil.NoSuchProcess(12345)
        
        with patch('src.komon.contextual_advisor.psutil.process_iter', return_value=[mock_proc]):
            processes = _get_top_processes("cpu", 3)
            # エラーが発生してもクラッシュしない
            assert isinstance(processes, list)


class TestMatchPattern:
    """_match_pattern()のテスト"""
    
    def test_match_pattern_node(self):
        """
        nodeパターンのマッチング
        
        **検証要件: AC-002**
        """
        pattern_name, advice = _match_pattern("node", DEFAULT_PATTERNS)
        
        assert pattern_name == "node"
        assert "開発サーバー" in advice
    
    def test_match_pattern_docker(self):
        """
        dockerパターンのマッチング
        
        **検証要件: AC-002**
        """
        pattern_name, advice = _match_pattern("docker", DEFAULT_PATTERNS)
        
        assert pattern_name == "docker"
        assert "コンテナ" in advice
    
    def test_match_pattern_python(self):
        """
        pythonパターンのマッチング
        
        **検証要件: AC-002**
        """
        pattern_name, advice = _match_pattern("python3", DEFAULT_PATTERNS)
        
        assert pattern_name == "python"
        assert "学習プロセス" in advice or "スクリプト" in advice
    
    def test_match_pattern_unknown(self):
        """
        不明なプロセスのマッチング
        
        **検証要件: AC-002**
        """
        pattern_name, advice = _match_pattern("unknown_process", DEFAULT_PATTERNS)
        
        assert pattern_name == "unknown"
        assert "高負荷" in advice
    
    def test_match_pattern_case_insensitive(self):
        """
        大文字小文字を区別しない
        
        **検証要件: AC-002**
        """
        pattern_name1, _ = _match_pattern("NODE", DEFAULT_PATTERNS)
        pattern_name2, _ = _match_pattern("node", DEFAULT_PATTERNS)
        pattern_name3, _ = _match_pattern("Node", DEFAULT_PATTERNS)
        
        assert pattern_name1 == pattern_name2 == pattern_name3 == "node"
    
    def test_match_pattern_partial_match(self):
        """
        部分一致のマッチング
        
        **検証要件: AC-002**
        """
        # "nodejs"は"node"を含むのでマッチする
        pattern_name, _ = _match_pattern("nodejs", DEFAULT_PATTERNS)
        assert pattern_name == "node"
        
        # "python3.11"は"python"を含むのでマッチする
        pattern_name, _ = _match_pattern("python3.11", DEFAULT_PATTERNS)
        assert pattern_name == "python"
    
    def test_match_pattern_empty_name(self):
        """
        プロセス名が空の場合
        
        **検証要件: AC-002**
        """
        pattern_name, advice = _match_pattern("", DEFAULT_PATTERNS)
        
        assert pattern_name == "unknown"
        assert advice is not None


class TestFormatAdvice:
    """_format_advice()のテスト"""
    
    def test_format_advice_minimal(self):
        """
        minimal詳細度のメッセージ生成
        
        **検証要件: AC-003**
        """
        processes = [
            {
                "name": "node",
                "pid": 12345,
                "cpu_percent": 45.0,
                "memory_percent": 30.0,
                "cmdline": "/usr/bin/node server.js",
                "advice": "テストアドバイス"
            }
        ]
        
        message = _format_advice(processes, "minimal")
        
        assert "node" in message
        assert "12345" in message
        assert "45.0" in message
        assert "30.0" in message
        # minimalではアドバイスは含まれない
        assert "テストアドバイス" not in message
    
    def test_format_advice_normal(self):
        """
        normal詳細度のメッセージ生成
        
        **検証要件: AC-003**
        """
        processes = [
            {
                "name": "node",
                "pid": 12345,
                "cpu_percent": 45.0,
                "memory_percent": 30.0,
                "cmdline": "/usr/bin/node server.js",
                "advice": "テストアドバイス"
            }
        ]
        
        message = _format_advice(processes, "normal")
        
        assert "node" in message
        assert "12345" in message
        # normalではアドバイスが含まれる
        assert "テストアドバイス" in message
        # normalではコマンドラインは含まれない
        assert "コマンド:" not in message
    
    def test_format_advice_detailed(self):
        """
        detailed詳細度のメッセージ生成
        
        **検証要件: AC-003**
        """
        processes = [
            {
                "name": "node",
                "pid": 12345,
                "cpu_percent": 45.0,
                "memory_percent": 30.0,
                "cmdline": "/usr/bin/node server.js",
                "advice": "テストアドバイス",
                "detailed_advice": "停止方法: kill {pid}"
            }
        ]
        
        message = _format_advice(processes, "detailed")
        
        assert "node" in message
        assert "12345" in message
        assert "テストアドバイス" in message
        # detailedではコマンドラインが含まれる
        assert "コマンド:" in message
        assert "/usr/bin/node server.js" in message
        # detailedでは詳細アドバイスが含まれる
        assert "停止方法" in message
        # {pid}が実際のPIDに置換される
        assert "kill 12345" in message
    
    def test_format_advice_empty_processes(self):
        """
        プロセス情報が空の場合
        
        **検証要件: AC-003**
        """
        message = _format_advice([], "normal")
        
        assert "取得できませんでした" in message
    
    def test_format_advice_invalid_level(self):
        """
        不正な詳細度の場合
        
        **検証要件: AC-003**
        """
        processes = [
            {
                "name": "test",
                "pid": 123,
                "cpu_percent": 10.0,
                "memory_percent": 5.0,
                "cmdline": "test",
                "advice": "test"
            }
        ]
        
        # 不正な詳細度を指定してもエラーにならず、normalにフォールバック
        message = _format_advice(processes, "invalid")
        
        assert "test" in message
        assert isinstance(message, str)
    
    def test_format_advice_long_cmdline(self):
        """
        長いコマンドラインの省略
        
        **検証要件: AC-003**
        """
        long_cmdline = "a" * 100
        processes = [
            {
                "name": "test",
                "pid": 123,
                "cpu_percent": 10.0,
                "memory_percent": 5.0,
                "cmdline": long_cmdline,
                "advice": "test"
            }
        ]
        
        message = _format_advice(processes, "detailed")
        
        # 80文字以上は省略される
        assert "..." in message
        assert len(long_cmdline) > 80


class TestGetContextualAdvice:
    """get_contextual_advice()のテスト"""
    
    def test_get_contextual_advice_cpu(self):
        """
        CPU使用率でコンテキストアドバイスを取得
        
        **検証要件: AC-001, AC-002, AC-003**
        """
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "normal",
                "top_processes_count": 3
            }
        }
        
        result = get_contextual_advice("cpu", config, "normal")
        
        assert "top_processes" in result
        assert "formatted_message" in result
        assert isinstance(result["top_processes"], list)
        assert isinstance(result["formatted_message"], str)
    
    def test_get_contextual_advice_memory(self):
        """
        メモリ使用率でコンテキストアドバイスを取得
        
        **検証要件: AC-001, AC-002, AC-003**
        """
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "normal",
                "top_processes_count": 3
            }
        }
        
        result = get_contextual_advice("memory", config, "normal")
        
        assert "top_processes" in result
        assert "formatted_message" in result
    
    def test_get_contextual_advice_invalid_metric_type(self):
        """
        不正なメトリクスタイプでエラー
        
        **検証要件: AC-001**
        """
        config = {"contextual_advice": {}}
        
        with pytest.raises(ValueError, match="Invalid metric_type"):
            get_contextual_advice("invalid", config, "normal")
    
    def test_get_contextual_advice_custom_patterns(self):
        """
        カスタムパターンの使用
        
        **検証要件: AC-002, AC-003**
        """
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "normal",
                "top_processes_count": 3,
                "patterns": {
                    "custom": {
                        "keywords": ["test"],
                        "advice": "カスタムアドバイス"
                    }
                }
            }
        }
        
        result = get_contextual_advice("memory", config, "normal")
        
        # カスタムパターンが使用される
        assert isinstance(result, dict)



class TestDetailedAdvice:
    """detailed_adviceのテスト"""
    
    def test_get_contextual_advice_with_detailed_advice(self):
        """
        detailed_adviceが正しく取得される
        
        **検証要件: AC-003**
        """
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "detailed",
                "top_processes_count": 3,
                "patterns": {
                    "test": {
                        "keywords": ["python"],
                        "advice": "テストアドバイス",
                        "detailed_advice": "詳細アドバイス: kill {pid}"
                    }
                }
            }
        }
        
        result = get_contextual_advice("memory", config, "detailed")
        
        # detailed_adviceが含まれる
        assert "top_processes" in result
        for proc in result["top_processes"]:
            if proc.get("pattern") == "test":
                assert "detailed_advice" in proc
                assert proc["detailed_advice"] == "詳細アドバイス: kill {pid}"


class TestExceptionHandling:
    """例外ハンドリングのテスト"""
    
    def test_exception_during_process_iteration(self):
        """
        プロセス走査中の例外ハンドリング
        
        **検証要件: AC-001**
        """
        # psutil.process_iter()が例外を投げる場合
        with patch('src.komon.contextual_advisor.psutil.process_iter', side_effect=Exception("Test error")):
            processes = _get_top_processes("cpu", 3)
            
            # 空リストが返される
            assert processes == []
    
    def test_exception_during_process_info_retrieval(self):
        """
        プロセス情報取得中の例外ハンドリング
        
        **検証要件: AC-001**
        """
        import psutil
        
        # プロセス情報取得時に例外が発生
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'test',
            'pid': 12345,
            'memory_percent': 10.0,
            'cmdline': ['test']
        }
        # 予期しない例外
        mock_proc.cpu_percent.side_effect = RuntimeError("Unexpected error")
        
        with patch('src.komon.contextual_advisor.psutil.process_iter', return_value=[mock_proc]):
            # 例外が発生してもクラッシュしない
            processes = _get_top_processes("cpu", 3)
            assert isinstance(processes, list)
