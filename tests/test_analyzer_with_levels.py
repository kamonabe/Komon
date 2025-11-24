"""
analyze_usage_with_levels関数のテスト

閾値レベル情報を返す新しい関数のテストです。
"""

import pytest
from komon.analyzer import analyze_usage_with_levels, load_thresholds


class TestAnalyzeUsageWithLevels:
    """analyze_usage_with_levels関数のテスト"""
    
    def test_no_alerts_returns_empty_levels(self):
        """閾値以下の場合、空のレベル情報を返す"""
        usage = {"cpu": 50.0, "mem": 50.0, "disk": 50.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        alerts, levels = analyze_usage_with_levels(usage, thresholds)
        
        assert alerts == []
        assert levels == {}
    
    def test_warning_level_alert(self):
        """警告レベルのアラートとレベル情報を返す"""
        usage = {"cpu": 75.0, "mem": 50.0, "disk": 50.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        alerts, levels = analyze_usage_with_levels(usage, thresholds)
        
        assert len(alerts) == 1
        assert "CPU" in alerts[0]
        assert "💛" in alerts[0]
        
        assert "cpu" in levels
        assert levels["cpu"][0] == "warning"
        assert levels["cpu"][1] == 75.0
    
    def test_alert_level_alert(self):
        """警戒レベルのアラートとレベル情報を返す"""
        usage = {"cpu": 50.0, "mem": 85.0, "disk": 50.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        alerts, levels = analyze_usage_with_levels(usage, thresholds)
        
        assert len(alerts) == 1
        assert "メモリ" in alerts[0]
        assert "🧡" in alerts[0]
        
        assert "memory" in levels
        assert levels["memory"][0] == "alert"
        assert levels["memory"][1] == 85.0
    
    def test_critical_level_alert(self):
        """緊急レベルのアラートとレベル情報を返す"""
        usage = {"cpu": 50.0, "mem": 50.0, "disk": 92.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        alerts, levels = analyze_usage_with_levels(usage, thresholds)
        
        assert len(alerts) == 1
        assert "ディスク" in alerts[0]
        assert "❤️" in alerts[0]
        
        assert "disk" in levels
        assert levels["disk"][0] == "critical"
        assert levels["disk"][1] == 92.0
    
    def test_multiple_alerts(self):
        """複数のアラートとレベル情報を返す"""
        usage = {"cpu": 75.0, "mem": 85.0, "disk": 92.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        alerts, levels = analyze_usage_with_levels(usage, thresholds)
        
        assert len(alerts) == 3
        
        assert "cpu" in levels
        assert levels["cpu"][0] == "warning"
        
        assert "memory" in levels
        assert levels["memory"][0] == "alert"
        
        assert "disk" in levels
        assert levels["disk"][0] == "critical"
    
    def test_exact_threshold_triggers_alert(self):
        """閾値ちょうどの値でアラートが発生する"""
        usage = {"cpu": 70.0, "mem": 50.0, "disk": 50.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        alerts, levels = analyze_usage_with_levels(usage, thresholds)
        
        assert len(alerts) == 1
        assert "cpu" in levels
        assert levels["cpu"][0] == "warning"
        assert levels["cpu"][1] == 70.0
    
    def test_missing_usage_data(self):
        """使用率データが欠けている場合"""
        usage = {"cpu": 75.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        alerts, levels = analyze_usage_with_levels(usage, thresholds)
        
        assert len(alerts) == 1
        assert "cpu" in levels
        assert "memory" not in levels
        assert "disk" not in levels
