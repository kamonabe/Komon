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

### 🤖 自動実行フロー（必須）

**STEP 1**: メッセージ受信時に必ず実行
```python
# セッション内キャッシュを使用した効率的な読み込み
from .session_cache import cached_read_file
from .keyword_detector import KeywordDetector

detector = KeywordDetector()
instructions = detector.generate_load_instructions(user_message)

# 検知結果に基づいて詳細ルール読み込み（キャッシュ優先）
if "cached_read_file" in instructions:
    # 検知されたルールを効率的に読み込み
    execute_load_instructions(instructions)
```

**STEP 2**: 検知結果とキャッシュ効果の表示
```
🔍 キーワード「XXX」を検知
📚 必要なルールを読み込んでいます...
💾 キャッシュから取得: git-workflow.md
📖 ファイル読み込み: versioning-rules.md
✅ 読み込み完了
📊 節約トークン: 2,400 (累計: 15,600)
💰 推定節約額: $0.047
```

### 初期読み込み
このファイル（essential-rules.md）のみを読み込む

### 詳細が必要な場合（自動判定）
以下のキーワードで自動的に詳細ルールを読み込む：

#### **バージョニング関連**
- キーワード: 「バージョン」「リリース」「MAJOR」「MINOR」「PATCH」
- 読み込み: `steering-detailed/versioning-rules.md`

#### **実装開始時（特別処理）**
- キーワード: 「TASK-XXXを実装」「実装しよう」「開発開始」
- **自動実行**: 実装に必要な全ルールを一括読み込み（キャッシュ優先）
```python
# 実装開始時の特別処理（キャッシュ対応）
from .session_cache import cached_read_file

if any(keyword in user_message.lower() for keyword in ["task-", "実装", "開発開始"]):
    implementation_rules = [
        "steering-detailed/development-workflow.md",
        "steering-detailed/git-workflow.md", 
        "steering-detailed/testing-strategy.md",
        "steering-detailed/error-handling-and-logging.md"
    ]
    for rule_path in implementation_rules:
        cached_read_file(rule_path, f"実装用ルール: {rule_path}")
```

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
🔍 キーワード「バージョン」を検知
📚 steering-detailed/versioning-rules.md を読み込んでいます...
✅ 詳細なバージョニングルールを取得しました
📊 Context使用量: 200行 → 800行 (90%削減)

🔍 キーワード「TASK-003を実装」を検知  
📚 実装に必要なルールを読み込んでいます...
✅ development-workflow.md
✅ git-workflow.md
✅ testing-strategy.md
✅ error-handling-and-logging.md
📊 Context使用量: 200行 → 3,200行 (60%削減)
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

---

## 🧠 Kiroの判断支援

### Context効率化の判断基準

| ユーザーメッセージの特徴 | 推奨Action | Context使用量 | 応答速度 |
|------------------------|-----------|--------------|----------|
| 「教えて」「何？」「どう？」 | 基本ルールのみ | 200行 | **超高速** |
| 「TASK-」「実装」「開発」 | 実装用ルール全読み込み | 3,200行 | 標準 |
| 「バージョン」「リリース」 | 該当ルール1-2ファイル | 800-1,200行 | **高速** |
| 「テスト」「Git」「エラー」 | 該当ルール1ファイル | 600-800行 | **高速** |

### 自動判定の信頼度

- **High (95%+)**: TASK-、バージョン、リリース
- **Medium (85%+)**: テスト、Git、エラー
- **Low (70%+)**: 一般的な開発用語

### Kiroの最適化戦略

1. **初期応答の高速化**: essential-rules.mdのみで即答
2. **段階的詳細化**: 必要に応じて詳細ルール追加
3. **Context節約**: 不要な情報は読み込まない
4. **品質保証**: 実装時は全ルール適用

---

**Kiro専用メモ**: このシステムにより、状況に応じた最適なContext管理が可能になります。