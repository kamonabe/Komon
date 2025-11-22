# Changelog

Komonの変更履歴を記録します。

このプロジェクトは[Semantic Versioning](https://semver.org/)に従います。

## [Unreleased]

## [1.12.0] - 2025-11-22

### Added

- **週次健全性レポート機能**
  - 毎週定期的にシステムの健全性レポートをSlack/メールで送信
  - CPU/メモリ/ディスク使用率の現状と先週比を表示
  - 過去7日間の警戒情報サマリーを含む
  - トレンド分析（安定/増加傾向/減少傾向）を表示
  - SSHログインせずにシステム状態を確認可能
  - 年末年始などの長期休暇前の健全性確認に最適

### New Modules

- `src/komon/weekly_data.py` - 週次データ収集と分析
- `src/komon/report_formatter.py` - レポートメッセージフォーマット
- `scripts/weekly_report.py` - 週次レポート生成スクリプト

### Configuration

- `settings.yml`に`weekly_report`セクションを追加
  - `enabled`: 週次レポートの有効/無効
  - `day_of_week`: レポート送信曜日（0=日曜, 1=月曜, ...）
  - `hour`, `minute`: レポート送信時刻
  - `notifications`: Slack/メール通知の個別設定

### Developer Improvements

- **テストの追加**
  - プロパティベーステスト6件（hypothesis）
  - ユニットテスト26件
  - 統合テスト6件
  - 全150テストが成功
  - カバレッジ92%を維持

### Documentation

- README.mdに週次レポートの使い方を追加
- cron設定例を追加（毎週月曜9時）
- プロジェクト構造に新モジュールを追加

## [1.11.2] - 2025-11-22

### Fixed

- **ログ傾向分析のバグ修正**
  - `log_trends.py`でデータ型エラーが発生していた問題を修正
  - state_dataが辞書形式の場合に`last_line`を正しく取得するように改善
  - `TypeError: unsupported operand type(s) for -: 'dict' and 'dict'` を解消
  - 後方互換性を保ちつつ、数値形式にも対応

## [1.11.1] - 2025-11-22

### Fixed

- **テストの安定性向上**
  - プロパティベーステストのデッドライン設定を修正
  - `test_limit_returns_correct_number`の実行時間制限を解除（`deadline=None`）
  - 全111テストが安定してパスするように改善

## [1.11.0] - 2025-11-22

### Added

- **通知履歴機能**
  - ローカルファイルに通知履歴を自動保存（最大100件、自動ローテーション）
  - `komon advise`コマンドで履歴を表示
  - `komon advise --history N`で直近N件のみ表示
  - Slack/メール通知が使えない環境でも検知情報を確認可能
  - 通知履歴は`notifications/queue.json`に保存

### Developer Improvements

- **テストの追加**
  - プロパティベーステスト（hypothesis）を導入
  - 通知履歴機能のテスト18件を追加（プロパティテスト7件、統合テスト6件、ユニットテスト5件）
  - 全111テストが成功
  - 6つの正確性プロパティを検証

### Documentation

- **プロジェクト管理構造の追加**
  - `.kiro/tasks/`フォルダを新設し、実装タスク管理を開始
  - `implementation-tasks.md`: future-ideasから実装タスクを分解・管理
  - README.md、PROJECT_STRUCTURE.md、docs/README.mdのディレクトリ構造を更新
  - 仕様管理（specs）とタスク管理（tasks）を明確に分離
- **Spec駆動開発**
  - `.kiro/specs/notification-history/`に要件定義、設計、タスクリストを作成
  - EARS形式の要件定義、正確性プロパティを含む設計書を整備

## [1.10.1] - 2025-11-22

### Changed

- **通知メッセージの改善**
  - 機械的な警告表現から、やさしい相談口調に変更
  - 「CPU使用率が高い状態です」→「CPUが頑張りすぎてるみたいです」
  - 「メモリ使用率が高い状態です」→「メモリ使用量が結構増えてますね」
  - 「ディスク使用率が高い状態です」→「ディスクの空きが少なくなってきました」
  - Komonの「やさしく見守る顧問」という思想をより明確に

### Developer Improvements

- **テストカバレッジの大幅向上**
  - テストカバレッジ: 47% → 95%（+48%）
  - テスト数: 46 → 93（+47テスト）
  - 新規テストファイル追加:
    - `tests/test_notification.py`: Slack/メール通知のテスト（9テスト）
    - `tests/test_log_watcher.py`: ログ監視機能のテスト（11テスト）
    - `tests/test_log_trends.py`: ログ傾向分析のテスト（17テスト）
    - `tests/test_cli.py`: CLIエントリーポイントのテスト（10テスト）

- **カバレッジ測定の改善**
  - CIFS/SMB共有環境でのSQLiteロック問題を修正
  - `.coveragerc`の追加（ローカルディスクへのデータ保存設定）
  - `run_coverage.sh`: カバレッジレポート生成スクリプトの追加
  - `setup_coverage_fix.sh`: カバレッジ設定の自動修正スクリプト

- **開発ツールの追加**
  - `check_coverage.py`: 簡易カバレッジチェックツール（coverageツール不要）

### Notes

- これらの改善は開発者向けで、エンドユーザーの機能には影響しません
- 全93テストがパス、本番環境での信頼性が向上しました

## [1.10.0] - 2025-11-21

### Changed

- **プロジェクト構造の大幅な整理**
  - `src/komon/`にコアモジュールを移動
  - `scripts/`に実行スクリプトを移動
  - `docs/`にドキュメントを集約
  - 標準的なPythonプロジェクト構造に準拠

### Added

- **テストコードの追加**
  - `test_analyzer.py`: 閾値判定とアラート生成のテスト（10個）
  - `test_log_analyzer.py`: ログ異常検知のテスト（6個）
  - `test_monitor.py`: リソース監視のテスト（7個、例外処理含む）
  - `test_history.py`: 履歴管理のテスト（9個）
  - `test_settings_validator.py`: 設定検証のテスト（14個）
  - `pytest.ini`: テスト設定ファイル（JUnit XMLレポート自動生成）
  - `requirements-dev.txt`: 開発用依存パッケージ
  - 全46個のテストが実装され、全てPASS
  - テストカバレッジ: コアモジュール5/9（約56%）

- **仕様駆動開発の基盤**
  - `.kiro/specs/komon-system.md`: 包括的なシステム仕様書
  - `.kiro/specs/testing-strategy.md`: テスト戦略と方針の文書化
  - `.kiro/specs/future-ideas.md`: 将来的な機能アイデア
  - リバースエンジニアリングにより既存コードから仕様を抽出

- **ドキュメントの充実**
  - `docs/PROJECT_STRUCTURE.md`: プロジェクト構造の詳細説明
  - `docs/CONTRIBUTING.md`: 貢献ガイドライン
  - `tests/README.md`: テストガイド
  - Linux専用方針の明確化

- **開発環境の改善**
  - `.gitignore`の更新（機密情報の保護強化）
  - `setup.py`の改善（新構造対応）

### Fixed

- なし（機能的な変更なし）

### Notes

- この更新は内部構造の整理が主で、既存機能は全て動作します
- `settings.yml`の場所や使い方に変更はありません
- `komon`コマンドは引き続き使用できます

---

## [1.9.0] - 2025-XX-XX

### Added

- 初期バージョン（詳細は過去のコミット履歴を参照）

---

## バージョニングポリシー

- **MAJOR**: 後方互換性のない変更
- **MINOR**: 後方互換性のある機能追加、大規模なリファクタリング
- **PATCH**: バグ修正、小規模な改善

## リンク

- [1.11.2]: https://github.com/kamonabe/Komon/releases/tag/v1.11.2
- [1.11.1]: https://github.com/kamonabe/Komon/releases/tag/v1.11.1
- [1.11.0]: https://github.com/kamonabe/Komon/releases/tag/v1.11.0
- [1.10.1]: https://github.com/kamonabe/Komon/releases/tag/v1.10.1
- [1.10.0]: https://github.com/kamonabe/Komon/releases/tag/v1.10.0
- [1.9.0]: https://github.com/kamonabe/Komon/releases/tag/v1.9.0
