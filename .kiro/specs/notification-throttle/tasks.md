---
title: 通知頻度制御（同一アラートの抑制）- 実装タスク
feature: notification-throttle
status: completed
created: 2025-11-24
updated: 2025-11-24
completed: 2025-11-24
---

# 通知頻度制御（同一アラートの抑制）- 実装タスク

## タスクチェックリスト

- [x] 1. NotificationThrottleクラスの実装
  - NotificationThrottleクラスの基本構造を作成
  - __init__メソッドで設定を読み込み
  - should_send_notification()メソッドの骨格を作成
  - record_notification()メソッドの骨格を作成
  - _要件: AC-001, AC-002, AC-003_

- [x] 2. 通知履歴ファイルの読み書き機能
  - _load_history()メソッドの実装
  - _save_history()メソッドの実装
  - JSONファイルの読み書き処理
  - エラーハンドリング（ファイル不在、破損対応）
  - _要件: AC-004.1, AC-004.2, AC-004.3, AC-004.4_

- [x] 3. 通知抑制ロジックの実装
  - 前回通知からの経過時間計算
  - 通知間隔との比較
  - 抑制判定ロジック
  - _要件: AC-001.1, AC-001.2, AC-001.3_

- [x] 4. 閾値レベル上昇判定の実装
  - _is_level_escalated()メソッドの実装
  - 閾値レベルの順序定義
  - レベル上昇時の即時通知ロジック
  - _要件: AC-002.1, AC-002.2, AC-002.4_

- [x] 5. エスカレーション機能の実装
  - 初回発生時刻の記録
  - 継続時間の計算
  - 再通知間隔の判定
  - エスカレーションメッセージの生成
  - _要件: AC-003.1, AC-003.2, AC-003.3_

- [x] 6. 既存コードとの統合
  - send_notification()関数の修正
  - NotificationThrottleの呼び出し
  - エスカレーションメッセージの追加
  - _要件: AC-006.1, AC-006.2, AC-006.3_

- [x] 7. 設定ファイルの更新
  - throttle設定セクションの追加
  - デフォルト値の設定
  - コメントの追加
  - _要件: AC-005.1, AC-005.2, AC-005.3_

- [x] 8. プロパティベーステストの追加
  - プロパティ1: 通知抑制の正確性
  - プロパティ2: 閾値レベル上昇時の即時通知
  - プロパティ3: エスカレーションの正確性
  - プロパティ4: 履歴ファイルの整合性
  - プロパティ5: 設定無効時の動作
  - _要件: AC-001, AC-002, AC-003, AC-004, AC-005_

- [x] 9. ユニットテストの追加
  - NotificationThrottleクラスの各メソッド
  - 閾値レベル判定ロジック
  - 履歴ファイルの読み書き
  - エラーハンドリング
  - _要件: 全て_

- [x] 10. 統合テストの追加
  - send_notification()関数との統合
  - 既存の通知機能との互換性
  - 設定ファイルの読み込み
  - _要件: AC-006_

- [x] 11. ドキュメント更新
  - README.mdに通知頻度制御の説明を追加
  - 設定例の追加
  - CHANGELOG.mdにv1.15.0の変更を記録
  - _要件: 全て_

- [x] 12. 全テスト実行と確認
  - pytest実行
  - カバレッジ確認（95%以上）
  - 既存機能の動作確認
  - _要件: AC-006.1_

## 詳細

### 1. NotificationThrottleクラスの実装
**ファイル**: `src/komon/notification.py`

- NotificationThrottleクラスの基本構造を作成
- __init__メソッドで設定を読み込み
- should_send_notification()メソッドの骨格を作成
- record_notification()メソッドの骨格を作成

### 2. 通知履歴ファイルの読み書き機能
**ファイル**: `src/komon/notification.py`

- _load_history()メソッドの実装
- _save_history()メソッドの実装
- JSONファイルの読み書き処理
- エラーハンドリング（ファイル不在、破損対応）

### 3. 通知抑制ロジックの実装
**ファイル**: `src/komon/notification.py`

- 前回通知からの経過時間計算
- 通知間隔との比較
- 抑制判定ロジック

### 4. 閾値レベル上昇判定の実装
**ファイル**: `src/komon/notification.py`

- _is_level_escalated()メソッドの実装
- 閾値レベルの順序定義
- レベル上昇時の即時通知ロジック

### 5. エスカレーション機能の実装
**ファイル**: `src/komon/notification.py`

- 初回発生時刻の記録
- 継続時間の計算
- 再通知間隔の判定
- エスカレーションメッセージの生成

### 6. 既存コードとの統合
**ファイル**: `src/komon/notification.py`

- send_notification()関数の修正
- NotificationThrottleの呼び出し
- エスカレーションメッセージの追加

### 7. 設定ファイルの更新
**ファイル**: `settings.yml`, `config/settings.yml.sample`

- throttle設定セクションの追加
- デフォルト値の設定
- コメントの追加

### 8. プロパティベーステストの追加
**ファイル**: `tests/test_notification_throttle_properties.py`

- P1: 通知抑制の正確性
- P2: 閾値レベル上昇時の即時通知
- P3: エスカレーションの正確性
- P4: 履歴ファイルの整合性
- P5: 設定無効時の動作

### 9. ユニットテストの追加
**ファイル**: `tests/test_notification_throttle.py`

- NotificationThrottleクラスの各メソッド
- 閾値レベル判定ロジック
- 履歴ファイルの読み書き
- エラーハンドリング

### 10. 統合テストの追加
**ファイル**: `tests/test_notification_integration.py`

- send_notification()関数との統合
- 既存の通知機能との互換性
- 設定ファイルの読み込み

### 11. ドキュメント更新
**ファイル**: `README.md`, `docs/CHANGELOG.md`

- README.mdに通知頻度制御の説明を追加
- 設定例の追加
- CHANGELOG.mdにv1.15.0の変更を記録

### 12. 全テスト実行と確認
- pytest実行
- カバレッジ確認（95%以上）
- 既存機能の動作確認

## 実装順序

1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12

## 見積もり

- 実装: 4-5時間
- テスト: 2-3時間
- 合計: 6-8時間
