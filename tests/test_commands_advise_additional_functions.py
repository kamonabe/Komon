"""
src/komon/commands/advise.py の追加関数テスト

カバレッジ改善のため、未カバーの関数をテストします。
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import sys

from src.komon.commands.advise import (
    advise_disk_prediction,
    advise_network_check,
    advise_notification_history
)


class TestAdviseAdditionalFunctions(unittest.TestCase):
    """advise.pyの追加関数テスト"""
    
    @patch('komon.disk_predictor.load_disk_history')
    @patch('komon.disk_predictor.calculate_daily_average')
    @patch('komon.disk_predictor.predict_disk_trend')
    @patch('komon.disk_predictor.detect_rapid_change')
    @patch('komon.disk_predictor.format_prediction_message')
    def test_advise_disk_prediction_success(self, mock_format_message, mock_detect_rapid, 
                                          mock_predict_trend, mock_calculate_daily, mock_load_history):
        """ディスク予測成功のテスト"""
        # モックデータの設定
        mock_load_history.return_value = [
            {"date": "2023-01-01", "usage": 70.0},
            {"date": "2023-01-02", "usage": 72.0},
            {"date": "2023-01-03", "usage": 74.0}
        ]
        mock_calculate_daily.return_value = [70.0, 72.0, 74.0]
        mock_predict_trend.return_value = {"days_to_90": 30, "trend": "increasing"}
        mock_detect_rapid.return_value = False
        mock_format_message.return_value = "ディスク使用量は30日後に90%に達する予測です。"
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_disk_prediction()
        
        output = captured_output.getvalue()
        
        # 予測結果が表示されることを確認
        self.assertIn("ディスク使用量の予測", output)
        self.assertIn("30日後に90%に達する", output)
        
        # 各関数が呼ばれることを確認
        mock_load_history.assert_called_once_with(days=7)
        mock_calculate_daily.assert_called_once()
        mock_predict_trend.assert_called_once()
        mock_detect_rapid.assert_called_once()
        mock_format_message.assert_called_once()
    
    @patch('komon.disk_predictor.load_disk_history')
    def test_advise_disk_prediction_insufficient_data(self, mock_load_history):
        """データ不足時のテスト"""
        # データが不足している場合
        mock_load_history.return_value = [{"date": "2023-01-01", "usage": 70.0}]
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_disk_prediction()
        
        output = captured_output.getvalue()
        
        # データ不足メッセージが表示されることを確認
        self.assertIn("データが不足しています", output)
        self.assertIn("7日分のデータが必要", output)
    
    @patch('komon.disk_predictor.load_disk_history')
    def test_advise_disk_prediction_exception(self, mock_load_history):
        """例外発生時のテスト"""
        # 例外を発生させる
        mock_load_history.side_effect = Exception("File not found")
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_disk_prediction()
        
        output = captured_output.getvalue()
        
        # エラーメッセージが表示されることを確認
        self.assertIn("予測計算中にエラーが発生", output)
        self.assertIn("File not found", output)
    
    @patch('src.komon.commands.advise.NetworkStateManager')
    @patch('src.komon.commands.advise.check_ping')
    @patch('src.komon.commands.advise.check_http')
    def test_advise_network_check_enabled(self, mock_check_http, mock_check_ping, mock_state_manager_class):
        """ネットワークチェック有効時のテスト"""
        # モックの設定
        mock_state_manager = MagicMock()
        mock_state_manager_class.return_value = mock_state_manager
        mock_state_manager.check_state_change.return_value = "ok_to_ng"
        mock_state_manager.get_ng_count.return_value = 0
        
        mock_check_ping.return_value = False  # Ping失敗
        mock_check_http.return_value = False  # HTTP失敗
        
        config = {
            "network_check": {
                "enabled": True,
                "ping": {
                    "targets": [
                        {"host": "8.8.8.8", "description": "Google DNS"},
                        {"host": "1.1.1.1", "description": "Cloudflare DNS"}
                    ],
                    "timeout": 3
                },
                "http": {
                    "targets": [
                        {"url": "https://google.com", "description": "Google"},
                        {"url": "https://github.com", "method": "GET"}
                    ],
                    "timeout": 10
                }
            }
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_network_check(config)
        
        output = captured_output.getvalue()
        
        # ネットワークチェック結果が表示されることを確認
        self.assertIn("ネットワーク疎通チェック", output)
        self.assertIn("Ping失敗", output)
        self.assertIn("HTTP失敗", output)
        
        # 各チェック関数が呼ばれることを確認
        self.assertEqual(mock_check_ping.call_count, 2)
        self.assertEqual(mock_check_http.call_count, 2)
    
    def test_advise_network_check_disabled(self):
        """ネットワークチェック無効時のテスト"""
        config = {
            "network_check": {
                "enabled": False
            }
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_network_check(config)
        
        output = captured_output.getvalue()
        
        # 無効時は何も表示されないことを確認
        self.assertEqual(output, "")
    
    @patch('src.komon.commands.advise.NetworkStateManager')
    @patch('src.komon.commands.advise.check_ping')
    def test_advise_network_check_recovery(self, mock_check_ping, mock_state_manager_class):
        """ネットワーク復旧時のテスト"""
        # モックの設定
        mock_state_manager = MagicMock()
        mock_state_manager_class.return_value = mock_state_manager
        mock_state_manager.check_state_change.return_value = "ng_to_ok"  # 復旧
        mock_state_manager.get_ng_count.return_value = 0
        
        mock_check_ping.return_value = True  # Ping成功
        
        config = {
            "network_check": {
                "enabled": True,
                "ping": {
                    "targets": [{"host": "8.8.8.8", "description": "Google DNS"}]
                }
            }
        }
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_network_check(config)
        
        output = captured_output.getvalue()
        
        # 復旧メッセージが表示されることを確認
        self.assertIn("Ping復旧", output)
        self.assertIn("全て正常", output)
    
    @patch('src.komon.commands.advise.load_notification_history')
    def test_advise_notification_history_with_data(self, mock_load_history):
        """通知履歴表示（データあり）のテスト"""
        # モック履歴データ
        mock_history = [
            {
                "timestamp": "2023-01-01T10:00:00",
                "metric_type": "cpu",
                "message": "CPU使用率が高いです",
                "level": "warning"
            },
            {
                "timestamp": "2023-01-01T11:00:00", 
                "metric_type": "memory",
                "message": "メモリ使用率が高いです",
                "level": "alert"
            }
        ]
        mock_load_history.return_value = mock_history
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_notification_history(limit=5)
        
        output = captured_output.getvalue()
        
        # 履歴が表示されることを確認
        self.assertIn("通知履歴", output)
        self.assertIn("CPU使用率が高い", output)
        self.assertIn("メモリ使用率が高い", output)
        mock_load_history.assert_called_once_with(limit=5)
    
    @patch('src.komon.commands.advise.load_notification_history')
    def test_advise_notification_history_empty(self, mock_load_history):
        """通知履歴表示（データなし）のテスト"""
        mock_load_history.return_value = []
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_notification_history()
        
        output = captured_output.getvalue()
        
        # 履歴なしメッセージが表示されることを確認
        self.assertIn("通知履歴はありません", output)
        mock_load_history.assert_called_once_with(limit=None)
    
    @patch('src.komon.commands.advise.load_notification_history')
    def test_advise_notification_history_exception(self, mock_load_history):
        """通知履歴表示（例外発生）のテスト"""
        mock_load_history.side_effect = Exception("Database error")
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            advise_notification_history()
        
        output = captured_output.getvalue()
        
        # エラーメッセージが表示されることを確認
        self.assertIn("通知履歴の読み込みに失敗", output)
        self.assertIn("Database error", output)


if __name__ == '__main__':
    unittest.main()