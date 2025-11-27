"""
contextual_advisor.py の統合テスト

エンドツーエンドの動作とanalyzer.pyとの統合を検証する
"""

import pytest
from unittest.mock import patch, MagicMock
from src.komon.contextual_advisor import get_contextual_advice
from src.komon.analyzer import analyze_usage


class TestEndToEndContextualAdvice:
    """エンドツーエンドのコンテキストアドバイス生成"""
    
    def test_end_to_end_contextual_advice(self):
        """
        エンドツーエンドでコンテキストアドバイスが生成される
        
        **検証要件: AC-001, AC-002, AC-003**
        """
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "normal",
                "top_processes_count": 3,
                "patterns": {
                    "test": {
                        "keywords": ["test"],
                        "advice": "テストアドバイス"
                    }
                }
            }
        }
        
        # CPU使用率でテスト
        result = get_contextual_advice("cpu", config, "normal")
        
        assert "top_processes" in result
        assert "formatted_message" in result
        assert isinstance(result["top_processes"], list)
        assert "上位プロセス:" in result["formatted_message"]
    
    def test_config_loading_and_application(self):
        """
        設定ファイルからパターン定義を読み込んで適用できる
        
        **検証要件: AC-003**
        """
        # カスタムパターンを含む設定
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "detailed",
                "top_processes_count": 5,
                "patterns": {
                    "custom": {
                        "keywords": ["custom_app"],
                        "advice": "カスタムアプリケーションが動いています",
                        "detailed_advice": "停止方法: systemctl stop custom_app"
                    }
                }
            }
        }
        
        result = get_contextual_advice("memory", config, "detailed")
        
        # 設定が正しく適用される
        assert len(result["top_processes"]) <= 5
        assert "コマンド:" in result["formatted_message"]  # detailed


class TestIntegrationWithAnalyzer:
    """analyzer.pyとの統合"""
    
    def test_integration_with_analyzer(self):
        """
        analyzer.py と統合して動作する
        
        **検証要件: AC-004**
        """
        usage = {
            "cpu": 90,
            "mem": 85,
            "disk": 70
        }
        
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "normal",
                "top_processes_count": 3
            }
        }
        
        # コンテキストアドバイスを有効にして実行
        alerts = analyze_usage(usage, thresholds, use_progressive=False, 
                              use_contextual_advice=True, config=config)
        
        # アラートが生成される
        assert len(alerts) > 0
        
        # コンテキストアドバイスが含まれる
        has_contextual = any("上位プロセス:" in alert for alert in alerts)
        assert has_contextual
    
    def test_backward_compatibility(self):
        """
        use_contextual_advice=False の場合、既存機能に影響がない
        
        **検証要件: AC-004**
        """
        usage = {
            "cpu": 90,
            "mem": 85,
            "disk": 70
        }
        
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        # コンテキストアドバイスを無効にして実行
        alerts = analyze_usage(usage, thresholds, use_progressive=False, 
                              use_contextual_advice=False, config=None)
        
        # アラートが生成される
        assert len(alerts) > 0
        
        # コンテキストアドバイスは含まれない
        has_contextual = any("上位プロセス:" in alert for alert in alerts)
        assert not has_contextual


class TestPerformanceImpact:
    """パフォーマンステスト"""
    
    def test_performance_impact(self):
        """
        コンテキストアドバイス機能の処理時間が5秒以内
        
        **検証要件: AC-005**
        """
        import time
        
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "normal",
                "top_processes_count": 3
            }
        }
        
        start = time.time()
        result = get_contextual_advice("cpu", config, "normal")
        elapsed = time.time() - start
        
        # 処理時間が5秒以内（CI環境を考慮）
        assert elapsed < 5.0, f"処理時間が長すぎます: {elapsed:.2f}秒"
        
        # 結果が正しく返される
        assert "top_processes" in result
        assert "formatted_message" in result


class TestErrorHandling:
    """エラーハンドリング"""
    
    def test_error_handling_invalid_metric_type(self):
        """
        不正なメトリクスタイプでエラー
        
        **検証要件: AC-001**
        """
        config = {"contextual_advice": {}}
        
        with pytest.raises(ValueError, match="Invalid metric_type"):
            get_contextual_advice("invalid", config, "normal")
    
    def test_error_handling_missing_config(self):
        """
        設定が不足している場合、デフォルト値を使用
        
        **検証要件: AC-003**
        """
        # 空の設定
        config = {}
        
        # エラーにならず、デフォルト値で動作
        result = get_contextual_advice("memory", config, "normal")
        
        assert "top_processes" in result
        assert "formatted_message" in result
    
    def test_error_handling_process_access_denied(self):
        """
        プロセス情報取得時のアクセス拒否エラーを適切にハンドリング
        
        **検証要件: AC-001**
        """
        import psutil
        
        # アクセス拒否をシミュレート
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'test',
            'pid': 12345,
            'memory_percent': 10.0,
            'cmdline': ['test']
        }
        mock_proc.cpu_percent.side_effect = psutil.AccessDenied(12345)
        
        with patch('src.komon.contextual_advisor.psutil.process_iter', return_value=[mock_proc]):
            config = {"contextual_advice": {"top_processes_count": 3}}
            
            # エラーが発生してもクラッシュしない
            result = get_contextual_advice("cpu", config, "normal")
            
            assert isinstance(result, dict)
            assert "top_processes" in result


class TestAdviceLevels:
    """詳細度のテスト"""
    
    def test_advice_level_minimal(self):
        """
        minimal詳細度のテスト
        
        **検証要件: AC-003**
        """
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "minimal",
                "top_processes_count": 3
            }
        }
        
        result = get_contextual_advice("memory", config, "minimal")
        
        # minimalではアドバイスが含まれない
        message = result["formatted_message"]
        assert "上位プロセス:" in message
        # アドバイスの矢印が含まれない
        assert "→" not in message
    
    def test_advice_level_normal(self):
        """
        normal詳細度のテスト
        
        **検証要件: AC-003**
        """
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "normal",
                "top_processes_count": 3
            }
        }
        
        result = get_contextual_advice("memory", config, "normal")
        
        # normalではアドバイスが含まれる
        message = result["formatted_message"]
        assert "上位プロセス:" in message
    
    def test_advice_level_detailed(self):
        """
        detailed詳細度のテスト
        
        **検証要件: AC-003**
        """
        config = {
            "contextual_advice": {
                "enabled": True,
                "advice_level": "detailed",
                "top_processes_count": 3
            }
        }
        
        result = get_contextual_advice("memory", config, "detailed")
        
        # detailedではコマンドラインが含まれる
        message = result["formatted_message"]
        assert "上位プロセス:" in message
        # 少なくとも1つのプロセスがあればコマンドが表示される
        if len(result["top_processes"]) > 0:
            assert "コマンド:" in message or "取得できませんでした" in message
