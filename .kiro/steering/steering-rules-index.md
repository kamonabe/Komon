---
rule-id: steering-rules-index
priority: critical
applies-to: [all]
triggers: [always]
description: 全ステアリングルールの索引と概要（自動生成）
auto-generated: true
generator: scripts/generate_steering_index.py
---

# ステアリングルール索引

このファイルは全てのステアリングルールの概要を提供します。
詳細が必要な場合は、各ルールファイルを参照してください。

**⚠️ 注意**: このファイルは自動生成されます。直接編集しないでください。

---

## 📚 アクティブなルール一覧

### Level 1: 常に読み込むルール（初期読み込み）

これらのルールは常に読み込まれます（約1,000行）。


### 1. environment-and-communication

**概要**: 開発環境とコミュニケーション言語のルール

**優先度**: high

**基本方針**:


**詳細**: `environment-and-communication.md`

---

### 2. ai-security-guardrails

**概要**: AI自身が機密情報を検知して警告するガードレール

**優先度**: critical

**基本方針**:
**Kiroは機密情報を検知したら、処理を中断してユーザーに警告する**

「過剰防衛くらいがちょうどいい」という原則に基づき、疑わしい情報は全て警告する。

**詳細**: `ai-security-guardrails.md`

---

### Level 2: オンデマンド読み込みルール（必要に応じて）

これらのルールは必要に応じて読み込まれます（約4,000行）。


### 1. versioning-rules

**概要**: Semantic Versioningに基づくバージョン番号の決定ルール

**優先度**: high

**適用場面**: release, versioning, changelog

**トリガー**: implementation-complete, changelog-update

**基本方針**:
Komonプロジェクトは**Semantic Versioning 2.0.0**に従います。

バージョン番号は`MAJOR.MINOR.PATCH`の形式で表現されます。

参考: https://semver.org/

**詳細**: `versioning-rules.md`

---

### 2. development-workflow

**概要**: 仕様駆動開発のワークフロー

**優先度**: high

**適用場面**: implementation, spec-creation, task-management

**トリガー**: task-start, spec-creation, implementation-start

**基本方針**:


**詳細**: `development-workflow.md`

---

### 3. task-management

**概要**: タスク管理の2階層構造ルール

**優先度**: medium

**適用場面**: task-management

**トリガー**: task-complete, task-update

**基本方針**:


**詳細**: `task-management.md`

---

### 4. spec-quality-assurance

**概要**: Spec品質保証と検証スクリプト実行ルール

**優先度**: high

**適用場面**: spec-creation, implementation-start

**トリガー**: spec-complete, implementation-start

**基本方針**:
Komonプロジェクトでは、**ローカルで確実に品質を作り込み、CI/CDで公開品質を証明する**方針を採用しています。

Komonはシンプル軽量なツールであり、検証スクリプトも軽量なため、冗長性を気にせずローカルとCI/CDの両方でしっかり検証を行います。

**詳細**: `spec-quality-assurance.md`

---

### 5. error-handling-and-logging

**概要**: エラーハンドリングとログ出力の標準

**優先度**: medium

**適用場面**: implementation, error-handling

**トリガー**: code-implementation

**基本方針**:
Komonは**軽量アドバイザー型ツール**であり、エラーが発生しても可能な限り処理を継続します。

ユーザー向けには分かりやすい日本語メッセージを表示し、開発者向けには詳細なログを記録します。

**詳細**: `error-handling-and-logging.md`

---

### 6. commit-message-rules

**概要**: Conventional Commits形式のコミットメッセージルール

**優先度**: low

**適用場面**: commit

**トリガー**: commit-creation

**基本方針**:


**詳細**: `commit-message-rules.md`

---

## 🔍 使い方

### 簡単な質問の場合

この索引から回答できます。詳細が必要な場合は、該当するルールファイルを自動的に読み込みます。

### 実装開始の場合

必要な全てのルールを自動的に読み込みます：
- development-workflow.md
- git-workflow.md
- error-handling-and-logging.md
- testing-strategy.md

### 詳細が必要な場合

「詳しく教えて」と言っていただければ、該当するルールファイルを読み込んで詳細を説明します。

---

## 🔄 更新履歴

このファイルは `scripts/generate_steering_index.py` により自動生成されます。

更新方法:
```bash
python scripts/generate_steering_index.py
```

---

## 📊 統計

- **Level 1ルール**: {len(level_1_rules)}ファイル（常に読み込む）
- **Level 2ルール**: {len(level_2_rules)}ファイル（オンデマンド）
- **合計**: {len(level_1_rules) + len(level_2_rules)}ファイル

---

**自動生成日時**: {import datetime; datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
