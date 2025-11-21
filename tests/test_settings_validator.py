"""
settings_validator.py のテスト

設定ファイル検証機能のテストを行います。
"""

import pytest
import os
import yaml
from pathlib import Path
from komon.settings_validator import validate_settings


@pytest.fixture
def temp_settings_file(tmp_path):
    """テスト用の一時設定ファイル"""
    settings_path = tmp_path / "test_settings.yml"
    return settings_path


class TestValidateSettings:
    """validate_settings関数のテスト"""
    
    def test_valid_minimal_settings(self, temp_settings_file):
        """最小限の有効な設定ファイル"""
        config = {
            "thresholds": {
                "cpu": 85,
                "mem": 80,
                "disk": 75
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is True
    
    def test_valid_full_settings(self, temp_settings_file):
        """完全な有効な設定ファイル"""
        config = {
            "thresholds": {
                "cpu": 85,
                "mem": 80,
                "disk": 75
            },
            "notifications": {
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/services/xxx"
                },
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.example.com",
                    "from": "komon@example.com",
                    "to": "admin@example.com"
                }
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is True
    
    def test_file_not_found(self):
        """設定ファイルが存在しない場合"""
        assert validate_settings("nonexistent.yml") is False
    
    def test_missing_thresholds_section(self, temp_settings_file):
        """thresholdsセクションが欠けている場合"""
        config = {
            "notifications": {
                "slack": {"enabled": False}
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is False
    
    def test_missing_cpu_threshold(self, temp_settings_file):
        """CPU閾値が欠けている場合"""
        config = {
            "thresholds": {
                "mem": 80,
                "disk": 75
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is False
    
    def test_invalid_threshold_value_negative(self, temp_settings_file):
        """閾値が負の値の場合"""
        config = {
            "thresholds": {
                "cpu": -10,
                "mem": 80,
                "disk": 75
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is False
    
    def test_invalid_threshold_value_over_100(self, temp_settings_file):
        """閾値が100を超える場合"""
        config = {
            "thresholds": {
                "cpu": 150,
                "mem": 80,
                "disk": 75
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is False
    
    def test_invalid_threshold_type(self, temp_settings_file):
        """閾値が数値でない場合"""
        config = {
            "thresholds": {
                "cpu": "high",
                "mem": 80,
                "disk": 75
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is False
    
    def test_slack_enabled_without_webhook(self, temp_settings_file):
        """Slack通知が有効だがwebhook_urlが無い場合"""
        config = {
            "thresholds": {
                "cpu": 85,
                "mem": 80,
                "disk": 75
            },
            "notifications": {
                "slack": {
                    "enabled": True
                }
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is False
    
    def test_slack_disabled_without_webhook(self, temp_settings_file):
        """Slack通知が無効でwebhook_urlが無い場合（OK）"""
        config = {
            "thresholds": {
                "cpu": 85,
                "mem": 80,
                "disk": 75
            },
            "notifications": {
                "slack": {
                    "enabled": False
                }
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is True
    
    def test_email_enabled_without_smtp_server(self, temp_settings_file):
        """メール通知が有効だがsmtp_serverが無い場合"""
        config = {
            "thresholds": {
                "cpu": 85,
                "mem": 80,
                "disk": 75
            },
            "notifications": {
                "email": {
                    "enabled": True,
                    "from": "komon@example.com",
                    "to": "admin@example.com"
                }
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is False
    
    def test_email_enabled_without_from(self, temp_settings_file):
        """メール通知が有効だがfromが無い場合"""
        config = {
            "thresholds": {
                "cpu": 85,
                "mem": 80,
                "disk": 75
            },
            "notifications": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.example.com",
                    "to": "admin@example.com"
                }
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is False
    
    def test_invalid_yaml_syntax(self, temp_settings_file):
        """YAML構文エラーの場合"""
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: syntax: error:")
        
        assert validate_settings(str(temp_settings_file)) is False
    
    def test_float_threshold_values(self, temp_settings_file):
        """閾値が小数の場合（有効）"""
        config = {
            "thresholds": {
                "cpu": 85.5,
                "mem": 80.2,
                "disk": 75.8
            }
        }
        
        with open(temp_settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        assert validate_settings(str(temp_settings_file)) is True
