"""
レポートフォーマッターモジュールのユニットテスト
"""

import pytest

from komon.report_formatter import (
    format_weekly_report,
    format_resource_status,
    format_trend_indicator,
    get_trend_text,
    format_alert_summary
)


class TestReportFormatter:
    """レポートフォーマッターのユニットテスト"""
    
    def test_format_resource_status_positive_change(self):
        """正の変化率のフォーマットテスト"""
        result = format_resource_status('CPU使用率', 50.5, 2.3)
        assert 'CPU使用率: 50.5%' in result
        assert '+2.3%' in result
        assert '先週比' in result
    
    def test_format_resource_status_negative_change(self):
        """負の変化率のフォーマットテスト"""
        result = format_resource_status('メモリ使用率', 60.2, -1.5)
        assert 'メモリ使用率: 60.2%' in result
        assert '-1.5%' in result
        assert '先週比' in result
    
    def test_format_resource_status_zero_change(self):
        """変化なしのフォーマットテスト"""
        result = format_resource_status('ディスク使用率', 70.0, 0.0)
        assert 'ディスク使用率: 70.0%' in result
        assert '+0.0%' in result
    
    def test_format_trend_indicator_stable(self):
        """安定トレンドのインジケーターテスト"""
        result = format_trend_indicator('stable')
        assert result == '✅'
    
    def test_format_trend_indicator_increasing(self):
        """増加トレンドのインジケーターテスト"""
        result = format_trend_indicator('increasing')
        assert result == '⚠️'
    
    def test_format_trend_indicator_decreasing(self):
        """減少トレンドのインジケーターテスト"""
        result = format_trend_indicator('decreasing')
        assert result == '📉'
    
    def test_format_trend_indicator_unknown(self):
        """不明なトレンドのインジケーターテスト"""
        result = format_trend_indicator('unknown')
        assert result == '❓'
    
    def test_get_trend_text_stable(self):
        """安定トレンドのテキストテスト"""
        result = get_trend_text('stable')
        assert result == '安定'
    
    def test_get_trend_text_increasing(self):
        """増加トレンドのテキストテスト"""
        result = get_trend_text('increasing')
        assert result == '緩やかに増加傾向'
    
    def test_get_trend_text_decreasing(self):
        """減少トレンドのテキストテスト"""
        result = get_trend_text('decreasing')
        assert result == '減少傾向'
    
    def test_format_alert_summary_empty(self):
        """警戒情報なしのフォーマットテスト"""
        result = format_alert_summary([])
        assert result == '- なし'
    
    def test_format_alert_summary_single(self):
        """警戒情報1件のフォーマットテスト"""
        alerts = [
            {
                'timestamp': '11/20 15:30',
                'type': 'cpu',
                'message': 'CPU使用率が高いです'
            }
        ]
        result = format_alert_summary(alerts)
        assert '11/20 15:30' in result
        assert 'CPU使用率が高いです' in result
    
    def test_format_alert_summary_multiple(self):
        """警戒情報複数件のフォーマットテスト"""
        alerts = [
            {'timestamp': '11/20 15:30', 'type': 'cpu', 'message': 'CPU使用率が高いです'},
            {'timestamp': '11/21 10:00', 'type': 'mem', 'message': 'メモリ使用率が高いです'},
            {'timestamp': '11/22 03:15', 'type': 'log', 'message': 'ログ急増を検出'}
        ]
        result = format_alert_summary(alerts)
        assert '11/20 15:30' in result
        assert '11/21 10:00' in result
        assert '11/22 03:15' in result
    
    def test_format_alert_summary_truncate_long_message(self):
        """長いメッセージの省略テスト"""
        long_message = 'これは非常に長いメッセージです。' * 10
        alerts = [
            {'timestamp': '11/20 15:30', 'type': 'cpu', 'message': long_message}
        ]
        result = format_alert_summary(alerts)
        assert '...' in result
        assert len(result) < len(long_message)
    
    def test_format_alert_summary_max_five(self):
        """最大5件表示のテスト"""
        alerts = [
            {'timestamp': f'11/{i:02d} 10:00', 'type': 'cpu', 'message': f'Alert {i}'}
            for i in range(1, 11)  # 10件作成
        ]
        result = format_alert_summary(alerts)
        
        # 最初の5件が含まれること
        assert '11/01 10:00' in result
        assert '11/05 10:00' in result
        
        # 6件目以降は含まれないこと
        assert '11/06 10:00' not in result
        
        # 省略表示があること
        assert '他 5 件' in result
    
    def test_format_weekly_report_structure(self):
        """週次レポート全体のフォーマット構造テスト"""
        data = {
            'period': {
                'start': '2025-11-18',
                'end': '2025-11-24'
            },
            'resources': {
                'cpu': {'current': 45.2, 'previous': 43.1, 'change': 2.1, 'trend': 'stable'},
                'mem': {'current': 62.8, 'previous': 64.3, 'change': -1.5, 'trend': 'stable'},
                'disk': {'current': 68.5, 'previous': 65.3, 'change': 3.2, 'trend': 'increasing'}
            },
            'alerts': []
        }
        
        result = format_weekly_report(data)
        
        # ヘッダー
        assert '📊 週次健全性レポート' in result
        assert '2025-11-18' in result
        assert '2025-11-24' in result
        
        # セクション
        assert '【リソース状況】' in result
        assert '【今週の警戒情報】' in result
        assert '【トレンド】' in result
        
        # リソース情報
        assert 'CPU使用率: 45.2%' in result
        assert 'メモリ使用率: 62.8%' in result
        assert 'ディスク使用率: 68.5%' in result
        
        # トレンド
        assert '✅' in result  # stable
        assert '⚠️' in result  # increasing
        
        # フッター
        assert '異常がなくても、定期的に確認しておくと安心ですね' in result
    
    def test_format_weekly_report_with_alerts(self):
        """警戒情報ありの週次レポートテスト"""
        data = {
            'period': {'start': '2025-11-18', 'end': '2025-11-24'},
            'resources': {
                'cpu': {'current': 85.0, 'previous': 50.0, 'change': 70.0, 'trend': 'increasing'},
                'mem': {'current': 60.0, 'previous': 60.0, 'change': 0.0, 'trend': 'stable'},
                'disk': {'current': 70.0, 'previous': 70.0, 'change': 0.0, 'trend': 'stable'}
            },
            'alerts': [
                {'timestamp': '11/20 15:30', 'type': 'cpu', 'message': 'CPU使用率が高いです'}
            ]
        }
        
        result = format_weekly_report(data)
        
        assert '11/20 15:30' in result
        assert 'CPU使用率が高いです' in result
        assert '- なし' not in result
