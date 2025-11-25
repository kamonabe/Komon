# Komon CI/CD ワークフロー

このディレクトリには、KomonプロジェクトのGitHub Actionsワークフローが含まれています。

## ワークフロー一覧

### 1. tests.yml - メインテストスイート

**トリガー**:
- `main`ブランチへのpush
- `feature/**`, `bugfix/**`ブランチへのpush
- `main`ブランチへのPull Request

**実行内容**:
- **test**: Python 3.10, 3.11, 3.12でのユニットテスト、プロパティテスト
- **validate-specs**: Spec構造と一貫性の検証
- **lint**: コードフォーマットとリンティング（black, isort, flake8）

**目的**: コード変更時に品質を保証し、リグレッションを防ぐ

### 2. spec-validation.yml - Specとドキュメント検証

**トリガー**:
- `.kiro/specs/**/*.md`の変更時
- `docs/**/*.md`の変更時
- `README.md`の変更時

**実行内容**:
- **validate-specs**: Spec構造と一貫性の検証
- **validate-docs**: ドキュメントのリンク切れチェック、必須ドキュメントの存在確認

**目的**: ドキュメント更新時に品質を保証し、Specとコードの乖離を防ぐ

## CI戦略

### こまめなテスト実行

Komonでは、以下のタイミングで自動テストを実行します：

1. **コード変更時** (`tests.yml`)
   - 全てのテストを実行
   - カバレッジチェック（目標95%）
   - リンティング

2. **Spec更新時** (`spec-validation.yml`)
   - Spec構造検証
   - Spec間の一貫性チェック

3. **ドキュメント更新時** (`spec-validation.yml`)
   - リンク切れチェック
   - 必須ドキュメントの存在確認

### なぜこまめにテストするのか？

1. **コードとSpecの乖離を防ぐ**
   - コード変更時にもSpec検証を実行
   - 実装とドキュメントの不一致を早期発見

2. **リグレッション防止**
   - 既存機能を壊していないか常に確認
   - PRごとにテストが走るので安心

3. **品質の継続的な保証**
   - 小さな変更でも品質を維持
   - 問題を早期に発見・修正

## ローカルでの実行

CI実行前にローカルで確認できます：

```bash
# 全テスト実行
python -m pytest tests/ -v

# カバレッジ確認
bash run_coverage.sh

# Spec検証
python scripts/validate_specs.py
python scripts/check_spec_consistency.py

# コードフォーマット
black src/ tests/ scripts/
isort src/ tests/ scripts/
flake8 src/ tests/ scripts/ --max-line-length=120
```

## CI失敗時の対応

### テスト失敗

1. ローカルでテストを実行して再現
2. 失敗したテストを修正
3. 全テストがパスすることを確認してpush

### Spec検証失敗

1. `python scripts/validate_specs.py`を実行してエラー確認
2. エラーメッセージに従ってSpecを修正
3. 再度検証してpush

### リンティング失敗

1. `black src/ tests/ scripts/`でフォーマット
2. `isort src/ tests/ scripts/`でimport整理
3. `flake8`の警告を確認して修正

## カスタマイズ

ワークフローをカスタマイズする場合は、以下を編集：

- `tests.yml`: テスト実行の設定
- `spec-validation.yml`: Spec/ドキュメント検証の設定

変更後は、`.github/workflows/`配下のファイルをcommitしてください。
