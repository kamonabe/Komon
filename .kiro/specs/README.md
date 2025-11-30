# Spec（仕様書）ディレクトリ

このディレクトリには、Komonの各機能のSpec（仕様書）が格納されています。

## 📋 Specファイルの形式

### ファイル形式

**構造化YAML形式**を使用します：

- **拡張子**: `.yml`
- **内容**: 構造化データ（辞書型、リスト型を使用）
- **パース**: `yaml.safe_load()`で読み込み可能
- **検証**: `scripts/validate_specs.py`で構造を検証

### 3つの必須ファイル

各機能のSpecは以下の3ファイルで構成されます：

```
.kiro/specs/{feature-name}/
├── requirements.yml  # 要件定義
├── design.yml        # 設計書
└── tasks.yml         # 実装タスク
```

## 📝 各ファイルの構造

### 1. requirements.yml（要件定義）

```yaml
metadata:
  title: 機能名 - 要件定義
  feature: feature-name
  status: draft | in-progress | implemented | deprecated
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  complexity: low | medium | high
  estimated-hours: 8
  dependencies: []

overview:
  description: |
    機能の概要

acceptance-criteria:
  - id: AC-001
    title: |
      受入基準のタイトル
      **WHEN** 条件
      **THEN** 期待される結果
    priority: high | medium | low
    type: functional | non-functional | security | performance
    user-story: ""
    conditions: []

constraints:
  technical: []
  business: []
  compatibility: []

out-of-scope: []
```

### 2. design.yml（設計書）

```yaml
metadata:
  title: 機能名 - 設計書
  feature: feature-name
  status: draft | in-progress | implemented | deprecated
  created: YYYY-MM-DD
  updated: YYYY-MM-DD

architecture:
  overview: |
    アーキテクチャの概要
  components:
    - name: コンポーネント名
      responsibility: 責務
      location: ファイルパス
  data-flow: |
    データフロー

correctness-properties:
  - id: PROP-001
    title: プロパティのタイトル
    description: |
      検証する内容
    validates: [AC-001, AC-002]
    test-strategy: property-based | integration | unit
    implementation: |
      テスト実装の方針

implementation-details:
  modules: []
  configuration: []
  error-handling: []

resilience:
  circuit-breaker:
    considered: true
    decision: adopted | not-adopted | delegated | not-applicable
    rationale: |
      理由
    implementation: []

testing-strategy:
  property-tests: []
  integration-tests: []
  unit-tests: []

backward-compatibility:
  breaking-changes: []
  migration-required: false
  migration-guide: ""
```

### 3. tasks.yml（実装タスク）

```yaml
metadata:
  title: 機能名 - 実装タスク
  feature: feature-name
  status: draft | in-progress | completed
  created: YYYY-MM-DD
  updated: YYYY-MM-DD

tasks:
  - id: 1
    title: タスクのタイトル
    description: |
      タスクの詳細
    validates: [AC-001]
    estimated-hours: 2
    status: pending | in-progress | completed
    dependencies: []
    subtasks:
      - サブタスク1
      - サブタスク2

completion-criteria:
  - criterion: 完了条件
    status: pending | completed

notes:
  - 実装時の注意事項
```

## 🎯 Specの作成方法

### 方法1: テンプレートを使用

```bash
# 新しい機能のディレクトリを作成
mkdir -p .kiro/specs/new-feature

# テンプレートをコピー
cp .kiro/specs/_templates/requirements.yml.template .kiro/specs/new-feature/requirements.yml
cp .kiro/specs/_templates/design.yml.template .kiro/specs/new-feature/design.yml
cp .kiro/specs/_templates/tasks.yml.template .kiro/specs/new-feature/tasks.yml

# 内容を編集
vim .kiro/specs/new-feature/requirements.yml
vim .kiro/specs/new-feature/design.yml
vim .kiro/specs/new-feature/tasks.yml
```

### 方法2: Kiroに依頼

```
「新機能XXXのSpecを作成して」
```

Kiroが自動的に3ファイルを作成します。

## ✅ Specの検証

### 構造検証

```bash
# 全Specの構造を検証
python scripts/validate_specs.py
```

**検証項目**:
- ✅ YAMLの構文が正しいか
- ✅ 必須フィールドが存在するか
- ✅ 日付フォーマットが正しいか（YYYY-MM-DD）
- ✅ 受入基準が3個以上あるか（推奨）
- ✅ 正確性プロパティが3個以上あるか（推奨）

### 一貫性検証

```bash
# 3ファイル間の一貫性を検証
python scripts/check_spec_consistency.py
```

**検証項目**:
- ✅ 3ファイルのfeature名が一致しているか
- ✅ 存在しない受入基準を参照していないか
- ✅ プロパティが受入基準を参照しているか
- ✅ タスクが受入基準をカバーしているか

## 📊 既存のSpec一覧

```bash
# Spec一覧を表示
ls -1 .kiro/specs/ | grep -v _templates | grep -v README.md
```

現在のSpec:
- `contextual-advice/` - 文脈に応じたアドバイス
- `disk-trend-prediction/` - ディスク使用量予測
- `duplicate-process-detection/` - 重複プロセス検知
- `log-tail-excerpt/` - ログ末尾抜粋
- `notification-history/` - 通知履歴
- `notification-throttle/` - 通知頻度制御
- `progressive-notification/` - 段階的通知メッセージ
- `progressive-threshold/` - 段階的閾値通知
- `weekly-health-report/` - 週次ヘルスレポート

## 🔍 トラブルシューティング

### Q: YAMLの構文エラーが出る

**A**: 以下を確認してください：

```bash
# YAML構文チェック
python -c "import yaml; yaml.safe_load(open('.kiro/specs/feature-name/requirements.yml'))"
```

**よくあるエラー**:
- インデントが不正（スペース2個で統一）
- コロン（:）の後にスペースがない
- リスト（-）の後にスペースがない
- 文字列に特殊文字が含まれている（`|`で複数行文字列に）

### Q: 検証スクリプトが失敗する

**A**: エラーメッセージを確認してください：

```bash
python scripts/validate_specs.py
```

**エラーの種類**:
- ❌ **エラー**: 必須フィールドが不足、構文エラー → 修正必須
- ⚠️ **警告**: 推奨事項（受入基準が3個未満等） → 機能の規模に応じて判断

### Q: テンプレートと既存Specの形式が違う

**A**: 既存Specは正しい形式です。テンプレートは参考用です。

既存Specを参考にしてください：
```bash
cat .kiro/specs/progressive-threshold/requirements.yml
```

## 📚 関連ドキュメント

- **開発ワークフロー**: `.kiro/steering/development-workflow.md`
- **Spec品質保証**: `.kiro/steering/spec-quality-assurance.md`
- **タスク管理**: `.kiro/steering/task-management.md`

## まとめ

- **形式**: 構造化YAML（.yml拡張子）
- **構成**: requirements.yml + design.yml + tasks.yml
- **検証**: validate_specs.py + check_spec_consistency.py
- **作成**: テンプレート使用 or Kiroに依頼

このルールに従うことで、一貫性のある高品質なSpecが作成できます。
