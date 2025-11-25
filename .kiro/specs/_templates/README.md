# Komonプロジェクト Specテンプレート

このディレクトリには、Komonプロジェクトで新しい機能のSpecを作成する際のテンプレートが含まれています。

## テンプレートファイル

- `requirements.md`: 要件定義書のテンプレート
- `design.md`: 設計書のテンプレート
- `tasks.md`: 実装タスクのテンプレート

## 使い方

### 1. 新しい機能のSpecを作成

```bash
# 機能名のディレクトリを作成（ケバブケース）
mkdir -p .kiro/specs/your-feature-name

# テンプレートをコピー
cp .kiro/specs/_templates/requirements.md .kiro/specs/your-feature-name/
cp .kiro/specs/_templates/design.md .kiro/specs/your-feature-name/
cp .kiro/specs/_templates/tasks.md .kiro/specs/your-feature-name/
```

### 2. テンプレートを編集

各ファイルを開いて、以下のプレースホルダーを置換：

- `[機能名]` → 実際の機能名（例: 通知履歴機能）
- `[feature-name]` → ケバブケース（例: notification-history）
- `YYYY-MM-DD` → 実際の日付
- その他の `[...]` で囲まれた部分

### 3. 内容を記入

各テンプレートの「テンプレート使用ガイド」セクションを参照して、必要な情報を記入してください。

### 4. 検証

Specを作成したら、以下のコマンドで検証できます：

```bash
# 構造検証
python scripts/validate_specs.py

# 一貫性チェック
python scripts/check_spec_consistency.py
```

## テンプレートの品質基準

### requirements.md
- [ ] Front Matterが全て記入されている
- [ ] 概要が2-3文で簡潔に書かれている
- [ ] 用語集に最低3つの用語が定義されている
- [ ] 受入基準が最低3つ定義されている
- [ ] 各受入基準にユーザーストーリーがある
- [ ] 受入条件がWHEN-THEN形式で書かれている

### design.md
- [ ] Front Matterが全て記入されている
- [ ] アーキテクチャ図が含まれている
- [ ] 最低2つのコンポーネントが定義されている
- [ ] 各コンポーネントに関数シグネチャがある
- [ ] データモデルがJSON形式で定義されている
- [ ] 正確性プロパティが最低3つ定義されている
- [ ] 各プロパティに検証対象の要件が明記されている
- [ ] テスト戦略が3種類（ユニット、プロパティ、統合）含まれている

### tasks.md
- [ ] Front Matterが全て記入されている
- [ ] タスクが実装順に並んでいる
- [ ] 各タスクに要件（AC-XXX）が明記されている
- [ ] プロパティテストタスクが含まれている
- [ ] ユニットテストタスクが含まれている
- [ ] チェックポイントタスクが含まれている
- [ ] ドキュメント更新タスクが最後にある

## CI/CD統合

GitHub Actionsで自動検証が実行されます：

- **トリガー**: `.kiro/specs/**/*.md` の変更時
- **検証内容**:
  1. Spec構造の検証（`validate_specs.py`）
  2. Spec間の一貫性チェック（`check_spec_consistency.py`）

## 参考例

良いSpecの例として、以下を参照してください：

- `.kiro/specs/notification-history/`
  - 完全な要件定義、設計書、タスクリストの例
  - プロパティベーステストの記述例
  - 要件とタスクのトレーサビリティの例

## よくある質問

### Q: テンプレートを変更したい場合は？

A: このディレクトリのテンプレートを直接編集してください。変更は次回作成するSpecから反映されます。

### Q: 既存のSpecをテンプレートに合わせたい場合は？

A: `validate_specs.py` を実行してエラーや警告を確認し、段階的に修正してください。

### Q: 検証スクリプトをカスタマイズしたい場合は？

A: `scripts/validate_specs.py` と `scripts/check_spec_consistency.py` を編集してください。

## 関連ドキュメント

- `.kiro/steering/task-management.md`: タスク管理ルール
- `.kiro/steering/development-workflow.md`: 開発ワークフロー
- `docs/PROJECT_STRUCTURE.md`: プロジェクト構造
