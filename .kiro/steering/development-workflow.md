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
**フォルダ**: `.kiro/specs/{feature-name}/`

以下の3ファイルを**日本語で**作成：
- `requirements.md`: 要件定義- `design.md`: 設計書（正確性プロパティを含む）- `tasks.md`: 実装タスクリスト
**この時点ではまだmainブランチでOK**

### 4. 🚨 実装開始前の必須チェック 🚨

**Kiroは実装を開始する前に、必ず以下を実行します：**

1. **現在のブランチを確認**
   ```bash
   git branch
   ```

2. **mainブランチにいる場合は停止**
   - ユーザーに「開発ブランチを作成してください」と依頼
   - ブランチ名を提案: `feature/task-XXX-{feature-name}`
   - ユーザーがブランチを作成するまで**実装を開始しない**

3. **開発ブランチにいることを確認してから実装開始**

**ブランチ作成コマンド（ユーザーが実行）**:
```bash
git checkout main
git checkout -b feature/task-XXX-{feature-name}
```

**ブランチ命名規則**:
- `feature/task-001-progressive-notification`
- `feature/task-003-contextual-advice`
- `bugfix/fix-memory-leak` (バグ修正の場合)

### 5. 実装フェーズ（Kiroが連続で進める）

Kiroは以下を**連続して自律的に**実行します：

1. コード実装
2. テスト作成（プロパティテスト + 統合テスト + ユニットテスト）3. ドキュメント更新（README.md, CHANGELOG.md）
4. タスクファイルの更新

**ユーザーの介入は不要**です。実装完了後に報告します。

### 6. 完了報告とマージ

Kiroが以下を報告：
- 実装内容のサマリー
- テスト結果（全テストパス確認）
- 提案するバージョン番号（例: v1.12.0）

**ユーザーが最終確認**して：
1. バージョン番号を決定
2. mainブランチにマージ
3. バージョンタグを作成

```bash
git checkout main
git merge feature/task-XXX-{feature-name}
git tag v1.X.X
git push origin main --tags
```

### 7. GitHub Releases用の情報を準備

**重要**: バージョンタグを作成した後、GitHub Releases登録用の情報を`.kiro/RELEASE_NOTES.md`に追記します。

Kiroが以下を自動的に追記：
- **Release Title**: `v1.X.X - 機能名`
- **Release Notes**: CHANGELOG.mdから該当バージョンの内容を抽出

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

## 重要なルール

### ✅ Kiroが自律的に進めて良いこと

- requirements.md, design.md, tasks.md の作成（日本語で）
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

## テスト品質の基準

Komonでは**しっかりしたテスト**を維持します：

### 必須テスト
1. **プロパティベーステスト**（hypothesis使用）
   - 正確性プロパティを検証
   - 不変条件のテスト
   
2. **統合テスト**
   - 既存機能との統合確認
   - エンドツーエンドの動作確認
   
3. **ユニットテスト**
   - 個別関数の動作確認
   - エッジケースのテスト

### テストカバレッジ
- 目標: 95%以上を維持
- 全テストがパスすることを確認

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
│   ├── future-ideas.md              # アイデア管理
│   ├── {feature-name}/              # 機能別Spec
│   │   ├── requirements.md
│   │   ├── design.md
│   │   └── tasks.md
│   └── ...
├── tasks/
│   └── implementation-tasks.md      # 実装タスク管理（マスター）
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

### 🚨 Kiroへの厳格な指示 🚨

#### 実装開始前の必須手順（絶対に守る）

**TASK-XXXの実装を開始する際、Kiroは以下を必ず実行：**

1. **「Specモードで進めます」と宣言**
2. **現在のブランチを確認**
   ```bash
   git branch
   ```
3. **mainブランチにいる場合**:
   - ❌ **絶対にコード実装を開始しない**
   - ✅ ユーザーに以下を依頼:
     ```
     実装を開始する前に、開発ブランチを作成してください：
     
     git checkout -b feature/task-XXX-{feature-name}
     
     ブランチ作成後、実装を開始します。
     ```
   - ⏸️ ユーザーの返答を待つ

4. **開発ブランチにいることを確認してから実装開始**

#### 実装完了後の手順

1. テスト全パス確認
2. **カバレッジ確認とREADME.mdバッジ更新**
   ```bash
   bash run_coverage.sh
   # htmlcov/index.html で実際のカバレッジを確認
   # カバレッジが変わっている場合は、README.mdのバッジを更新：
   # [![Test Coverage](https://img.shields.io/badge/coverage-XX%25-brightgreen)](htmlcov/index.html)
   # の XX% 部分を新しい値に変更
   ```
3. バージョン番号を提案
4. ユーザーにmainへのマージを依頼
5. バージョンタグ作成後、GitHub Releases用の情報を`.kiro/RELEASE_NOTES.md`に追記

#### チェックリスト（実装開始前）

- [ ] `git branch` でブランチを確認した
- [ ] mainブランチの場合、ユーザーにブランチ作成を依頼した
- [ ] 開発ブランチにいることを確認した
- [ ] 上記が全て完了してから実装を開始した

#### チェックリスト（実装完了後）

- [ ] テストが全てパスした
- [ ] カバレッジを確認した（`bash run_coverage.sh`）
- [ ] カバレッジが変わっている場合、README.mdのバッジを更新した
- [ ] バージョン番号を提案した
- [ ] GitHub Releases用の情報を`.kiro/RELEASE_NOTES.md`に追記した

## まとめ

- **小さな追加機能**: Specモードで自律的に進める
- **大きな変更**: Vibeモードで仕様を詰めてからSpecモードへ
- **テスト品質**: しっかり維持（95%カバレッジ目標）
- **ドキュメント**: Kiroが自動更新
- **バージョン**: Kiroが提案、ユーザーが決定
- **ブランチ**: Spec作成はmain、コード実装は開発ブランチ

このワークフローにより、効率的かつ品質の高い開発が可能になります。