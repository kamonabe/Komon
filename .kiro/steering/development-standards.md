---
inclusion: manual
---

# 開発標準ガイド（オンボーディング用）

> このファイルは新メンバーのオンボーディングや、プロジェクト全体の方針確認時に参照する。
> 日常の開発では auto/fileMatch のルールが自動的に適用されるため、このファイルを毎回読む必要はない。

## 基本原則

```
人間の理解速度 > AI の生成速度
```

Kiroが高速にコードを生成できても、人間が理解・レビューできる範囲で進める。

## プロジェクト構造

```
PROJECT_NAME/
├── src/PROJECT_NAME/       # コアモジュール
├── tests/                  # テストコード
├── docs/                   # ドキュメント
├── config/                 # 設定サンプル
├── scripts/                # 実行スクリプト
├── .kiro/                  # Kiro設定
│   ├── specs/              # 仕様書（YAML形式）
│   ├── steering/           # ステアリングルール
│   ├── hooks/              # 自動化hook
│   └── tasks/              # タスク管理
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── setup.py
└── pytest.ini
```

## 品質基準の参照先

全ての数値目標（カバレッジ、閾値等）は `project-config.yml` で一元管理。
各ルールファイルはその値を参照する。これにより、プロジェクトごとに異なる基準を設定しても、ルール体系は同じものを使える。

## コード品質ツール（将来用）

```bash
black src/ tests/       # フォーマット
flake8 src/ tests/      # リント
mypy src/               # 型チェック
```

## ドキュメント標準

必須ドキュメント:
- `README.md`: プロジェクト概要
- `CHANGELOG.md`: 変更履歴（keep-a-changelog形式）
- `.kiro/specs/`: 仕様書（YAML形式）

## ルール体系の全体像

```
essential-rules.md (always)     ← 判断基準のみ、50行
project-config.yml (always)     ← 数値・設定の一元管理
    ↓ 状況に応じて自動読み込み
development-workflow.md (auto)  ← 開発フロー
git-workflow.md (auto)          ← Git運用
testing-strategy.md (auto)      ← テスト戦略
komon-customizations.md (auto)  ← プロジェクト固有
    ↓ ファイル編集時に自動読み込み
error-handling-and-logging.md (fileMatch: src/**/*.py)
task-management.md (fileMatch: .kiro/tasks/**)
spec-quality-assurance.md (fileMatch: .kiro/specs/**)
    ↓ 必要時に手動参照
versioning-rules.md (manual)
release-process.md (manual)
commit-message-rules.md (manual)
git-ssh-setup.md (manual)
development-standards.md (manual) ← このファイル
```

## 企業利用時のカスタマイズポイント

1. `project-config.yml` をプロジェクトに合わせて編集
2. `komon-customizations.md` を自社プロジェクト固有の内容に差し替え
3. hookを自社のCI/CDパイプラインに合わせて調整
4. ワークスペースルートの `.kiro/docs/extended-rules/` から必要なルールを有効化
