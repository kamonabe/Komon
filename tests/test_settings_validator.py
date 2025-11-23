"""
設定バリデータのテスト

プロパティベーステストとユニットテストを含む。
"""

import pytest
from hypothesis import given, strategies as st

from src.komon.settings_validator import (
    validate_threshold_config,
    determine_threshold_level,
    ThresholdLevel,
    ValidationError,
    _normalize_single_threshold,
    _validate_three_tier,
)


# ========================================
# プロパティベーステスト
# ========================================

@given(
    warning=st.integers(min_value=0, max_value=90),
    gap1=st.integers(min_value=1, max_value=10),
    gap2=st.integers(min_value=1, max_value=10),
)
def test_prop_threshold_ordering(warning, gap1, gap2):
    """
    [PROP-001] 閾値の順序性
    
    任意の有効な3段階閾値について、warning < alert < critical が成立する。
    """
    alert = warning + gap1
    critical = alert + gap2
    
    thresholds = {
        "warning": warning,
        "alert": alert,
        "critical": critical,
    }
    
    validated = _validate_three_tier("test", thresholds)
    
    assert validated["warning"] < validated["alert"]
    assert validated["alert"] < validated["critical"]


@given(
    value=st.floats(min_value=-10, max_value=200),
    warning=st.integers(min_value=10, max_value=60),
    alert=st.integers(min_value=70, max_value=80),
    critical=st.integers(min_value=85, max_value=100),
)
def test_prop_level_determination(value, warning, alert, critical):
    """
    [PROP-002] レベル判定の正確性
    
    値Vと閾値(W, A, C)が与えられたとき、正しいレベルが判定される。
    """
    thresholds = {
        "warning": warning,
        "alert": alert,
        "critical": critical,
    }
    
    level = determine_threshold_level(value, thresholds)
    
    if value < 0:
        assert level == ThresholdLevel.NORMAL
    elif value >= critical:
        assert level == ThresholdLevel.CRITICAL
    elif value >= alert:
        assert level == ThresholdLevel.ALERT
    elif value >= warning:
        assert level == ThresholdLevel.WARNING
    else:
        assert level == ThresholdLevel.NORMAL


@given(threshold=st.integers(min_value=10, max_value=90))
def test_prop_backward_compatibility(threshold):
    """
    [PROP-003] 後方互換性
    
    従来の単一閾値Tは、3段階形式に正規化される。
    """
    normalized = _normalize_single_threshold(threshold)
    
    assert "warning" in normalized
    assert "alert" in normalized
    assert "critical" in normalized
    assert normalized["warning"] < normalized["alert"] < normalized["critical"]
    assert normalized["alert"] == threshold


# ========================================
# ユニットテスト
# ========================================

def test_valid_three_tier_config():
    """有効な3段階設定の読み込み"""
    config = {
        "thresholds": {
            "cpu": {"warning": 70, "alert": 80, "critical": 90},
            "mem": {"warning": 70, "alert": 80, "critical": 90},
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
    }
    
    result = validate_threshold_config(config)
    
    assert result["cpu"]["warning"] == 70
    assert result["cpu"]["alert"] == 80
    assert result["cpu"]["critical"] == 90


def test_legacy_single_threshold():
    """従来の単一閾値設定の後方互換性"""
    config = {
        "thresholds": {
            "cpu": 85,
            "mem": 80,
            "disk": 80,
        }
    }
    
    result = validate_threshold_config(config)
    
    # 単一閾値が3段階に正規化される
    assert result["cpu"]["alert"] == 85
    assert result["cpu"]["warning"] == 75  # 85 - 10
    assert result["cpu"]["critical"] == 95  # 85 + 10


def test_mixed_format():
    """3段階と単一値の混在設定"""
    config = {
        "thresholds": {
            "cpu": {"warning": 70, "alert": 85, "critical": 95},
            "mem": 80,  # 単一値
            "disk": {"warning": 70, "alert": 80, "critical": 90},
        }
    }
    
    result = validate_threshold_config(config)
    
    assert result["cpu"]["warning"] == 70
    assert result["mem"]["alert"] == 80
    assert result["disk"]["critical"] == 90


def test_invalid_ordering():
    """無効な順序の閾値設定"""
    config = {
        "thresholds": {
            "cpu": {"warning": 90, "alert": 80, "critical": 70},  # 逆順
        }
    }
    
    with pytest.raises(ValidationError, match="順序が無効"):
        validate_threshold_config(config)


def test_missing_key():
    """必須キーの欠落"""
    config = {
        "thresholds": {
            "cpu": {"warning": 70, "alert": 80},  # critical が欠落
        }
    }
    
    with pytest.raises(ValidationError, match="'critical' が指定されていません"):
        validate_threshold_config(config)


def test_invalid_type():
    """無効な型の閾値"""
    config = {
        "thresholds": {
            "cpu": {"warning": "70", "alert": 80, "critical": 90},  # 文字列
        }
    }
    
    with pytest.raises(ValidationError, match="数値で指定してください"):
        validate_threshold_config(config)


def test_out_of_range():
    """範囲外の閾値"""
    config = {
        "thresholds": {
            "cpu": {"warning": -10, "alert": 80, "critical": 90},  # 負の値
        }
    }
    
    with pytest.raises(ValidationError, match="0-200 の範囲"):
        validate_threshold_config(config)


def test_level_determination_exact_threshold():
    """閾値ちょうどの値でのレベル判定"""
    thresholds = {"warning": 70, "alert": 80, "critical": 90}
    
    assert determine_threshold_level(70, thresholds) == ThresholdLevel.WARNING
    assert determine_threshold_level(80, thresholds) == ThresholdLevel.ALERT
    assert determine_threshold_level(90, thresholds) == ThresholdLevel.CRITICAL


def test_level_determination_negative():
    """負の値のレベル判定"""
    thresholds = {"warning": 70, "alert": 80, "critical": 90}
    
    assert determine_threshold_level(-5, thresholds) == ThresholdLevel.NORMAL


def test_level_determination_over_100():
    """100超の値のレベル判定（CPUバースト）"""
    thresholds = {"warning": 70, "alert": 80, "critical": 90}
    
    assert determine_threshold_level(150, thresholds) == ThresholdLevel.CRITICAL


def test_default_thresholds():
    """デフォルト閾値の使用"""
    config = {"thresholds": {}}  # 空の設定
    
    result = validate_threshold_config(config)
    
    # デフォルト値が設定される
    assert "cpu" in result
    assert "mem" in result
    assert "disk" in result
    assert result["cpu"]["warning"] < result["cpu"]["alert"] < result["cpu"]["critical"]


def test_message_template_consistency():
    """
    [PROP-004] メッセージの一貫性
    
    各閾値レベルが正確に1つの絵文字とメッセージにマッピングされる。
    """
    from src.komon.analyzer import MESSAGE_TEMPLATES
    
    # すべてのレベル（NORMAL以外）にテンプレートが存在
    assert ThresholdLevel.WARNING in MESSAGE_TEMPLATES
    assert ThresholdLevel.ALERT in MESSAGE_TEMPLATES
    assert ThresholdLevel.CRITICAL in MESSAGE_TEMPLATES
    
    # 各テンプレートにemojiとprefixが存在
    for level in [ThresholdLevel.WARNING, ThresholdLevel.ALERT, ThresholdLevel.CRITICAL]:
        assert "emoji" in MESSAGE_TEMPLATES[level]
        assert "prefix" in MESSAGE_TEMPLATES[level]
        assert isinstance(MESSAGE_TEMPLATES[level]["emoji"], str)
        assert isinstance(MESSAGE_TEMPLATES[level]["prefix"], str)
