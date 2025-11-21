"""
log_analyzer.pyのテスト

ログ異常検知のロジックをテストします。
"""

import pytest
from komon.log_analyzer import check_log_anomaly


class TestCheckLogAnomaly:
    """ログ異常検知のテスト"""
    
    def test_no_anomaly_below_threshold(self):
        """閾値以下の場合、警告が発生しないこと"""
        config = {
            "log_analysis": {
                "line_threshold": 100
            }
        }
        
        result = check_log_anomaly("/var/log/test.log", 50, config)
        
        assert result == ""
    
    def test_anomaly_above_threshold(self):
        """閾値を超えた場合、警告が発生すること"""
        config = {
            "log_analysis": {
                "line_threshold": 100
            }
        }
        
        result = check_log_anomaly("/var/log/test.log", 150, config)
        
        assert result != ""
        assert "/var/log/test.log" in result
        assert "150" in result
    
    def test_default_threshold(self):
        """設定がない場合、デフォルト閾値（100行）が使われること"""
        config = {}
        
        # 100行以下
        result1 = check_log_anomaly("/var/log/test.log", 99, config)
        assert result1 == ""
        
        # 100行超
        result2 = check_log_anomaly("/var/log/test.log", 101, config)
        assert result2 != ""
    
    def test_exact_threshold(self):
        """閾値ちょうどの場合、警告が発生しないこと"""
        config = {
            "log_analysis": {
                "line_threshold": 100
            }
        }
        
        result = check_log_anomaly("/var/log/test.log", 100, config)
        
        assert result == ""
    
    def test_zero_lines(self):
        """0行の場合、警告が発生しないこと"""
        config = {
            "log_analysis": {
                "line_threshold": 100
            }
        }
        
        result = check_log_anomaly("/var/log/test.log", 0, config)
        
        assert result == ""
    
    def test_custom_threshold(self):
        """カスタム閾値が正しく適用されること"""
        config = {
            "log_analysis": {
                "line_threshold": 500
            }
        }
        
        # 閾値以下
        result1 = check_log_anomaly("/var/log/test.log", 400, config)
        assert result1 == ""
        
        # 閾値超
        result2 = check_log_anomaly("/var/log/test.log", 600, config)
        assert result2 != ""
        assert "600" in result2
