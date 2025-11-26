# ステアリングルール - 使い方ガイド

## 概要

このディレクトリには、Kiro AIの動作を制御する**ステアリングルール**が格納されています。

ステアリングルールは**テンプレート化**されており、プロジェクト設定を変更するだけで、他のプロジェクトでも同じルールを使用できます。

## ディレクトリ構造

```
.kiro/
├── steering/                          # ステアリングルール
│   ├── README.md                      # このファイル
│   ├── project-config.yml             # プロジェクト固有の設定
│   ├── _templates/                    # ルールテンプレート（汎用）
│   │   ├── versioning-rules.template.md
│   │   ├── development-workflow.template.md
│   │   ├── task-management.template.md
│   │   ├── spec-quality-assurance.template.md
│   │   ├── error-handling-and-logging.template.md
│   │   ├── environment-and-communication.template.md
│   │   └── commit-message-rules.template.md
│   └── [生成されたルール]              # テンプレートから生成
│       ├── versioning-rules.md
│       ├── development-workflow.md
│       ├── task-management.md
│       ├── spec-quality-assurance.md
│       ├── error-handling-and-logging.md
│       ├── environment-and-communication.md
│       └── commit-message-rules.md
└── tasks/                             # タスク管理
    ├── _templates/                    # タスクテンプレート（汎用）
    │   └── implementation-tasks.template.md
    ├── implementation-tasks.md        # 実装タスクリスト（進行中・未着手）
    └── completed-tasks.md             # 完了タスクアーカイブ
```

## 使い方

### 1. Komonプロジェクトでルールを更新する場合

#### ステップ1: テンプレートを編集

```bash
# 例: バージョニングルールを修正
vim .kiro/steering/_templates/versioning-rules.template.md
```

#### ステップ2: ルールを再生成

```bash
python scripts/generate_steering_rules.py
```

#### ステップ3: 差分を確認

```bash
git diff .kiro/steering/*.md
```

#### ステップ4: コミット

```bash
git add .kiro/steering/
git commit -m "docs: ステアリングルールを更新"
```

### 1-2. タスクテンプレートを更新する場合

#### ステップ1: テンプレートを編集

```bash
vim .kiro/tasks/_templates/implementation-tasks.template.md
```

#### ステップ2: テンプレートを再生成（新規プロジェクト用）

⚠️ **注意**: このコマンドは既存の`implementation-tasks.md`を上書きします！

```bash
python scripts/generate_task_template.py
```

**既存プロジェクトの場合**: テンプレートは参考用として、実際のタスクは手動で管理してください。

#### ステップ3: 差分を確認

```bash
git diff .kiro/steering/*.md
```

#### ステップ4: コミット

```bash
git add .kiro/steering/
git commit -m "docs: ステアリングルールを更新"
```

### 2. 他のプロジェクトでKomonのルールを使う場合

#### ステップ1: テンプレートとスクリプトをコピー

```bash
# Komonプロジェクトから
cp -r /path/to/komon/.kiro/steering/_templates /path/to/myproject/.kiro/steering/
cp -r /path/to/komon/.kiro/tasks/_templates /path/to/myproject/.kiro/tasks/
cp /path/to/komon/scripts/generate_steering_rules.py /path/to/myproject/scripts/
cp /path/to/komon/scripts/generate_task_template.py /path/to/myproject/scripts/
```

#### ステップ2: プロジェクト設定を作成

```bash
cd /path/to/myproject
vim .kiro/steering/project-config.yml
```

**例: Node.jsプロジェクトの場合**

```yaml
# MyProjectプロジェクト設定
project:
  name: "MyProject"
  type: "web-app"
  language: "node"
  description: "素晴らしいWebアプリケーション"

environment:
  platform: "Ubuntu 22.04"
  platform_type: "Debian"
  shell: "bash"
  package_manager: "apt"
  node_version: "20+"

communication:
  language: "en"
  language_name: "English"
  use_emoji: true

versioning:
  scheme: "semver"
  initial_version: "0.1.0"
  current_version: "0.1.0"

testing:
  framework: "jest"
  coverage_target: 90
  property_testing: false

git:
  main_branch: "main"
  branch_prefix:
    feature: "feature/"
    bugfix: "bugfix/"
    refactor: "refactor/"

spec:
  location: ".kiro/specs/"
  required_files:
    - "requirements.md"
    - "design.md"
    - "tasks.md"
  validation_scripts:
    - "scripts/validate_specs.py"
    - "scripts/check_spec_consistency.py"

changelog:
  location: "CHANGELOG.md"
  format: "keep-a-changelog"

# プロジェクト固有の境界線ケース（バージョニング）
versioning_boundary_cases:
  - change: "APIエンドポイントの追加"
    version: "MINOR"
    reason: "後方互換性あり"
  - change: "APIエンドポイントの削除"
    version: "MAJOR"
    reason: "破壊的変更"
  - change: "内部リファクタリング"
    version: "PATCH"
    reason: "ユーザーには見えない"
```

#### ステップ3: 依存パッケージをインストール

```bash
pip install jinja2 pyyaml
```

#### ステップ4: ステアリングルールを生成

```bash
python scripts/generate_steering_rules.py
```

#### ステップ5: タスクテンプレートを生成

```bash
python scripts/generate_task_template.py
```

#### ステップ6: 生成されたファイルを確認

```bash
ls -la .kiro/steering/*.md
ls -la .kiro/tasks/implementation-tasks.md
```

#### ステップ7: Kiroで使用開始

生成されたルールは自動的にKiroに読み込まれます。

**タスク管理の開始**:
- `implementation-tasks.md`に実際のタスク（TASK-001, TASK-002...）を追加
- `future-ideas.md`でアイデアを管理
- 次のバージョンリリース時に完了タスクを`completed-tasks.md`にアーカイブ

### 3. プロジェクト設定のカスタマイズ

#### 必須フィールド

```yaml
project:
  name: "プロジェクト名"          # 必須
  type: "cli-tool|library|web-app"  # 必須
  language: "python|node|..."       # 必須

environment:
  platform: "OS名"                  # 必須
  shell: "bash|zsh|..."             # 必須
  package_manager: "dnf/yum|apt|..." # 必須

communication:
  language: "ja|en|zh|..."          # 必須
  language_name: "日本語|English|..." # 必須

git:
  main_branch: "main|master"        # 必須
  branch_prefix:                    # 必須
    feature: "feature/"
    bugfix: "bugfix/"
    refactor: "refactor/"

spec:
  location: ".kiro/specs/"          # 必須
  required_files:                   # 必須
    - "requirements.md"
    - "design.md"
    - "tasks.md"

changelog:
  location: "docs/CHANGELOG.md"     # 必須
```

#### オプションフィールド

```yaml
testing:
  framework: "pytest|jest|..."      # オプション
  coverage_target: 95               # オプション
  property_testing: true            # オプション
  property_framework: "hypothesis"  # オプション

versioning_boundary_cases:         # オプション
  - change: "変更内容"
    version: "MAJOR|MINOR|PATCH"
    reason: "理由"
```

## テンプレート変数リファレンス

### 利用可能な変数

| 変数 | 説明 | 例 |
|------|------|-----|
| `{{project.name}}` | プロジェクト名 | `Komon` |
| `{{project.type}}` | プロジェクトタイプ | `cli-tool` |
| `{{project.language}}` | プログラミング言語 | `python` |
| `{{environment.platform}}` | 実行環境 | `AlmaLinux 9` |
| `{{environment.shell}}` | シェル | `bash` |
| `{{environment.package_manager}}` | パッケージマネージャー | `dnf/yum` |
| `{{communication.language}}` | コミュニケーション言語 | `ja` |
| `{{communication.language_name}}` | 言語名 | `日本語` |
| `{{git.main_branch}}` | メインブランチ名 | `main` |
| `{{testing.framework}}` | テストフレームワーク | `pytest` |
| `{{testing.coverage_target}}` | カバレッジ目標 | `95` |
| `{{spec.location}}` | Spec保存場所 | `.kiro/specs/` |
| `{{changelog.location}}` | CHANGELOG場所 | `docs/CHANGELOG.md` |

### 条件分岐

```jinja2
{% if project.type == "cli-tool" %}
CLIツール固有の内容
{% endif %}

{% if project.language == "python" %}
Python固有の内容
{% endif %}

{% if communication.language == "ja" %}
日本語の内容
{% endif %}
```

### ループ

```jinja2
{% for file in spec.required_files %}
- {{file}}
{% endfor %}

{% for script in spec.validation_scripts %}
python {{script}}
{% endfor %}
```

### フィルター

```jinja2
{{project.name|lower}}        # 小文字に変換: komon
{{project.name|upper}}        # 大文字に変換: KOMON
{{script|basename}}           # ファイル名のみ: validate_specs.py
{{spec.required_files|length}} # 配列の長さ: 3
```

## トラブルシューティング

### Q: 生成スクリプトが失敗する

**A**: 以下を確認してください：

```bash
# Pythonバージョン確認（3.10以上）
python --version

# 依存パッケージインストール
pip install jinja2 pyyaml

# 設定ファイルの構文確認
python -c "import yaml; yaml.safe_load(open('.kiro/steering/project-config.yml'))"
```

### Q: テンプレート変数が展開されない

**A**: `project-config.yml`に該当する変数が定義されているか確認してください。

```bash
# 設定ファイルの内容を確認
cat .kiro/steering/project-config.yml
```

### Q: 生成されたルールが期待と違う

**A**: テンプレートファイルを確認してください。

```bash
# テンプレートを確認
cat .kiro/steering/_templates/versioning-rules.template.md
```

## ベストプラクティス

### 1. テンプレートは汎用的に保つ

プロジェクト固有の内容は`project-config.yml`に記述し、テンプレートは汎用的に保ちます。

**❌ 悪い例（テンプレートにプロジェクト固有の内容）**:
```markdown
Komonプロジェクトでは...
```

**✅ 良い例（変数を使用）**:
```markdown
{{project.name}}プロジェクトでは...
```

### 2. 条件分岐を活用

プロジェクトタイプや言語によって内容を変える場合は、条件分岐を使います。

```jinja2
{% if project.type == "cli-tool" %}
- CLIコマンドの実行結果
{% endif %}

{% if project.type == "library" %}
- 公開APIの動作確認
{% endif %}
```

### 3. デフォルト値を設定

オプションフィールドにはデフォルト値を設定します。

```jinja2
カバレッジ目標: {{testing.coverage_target|default(90)}}%
```

### 4. コメントで説明を追加

`project-config.yml`にはコメントで説明を追加します。

```yaml
testing:
  framework: "pytest"           # テストフレームワーク
  coverage_target: 95           # カバレッジ目標（%）
  property_testing: true        # プロパティテストを使用するか
```

## まとめ

- **テンプレート**: 汎用的なルール（`_templates/`）
- **設定ファイル**: プロジェクト固有の情報（`project-config.yml`）
- **生成スクリプト**: テンプレート + 設定 → ルール（`generate_steering_rules.py`）

このアプローチにより、Komonの開発ルールを他のプロジェクトでも簡単に使用できます。
