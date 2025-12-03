# {{project.name}}仕様駆動開発ワークフロー

## 開発の基本方針

{{project.name}}プロジェクトは**仕様駆動開発（Spec-Driven Development）**を採用しています。

## アイデアから実装までの流れ

### 1. アイデア段階
**ファイル**: `{{spec.location}}future-ideas.md`

- 新機能のアイデアはまず`future-ideas.md`に追加
- アイデアの検討・熟成期間を設ける
- 実装に値するかどうかを判断

### 2. 実装決定
**ファイル**: `.kiro/tasks/implementation-tasks.md`

- 実装を決定したアイデアを`TASK-XXX`として追加
- 優先度、見積もり、背景を記載
- タスク分解を行う

### 3. Spec作成（{{git.main_branch}}ブランチ）

**🚨 必須手順: Spec作成前の確認**

Kiroは新しいSpecを作成する前に、**必ず以下を実行**してください：

#### **ステップ1: 既存のSpecファイルの構造を確認**

```bash
# 既存のSpecディレクトリを確認
ls {{spec.location}}contextual-advice/

# requirements.ymlの形式を確認（先頭50行）
head -50 {{spec.location}}contextual-advice/requirements.yml

# テンプレートを確認
ls {{spec.location}}_templates/
```

#### **ステップ2: ファイル形式の確認**

確認ポイント：
- [ ] ファイル拡張子は`.yml`である（`.md`ではない）
- [ ] 内容はYAML構造化形式である（Markdownではない）
- [ ] `metadata`, `overview`, `acceptance-criteria`などのセクションがある
- [ ] 上記を確認してから作成を開始する

#### **ステップ3: Specファイルの作成**

**フォルダ**: `{{spec.location}}{feature-name}/`

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

**テンプレート**: `{{spec.location}}_templates/` を参照

**この時点ではまだ{{git.main_branch}}ブランチでOK**

### 4. 🚨 実装開始前の必須チェック 🚨

**⚠️ 重要**: このチェックをスキップすると{{git.main_branch}}ブランチが破壊される危険性があります。

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
- ❌ **{{git.main_branch}}ブランチにいる場合**: **即座に停止**

#### **ステップ3: {{git.main_branch}}ブランチの場合の対応**
**Kiroは以下を必ず実行**：

1. **実装を開始しない**（コード変更を一切行わない）
2. **明確な警告を表示**：
   ```
   🚨 危険: {{git.main_branch}}ブランチで実装しようとしています
   
   【リスク】
   - {{git.main_branch}}ブランチの破壊
   - 他の開発者への影響
   - リリース品質の低下
   
   【必要な作業】
   開発ブランチを作成してください：
   
   git checkout -b {{git.branch_prefix.feature}}XXX-{feature-name}
   
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
# ❌ まだ{{git.main_branch}}ブランチ → 再度警告
```

#### **ステップ5: 最終安全確認**
実装開始直前に以下を確認：
- [ ] 開発ブランチにいることを確認済み
- [ ] 作業ディレクトリがクリーンであることを確認済み
- [ ] システム時刻が正常であることを確認済み
- [ ] 上記が全て完了してから実装開始

**ブランチ作成コマンド（ユーザーが実行）**:
```bash
git checkout {{git.main_branch}}
git checkout -b {{git.branch_prefix.feature}}XXX-{feature-name}
```

**ブランチ命名規則**:
- `{{git.branch_prefix.feature}}001-progressive-notification`
- `{{git.branch_prefix.feature}}003-contextual-advice`
- `{{git.branch_prefix.bugfix}}fix-memory-leak` (バグ修正の場合)

### 5. 実装フェーズ（Kiroが自律的に進める）

Kiroは以下を**サブタスクごとに**実行します：

#### サブタスク1: コード実装
1. モジュールを実装
2. **即座にタスクファイルを更新**
   - Spec別タスクリスト: `[x]` を付ける
   - 実装タスクリスト: `[x]` を付ける + 進捗率を更新
3. ユーザーに報告: 「✅ サブタスク1完了、進捗: 1/3」

#### サブタスク2: テスト作成
1. テストを作成{% if testing.property_testing %}（プロパティテスト + 統合テスト + ユニットテスト）{% endif %}
2. **即座にタスクファイルを更新**
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

**Kiroへの指示**: ユーザーがバージョン番号を決定したら、**必ず以下をリマインド**してください：

```
📋 リリース前の必須作業（3つのファイルを更新）:

1. version.txtを更新してください：
   version.txt を新しいバージョン番号に変更
   
   変更例：
   1.18.1
   ↓
   1.19.0

2. CHANGELOGを更新してください：
   {{changelog.location}} の [Unreleased] を [1.X.X] - YYYY-MM-DD に変更

   変更例：
   ## [Unreleased]
   ↓
   ## [Unreleased]
   
   ## [1.X.X] - 2025-11-27

3. project-config.ymlのバージョンを更新してください：
   .kiro/steering/project-config.yml の current_version を更新

   変更例：
   versioning:
     current_version: "1.X.X"

4. この作業が完了したら、次のステップに進みます
```

**なぜ重要か**：
- ❌ version.txtを忘れると`pip install -e .`で古いバージョンが表示される
- ❌ CHANGELOGを忘れると`generate_release_notes.py`が動かない
- ❌ project-config.ymlを忘れるとステアリングルールが古いバージョンを参照する
- ❌ 3つのファイルのバージョンが不一致になる
- ❌ 次のリリース時に混乱する

**Kiroのチェックポイント**：
- [ ] ユーザーがバージョン番号を決定した
- [ ] version.txtの更新をリマインドした
- [ ] CHANGELOGの更新をリマインドした
- [ ] project-config.ymlの更新をリマインドした
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

### 9. {{git.main_branch}}ブランチへのマージとタグ作成

**ユーザーが実行**：

```bash
git checkout {{git.main_branch}}
git merge {{git.branch_prefix.feature}}XXX-{feature-name}
git tag v1.X.X
git push origin {{git.main_branch}} --tags
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
- **{{changelog.location}}から該当バージョンを抽出**
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

## テスト品質の基準

{{project.name}}では**しっかりしたテスト**を維持します：

### 必須テスト
{% if testing.property_testing %}
1. **プロパティベーステスト**（{{testing.property_framework}}使用）
   - 正確性プロパティを検証
   - 不変条件のテスト
   
2. **統合テスト**
   - 既存機能との統合確認
   - エンドツーエンドの動作確認
   
3. **ユニットテスト**
   - 個別関数の動作確認
   - エッジケースのテスト
{% else %}
1. **統合テスト**
   - 既存機能との統合確認
   - エンドツーエンドの動作確認
   
2. **ユニットテスト**
   - 個別関数の動作確認
   - エッジケースのテスト
{% endif %}

### テストカバレッジ
- 目標: {{testing.coverage_target}}%以上（90%以上なら許容）
- 全テストがパスすることを確認

## テスト戦略の詳細

{{project.name}}では、**3層テスト構造**を採用し、異なる観点から品質を保証します。

### テストの3層構造

#### 1. プロパティベーステスト（Property-Based Testing）
{% if testing.property_testing %}
**目的**: 仕様の正確性を数学的に検証する

**対象**:
- 不変条件（Invariants）
- 数学的な性質（例: 線形回帰の正確性、平均値計算）
- 境界値の挙動

**ファイル命名**: `test_{module}_properties.py`

**例（{{project.name}}の場合）**:
{% if project.language == "python" %}
```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(min_value=0.0, max_value=100.0), min_size=2))
def test_property_calculation_accuracy(data):
    """
    任意のデータに対して、計算結果は数学的に正しい値でなければならない
    
    **検証要件: AC-001**
    """
    result = calculate_average(data)
    expected = sum(data) / len(data)
    assert abs(result - expected) < 0.0001
```
{% endif %}

**書くべきプロパティ**:
- ✅ 計算結果の正確性（例: 平均値、傾き、閾値判定）
- ✅ 不変条件（例: ソート後も要素数は同じ、閾値の順序性）
- ✅ 境界値の挙動（例: 0%, 100%, 閾値ちょうど）
- ✅ 冪等性（例: 同じ入力で同じ出力）

**書かなくて良いもの**:
- ❌ ファイルI/O
- ❌ 外部API呼び出し
- ❌ 複数モジュールの連携
{% else %}
**注**: {{project.name}}ではプロパティテストを使用していません。
{% endif %}

#### 2. 統合テスト（Integration Testing）

**目的**: 複数モジュールの連携を検証する

**対象**:
- モジュール間のデータフロー
- ファイルI/O（実ファイル使用）
- エンドツーエンドの動作
{% if project.type == "cli-tool" %}
- CLIコマンドの実行結果
{% endif %}

**ファイル命名**: `test_{module}_integration.py`

**例（{{project.name}}の場合）**:
{% if project.language == "python" %}
```python
def test_end_to_end_with_data(tmp_path, capsys):
    """
    エンドツーエンドの動作を確認
    
    **検証要件: AC-005**
    """
    # 実際のファイルを作成（tmp_path使用）
    test_dir = tmp_path / "data"
    test_dir.mkdir()
    test_file = test_dir / "test.csv"
    test_file.write_text("timestamp,cpu,mem,disk\n2025-11-25 10:00:00,50.0,60.0,70.0")
    
    # モジュールを実行
    result = process_data(str(test_dir))
    
    # 結果を検証
    assert result['cpu'] == 50.0
```
{% endif %}

**書くべきテスト**:
{% if project.type == "cli-tool" %}
- ✅ CLIコマンドの実行結果
{% endif %}
- ✅ ファイル読み書き
- ✅ 複数モジュールの連携
- ✅ エラーハンドリング（実際のエラーケース）
- ✅ データフローの確認

**モックの使い方**:
- ✅ 外部API（Slack, Email, HTTP等）はモック
- ✅ 時刻依存の処理はモック（`freezegun`使用）
- ✅ ランダム値はモック（再現性のため）
- ❌ ファイルI/Oは実ファイル（`tmp_path`使用）
- ❌ 内部モジュールはモックしない

#### 3. ユニットテスト（Unit Testing）

**目的**: 個別関数のロジックを検証する

**対象**:
- 単一関数の動作
- エッジケース
- エラーハンドリング

**ファイル命名**: `test_{module}_unit.py` または `test_{module}.py`

**例（{{project.name}}の場合）**:
{% if project.language == "python" %}
```python
def test_calculate_insufficient_data():
    """
    データが不足している場合、適切なエラーを発生させる
    
    **検証要件: AC-001**
    """
    data = []
    
    with pytest.raises(ValueError, match="データが不足"):
        calculate_average(data)
```
{% endif %}

**書くべきテスト**:
- ✅ 正常系（典型的な入力）
- ✅ 異常系（不正な入力）
- ✅ エッジケース（空、1件、境界値）
- ✅ エラーメッセージの検証

**書かなくて良いもの**:
- ❌ 複数モジュールの連携
- ❌ ファイルI/O
- ❌ 外部API呼び出し

### テストデータの管理

#### 一時ファイルの使用

統合テストでファイルI/Oをテストする場合、`pytest`の`tmp_path`フィクスチャを使用します。

{% if project.language == "python" %}
```python
def test_with_file(tmp_path):
    """一時ファイルを使ったテスト"""
    # 一時ディレクトリを作成
    test_dir = tmp_path / "data"
    test_dir.mkdir()
    
    # ファイルを作成
    test_file = test_dir / "test.csv"
    test_file.write_text("data")
    
    # テスト実行...
    result = load_data(str(test_file))
    assert result is not None
```
{% endif %}

**ルール**:
- ✅ `tmp_path`を使う（自動クリーンアップ）
- ❌ 実際のプロジェクトディレクトリにファイルを作らない
- ❌ テスト後に手動でファイルを削除しない

#### モックの使用

外部依存をモックする場合、`unittest.mock`または`pytest-mock`を使用します。

{% if project.language == "python" %}
```python
from unittest.mock import patch, MagicMock

def test_external_api_call():
    """外部API呼び出しのテスト（モック使用）"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        
        send_notification("test message")
        
        # 呼び出しを検証
        mock_post.assert_called_once()
        assert 'test message' in str(mock_post.call_args)
```
{% endif %}

**モックする対象**:
- ✅ 外部API（Slack, Email, HTTP）
- ✅ 時刻依存の処理（`datetime.now()`）
- ✅ ランダム値（`random.random()`）
- ✅ 環境変数（テストごとに独立させる）
- ❌ 内部モジュール（原則モックしない）

### 新機能追加時のテスト作成フロー

Kiroが新機能を実装する際、以下の順序でテストを作成します：

#### ステップ1: design.mdの正確性プロパティを確認

```markdown
## 正確性プロパティ

### Property 1: 計算結果の正確性
任意のデータに対して、計算結果は数学的に正しい値でなければならない

**検証対象**: AC-001, AC-002
```

{% if testing.property_testing %}
#### ステップ2: プロパティテストを作成

{% if project.language == "python" %}
```python
# tests/test_{module}_properties.py

from hypothesis import given, strategies as st

@given(st.lists(...))
def test_property_calculation_accuracy(data):
    """
    **Feature: {feature-name}, Property 1: 計算結果の正確性**
    
    任意のデータに対して、計算結果は数学的に正しい値でなければならない
    
    **検証要件: AC-001, AC-002**
    """
    result = calculate(data)
    # 検証ロジック...
    assert result is not None
```
{% endif %}
{% endif %}

#### ステップ{% if testing.property_testing %}3{% else %}2{% endif %}: 統合テストを作成

{% if project.language == "python" %}
```python
# tests/test_{module}_integration.py

def test_end_to_end_with_data(tmp_path{% if project.type == "cli-tool" %}, capsys{% endif %}):
    """
    エンドツーエンドの動作を確認
    
    **検証要件: AC-005**
    """
    # 実ファイルを作成
    test_dir = tmp_path / "data"
    test_dir.mkdir()
    
    # 処理を実行
    result = process_data(str(test_dir))
    
    # 結果を検証
    assert result is not None
```
{% endif %}

#### ステップ{% if testing.property_testing %}4{% else %}3{% endif %}: ユニットテストを作成

{% if project.language == "python" %}
```python
# tests/test_{module}_unit.py

def test_calculate_insufficient_data():
    """
    データ不足時のエラーハンドリング
    
    **検証要件: AC-001**
    """
    with pytest.raises(ValueError):
        calculate([])
```
{% endif %}

### テストカバレッジの目標

- **全体**: {{testing.coverage_target}}%以上を目標（90%以上なら許容）
- **新規モジュール**: 90%以上（初回実装時）
- **既存モジュール**: 現状維持または向上

**判断基準**:
- {{testing.coverage_target}}%達成: 理想的な状態
- 90-{{testing.coverage_target|int - 1}}%: 許容範囲（主要機能がカバーされていればOK）
- 90%未満: 追加テストを検討

**カバレッジ確認**:
{% if project.language == "python" %}
```bash
bash run_coverage.sh
# htmlcov/index.html で確認
```
{% endif %}

### スクリプトファイルのテスト

{% if project.type == "cli-tool" %}
`scripts/`配下の実行スクリプトも、最低限のインポートテストを追加します。
{% else %}
実行スクリプトがある場合は、最低限のインポートテストを追加します。
{% endif %}

**目的**: 実行時まで発覚しないImportErrorを防ぐ

**対象**:
{% if project.type == "cli-tool" %}
- `scripts/main.py` - メイン監視スクリプト
- `scripts/advise.py` - アドバイス表示
- `scripts/status.py` - ステータス表示
- その他の実行スクリプト
{% else %}
- プロジェクトの実行スクリプト
{% endif %}

**テスト内容**:
- ✅ インポートが成功すること
- ✅ 主要な関数が存在すること
- ✅ 依存モジュールが正しくインポートされること

**ファイル命名**: `test_scripts_import.py`

**例**:
{% if project.language == "python" %}
```python
"""スクリプトファイルのインポートテスト"""

import sys
import pytest
from pathlib import Path


class TestScriptsImport:
    """スクリプトファイルのインポートテスト"""
    
    def setup_method(self):
        """テスト前にscriptsディレクトリをパスに追加"""
        scripts_path = Path(__file__).parent.parent / "scripts"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
    
    def test_main_script_imports(self):
        """main.pyが正常にインポートできることを確認"""
        try:
            import main
            assert hasattr(main, 'main')
            assert hasattr(main, 'load_config')
        except ImportError as e:
            pytest.fail(f"main.pyのインポートに失敗: {e}")
```
{% endif %}

**ルール**:
- ✅ 全ての実行スクリプトにインポートテストを追加
- ✅ 主要な関数の存在確認も行う
- ✅ CI/CDでも実行する
- ❌ 詳細な動作テストは不要（統合テストで実施）

**効果**:
- ImportErrorを実行前に検知
- 関数名の変更による影響を早期発見
- リファクタリング時の安全性向上

### Kiroへの指示

#### テスト作成時のチェックリスト

新機能実装時、Kiroは以下を確認します：

{% if testing.property_testing %}
- [ ] design.mdの正確性プロパティを全てプロパティテストで検証した
{% endif %}
{% if project.type == "cli-tool" %}
- [ ] CLIコマンドや複数モジュールの連携を統合テストで検証した
{% else %}
- [ ] 複数モジュールの連携を統合テストで検証した
{% endif %}
- [ ] エッジケースをユニットテストで検証した
- [ ] 全テストに`**検証要件: AC-XXX**`を記載した
- [ ] モックは外部APIのみに使用した
- [ ] ファイルI/Oは`tmp_path`を使用した
- [ ] スクリプトファイルのインポートテストを追加した（新規スクリプト追加時）
- [ ] カバレッジが90%以上を維持している（{{testing.coverage_target}}%以上が理想）

#### テスト実行の順序

実装完了後、Kiroは以下の順序でテストを実行します：

1. **ユニットテスト**（高速）
{% if project.language == "python" %}
   ```bash
   python -m {{testing.framework}} tests/test_{module}_unit.py -v
   ```
{% endif %}

{% if testing.property_testing %}
2. **プロパティテスト**（中速）
{% if project.language == "python" %}
   ```bash
   python -m {{testing.framework}} tests/test_{module}_properties.py -v
   ```
{% endif %}
{% endif %}

{% if testing.property_testing %}3{% else %}2{% endif %}. **統合テスト**（低速）
{% if project.language == "python" %}
   ```bash
   python -m {{testing.framework}} tests/test_{module}_integration.py -v
   ```
{% endif %}

{% if testing.property_testing %}4{% else %}3{% endif %}. **全テスト + カバレッジ**
{% if project.language == "python" %}
   ```bash
   bash run_coverage.sh
   ```
{% endif %}

### トラブルシューティング

{% if testing.property_testing %}
#### Q: プロパティテストと統合テストの境界が曖昧

**A**: 以下の基準で判断してください：
- ファイルI/Oがある → 統合テスト
- 複数モジュールを使う → 統合テスト
- 純粋な計算ロジック → プロパティテスト
{% endif %}

#### Q: モックを使うべきか実ファイルを使うべきか迷う

**A**:
- 外部API（Slack, Email） → モック
- ファイルI/O → 実ファイル（`tmp_path`）
- 内部モジュール → モックしない

#### Q: テストが遅い

**A**: 以下を確認してください：
{% if testing.property_testing %}
- プロパティテストの`max_examples`を減らす（デフォルト100）
{% endif %}
- 統合テストで不要なファイル作成を減らす
{% if project.language == "python" %}
- `pytest -n auto`で並列実行
{% endif %}

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
│   ├── implementation-tasks.md      # 実装タスク管理（進行中・未着手）
│   └── completed-tasks.md           # 完了タスクアーカイブ
└── steering/
    ├── task-management.md           # タスク管理ルール
    └── development-workflow.md      # このファイル
```

## ワークフロー例

### 例1: 新機能「段階的通知メッセージ」

```
1. future-ideas.md に [IDEA-001] として記載（{{git.main_branch}}ブランチ）
   ↓
2. 実装を決定 → implementation-tasks.md に [TASK-001] 追加（{{git.main_branch}}ブランチ）
   ↓
3. {{spec.location}}progressive-notification/ を作成（{{git.main_branch}}ブランチ）
   - requirements.md: 要件定義
   - design.md: 設計書
   - tasks.md: タスクリスト
   ↓
4. ユーザー「TASK-001の実装を開始しよう」
   ↓
5. Kiro「Specモードで進めます。まず現在のブランチを確認します」
   git branch  # → {{git.main_branch}}ブランチにいることを確認
   ↓
6. Kiro「開発ブランチを作成してください：
         git checkout -b {{git.branch_prefix.feature}}001-progressive-notification」
   ↓
7. ユーザーがブランチを作成
   git checkout -b {{git.branch_prefix.feature}}001-progressive-notification
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
12. {{git.main_branch}}にマージしてタグ作成
    git checkout {{git.main_branch}}
    git merge {{git.branch_prefix.feature}}001-progressive-notification
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

### {{git.main_branch}}ブランチで作業してOK

以下の作業は**{{git.main_branch}}ブランチで直接**行います：

- ドキュメント整備（README, CHANGELOG等）
- future-ideas.mdへのアイデア追加
- implementation-tasks.mdへのタスク追加
- Spec作成（{% for file in spec.required_files %}{{file}}{% if not loop.last %}, {% endif %}{% endfor %}）
- ステアリングルールの追加・更新

### 開発ブランチを切る必要がある

以下の作業は**必ず開発ブランチ**を作成してから行います：

- **コード実装**（src/配下の変更）
- **テスト追加**（tests/配下の変更）
- **設定ファイル変更**（settings.yml, setup.py等）
- **依存パッケージ変更**（requirements.txt等）

### ブランチ命名規則

```
{{git.branch_prefix.feature}}XXX-{feature-name}     # 新機能
{{git.branch_prefix.bugfix}}{issue-description}     # バグ修正
{{git.branch_prefix.refactor}}{module-name}         # リファクタリング

例:
- {{git.branch_prefix.feature}}001-progressive-notification
- {{git.branch_prefix.feature}}003-contextual-advice
- {{git.branch_prefix.bugfix}}fix-memory-leak
- {{git.branch_prefix.refactor}}analyzer-module
```

## Git運用の安全策（複数マシン・チーム開発対応）

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
  - {{git.main_branch}}ブランチの作成
  - 初期commit/pushの案内

### 作業開始前の必須手順

**新しい作業ブランチを切る前に、必ず origin/{{git.main_branch}} と同期する**

これは**複数マシン開発**や**チーム開発**で、以下の事故を防ぐための保険：
- 古い{{git.main_branch}}から作業を開始してしまう
- 他の人の変更を知らずに開発してしまう
- マージ時に余計なコンフリクトが発生する

#### 手順

```bash
# 1. リモート情報を最新化
git fetch origin

# 2. {{git.main_branch}}に移動
git switch {{git.main_branch}}

# 3. origin/{{git.main_branch}}を取り込む
git pull origin {{git.main_branch}}

# 4. 最新の{{git.main_branch}}からfeatureブランチを作成
git switch -c {{git.branch_prefix.feature}}XXX-{feature-name}
```

#### なぜ必要か

一人開発では気づきにくいが、以下の状況で必須になる：
- **複数マシンで開発**：PC-Aで作業 → push → PC-Bで作業開始時にpull忘れ
- **チーム開発**：他の人が{{git.main_branch}}にマージ → 自分は古い{{git.main_branch}}から作業
- **長期間の作業**：feature作業中に{{git.main_branch}}が進んでいる

### マージ前の安全確認（マージテスト）

**{{git.main_branch}}に直接マージする前に、仮マージで動作確認を行う**

これは**{{git.main_branch}}を絶対に壊さない**ための文化。

#### 方法1: 仮マージ（--no-commit）

```bash
# {{git.main_branch}}にいることを確認
git checkout {{git.main_branch}}
git pull

# 仮マージ（コミットはしない）
git merge --no-commit --no-ff {{git.branch_prefix.feature}}beta

# この状態で確認
git status
git diff

# テスト実行
{% if project.language == "python" %}
python -m {{testing.framework}} tests/ -v
{% endif %}

# 問題なければコミット
git commit

# やめたい場合は
git merge --abort
```

#### 方法2: マージテスト用ブランチ（推奨）

```bash
# {{git.main_branch}}を最新化
git checkout {{git.main_branch}}
git pull

# テスト用ブランチを作成
git checkout -b merge-check/beta

# ここでfeature/betaをマージ
git merge {{git.branch_prefix.feature}}beta

# テスト実行・動作確認
{% if project.language == "python" %}
bash run_coverage.sh
{% endif %}

# 問題なければ正式にマージ
git checkout {{git.main_branch}}
git merge {{git.branch_prefix.feature}}beta

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
- **{{git.main_branch}}を守るための投資**
- **事故を未然に防ぐ文化**

### Kiroの役割（AI IDEによる自動化）

Kiroは以下を自動で実行・チェックできる：

#### 1. 作業前の同期チェック
- feature作成前に `git fetch origin` を自動実行
- origin/{{git.main_branch}}との差分を警告
- 古い{{git.main_branch}}からの作業開始を防ぐ

#### 2. マージ前の仮マージ自動実行
- merge-checkブランチを裏で作成
- {{git.main_branch}}とfeatureを自動統合
- テスト実行
- コンフリクト・意味的衝突を検知
- 結果をユーザーに提示

#### 3. ヒューマンエラーのゼロ化
人間のルールでは「うっかり」が必ず出るが、AI IDEが強制すれば：
- pull忘れ
- 古い{{git.main_branch}}での開発
- コンフリクト放置
- 動作確認不足
- {{git.main_branch}}破壊事故

これらを**構造的に防げる**。

少しの時間とクレジットで「不安ゼロ・事故ゼロ・正史保護」が手に入るなら、それは**開発品質への投資**。

### 🚨 Kiroへの厳格な指示 🚨

#### 実装開始前の必須手順（絶対に守る）

**⚠️ 重要**: この手順をスキップすると{{git.main_branch}}ブランチ破壊の危険性があります。

**TASK-XXXの実装を開始する際、Kiroは以下を厳格に実行：**

#### **フェーズ1: 宣言と環境確認**
1. **「Specモードで進めます」と宣言**
2. **安全性チェックの実行を宣言**：
   ```
   実装開始前に安全性チェックを実行します。
   ```

#### **フェーズ2: 必須安全性チェック**
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

#### **フェーズ3: ブランチ安全性の判定**
6. **{{git.main_branch}}ブランチにいる場合**:
   - ❌ **絶対にコード実装を開始しない**
   - ❌ **ファイル変更を一切行わない**
   - 🚨 **即座に危険警告を表示**:
     ```
     🚨 危険: {{git.main_branch}}ブランチで実装しようとしています
     
     【リスク】
     - {{git.main_branch}}ブランチの破壊
     - 他の開発者への影響  
     - リリース品質の低下
     
     【必要な作業】
     開発ブランチを作成してください：
     
     git checkout -b {{git.branch_prefix.feature}}XXX-{feature-name}
     
     ブランチ作成後、「ブランチ作成完了」とお知らせください。
     実装はそれまで開始しません。
     ```
   - ⏸️ **ユーザーの返答を待機**（実装は開始しない）

#### **フェーズ4: ブランチ作成完了の再確認**
7. **ユーザーから「ブランチ作成完了」の返答後**:
   ```bash
   # 再度ブランチ確認
   git branch
   ```
8. **開発ブランチ確認**:
   - ✅ **開発ブランチにいる場合**: 実装開始
   - ❌ **まだ{{git.main_branch}}ブランチの場合**: 再度警告・待機

#### **フェーズ5: 実装開始の最終確認**
9. **実装開始直前の宣言**:
   ```
   ✅ 安全性チェック完了
   - 開発ブランチ: 確認済み
   - 作業ディレクトリ: クリーン
   - システム時刻: 正常
   
   実装を開始します。
   ```

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
4. ユーザーに{{git.main_branch}}へのマージを依頼
5. バージョンタグ作成後、GitHub Releases用の情報を`.kiro/RELEASE_NOTES.md`に追記

#### チェックリスト（実装開始前）

**🚨 必須チェック項目（全て完了してから実装開始）**:

**環境安全性チェック**:
- [ ] `git branch` でブランチを確認した
- [ ] `git status` で作業ディレクトリの状態を確認した  
- [ ] `date` でシステム時刻を確認した

**ブランチ安全性チェック**:
- [ ] {{git.main_branch}}ブランチの場合、実装を開始しなかった
- [ ] {{git.main_branch}}ブランチの場合、危険警告を表示した
- [ ] {{git.main_branch}}ブランチの場合、ユーザーにブランチ作成を依頼した
- [ ] ユーザーの「ブランチ作成完了」返答を待機した

**最終確認**:
- [ ] 開発ブランチにいることを再確認した
- [ ] 安全性チェック完了を宣言した
- [ ] 上記が全て完了してから実装を開始した

**❌ 禁止事項**:
- [ ] {{git.main_branch}}ブランチでの実装開始
- [ ] ブランチ確認のスキップ
- [ ] 安全性チェックの省略

### 🛡️ 安全性向上のための追加対策

#### **1. 多重安全確認システム**

**実装開始前の3段階チェック**:
1. **環境チェック**: ブランチ・作業ディレクトリ・時刻
2. **安全性判定**: {{git.main_branch}}ブランチでの実装阻止
3. **最終確認**: 開発ブランチ確認後の実装開始

#### **2. エラー回復手順**

**{{git.main_branch}}ブランチで実装してしまった場合**:
```bash
# 1. 即座に作業を停止
git status

# 2. 変更をスタッシュ
git stash

# 3. 開発ブランチを作成
git checkout -b {{git.branch_prefix.feature}}XXX-{feature-name}

# 4. 変更を復元
git stash pop

# 5. 実装を継続
```

#### **3. システム環境の事前確認**

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

#### **4. 予防的措置**

**開発開始時の習慣**:
- 毎回必ずブランチ確認
- 実装前の環境チェック
- 定期的な時刻同期確認

**緊急時の対応**:
- 問題発生時は即座に作業停止
- 状況を正確に把握してから対処
- 不明な場合はユーザーに確認

#### **5. 品質保証の強化**

**実装品質の維持**:
- テストカバレッジの確認
- 後方互換性の検証
- ドキュメント更新の確認

**リリース前の最終チェック**:
- 全テストの実行
- 手動動作確認
- Git履歴の整合性確認

#### チェックリスト（実装完了後）

- [ ] テストが全てパスした
- [ ] カバレッジを確認した（`bash run_coverage.sh`）
- [ ] カバレッジが変わっている場合、README.mdのバッジを更新した
- [ ] バージョン番号を提案した
- [ ] GitHub Releases用の情報を`.kiro/RELEASE_NOTES.md`に追記した

### リリース前の最終確認

実装完了後、リリース前に以下を確認します：

#### 基本チェックリスト

- [ ] **全テストがパス**
{% if project.language == "python" %}
  ```bash
  bash run_coverage.sh
  ```
{% endif %}

- [ ] **カバレッジが目標値以上**
  - 目標: {{testing.coverage_target}}%以上（90%以上なら許容）

- [ ] **実際に動作確認（手動実行）**
{% if project.type == "cli-tool" %}
  ```bash
  # 主要コマンドを実行
  {{project.name|lower}} advise
  {{project.name|lower}} status
  ```
{% endif %}

#### 手動動作確認チェックリスト

新機能の手動確認を行います：

**基本動作確認**:
- [ ] 主要コマンドが正常に実行できる
- [ ] 設定ファイルが正しく読み込まれる
- [ ] 新機能が期待通り動作する
- [ ] エラーなく実行完了する

**設定変更テスト**:
- [ ] 機能の有効/無効切り替え（`enabled: true/false`）
- [ ] 詳細度の変更（該当する場合: minimal/normal/detailed）
- [ ] カスタム設定の動作確認
- [ ] デフォルト値での動作確認

**エラーハンドリング**:
- [ ] 不正な設定でもクラッシュしない
- [ ] エラーメッセージが分かりやすい（{{communication.language_name}}、原因と対処法）
- [ ] ログに詳細情報が記録される

**後方互換性**:
- [ ] 既存機能に影響がない
- [ ] 既存の設定ファイルで動作する
- [ ] 新機能を無効化しても従来通り動作する

- [ ] **ドキュメントが更新されている**
  - README.md
  - {{changelog.location}}
  - version.txt

- [ ] **CHANGELOGが記録されている**
  - `[Unreleased]`セクションに変更内容を記載

{% if project.type == "cli-tool" %}
#### cronジョブのテスト（該当する場合）

cronジョブで実行されるスクリプトは、以下を確認：

1. **手動実行テスト**
{% if project.language == "python" %}
   ```bash
   python scripts/main.py
   ```
{% endif %}

2. **ログ確認**
   ```bash
   tail -20 log/main.log
   ```

3. **1分待ってcron実行を確認**
   ```bash
   # 1分後
   tail -5 log/main.log
   ```

4. **エラーがないことを確認**
   - ImportError
   - 設定ファイルエラー
   - 実行時エラー
{% endif %}

#### リリース判断

全てのチェックが完了したら、リリース可能です：

1. ✅ 全テストパス
2. ✅ カバレッジ目標達成
3. ✅ 手動動作確認OK
{% if project.type == "cli-tool" %}
4. ✅ cronジョブ正常動作（該当する場合）
{% endif %}
5. ✅ ドキュメント更新完了

**リリース手順**:
1. {{git.main_branch}}にマージ
2. バージョンタグ作成
3. リモートにプッシュ
4. GitHub Releasesに登録
5. RELEASE_NOTES.mdをアーカイブ

### 既存テストの失敗への対応

新機能実装中に既存テストが失敗した場合の対応方針：

#### 1. 新機能と関係ない場合

**判断基準**:
- 失敗したテストが新機能のコードに触れていない
- 以前から存在していた問題の可能性がある
- 新機能を無効化してもテストが失敗する

**対応**:
- ✅ 既存の問題として記録（GitHub Issue作成）
- ✅ 新機能のリリースは継続
- ✅ 別タスクとして修正を計画
- ✅ {{changelog.location}}に「既知の問題」として記載（必要に応じて）

**例**:
```
TASK-003実装中に、notification_throttleのプロパティテスト2件が
DeadlineExceededで失敗。新機能とは無関係なため、Issue #XXXとして記録し、
vX.X.Xのリリースは継続。
```

#### 2. 新機能が原因の場合

**判断基準**:
- 失敗したテストが新機能のコードに関連している
- 新機能を無効化するとテストがパスする
- 既存機能の動作が変わった

**対応**:
- ❌ リリースを延期
- ✅ 即座に修正
- ✅ リリース前に全テストパスを確認
- ✅ 後方互換性を確認

**修正方針**:
1. 既存機能への影響を最小化
2. 新機能を無効化できるようにする（`enabled: false`）
3. デフォルト値で従来通り動作するようにする

### マージ時のトラブルシューティング

{{git.main_branch}}ブランチへのマージでエラーが発生した場合の対処法：

#### エラー: "Your local changes would be overwritten by merge"

**原因**: {{git.main_branch}}ブランチに未コミットの変更が残っている

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
git merge {{git.branch_prefix.feature}}XXX-feature-name
```

#### エラー: "unable to create file ... No such file or directory"

**原因**: ディレクトリが存在しない

**対処法**:
```bash
# 必要なディレクトリを作成
mkdir -p .kiro/steering
mkdir -p .kiro/tasks
mkdir -p {{spec.location}}

# 再度マージ
git merge {{git.branch_prefix.feature}}XXX-feature-name
```

#### マージ後の確認

```bash
# マージ結果を確認
git status

# ログ確認
git log --oneline -5

# リモートにプッシュ
git push origin {{git.main_branch}}
```

### GitHub Releases登録後の作業

バージョンタグをプッシュした後、以下の手順でGitHub Releasesに登録します：

#### 1. RELEASE_NOTES.mdから情報をコピー

`.kiro/RELEASE_NOTES.md`の「登録待ちリリース」セクションから、該当バージョンの情報をコピーします。

#### 2. GitHub Releasesに登録

1. GitHubのリリースページにアクセス: `https://github.com/{user}/{repo}/releases/new`
2. 以下の情報を入力：
   - **Tag**: `vX.X.X`（既に作成済み）
   - **Title**: `vX.X.X - 機能名`
   - **Description**: RELEASE_NOTES.mdの内容をコピー＆ペースト
3. 「Publish release」をクリック

#### 3. RELEASE_NOTES.mdをアーカイブ

GitHub Releasesに登録完了後、`.kiro/RELEASE_NOTES.md`を更新：

```markdown
## 登録待ちリリース

<!-- Kiroがここに新しいリリース情報を追記します -->

---

## 登録済みリリース（アーカイブ）

### ✅ vX.X.X - 機能名
**作成日**: YYYY-MM-DD  
**登録日**: YYYY-MM-DD  
**GitHub Release**: https://github.com/{user}/{repo}/releases/tag/vX.X.X

---
```

**重要**: 登録日とGitHub ReleaseのURLを必ず記載してください。

## まとめ

- **小さな追加機能**: Specモードで自律的に進める
- **大きな変更**: Vibeモードで仕様を詰めてからSpecモードへ
- **テスト品質**: しっかり維持（{{testing.coverage_target}}%カバレッジ目標）
- **ドキュメント**: Kiroが自動更新
- **バージョン**: Kiroが提案、ユーザーが決定
- **ブランチ**: Spec作成は{{git.main_branch}}、コード実装は開発ブランチ

このワークフローにより、効率的かつ品質の高い開発が可能になります。
