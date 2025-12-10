---
rule-id: development-workflow
priority: high
applies-to:
- implementation
- spec-creation
- task-management
triggers:
- task-start
- spec-creation
- implementation-start
description: 仕様駆動開発のワークフロー
---

# Komon仕様駆動開発ワークフロー

## 開発の基本方針

Komonプロジェクトは**仕様駆動開発（Spec-Driven Development）**を採用しています。

## アイデアから実装までの流れ

### 1. アイデア段階
**ファイル**: `.kiro/specs/future-ideas.md`

- 新機能のアイデアはまず`future-ideas.md`に追加
- アイデアの検討・熟成期間を設ける
- 実装に値するかどうかを判断

### 2. 実装決定
**ファイル**: `.kiro/tasks/implementation-tasks.md`

- 実装を決定したアイデアを`TASK-XXX`として追加
- 優先度、見積もり、背景を記載
- タスク分解を行う

### 3. Spec作成（mainブランチ）

**🚨 必須手順: Spec作成前の確認**

Kiroは新しいSpecを作成する前に、**必ず以下を実行**してください：

#### **ステップ1: 既存のSpecファイルの構造を確認**

```bash
# 既存のSpecディレクトリを確認
ls .kiro/specs/contextual-advice/

# requirements.ymlの形式を確認（先頭50行）
head -50 .kiro/specs/contextual-advice/requirements.yml

# テンプレートを確認
ls .kiro/specs/_templates/
```

#### **ステップ2: ファイル形式の確認**

確認ポイント：
- [ ] ファイル拡張子は`.yml`である（`.md`ではない）
- [ ] 内容はYAML構造化形式である（Markdownではない）
- [ ] `metadata`, `overview`, `acceptance-criteria`などのセクションがある
- [ ] 上記を確認してから作成を開始する

#### **ステップ3: Specファイルの作成**

**フォルダ**: `.kiro/specs/{feature-name}/`

以下の3ファイルを**YAML構造化形式**で作成：
- `requirements.yml`: 要件定義
- `design.yml`: 設計書（正確性プロパティを含む）
- `tasks.yml`: 実装タスクリスト

**ファイル形式（厳守）**:
- ✅ **拡張子**: `.yml`（`.md`ではない）
- ✅ **内容**: YAML構造化形式（Markdownではない）
- ✅ **パース**: `yaml.safe_load()`で読み込み可能
- ✅ **検証**: `scripts/validate_specs.py`で構造を検証
- ❌ **禁止**: Markdown形式（`.md`）での作成

**YAML構造の例**:
```yaml
# requirements.yml
metadata:
  title: "機能名"
  feature: "feature-name"
  status: "draft"
  created: "YYYY-MM-DD"
  ...

overview:
  description: |
    説明文
  background: |
    背景
  ...

acceptance-criteria:
  - id: "AC-001"
    title: "タイトル"
    priority: "high"
    type: "functional"
    description: |
      説明
    when: "条件"
    then: "結果"
    examples:
      - input: "入力"
        output: "出力"
```

**テンプレート**: `.kiro/specs/_templates/` を参照

**この時点ではまだmainブランチでOK**

### 4. 🚨 実装開始前の必須チェック 🚨

**⚠️ 重要**: このチェックをスキップするとmainブランチが破壊される危険性があります。

**Kiroは実装を開始する前に、必ず以下を厳格に実行します：**

#### **ステップ1: 環境の安全性確認**
```bash
# 1. 現在のブランチを確認（必須）
git branch

# 2. 作業ディレクトリの状態確認
git status

# 3. システム時刻の確認（コミット時刻の正確性のため）
date
```

#### **ステップ2: ブランチ安全性の判定**
- ✅ **開発ブランチにいる場合**: 実装を開始
- ❌ **mainブランチにいる場合**: **即座に停止**

#### **ステップ3: mainブランチの場合の対応**
**Kiroは以下を必ず実行**：

1. **実装を開始しない**（コード変更を一切行わない）
2. **明確な警告を表示**：
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
   ```
3. **ユーザーの返答を待機**（実装は開始しない）

#### **ステップ4: ブランチ作成完了の確認**
ユーザーから「ブランチ作成完了」の返答があった後：

```bash
# ブランチ確認（再実行）
git branch

# 開発ブランチにいることを確認
# ✅ 開発ブランチ → 実装開始
# ❌ まだmainブランチ → 再度警告
```

#### **ステップ5: 最終安全確認**
実装開始直前に以下を確認：
- [ ] 開発ブランチにいることを確認済み
- [ ] 作業ディレクトリがクリーンであることを確認済み
- [ ] システム時刻が正常であることを確認済み
- [ ] 上記が全て完了してから実装開始

**ブランチ作成コマンド（ユーザーが実行）**:
```bash
git checkout main
git checkout -b feature/task-XXX-{feature-name}
```

**ブランチ命名規則**:
- `feature/task-001-progressive-notification`
- `feature/task-003-contextual-advice`
- `bugfix/fix-memory-leak` (バグ修正の場合)

### 5. 実装フェーズ（Kiroが自律的に進める）

Kiroは以下を**サブタスクごとに**実行します：

#### サブタスク1: コード実装
1. モジュールを実装
2. **即座にタスクファイルを更新**
   - Spec別タスクリスト: `[x]` を付ける
   - 実装タスクリスト: `[x]` を付ける + 進捗率を更新
3. ユーザーに報告: 「✅ サブタスク1完了、進捗: 1/3」

#### サブタスク2: テスト作成
1. テストを作成（プロパティテスト + 統合テスト + ユニットテスト）2. **即座にタスクファイルを更新**
   - Spec別タスクリスト: `[x]` を付ける
   - 実装タスクリスト: `[x]` を付ける + 進捗率を更新
3. ユーザーに報告: 「✅ サブタスク2完了、進捗: 2/3」

#### サブタスク3: ドキュメント更新
1. ドキュメントを更新（README.md, CHANGELOG.md）
2. **即座にタスクファイルを更新**
   - Spec別タスクリスト: `[x]` を付ける
   - 実装タスクリスト: `[x]` を付ける + 進捗率を更新
3. ステータスを 🟢 Done に変更
4. ユーザーに完了報告: 「✅ 全タスク完了、進捗: 3/3」

**各サブタスク完了時に即座に更新**することで、中断・再開が容易になります。

### 6. 完了報告とバージョン決定

Kiroが以下を報告：
- 実装内容のサマリー
- テスト結果（全テストパス確認）
- 提案するバージョン番号（例: v1.12.0）

**ユーザーが最終確認**して：
1. バージョン番号を決定（例: v1.12.0）

### 7. 🚨 バージョン情報の更新（重要！）

**Kiroへの指示**: ユーザーがバージョン番号を決定したら、**必ず以下の順序でリマインド**してください：

```
📋 リリース前の必須作業（4つのファイルを順番に更新）:

**重要**: 抜け漏れ防止のため、必ずこの順序で更新してください。

1. version.txtを更新してください：
   version.txt を新しいバージョン番号に変更
   
   変更例：
   1.18.1
   ↓
   1.19.0

2. src/komon/__init__.pyを更新してください：
   __version__ を新しいバージョン番号に変更
   
   変更例：
   __version__ = "1.18.1"
   ↓
   __version__ = "1.19.0"

3. CHANGELOGを更新してください：
   docs/CHANGELOG.md の [Unreleased] を [1.X.X] - YYYY-MM-DD に変更

   変更例：
   ## [Unreleased]
   ↓
   ## [Unreleased]
   
   ## [1.X.X] - 2025-11-27

4. project-config.ymlのバージョンを更新してください：
   .kiro/steering/project-config.yml の current_version を更新

   変更例：
   versioning:
     current_version: "1.X.X"

5. 4つのファイル全てを更新したことを確認してください
   - [ ] version.txt
   - [ ] src/komon/__init__.py
   - [ ] docs/CHANGELOG.md
   - [ ] .kiro/steering/project-config.yml

6. この作業が完了したら、次のステップに進みます
```

**なぜ重要か**：
- ❌ version.txtを忘れると`pip install -e .`で古いバージョンが表示される
- ❌ __init__.pyを忘れるとパッケージのバージョンが古いまま
- ❌ CHANGELOGを忘れると`generate_release_notes.py`が動かない
- ❌ project-config.ymlを忘れるとステアリングルールが古いバージョンを参照する
- ❌ 4つのファイルのバージョンが不一致になる
- ❌ 次のリリース時に混乱する

**Kiroのチェックポイント**：
- [ ] ユーザーがバージョン番号を決定した
- [ ] 4つのファイルの更新を**順番に**リマインドした
  - [ ] 1. version.txt
  - [ ] 2. src/komon/__init__.py
  - [ ] 3. docs/CHANGELOG.md
  - [ ] 4. .kiro/steering/project-config.yml
- [ ] ユーザーが「更新完了」と返答した
- [ ] 上記が全て完了してから次のステップに進む

### 8. 🚨 GitHub push前の必須チェック（ステータス整合性確認）

**⚠️ 重要**: このチェックをスキップするとGitHub Actionsでエラーになります。

**Kiroは必ず以下を実行**：

```bash
# ステータス整合性チェック
python scripts/check_status_consistency.py
```

**チェック内容**:
- future-ideas.mdとimplementation-tasks.mdのステータス一致
- tasks.ymlにtask-idまたはfeature-nameが記載されているか
- 完了タスクのアーカイブ状況

**エラーが出た場合**:
1. **即座に修正**（push前に必ず解決）
2. エラーメッセージに従って修正
3. 再度チェックを実行
4. 全てパスしてからpush

**Kiroのチェックポイント**:
- [ ] `python scripts/check_status_consistency.py` を実行した
- [ ] エラー0件、警告0件を確認した
- [ ] 上記が完了してからpushに進む

### 9. mainブランチへのマージとタグ作成

**ユーザーが実行**：

```bash
git checkout main
git merge feature/task-XXX-{feature-name}
git tag v1.X.X
git push origin main --tags
```

### 10. 🚨 完了タスクのアーカイブ（必須作業）

**タイミング**: タグ作成直後

**Kiroの必須作業**:

```markdown
📋 タスクアーカイブ作業（必須）

新バージョン v1.X.X をリリースしました。
前バージョンの完了タスクをアーカイブします。

1. 前バージョンの完了タスクを特定
   - implementation-tasks.mdで前バージョンを検索
   - 例: 「完了日: YYYY-MM-DD (v1.Y.Z)」

2. completed-tasks.mdに移動
   - v1.Y.Zセクションを作成（バージョン降順で配置）
   - タスク全体をコピー＆ペースト
   - implementation-tasks.mdから削除

3. 更新履歴を記録
   - 両ファイルの「更新履歴」セクションに記録
   - 日付とタスク番号を明記

この作業を完了してから、次のステップに進みます。
```

**具体例**:
```
v1.19.0をリリース（タグ作成）
  ↓
v1.18.0の完了タスク（TASK-003）をcompleted-tasks.mdに移動
  ↓
implementation-tasks.mdには直近バージョン（v1.19.0）のみ残る
```

**Kiroのチェックポイント**:
- [ ] 前バージョンの完了タスクを特定した
- [ ] completed-tasks.mdに移動した
- [ ] implementation-tasks.mdから削除した
- [ ] 両ファイルの更新履歴を記録した
- [ ] 上記が全て完了してから次のステップに進んだ

### 11. GitHub Releases用の情報を準備

**Kiroが自動実行**：

```bash
# リリースノートを自動生成
python scripts/generate_release_notes.py v1.X.X
```

スクリプトが以下を自動的に実行：
- **docs/CHANGELOG.mdから該当バージョンを抽出**
- **GitHub Releases用にフォーマット**
- **RELEASE_NOTES.mdの「登録待ちリリース」セクションに追記**

```markdown
### v1.X.X - 機能名
**作成日**: YYYY-MM-DD

**Title**:
v1.X.X - 機能名

**Notes**:
（CHANGELOG.mdから抽出した内容）

---
```

ユーザーはこの情報をコピーしてGitHub Releasesに登録します。
登録完了後は「登録済みリリース（アーカイブ）」セクションに移動してください。

### 12. PyPI公開（手動作業）

**タイミング**: GitHub Releasesに登録後、**CIチェックがクリアしたことを目視確認してから**

**手順**:

1. **GitHub ActionsのCIチェックを確認**
   - GitHub Releasesページでワークフローの実行状況を確認
   - 全てのチェックが✅になっていることを確認
   - テスト、カバレッジ、Spec検証が全てパス

2. **ビルド**
   ```bash
   python -m build
   ```

3. **PyPI公開**
   ```bash
   python -m twine upload dist/*
   ```

4. **公開確認**
   ```bash
   pip install komon==
   komon --version
   ```

**公開失敗時の対応**:
- エラーメッセージを確認
- 問題を修正（通常はビルド設定やパッケージメタデータ）
- 再度ビルド＆公開
- タグやGitHub Releasesは変更不要（PyPIのみ再公開）

**注意**:
- PyPI公開日は現在追跡していません
- 将来、自動化した際に記録方法を再検討します
- 詳細な手順は `.kiro/PYPI_RELEASE_GUIDE.md` を参照

## 重要なルール

### ✅ Kiroが自律的に進めて良いこと

- requirements.yml, design.yml, tasks.yml の作成（構造化YAML形式で）
- コード実装
- テスト作成（しっかりした品質を維持）
- ドキュメント更新（README, CHANGELOG）
- タスクファイルの更新
- GitHub Releases用の情報を`.kiro/RELEASE_NOTES.md`に追記

### ⚠️ ユーザー確認が必要なこと

- **大きな既存コードの変更**
  - 既存機能に影響がある場合
  - 主要モジュールの大幅変更
  - → **Specモードを停止**し、**Vibeモード**で仕様を詰め直す
  
- **バージョン番号の決定**
  - Kiroが提案 → ユーザーが決定

- **アイデアの実装判断**
  - future-ideas.md → implementation-tasks.md への移行
  
- **実装完了後のアイデア管理**
  - 実装済みアイデアは future-ideas.md に ✅ 実装済み マークを付ける
  - 次のバージョンリリース時に implemented-ideas.md に移動
  - 見送りアイデアは rejected-ideas.md に移動
  - 研究プロジェクトは research-projects.md で管理

## テスト品質の基準

詳細は `testing-strategy.md` を参照してください。

### 必須テスト
- プロパティベーステスト（hypothesis使用）
- 統合テスト
- ユニットテスト

### テストカバレッジ
- 目標: 95%以上（90%以上なら許容）

## テスト戦略の詳細

テスト戦略の詳細については、`testing-strategy.md`を参照してください。

### テストの概要

Komonでは、**3層テスト構造**を採用しています：
1. **プロパティベーステスト**: 仕様の正確性を数学的に検証
2. **統合テスト**: 複数モジュールの連携を検証
3. **ユニットテスト**: 個別関数のロジックを検証

詳細な実装方法、テストデータの管理、トラブルシューティングについては、`testing-strategy.md`を参照してください。

## 開発モードの使い分け

### Specモード（仕様駆動開発）
**使用場面**:
- 新機能の追加
- 既存機能への小規模な変更
- テストの追加

**特徴**:
- Kiroが自律的に進める
- 仕様 → 実装 → テストの流れ

### Vibeモード（対話的開発）
**使用場面**:
- 既存コードの大幅な変更
- 設計の見直しが必要な場合
- アーキテクチャの変更

**特徴**:
- ユーザーとKiroが対話しながら進める
- 仕様を詰め直してからSpecモードに戻る

## ファイル構成

```
.kiro/
├── specs/
│   ├── future-ideas.md              # アイデア管理（未実装）
│   ├── implemented-ideas.md         # 実装済みアイデアのアーカイブ
│   ├── research-projects.md         # 研究プロジェクト
│   ├── rejected-ideas.md            # 見送りアイデア
│   ├── {feature-name}/              # 機能別Spec
│   │   ├── requirements.md
│   │   ├── design.md
│   │   └── tasks.md
│   └── ...
├── tasks/
│   ├── implementation-tasks.md      # 実装タスク管理（進行中・未着手）
│   └── completed-tasks.md           # 完了タスクアーカイブ
└── steering/
    ├── task-management.md           # タスク管理ルール
    └── development-workflow.md      # このファイル
```

## ワークフロー例

### 例1: 新機能「段階的通知メッセージ」

```
1. future-ideas.md に [IDEA-001] として記載（mainブランチ）
   ↓
2. 実装を決定 → implementation-tasks.md に [TASK-001] 追加（mainブランチ）
   ↓
3. .kiro/specs/progressive-notification/ を作成（mainブランチ）
   - requirements.md: 要件定義
   - design.md: 設計書
   - tasks.md: タスクリスト
   ↓
4. ユーザー「TASK-001の実装を開始しよう」
   ↓
5. Kiro「Specモードで進めます。まず現在のブランチを確認します」
   git branch  # → mainブランチにいることを確認
   ↓
6. Kiro「開発ブランチを作成してください：
         git checkout -b feature/task-001-progressive-notification」
   ↓
7. ユーザーがブランチを作成
   git checkout -b feature/task-001-progressive-notification
   ↓
8. ユーザー「ブランチ作成したよ」
   ↓
9. Kiroが実装開始（Specモード）
   - コード実装
   - テスト追加
   - ドキュメント更新
   ↓
10. Kiroが完了報告「v1.12.0を提案します」
    ↓
11. ユーザーが確認「OK、v1.12.0でリリース」
    ↓
12. mainにマージしてタグ作成
    git checkout main
    git merge feature/task-001-progressive-notification
    git tag v1.12.0
```

### 例2: 既存機能の大幅変更

```
1. ユーザー「主要モジュールを大きく変更したい」
   ↓
2. Kiro「既存機能への影響が大きいので、Vibeモードで進めましょう」
   ↓
3. Vibeモードで対話
   - 現状の問題点を整理
   - 新しい設計を議論
   - 影響範囲を確認
   ↓
4. 仕様が固まったらSpecモードに移行
   - requirements.md, design.md を作成
   - 実装開始
   ↓
5. 完了報告 → リリース
```

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

## Git運用の詳細

Git運用の安全策、ブランチ戦略、マージテストの詳細については、`git-workflow.md`を参照してください。

### 基本的なGit運用

- **mainブランチ**: ドキュメント・Spec作成のみ
- **開発ブランチ**: コード実装・テスト追加（必須）
- **実装開始前**: 必ずブランチ確認（`git branch`）
- **マージ前**: テスト実行とマージテスト推奨

詳細な手順、安全策、トラブルシューティングは`git-workflow.md`を参照してください。

## まとめ

- **小さな追加機能**: Specモードで自律的に進める
- **大きな変更**: Vibeモードで仕様を詰めてからSpecモードへ
- **テスト品質**: しっかり維持（95%カバレッジ目標）
- **ドキュメント**: Kiroが自動更新
- **バージョン**: Kiroが提案、ユーザーが決定
- **ブランチ**: Spec作成はmain、コード実装は開発ブランチ

このワークフローにより、効率的かつ品質の高い開発が可能になります。