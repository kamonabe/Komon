"""
ログ分析モジュール

ログの異常検知を行います。
"""


def check_log_anomaly(log_path: str, line_count: int, config: dict) -> str:
    """
    ログの急増を検知します。
    
    Args:
        log_path: ログファイルのパス
        line_count: 差分行数
        config: 設定ファイルの内容
        
    Returns:
        str: 警告メッセージ（異常がない場合は空文字列）
    """
    # 閾値の取得（デフォルト: 100行）
    threshold = config.get("log_analysis", {}).get("line_threshold", 100)
    
    if line_count > threshold:
        return f"{log_path} で {line_count} 行の増加を検出（閾値: {threshold}行）"
    
    return ""
