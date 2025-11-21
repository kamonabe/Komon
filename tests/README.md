# Komonテストガイド

このディレクトリには、Komonのテストコードが含まれています。

## テストの実行

### 初回セットアップ

```bash
# 開発用パッケージをインストール
pip install -r requirements-dev.txt
```

### すべてのテストを実行

```bash
pytest
```

### 特定のテストファイルを実行

```bash
pytest tests/test_analyzer.py
```

### カバレッジ付きで実行

```bash
pytest --cov=komon --cov-report=html
```

カバレッジレポートは`htmlcov/index.html`で確認できます。

## テストの構成

### 現在のテスト

- `test_analyzer.py` - 閾値判定とアラート生成のテスト
- `test_log_analyzer.py` - ログ異常検知のテスト

### 今後追加予定

- `test_monitor.py` - リソース監視機能のテスト
- `test_notification.py` - 通知機能のテスト（モック使用）
- `test_history.py` - 履歴管理のテスト
- `test_log_watcher.py` - ログ監視のテスト
- `test_log_trends.py` - ログ傾向分析のテスト

## テストの種類

### ユニットテスト（現在実装済み）

外部依存がない純粋な関数のテスト。

```bash
pytest -m unit
```

### 統合テスト（今後実装予定）

複数のモジュールを組み合わせたテスト。

```bash
pytest -m integration
```

## テストの書き方

### 基本的なテスト

```python
def test_example():
    """テストの説明"""
    # Arrange（準備）
    input_data = {"key": "value"}
    
    # Act（実行）
    result = some_function(input_data)
    
    # Assert（検証）
    assert result == expected_value
```

### フィクスチャの使用

```python
def test_with_fixture(sample_config):
    """フィクスチャを使ったテスト"""
    result = load_thresholds(sample_config)
    assert result["cpu"] == 85
```

共通のフィクスチャは`conftest.py`に定義されています。

## テストのガイドライン

1. **テスト名は明確に**
   - `test_<何をテストするか>_<どういう条件で>_<期待される結果>`
   - 例: `test_analyze_usage_when_above_threshold_returns_alert`

2. **1テスト1検証**
   - 1つのテストで1つのことだけを検証
   - 複数の検証が必要なら、テストを分ける

3. **日本語コメントOK**
   - Komonの特徴として、日本語コメントを推奨

4. **外部依存を避ける**
   - ファイルI/O、ネットワーク通信はモックを使用
   - 純粋な関数から優先的にテスト

## CI/CD（今後実装予定）

GitHub Actionsで自動テストを実行する予定です。

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements-dev.txt
      - run: pytest
```

## トラブルシューティング

### モジュールが見つからない

```bash
# Pythonパスを設定
export PYTHONPATH=src:$PYTHONPATH
pytest
```

または、開発モードでインストール：

```bash
pip install -e .
```

### テストが失敗する

1. 最新のコードを取得: `git pull`
2. 依存パッケージを更新: `pip install -r requirements-dev.txt`
3. キャッシュをクリア: `pytest --cache-clear`

## 参考リンク

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
