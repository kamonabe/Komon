"""
ログ傾向分析モジュール

ログの時系列データから傾向を分析します。
"""

import os
import json
import pickle
from datetime import datetime, timedelta


HISTORY_DIR = "data/logstats/history"
STATE_DIR = "data/logstats"


def _get_history_file(log_id: str) -> str:
    """ログIDから履歴ファイルのパスを生成"""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    return f"{HISTORY_DIR}/{log_id}.json"


def _load_history(log_id: str) -> list:
    """履歴データを読み込む"""
    history_file = _get_history_file(log_id)
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_history(log_id: str, history: list):
    """履歴データを保存"""
    history_file = _get_history_file(log_id)
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 履歴保存エラー: {e}")


def analyze_log_trend(log_id: str, threshold_percent: int = 30) -> str:
    """
    ログの傾向を分析します。
    
    Args:
        log_id: ログの識別子
        threshold_percent: 急増とみなす増加率（%）
        
    Returns:
        str: 分析結果メッセージ
    """
    # 現在の行数を取得（仮実装）
    state_file = f"{STATE_DIR}/{log_id}.pkl"
    if not os.path.exists(state_file):
        return f"📊 {log_id}: データ不足（初回実行）"
    
    try:
        with open(state_file, "rb") as f:
            current_lines = pickle.load(f)
    except Exception:
        return f"📊 {log_id}: 状態ファイル読み込みエラー"
    
    # 履歴を読み込む
    history = _load_history(log_id)
    
    # 履歴に追加
    today = datetime.now().strftime("%Y-%m-%d")
    history.append({
        "date": today,
        "lines": current_lines
    })
    
    # 最大30日分保持
    if len(history) > 30:
        history = history[-30:]
    
    _save_history(log_id, history)
    
    # 傾向分析
    if len(history) < 2:
        return f"📊 {log_id}: データ蓄積中（{len(history)}日分）"
    
    # 前日比
    yesterday_lines = history[-2]["lines"]
    increase_rate = ((current_lines - yesterday_lines) / max(yesterday_lines, 1)) * 100
    
    if increase_rate > threshold_percent:
        return f"📊 {log_id}: 前日比 +{increase_rate:.1f}% の急増の可能性"
    else:
        return f"📊 {log_id}: 正常範囲（前日比 {increase_rate:+.1f}%）"


def detect_repeated_spikes(log_id: str, days: int = 3) -> bool:
    """
    複数日にわたる急増パターンを検出します。
    
    Args:
        log_id: ログの識別子
        days: 検出対象の日数
        
    Returns:
        bool: 連続急増が検出された場合True
    """
    history = _load_history(log_id)
    
    if len(history) < days + 1:
        return False
    
    # 直近N日間の増加率をチェック
    spike_count = 0
    for i in range(len(history) - days, len(history)):
        if i > 0:
            prev_lines = history[i - 1]["lines"]
            curr_lines = history[i]["lines"]
            increase_rate = ((curr_lines - prev_lines) / max(prev_lines, 1)) * 100
            
            if increase_rate > 20:  # 20%以上の増加
                spike_count += 1
    
    return spike_count >= days
