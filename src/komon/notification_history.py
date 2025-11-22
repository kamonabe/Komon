"""
通知履歴モジュール

Komonの通知をローカルファイルに保存し、後から確認できるようにします。
"""

import json
import os
from datetime import datetime
from typing import Optional


MAX_QUEUE_SIZE = 100
DEFAULT_QUEUE_FILE = "data/notifications/queue.json"


def save_notification(
    metric_type: str,
    metric_value: float,
    message: str,
    queue_file: str = DEFAULT_QUEUE_FILE
) -> bool:
    """
    通知をキューファイルに保存します。
    
    Args:
        metric_type: メトリクスの種類 (cpu, mem, disk, log等)
        metric_value: メトリクスの値
        message: 通知メッセージ
        queue_file: 保存先ファイルパス
        
    Returns:
        bool: 保存成功時True、失敗時False
    """
    try:
        # 新しい通知エントリを作成
        notification = {
            "timestamp": datetime.now().isoformat(),
            "metric_type": metric_type,
            "metric_value": metric_value,
            "message": message
        }
        
        # 既存の履歴を読み込む
        queue = []
        if os.path.exists(queue_file):
            try:
                with open(queue_file, "r", encoding="utf-8") as f:
                    queue = json.load(f)
                    if not isinstance(queue, list):
                        queue = []
            except (json.JSONDecodeError, IOError):
                # 破損したファイルは無視して新規作成
                queue = []
        
        # 新しい通知を先頭に追加
        queue.insert(0, notification)
        
        # 100件を超える場合は古いものを削除
        if len(queue) > MAX_QUEUE_SIZE:
            queue = queue[:MAX_QUEUE_SIZE]
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(queue_file), exist_ok=True)
        
        # ファイルに保存
        with open(queue_file, "w", encoding="utf-8") as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"⚠️ 通知履歴の保存に失敗: {e}")
        return False


def load_notification_history(
    queue_file: str = DEFAULT_QUEUE_FILE,
    limit: Optional[int] = None
) -> list[dict]:
    """
    通知履歴を読み込みます。
    
    Args:
        queue_file: 読み込み元ファイルパス
        limit: 取得する最大件数（Noneの場合は全件）
        
    Returns:
        list[dict]: 通知履歴のリスト（新しい順）
    """
    try:
        if not os.path.exists(queue_file):
            return []
        
        with open(queue_file, "r", encoding="utf-8") as f:
            queue = json.load(f)
        
        if not isinstance(queue, list):
            return []
        
        # 有効なエントリのみをフィルタリング
        valid_queue = []
        for entry in queue:
            if not isinstance(entry, dict):
                continue
            
            # 必須フィールドの確認
            required_fields = ["timestamp", "metric_type", "metric_value", "message"]
            if all(field in entry for field in required_fields):
                valid_queue.append(entry)
        
        # limit指定がある場合は制限
        if limit is not None and limit > 0:
            valid_queue = valid_queue[:limit]
        
        return valid_queue
        
    except json.JSONDecodeError:
        # JSONパースエラーは空リストを返す
        return []
    except Exception:
        # その他のエラーも空リストを返す
        return []


def format_notification(notification: dict) -> str:
    """
    通知データを人間が読みやすい形式にフォーマットします。
    
    Args:
        notification: 通知データ
        
    Returns:
        str: フォーマット済み文字列
    """
    try:
        timestamp = notification.get("timestamp", "")
        metric_type = notification.get("metric_type", "unknown")
        metric_value = notification.get("metric_value", 0)
        message = notification.get("message", "")
        
        # ISO 8601形式のタイムスタンプを読みやすい形式に変換
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            formatted_time = timestamp
        
        # メトリクスタイプに応じた絵文字
        emoji_map = {
            "cpu": "🔥",
            "mem": "💾",
            "disk": "💿",
            "log": "📝"
        }
        emoji = emoji_map.get(metric_type, "📊")
        
        return f"{emoji} [{formatted_time}] {metric_type.upper()}: {metric_value} - {message}"
        
    except Exception:
        return str(notification)
