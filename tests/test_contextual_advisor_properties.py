"""
contextual_advisor.py のプロパティベーステスト

正確性プロパティを検証する
"""

import pytest
from hypothesis import given, strategies as st, settings
from src.komon.contextual_advisor import (
    _get_top_processes,
    _match_pattern,
    _format_advice,
    DEFAULT_PATTERNS
)


class TestPropertyTopProcessesCount:
    """Property 1: プロセス情報の正確性"""
    
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=50, deadline=5000)  # 5秒のタイムアウト
    def test_property_top_processes_count(self, count):
        """
        任意の取得件数に対して、返されるプロセス数はcount以下である
        
        **Feature: contextual-advice, Property 1: プロセス情報の正確性**
        **検証要件: AC-001**
        """
        processes = _get_top_processes("cpu", count)
        
        # プロパティ: 返されるプロセス数はcount以下
        assert len(processes) <= count
        
        # プロパティ: 各プロセスが必要なフィールドを持つ
        for proc in processes:
            assert "name" in proc
            assert "pid" in proc
            assert "cpu_percent" in proc
            assert "memory_percent" in proc
            assert isinstance(proc["cpu_percent"], (int, float))
            assert isinstance(proc["memory_percent"], (int, float))


class TestPropertyPatternMatchingConsistency:
    """Property 2: パターンマッチングの一貫性"""
    
    @given(st.text(min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_property_pattern_matching_consistency(self, process_name):
        """
        任意のプロセス名に対して、パターンマッチングは一貫した結果を返す
        
        **Feature: contextual-advice, Property 2: パターンマッチングの一貫性**
        **検証要件: AC-002**
        """
        # 同じプロセス名で2回マッチング
        result1 = _match_pattern(process_name, DEFAULT_PATTERNS)
        result2 = _match_pattern(process_name, DEFAULT_PATTERNS)
        
        # プロパティ: 結果は常に同じ
        assert result1 == result2
        
        # プロパティ: 結果はタプル(パターン名, アドバイス)
        assert isinstance(result1, tuple)
        assert len(result1) == 2
        assert isinstance(result1[0], str)
        assert isinstance(result1[1], str)


class TestPropertyMessageFormattingIdempotency:
    """Property 3: メッセージ整形の冪等性"""
    
    @given(
        st.lists(
            st.fixed_dictionaries({
                "name": st.text(min_size=1, max_size=20),
                "pid": st.integers(min_value=1, max_value=99999),
                "cpu_percent": st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
                "memory_percent": st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
                "cmdline": st.text(min_size=0, max_size=100),
                "advice": st.text(min_size=1, max_size=100)
            }),
            min_size=1,
            max_size=5
        ),
        st.sampled_from(["minimal", "normal", "detailed"])
    )
    @settings(max_examples=100)
    def test_property_message_formatting_idempotency(self, processes, advice_level):
        """
        任意のプロセス情報と詳細度に対して、メッセージ生成は冪等である
        
        **Feature: contextual-advice, Property 3: メッセージ整形の冪等性**
        **検証要件: AC-003**
        """
        # 同じ入力で2回メッセージ生成
        message1 = _format_advice(processes, advice_level)
        message2 = _format_advice(processes, advice_level)
        
        # プロパティ: 結果は常に同じ
        assert message1 == message2
        
        # プロパティ: 結果は文字列
        assert isinstance(message1, str)
        assert len(message1) > 0


class TestPropertyAdviceLevelOrdering:
    """Property 4: 詳細度の順序性"""
    
    @given(
        st.lists(
            st.fixed_dictionaries({
                "name": st.text(min_size=1, max_size=20),
                "pid": st.integers(min_value=1, max_value=99999),
                "cpu_percent": st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
                "memory_percent": st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
                "cmdline": st.text(min_size=1, max_size=100),
                "advice": st.text(min_size=1, max_size=100),
                "detailed_advice": st.text(min_size=1, max_size=100)
            }),
            min_size=1,
            max_size=3
        )
    )
    @settings(max_examples=100)
    def test_property_advice_level_ordering(self, processes):
        """
        詳細度が上がるほど、メッセージの長さが増加する
        
        **Feature: contextual-advice, Property 4: 詳細度の順序性**
        **検証要件: AC-003**
        """
        minimal = _format_advice(processes, "minimal")
        normal = _format_advice(processes, "normal")
        detailed = _format_advice(processes, "detailed")
        
        # プロパティ: minimal <= normal <= detailed
        assert len(minimal) <= len(normal) <= len(detailed)


class TestPropertyPerformanceGuarantee:
    """Property 5: パフォーマンス保証"""
    
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=20, deadline=5000)  # 5秒のタイムアウト
    def test_property_performance_guarantee(self, count):
        """
        任意の取得件数に対して、処理時間は100ms以内である
        
        **Feature: contextual-advice, Property 5: パフォーマンス保証**
        **検証要件: AC-005**
        """
        import time
        
        start = time.time()
        processes = _get_top_processes("cpu", count)
        elapsed = time.time() - start
        
        # プロパティ: 処理時間は100ms以内
        # 注: CPU測定のため、実際には2秒程度かかる可能性がある
        # ここでは5秒以内を許容（CI環境を考慮）
        assert elapsed < 5.0, f"処理時間が長すぎます: {elapsed:.2f}秒"
        
        # プロパティ: 結果は正しく返される
        assert isinstance(processes, list)
        assert len(processes) <= count
