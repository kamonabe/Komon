"""
ログ末尾抽出モジュールのユニットテスト
"""

import os
import tempfile
import pytest
from komon.log_tail_extractor import extract_log_tail


class TestExtractLogTail:
    """extract_log_tail関数のユニットテスト"""
    
    def test_extract_normal_case(self):
        """
        正常系: 指定行数を正しく抽出できる
        
        **検証要件: AC-001**
        """
        # テストファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            for i in range(20):
                f.write(f"Line {i+1}\n")
            temp_path = f.name
        
        try:
            # 末尾10行を抽出
            result = extract_log_tail(temp_path, 10)
            
            # 検証
            assert len(result) == 10
            assert result[0] == "Line 11"
            assert result[-1] == "Line 20"
        finally:
            os.unlink(temp_path)
    
    def test_extract_file_not_found(self):
        """
        異常系: ファイルが存在しない場合、FileNotFoundErrorを発生させる
        
        **検証要件: AC-005**
        """
        with pytest.raises(FileNotFoundError):
            extract_log_tail("/nonexistent/file.log", 10)
    
    def test_extract_permission_denied(self, tmp_path):
        """
        異常系: 読み込み権限がない場合、PermissionErrorを発生させる
        
        **検証要件: AC-005**
        """
        # テストファイルを作成
        test_file = tmp_path / "test.log"
        test_file.write_text("Line 1\nLine 2\n")
        
        # 読み込み権限を削除
        os.chmod(test_file, 0o000)
        
        try:
            with pytest.raises(PermissionError):
                extract_log_tail(str(test_file), 10)
        finally:
            # 権限を戻す（クリーンアップのため）
            os.chmod(test_file, 0o644)
    
    def test_extract_empty_file(self, tmp_path):
        """
        エッジケース: ファイルが空の場合、空リストを返す
        
        **検証要件: AC-005**
        """
        # 空ファイルを作成
        test_file = tmp_path / "empty.log"
        test_file.write_text("")
        
        result = extract_log_tail(str(test_file), 10)
        
        assert result == []
    
    def test_extract_fewer_lines_than_requested(self, tmp_path):
        """
        エッジケース: ファイルの行数が指定行数より少ない場合、全行を返す
        
        **検証要件: AC-001**
        """
        # 5行のファイルを作成
        test_file = tmp_path / "short.log"
        test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        
        # 10行を要求
        result = extract_log_tail(str(test_file), 10)
        
        # 5行しか返らない
        assert len(result) == 5
        assert result[0] == "Line 1"
        assert result[-1] == "Line 5"
    
    def test_extract_long_line_truncation(self, tmp_path):
        """
        長い行の切り詰め: 1行が最大文字数を超える場合、切り詰められる
        
        **検証要件: AC-004**
        """
        # 長い行を含むファイルを作成
        test_file = tmp_path / "long.log"
        long_line = "A" * 1000
        test_file.write_text(f"{long_line}\nShort line\n")
        
        # 最大100文字で抽出
        result = extract_log_tail(str(test_file), 10, max_line_length=100)
        
        # 検証
        assert len(result) == 2
        assert len(result[0]) <= 100 + len(" ... (truncated)")
        assert " ... (truncated)" in result[0]
        assert result[1] == "Short line"
    
    def test_extract_zero_lines(self, tmp_path):
        """
        エッジケース: 0行を要求した場合、空リストを返す
        
        **検証要件: AC-001**
        """
        test_file = tmp_path / "test.log"
        test_file.write_text("Line 1\nLine 2\n")
        
        result = extract_log_tail(str(test_file), 0)
        
        assert result == []
    
    def test_extract_negative_lines(self, tmp_path):
        """
        エッジケース: 負の行数を要求した場合、空リストを返す
        
        **検証要件: AC-001**
        """
        test_file = tmp_path / "test.log"
        test_file.write_text("Line 1\nLine 2\n")
        
        result = extract_log_tail(str(test_file), -5)
        
        assert result == []
