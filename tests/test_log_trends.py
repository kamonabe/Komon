"""
log_trends.py のテスト

ログ傾向分析機能のテストを行います。
"""

import pytest
import os
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from komon.log_trends import (
    analyze_log_trend,
    detect_repeated_spikes,
    _get_history_file,
    _load_history,
    _save_history
)


@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    """テスト用の一時データディレクトリ"""
    history_dir = tmp_path / "history"
    state_dir = tmp_path / "state"
    history_dir.mkdir(parents=True)
    state_dir.mkdir(parents=True)
    
    monkeypatch.setattr('komon.log_trends.HISTORY_DIR', str(history_dir))
    monkeypatch.setattr('komon.log_trends.STATE_DIR', str(state_dir))
    
    return {
        'history_dir': history_dir,
        'state_dir': state_dir
    }


class TestGetHistoryFile:
    """_get_history_file関数のテスト"""
    
    def test_get_history_file_path(self, temp_data_dir):
        """履歴ファイルパスが正しく生成される"""
        log_id = "test_log"
        file_path = _get_history_file(log_id)
        
        assert "test_log.json" in file_path
        assert str(temp_data_dir['history_dir']) in file_path


class TestLoadHistory:
    """_load_history関数のテスト"""
    
    def test_load_history_empty(self, temp_data_dir):
        """履歴ファイルが存在しない場合、空リストを返す"""
        history = _load_history("nonexistent_log")
        
        assert history == []
    
    def test_load_history_with_data(self, temp_data_dir):
        """履歴ファイルが存在する場合、データを読み込む"""
        log_id = "test_log"
        test_data = [
            {"date": "2024-01-01", "lines": 100},
            {"date": "2024-01-02", "lines": 150}
        ]
        
        # 履歴ファイルを作成
        history_file = _get_history_file(log_id)
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        history = _load_history(log_id)
        
        assert len(history) == 2
        assert history[0]["lines"] == 100
        assert history[1]["lines"] == 150
    
    def test_load_history_corrupted_file(self, temp_data_dir):
        """破損した履歴ファイルの場合、空リストを返す"""
        log_id = "corrupted_log"
        history_file = _get_history_file(log_id)
        
        # 破損したJSONファイルを作成
        with open(history_file, 'w', encoding='utf-8') as f:
            f.write("invalid json {")
        
        history = _load_history(log_id)
        
        assert history == []


class TestSaveHistory:
    """_save_history関数のテスト"""
    
    def test_save_history_success(self, temp_data_dir):
        """履歴データが正しく保存される"""
        log_id = "test_log"
        test_data = [
            {"date": "2024-01-01", "lines": 100},
            {"date": "2024-01-02", "lines": 150}
        ]
        
        _save_history(log_id, test_data)
        
        # 保存されたデータを確認
        history_file = _get_history_file(log_id)
        assert os.path.exists(history_file)
        
        with open(history_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data


class TestAnalyzeLogTrend:
    """analyze_log_trend関数のテスト"""
    
    def test_analyze_log_trend_no_state_file(self, temp_data_dir):
        """状態ファイルが存在しない場合（初回実行）"""
        result = analyze_log_trend("test_log")
        
        assert "データ不足" in result or "初回実行" in result
    
    def test_analyze_log_trend_first_data(self, temp_data_dir):
        """データが1件のみの場合"""
        log_id = "test_log"
        state_file = f"{temp_data_dir['state_dir']}/{log_id}.pkl"
        
        # 状態ファイルを作成
        with open(state_file, 'wb') as f:
            pickle.dump(100, f)
        
        result = analyze_log_trend(log_id)
        
        assert "データ蓄積中" in result or "1日分" in result
    
    def test_analyze_log_trend_normal_increase(self, temp_data_dir):
        """正常範囲の増加の場合"""
        log_id = "test_log"
        state_file = f"{temp_data_dir['state_dir']}/{log_id}.pkl"
        
        # 状態ファイルを作成
        with open(state_file, 'wb') as f:
            pickle.dump(120, f)
        
        # 履歴データを作成（前日: 100行）
        history = [
            {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "lines": 100}
        ]
        _save_history(log_id, history)
        
        result = analyze_log_trend(log_id)
        
        assert "正常範囲" in result or "20.0%" in result
    
    def test_analyze_log_trend_spike_detected(self, temp_data_dir):
        """急増が検出される場合"""
        log_id = "test_log"
        state_file = f"{temp_data_dir['state_dir']}/{log_id}.pkl"
        
        # 状態ファイルを作成（現在: 200行）
        with open(state_file, 'wb') as f:
            pickle.dump(200, f)
        
        # 履歴データを作成（前日: 100行）
        history = [
            {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "lines": 100}
        ]
        _save_history(log_id, history)
        
        result = analyze_log_trend(log_id, threshold_percent=30)
        
        assert "急増" in result or "100.0%" in result
    
    def test_analyze_log_trend_custom_threshold_normal(self, temp_data_dir):
        """カスタム閾値（正常範囲）が適用される"""
        log_id = "test_log_normal"
        state_file = f"{temp_data_dir['state_dir']}/{log_id}.pkl"
        
        # 状態ファイルを作成（現在: 140行）
        with open(state_file, 'wb') as f:
            pickle.dump(140, f)
        
        # 履歴データを作成（前日: 100行）
        history = [
            {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "lines": 100}
        ]
        _save_history(log_id, history)
        
        # 閾値50%の場合は正常範囲（100→140は40%増加）
        result = analyze_log_trend(log_id, threshold_percent=50)
        assert "正常範囲" in result
        assert "40.0%" in result
    
    def test_analyze_log_trend_custom_threshold_spike(self, temp_data_dir):
        """カスタム閾値（急増）が適用される"""
        log_id = "test_log_spike"
        state_file = f"{temp_data_dir['state_dir']}/{log_id}.pkl"
        
        # 状態ファイルを作成（現在: 140行）
        with open(state_file, 'wb') as f:
            pickle.dump(140, f)
        
        # 履歴データを作成（前日: 100行）
        history = [
            {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "lines": 100}
        ]
        _save_history(log_id, history)
        
        # 閾値30%の場合は急増（100→140は40%増加）
        result = analyze_log_trend(log_id, threshold_percent=30)
        assert "急増" in result
        assert "40.0%" in result
    
    def test_analyze_log_trend_history_limit(self, temp_data_dir):
        """履歴が30日分に制限される"""
        log_id = "test_log"
        state_file = f"{temp_data_dir['state_dir']}/{log_id}.pkl"
        
        # 状態ファイルを作成
        with open(state_file, 'wb') as f:
            pickle.dump(100, f)
        
        # 40日分の履歴を作成
        history = []
        for i in range(40):
            date = (datetime.now() - timedelta(days=40-i)).strftime("%Y-%m-%d")
            history.append({"date": date, "lines": 100 + i})
        
        _save_history(log_id, history)
        
        # 分析実行
        analyze_log_trend(log_id)
        
        # 履歴が30日分に制限されているか確認
        updated_history = _load_history(log_id)
        assert len(updated_history) <= 30


class TestDetectRepeatedSpikes:
    """detect_repeated_spikes関数のテスト"""
    
    def test_detect_repeated_spikes_insufficient_data(self, temp_data_dir):
        """データが不足している場合、Falseを返す"""
        log_id = "test_log"
        
        result = detect_repeated_spikes(log_id, days=3)
        
        assert result is False
    
    def test_detect_repeated_spikes_no_spikes(self, temp_data_dir):
        """急増がない場合、Falseを返す"""
        log_id = "test_log"
        
        # 安定した履歴データを作成
        history = []
        for i in range(5):
            date = (datetime.now() - timedelta(days=5-i)).strftime("%Y-%m-%d")
            history.append({"date": date, "lines": 100 + i})
        
        _save_history(log_id, history)
        
        result = detect_repeated_spikes(log_id, days=3)
        
        assert result is False
    
    def test_detect_repeated_spikes_detected(self, temp_data_dir):
        """連続急増が検出される場合、Trueを返す"""
        log_id = "test_log"
        
        # 連続急増の履歴データを作成
        history = [
            {"date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"), "lines": 100},
            {"date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"), "lines": 130},  # +30%
            {"date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "lines": 170},  # +30%
            {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "lines": 220},  # +29%
        ]
        
        _save_history(log_id, history)
        
        result = detect_repeated_spikes(log_id, days=3)
        
        assert result is True
    
    def test_detect_repeated_spikes_partial(self, temp_data_dir):
        """一部のみ急増の場合、Falseを返す"""
        log_id = "test_log"
        
        # 一部のみ急増の履歴データを作成
        history = [
            {"date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"), "lines": 100},
            {"date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"), "lines": 130},  # +30%
            {"date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "lines": 135},  # +3%
            {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "lines": 175},  # +29%
        ]
        
        _save_history(log_id, history)
        
        result = detect_repeated_spikes(log_id, days=3)
        
        assert result is False
    
    def test_detect_repeated_spikes_custom_days(self, temp_data_dir):
        """カスタム日数が適用される"""
        log_id = "test_log"
        
        # 2日連続急増の履歴データを作成
        history = [
            {"date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"), "lines": 100},
            {"date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "lines": 130},  # +30%
            {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "lines": 170},  # +30%
        ]
        
        _save_history(log_id, history)
        
        # 2日連続の場合はTrue
        result = detect_repeated_spikes(log_id, days=2)
        assert result is True
        
        # 3日連続を要求する場合はFalse
        result = detect_repeated_spikes(log_id, days=3)
        assert result is False
