import json
from pathlib import Path
from datetime import datetime
from statistics import mean

DEFAULT_THRESHOLD_PERCENT = 30
HISTORY_DIR = Path("data/logstats/history")
DAYS_TO_ANALYZE = 7

def analyze_log_trend(log_name: str, threshold_percent: int = DEFAULT_THRESHOLD_PERCENT) -> str:
    """指定ログの傾向を分析し、アドバイス文を返す"""
    history_path = HISTORY_DIR / f"{log_name}.json"
    if not history_path.exists():
        return f"- {log_name} の履歴が見つかりません"

    with open(history_path, "r", encoding="utf-8") as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            return f"- {log_name} の履歴ファイルが壊れています"

    if len(history) < 2:
        return f"- {log_name} の履歴が不足しています"

    recent_data = history[-DAYS_TO_ANALYZE:]
    if len(recent_data) < 2:
        return f"- {log_name} の直近データが不十分です"

    try:
        avg_lines = mean([entry["lines"] for entry in recent_data[:-1]])
        last_day_lines = recent_data[-1]["lines"]
    except (KeyError, TypeError):
        return f"- {log_name} の履歴形式に問題があります"

    increase_percent = ((last_day_lines - avg_lines) / avg_lines) * 100
    if increase_percent >= threshold_percent:
        return f"- {log_name}：昨日のログ行数は平均の{increase_percent:.1f}%増（{last_day_lines}行）でした。急増の可能性があります。"
    else:
        return f"- {log_name}：特に異常な増加は見られません（{last_day_lines}行）。"

def list_available_logs() -> list:
    """historyフォルダにあるJSONファイル一覧からログ名を取得"""
    if not HISTORY_DIR.exists():
        return []
    return [p.stem for p in HISTORY_DIR.glob("*.json")]

def detect_repeated_spikes(log_name: str, threshold: int = 30, days: int = 3) -> bool:
    """
    指定ログについて、直近 `days` 日間にわたってログ行数が平均より `threshold`%以上
    増加している日が連続しているかどうかを判定する。
    """
    history_path = HISTORY_DIR / f"{log_name}.json"
    if not history_path.exists():
        return False

    try:
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    except json.JSONDecodeError:
        return False

    if len(history) < days + 1:
        return False  # 平均＋比較対象分のデータが必要

    recent_data = history[-(days + 1):]  # days+1日分を使用（平均と比較）
    try:
        base_avg = mean([entry["lines"] for entry in recent_data[:-1]])
    except (KeyError, TypeError):
        return False

    count = 0
    for i in range(1, days + 1):
        try:
            daily = recent_data[i]["lines"]
            percent_increase = ((daily - base_avg) / base_avg) * 100
            if percent_increase >= threshold:
                count += 1
            else:
                break  # 連続ではない
        except (KeyError, TypeError):
            break

    return count == days
