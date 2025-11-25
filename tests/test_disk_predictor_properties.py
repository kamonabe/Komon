"""
ディスク使用量予測のプロパティベーステスト

hypothesisを使用して、予測ロジックの正確性を検証します。
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, date, timedelta

from komon.disk_predictor import (
    calculate_daily_average,
    predict_disk_trend,
    detect_rapid_change,
    format_prediction_message
)


# ========================================
# Property 1: 日次平均計算の正確性
# ========================================

@given(
    st.lists(
        st.tuples(
            st.datetimes(
                min_value=datetime(2025, 1, 1),
                max_value=datetime(2025, 12, 31)
            ),
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
        ),
        min_size=1,
        max_size=50
    )
)
@settings(max_examples=100)
def test_property_daily_average_accuracy(data):
    """
    **Feature: disk-trend-prediction, Property 1: 日次平均計算の正確性**
    
    任意の7日分のディスク使用率データに対して、日次平均を計算した結果は、
    各日のデータの算術平均と一致しなければならない
    
    **検証要件: 1.1**
    """
    # 日次平均を計算
    daily_averages = calculate_daily_average(data)
    
    # 手動で日次平均を計算して検証
    daily_data = {}
    for dt, usage in data:
        day = dt.date()
        if day not in daily_data:
            daily_data[day] = []
        daily_data[day].append(usage)
    
    # 各日の平均が正しいことを確認
    for day, avg_usage in daily_averages:
        expected_avg = sum(daily_data[day]) / len(daily_data[day])
        assert abs(avg_usage - expected_avg) < 0.0001, \
            f"日次平均が一致しません: {avg_usage} != {expected_avg}"
    
    # 全ての日が含まれていることを確認
    assert len(daily_averages) == len(daily_data), \
        f"日数が一致しません: {len(daily_averages)} != {len(daily_data)}"



# ========================================
# Property 2: 欠損データの処理
# ========================================

@given(
    st.lists(
        st.tuples(
            st.dates(min_value=date(2025, 1, 1), max_value=date(2025, 12, 31)),
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
        ),
        min_size=2,
        max_size=30
    )
)
@settings(max_examples=100)
def test_property_missing_data_handling(daily_data):
    """
    **Feature: disk-trend-prediction, Property 2: 欠損データの処理**
    
    任意の欠損を含むディスク使用率データに対して、予測は利用可能なデータのみを
    使用して実行され、欠損データは無視されなければならない
    
    **検証要件: 1.4**
    """
    # 欠損がある場合でも予測が実行されることを確認
    # （欠損は日付の連続性が途切れることで表現される）
    
    # データが2件以上あれば予測が実行される
    if len(daily_data) >= 2:
        try:
            result = predict_disk_trend(daily_data)
            # 予測結果が返されることを確認
            assert 'slope' in result
            assert 'intercept' in result
            assert 'current_usage' in result
            assert 'trend' in result
        except Exception as e:
            # データが不正な場合を除き、エラーは発生しないはず
            pytest.fail(f"予測計算でエラーが発生しました: {e}")



# ========================================
# Property 3: 線形回帰の正確性
# ========================================

@given(
    slope=st.floats(min_value=-3.0, max_value=3.0, allow_nan=False, allow_infinity=False),
    intercept=st.floats(min_value=20.0, max_value=80.0, allow_nan=False, allow_infinity=False),
    num_points=st.integers(min_value=3, max_value=20)
)
@settings(max_examples=100)
def test_property_linear_regression_accuracy(slope, intercept, num_points):
    """
    **Feature: disk-trend-prediction, Property 3: 線形回帰の正確性**
    
    任意のデータセットに対して、最小二乗法で計算された傾きと切片は
    数学的に正しい値でなければならない
    
    **検証要件: 2.1**
    """
    # 既知の傾きと切片を持つデータを生成
    base_date = date(2025, 11, 1)
    data = []
    
    # データが0-100%の範囲内に収まるようにする
    valid_data = True
    for i in range(num_points):
        day = base_date + timedelta(days=i)
        # y = slope * x + intercept
        usage = slope * i + intercept
        
        # 範囲外のデータが多い場合はスキップ
        if usage < 0 or usage > 100:
            valid_data = False
            break
        
        data.append((day, usage))
    
    # 有効なデータのみテスト
    if not valid_data or len(data) < 2:
        return
    
    # 予測を実行
    result = predict_disk_trend(data)
    
    # 傾きが期待値に近いことを確認（許容誤差: 0.1）
    assert abs(result['slope'] - slope) < 0.1, \
        f"傾きが一致しません: {result['slope']} != {slope}"
    
    # 切片が期待値に近いことを確認（許容誤差: 1.0）
    assert abs(result['intercept'] - intercept) < 1.0, \
        f"切片が一致しません: {result['intercept']} != {intercept}"



# ========================================
# Property 4: 90%到達予測の正確性
# ========================================

@given(
    initial_usage=st.floats(min_value=50.0, max_value=75.0, allow_nan=False, allow_infinity=False),
    slope=st.floats(min_value=0.5, max_value=3.0, allow_nan=False, allow_infinity=False),
    num_days=st.integers(min_value=3, max_value=10)
)
@settings(max_examples=100)
def test_property_90_percent_prediction_accuracy(initial_usage, slope, num_days):
    """
    **Feature: disk-trend-prediction, Property 4: 90%到達予測の正確性**
    
    任意の増加傾向（傾き > 0）のデータに対して、90%到達予測日は
    (90 - current_usage) / slope の計算式で算出された日数と一致しなければならない
    
    **検証要件: 2.2**
    """
    # 増加傾向のデータを生成
    base_date = date(2025, 11, 1)
    data = []
    
    for i in range(num_days):
        day = base_date + timedelta(days=i)
        usage = initial_usage + slope * i
        usage = min(88.0, usage)  # 90%未満に保つ（余裕を持たせる）
        data.append((day, usage))
    
    # 予測を実行
    result = predict_disk_trend(data)
    
    # 傾きが正であることを確認
    assert result['slope'] > 0, f"増加傾向のデータで傾きが正でない: {result['slope']}"
    
    # 現在の使用率が90%未満であることを確認
    if result['current_usage'] < 90.0:
        # 90%到達予測日が計算されていることを確認
        if result['days_to_90'] is not None:
            # 期待値を計算
            expected_days = (90.0 - result['current_usage']) / result['slope']
            
            # 予測日数が期待値に近いことを確認（許容誤差: 2日）
            assert abs(result['days_to_90'] - expected_days) <= 2, \
                f"予測日数が一致しません: {result['days_to_90']} != {expected_days}"



# ========================================
# Property 5: 前日比計算の正確性
# ========================================

@given(
    st.lists(
        st.tuples(
            st.dates(min_value=date(2025, 1, 1), max_value=date(2025, 12, 31)),
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
        ),
        min_size=2,
        max_size=30
    )
)
@settings(max_examples=100)
def test_property_day_over_day_calculation_accuracy(daily_data):
    """
    **Feature: disk-trend-prediction, Property 5: 前日比計算の正確性**
    
    任意の2日以上のデータに対して、前日比は最新日と前日のディスク使用率の
    差分と一致しなければならない
    
    **検証要件: 3.1**
    """
    # データをソート
    sorted_data = sorted(daily_data, key=lambda x: x[0])
    
    # 急激な変化を検出
    result = detect_rapid_change(sorted_data)
    
    # 前日比が正しく計算されていることを確認
    if len(sorted_data) >= 2:
        expected_change = sorted_data[-1][1] - sorted_data[-2][1]
        assert abs(result['change_percent'] - expected_change) < 0.0001, \
            f"前日比が一致しません: {result['change_percent']} != {expected_change}"
        
        assert abs(result['previous_usage'] - sorted_data[-2][1]) < 0.0001
        assert abs(result['current_usage'] - sorted_data[-1][1]) < 0.0001



# ========================================
# Property 6: 急激な変化検出の正確性
# ========================================

@given(
    previous_usage=st.floats(min_value=0.0, max_value=90.0, allow_nan=False, allow_infinity=False),
    change=st.floats(min_value=-20.0, max_value=20.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_property_rapid_change_detection_accuracy(previous_usage, change):
    """
    **Feature: disk-trend-prediction, Property 6: 急激な変化検出の正確性**
    
    任意の前日比データに対して、10%以上の増加の場合はis_rapid=True、
    10%未満の場合はis_rapid=Falseでなければならない
    
    **検証要件: 3.2, 3.3**
    """
    current_usage = previous_usage + change
    current_usage = max(0.0, min(100.0, current_usage))
    
    data = [
        (date(2025, 11, 24), previous_usage),
        (date(2025, 11, 25), current_usage)
    ]
    
    result = detect_rapid_change(data)
    
    # 実際の変化量
    actual_change = current_usage - previous_usage
    
    # 10%以上の増加の場合、is_rapid=True
    if actual_change >= 10.0:
        assert result['is_rapid'] is True, \
            f"10%以上の増加でis_rapidがTrueでない: {actual_change}%"
    else:
        assert result['is_rapid'] is False, \
            f"10%未満の増加でis_rapidがFalseでない: {actual_change}%"



# ========================================
# Property 7: 予測メッセージの完全性
# ========================================

@given(
    current_usage=st.floats(min_value=50.0, max_value=89.0, allow_nan=False, allow_infinity=False),
    slope=st.floats(min_value=-2.0, max_value=5.0, allow_nan=False, allow_infinity=False),
    is_rapid=st.booleans(),
    change_percent=st.floats(min_value=-20.0, max_value=20.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_property_message_completeness(current_usage, slope, is_rapid, change_percent):
    """
    **Feature: disk-trend-prediction, Property 7: 予測メッセージの完全性**
    
    任意の予測結果に対して、生成されるメッセージは以下の要素を含まなければならない：
    - 増加トレンドの説明（傾きまたはトレンド）
    - 90%到達予測日が存在する場合は「あとN日で90%に到達」
    - 急激な変化が検出された場合は「急激な増加」の警告
    - 警告がある場合は推奨アクション
    
    **検証要件: 4.1, 4.2, 4.3, 4.4**
    """
    # 予測結果を構築
    prediction = {
        'slope': slope,
        'intercept': 50.0,
        'current_usage': current_usage,
        'days_to_90': None,
        'prediction_date': None,
        'trend': 'increasing' if slope > 0.01 else ('decreasing' if slope < -0.01 else 'stable')
    }
    
    # 90%到達予測を計算
    if slope > 0.001 and current_usage < 90.0:
        try:
            days_float = (90.0 - current_usage) / slope
            if days_float < 36500 and days_float == days_float:  # 100年未満かつNaNでない
                prediction['days_to_90'] = int(days_float)
                prediction['prediction_date'] = '2025-12-01'
        except (OverflowError, ValueError):
            # オーバーフローやエラーの場合は予測なし
            pass
    
    # 急激な変化の結果を構築
    rapid_change = {
        'is_rapid': is_rapid and change_percent >= 10.0,
        'change_percent': change_percent,
        'previous_usage': current_usage - change_percent,
        'current_usage': current_usage
    }
    
    # メッセージを生成
    message = format_prediction_message(prediction, rapid_change)
    
    # 検証1: 増加トレンドの説明が含まれる（急激な変化や90%到達予測がない場合）
    if not rapid_change['is_rapid'] and prediction['days_to_90'] is None:
        assert '増加率' in message or '減少率' in message or 'トレンド' in message or '安定' in message, \
            "メッセージにトレンドの説明が含まれていない"
    
    # 検証2: 90%到達予測日が存在する場合、メッセージに含まれる
    if prediction['days_to_90'] is not None:
        assert '90%に到達' in message or '90%' in message, \
            "90%到達予測がメッセージに含まれていない"
        assert f"{prediction['days_to_90']}日" in message, \
            "予測日数がメッセージに含まれていない"
    
    # 検証3: 急激な変化が検出された場合、警告が含まれる
    if rapid_change['is_rapid']:
        assert '急激' in message or '⚠️' in message, \
            "急激な変化の警告がメッセージに含まれていない"
    
    # 検証4: 警告がある場合、推奨アクションが含まれる
    if rapid_change['is_rapid'] or prediction['days_to_90'] is not None:
        if prediction['days_to_90'] is not None:
            assert '推奨アクション' in message or 'journalctl' in message, \
                "推奨アクションがメッセージに含まれていない"



# ========================================
# Property 8: 警告の優先度順表示
# ========================================

@given(
    has_rapid_change=st.booleans(),
    has_90_prediction=st.booleans()
)
@settings(max_examples=100)
def test_property_warning_priority_order(has_rapid_change, has_90_prediction):
    """
    **Feature: disk-trend-prediction, Property 8: 警告の優先度順表示**
    
    任意の複数の警告を含む予測結果に対して、メッセージは優先度の高い順
    （急激な変化 > 90%到達予測 > 通常の増加）に表示されなければならない
    
    **検証要件: 5.5**
    """
    # 予測結果を構築
    prediction = {
        'slope': 1.0,
        'intercept': 50.0,
        'current_usage': 75.0,
        'days_to_90': 15 if has_90_prediction else None,
        'prediction_date': '2025-12-10' if has_90_prediction else None,
        'trend': 'increasing'
    }
    
    # 急激な変化の結果を構築
    rapid_change = {
        'is_rapid': has_rapid_change,
        'change_percent': 12.0 if has_rapid_change else 2.0,
        'previous_usage': 63.0 if has_rapid_change else 73.0,
        'current_usage': 75.0
    }
    
    # メッセージを生成
    message = format_prediction_message(prediction, rapid_change)
    
    # 優先度順に表示されることを確認
    if has_rapid_change and has_90_prediction:
        # 急激な変化が最初に表示される
        rapid_index = message.find('急激')
        prediction_index = message.find('90%に到達')
        
        if rapid_index >= 0 and prediction_index >= 0:
            assert rapid_index < prediction_index, \
                "急激な変化が90%到達予測より後に表示されている"
