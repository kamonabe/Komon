import os
import pickle
from pathlib import Path
from typing import Dict


BASELINE_DIR = Path("data/logstats")
BASELINE_SUFFIX = "_baseline.pkl"


def _get_baseline_path(log_path: str) -> Path:
    """対象ログのベースライン保存パスを取得"""
    name = log_path.strip("/").replace("/", "_")
    return BASELINE_DIR / f"{name}{BASELINE_SUFFIX}"


def load_baseline(log_path: str) -> float:
    """指定ログのベースライン（平均行数）を読み込む"""
    path = _get_baseline_path(log_path)
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def update_baseline(log_path: str, new_value: int, alpha: float = 0.1):
    """
    ベースラインを移動平均で更新（重み付き平均）
    alpha: 学習率（0.1 = 10%だけ新しい値を採用）
    """
    old = load_baseline(log_path)
    if old is None:
        updated = new_value
    else:
        updated = (1 - alpha) * old + alpha * new_value

    path = _get_baseline_path(log_path)
    with open(path, "wb") as f:
        pickle.dump(updated, f)


def check_log_anomaly(log_path: str, new_count: int, config: dict) -> str:
    """
    ログ行数の急増／急減を検知し、異常があれば警戒文を返す。
    設定からしきい値と学習率を読み取る。
    """
    analysis_cfg = config.get("log_analysis", {})
    threshold_percent = analysis_cfg.get("anomaly_threshold_percent", 30)
    alpha = analysis_cfg.get("baseline_learning_rate", 0.1)

    baseline = load_baseline(log_path)
    if baseline is None:
        # 初期学習中扱い
        update_baseline(log_path, new_count, alpha)
        return None

    diff_percent = (new_count - baseline) / baseline * 100

    if abs(diff_percent) >= threshold_percent:
        status = "増加" if diff_percent > 0 else "減少"
        alert = (
            f"📈 ログ[{log_path}] 行数が急{status}（{baseline:.1f} → {new_count}行）"
        )
        update_baseline(log_path, new_count, alpha)  # 継続学習
        return alert

    # 正常範囲内：ベースラインだけ更新
    update_baseline(log_path, new_count, alpha)
    return None
