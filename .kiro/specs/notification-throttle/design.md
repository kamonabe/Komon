---
title: 通知頻度制御（同一アラートの抑制）- 設計書
feature: notification-throttle
status: draft
created: 2025-11-24
updated: 2025-11-24
---

# 通知頻度制御（同一アラートの抑制）- 設計書

## 概要

通知頻度制御機能は、同一メトリクスの通知を適切な間隔で抑制し、閾値レベル上昇時は即座に通知、長時間継続する問題はエスカレーション通知を行います。

設計の主要な方針：
- NotificationThrottleクラスによる独立した抑制ロジック
- JSON形式での通知履歴の永続化
- 既存の通知機能への非侵襲的な統合
- 設定ファイルによる柔軟な制御

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                     scripts/main.py                         │
│                  (メイン監視スクリプト)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  src/komon/analyzer.py                      │
│              (閾値判定・メッセージ生成)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               src/komon/notification.py                     │
│                  (通知送信処理)                              │
│                         │                                    │
│    ┌────────────────────┴────────────────────┐              │
│    ▼                                         ▼              │
│  send_notification()              NotificationThrottle      │
│  (既存の送信処理)                   (新規モジュール)         │
└────────────────────────┬────────────────────┬───────────────┘
                         │                    │
                         ▼                    ▼
                  Slack/メール送信    data/notifications/
                                      throttle.json
```

## コンポーネントとインターフェース

### 1. NotificationThrottle クラス（新規）

**ファイル**: `src/komon/notification.py` に追加

**責務**:
- 通知抑制の判定
- 通知履歴の管理
- エスカレーション判定

**主要メソッド**:

```python
class NotificationThrottle:
    """通知頻度制御を管理するクラス"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: settings.ymlのthrottle設定
        """
        
    def should_send_notification(
        self,
        metric_type: str,
        threshold_level: str,
        current_value: float
    ) -> tuple[bool, str]:
        """
        通知を送信すべきかを判定する
        
        Args:
            metric_type: メトリクスタイプ（'cpu', 'memory', 'disk'）
            threshold_level: 閾値レベル（'warning', 'alert', 'critical'）
            current_value: 現在の値
            
        Returns:
            (送信すべきか, 理由)
            例: (True, "escalation"), (False, "throttled"), (True, "level_up")
        """
        
    def record_notification(
        self,
        metric_type: str,
        threshold_level: str,
        current_value: float
    ) -> None:
        """通知を記録する"""
        
    def _load_history(self) -> dict:
        """履歴ファイルを読み込む"""
        
    def _save_history(self, history: dict) -> None:
        """履歴ファイルに保存する"""
        
    def _is_level_escalated(
        self,
        previous_level: str,
        current_level: str
    ) -> bool:
        """閾値レベルが上昇したかを判定する"""
```

### 2. 通知履歴データ構造

**ファイル**: `data/notifications/throttle.json`

```json
{
  "cpu": {
    "last_notification_time": "2025-11-24T10:30:00",
    "threshold_level": "alert",
    "value": 85.5,
    "first_occurrence_time": "2025-11-24T09:00:00"
  },
  "memory": {
    "last_notification_time": "2025-11-24T09:15:00",
    "threshold_level": "warning",
    "value": 72.3,
    "first_occurrence_time": "2025-11-24T09:15:00"
  },
  "disk": {
    "last_notification_time": "2025-11-24T08:00:00",
    "threshold_level": "critical",
    "value": 92.1,
    "first_occurrence_time": "2025-11-24T06:00:00"
  }
}
```

**フィールド説明**:
- `last_notification_time`: 最後に通知を送信した時刻（ISO 8601形式）
- `threshold_level`: 最後に通知した閾値レベル
- `value`: 最後に通知した時の値
- `first_occurrence_time`: 問題が最初に発生した時刻（エスカレーション用）

### 3. 設定ファイル拡張

**ファイル**: `settings.yml`

```yaml
# 通知頻度制御設定
throttle:
  enabled: true                    # 有効/無効
  interval_minutes: 60             # 通知間隔（分）
  escalation_minutes: 180          # 再通知間隔（分）
```

**デフォルト値**:
- `enabled`: true
- `interval_minutes`: 60
- `escalation_minutes`: 180

### 4. 既存コードの修正

#### `src/komon/notification.py` の `send_notification()` 関数

```python
def send_notification(message: str, metric_type: str = None, 
                     threshold_level: str = None, 
                     current_value: float = None) -> bool:
    """
    通知を送信する（頻度制御を含む）
    
    Args:
        message: 通知メッセージ
        metric_type: メトリクスタイプ（'cpu', 'memory', 'disk'）
        threshold_level: 閾値レベル（'warning', 'alert', 'critical'）
        current_value: 現在の値
        
    Returns:
        送信成功したか
    """
    # 頻度制御の判定
    if metric_type and threshold_level:
        throttle = NotificationThrottle(settings.get('throttle', {}))
        should_send, reason = throttle.should_send_notification(
            metric_type, threshold_level, current_value
        )
        
        if not should_send:
            logger.info(f"通知を抑制しました: {metric_type}, 理由: {reason}")
            return False
        
        if reason == "escalation":
            # エスカレーションメッセージを追加
            duration = _calculate_duration(throttle, metric_type)
            message = f"{message}\n\n⏰ {duration}経過しましたが、まだ高い状態が続いています"
    
    # 既存の送信処理
    success = _send_to_slack(message) or _send_to_email(message)
    
    # 送信成功時に履歴を記録
    if success and metric_type and threshold_level:
        throttle.record_notification(metric_type, threshold_level, current_value)
    
    return success
```

## 判定ロジック

### 通知送信判定フローチャート

```
開始
  │
  ▼
頻度制御が有効か？
  │
  ├─ No ─→ 通知送信
  │
  ▼ Yes
履歴ファイルを読み込み
  │
  ▼
該当メトリクスの履歴あり？
  │
  ├─ No ─→ 通知送信（初回）
  │
  ▼ Yes
閾値レベルが上昇？
  │
  ├─ Yes ─→ 通知送信（レベルアップ）
  │
  ▼ No
前回通知からの経過時間を計算
  │
  ▼
経過時間 < 通知間隔？
  │
  ├─ Yes ─→ 通知抑制
  │
  ▼ No
経過時間 >= 再通知間隔？
  │
  ├─ Yes ─→ 通知送信（エスカレーション）
  │
  ▼ No
通知送信（通常）
```

### 閾値レベル判定

```python
LEVEL_ORDER = {
    'warning': 1,
    'alert': 2,
    'critical': 3
}

def _is_level_escalated(previous_level: str, current_level: str) -> bool:
    """閾値レベルが上昇したかを判定"""
    return LEVEL_ORDER.get(current_level, 0) > LEVEL_ORDER.get(previous_level, 0)
```

## 正確性プロパティ

*プロパティとは、システムの全ての有効な実行において真であるべき特性や振る舞いのことです。本質的には、システムが何をすべきかについての形式的な記述です。プロパティは、人間が読める仕様と機械で検証可能な正確性保証との橋渡しをします。*

### プロパティ1: 通知抑制の正確性
*任意の*同一メトリクスの通知について、設定された間隔内に2回以上送信されない（閾値レベル上昇を除く）
**検証対象: 要件 AC-001.2**

### プロパティ2: 閾値レベル上昇時の即時通知
*任意の*閾値レベル上昇について、通知間隔に関わらず即座に通知される
**検証対象: 要件 AC-002.2**

### プロパティ3: エスカレーションの正確性
*任意の*再通知間隔を超えた問題について、エスカレーション通知が送信される
**検証対象: 要件 AC-003.2**

### プロパティ4: 履歴ファイルの整合性
*任意の*通知履歴について、ファイルの読み書きが正しく行われデータが失われない
**検証対象: 要件 AC-004.1, AC-004.5**

### プロパティ5: 設定無効時の動作
*任意の*頻度制御無効時について、全ての通知が抑制なしで送信される
**検証対象: 要件 AC-005.5**

## テスト戦略

### プロパティベーステスト

Pythonの`hypothesis`ライブラリを使用します。

**設定:**
- 最小実行回数: 100回
- タイムアウト: テストごとに30秒

**テスト対象:**
- プロパティ1: 通知抑制の正確性
- プロパティ2: 閾値レベル上昇時の即時通知
- プロパティ3: エスカレーションの正確性
- プロパティ4: 履歴ファイルの整合性
- プロパティ5: 設定無効時の動作

**テストファイル:** `tests/test_notification_throttle_properties.py`

### ユニットテスト

Pythonの標準`unittest`フレームワークを使用します。

**テスト対象:**
- NotificationThrottleクラスの各メソッド
- 閾値レベル判定ロジック
- 履歴ファイルの読み書き
- エラーハンドリング

**テストファイル:** `tests/test_notification_throttle.py`

### 統合テスト

**テストシナリオ:**
1. send_notification()関数との統合
2. 既存の通知機能との互換性
3. 設定ファイルの読み込み

**テストファイル:** `tests/test_notification_integration.py`

### 手動テスト

**確認項目:**
1. 実際の通知発生時に抑制が機能するか
2. 閾値レベル上昇時に即座に通知されるか
3. エスカレーション通知が正しく送信されるか
4. プロセス再起動後も履歴が保持されるか

## 元の正確性プロパティ詳細

### P1: 通知抑制の正確性
**プロパティ**: 同一メトリクスの通知が、設定された間隔内に2回以上送信されない（閾値レベル上昇を除く）

**検証方法**:
```python
@given(
    metric_type=st.sampled_from(['cpu', 'memory', 'disk']),
    threshold_level=st.sampled_from(['warning', 'alert', 'critical']),
    interval_minutes=st.integers(min_value=1, max_value=120)
)
def test_throttle_interval(metric_type, threshold_level, interval_minutes):
    """通知間隔が正しく機能することを検証"""
    throttle = NotificationThrottle({'interval_minutes': interval_minutes})
    
    # 1回目の通知
    should_send_1, _ = throttle.should_send_notification(
        metric_type, threshold_level, 80.0
    )
    assert should_send_1 is True
    throttle.record_notification(metric_type, threshold_level, 80.0)
    
    # 間隔内の2回目の通知（同じレベル）
    should_send_2, _ = throttle.should_send_notification(
        metric_type, threshold_level, 81.0
    )
    assert should_send_2 is False
```

### P2: 閾値レベル上昇時の即時通知
**プロパティ**: 閾値レベルが上昇した場合、通知間隔に関わらず即座に通知される

**検証方法**:
```python
@given(
    metric_type=st.sampled_from(['cpu', 'memory', 'disk']),
    previous_level=st.sampled_from(['warning', 'alert']),
    interval_minutes=st.integers(min_value=1, max_value=120)
)
def test_level_escalation_immediate(metric_type, previous_level, interval_minutes):
    """閾値レベル上昇時に即座に通知されることを検証"""
    throttle = NotificationThrottle({'interval_minutes': interval_minutes})
    
    # 1回目の通知
    throttle.record_notification(metric_type, previous_level, 75.0)
    
    # レベルが上昇した場合（間隔内でも通知される）
    next_level = 'critical' if previous_level == 'alert' else 'alert'
    should_send, reason = throttle.should_send_notification(
        metric_type, next_level, 85.0
    )
    assert should_send is True
    assert reason == "level_up"
```

### P3: エスカレーションの正確性
**プロパティ**: 再通知間隔を超えた場合、エスカレーション通知が送信される

**検証方法**:
```python
@given(
    metric_type=st.sampled_from(['cpu', 'memory', 'disk']),
    threshold_level=st.sampled_from(['warning', 'alert', 'critical']),
    escalation_minutes=st.integers(min_value=60, max_value=360)
)
def test_escalation_timing(metric_type, threshold_level, escalation_minutes):
    """エスカレーションが正しいタイミングで発生することを検証"""
    throttle = NotificationThrottle({
        'interval_minutes': 60,
        'escalation_minutes': escalation_minutes
    })
    
    # 初回通知
    throttle.record_notification(metric_type, threshold_level, 80.0)
    
    # 再通知間隔を超えた場合
    # （実際のテストでは時刻を操作する）
    should_send, reason = throttle.should_send_notification(
        metric_type, threshold_level, 80.0
    )
    # escalation_minutes経過後はエスカレーション通知が送信される
    assert reason in ["escalation", "throttled"]
```

### P4: 履歴ファイルの整合性
**プロパティ**: 履歴ファイルの読み書きが正しく行われ、データが失われない

**検証方法**:
```python
@given(
    notifications=st.lists(
        st.tuples(
            st.sampled_from(['cpu', 'memory', 'disk']),
            st.sampled_from(['warning', 'alert', 'critical']),
            st.floats(min_value=0.0, max_value=100.0)
        ),
        min_size=1,
        max_size=10
    )
)
def test_history_persistence(notifications):
    """履歴ファイルの永続化が正しく機能することを検証"""
    throttle = NotificationThrottle({'interval_minutes': 60})
    
    # 複数の通知を記録
    for metric_type, threshold_level, value in notifications:
        throttle.record_notification(metric_type, threshold_level, value)
    
    # 新しいインスタンスで履歴を読み込み
    throttle2 = NotificationThrottle({'interval_minutes': 60})
    history = throttle2._load_history()
    
    # 最後の通知が正しく記録されている
    last_metric, last_level, last_value = notifications[-1]
    assert last_metric in history
    assert history[last_metric]['threshold_level'] == last_level
```

### P5: 設定無効時の動作
**プロパティ**: 頻度制御が無効の場合、全ての通知が送信される

**検証方法**:
```python
@given(
    metric_type=st.sampled_from(['cpu', 'memory', 'disk']),
    threshold_level=st.sampled_from(['warning', 'alert', 'critical']),
    notification_count=st.integers(min_value=1, max_value=10)
)
def test_throttle_disabled(metric_type, threshold_level, notification_count):
    """頻度制御無効時に全通知が送信されることを検証"""
    throttle = NotificationThrottle({'enabled': False})
    
    for _ in range(notification_count):
        should_send, _ = throttle.should_send_notification(
            metric_type, threshold_level, 80.0
        )
        assert should_send is True
        throttle.record_notification(metric_type, threshold_level, 80.0)
```

## エラーハンドリング

### ファイルI/Oエラー
- 履歴ファイルの読み込みに失敗した場合、空の履歴として扱う
- 履歴ファイルの書き込みに失敗した場合、ログに記録するが通知は送信する

### 設定エラー
- 設定が不正な場合、デフォルト値を使用する
- 負の値や0が設定された場合、デフォルト値を使用する

### データ破損
- JSONパースエラーが発生した場合、履歴ファイルを削除して新規作成する

## パフォーマンス考慮事項

### ファイルI/O最適化
- 履歴ファイルは通知送信時のみ読み書きする
- ファイルサイズは常に小さい（3メトリクス分のみ）

### メモリ使用量
- 履歴データは最小限（メトリクスタイプごとに1レコード）
- 古いデータは自動的に上書きされる

## テスト戦略

### プロパティベーステスト（hypothesis）
- P1〜P5の正確性プロパティを検証
- 様々な入力パターンで動作を確認

### ユニットテスト
- NotificationThrottleクラスの各メソッド
- 閾値レベル判定ロジック
- 履歴ファイルの読み書き
- エラーハンドリング

### 統合テスト
- send_notification()関数との統合
- 既存の通知機能との互換性
- 設定ファイルの読み込み

## 実装の優先順位

1. NotificationThrottleクラスの基本実装
2. 履歴ファイルの読み書き
3. 通知抑制ロジック
4. 閾値レベル上昇判定
5. エスカレーション機能
6. 既存コードとの統合
7. テストの追加

## 依存関係

- `datetime`: 時刻計算
- `json`: 履歴ファイルの読み書き
- `pathlib`: ファイルパス操作
- `logging`: ログ出力

## 後方互換性

- 既存の通知機能は変更なし
- 頻度制御を無効にすれば従来通りの動作
- 履歴ファイルが存在しなくても動作する

## 将来の拡張性

- 通知チャネルごとの個別制御
- メトリクスタイプごとの個別設定
- 通知履歴のWeb UI表示
