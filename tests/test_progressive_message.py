"""
段階的通知メッセージのユニットテスト
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta

from src.komon.progressive_message import (
    get_notification_count,
    generate_progressive_message,
    DEFAULT_TEMPLATES,
    METRIC_NAMES,
    METRIC_UNITS
)


class TestGetNotificationCount(unittest.TestCase):
    """get_notification_count()のテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.queue_file = self.temp_file.name
        self.temp_file.close()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.queue_file):
            os.unlink(self.queue_file)
    
    def test_no_notifications(self):
        """通知なし（0件）"""
        # 空の履歴
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 0)
    
    def test_single_notification(self):
        """通知あり（1件）"""
        now = datetime.now()
        history = [{
            "timestamp": now.isoformat(),
            "metric_type": "cpu",
            "metric_value": 80.0,
            "message": "Test"
        }]
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 1)
    
    def test_multiple_notifications(self):
        """通知あり（複数件）"""
        now = datetime.now()
        history = []
        for i in range(3):
            history.append({
                "timestamp": (now - timedelta(hours=i)).isoformat(),
                "metric_type": "cpu",
                "metric_value": 80.0,
                "message": "Test"
            })
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 3)
    
    def test_time_window_exclusion(self):
        """時間窓外の通知は除外"""
        now = datetime.now()
        history = [
            # 時間窓内
            {
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "metric_type": "cpu",
                "metric_value": 80.0,
                "message": "Recent"
            },
            # 時間窓外
            {
                "timestamp": (now - timedelta(hours=25)).isoformat(),
                "metric_type": "cpu",
                "metric_value": 80.0,
                "message": "Old"
            }
        ]
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 1)
    
    def test_different_metric_type_exclusion(self):
        """異なるメトリクスタイプは除外"""
        now = datetime.now()
        history = [
            {
                "timestamp": now.isoformat(),
                "metric_type": "cpu",
                "metric_value": 80.0,
                "message": "CPU"
            },
            {
                "timestamp": now.isoformat(),
                "metric_type": "mem",
                "metric_value": 80.0,
                "message": "Memory"
            }
        ]
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        cpu_count = get_notification_count("cpu", 24, self.queue_file)
        mem_count = get_notification_count("mem", 24, self.queue_file)
        
        self.assertEqual(cpu_count, 1)
        self.assertEqual(mem_count, 1)
    
    def test_file_not_found(self):
        """ファイルが存在しない場合"""
        count = get_notification_count("cpu", 24, "/tmp/non_existent.json")
        self.assertEqual(count, 0)
    
    def test_corrupted_file(self):
        """破損したファイル"""
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            f.write("invalid json {{{")
        
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 0)
    
    def test_invalid_timestamp(self):
        """不正なタイムスタンプはスキップ"""
        now = datetime.now()
        history = [
            {
                "timestamp": "invalid-timestamp",
                "metric_type": "cpu",
                "metric_value": 80.0,
                "message": "Invalid"
            },
            {
                "timestamp": now.isoformat(),
                "metric_type": "cpu",
                "metric_value": 80.0,
                "message": "Valid"
            }
        ]
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        count = get_notification_count("cpu", 24, self.queue_file)
        self.assertEqual(count, 1)  # 有効なエントリのみカウント


class TestGenerateProgressiveMessage(unittest.TestCase):
    """generate_progressive_message()のテスト"""
    
    def test_first_notification(self):
        """1回目の通知"""
        message = generate_progressive_message("cpu", 85.5, 90.0, 1)
        
        self.assertIn("ちょっと気になる", message)
        self.assertIn("CPU使用率", message)
        self.assertIn("85.5", message)
        self.assertIn("%", message)
    
    def test_second_notification(self):
        """2回目の通知"""
        message = generate_progressive_message("mem", 82.3, 90.0, 2)
        
        self.assertIn("まだ続いてます", message)
        self.assertIn("メモリ使用率", message)
        self.assertIn("82.3", message)
    
    def test_third_notification(self):
        """3回目の通知"""
        message = generate_progressive_message("disk", 88.7, 90.0, 3)
        
        self.assertIn("そろそろ見た方がいいかも", message)
        self.assertIn("ディスク使用率", message)
        self.assertIn("88.7", message)
    
    def test_fourth_notification_uses_third_template(self):
        """4回目以降は3回目のテンプレートを使用"""
        message = generate_progressive_message("cpu", 90.0, 90.0, 4)
        
        self.assertIn("そろそろ見た方がいいかも", message)
    
    def test_custom_templates(self):
        """カスタムテンプレート"""
        custom_templates = {
            1: "カスタム1: {metric_name} {value}{unit}",
            2: "カスタム2: {metric_name} {value}{unit}",
            3: "カスタム3: {metric_name} {value}{unit}"
        }
        
        message = generate_progressive_message(
            "cpu", 85.0, 90.0, 1, templates=custom_templates
        )
        
        self.assertIn("カスタム1", message)
        self.assertIn("CPU使用率", message)
        self.assertIn("85.0", message)
    
    def test_all_metric_types(self):
        """全てのメトリクスタイプ"""
        for metric_type in ["cpu", "mem", "disk"]:
            message = generate_progressive_message(metric_type, 80.0, 90.0, 1)
            
            self.assertIsInstance(message, str)
            self.assertGreater(len(message), 0)
            self.assertIn(METRIC_NAMES[metric_type], message)
            self.assertIn("80.0", message)
            self.assertIn(METRIC_UNITS[metric_type], message)
    
    def test_error_handling(self):
        """エラーハンドリング"""
        # 不正なテンプレート
        invalid_templates = {
            1: "Invalid template without placeholders"
        }
        
        # エラーが発生してもメッセージは生成される
        message = generate_progressive_message(
            "cpu", 85.0, 90.0, 1, templates=invalid_templates
        )
        
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)


class TestDefaultTemplates(unittest.TestCase):
    """デフォルトテンプレートのテスト"""
    
    def test_default_templates_exist(self):
        """デフォルトテンプレートが存在する"""
        self.assertIn(1, DEFAULT_TEMPLATES)
        self.assertIn(2, DEFAULT_TEMPLATES)
        self.assertIn(3, DEFAULT_TEMPLATES)
    
    def test_default_templates_have_placeholders(self):
        """デフォルトテンプレートにプレースホルダーが含まれる"""
        for template in DEFAULT_TEMPLATES.values():
            self.assertIn("{metric_name}", template)
            self.assertIn("{value}", template)
            self.assertIn("{unit}", template)


class TestMetricMappings(unittest.TestCase):
    """メトリクスマッピングのテスト"""
    
    def test_metric_names_exist(self):
        """メトリクス名が定義されている"""
        self.assertIn("cpu", METRIC_NAMES)
        self.assertIn("mem", METRIC_NAMES)
        self.assertIn("disk", METRIC_NAMES)
    
    def test_metric_units_exist(self):
        """メトリクス単位が定義されている"""
        self.assertIn("cpu", METRIC_UNITS)
        self.assertIn("mem", METRIC_UNITS)
        self.assertIn("disk", METRIC_UNITS)


if __name__ == '__main__':
    unittest.main()
