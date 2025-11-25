"""
ディスク使用量予測の統合テスト

advise.pyおよびweekly_report.pyとの統合をテストします。
"""

import pytest
import os
import tempfile
import csv
from datetime import datetime, date, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from komon.disk_predictor import (
    load_disk_history,
    calculate_daily_average,
    predict_disk_trend,
    detect_rapid_change,
    format_prediction_message
)


# ========================================
# advise.py統合テスト
# ========================================

def test_advise_disk_prediction_with_data(tmp_path, capsys):
    """
    予測結果が表示されることを確認
    
    **検証要件: 5.1**
    """
    # テスト用の履歴データを作成
    history_dir = tmp_path / "data" / "usage_history"
    history_dir.mkdir(parents=True)
    
    # 7日分のデータを作成（増加傾向）
    base_date = datetime.now() - timedelta(days=7)
    for i in range(7):
        file_date = base_date + timedelta(days=i)
        filename = f"usage_{file_date.strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = history_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'cpu', 'mem', 'disk'])
            disk_usage = 70.0 + i * 2.0  # 70%から84%まで増加
            writer.writerow([file_date.strftime('%Y-%m-%d %H:%M:%S'), 50.0, 60.0, disk_usage])
    
    # disk_predictorのHISTORY_DIRを一時的に変更
    import komon.disk_predictor as dp
    original_dir = dp.HISTORY_DIR
    dp.HISTORY_DIR = str(history_dir)
    
    try:
        # advise_disk_prediction関数をインポートして実行
        from scripts.advise import advise_disk_prediction
        
        advise_disk_prediction()
        
        # 出力を確認
        captured = capsys.readouterr()
        assert "📊 ディスク使用量の予測" in captured.out
        assert "現在の使用率" in captured.out or "増加" in captured.out or "安定" in captured.out
        
    finally:
        dp.HISTORY_DIR = original_dir


def test_advise_disk_prediction_insufficient_data(tmp_path, capsys):
    """
    データ不足時のメッセージを確認
    
    **検証要件: 5.2**
    """
    # 空のディレクトリを作成
    history_dir = tmp_path / "data" / "usage_history"
    history_dir.mkdir(parents=True)
    
    # disk_predictorのHISTORY_DIRを一時的に変更
    import komon.disk_predictor as dp
    original_dir = dp.HISTORY_DIR
    dp.HISTORY_DIR = str(history_dir)
    
    try:
        from scripts.advise import advise_disk_prediction
        
        advise_disk_prediction()
        
        # 出力を確認
        captured = capsys.readouterr()
        assert "データが不足しています" in captured.out
        
    finally:
        dp.HISTORY_DIR = original_dir


def test_advise_disk_prediction_error_handling(capsys):
    """
    エラー時の動作を確認
    
    **検証要件: 5.3**
    """
    # 存在しないディレクトリを指定してエラーを発生させる
    import komon.disk_predictor as dp
    original_dir = dp.HISTORY_DIR
    dp.HISTORY_DIR = "/nonexistent/directory"
    
    try:
        from scripts.advise import advise_disk_prediction
        
        # エラーが発生しても例外は発生せず、メッセージが表示される
        advise_disk_prediction()
        
        # 出力を確認（エラーメッセージまたはデータ不足メッセージ）
        captured = capsys.readouterr()
        assert "データが不足しています" in captured.out or "エラーが発生しました" in captured.out
        
    finally:
        dp.HISTORY_DIR = original_dir



# ========================================
# weekly_report.py統合テスト
# ========================================

def test_weekly_report_includes_prediction(tmp_path):
    """
    予測結果がレポートに含まれることを確認
    
    **検証要件: 6.1**
    """
    # テスト用の履歴データを作成
    history_dir = tmp_path / "data" / "usage_history"
    history_dir.mkdir(parents=True)
    
    # 7日分のデータを作成
    base_date = datetime.now() - timedelta(days=7)
    for i in range(7):
        file_date = base_date + timedelta(days=i)
        filename = f"usage_{file_date.strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = history_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'cpu', 'mem', 'disk'])
            disk_usage = 70.0 + i * 2.0
            writer.writerow([file_date.strftime('%Y-%m-%d %H:%M:%S'), 50.0, 60.0, disk_usage])
    
    # disk_predictorのHISTORY_DIRを一時的に変更
    import komon.disk_predictor as dp
    original_dir = dp.HISTORY_DIR
    dp.HISTORY_DIR = str(history_dir)
    
    try:
        from komon.weekly_data import collect_weekly_data
        from komon.report_formatter import format_weekly_report
        
        # 週次データを収集
        data = collect_weekly_data()
        
        # 予測結果が含まれることを確認
        assert 'disk_prediction' in data
        assert data['disk_prediction'] is not None
        assert 'prediction' in data['disk_prediction']
        assert 'rapid_change' in data['disk_prediction']
        
        # レポートをフォーマット
        report = format_weekly_report(data)
        
        # レポートに予測セクションが含まれることを確認
        assert 'ディスク使用量の予測' in report
        
    finally:
        dp.HISTORY_DIR = original_dir


def test_weekly_report_insufficient_data(tmp_path):
    """
    データ不足時のメッセージを確認
    
    **検証要件: 6.5**
    """
    # 空のディレクトリを作成
    history_dir = tmp_path / "data" / "usage_history"
    history_dir.mkdir(parents=True)
    
    # disk_predictorのHISTORY_DIRを一時的に変更
    import komon.disk_predictor as dp
    original_dir = dp.HISTORY_DIR
    dp.HISTORY_DIR = str(history_dir)
    
    try:
        from komon.weekly_data import collect_weekly_data
        from komon.report_formatter import format_weekly_report
        
        # 週次データを収集
        data = collect_weekly_data()
        
        # 予測結果がNoneであることを確認
        assert data.get('disk_prediction') is None
        
        # レポートをフォーマット（エラーなく完了すること）
        report = format_weekly_report(data)
        
        # レポートが生成されることを確認
        assert '週次健全性レポート' in report
        
    finally:
        dp.HISTORY_DIR = original_dir
