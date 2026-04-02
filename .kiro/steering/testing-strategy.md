---
inclusion: auto
name: testing-strategy
description: テスト、カバレッジ、プロパティテスト、pytest、テスト作成時のテスト戦略
---

# テスト戦略

## 基本方針

3層テスト構造で品質を保証する。カバレッジ目標は `project-config.yml` の `testing` セクションを参照。

## 3層テスト構造

### 1. プロパティベーステスト

目的: 仕様の正確性を数学的に検証
ファイル命名: `test_{module}_properties.py`
対象: 計算結果の正確性、不変条件、境界値の挙動、冪等性

```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(min_value=0.0, max_value=100.0), min_size=2))
def test_property_calculation_accuracy(data):
    """検証要件: AC-001"""
    result = calculate_average(data)
    expected = sum(data) / len(data)
    assert abs(result - expected) < 0.0001
```

### 2. 統合テスト

目的: 複数モジュールの連携を検証
ファイル命名: `test_{module}_integration.py`
対象: モジュール間データフロー、ファイルI/O（`tmp_path`使用）、CLIコマンド実行結果

### 3. ユニットテスト

目的: 個別関数のロジックを検証
ファイル命名: `test_{module}_unit.py` または `test_{module}.py`
対象: 正常系、異常系、エッジケース、エラーメッセージ

## モックの使い分け

| 対象 | 方針 |
|------|------|
| 外部API（Slack, Email, HTTP） | モック必須 |
| 時刻依存の処理 | モック（freezegun等） |
| ランダム値 | モック（再現性のため） |
| 環境変数 | テストごとに独立させる |
| ファイルI/O | 実ファイル（`tmp_path`使用） |
| 内部モジュール | モックしない |

## テスト作成フロー（新機能追加時）

1. `design.yml` の正確性プロパティを確認
2. プロパティテストを作成（正確性プロパティ → テストコード）
3. 統合テストを作成（エンドツーエンド動作確認）
4. ユニットテストを作成（エッジケース）
5. 全テストに `検証要件: AC-XXX` を記載

## スクリプトファイルのインポートテスト

`scripts/` 配下の実行スクリプトには最低限のインポートテストを追加する。
目的: 実行時まで発覚しないImportErrorを防ぐ。

```python
def test_main_script_imports(self):
    import main
    assert hasattr(main, 'main')
```

## テスト実行順序

```bash
# 1. ユニットテスト（高速）
python -m pytest tests/test_{module}_unit.py -v
# 2. プロパティテスト（中速）
python -m pytest tests/test_{module}_properties.py -v
# 3. 統合テスト（低速）
python -m pytest tests/test_{module}_integration.py -v
# 4. 全テスト + カバレッジ
bash run_coverage.sh
```
