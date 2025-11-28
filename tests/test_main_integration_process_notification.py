"""
main.pyのプロセス情報付き通知機能の統合テスト
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# scriptsディレクトリをパスに追加
scripts_path = Path(__file__).parent.parent / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

import main


class TestMainIntegrationProcessNotification:
    """main.pyのプロセス情報付き通知統合テスト"""
    
    @patch('main.collect_detailed_resource_usage')
    @patch('main.analyze_usage_with_levels')
    @patch('main.validate_threshold_config')
    @patch('main.rotate_history')
    @patch('main.save_current_usage')
    @patch('requests.post')
    def test_main_with_cpu_alert_and_process_info(
        self, 
        mock_post, 
        mock_save_usage, 
        mock_rotate, 
        mock_validate, 
        mock_analyze, 
        mock_collect,
        tmp_path
    ):
        """CPUアラート時にプロセス情報付きSlack通知が送信されることを確認"""
        
        # 設定ファイルを作成
        config_file = tmp_path / "settings.yml"
        config_content = """
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/test"

throttle:
  enabled: false

thresholds:
  cpu:
    warning: 70
    alert: 85
    critical: 95
"""
        config_file.write_text(config_content)
        
        # モックの設定
        mock_validate.return_value = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95}
        }
        
        mock_collect.return_value = {
            "cpu": 88.5,
            "mem": 45.2,
            "disk": 60.1,
            "cpu_by_process": [
                {"name": "python", "cpu": 35.2},
                {"name": "node", "cpu": 28.1},
                {"name": "docker", "cpu": 15.7}
            ],
            "mem_by_process": [
                {"name": "chrome", "mem": 512.3},
                {"name": "python", "mem": 256.1}
            ]
        }
        
        mock_analyze.return_value = (
            ["CPU使用率が高いです: 88.5%"],
            {"cpu": ("alert", 88.5)}
        )
        
        # Slack APIのモック
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # 履歴ファイルのパスを設定
        history_dir = tmp_path / "data" / "notifications"
        history_dir.mkdir(parents=True)
        
        # main関数を実行
        with patch('main.load_config') as mock_load_config:
            mock_load_config.return_value = {
                "notifications": {
                    "slack": {
                        "enabled": True,
                        "webhook_url": "https://hooks.slack.com/test"
                    }
                },
                "throttle": {"enabled": False},
                "thresholds": {
                    "cpu": {"warning": 70, "alert": 85, "critical": 95}
                }
            }
            
            with patch('komon.notification.NotificationThrottle') as mock_throttle_class:
                mock_throttle = MagicMock()
                mock_throttle.should_send_notification.return_value = (True, "first")
                mock_throttle_class.return_value = mock_throttle
                
                main.main()
        
        # Slack APIが呼び出されたことを確認
        mock_post.assert_called_once()
        
        # 送信されたメッセージを確認
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        message = payload['text']
        
        # 基本的なアラートメッセージが含まれることを確認
        assert "⚠️ Komon 警戒情報:" in message
        assert "CPU使用率が高いです: 88.5%" in message
        
        # プロセス情報が含まれることを確認
        assert "📊 上位プロセス:" in message
        assert "1. python: 35.2%" in message
        assert "2. node: 28.1%" in message
        assert "3. docker: 15.7%" in message
    
    @patch('main.collect_detailed_resource_usage')
    @patch('main.analyze_usage_with_levels')
    @patch('main.validate_threshold_config')
    @patch('main.rotate_history')
    @patch('main.save_current_usage')
    @patch('requests.post')
    def test_main_with_memory_alert_and_process_info(
        self, 
        mock_post, 
        mock_save_usage, 
        mock_rotate, 
        mock_validate, 
        mock_analyze, 
        mock_collect,
        tmp_path
    ):
        """メモリアラート時にプロセス情報付きSlack通知が送信されることを確認"""
        
        # モックの設定
        mock_validate.return_value = {
            "memory": {"warning": 70, "alert": 85, "critical": 95}
        }
        
        mock_collect.return_value = {
            "cpu": 45.2,
            "mem": 91.3,
            "disk": 60.1,
            "cpu_by_process": [
                {"name": "python", "cpu": 15.2}
            ],
            "mem_by_process": [
                {"name": "chrome", "mem": 1024.5},
                {"name": "python", "mem": 512.3},
                {"name": "node", "mem": 256.1}
            ]
        }
        
        mock_analyze.return_value = (
            ["メモリ使用率が高いです: 91.3%"],
            {"memory": ("alert", 91.3)}
        )
        
        # Slack APIのモック
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # main関数を実行
        with patch('main.load_config') as mock_load_config:
            mock_load_config.return_value = {
                "notifications": {
                    "slack": {
                        "enabled": True,
                        "webhook_url": "https://hooks.slack.com/test"
                    }
                },
                "throttle": {"enabled": False}
            }
            
            with patch('komon.notification.NotificationThrottle') as mock_throttle_class:
                mock_throttle = MagicMock()
                mock_throttle.should_send_notification.return_value = (True, "first")
                mock_throttle_class.return_value = mock_throttle
                
                main.main()
        
        # Slack APIが呼び出されたことを確認
        mock_post.assert_called_once()
        
        # 送信されたメッセージを確認
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        message = payload['text']
        
        # 基本的なアラートメッセージが含まれることを確認
        assert "⚠️ Komon 警戒情報:" in message
        assert "メモリ使用率が高いです: 91.3%" in message
        
        # プロセス情報が含まれることを確認
        assert "📊 上位プロセス:" in message
        assert "1. chrome: 1024.5MB" in message
        assert "2. python: 512.3MB" in message
        assert "3. node: 256.1MB" in message
    
    @patch('main.collect_detailed_resource_usage')
    @patch('main.analyze_usage_with_levels')
    @patch('main.validate_threshold_config')
    @patch('main.rotate_history')
    @patch('main.save_current_usage')
    @patch('requests.post')
    def test_main_with_disk_alert_no_process_info(
        self, 
        mock_post, 
        mock_save_usage, 
        mock_rotate, 
        mock_validate, 
        mock_analyze, 
        mock_collect,
        tmp_path
    ):
        """ディスクアラート時にプロセス情報が含まれないことを確認"""
        
        # モックの設定
        mock_validate.return_value = {
            "disk": {"warning": 70, "alert": 85, "critical": 95}
        }
        
        mock_collect.return_value = {
            "cpu": 45.2,
            "mem": 60.1,
            "disk": 96.7,
            "cpu_by_process": [],
            "mem_by_process": []
        }
        
        mock_analyze.return_value = (
            ["ディスク使用率が高いです: 96.7%"],
            {"disk": ("critical", 96.7)}
        )
        
        # Slack APIのモック
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # main関数を実行
        with patch('main.load_config') as mock_load_config:
            mock_load_config.return_value = {
                "notifications": {
                    "slack": {
                        "enabled": True,
                        "webhook_url": "https://hooks.slack.com/test"
                    }
                },
                "throttle": {"enabled": False}
            }
            
            with patch('komon.notification.NotificationThrottle') as mock_throttle_class:
                mock_throttle = MagicMock()
                mock_throttle.should_send_notification.return_value = (True, "first")
                mock_throttle_class.return_value = mock_throttle
                
                main.main()
        
        # Slack APIが呼び出されたことを確認
        mock_post.assert_called_once()
        
        # 送信されたメッセージを確認
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        message = payload['text']
        
        # 基本的なアラートメッセージが含まれることを確認
        assert "⚠️ Komon 警戒情報:" in message
        assert "ディスク使用率が高いです: 96.7%" in message
        
        # ディスクの場合はプロセス情報が含まれないことを確認
        assert "📊 上位プロセス:" not in message