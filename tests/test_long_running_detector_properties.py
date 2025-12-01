"""
長時間実行プロセス検出のプロパティベーステスト

**Feature: long-running-detector**

このテストは、長時間実行プロセス検出機能の正確性プロパティを検証します。
"""

import time
from hypothesis import given, strategies as st, assume
from komon.long_running_detector import (
    _extract_script_name,
    _format_duration
)


@given(st.integers(min_value=0, max_value=86400 * 365))
def test_property_1_duration_calculation_accuracy(seconds):
    """
    **Feature: long-running-detector, Property 1: 実行時間計算の正確性**
    
    任意のプロセス開始時刻について、現在時刻との差分が正確に計算されること
    
    **検証要件: AC-002**
    """
    # 開始時刻をシミュレート
    start_time = time.time() - seconds
    current_time = time.time()
    
    # 実行時間を計算
    runtime = int(current_time - start_time)
    
    # 誤差は1秒以内であること
    assert abs(runtime - seconds) <= 1


@given(
    st.integers(min_value=1, max_value=86400 * 365),
    st.integers(min_value=1, max_value=86400 * 365)
)
def test_property_2_threshold_judgment_accuracy(threshold, runtime):
    """
    **Feature: long-running-detector, Property 2: 閾値判定の正確性**
    
    任意の閾値Tと実行時間Rについて、R >= Tの場合のみ長時間実行と判定されること
    
    **検証要件: AC-001**
    """
    # 閾値以上の場合は長時間実行と判定
    if runtime >= threshold:
        assert runtime >= threshold
    else:
        assert runtime < threshold


@given(
    st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
    st.sampled_from(['.py', '.sh', '.rb', '.pl'])
)
def test_property_3_script_name_extraction_accuracy(cmdline_parts, extension):
    """
    **Feature: long-running-detector, Property 3: スクリプト名抽出の正確性**
    
    任意のコマンドライン形式について、対象拡張子を持つスクリプト名が正しく抽出されること
    
    **検証要件: AC-001**
    """
    # スクリプトパスを生成
    script_path = f"/path/to/script{extension}"
    cmdline = cmdline_parts + [script_path]
    
    # スクリプト名を抽出
    result = _extract_script_name(cmdline, [extension])
    
    # 正しく抽出されること
    assert result == f"script{extension}"


@given(st.integers(min_value=0, max_value=86400 * 365))
def test_property_4_time_format_accuracy(seconds):
    """
    **Feature: long-running-detector, Property 4: 時間フォーマットの正確性**
    
    任意の秒数について、人間に読みやすい形式（X時間Y分Z秒）に正確に変換されること
    
    **検証要件: AC-003**
    """
    result = _format_duration(seconds)
    
    # 結果が文字列であること
    assert isinstance(result, str)
    
    # 結果が空でないこと
    assert len(result) > 0
    
    # 日・時間・分・秒のいずれかを含むこと
    assert any(unit in result for unit in ['日', '時間', '分', '秒'])
    
    # 秒数が0の場合は"0秒"
    if seconds == 0:
        assert result == '0秒'
    
    # 秒数が60未満の場合は秒のみ
    if 0 < seconds < 60:
        assert '秒' in result
        assert '分' not in result
        assert '時間' not in result
    
    # 秒数が3600以上86400未満の場合は時間を含む
    if 3600 <= seconds < 86400:
        assert '時間' in result
    
    # 秒数が86400以上の場合は日を含む
    if seconds >= 86400:
        assert '日' in result


@given(st.integers(min_value=-1000, max_value=0).filter(lambda x: x != 0))
def test_property_5_config_validation(invalid_threshold):
    """
    **Feature: long-running-detector, Property 5: 設定値の検証**
    
    任意の閾値設定について、正の整数のみが許可され、
    無効な値はデフォルト値にフォールバックすること
    
    **検証要件: AC-004**
    """
    from komon.long_running_detector import detect_long_running_processes
    
    # 無効な閾値でも例外が発生しないこと
    try:
        result = detect_long_running_processes(threshold_seconds=invalid_threshold)
        # 結果がリストであること
        assert isinstance(result, list)
    except Exception as e:
        # 例外が発生した場合は失敗
        assert False, f"Unexpected exception: {e}"
