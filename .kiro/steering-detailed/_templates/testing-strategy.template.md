# {{project.name}}テスト戦略

## 基本方針

{{project.name}}では**しっかりしたテスト**を維持します。

## テスト品質の基準

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

## テストデータの管理

### 一時ファイルの使用

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

### モックの使用

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

## 新機能追加時のテスト作成フロー

Kiroが新機能を実装する際、以下の順序でテストを作成します：

### ステップ1: design.mdの正確性プロパティを確認

```markdown
## 正確性プロパティ

### Property 1: 計算結果の正確性
任意のデータに対して、計算結果は数学的に正しい値でなければならない

**検証対象**: AC-001, AC-002
```

{% if testing.property_testing %}
### ステップ2: プロパティテストを作成

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

### ステップ{% if testing.property_testing %}3{% else %}2{% endif %}: 統合テストを作成

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

### ステップ{% if testing.property_testing %}4{% else %}3{% endif %}: ユニットテストを作成

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

## テストカバレッジの目標

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

## スクリプトファイルのテスト

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

## Kiroへの指示

### テスト作成時のチェックリスト

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

### テスト実行の順序

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

## トラブルシューティング

{% if testing.property_testing %}
### Q: プロパティテストと統合テストの境界が曖昧

**A**: 以下の基準で判断してください：
- ファイルI/Oがある → 統合テスト
- 複数モジュールを使う → 統合テスト
- 純粋な計算ロジック → プロパティテスト
{% endif %}

### Q: モックを使うべきか実ファイルを使うべきか迷う

**A**:
- 外部API（Slack, Email） → モック
- ファイルI/O → 実ファイル（`tmp_path`）
- 内部モジュール → モックしない

### Q: テストが遅い

**A**: 以下を確認してください：
{% if testing.property_testing %}
- プロパティテストの`max_examples`を減らす（デフォルト100）
{% endif %}
- 統合テストで不要なファイル作成を減らす
{% if project.language == "python" %}
- `pytest -n auto`で並列実行
{% endif %}

## まとめ

- **3層テスト構造**: プロパティ/統合/ユニット
- **カバレッジ目標**: {{testing.coverage_target}}%以上
- **モック**: 外部APIのみ
- **ファイルI/O**: `tmp_path`を使用
- **スクリプト**: インポートテストを追加
