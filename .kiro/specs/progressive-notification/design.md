---
title: 段階的通知メッセージ - 設計書
feature: progressive-notification
status: in-progress
created: 2025-11-26
updated: 2025-11-26
---

# 段階的通知メッセージ - 設計書

## 概要

段階的通知メッセージ機能は、既存の通知履歴機能（v1.11.0）を活用して、同一問題の繰り返し回数に応じてメッセージを段階的に変化させる機能です。これにより、問題の緊急度を適切に伝え、「通知疲れ」を防ぎます。

設計の主要な方針：
- 既存の通知履歴機能を活用（新しいファイルは作成しない）
- 通知送信ロジックへの最小限の変更
- 設定ファイルでカスタマイズ可能
- 後方互換性の維持

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                    Komon Main Process                    │
│  (scripts/main.py)                                       │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ detect anomaly
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Analyzer Module                             │
│           (src/komon/analyzer.py)                        │
│                                                          │
│  ┌──────────────────────────────────────────┐           │
│  │ (MODIFIED) analyze_usage()               │           │
│  │  - Detect threshold violation            │           │
│  │  - Get notification count (NEW)          │           │
│  │  - Generate progressive message (NEW)    │           │
│  └──────────────────┬───────────────────────┘           │
└─────────────────────┼──────────────────────────────────┘
                      │
                      │ call
                      ▼
┌─────────────────────────────────────────────────────────┐
│         Progressive Message Module (NEW)                 │
│      (src/komon/progressive_message.py)                  │
│                                                          │
│  ┌──────────────────────────────────────────┐           │
│  │ get_notification_count()                 │           │
│  │  - Read notification history             │           │
│  │  - Count same metric_type in 24h         │           │
│  └──────────────────┬───────────────────────┘           │
│                     │                                    │
│  ┌──────────────────▼───────────────────────┐           │
│  │ generate_progressive_message()           │           │
│  │  - Select template by count              │           │
│  │  - Format message with metric data       │           │
│  └──────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
                      │
                      │ return message
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
│                      ▼                                  │
│         ┌────────────────────────┐                      │
│         │ save_notification_     │                      │
│         │ to_history()           │                      │
│         └────────────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

## コンポーネントとインターフェース

### 1. 段階的メッセージモジュール（新規）

新しいモジュール `src/komon/progressive_message.py` を作成します。

```python
from datetime import datetime, timedelta
from typing import Optional
from komon.notification_history import load_notification_history


def get_notification_count(
    metric_type: str,
    time_window_hours: int = 24,
    queue_file: str = "data/notifications/queue.json"
) -> int:
    """
    指定された時間窓内の同一メトリクスタイプの通知回数を取得します。
    
    Args:
        metric_type: メトリクスの種類 (cpu, mem, disk)
        time_window_hours: 時間窓（時間）
        queue_file: 通知履歴ファイルパス
        
    Returns:
        int: 通知回数（0以上）
    """
    pass


def generate_progressive_message(
    metric_type: str,
    metric_value: float,
    threshold: float,
    notification_count: int,
    templates: Optional[dict] = None
) -> str:
    """
    通知回数に応じた段階的メッセージを生成します。
    
    Args:
        metric_type: メトリクスの種類 (cpu, mem, disk)
        metric_value: 現在の値
        threshold: 閾値
        notification_count: 通知回数（1, 2, 3以上）
        templates: カスタムテンプレート（Noneの場合はデフォルト）
        
    Returns:
        str: 生成されたメッセージ
    """
    pass


# デフォルトテンプレート
DEFAULT_TEMPLATES = {
    1: "ちょっと気になることがあります。{metric_name}が {value}{unit} になっています。",
    2: "まだ続いてますね。{metric_name}が {value}{unit} のままです。",
    3: "そろそろ見た方がいいかも。{metric_name}が {value}{unit} の状態が続いています。"
}
```

### 2. Analyzerモジュールの修正

既存の `src/komon/analyzer.py` を修正します。

```python
from komon.progressive_message import get_notification_count, generate_progressive_message


def analyze_usage(cpu: float, mem: float, disk: float, thresholds: dict) -> dict:
    """
    リソース使用状況を分析し、閾値超過を検出します。
    
    Args:
        cpu: CPU使用率 (%)
        mem: メモリ使用率 (%)
        disk: ディスク使用率 (%)
        thresholds: 閾値設定
        
    Returns:
        dict: 分析結果
    """
    result = {
        "cpu_exceeded": False,
        "mem_exceeded": False,
        "disk_exceeded": False,
        "messages": []
    }
    
    # CPU使用率チェック
    if cpu > thresholds.get("cpu", 80):
        count = get_notification_count("cpu")
        message = generate_progressive_message("cpu", cpu, thresholds["cpu"], count + 1)
        result["cpu_exceeded"] = True
        result["messages"].append({
            "metric_type": "cpu",
            "metric_value": cpu,
            "message": message
        })
    
    # メモリ使用率チェック（同様）
    # ディスク使用率チェック（同様）
    
    return result
```

### 3. 設定ファイルの拡張

`settings.yml` に段階的メッセージの設定を追加します。

```yaml
# 段階的通知メッセージ設定
progressive_notification:
  enabled: true
  time_window_hours: 24
  
  # カスタムテンプレート（オプション）
  templates:
    1: "ちょっと気になることがあります。{metric_name}が {value}{unit} になっています。"
    2: "まだ続いてますね。{metric_name}が {value}{unit} のままです。"
    3: "そろそろ見た方がいいかも。{metric_name}が {value}{unit} の状態が続いています。"
```

## データフロー

### 通知発生時のフロー

```
1. scripts/main.py
   ↓ リソース使用率を取得
   
2. src/komon/analyzer.py: analyze_usage()
   ↓ 閾値超過を検出
   
3. src/komon/progressive_message.py: get_notification_count()
   ↓ 通知履歴から回数を取得
   
4. src/komon/progressive_message.py: generate_progressive_message()
   ↓ 段階的メッセージを生成
   
5. src/komon/notification.py: send_slack_alert()
   ↓ 通知を送信
   
6. src/komon/notification_history.py: save_notification()
   ↓ 履歴に保存
```

### 通知回数の判定ロジック

```python
def get_notification_count(metric_type: str, time_window_hours: int = 24) -> int:
    # 1. 通知履歴を読み込む
    history = load_notification_history()
    
    # 2. 時間窓を計算
    cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
    
    # 3. 同一メトリクスタイプの通知をカウント
    count = 0
    for notification in history:
        # タイムスタンプをパース
        timestamp = datetime.fromisoformat(notification["timestamp"])
        
        # 時間窓内かつ同一メトリクスタイプ
        if timestamp >= cutoff_time and notification["metric_type"] == metric_type:
            count += 1
    
    return count
```

## 正確性プロパティ

*プロパティとは、システムの全ての有効な実行において真であるべき特性や振る舞いのことです。*

### プロパティ1: 通知回数の正確性
*任意の*メトリクスタイプと時間窓について、get_notification_count()は指定された時間窓内の同一メトリクスタイプの通知回数を正確に返すこと
**検証対象: 要件 AC-001**

### プロパティ2: 段階的メッセージの一貫性
*任意の*通知回数（1, 2, 3以上）について、generate_progressive_message()は対応するテンプレートを使用してメッセージを生成すること
**検証対象: 要件 AC-002**

### プロパティ3: 時間窓のリセット
*任意の*メトリクスタイプについて、時間窓外の通知はカウントされないこと
**検証対象: 要件 AC-004**

### プロパティ4: メトリクスタイプの独立性
*任意の*2つの異なるメトリクスタイプについて、一方の通知回数は他方に影響しないこと
**検証対象: 要件 AC-001, AC-004**

### プロパティ5: エラー時のデフォルト動作
*任意の*エラー状態（履歴ファイル不在、破損等）について、get_notification_count()は0を返し、デフォルトメッセージが生成されること
**検証対象: 要件 AC-005**

## エラーハンドリング

### 通知履歴の読み込みエラー

1. **ファイルが存在しない**
   - 対応: 通知回数を0として扱う（1回目のメッセージ）
   - ログ: 警告を出力しない（初回実行時は正常）

2. **ファイルが破損している**
   - 対応: 通知回数を0として扱う
   - ログ: 警告を出力

3. **タイムスタンプのパースエラー**
   - 対応: 該当エントリをスキップ
   - ログ: デバッグレベルで出力

### 設定ファイルのエラー

1. **progressive_notification設定が存在しない**
   - 対応: デフォルト設定を使用
   - ログ: 情報レベルで出力

2. **カスタムテンプレートが不正**
   - 対応: デフォルトテンプレートを使用
   - ログ: 警告を出力

## テスト戦略

### ユニットテスト

**テスト対象:**
- `get_notification_count()`: 各種時間窓、メトリクスタイプ
- `generate_progressive_message()`: 各段階のメッセージ生成
- エラーハンドリング: ファイル不在、破損等

**テストファイル:** `tests/test_progressive_message.py`

### プロパティベーステスト

**テスト対象:**
- プロパティ1: 通知回数の正確性
- プロパティ2: 段階的メッセージの一貫性
- プロパティ3: 時間窓のリセット
- プロパティ4: メトリクスタイプの独立性
- プロパティ5: エラー時のデフォルト動作

**テストファイル:** `tests/test_progressive_message_properties.py`

### 統合テスト

**テストシナリオ:**
1. 初回通知: 1回目のメッセージが生成される
2. 2回目通知: 2回目のメッセージが生成される
3. 3回目以降: 3回目のメッセージが生成される
4. 時間窓リセット: 24時間後に1回目に戻る
5. 異なるメトリクス: 独立してカウントされる

**テストファイル:** `tests/test_progressive_notification_integration.py`

## パフォーマンス考慮事項

### 通知履歴の読み込み

- 通知履歴は最大100件なので、全件読み込みでも問題なし
- ファイルI/Oは1回のみ（キャッシュ不要）

### 時間窓の計算

- タイムスタンプのパースは高速（datetime.fromisoformat）
- 最悪ケース: 100件 × パース時間 < 10ms

### メッセージ生成

- 文字列フォーマットのみ（高速）
- テンプレート選択はO(1)

## 後方互換性

### 既存機能への影響

1. **通知履歴機能**
   - 変更なし（読み込みのみ）

2. **通知送信機能**
   - メッセージ内容のみ変更
   - インターフェースは変更なし

3. **設定ファイル**
   - 新しいセクションを追加（オプション）
   - 既存設定は影響なし

### 無効化オプション

設定ファイルで機能を無効化可能：

```yaml
progressive_notification:
  enabled: false
```

無効化時は従来のメッセージを使用します。
