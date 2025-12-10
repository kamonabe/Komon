# Komon Git運用ルール

## 基本方針

Komonプロジェクトでは、**mainブランチを絶対に壊さない**ことを最優先とします。

## Gitブランチ戦略

### mainブランチで作業してOK

以下の作業は**mainブランチで直接**行います：

- ドキュメント整備（README, CHANGELOG等）
- future-ideas.mdへのアイデア追加
- implementation-tasks.mdへのタスク追加
- Spec作成（requirements.md, design.md, tasks.md）
- ステアリングルールの追加・更新

### 開発ブランチを切る必要がある

以下の作業は**必ず開発ブランチ**を作成してから行います：

- **コード実装**（src/配下の変更）
- **テスト追加**（tests/配下の変更）
- **設定ファイル変更**（settings.yml, setup.py等）
- **依存パッケージ変更**（requirements.txt等）

### ブランチ命名規則

```
feature/task-XXX-{feature-name}     # 新機能
bugfix/{issue-description}     # バグ修正
refactor/{module-name}         # リファクタリング

例:
- feature/task-001-progressive-notification
- feature/task-003-contextual-advice
- bugfix/fix-memory-leak
- refactor/analyzer-module
```

## Git運用の安全策

### 前提条件チェック

#### .gitの存在確認

プロジェクト内に `.git` が存在しない場合：
- Git関連の処理は実行しない
- 代わりに次のような**推奨コメント**を表示・案内してよい

```
現在このプロジェクトにはGitが設定されていません。
Gitを導入するとバージョン管理や安全な開発フローが利用できるため推奨です。
```

- Git導入の判断は開発者に委ねる（強制しない）
- 希望する場合は、次のような自動化フローを提供：
  - `git init`
  - `.gitignore` 自動生成
  - GitHub/社内Gitへのリポジトリ作成
  - mainブランチの作成
  - 初期commit/pushの案内

### 作業開始前の必須手順

**新しい作業ブランチを切る前に、必ず origin/main と同期する**

これは**複数マシン開発**や**チーム開発**で、以下の事故を防ぐための保険：
- 古いmainから作業を開始してしまう
- 他の人の変更を知らずに開発してしまう
- マージ時に余計なコンフリクトが発生する

#### 手順

```bash
# 1. リモート情報を最新化
git fetch origin

# 2. mainに移動
git switch main

# 3. origin/mainを取り込む
git pull origin main

# 4. 最新のmainからfeatureブランチを作成
git switch -c feature/task-XXX-{feature-name}
```

#### なぜ必要か

一人開発では気づきにくいが、以下の状況で必須になる：
- **複数マシンで開発**：PC-Aで作業 → push → PC-Bで作業開始時にpull忘れ
- **チーム開発**：他の人がmainにマージ → 自分は古いmainから作業
- **長期間の作業**：feature作業中にmainが進んでいる

### マージ前の安全確認（マージテスト）

**mainに直接マージする前に、仮マージで動作確認を行う**

これは**mainを絶対に壊さない**ための文化。

#### 方法1: 仮マージ（--no-commit）

```bash
# mainにいることを確認
git checkout main
git pull

# 仮マージ（コミットはしない）
git merge --no-commit --no-ff feature/task-beta

# この状態で確認
git status
git diff

# テスト実行
python -m pytest tests/ -v

# 問題なければコミット
git commit

# やめたい場合は
git merge --abort
```

#### 方法2: マージテスト用ブランチ（推奨）

```bash
# mainを最新化
git checkout main
git pull

# テスト用ブランチを作成
git checkout -b merge-check/beta

# ここでfeature/betaをマージ
git merge feature/task-beta

# テスト実行・動作確認
bash run_coverage.sh

# 問題なければ正式にマージ
git checkout main
git merge feature/task-beta

# テスト用ブランチを削除
git branch -D merge-check/beta
```

#### なぜ必要か

Gitは**テキスト差分**しか見ないため：
- 構文的にはマージ成功でも、**意味的に壊れる**ことがある
- 同じ処理が重複する（for文が2つ並ぶ等）
- 既存機能との相性問題

これらは**人間が見て・テストして**初めて気づける。

マージテストは：
- **冗長ではなく安全策**
- **mainを守るための投資**
- **事故を未然に防ぐ文化**

### Kiroの役割（AI IDEによる自動化）

Kiroは以下を自動で実行・チェックできる：

#### 1. 作業前の同期チェック
- feature作成前に `git fetch origin` を自動実行
- origin/mainとの差分を警告
- 古いmainからの作業開始を防ぐ

#### 2. マージ前の仮マージ自動実行
- merge-checkブランチを裏で作成
- mainとfeatureを自動統合
- テスト実行
- コンフリクト・意味的衝突を検知
- 結果をユーザーに提示

#### 3. ヒューマンエラーのゼロ化
人間のルールでは「うっかり」が必ず出るが、AI IDEが強制すれば：
- pull忘れ
- 古いmainでの開発
- コンフリクト放置
- 動作確認不足
- main破壊事故

これらを**構造的に防げる**。

少しの時間とクレジットで「不安ゼロ・事故ゼロ・正史保護」が手に入るなら、それは**開発品質への投資**。

## 🚨 実装開始前の必須手順（Kiroへの厳格な指示）

**⚠️ 重要**: この手順をスキップするとmainブランチ破壊の危険性があります。

**TASK-XXXの実装を開始する際、Kiroは以下を厳格に実行：**

### フェーズ1: 宣言と環境確認
1. **「Specモードで進めます」と宣言**
2. **安全性チェックの実行を宣言**：
   ```
   実装開始前に安全性チェックを実行します。
   ```

### フェーズ2: 必須安全性チェック
3. **現在のブランチを確認**（必須）
   ```bash
   git branch
   ```
4. **作業ディレクトリの状態確認**
   ```bash
   git status
   ```
5. **システム時刻の確認**
   ```bash
   date
   ```

### フェーズ3: ブランチ安全性の判定
6. **mainブランチにいる場合**:
   - ❌ **絶対にコード実装を開始しない**
   - ❌ **ファイル変更を一切行わない**
   - 🚨 **即座に危険警告を表示**:
     ```
     🚨 危険: mainブランチで実装しようとしています
     
     【リスク】
     - mainブランチの破壊
     - 他の開発者への影響  
     - リリース品質の低下
     
     【必要な作業】
     開発ブランチを作成してください：
     
     git checkout -b feature/task-XXX-{feature-name}
     
     ブランチ作成後、「ブランチ作成完了」とお知らせください。
     実装はそれまで開始しません。
     ```
   - ⏸️ **ユーザーの返答を待機**（実装は開始しない）

### フェーズ4: ブランチ作成完了の再確認
7. **ユーザーから「ブランチ作成完了」の返答後**:
   ```bash
   # 再度ブランチ確認
   git branch
   ```
8. **開発ブランチ確認**:
   - ✅ **開発ブランチにいる場合**: 実装開始
   - ❌ **まだmainブランチの場合**: 再度警告・待機

### フェーズ5: 実装開始の最終確認
9. **実装開始直前の宣言**:
   ```
   ✅ 安全性チェック完了
   - 開発ブランチ: 確認済み
   - 作業ディレクトリ: クリーン
   - システム時刻: 正常
   
   実装を開始します。
   ```

### チェックリスト（実装開始前）

**🚨 必須チェック項目（全て完了してから実装開始）**:

**環境安全性チェック**:
- [ ] `git branch` でブランチを確認した
- [ ] `git status` で作業ディレクトリの状態を確認した  
- [ ] `date` でシステム時刻を確認した

**ブランチ安全性チェック**:
- [ ] mainブランチの場合、実装を開始しなかった
- [ ] mainブランチの場合、危険警告を表示した
- [ ] mainブランチの場合、ユーザーにブランチ作成を依頼した
- [ ] ユーザーの「ブランチ作成完了」返答を待機した

**最終確認**:
- [ ] 開発ブランチにいることを再確認した
- [ ] 安全性チェック完了を宣言した
- [ ] 上記が全て完了してから実装を開始した

**❌ 禁止事項**:
- [ ] mainブランチでの実装開始
- [ ] ブランチ確認のスキップ
- [ ] 安全性チェックの省略

## 安全性向上のための追加対策

### 1. 多重安全確認システム

**実装開始前の3段階チェック**:
1. **環境チェック**: ブランチ・作業ディレクトリ・時刻
2. **安全性判定**: mainブランチでの実装阻止
3. **最終確認**: 開発ブランチ確認後の実装開始

### 2. エラー回復手順

**mainブランチで実装してしまった場合**:
```bash
# 1. 即座に作業を停止
git status

# 2. 変更をスタッシュ
git stash

# 3. 開発ブランチを作成
git checkout -b feature/task-XXX-{feature-name}

# 4. 変更を復元
git stash pop

# 5. 実装を継続
```

### 3. システム環境の事前確認

**時刻同期の確認**:
```bash
# NTP同期状態の確認
timedatectl status

# 必要に応じて強制同期
sudo chronyc makestep
```

**Git設定の確認**:
```bash
# ユーザー設定確認
git config --global user.name
git config --global user.email

# リモート設定確認
git remote -v
```

### 4. 予防的措置

**開発開始時の習慣**:
- 毎回必ずブランチ確認
- 実装前の環境チェック
- 定期的な時刻同期確認

**緊急時の対応**:
- 問題発生時は即座に作業停止
- 状況を正確に把握してから対処
- 不明な場合はユーザーに確認

### 5. 品質保証の強化

**実装品質の維持**:
- テストカバレッジの確認
- 後方互換性の検証
- ドキュメント更新の確認

**リリース前の最終チェック**:
- 全テストの実行
- 手動動作確認
- Git履歴の整合性確認

## マージ時のトラブルシューティング

mainブランチへのマージでエラーが発生した場合の対処法：

### エラー: "Your local changes would be overwritten by merge"

**原因**: mainブランチに未コミットの変更が残っている

**対処法**:
```bash
# 1. 現在の状態を確認
git status

# 2. 変更を破棄してクリーンな状態に
git reset --hard HEAD
git clean -fd

# 3. 状態確認
git status

# 4. 再度マージ
git merge feature/task-XXX-feature-name
```

### エラー: "unable to create file ... No such file or directory"

**原因**: ディレクトリが存在しない

**対処法**:
```bash
# 必要なディレクトリを作成
mkdir -p .kiro/steering
mkdir -p .kiro/tasks
mkdir -p .kiro/specs/

# 再度マージ
git merge feature/task-XXX-feature-name
```

### マージ後の確認

```bash
# マージ結果を確認
git status

# ログ確認
git log --oneline -5

# リモートにプッシュ
git push origin main
```

## まとめ

- **mainブランチ**: ドキュメント・Spec作成のみ
- **開発ブランチ**: コード実装・テスト追加
- **ブランチ命名**: `feature/task-XXX-{feature-name}`
- **実装開始前**: 必ずブランチ確認（3段階チェック）
- **マージ前**: 仮マージでテスト実行
- **事故防止**: Kiroが自動チェック