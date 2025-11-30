"""
ログ末尾抽出モジュールのプロパティテスト
"""

import os
import tempfile
from hypothesis import given, strategies as st
from komon.log_tail_extractor import extract_log_tail


@given(st.lists(st.text(min_size=1).filter(lambda x: '\n' not in x and x.strip()), min_size=1, max_size=100))
def test_property_1_line_count_accuracy(lines):
    """
    **Feature: log-tail-excerpt, Property 1: 行数カウントの正確性**
    
    任意の行数のログに対して、抽出結果の行数は指定した行数と一致する
    （ファイルの行数が少ない場合を除く）
    
    **検証要件: AC-001**
    """
    # テストファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
        f.write('\n'.join(lines))
        temp_path = f.name
    
    try:
        requested_lines = 5
        result = extract_log_tail(temp_path, requested_lines)
        
        # ファイルの行数が少ない場合は全行、多い場合は指定行数
        expected_count = min(requested_lines, len(lines))
        assert len(result) == expected_count
    finally:
        os.unlink(temp_path)


@given(st.lists(st.text(min_size=1).filter(lambda x: '\n' not in x and x.strip()), min_size=10, max_size=100))
def test_property_2_tail_order(lines):
    """
    **Feature: log-tail-excerpt, Property 2: 末尾からの順序性**
    
    抽出された行は、ファイルの末尾から指定行数分を古い順に並べたものである
    （空白のみの行は除外される）
    
    **検証要件: AC-001**
    """
    # テストファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
        f.write('\n'.join(lines))
        temp_path = f.name
    
    try:
        requested_lines = 5
        result = extract_log_tail(temp_path, requested_lines)
        
        # 期待値: ファイルの末尾5行（rstrip適用後）
        expected = [line.rstrip() for line in lines[-requested_lines:]]
        assert result == expected
    finally:
        os.unlink(temp_path)


@given(st.lists(st.text(min_size=1, max_size=1000).filter(lambda x: '\n' not in x and x.strip()), min_size=1, max_size=10))
def test_property_3_line_truncation(lines):
    """
    **Feature: log-tail-excerpt, Property 3: 長い行の切り詰め**
    
    1行が最大文字数を超える場合、適切に切り詰められる
    
    **検証要件: AC-004**
    """
    # テストファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
        f.write('\n'.join(lines))
        temp_path = f.name
    
    try:
        max_length = 100
        result = extract_log_tail(temp_path, len(lines), max_length)
        
        # 全ての行が最大文字数以下（切り詰めメッセージを含む）
        for line in result:
            assert len(line) <= max_length + len(" ... (truncated)")
    finally:
        os.unlink(temp_path)
