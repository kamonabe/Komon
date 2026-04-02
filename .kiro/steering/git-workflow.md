---
inclusion: auto
name: git-workflow
description: ブランチ、マージ、コミット、push、git操作時のGit運用ルール
---

# Git運用ルール

## 基本原則

mainブランチを絶対に壊さない。この原則はhookによって自動的に強制される。

## ブランチ戦略

mainブランチで作業OK:
- ドキュメント整備（README, CHANGELOG等）
- アイデア・タスク管理ファイルの編集
- Spec作成（requirements.yml, design.yml, tasks.yml）
- ステアリングルールの追加・更新

開発ブランチ必須:
- コード実装（src/配下）
- テスト追加（tests/配下）
- 設定ファイル変更（settings.yml, setup.py等）
- 依存パッケージ変更（requirements.txt等）

命名規則:
```
feature/task-XXX-{feature-name}   # 新機能
bugfix/{issue-description}        # バグ修正
refactor/{module-name}            # リファクタリング
```

## 作業開始前の同期

新しいブランチを切る前に必ずorigin/mainと同期する:
```bash
git fetch origin
git switch main
git pull origin main
git switch -c feature/task-XXX-{feature-name}
```

理由: 複数マシン開発やチーム開発で、古いmainからの作業開始を防ぐ。

## マージ前の安全確認

mainに直接マージする前に仮マージで動作確認を行う:

```bash
# 方法1: --no-commit で仮マージ
git checkout main && git pull
git merge --no-commit --no-ff feature/task-XXX
# テスト実行 → 問題なければ git commit / やめるなら git merge --abort

# 方法2: テスト用ブランチ（推奨）
git checkout main && git pull
git checkout -b merge-check/feature-name
git merge feature/task-XXX
# テスト実行 → 問題なければ本番マージ → テスト用ブランチ削除
```

## push前の品質チェック

`project-config.yml` の `quality.pre_push_checks` に定義されたスクリプトが hookで自動実行される。全チェック通過後にのみpush可能。

## エラー回復

mainブランチで誤って実装してしまった場合:
```bash
git stash
git checkout -b feature/task-XXX-{feature-name}
git stash pop
```

マージエラー "Your local changes would be overwritten":
```bash
git reset --hard HEAD
git clean -fd
git merge feature/task-XXX-feature-name
```

## .gitが存在しない場合

Git未設定のプロジェクトではGit関連処理を実行しない。Git導入を推奨するが、判断は開発者に委ねる。
