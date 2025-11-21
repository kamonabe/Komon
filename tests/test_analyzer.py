"""
analyzer.pyのテスト

閾値判定とアラート生成のロジックをテストします。
"""

import pytest
from komon.analyzer import load_thresholds, analyze_usage


class TestLoadThresholds:
    """閾値読み込みのテスト"""
    
    def test_load_default_thresholds(self):
        """デフォルト値が正しく読み込まれること"""
        config = {}
        thresholds = load_thresholds(config)
        
        assert thresholds["cpu"] == 85
        assert thresholds["mem"] == 80
        assert thresholds["disk"] == 80
        assert thresholds["proc_cpu"] == 20
    
    def test_load_custom_thresholds(self):
        """カスタム閾値が正しく読み込まれること"""
        config = {
            "thresholds": {
                "cpu": 90,
                "mem": 75,
                "disk": 85,
                "proc_cpu": 30
            }
        }
        thresholds = load_thresholds(config)
        
        assert thresholds["cpu"] == 90
        assert thresholds["mem"] == 75
        assert thresholds["disk"] == 85
        assert thresholds["proc_cpu"] == 30
    
    def test_load_partial_thresholds(self):
        """一部のみ設定された場合、残りはデフォルト値になること"""
        config = {
            "thresholds": {
                "cpu": 95
            }
        }
        thresholds = load_thresholds(config)
        
        assert thresholds["cpu"] == 95
        assert thresholds["mem"] == 80  # デフォルト
        assert thresholds["disk"] == 80  # デフォルト


class TestAnalyzeUsage:
    """使用率分析のテスト"""
    
    def test_no_alerts_when_below_threshold(self):
        """閾値以下の場合、アラートが発生しないこと"""
        usage = {"cpu": 50.0, "mem": 60.0, "disk": 70.0}
        thresholds = {"cpu": 85, "mem": 80, "disk": 80}
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 0
    
    def test_cpu_alert_when_above_threshold(self):
        """CPU使用率が閾値を超えた場合、アラートが発生すること"""
        usage = {"cpu": 90.0, "mem": 60.0, "disk": 70.0}
        thresholds = {"cpu": 85, "mem": 80, "disk": 80}
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 1
        assert "CPU" in alerts[0]
        assert "90.0%" in alerts[0]
    
    def test_mem_alert_when_above_threshold(self):
        """メモリ使用率が閾値を超えた場合、アラートが発生すること"""
        usage = {"cpu": 50.0, "mem": 85.0, "disk": 70.0}
        thresholds = {"cpu": 85, "mem": 80, "disk": 80}
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 1
        assert "メモリ" in alerts[0]
        assert "85.0%" in alerts[0]
    
    def test_disk_alert_when_above_threshold(self):
        """ディスク使用率が閾値を超えた場合、アラートが発生すること"""
        usage = {"cpu": 50.0, "mem": 60.0, "disk": 85.0}
        thresholds = {"cpu": 85, "mem": 80, "disk": 80}
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 1
        assert "ディスク" in alerts[0]
        assert "85.0%" in alerts[0]
    
    def test_multiple_alerts(self):
        """複数の閾値を超えた場合、複数のアラートが発生すること"""
        usage = {"cpu": 90.0, "mem": 85.0, "disk": 85.0}
        thresholds = {"cpu": 85, "mem": 80, "disk": 80}
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 3
        assert any("CPU" in alert for alert in alerts)
        assert any("メモリ" in alert for alert in alerts)
        assert any("ディスク" in alert for alert in alerts)
    
    def test_exact_threshold_triggers_alert(self):
        """閾値ちょうどの場合もアラートが発生すること"""
        usage = {"cpu": 85.0, "mem": 80.0, "disk": 80.0}
        thresholds = {"cpu": 85, "mem": 80, "disk": 80}
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 3
    
    def test_missing_usage_data(self):
        """使用率データが欠けている場合、エラーにならないこと"""
        usage = {"cpu": 90.0}  # mem, diskが欠けている
        thresholds = {"cpu": 85, "mem": 80, "disk": 80}
        
        alerts = analyze_usage(usage, thresholds)
        
        # CPUのアラートのみ発生
        assert len(alerts) == 1
        assert "CPU" in alerts[0]
