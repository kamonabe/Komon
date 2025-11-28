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
        """ディスク用プロセス情報取得のテスト（空文字列を返す）"""
        usage = {"cpu_by_process": [], "mem_by_process": []}
        
        result = main._get_process_info_for_metric("disk", usage)
        
        assert result == ""
    
    def test_get_process_info_empty_processes(self):
        """プロセス情報が空の場合のテスト"""
        usage = {"cpu_by_process": [], "mem_by_process": []}
        
        cpu_result = main._get_process_info_for_metric("cpu", usage)
        memory_result = main._get_process_info_for_metric("memory", usage)
        
        assert cpu_result == ""
        assert memory_result == ""
    
    def test_get_process_info_missing_data(self):
        """プロセス情報が存在しない場合のテスト"""
        usage = {}
        
        cpu_result = main._get_process_info_for_metric("cpu", usage)
        memory_result = main._get_process_info_for_metric("memory", usage)
        
        assert cpu_result == ""
        assert memory_result == ""
    
    def test_get_process_info_more_than_three_processes(self):
        """3個以上のプロセスがある場合、上位3個のみ表示"""
        usage = {
            "cpu_by_process": [
                {"name": "proc1", "cpu": 30.0},
                {"name": "proc2", "cpu": 25.0},
                {"name": "proc3", "cpu": 20.0},
                {"name": "proc4", "cpu": 15.0},
                {"name": "proc5", "cpu": 10.0}
            ]
        }
        
        result = main._get_process_info_for_metric("cpu", usage)
        
        expected = "1. proc1: 30.0%\n2. proc2: 25.0%\n3. proc3: 20.0%"
        assert result == expected
        # proc4, proc5は含まれない
        assert "proc4" not in result
        assert "proc5" not in result


class TestHandleAlertsWithProcessInfo:
    """プロセス情報付きアラート処理のテスト"""
    
    @patch('main.send_slack_alert')
    @patch('main.NotificationThrottle')
    def test_handle_alerts_includes_process_info(self, mock_throttle_class, mock_send_slack):
        """アラート処理にプロセス情報が含まれることを確認"""
        # モックの設定
        mock_throttle = MagicMock()
        mock_throttle.should_send_notification.return_value = (True, "first")
        mock_throttle_class.return_value = mock_throttle
        mock_send_slack.return_value = True
        
        # テストデータ
        alerts = ["CPU使用率が高いです: 85.5%"]
        levels = {"cpu": ("warning", 85.5)}
        config = {
            "throttle": {},
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "test-url"}
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
        mock_send_slack.assert_called_once()
        call_args = mock_send_slack.call_args[0]
        message = call_args[0]
        
        # メッセージにプロセス情報が含まれることを確認
        assert "📊 上位プロセス:" in message
        assert "1. python: 45.2%" in message
        assert "2. node: 25.1%" in message
        assert "3. docker: 15.2%" in message
    
    @patch('main.send_slack_alert')
    @patch('main.NotificationThrottle')
    def test_handle_alerts_memory_with_process_info(self, mock_throttle_class, mock_send_slack):
        """メモリアラートにプロセス情報が含まれることを確認"""
        # モックの設定
        mock_throttle = MagicMock()
        mock_throttle.should_send_notification.return_value = (True, "first")
        mock_throttle_class.return_value = mock_throttle
        mock_send_slack.return_value = True
        
        # テストデータ
        alerts = ["メモリ使用率が高いです: 92.3%"]
        levels = {"memory": ("alert", 92.3)}
        config = {
            "throttle": {},
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "test-url"}
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
        mock_send_slack.assert_called_once()
        call_args = mock_send_slack.call_args[0]
        message = call_args[0]
        
        # メッセージにプロセス情報が含まれることを確認
        assert "📊 上位プロセス:" in message
        assert "1. chrome: 1024.5MB" in message
        assert "2. python: 512.3MB" in message
        assert "3. node: 256.1MB" in message
    
    @patch('main.send_slack_alert')
    @patch('main.NotificationThrottle')
    def test_handle_alerts_disk_no_process_info(self, mock_throttle_class, mock_send_slack):
        """ディスクアラートにはプロセス情報が含まれないことを確認"""
        # モックの設定
        mock_throttle = MagicMock()
        mock_throttle.should_send_notification.return_value = (True, "first")
        mock_throttle_class.return_value = mock_throttle
        mock_send_slack.return_value = True
        
        # テストデータ
        alerts = ["ディスク使用率が高いです: 95.2%"]
        levels = {"disk": ("critical", 95.2)}
        config = {
            "throttle": {},
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "test-url"}
            }
        }
        usage = {}
        
        # 実行
        main.handle_alerts(alerts, levels, config, usage)
        
        # 検証
        mock_send_slack.assert_called_once()
        call_args = mock_send_slack.call_args[0]
        message = call_args[0]
        
        # ディスクの場合はプロセス情報が含まれないことを確認
        assert "📊 上位プロセス:" not in message
    
    @patch('main.send_slack_alert')
    @patch('main.NotificationThrottle')
    def test_handle_alerts_no_process_data(self, mock_throttle_class, mock_send_slack):
        """プロセスデータがない場合の処理"""
        # モックの設定
        mock_throttle = MagicMock()
        mock_throttle.should_send_notification.return_value = (True, "first")
        mock_throttle_class.return_value = mock_throttle
        mock_send_slack.return_value = True
        
        # テストデータ
        alerts = ["CPU使用率が高いです: 85.5%"]
        levels = {"cpu": ("warning", 85.5)}
        config = {
            "throttle": {},
            "notifications": {
                "slack": {"enabled": True, "webhook_url": "test-url"}
            }
        }
        usage = {}  # プロセス情報なし
        
        # 実行
        main.handle_alerts(alerts, levels, config, usage)
        
        # 検証
        mock_send_slack.assert_called_once()
        call_args = mock_send_slack.call_args[0]
        message = call_args[0]
        
        # プロセス情報がない場合は追加されないことを確認
        assert "📊 上位プロセス:" not in message