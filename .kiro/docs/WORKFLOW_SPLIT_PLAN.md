# development-workflow.md 分割計画

## 現状分析

**ファイルサイズ**: 1,682行（約70KB）
**問題点**:
- テスト戦略の詳細が重複（spec-quality-assurance.mdと重複）
- Git運用の詳細が長大（独立したルールとして分離可能）
- リリース手順が詳細すぎる（独立したルールとして分離可能）

## 分割方針

### 1. コアワークフロー（development-workflow.md）
**残すもの**:
- アイデアから実装までの基本フロー（ステップ1-12）
- 開発モードの使い分け（Spec/Vibe）
- ファイル構成
- ワークフロー例
- まとめ

**削除するもの**:
- テスト戦略の詳細 → `testing-strategy.md`に移動
- Git運用の詳細 → `git-workflow.md`に移動
- リリース手順の詳細 → `release-process.md`に移動

**目標サイズ**: 約600-700行

---

### 2. テスト戦略（testing-strategy.md）【新規作成】
**含めるもの**:
- テスト品質の基準
- テスト戦略の詳細（3層テスト構造）
- プロパティベーステスト
- 統合テスト
- ユニットテスト
- テストデータの管理
- 新機能追加時のテスト作成フロー
- テストカバレッジの目標
- スクリプトファイルのテスト
- Kiroへの指示（テスト作成時）
- トラブルシューティング

**目標サイズ**: 約400-500行

---

### 3. Git運用ルール（git-workflow.md）【新規作成】
**含めるもの**:
- Gitブランチ戦略
- ブランチ命名規則
- Git運用の安全策
  - 前提条件チェック
  - 作業開始前の必須手順
  - マージ前の安全確認（マージテスト）
  - Kiroの役割（AI IDEによる自動化）
- 実装開始前の必須手順（厳格な指示）
- 安全性向上のための追加対策
- マージ時のトラブルシューティング

**目標サイズ**: 約400-500行

---

### 4. リリースプロセス（release-process.md）【新規作成】
**含めるもの**:
- リリース前の最終確認
  - 基本チェックリスト
  - 手動動作確認チェックリスト
  - cronジョブのテスト（該当する場合）
  - リリース判断
- 既存テストの失敗への対応
- GitHub Releases登録後の作業
- PyPI公開（手動作業）

**目標サイズ**: 約200-300行

---

## 分割後の構造

```
.kiro/steering/
├── development-workflow.md       # コアワークフロー（600-700行）
├── testing-strategy.md           # テスト戦略（400-500行）
├── git-workflow.md               # Git運用（400-500行）
└── release-process.md            # リリースプロセス（200-300行）
```

**合計**: 約1,600-2,000行（現在とほぼ同じ）

---

## 相互参照

### development-workflow.md から参照

```markdown
## テスト品質の基準

詳細は `testing-strategy.md` を参照してください。

### 必須テスト
- プロパティベーステスト（該当する場合）
- 統合テスト
- ユニットテスト

### テストカバレッジ
- 目標: 95%以上（90%以上なら許容）
```

```markdown
## Gitブランチ戦略

詳細は `git-workflow.md` を参照してください。

### mainブランチで作業してOK
- ドキュメント整備
- Spec作成

### 開発ブランチを切る必要がある
- コード実装
- テスト追加
```

```markdown
## リリース前の最終確認

詳細は `release-process.md` を参照してください。

### 基本チェックリスト
- 全テストがパス
- カバレッジが目標値以上
- 実際に動作確認
```

---

## rules-metadata.yml の更新

```yaml
testing-strategy:
  priority: high
  applies-to: [implementation, testing]
  triggers: [test-creation, implementation-complete]
  description: テスト戦略と品質基準

git-workflow:
  priority: high
  applies-to: [implementation, git-operations]
  triggers: [implementation-start, merge]
  description: Git運用ルールとブランチ戦略

release-process:
  priority: high
  applies-to: [release]
  triggers: [implementation-complete, release]
  description: リリースプロセスと最終確認
```

---

## 実装手順

### ステップ1: テンプレート作成
1. `testing-strategy.template.md` を作成
2. `git-workflow.template.md` を作成
3. `release-process.template.md` を作成

### ステップ2: development-workflow.template.md を編集
- テスト戦略の詳細を削除（参照に置き換え）
- Git運用の詳細を削除（参照に置き換え）
- リリースプロセスの詳細を削除（参照に置き換え）

### ステップ3: rules-metadata.yml を更新
- 新しいルールを追加

### ステップ4: ルールを再生成
```bash
python scripts/generate_steering_rules.py
```

### ステップ5: 差分確認
```bash
git diff .kiro/steering/*.md
```

### ステップ6: コミット
```bash
git add .kiro/steering/_templates/
git add .kiro/steering/*.md
git add .kiro/steering/rules-metadata.yml
git commit -m "refactor: development-workflowを4つのルールに分割"
```

---

## メリット

### 1. 可読性の向上
- 各ルールが独立して読みやすい
- 目的に応じて必要なルールだけ参照できる

### 2. 保守性の向上
- テスト戦略だけ更新したい場合、testing-strategy.mdだけ編集
- Git運用だけ更新したい場合、git-workflow.mdだけ編集

### 3. 再利用性の向上
- 他のプロジェクトで「テスト戦略だけ」使いたい場合に便利
- 「Git運用だけ」使いたい場合に便利

### 4. Kiroの処理効率
- 必要なルールだけ読み込める
- トリガーに応じて適切なルールを参照

---

## 注意点

### 1. 相互参照の明示
- 各ルールで「詳細は XXX.md を参照」と明記
- ユーザーが迷わないようにする

### 2. 重複の最小化
- 基本的な説明は各ルールに含める
- 詳細な説明は参照先に任せる

### 3. テンプレート変数の一貫性
- 全てのテンプレートで同じ変数を使用
- project-config.ymlとの整合性を保つ

---

## 次のステップ

1. この計画をユーザーに確認
2. 承認されたら実装開始
3. テンプレート作成
4. ルール再生成
5. 差分確認
6. コミット

