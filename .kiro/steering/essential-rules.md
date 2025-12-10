---
rule-id: essential-rules
priority: critical
applies-to: [all]
triggers: [always]
description: 最低限の必須ルール（軽量版）
---

# 必須ルール（軽量版）

このファイルには最低限の必須ルールのみを記載しています。
詳細なルールは必要に応じて `.kiro/steering-detailed/` から読み込みます。

---

## 🌍 基本環境

### プラットフォーム
- **AlmaLinux 9**（RHEL系Linux）
- **シェル**: bash
- **パッケージ管理**: dnf/yum

### 基本コマンド
```bash
# 使用可能
ls, cat, grep, git, python, pip

# 使用禁止
findstr, dir, type (Windowsコマンド)
```

---

## 💬 コミュニケーション

### 言語ルール
- **ユーザーとの会話**: 必ず日本語
- **コード**: 変数名・関数名は英語
- **コミットメッセージ**: 日本語推奨

### エラーメッセージ
- **ユーザー向け**: 日本語、原因と対処法を記載
- **ログ**: 英語、詳細な技術情報

---

## 🚨 セキュリティ（最重要）

### 機密情報検知（即座に処理中断）
以下を検知したら**即座に処理を中断**し警告：

- **APIキー**: `sk-`, `AKIA[0-9A-Z]{16}`
- **Webhook URL**: `https://hooks.slack.com/services/`
- **パスワード**: `password\s*[:=]\s*["'][^"']+["']`
- **秘密鍵**: `BEGIN PRIVATE KEY`

### 対応方法
```
🚨 機密情報を検知しました

【推奨対応】
1. 環境変数に移行: webhook_url: "env:SLACK_WEBHOOK"
2. 既存の情報を無効化

処理を中断します。安全化してから再度お試しください。
```

---

## 🔧 開発の基本フロー

### 1. アイデア → タスク化
- `future-ideas.md` でアイデア管理
- 実装決定 → `implementation-tasks.md` に TASK-XXX として追加

### 2. Spec作成（mainブランチ）
- `.kiro/specs/{feature-name}/` フォルダ作成
- `requirements.yml`, `design.yml`, `tasks.yml` を作成

### 3. 実装開始前の必須チェック
```bash
git branch  # 必ず確認！
```
- ✅ 開発ブランチ → 実装開始
- ❌ mainブランチ → 危険警告、ブランチ作成を指示

### 4. 実装 → テスト → リリース
- コード実装（開発ブランチ）
- テスト作成（カバレッジ95%目標）
- mainにマージ → タグ作成

---

## 📚 詳細ルール参照

詳細が必要な場合は以下を読み込み：

### 開発関連
- **開発ワークフロー**: `steering-detailed/development-workflow.md`
- **Git運用**: `steering-detailed/git-workflow.md`
- **テスト戦略**: `steering-detailed/testing-strategy.md`
- **エラーハンドリング**: `steering-detailed/error-handling-and-logging.md`

### 管理関連
- **バージョニング**: `steering-detailed/versioning-rules.md`
- **タスク管理**: `steering-detailed/task-management.md`
- **Spec品質保証**: `steering-detailed/spec-quality-assurance.md`
- **リリースプロセス**: `steering-detailed/release-process.md`

### その他
- **コミットメッセージ**: `steering-detailed/commit-message-rules.md`

---

## 🎯 Kiroへの指示

### 初期読み込み
このファイル（essential-rules.md）のみを読み込む

### 詳細が必要な場合（自動判定）
以下のキーワードで自動的に詳細ルールを読み込む：

#### **バージョニング関連**
- キーワード: 「バージョン」「リリース」「MAJOR」「MINOR」「PATCH」
- 読み込み: `steering-detailed/versioning-rules.md`

#### **実装開始時**
- キーワード: 「TASK-XXXを実装」「実装しよう」「開発開始」
- 読み込み: 
  - `steering-detailed/development-workflow.md`
  - `steering-detailed/git-workflow.md`
  - `steering-detailed/testing-strategy.md`
  - `steering-detailed/error-handling-and-logging.md`

#### **Git操作関連**
- キーワード: 「ブランチ」「マージ」「コミット」「push」
- 読み込み: `steering-detailed/git-workflow.md`

#### **テスト関連**
- キーワード: 「テスト」「カバレッジ」「プロパティテスト」
- 読み込み: `steering-detailed/testing-strategy.md`

#### **タスク管理関連**
- キーワード: 「タスク番号」「TASK-」「implementation-tasks」
- 読み込み: `steering-detailed/task-management.md`

#### **Spec作成関連**
- キーワード: 「Spec」「requirements」「design」「品質保証」
- 読み込み: `steering-detailed/spec-quality-assurance.md`

#### **リリース関連**
- キーワード: 「リリース」「GitHub Releases」「PyPI」
- 読み込み: `steering-detailed/release-process.md`

#### **エラー・ログ関連**
- キーワード: 「エラー」「ログ」「例外」「print」「logging」
- 読み込み: `steering-detailed/error-handling-and-logging.md`

#### **コミットメッセージ関連**
- キーワード: 「コミットメッセージ」「Conventional Commits」
- 読み込み: `steering-detailed/commit-message-rules.md`

### 読み込み時の表示（自動判定）
```
� キ細ーワード「バージョン」を検知
📚 steering-detailed/versioning-rules.md を読み込んでいます...
✅ 詳細なバージョニングルールを取得しました

🔍 キーワード「TASK-003を実装」を検知  
📚 実装に必要なルールを読み込んでいます...
✅ development-workflow.md
✅ git-workflow.md
✅ testing-strategy.md
✅ error-handling-and-logging.md
```

---

## ⚡ Context効率化

| シーン | 読み込み量 | 削減率 |
|--------|-----------|--------|
| 簡単な質問 | 200行 | **96%削減** |
| 詳細な質問 | 200行 + 詳細1ファイル | **90%削減** |
| 実装開始 | 200行 + 必要ルール4-5ファイル | **60%削減** |

**メリット**:
- 初期応答が超高速
- 必要な情報だけ読み込み
- 実装時も必要最小限

---

**最終更新**: 2025-12-10
**ファイルサイズ**: 約200行