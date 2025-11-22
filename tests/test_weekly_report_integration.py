"""
週次レポート機能の統合テスト
"""

import os
import csv
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from komon.weekly_data import collect_weekly_data
from komon.report_formatter import format_weekly_report


class TestWeeklyReportIntegration:
    """週次レポート機能の統合テスト"""
    
    def test_end_to_end_report_generation_no_data(self, monkeypatch):
        """データなしでのエンドツーエンドレポート生成テスト"""
        # データがない状態をシミュレート
        monkeypatch.setattr('komon.weekly_data.HISTORY_DIR', '/nonexistent/path')
        
        def mock_load():
            return []
        monkeypatch.setattr('komon.weekly_data.load_notification_history', mock_load)
        
        # データ収集
        data = collect_weekly_data()
        
        # レポート生成
        report = format_weekly_report(data)
        
        # 基本構造が含まれていること
        assert '📊 週次健全性レポート' in report
        assert '【リソース状況】' in report
        assert '【今週の警戒情報】' in report
        assert '【トレンド】' in report
        assert '- なし' in report  # 警戒情報なし
    
    def test_end_to_end_report_generation_with_data(self, tmp_path, monkeypatch):
        """データありでのエンドツーエンドレポート生成テスト"""
        # 一時ディレクトリを使用
        history_dir = tmp_path / "usage_history"
        history_dir.mkdir()
        monkeypatch.setattr('komon.weekly_data.HISTORY_DIR', str(history_dir))
        
        # 今週のテストデータを作成（直近3日分）
        now = datetime.now()
        for i in range(1, 4):
            date = now - timedelta(days=i)
            filename = f"usage_{date.strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = history_dir / filename
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'cpu', 'mem', 'disk'])
                writer.writerow([date.isoformat(), 50.0, 60.0, 70.0])
        
        # 先週のテストデータを作成（8-10日前）
        for i in range(8, 11):
            date = now - timedelta(days=i)
            filename = f"usage_{date.strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = history_dir / filename
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'cpu', 'mem', 'disk'])
                writer.writerow([date.isoformat(), 48.0, 62.0, 68.0])
        
        # 通知履歴のモック
        test_notifications = [
            {
                'timestamp': (now - timedelta(days=2)).isoformat(),
                'metric_type': 'cpu',
                'metric_value': 90.0,
                'message': 'CPU使用率が高いです'
            }
        ]
        
        def mock_load():
            return test_notifications
        monkeypatch.setattr('komon.weekly_data.load_notification_history', mock_load)
        
        # データ収集
        data = collect_weekly_data()
        
        # データの検証
        assert 'resources' in data
        assert data['resources']['cpu']['current'] == 50.0
        assert data['resources']['mem']['current'] == 60.0
        assert data['resources']['disk']['current'] == 70.0
        
        # レポート生成
        report = format_weekly_report(data)
        
        # レポート内容の検証
        assert '📊 週次健全性レポート' in report
        assert 'CPU使用率: 50.0%' in report
        assert 'メモリ使用率: 60.0%' in report
        assert 'ディスク使用率: 70.0%' in report
        assert 'CPU使用率が高いです' in report
    
    def test_notification_delivery_slack_only(self, monkeypatch):
        """Slack通知のみの配信テスト"""
        from scripts.weekly_report import send_report
        
        # モック設定
        slack_called = {'called': False, 'message': None}
        
        def mock_slack(message, webhook_url, metadata=None):
            slack_called['called'] = True
            slack_called['message'] = message
            return True
        
        def mock_email(message, config, metadata=None):
            pytest.fail("Email should not be called")
        
        monkeypatch.setattr('scripts.weekly_report.send_slack_alert', mock_slack)
        monkeypatch.setattr('scripts.weekly_report.send_email_alert', mock_email)
        
        # 設定
        config = {
            'notifications': {
                'slack': {
                    'enabled': True,
                    'webhook_url': 'https://hooks.slack.com/test'
                },
                'email': {
                    'enabled': False
                }
            },
            'weekly_report': {
                'notifications': {
                    'slack': True,
                    'email': False
                }
            }
        }
        
        # レポート送信
        send_report('Test report', config)
        
        # Slackが呼ばれたことを確認
        assert slack_called['called']
        assert slack_called['message'] == 'Test report'
    
    def test_notification_delivery_both(self, monkeypatch):
        """Slack/メール両方の配信テスト"""
        from scripts.weekly_report import send_report
        
        # モック設定
        calls = {'slack': False, 'email': False}
        
        def mock_slack(message, webhook_url, metadata=None):
            calls['slack'] = True
            return True
        
        def mock_email(message, config, metadata=None):
            calls['email'] = True
            return True
        
        monkeypatch.setattr('scripts.weekly_report.send_slack_alert', mock_slack)
        monkeypatch.setattr('scripts.weekly_report.send_email_alert', mock_email)
        
        # 設定
        config = {
            'notifications': {
                'slack': {
                    'enabled': True,
                    'webhook_url': 'https://hooks.slack.com/test'
                },
                'email': {
                    'enabled': True,
                    'smtp_server': 'smtp.test.com'
                }
            },
            'weekly_report': {
                'notifications': {
                    'slack': True,
                    'email': True
                }
            }
        }
        
        # レポート送信
        send_report('Test report', config)
        
        # 両方が呼ばれたことを確認
        assert calls['slack']
        assert calls['email']
    
    def test_configuration_loading(self, tmp_path):
        """設定ファイル読み込みテスト"""
        from scripts.weekly_report import load_config
        
        # テスト用設定ファイルを作成
        config_file = tmp_path / "test_settings.yml"
        config_content = """
weekly_report:
  enabled: true
  day_of_week: 1
  hour: 9
  minute: 0
  notifications:
    slack: true
    email: false
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        # 設定読み込み
        config = load_config(str(config_file))
        
        # 検証
        assert config is not None
        assert 'weekly_report' in config
        assert config['weekly_report']['enabled'] is True
        assert config['weekly_report']['day_of_week'] == 1
        assert config['weekly_report']['hour'] == 9
    
    def test_graceful_degradation_missing_data(self, monkeypatch):
        """データ不足時のグレースフルデグラデーションテスト"""
        # データがない状態
        monkeypatch.setattr('komon.weekly_data.HISTORY_DIR', '/nonexistent/path')
        
        def mock_load():
            return []
        monkeypatch.setattr('komon.weekly_data.load_notification_history', mock_load)
        
        # レポート生成が失敗しないことを確認
        try:
            data = collect_weekly_data()
            report = format_weekly_report(data)
            
            # レポートが生成されること
            assert report is not None
            assert len(report) > 0
            assert '📊 週次健全性レポート' in report
            
        except Exception as e:
            pytest.fail(f"Report generation should not fail: {e}")
