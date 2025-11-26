"""
段階的通知メッセージの統合テスト

実際の使用シナリオに基づいて、段階的メッセージ機能が
正しく動作することを検証します。
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta

from src.komon.progressive_message import get_notification_count, generate_progressive_message
from src.komon.analyzer import analyze_usage
from src.komon.notification_history import save_notification


class TestProgressiveNotificationIntegration(unittest.TestCase):
    """段階的通知メッセージの統合テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.queue_file = self.temp_file.name
        self.temp_file.close()
        
        # 空の履歴ファイルを作成
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.queue_file):
            os.unlink(self.queue_file)
    
    def test_scenario_first_notification(self):
        """
        シナリオ1: 初回通知
        
        通知履歴が空の状態で閾値超過が発生した場合、
        1回目のメッセージが生成されること
        """
        # 通知回数を取得（履歴が空なので0）
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 0)
        
        # 1回目のメッセージを生成
        message = generate_progressive_message("cpu", 85.5, 90.0, count + 1)
        
        # 検証
        self.assertIn("ちょっと気になる", message)
        self.assertIn("CPU使用率", message)
        self.assertIn("85.5", message)
    
    def test_scenario_second_notification(self):
        """
        シナリオ2: 2回目通知
        
        1回目の通知後、再度閾値超過が発生した場合、
        2回目のメッセージが生成されること
        """
        # 1回目の通知を履歴に保存
        now = datetime.now()
        history = [{
            "timestamp": (now - timedelta(hours=1)).isoformat(),
            "metric_type": "cpu",
            "metric_value": 85.0,
            "message": "First notification"
        }]
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        # 通知回数を取得（1回）
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 1)
        
        # 2回目のメッセージを生成
        message = generate_progressive_message("cpu", 86.0, 90.0, count + 1)
        
        # 検証
        self.assertIn("まだ続いてます", message)
        self.assertIn("CPU使用率", message)
        self.assertIn("86.0", message)
    
    def test_scenario_third_and_beyond_notification(self):
        """
        シナリオ3: 3回目以降の通知
        
        2回目の通知後、さらに閾値超過が発生した場合、
        3回目のメッセージが生成されること
        """
        # 2回の通知を履歴に保存
        now = datetime.now()
        history = [
            {
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "metric_type": "cpu",
                "metric_value": 85.0,
                "message": "First notification"
            },
            {
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "metric_type": "cpu",
                "metric_value": 86.0,
                "message": "Second notification"
            }
        ]
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        # 通知回数を取得（2回）
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 2)
        
        # 3回目のメッセージを生成
        message = generate_progressive_message("cpu", 87.0, 90.0, count + 1)
        
        # 検証
        self.assertIn("そろそろ見た方がいいかも", message)
        self.assertIn("CPU使用率", message)
        self.assertIn("87.0", message)
        
        # 4回目以降も同じメッセージ
        message_4th = generate_progressive_message("cpu", 88.0, 90.0, 4)
        self.assertIn("そろそろ見た方がいいかも", message_4th)
    
    def test_scenario_time_window_reset(self):
        """
        シナリオ4: 時間窓リセット
        
        24時間以上通知がなかった場合、
        次の通知は1回目として扱われること
        """
        # 24時間以上前の通知を履歴に保存
        now = datetime.now()
        history = [{
            "timestamp": (now - timedelta(hours=25)).isoformat(),
            "metric_type": "cpu",
            "metric_value": 85.0,
            "message": "Old notification"
        }]
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        # 通知回数を取得（時間窓外なので0）
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 0)
        
        # 1回目のメッセージが生成される
        message = generate_progressive_message("cpu", 85.5, 90.0, count + 1)
        self.assertIn("ちょっと気になる", message)
    
    def test_scenario_different_metrics_independent(self):
        """
        シナリオ5: 異なるメトリクスの独立カウント
        
        異なるメトリクスタイプの通知は独立してカウントされること
        """
        # CPU、メモリ、ディスクの通知を履歴に保存
        now = datetime.now()
        history = [
            # CPU: 2回
            {
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "metric_type": "cpu",
                "metric_value": 85.0,
                "message": "CPU 1"
            },
            {
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "metric_type": "cpu",
                "metric_value": 86.0,
                "message": "CPU 2"
            },
            # メモリ: 1回
            {
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "metric_type": "mem",
                "metric_value": 82.0,
                "message": "Memory 1"
            },
            # ディスク: 3回
            {
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "metric_type": "disk",
                "metric_value": 88.0,
                "message": "Disk 1"
            },
            {
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "metric_type": "disk",
                "metric_value": 89.0,
                "message": "Disk 2"
            },
            {
                "timestamp": (now - timedelta(hours=3)).isoformat(),
                "metric_type": "disk",
                "metric_value": 90.0,
                "message": "Disk 3"
            }
        ]
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        # 各メトリクスの通知回数を取得
        cpu_count = get_notification_count("cpu", 24, self.queue_file)
        mem_count = get_notification_count("mem", 24, self.queue_file)
        disk_count = get_notification_count("disk", 24, self.queue_file)
        
        # 検証: 独立してカウントされる
        self.assertEqual(cpu_count, 2)
        self.assertEqual(mem_count, 1)
        self.assertEqual(disk_count, 3)
        
        # 各メトリクスで適切なメッセージが生成される
        cpu_message = generate_progressive_message("cpu", 87.0, 90.0, cpu_count + 1)
        mem_message = generate_progressive_message("mem", 83.0, 90.0, mem_count + 1)
        disk_message = generate_progressive_message("disk", 91.0, 90.0, disk_count + 1)
        
        self.assertIn("そろそろ見た方がいいかも", cpu_message)  # 3回目
        self.assertIn("まだ続いてます", mem_message)  # 2回目
        self.assertIn("そろそろ見た方がいいかも", disk_message)  # 4回目（3回目のテンプレート）
    
    def test_integration_with_analyzer(self):
        """
        Analyzerモジュールとの統合テスト
        
        analyze_usage()が段階的メッセージを正しく生成すること
        """
        # 閾値設定
        thresholds = {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90}
        }
        
        # 使用率データ（CPU閾値超過）
        usage = {
            "cpu": 87.0,
            "mem": 60.0,
            "disk": 50.0
        }
        
        # 段階的メッセージを使用して分析
        alerts = analyze_usage(usage, thresholds, use_progressive=True)
        
        # 検証: アラートが生成される
        self.assertEqual(len(alerts), 1)
        self.assertIn("CPU使用率", alerts[0])


if __name__ == '__main__':
    unittest.main()
