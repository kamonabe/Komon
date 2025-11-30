"""
ログ末尾抽出機能の統合テスト
"""

import os
import tempfile
import yaml
import pytest


class TestLogTailIntegration:
    """ログ末尾抽出機能の統合テスト"""
    
    def test_end_to_end_with_config(self, tmp_path):
        """
        エンドツーエンドの動作確認: 設定ファイルから末尾抽出まで
        
        **検証要件: AC-001, AC-002, AC-003**
        """
        from komon.log_tail_extractor import extract_log_tail
        
        # 設定ファイルを作成
        config_file = tmp_path / "test_settings.yml"
        config = {
            "log_analysis": {
                "tail_lines": 5,
                "max_line_length": 100
            }
        }
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # テストログファイルを作成
        log_file = tmp_path / "test.log"
        with open(log_file, 'w') as f:
            for i in range(20):
                f.write(f"Log line {i+1}\n")
        
        # 設定を読み込む
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        tail_lines = loaded_config["log_analysis"]["tail_lines"]
        max_line_length = loaded_config["log_analysis"]["max_line_length"]
        
        # ログ末尾を抽出
        result = extract_log_tail(str(log_file), tail_lines, max_line_length)
        
        # 検証
        assert len(result) == 5
        assert result[0] == "Log line 16"
        assert result[-1] == "Log line 20"
    
    def test_notification_message_format(self, tmp_path):
        """
        通知メッセージのフォーマット確認
        
        **検証要件: AC-002**
        """
        from komon.log_tail_extractor import extract_log_tail
        
        # テストログファイルを作成
        log_file = tmp_path / "test.log"
        with open(log_file, 'w') as f:
            f.write("Error: Connection timeout\n")
            f.write("Error: Database unavailable\n")
            f.write("Warning: High memory usage\n")
        
        # ログ末尾を抽出
        tail_content = extract_log_tail(str(log_file), 3)
        
        # メッセージを作成
        alert = "ログが急増しています（+50行）"
        message_parts = [f"⚠️ {alert}"]
        message_parts.append(f"\n📄 ログファイル: {log_file}")
        message_parts.append(f"📋 末尾 {len(tail_content)} 行:")
        message_parts.append("```")
        message_parts.extend(tail_content)
        message_parts.append("```")
        message = "\n".join(message_parts)
        
        # 検証
        assert "ログが急増しています" in message
        assert str(log_file) in message
        assert "Error: Connection timeout" in message
        assert "```" in message
    
    def test_error_handling_file_not_found(self):
        """
        エラーハンドリング: ファイルが存在しない場合
        
        **検証要件: AC-005**
        """
        from komon.log_tail_extractor import extract_log_tail
        
        with pytest.raises(FileNotFoundError):
            extract_log_tail("/nonexistent/file.log", 10)
    
    def test_error_handling_empty_file(self, tmp_path):
        """
        エラーハンドリング: ファイルが空の場合
        
        **検証要件: AC-005**
        """
        from komon.log_tail_extractor import extract_log_tail
        
        # 空ファイルを作成
        log_file = tmp_path / "empty.log"
        log_file.write_text("")
        
        # 空リストが返る
        result = extract_log_tail(str(log_file), 10)
        assert result == []
    
    def test_large_file_performance(self, tmp_path):
        """
        大きなファイルのパフォーマンス確認
        
        **検証要件: NFR-001**
        """
        import time
        from komon.log_tail_extractor import extract_log_tail
        
        # 大きなファイルを作成（10万行）
        log_file = tmp_path / "large.log"
        with open(log_file, 'w') as f:
            for i in range(100000):
                f.write(f"Log line {i+1}\n")
        
        # 実行時間を計測
        start = time.time()
        result = extract_log_tail(str(log_file), 10)
        elapsed = time.time() - start
        
        # 検証
        assert len(result) == 10
        assert result[0] == "Log line 99991"
        assert result[-1] == "Log line 100000"
        assert elapsed < 1.0, f"Too slow: {elapsed:.2f} seconds"
    
    def test_config_tail_lines_zero_disables_feature(self, tmp_path):
        """
        設定でtail_lines=0の場合、末尾抜粋が無効化される
        
        **検証要件: AC-003**
        """
        from komon.log_tail_extractor import extract_log_tail
        
        # tail_lines=0の場合
        result = extract_log_tail(str(tmp_path / "dummy.log"), 0)
        
        # 空リストが返る（ファイルが存在しなくてもエラーにならない）
        assert result == []
