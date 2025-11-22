# Design Document

## Overview

通知履歴機能は、Komonが検知したシステムメトリクスの異常や警告をローカルファイルシステムに永続化し、後から確認できるようにする機能です。この機能により、Slack等の外部通知サービスが利用できない環境でも、重要な検知情報を見逃すことなく確認できます。

設計の主要な方針：
- 既存の通知機能に影響を与えない非侵襲的な実装
- シンプルなJSON形式での保存
- 最大100件の自動ローテーション
- `komon advise`コマンドへの自然な統合

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Komon Main Process                    │
│  (scripts/main.py, scripts/main_log_monitor.py)         │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ detect anomaly
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Notification System                         │
│           (src/komon/notification.py)                    │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │ send_slack_alert │      │ send_email_alert │        │
│  └──────────────────┘      └──────────────────┘        │
│           │                          │                  │
│           └──────────┬───────────────┘                  │
│                      │                                  │
│                      │ (NEW)                            │
│                      ▼                                  │
│         ┌────────────────────────┐                      │
│         │ save_notification_     │                      │
│         │ to_history()           │                      │
│         └────────────┬───────────┘                      │
└──────────────────────┼──────────────────────────────────┘
                       │
                       │ write
                       ▼
              ┌─────────────────┐
              │  Queue File     │
              │ notifications/  │
              │  queue.json     │
              └─────────────────┘
                       │
                       │ read
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Advise Command                              │
│            (scripts/advise.py)                           │
│                                                          │
│  ┌──────────────────────────────────────────┐           │
│  │ (NEW) display_notification_history()     │           │
│  │  - Read queue.json                       │           │
│  │  - Format and display                    │           │
│  │  - Handle --history N option             │           │
│  └──────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Notification History Manager

新しいモジュール `src/komon/notification_history.py` を作成します。

```python
def save_notification(
    metric_type: str,
    metric_value: float,
    message: str,
    queue_file: str = "notifications/queue.json"
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
    pass

def load_notification_history(
    queue_file: str = "notifications/queue.json",
    limit: int = None
) -> list[dict]:
    """
    通知履歴を読み込みます。
    
    Args:
        queue_file: 読み込み元ファイルパス
        limit: 取得する最大件数（Noneの場合は全件）
        
    Returns:
        list[dict]: 通知履歴のリスト（新しい順）
    """
    pass

def format_notification(notification: dict) -> str:
    """
    通知データを人間が読みやすい形式にフォーマットします。
    
    Args:
        notification: 通知データ
        
    Returns:
        str: フォーマット済み文字列
    """
    pass
```

### 2. Notification Module Integration

既存の `src/komon/notification.py` を拡張します。

```python
def send_slack_alert(message: str, webhook_url: str, metadata: dict = None) -> bool:
    """
    Slackに通知を送信し、履歴に保存します。
    
    Args:
        message: 送信するメッセージ
        webhook_url: Slack Incoming Webhook URL
        metadata: 通知メタデータ（metric_type, metric_value等）
        
    Returns:
        bool: 送信成功時True
    """
    # 既存のSlack送信処理
    success = _send_to_slack(message, webhook_url)
    
    # 履歴に保存（失敗しても通知は継続）
    if metadata:
        try:
            from komon.notification_history import save_notification
            save_notification(
                metric_type=metadata.get("metric_type", "unknown"),
                metric_value=metadata.get("metric_value", 0),
                message=message
            )
        except Exception as e:
            print(f"⚠️ 通知履歴の保存に失敗: {e}")
    
    return success
```

### 3. Advise Command Extension

`scripts/advise.py` に履歴表示機能を追加します。

```python
def advise_notification_history(limit: int = None):
    """
    通知履歴を表示します。
    
    Args:
        limit: 表示する最大件数（Noneの場合は全件）
    """
    from komon.notification_history import load_notification_history, format_notification
    
    print("\n📜 通知履歴")
    try:
        history = load_notification_history(limit=limit)
        if not history:
            print("→ 通知履歴はありません。")
            return
        
        for notification in history:
            print(format_notification(notification))
    except Exception as e:
        print(f"⚠️ 通知履歴の読み込みに失敗: {e}")
```

## Data Models

### Notification Entry

```json
{
  "timestamp": "2025-11-22T10:30:45.123456",
  "metric_type": "mem",
  "metric_value": 85.5,
  "message": "ちょっと気になることがあります。メモリ使用率が 85.5% になっています。"
}
```

フィールド定義：
- `timestamp` (string): ISO 8601形式のタイムスタンプ
- `metric_type` (string): メトリクスの種類（cpu, mem, disk, log等）
- `metric_value` (float): メトリクスの値
- `message` (string): 通知メッセージ本文

### Queue File Structure

```json
[
  {
    "timestamp": "2025-11-22T10:30:45.123456",
    "metric_type": "mem",
    "metric_value": 85.5,
    "message": "..."
  },
  {
    "timestamp": "2025-11-22T09:15:30.654321",
    "metric_type": "cpu",
    "metric_value": 92.3,
    "message": "..."
  }
]
```

- ファイルパス: `notifications/queue.json`
- 形式: JSON配列
- 順序: 新しい通知が先頭（index 0）
- 最大件数: 100件

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Notification persistence
*For any* notification with valid metric_type, metric_value, and message, calling save_notification should result in that notification being present in the queue file
**Validates: Requirements 1.1, 1.2**

### Property 2: Maximum queue size invariant
*For any* sequence of save operations, the queue file should never contain more than 100 notifications
**Validates: Requirements 1.4, 3.1**

### Property 3: Chronological order preservation
*For any* queue state, after adding a new notification, all remaining notifications should maintain their chronological order (newest first)
**Validates: Requirements 3.2**

### Property 4: History retrieval with limit
*For any* queue with N notifications and limit value L, load_notification_history(limit=L) should return exactly min(N, L) most recent notifications
**Validates: Requirements 2.2**

### Property 5: Format completeness
*For any* valid notification, format_notification should produce a string containing the timestamp, metric_type, metric_value, and message
**Validates: Requirements 2.3**

### Property 6: Graceful error handling
*For any* corrupted or invalid queue file, load_notification_history should not crash and should return an empty list or raise a handled exception
**Validates: Requirements 2.5, 3.3**

## Error Handling

### File System Errors

1. **ディレクトリ作成失敗**
   - 原因: 権限不足、ディスク容量不足
   - 対応: エラーログを出力し、通知送信は継続

2. **ファイル書き込み失敗**
   - 原因: 権限不足、ディスク容量不足、ファイルロック
   - 対応: エラーログを出力し、通知送信は継続

3. **ファイル読み込み失敗**
   - 原因: ファイルが存在しない、権限不足
   - 対応: 空の履歴として扱い、ユーザーに通知

### Data Validation Errors

1. **不正なJSON形式**
   - 原因: ファイル破損、手動編集ミス
   - 対応: エラーメッセージを表示し、空の履歴として扱う

2. **必須フィールドの欠落**
   - 原因: 古いバージョンのデータ、不完全な保存
   - 対応: 該当エントリをスキップし、有効なエントリのみ表示

3. **不正なデータ型**
   - 原因: 手動編集ミス、バグ
   - 対応: 該当エントリをスキップし、警告を表示

### Backward Compatibility

1. **既存通知機能への影響**
   - 履歴保存が失敗しても、Slack/メール通知は正常に動作
   - try-exceptで履歴保存処理を保護

2. **既存adviseコマンドへの影響**
   - 履歴表示は独立したセクションとして追加
   - 既存の助言機能は変更なし

## Testing Strategy

### Unit Testing

Pythonの標準`unittest`フレームワークを使用します。

**テスト対象:**
- `save_notification()`: 正常系、エラー系
- `load_notification_history()`: 正常系、エラー系、limit指定
- `format_notification()`: 各種データパターン
- ファイルI/O: 存在しないディレクトリ、権限エラー等

**テストファイル:** `tests/test_notification_history.py`

### Property-Based Testing

Pythonの`hypothesis`ライブラリを使用します。

**設定:**
- 最小実行回数: 100回
- タイムアウト: テストごとに30秒

**テスト対象:**
- Property 1: Notification persistence
- Property 2: Maximum queue size invariant
- Property 3: Chronological order preservation
- Property 4: History retrieval with limit
- Property 5: Format completeness
- Property 6: Graceful error handling

**テストファイル:** `tests/test_notification_history_properties.py`

### Integration Testing

**テストシナリオ:**
1. 通知送信から履歴保存までの一連の流れ
2. adviseコマンドでの履歴表示
3. 既存機能との共存確認

**テストファイル:** `tests/test_notification_integration.py`

### Manual Testing

**確認項目:**
1. 実際の通知発生時に履歴が保存されるか
2. `komon advise`で履歴が正しく表示されるか
3. 100件を超えた際のローテーション動作
4. エラー時の挙動（ディスク容量不足等）
