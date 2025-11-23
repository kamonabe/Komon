"""
analyzer.pyのテスト

閾値判定とアラート生成のロジックをテストします。
"""

import pytest
from komon.analyzer import load_thresholds, analyze_usage
from komon.settings_validator import ThresholdLevel


class TestLoadThresholds:
    """閾値読み込みのテスト"""
    
    def test_load_default_thresholds(self):
        """デフォルト値が正しく読み込まれること"""
        config = {}
        thresholds = load_thresholds(config)
        
        # 3段階形式に正規化される
        assert isinstance(thresholds["cpu"], dict)
        assert "warning" in thresholds["cpu"]
        assert "alert" in thresholds["cpu"]
        assert "critical" in thresholds["cpu"]
        assert thresholds["proc_cpu"] == 20
    
    def test_load_three_tier_thresholds(self):
        """3段階閾値が正しく読み込まれること"""
        config = {
            "thresholds": {
                "cpu": {"warning": 70, "alert": 85, "critical": 95},
                "mem": {"warning": 70, "alert": 80, "critical": 90},
                "disk": {"warning": 70, "alert": 80, "critical": 90},
                "proc_cpu": 30
            }
        }
        thresholds = load_thresholds(config)
        
        assert thresholds["cpu"]["warning"] == 70
        assert thresholds["cpu"]["alert"] == 85
        assert thresholds["cpu"]["critical"] == 95
        assert thresholds["proc_cpu"] == 30
    
    def test_load_legacy_single_thresholds(self):
        """従来の単一閾値が3段階に正規化されること"""
        config = {
            "thresholds": {
                "cpu": 85,
                "mem": 80,
                "disk": 80,
                "proc_cpu": 20
            }
        }
        thresholds = load_thresholds(config)
        
        # 単一値が3段階に正規化される
        assert thresholds["cpu"]["alert"] == 85
        assert thresholds["cpu"]["warning"] == 75  # 85 - 10
        assert thresholds["cpu"]["critical"] == 95  # 85 + 10
        assert thresholds["proc_cpu"] == 20


class TestAnalyzeUsage:
    """使用率分析のテスト"""
    
    def test_no_alerts_when_below_threshold(self):
        """閾値以下の場合、アラートが発生しないこと"""
        usage = {"cpu": 50.0, "mem": 60.0, "disk": 60.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 0
    
    def test_warning_level_alert(self):
        """警告レベルの閾値を超えた場合、警告アラートが発生すること"""
        usage = {"cpu": 75.0, "mem": 60.0, "disk": 60.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 1
        assert "💛" in alerts[0]  # 警告の絵文字
        assert "CPU" in alerts[0]
        assert "75.0%" in alerts[0]
    
    def test_alert_level_alert(self):
        """警戒レベルの閾値を超えた場合、警戒アラートが発生すること"""
        usage = {"cpu": 50.0, "mem": 85.0, "disk": 60.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 1
        assert "🧡" in alerts[0]  # 警戒の絵文字
        assert "メモリ" in alerts[0]
        assert "85.0%" in alerts[0]
    
    def test_critical_level_alert(self):
        """緊急レベルの閾値を超えた場合、緊急アラートが発生すること"""
        usage = {"cpu": 50.0, "mem": 60.0, "disk": 95.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 1
        assert "❤️" in alerts[0]  # 緊急の絵文字
        assert "ディスク" in alerts[0]
        assert "95.0%" in alerts[0]
    
    def test_multiple_level_alerts(self):
        """異なるレベルの複数アラートが発生すること"""
        usage = {"cpu": 75.0, "mem": 85.0, "disk": 95.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 3
        assert any("💛" in alert and "CPU" in alert for alert in alerts)
        assert any("🧡" in alert and "メモリ" in alert for alert in alerts)
        assert any("❤️" in alert and "ディスク" in alert for alert in alerts)
    
    def test_exact_threshold_triggers_alert(self):
        """閾値ちょうどの場合もアラートが発生すること"""
        usage = {"cpu": 70.0, "mem": 80.0, "disk": 90.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
        
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 3
        assert any("💛" in alert for alert in alerts)  # CPU: warning
        assert any("🧡" in alert for alert in alerts)  # mem: alert
        assert any("❤️" in alert for alert in alerts)  # disk: critical
    
    def test_missing_usage_data(self):
        """使用率データが欠けている場合、エラーにならないこと"""
        usage = {"cpu": 90.0}  # mem, diskが欠けている
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
        
        alerts = analyze_usage(usage, thresholds)
        
        # CPUのアラートのみ発生
        assert len(alerts) == 1
        assert "CPU" in alerts[0]
    
    def test_emoji_assignment(self):
        """各レベルに正しい絵文字が割り当てられること"""
        # 警告レベル
        usage_warning = {"cpu": 75.0, "mem": 60.0, "disk": 60.0}
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
        alerts = analyze_usage(usage_warning, thresholds)
        assert "💛" in alerts[0]
        
        # 警戒レベル
        usage_alert = {"cpu": 87.0, "mem": 60.0, "disk": 60.0}
        alerts = analyze_usage(usage_alert, thresholds)
        assert "🧡" in alerts[0]
        
        # 緊急レベル
        usage_critical = {"cpu": 96.0, "mem": 60.0, "disk": 60.0}
        alerts = analyze_usage(usage_critical, thresholds)
        assert "❤️" in alerts[0]
