---
title: 通知頻度制御（同一アラートの抑制）- 実装タスク
feature: notification-throttle
status: completed
created: 2025-11-24
updated: 2025-11-24
completed: 2025-11-24
---

# 通知頻度制御（同一アラートの抑制）- 実装タスク

## タスク一覧

- [x] 1. NotificationThrottleクラスの実装
- [x] 2. 通知履歴ファイルの読み書き機能
- [x] 3. 通知抑制ロジックの実装
- [x] 4. 閾値レベル上昇判定の実装
- [x] 5. エスカレーション機能の実装
- [x] 6. 既存コードとの統合
- [x] 7. 設定ファイルの更新
- [x] 8. プロパティベーステストの追加
- [x] 9. ユニットテストの追加
- [x] 10. 統合テストの追加
- [x] 11. ドキュメント更新
- [x] 12. 全テスト実行と確認

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
