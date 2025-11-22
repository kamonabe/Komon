"""
週次データ収集モジュールのプロパティベーステスト

hypothesisを使用して、様々な入力値での正確性を検証します。
"""

import pytest
from hypothesis import given, strategies as st

from komon.weekly_data import analyze_trend


class TestWeeklyDataProperties:
    """週次データ収集のプロパティベーステスト"""
    
    @given(
        current=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        previous=st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False)
    )
    def test_trend_analysis_consistency(self, current, previous):
        """
        トレンド分析の一貫性をテスト
        
        Property: 同じ入力に対して常に同じ結果を返すこと
        """
        result1 = analyze_trend(current, previous)
        result2 = analyze_trend(current, previous)
        
        assert result1 == result2
        assert result1 in ['stable', 'increasing', 'decreasing']
    
    @given(
        current=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        previous=st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False),
        threshold=st.floats(min_value=1, max_value=50, allow_nan=False, allow_infinity=False)
    )
    def test_trend_threshold_boundaries(self, current, previous, threshold):
        """
        トレンド閾値の境界条件をテスト
        
        Property: 閾値に基づいて正しく分類されること
        """
        change_percent = ((current - previous) / previous) * 100
        result = analyze_trend(current, previous, threshold)
        
        if change_percent >= threshold:
            assert result == 'increasing'
        elif change_percent <= -threshold:
            assert result == 'decreasing'
        else:
            assert result == 'stable'
    
    @given(value=st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False))
    def test_trend_same_values_stable(self, value):
        """
        同じ値の場合は常にstableになることをテスト
        
        Property: current == previous の場合、変化率は0%でstable
        """
        result = analyze_trend(value, value)
        assert result == 'stable'
    
    @given(
        previous=st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False),
        increase_factor=st.floats(min_value=1.1, max_value=2.0, allow_nan=False, allow_infinity=False)
    )
    def test_trend_increasing_detection(self, previous, increase_factor):
        """
        増加トレンドの検出をテスト
        
        Property: current > previous * 1.05 の場合、increasing
        """
        current = previous * increase_factor
        result = analyze_trend(current, previous, threshold=5.0)
        
        # 10%以上増加している場合は必ずincreasing
        if increase_factor >= 1.1:
            assert result == 'increasing'
    
    @given(
        previous=st.floats(min_value=10, max_value=100, allow_nan=False, allow_infinity=False),
        decrease_factor=st.floats(min_value=0.5, max_value=0.9, allow_nan=False, allow_infinity=False)
    )
    def test_trend_decreasing_detection(self, previous, decrease_factor):
        """
        減少トレンドの検出をテスト
        
        Property: current < previous * 0.95 の場合、decreasing
        """
        current = previous * decrease_factor
        result = analyze_trend(current, previous, threshold=5.0)
        
        # 10%以上減少している場合は必ずdecreasing
        if decrease_factor <= 0.9:
            assert result == 'decreasing'
    
    def test_trend_zero_previous_stable(self):
        """
        previous=0の場合はstableを返すことをテスト
        
        Property: ゼロ除算を避け、stableを返す
        """
        result = analyze_trend(50.0, 0.0)
        assert result == 'stable'
