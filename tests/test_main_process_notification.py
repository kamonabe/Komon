"""
main.pyのプロセス情報付き通知機能のテスト
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# scriptsディレクトリをパスに追加
scripts_path = Path(__file__).parent.parent / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

import main


class TestProcessNotification:
    """プロセス情報付き通知のテスト"""
    
    def test_get_process_info_for_cpu(self):
        """CPU用プロセス情報取得のテスト"""
        usage = {
            "cpu_by_process": [
                {"name": "python", "cpu": 25.5},
                {"name": "node", "cpu": 15.2},
                {"name": "docker", "cpu": 8.7}
            ]
        }
        
        result = main._get_process_info_for_metric("cpu", usage)
        
        expected = "1. python: 25.5%\n2. node: 15.2%\n3. docker: 8.7%"
        assert result == expected
    
    def test_get_process_info_for_memory(self):
        """メモリ用プロセス情報取得のテスト"""
        usage = {
            "mem_by_process": [
                {"name": "chrome", "mem": 512.3},
                {"name": "python", "mem": 256.1},
                {"name": "node", "mem": 128.7}
            ]
        }
        
        result = main._get_process_info_for_metric("memory", usage)
        
        expected = "1. chrome: 512.3MB\n2. python: 256.1MB\n3. node: 128.7MB"
        assert result == expected
    
    def test_get_process_info_for_disk(self):
        """ディスク用プロセス情報取得のテスト（空文字を返す）"""
        usage = {}
        
        result = main._get_process_info_for_metric("disk", usage)
        
        assert result == ""
    
    def test_get_process_info_empty_data(self):
        """プロセス情報が空の場合のテスト"""
        usage = {"cpu_by_process": []}
        
        result = main._get_process_info_for_metric("cpu", usage)
        
        assert result == ""
    
    def test_is_metric_alert_cpu(self):
        """CPU関連アラートの判定テスト"""
        alert = "CPU使用率が高いです: 85.5%"
        
        result = main._is_metric_alert(alert, "cpu")
        
        assert result is True
    
    def test_is_metric_alert_memory(self):
        """メモリ関連アラートの判定テスト"""
        alert = "メモリ使用率が高いです: 92.3%"
        
        result = main._is_metric_alert(alert, "memory")
        
        assert result is True
    
    def test_is_metric_alert_disk(self):
        """ディスク関連アラートの判定テスト"""
        alert = "ディスク使用率が高いです: 95.2%"
        
        result = main._is_metric_alert(alert, "disk")
        
        assert result is True
    
    def test_is_metric_alert_no_match(self):
        """関連しないアラートの判定テスト"""
        alert = "CPU使用率が高いです: 85.5%"
        
        result = main._is_metric_alert(alert, "memory")
        
        assert result is False


class TestHandleAlertsWithProcessInfo:
    """プロセス情報付きアラート処理のテスト"""
    
    @patch('main.send_notification_with_fallback')
    @patch('main.NotificationThrottle')
    def test_handle_alerts_includes_process_info(self, mock_throttle_class, mock_send_fallback):
        """アラート処理にプロセス情報が含まれることを確認"""
        # モックの設定
        mock_throttle = MagicMock()
        mock_throttle.should_send_notification.return_value = (True, "first")
        mock_throttle_class.return_value = mock_throttle
        mock_send_fallback.return_value = True
        
        # テストデータ
        alerts = ["CPU使用率が高いです: 85.5%"]
        levels = {"cpu": ("warning", 85.5)}
        config = {
            "throttle": {},
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/test"}
            }
        }
        usage = {
            "cpu_by_process": [
                {"name": "python", "cpu": 45.2},
                {"name": "node", "cpu": 25.1},
                {"name": "docker", "cpu": 15.2}
            ]
        }
        
        # 実行
        main.handle_alerts(alerts, levels, config, usage)
        
        # 検証
        mock_send_fallback.assert_called_once()
        call_args = mock_send_fallback.call_args
        message = call_args.kwargs['message']
        
        # メッセージにプロセス情報が含まれることを確認
        assert "📊 上位プロセス:" in message
        assert "1. python: 45.2%" in message
        assert "2. node: 25.1%" in message
        assert "3. docker: 15.2%" in message
    
    @patch('main.send_notification_with_fallback')
    @patch('main.NotificationThrottle')
    def test_handle_alerts_memory_with_process_info(self, mock_throttle_class, mock_send_fallback):
        """メモリアラートにプロセス情報が含まれることを確認"""
        # モックの設定
        mock_throttle = MagicMock()
        mock_throttle.should_send_notification.return_value = (True, "first")
        mock_throttle_class.return_value = mock_throttle
        mock_send_fallback.return_value = True
        
        # テストデータ
        alerts = ["メモリ使用率が高いです: 92.3%"]
        levels = {"memory": ("alert", 92.3)}
        config = {
            "throttle": {},
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/test"}
            }
        }
        usage = {
            "mem_by_process": [
                {"name": "chrome", "mem": 1024.5},
                {"name": "python", "mem": 512.3},
                {"name": "node", "mem": 256.1}
            ]
        }
        
        # 実行
        main.handle_alerts(alerts, levels, config, usage)
        
        # 検証
        mock_send_fallback.assert_called_once()
        call_args = mock_send_fallback.call_args
        message = call_args.kwargs['message']
        
        # メッセージにプロセス情報が含まれることを確認
        assert "📊 上位プロセス:" in message
        assert "1. chrome: 1024.5MB" in message
        assert "2. python: 512.3MB" in message
        assert "3. node: 256.1MB" in message
    
    @patch('main.send_notification_with_fallback')
    @patch('main.NotificationThrottle')
    def test_handle_alerts_disk_no_process_info(self, mock_throttle_class, mock_send_fallback):
        """ディスクアラートにはプロセス情報が含まれないことを確認"""
        # モックの設定
        mock_throttle = MagicMock()
        mock_throttle.should_send_notification.return_value = (True, "first")
        mock_throttle_class.return_value = mock_throttle
        mock_send_fallback.return_value = True
        
        # テストデータ
        alerts = ["ディスク使用率が高いです: 95.2%"]
        levels = {"disk": ("critical", 95.2)}
        config = {
            "throttle": {},
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/test"}
            }
        }
        usage = {}
        
        # 実行
        main.handle_alerts(alerts, levels, config, usage)
        
        # 検証
        mock_send_fallback.assert_called_once()
        call_args = mock_send_fallback.call_args
        message = call_args.kwargs['message']
        
        # ディスクの場合はプロセス情報が含まれないことを確認
        assert "📊 上位プロセス:" not in message
    
    @patch('main.send_notification_with_fallback')
    @patch('main.NotificationThrottle')
    def test_handle_alerts_no_process_data(self, mock_throttle_class, mock_send_fallback):
        """プロセスデータがない場合の処理"""
        # モックの設定
        mock_throttle = MagicMock()
        mock_throttle.should_send_notification.return_value = (True, "first")
        mock_throttle_class.return_value = mock_throttle
        mock_send_fallback.return_value = True
        
        # テストデータ
        alerts = ["CPU使用率が高いです: 85.5%"]
        levels = {"cpu": ("warning", 85.5)}
        config = {
            "throttle": {},
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "https://hooks.slack.com/test"}
            }
        }
        usage = {}  # プロセス情報なし
        
        # 実行
        main.handle_alerts(alerts, levels, config, usage)
        
        # 検証
        mock_send_fallback.assert_called_once()
        call_args = mock_send_fallback.call_args
        message = call_args.kwargs['message']
        
        # プロセス情報がない場合は追加されないことを確認
        assert "📊 上位プロセス:" not in message