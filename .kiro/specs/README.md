# Spec（仕様駆動開発）- 使い方ガイド

## 概要

このディレクトリには、**仕様駆動開発（Spec-Driven Development）**で使用するSpec文書が格納されています。

Komonプロジェクトでは、アイデア → 仕様 → 実装 → テストの流れで開発を進めます。

## ディレクトリ構造

```
.kiro/specs/
├── README.md                          # このファイル
├── future-ideas.md                    # アイデア管理
├── {feature-name}/                    # 機能別Spec
│   ├── requirements.md                # 要件定義
│   ├── design.md                      # 設計書（正確性プロパティを含む）
│   └── tasks.md                       # 実装タスクリスト
└── ...
```

## 開発フロー

### 1. アイデア段階

新機能のアイデアは`future-ideas.md`に追加します。

```markdown
### [IDEA-XXX] 機能名
**ステータス**: 💡 検討中
**優先度**: High/Medium/Low

#### 概要
どんな機能か、なぜ必要か。

#### 期待効果
- 効果1
- 効果2

#### 実装の難易度
- 見積もり: 小/中/大
```

### 2. 実装決定

実装を決定したら、`.kiro/tasks/implementation-tasks.md`に`TASK-XXX`として追加します。

### 3. Spec作成

機能別のディレクトリを作成し、3つのファイルを作成します：

```bash
mkdir -p .kiro/specs/{feature-name}
```

#### 3-1. requirements.md（要件定義）

```markdown
---
title: 機能名 - 要件定義
feature: feature-name
status: draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# 機能名 - 要件定義

## 概要
機能の概要説明。

## 受入基準

### [AC-001] 基準名
**WHEN**: 条件
**THEN**: 期待される結果
```

#### 3-2. design.md（設計書）

```markdown
---
title: 機能名 - 設計書
feature: feature-name
status: draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# 機能名 - 設計書

## アーキテクチャ
システム構成の説明。

## 正確性プロパティ

### [PROP-001] プロパティ名
**検証対象**: AC-001
**プロパティ**: 不変条件の説明
```

#### 3-3. tasks.md（実装タスクリスト）

```markdown
---
title: 機能名 - 実装タスク
feature: feature-name
status: draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# 機能名 - 実装タスク

- [ ] 1. タスク1（要件: AC-001）
- [ ] 2. タスク2（要件: AC-002）
- [ ] 3. テスト追加
- [ ] 4. ドキュメント更新
```

### 4. Spec検証

Spec作成後、検証スクリプトを実行します：

```bash
python scripts/validate_specs.py
python scripts/check_spec_consistency.py
```

### 5. 実装開始

開発ブランチを作成してから実装を開始します：

```bash
git checkout -b feature/task-XXX-{feature-name}
```

### 6. 完了

実装完了後、以下を更新します：

- `tasks.md` の全タスクを `[x]` に
- `.kiro/tasks/implementation-tasks.md` のステータスを 🟢 Done に
- `docs/CHANGELOG.md` に記録
- `future-ideas.md` のステータスを「実装済み」に

## Spec品質保証

### 構造検証（validate_specs.py）

- Front Matterの必須フィールド
- 日付フォーマット
- 必須セクションの存在
- 受入基準・プロパティ・タスクの数

### 一貫性検証（check_spec_consistency.py）

- 3ファイル間のfeature名一致
- 存在しない受入基準の参照
- プロパティと受入基準の対応
- タスクと受入基準のカバレッジ

## トレーサビリティ

Komonでは、以下のトレーサビリティを維持します：

```
[IDEA-XXX] アイデア
    ↓
[TASK-XXX] 実装タスク
    ↓
[AC-XXX] 受入基準（requirements.md）
    ↓
[PROP-XXX] 正確性プロパティ（design.md）
    ↓
タスク（tasks.md）
    ↓
テストコード（tests/）
```

## 他のプロジェクトで使う場合

### ステップ1: ディレクトリ構造をコピー

```bash
mkdir -p /path/to/myproject/.kiro/specs
cp /path/to/komon/.kiro/specs/README.md /path/to/myproject/.kiro/specs/
```

### ステップ2: future-ideas.mdを作成

```bash
touch /path/to/myproject/.kiro/specs/future-ideas.md
```

### ステップ3: 検証スクリプトをコピー

```bash
cp /path/to/komon/scripts/validate_specs.py /path/to/myproject/scripts/
cp /path/to/komon/scripts/check_spec_consistency.py /path/to/myproject/scripts/
```

### ステップ4: 開発開始

アイデアを`future-ideas.md`に追加して、開発を開始します。

## まとめ

- **アイデア管理**: `future-ideas.md`
- **Spec作成**: `{feature-name}/requirements.md`, `design.md`, `tasks.md`
- **品質保証**: 検証スクリプトで自動チェック
- **トレーサビリティ**: アイデア → 要件 → 設計 → タスク → テスト

このアプローチにより、仕様と実装の乖離を防ぎ、高品質な開発が可能になります。
