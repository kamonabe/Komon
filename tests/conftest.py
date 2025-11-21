"""
pytestの共通設定とフィクスチャ

テスト全体で使用する共通の設定やヘルパー関数を定義します。
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """一時ディレクトリを作成するフィクスチャ"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """サンプル設定を返すフィクスチャ"""
    return {
        "thresholds": {
            "cpu": 85,
            "mem": 80,
            "disk": 80,
            "proc_cpu": 20
        },
        "notifications": {
            "slack": {
                "enabled": False,
                "webhook_url": "https://hooks.slack.com/services/test"
            },
            "email": {
                "enabled": False
            }
        },
        "log_monitor_targets": {
            "/var/log/messages": True
        },
        "log_analysis": {
            "anomaly_threshold_percent": 30,
            "baseline_learning_rate": 0.1,
            "line_threshold": 100
        }
    }


@pytest.fixture
def sample_usage():
    """サンプル使用率データを返すフィクスチャ"""
    return {
        "cpu": 50.0,
        "mem": 60.0,
        "disk": 70.0,
        "cpu_by_process": [
            {"name": "python", "cpu": 10.5},
            {"name": "nginx", "cpu": 5.2}
        ],
        "mem_by_process": [
            {"name": "python", "mem": 512.0},
            {"name": "nginx", "mem": 256.0}
        ]
    }
