---
rule-id: essential-rules
priority: critical
applies-to: [all-projects]
triggers: [always]
description: 全プロジェクト共通の必須ルール（軽量版）
---

# 全プロジェクト共通 必須ルール

このファイルには**全プロジェクト共通**の最低限の必須ルールのみを記載しています。
詳細なルールは必要に応じて `.kiro/steering-detailed/` から読み込みます。

---

## 🌍 基本環境

### 開発に必要なもの
- **コンピューター**: Windows/Mac/Linux どれでもOK
- **インターネット**: GitHubに接続するため
- **やる気**: これが一番大事！

### 初めての方へ
👉 **[初心者向けオンボーディングガイド](.kiro/steering-detailed/onboarding/00-welcome.md)**

Linux/Git初心者でも1週間で開発に参加できるようになります！

### 経験者の方へ（技術仕様）
- **プラットフォーム**: AlmaLinux 9（RHEL系Linux）
- **シェル**: bash
- **パッケージ管理**: dnf/yum
- **Python**: 3.10+以上

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
- `requirements.yml`, `design.yml`, `tasks.yml` を作成（YAML構造化形式）

### 3. 実装開始前の必須チェック
```bash
git branch  # 必ず確認！
```
- ✅ 開発ブランチ → 実装開始
- ❌ mainブランチ → 危険警告、ブランチ作成を指示

### 4. 実装 → テスト → リリース
- コード実装（開発ブランチ）
- テスト作成（カバレッジ90%以上目標）
- mainにマージ → タグ作成

---

## 📚 詳細ルール参照（キーワード検知）

詳細が必要な場合は以下を読み込み：

### 開発関連キーワード
**検知語**: 「実装」「コード」「テスト」「品質」「カバレッジ」
- **開発ワークフロー**: `steering-detailed/development/workflow.md`
- **テスト戦略**: `steering-detailed/development/testing-strategy.md`
- **品質管理**: `steering-detailed/development/quality-management.md`

### Git操作キーワード
**検知語**: 「ブランチ」「マージ」「コミット」「push」「pull」
- **Git運用**: `steering-detailed/git/git-workflow.md`
- **ブランチ戦略**: `steering-detailed/git/branch-strategy.md`

### タスク管理キーワード
**検知語**: 「タスク」「進捗」「TASK-」「やること」「スケジュール」
- **タスク管理**: `steering-detailed/task/task-management.md`
- **進捗追跡**: `steering-detailed/task/progress-tracking.md`

### リリース関連キーワード
**検知語**: 「リリース」「バージョン」「公開」「タグ」「PyPI」
- **バージョニング**: `steering-detailed/release/versioning-rules.md`
- **リリースプロセス**: `steering-detailed/release/release-process.md`

---

## ⚡ Context効率化

| シーン | 読み込み量 | 削減率 |
|--------|-----------|--------|
| 簡単な質問 | 200行 | **96%削減** |
| 開発作業 | 200行 + 開発ルール | **70%削減** |
| Git操作 | 200行 + Gitルール | **85%削減** |
| リリース作業 | 200行 + リリースルール | **75%削減** |

**メリット**:
- 初期応答が超高速
- 必要な情報だけ読み込み
- セッション時間の大幅延長

---

## 🎯 適用プロジェクト

- ✅ Komon
- ✅ Okina
- 🔄 今後の新プロジェクト全て

---

**最終更新**: 2025-01-05
**ファイルサイズ**: 約200行