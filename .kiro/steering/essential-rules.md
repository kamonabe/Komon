---
inclusion: always
---

# 開発基本ルール

## プロジェクト概要

設定値は `project-config.yml` を参照。このファイルには判断基準のみ記載する。

## コミュニケーション

- ユーザーとの会話: 日本語
- コード（変数名・関数名）: 英語
- コミットメッセージ: 日本語（type部分は英語）
- ユーザー向けエラーメッセージ: 日本語（原因と対処法を記載）
- ログ・例外メッセージ: 英語

## セキュリティ（最優先・即時中断）

以下のパターンを検知したら即座に処理を中断し警告する:

- APIキー: `sk-`, `AKIA[0-9A-Z]{16}`
- Webhook URL: `https://hooks.slack.com/services/`
- パスワード: `password\s*[:=]\s*["'][^"']+["']`
- 秘密鍵: `BEGIN PRIVATE KEY`
- トークン: `ghp_`, `gho_`, `github_pat_`

検知時の対応:
```
🚨 機密情報を検知しました
1. 環境変数に移行してください
2. 既にコミットした場合は即座に無効化してください
処理を中断します。
```

## 開発フローの原則

1. アイデア → `future-ideas.md` に記録
2. 実装決定 → `implementation-tasks.md` に TASK-XXX として追加
3. Spec作成 → `.kiro/specs/{feature-name}/` に YAML形式で作成（mainブランチでOK）
4. 実装 → 開発ブランチで実施（hookが自動でブランチ安全性を検証）
5. 完了 → テスト・カバレッジ確認後、mainにマージ・タグ作成

## ブランチルール

- mainブランチ: ドキュメント・Spec作成のみ
- 開発ブランチ: コード実装・テスト追加（`feature/task-XXX-{name}`, `bugfix/{desc}`, `refactor/{module}`）
- コード変更時のmainブランチ保護はhookで自動検証される

## テスト基準

- カバレッジ目標: `project-config.yml` の `testing.coverage_target` を参照
- 3層構造: プロパティテスト（hypothesis）→ 統合テスト → ユニットテスト
- 外部API: モック必須、ファイルI/O: `tmp_path` 使用、内部モジュール: モックしない

## バージョニング

Semantic Versioning準拠。判断フロー:
1. 破壊的変更あり → MAJOR
2. 新機能追加あり → MINOR
3. バグ修正・小改善 → PATCH
4. 開発者向け改善のみ → バージョンアップなし

## ルール参照テーブル

| 状況 | 参照ファイル | inclusion |
|------|-------------|-----------|
| コード実装時 | `development-workflow.md` | auto |
| Git操作時 | `git-workflow.md` | auto |
| テスト作成時 | `testing-strategy.md` | auto |
| Pythonファイル編集時 | `error-handling-and-logging.md` | fileMatch: src/**/*.py |
| タスクファイル編集時 | `task-management.md` | fileMatch: .kiro/tasks/** |
| Specファイル編集時 | `spec-quality-assurance.md` | fileMatch: .kiro/specs/** |
| バージョン決定時 | `#versioning-rules` | manual |
| リリース作業時 | `#release-process` | manual |
| コミット作成時 | `#commit-message-rules` | manual |
| Git/SSH設定時 | `#git-ssh-setup` | manual |
