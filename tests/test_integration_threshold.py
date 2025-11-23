"""
3段階閾値の統合テスト

エンドツーエンドでの閾値検知と通知生成をテストします。
"""

import pytest
from komon.analyzer import load_thresholds, analyze_usage
from komon.settings_validator import ThresholdLevel


class TestThreeTierIntegration:
    """3段階閾値の統合テスト"""
    
    def test_end_to_end_three_tier_detection(self):
        """3段階閾値でのエンドツーエンド検知"""
        config = {
            "thresholds": {
                "cpu": {"warning": 70, "alert": 85, "critical": 95},
                "mem": {"warning": 70, "alert": 80, "critical": 90},
                "disk": {"warning": 70, "alert": 80, "critical": 90},
            }
        }
        
        # 設定読み込み
        thresholds = load_thresholds(config)
        
        # 使用率データ
        usage = {
            "cpu": 75.0,   # 警告レベル
            "mem": 85.0,   # 警戒レベル
            "disk": 95.0,  # 緊急レベル
        }
        
        # 分析実行
        alerts = analyze_usage(usage, thresholds)
        
        # 3つのアラートが生成される
        assert len(alerts) == 3
        
        # 各レベルの絵文字が含まれる
        alert_text = "\n".join(alerts)
        assert "💛" in alert_text  # 警告
        assert "🧡" in alert_text  # 警戒
        assert "❤️" in alert_text  # 緊急
    
    def test_backward_compatibility_with_legacy_config(self):
        """従来設定との後方互換性"""
        # 従来の単一閾値設定
        legacy_config = {
            "thresholds": {
                "cpu": 85,
                "mem": 80,
                "disk": 80,
            }
        }
        
        # 設定読み込み（3段階に正規化される）
        thresholds = load_thresholds(legacy_config)
        
        # 従来の閾値（alert）を超える値
        usage = {
            "cpu": 87.0,
            "mem": 82.0,
            "disk": 82.0,
        }
        
        # 分析実行
        alerts = analyze_usage(usage, thresholds)
        
        # すべてアラートが発生する
        assert len(alerts) == 3
        
        # 警戒レベル（alert）として検知される
        for alert in alerts:
            assert "🧡" in alert
    
    def test_escalation_scenario(self):
        """エスカレーションシナリオ"""
        config = {
            "thresholds": {
                "cpu": {"warning": 70, "alert": 85, "critical": 95},
                "mem": {"warning": 70, "alert": 80, "critical": 90},
                "disk": {"warning": 70, "alert": 80, "critical": 90},
            }
        }
        
        thresholds = load_thresholds(config)
        
        # シナリオ1: 警告レベル
        usage1 = {"cpu": 75.0, "mem": 60.0, "disk": 60.0}
        alerts1 = analyze_usage(usage1, thresholds)
        assert len(alerts1) == 1
        assert "💛" in alerts1[0]
        
        # シナリオ2: 警戒レベルにエスカレーション
        usage2 = {"cpu": 87.0, "mem": 60.0, "disk": 60.0}
        alerts2 = analyze_usage(usage2, thresholds)
        assert len(alerts2) == 1
        assert "🧡" in alerts2[0]
        
        # シナリオ3: 緊急レベルにエスカレーション
        usage3 = {"cpu": 96.0, "mem": 60.0, "disk": 60.0}
        alerts3 = analyze_usage(usage3, thresholds)
        assert len(alerts3) == 1
        assert "❤️" in alerts3[0]
    
    def test_mixed_format_config(self):
        """3段階と単一値の混在設定"""
        config = {
            "thresholds": {
                "cpu": {"warning": 70, "alert": 85, "critical": 95},
                "mem": 80,  # 単一値
                "disk": {"warning": 70, "alert": 80, "critical": 90},
            }
        }
        
        thresholds = load_thresholds(config)
        
        # すべて3段階形式に正規化される
        assert isinstance(thresholds["cpu"], dict)
        assert isinstance(thresholds["mem"], dict)
        assert isinstance(thresholds["disk"], dict)
        
        # 単一値が正しく正規化される
        assert thresholds["mem"]["alert"] == 80
        assert thresholds["mem"]["warning"] == 70  # 80 - 10
        assert thresholds["mem"]["critical"] == 90  # 80 + 10
    
    def test_notification_message_format(self):
        """通知メッセージのフォーマット確認"""
        config = {
            "thresholds": {
                "cpu": {"warning": 70, "alert": 85, "critical": 95},
                "mem": {"warning": 70, "alert": 80, "critical": 90},
                "disk": {"warning": 70, "alert": 80, "critical": 90},
            }
        }
        
        thresholds = load_thresholds(config)
        usage = {"cpu": 75.0, "mem": 60.0, "disk": 60.0}
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 1
        alert = alerts[0]
        
        # メッセージに必要な要素が含まれる
        assert "💛" in alert  # 絵文字
        assert "そろそろ気にかけておいた方がいいかも" in alert  # プレフィックス
        assert "CPU" in alert  # メトリクス名
        assert "75.0%" in alert  # 値
    
    def test_all_levels_message_content(self):
        """すべてのレベルのメッセージ内容確認"""
        config = {
            "thresholds": {
                "cpu": {"warning": 70, "alert": 85, "critical": 95},
                "mem": {"warning": 70, "alert": 80, "critical": 90},
                "disk": {"warning": 70, "alert": 80, "critical": 90},
            }
        }
        
        thresholds = load_thresholds(config)
        
        # 警告レベル
        usage_warning = {"cpu": 75.0, "mem": 60.0, "disk": 60.0}
        alerts_warning = analyze_usage(usage_warning, thresholds)
        assert "そろそろ気にかけておいた方がいいかも" in alerts_warning[0]
        
        # 警戒レベル
        usage_alert = {"cpu": 87.0, "mem": 60.0, "disk": 60.0}
        alerts_alert = analyze_usage(usage_alert, thresholds)
        assert "ちょっと気になる水準です" in alerts_alert[0]
        
        # 緊急レベル
        usage_critical = {"cpu": 96.0, "mem": 60.0, "disk": 60.0}
        alerts_critical = analyze_usage(usage_critical, thresholds)
        assert "かなり逼迫しています！" in alerts_critical[0]
    
    def test_boundary_values(self):
        """境界値でのテスト"""
        config = {
            "thresholds": {
                "cpu": {"warning": 70, "alert": 85, "critical": 95},
                "mem": {"warning": 70, "alert": 80, "critical": 90},
                "disk": {"warning": 70, "alert": 80, "critical": 90},
            }
        }
        
        thresholds = load_thresholds(config)
        
        # 閾値ちょうどの値
        usage = {"cpu": 70.0, "mem": 80.0, "disk": 90.0}
        alerts = analyze_usage(usage, thresholds)
        
        assert len(alerts) == 3
        
        # 各レベルが正しく判定される
        cpu_alert = [a for a in alerts if "CPU" in a][0]
        mem_alert = [a for a in alerts if "メモリ" in a][0]
        disk_alert = [a for a in alerts if "ディスク" in a][0]
        
        assert "💛" in cpu_alert  # warning
        assert "🧡" in mem_alert  # alert
        assert "❤️" in disk_alert  # critical
    
    def test_no_threshold_config(self):
        """閾値設定がない場合のデフォルト動作"""
        config = {}  # 空の設定
        
        thresholds = load_thresholds(config)
        
        # デフォルト値が設定される
        assert "cpu" in thresholds
        assert "mem" in thresholds
        assert "disk" in thresholds
        
        # すべて3段階形式
        assert isinstance(thresholds["cpu"], dict)
        assert "warning" in thresholds["cpu"]
        assert "alert" in thresholds["cpu"]
        assert "critical" in thresholds["cpu"]
