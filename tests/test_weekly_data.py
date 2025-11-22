"""
週次データ収集モジュールのユニットテスト
"""

import os
import csv
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from komon.weekly_data import (
    collect_weekly_data,
    calculate_average_usage,
    get_alert_history,
    analyze_trend
)


class TestWeeklyData:
    """週次データ収集のユニットテスト"""
    
    def test_analyze_trend_stable(self):
        """安定トレンドの判定テスト"""
        result = analyze_trend(50.0, 48.0, threshold=5.0)
        assert result == 'stable'
    
    def test_analyze_trend_increasing(self):
        """増加トレンドの判定テスト"""
        result = analyze_trend(60.0, 50.0, threshold=5.0)
        assert result == 'increasing'
    
    def test_analyze_trend_decreasing(self):
        """減少トレンドの判定テスト"""
        result = analyze_trend(40.0, 50.0, threshold=5.0)
        assert result == 'decreasing'
    
    def test_analyze_trend_zero_previous(self):
        """previous=0の場合のテスト"""
        result = analyze_trend(50.0, 0.0)
        assert result == 'stable'
    
    def test_analyze_trend_custom_threshold(self):
        """カスタム閾値のテスト"""
        # 8%の変化、閾値10%の場合はstable
        result = analyze_trend(54.0, 50.0, threshold=10.0)
        assert result == 'stable'
        
        # 8%の変化、閾値5%の場合はincreasing
        result = analyze_trend(54.0, 50.0, threshold=5.0)
        assert result == 'increasing'
    
    def test_calculate_average_usage_no_data(self, monkeypatch):
        """データがない場合のテスト"""
        # 存在しないディレクトリを指定
        monkeypatch.setattr('komon.weekly_data.HISTORY_DIR', '/nonexistent/path')
        
        result = calculate_average_usage(days=7)
        
        assert result == {'cpu': 0, 'mem': 0, 'disk': 0}
    
    def test_calculate_average_usage_with_data(self, tmp_path, monkeypatch):
        """データがある場合の平均値計算テスト"""
        # 一時ディレクトリを使用
        history_dir = tmp_path / "usage_history"
        history_dir.mkdir()
        monkeypatch.setattr('komon.weekly_data.HISTORY_DIR', str(history_dir))
        
        # テストデータを作成（3日分）
        now = datetime.now()
        test_data = [
            (now - timedelta(days=1), 50.0, 60.0, 70.0),
            (now - timedelta(days=2), 55.0, 65.0, 75.0),
            (now - timedelta(days=3), 45.0, 55.0, 65.0)
        ]
        
        for date, cpu, mem, disk in test_data:
            filename = f"usage_{date.strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = history_dir / filename
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'cpu', 'mem', 'disk'])
                writer.writerow([date.isoformat(), cpu, mem, disk])
        
        # 平均値を計算
        result = calculate_average_usage(days=7)
        
        # 期待値: (50+55+45)/3=50, (60+65+55)/3=60, (70+75+65)/3=70
        assert abs(result['cpu'] - 50.0) < 0.1
        assert abs(result['mem'] - 60.0) < 0.1
        assert abs(result['disk'] - 70.0) < 0.1
    
    def test_get_alert_history_no_data(self, monkeypatch):
        """通知履歴がない場合のテスト"""
        # load_notification_historyが空リストを返すようにモック
        def mock_load():
            return []
        
        monkeypatch.setattr('komon.weekly_data.load_notification_history', mock_load)
        
        result = get_alert_history(days=7)
        
        assert result == []
    
    def test_get_alert_history_with_data(self, monkeypatch):
        """通知履歴がある場合のテスト"""
        now = datetime.now()
        
        # テスト用の通知データ
        test_notifications = [
            {
                'timestamp': (now - timedelta(days=1)).isoformat(),
                'metric_type': 'cpu',
                'metric_value': 90.0,
                'message': 'CPU使用率が高いです'
            },
            {
                'timestamp': (now - timedelta(days=3)).isoformat(),
                'metric_type': 'mem',
                'metric_value': 85.0,
                'message': 'メモリ使用率が高いです'
            },
            {
                'timestamp': (now - timedelta(days=10)).isoformat(),
                'metric_type': 'disk',
                'metric_value': 90.0,
                'message': '古い通知（除外されるべき）'
            }
        ]
        
        def mock_load():
            return test_notifications
        
        monkeypatch.setattr('komon.weekly_data.load_notification_history', mock_load)
        
        result = get_alert_history(days=7)
        
        # 7日以内の通知のみが含まれること
        assert len(result) == 2
        assert all('timestamp' in alert for alert in result)
        assert all('type' in alert for alert in result)
        assert all('message' in alert for alert in result)
    
    def test_collect_weekly_data_structure(self, monkeypatch):
        """collect_weekly_data の戻り値構造テスト"""
        # モック関数を設定
        def mock_calculate_average(days, offset_days=0):
            if offset_days == 0:
                return {'cpu': 50.0, 'mem': 60.0, 'disk': 70.0}
            else:
                return {'cpu': 48.0, 'mem': 62.0, 'disk': 68.0}
        
        def mock_get_alerts(days):
            return []
        
        monkeypatch.setattr('komon.weekly_data.calculate_average_usage', mock_calculate_average)
        monkeypatch.setattr('komon.weekly_data.get_alert_history', mock_get_alerts)
        
        result = collect_weekly_data()
        
        # 構造の検証
        assert 'period' in result
        assert 'start' in result['period']
        assert 'end' in result['period']
        
        assert 'resources' in result
        assert 'cpu' in result['resources']
        assert 'mem' in result['resources']
        assert 'disk' in result['resources']
        
        # 各リソースの構造
        for resource in ['cpu', 'mem', 'disk']:
            assert 'current' in result['resources'][resource]
            assert 'previous' in result['resources'][resource]
            assert 'change' in result['resources'][resource]
            assert 'trend' in result['resources'][resource]
        
        assert 'alerts' in result
