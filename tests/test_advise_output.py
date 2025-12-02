"""
advise.pyの出力フォーマット機能のテスト
"""

import pytest
import sys
from pathlib import Path

# scriptsディレクトリをパスに追加
scripts_path = Path(__file__).parent.parent / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

from advise import generate_progress_bar, get_status_info


class TestProgressBar:
    """プログレスバー生成のテスト"""
    
    def test_progress_bar_0_percent(self):
        """0%のプログレスバー"""
        result = generate_progress_bar(0)
        assert result == "[░░░░░░░░░░]"
    
    def test_progress_bar_50_percent(self):
        """50%のプログレスバー"""
        result = generate_progress_bar(50)
        assert result == "[█████░░░░░]"
    
    def test_progress_bar_100_percent(self):
        """100%のプログレスバー"""
        result = generate_progress_bar(100)
        assert result == "[██████████]"
    
    def test_progress_bar_negative(self):
        """負の値は0%として扱う"""
        result = generate_progress_bar(-10)
        assert result == "[░░░░░░░░░░]"
    
    def test_progress_bar_over_100(self):
        """100%を超える値は100%として扱う"""
        result = generate_progress_bar(150)
        assert result == "[██████████]"
    
    def test_progress_bar_custom_width(self):
        """カスタム幅のプログレスバー"""
        result = generate_progress_bar(50, width=5)
        # 50% * 5 / 100 = 2.5 → 2個埋まる
        assert result == "[██░░░]"
        assert len(result) == 7  # [と]を含む
    
    def test_progress_bar_10_percent_increments(self):
        """10%刻みで正しく表示される"""
        assert generate_progress_bar(0) == "[░░░░░░░░░░]"
        assert generate_progress_bar(10) == "[█░░░░░░░░░]"
        assert generate_progress_bar(20) == "[██░░░░░░░░]"
        assert generate_progress_bar(30) == "[███░░░░░░░]"
        assert generate_progress_bar(40) == "[████░░░░░░]"
        assert generate_progress_bar(50) == "[█████░░░░░]"
        assert generate_progress_bar(60) == "[██████░░░░]"
        assert generate_progress_bar(70) == "[███████░░░]"
        assert generate_progress_bar(80) == "[████████░░]"
        assert generate_progress_bar(90) == "[█████████░]"
        assert generate_progress_bar(100) == "[██████████]"
    
    def test_progress_bar_between_increments(self):
        """10%刻みの間の値は切り捨て"""
        assert generate_progress_bar(15) == "[█░░░░░░░░░]"  # 10%と同じ
        assert generate_progress_bar(25) == "[██░░░░░░░░]"  # 20%と同じ
        assert generate_progress_bar(95) == "[█████████░]"  # 90%と同じ


class TestStatusInfo:
    """状態判定のテスト"""
    
    def test_status_normal(self):
        """正常状態"""
        thresholds = {"warning": 80, "alert": 90, "critical": 95}
        icon, status = get_status_info(50, thresholds)
        assert icon == "✅"
        assert status == "正常"
    
    def test_status_warning(self):
        """警告状態"""
        thresholds = {"warning": 80, "alert": 90, "critical": 95}
        icon, status = get_status_info(85, thresholds)
        assert icon == "⚠️"
        assert status == "警告"
    
    def test_status_alert(self):
        """警戒状態"""
        thresholds = {"warning": 80, "alert": 90, "critical": 95}
        icon, status = get_status_info(92, thresholds)
        assert icon == "⚠️"
        assert status == "警戒"
    
    def test_status_critical(self):
        """危険状態"""
        thresholds = {"warning": 80, "alert": 90, "critical": 95}
        icon, status = get_status_info(97, thresholds)
        assert icon == "🔥"
        assert status == "危険"
    
    def test_status_at_warning_threshold(self):
        """警告閾値ちょうど"""
        thresholds = {"warning": 80, "alert": 90, "critical": 95}
        icon, status = get_status_info(80, thresholds)
        assert icon == "⚠️"
        assert status == "警告"
    
    def test_status_at_alert_threshold(self):
        """警戒閾値ちょうど"""
        thresholds = {"warning": 80, "alert": 90, "critical": 95}
        icon, status = get_status_info(90, thresholds)
        assert icon == "⚠️"
        assert status == "警戒"
    
    def test_status_at_critical_threshold(self):
        """危険閾値ちょうど"""
        thresholds = {"warning": 80, "alert": 90, "critical": 95}
        icon, status = get_status_info(95, thresholds)
        assert icon == "🔥"
        assert status == "危険"
    
    def test_status_default_thresholds(self):
        """デフォルト閾値"""
        thresholds = {}
        icon, status = get_status_info(85, thresholds)
        assert icon == "⚠️"
        assert status == "警告"
    
    def test_status_custom_thresholds(self):
        """カスタム閾値"""
        thresholds = {"warning": 60, "alert": 70, "critical": 80}
        icon, status = get_status_info(65, thresholds)
        assert icon == "⚠️"
        assert status == "警告"
