# Changelog

Komonの変更履歴を記録します。

このプロジェクトは[Semantic Versioning](https://semver.org/)に従います。

## [Unreleased]

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

- [1.10.1]: https://github.com/kamonabe/Komon/releases/tag/v1.10.1
- [1.10.0]: https://github.com/kamonabe/Komon/releases/tag/v1.10.0
- [1.9.0]: https://github.com/kamonabe/Komon/releases/tag/v1.9.0
