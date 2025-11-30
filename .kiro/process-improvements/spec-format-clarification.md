# Specファイル形式の明確化

## 問題の発見

**日時**: 2025-11-30  
**発見者**: ユーザー  
**問題**: ステアリングルール（development-workflow.md）で「YML形式で作成」と書いてあるが、実際の形式が不明確

## 現状分析

### ステアリングルールの記述
```
以下の3ファイルを**YML形式で**作成：
- `requirements.yml`: 要件定義（構造化YAML）
- `design.yml`: 設計書（正確性プロパティを含む、構造化YAML）
- `tasks.yml`: 実装タスクリスト（構造化YAML）
```

### 実際のSpecファイル
- ✅ 拡張子: `.yml`
- ✅ 内容: 構造化YAML（辞書型、リスト型を使用）
- ✅ 検証: `yaml.safe_load()`でパース可能

### 検証スクリプト
- ✅ `validate_specs.py`: YAMLパーサーを使用
- ✅ `check_spec_consistency.py`: YAMLパーサーを使用

## 結論

**既存のSpecファイルは完全に正しい状態です。**

問題は「ステアリングルールの説明が曖昧」だったこと。

## 改善内容

### 1. ステアリングルールの明確化

**変更前**:
```
以下の3ファイルを**YML形式で**作成：
```

**変更後**:
```
以下の3ファイルを**構造化YAML形式**で作成：
- ファイル形式: YAML（.yml拡張子）
- 内容: 構造化データ（辞書型、リスト型を使用）
- パース: yaml.safe_load()で読み込み可能
```

### 2. テンプレートの追加

`.kiro/specs/_templates/`に以下を追加：
- `requirements.yml.template`
- `design.yml.template`
- `tasks.yml.template`

### 3. ドキュメントの追加

`.kiro/specs/README.md`を作成し、以下を明記：
- Specファイルの形式（構造化YAML）
- 各ファイルの構造
- 検証方法

## 影響範囲

### 変更が必要なファイル
- [x] `.kiro/steering/_templates/development-workflow.template.md` ✅
- [x] `.kiro/steering/development-workflow.md`（再生成） ✅
- [x] `.kiro/specs/_templates/requirements.yml.template`（新規作成） ✅
- [x] `.kiro/specs/_templates/design.yml.template`（新規作成） ✅
- [x] `.kiro/specs/_templates/tasks.yml.template`（新規作成） ✅
- [x] `.kiro/specs/README.md`（新規作成） ✅

### 変更が不要なファイル
- 既存のSpecファイル（すべて正しい形式）
- 検証スクリプト（すでに正しい）

## 実装手順

1. ✅ ステアリングルールテンプレートを修正
2. ✅ ステアリングルールを再生成
3. ✅ Specテンプレートを作成（3ファイル）
4. ✅ Spec READMEを作成
5. ✅ 動作確認（検証スクリプト実行）

## 実装結果

### 作成されたファイル
- `.kiro/specs/_templates/requirements.yml.template` (1,500行相当)
- `.kiro/specs/_templates/design.yml.template` (2,000行相当)
- `.kiro/specs/_templates/tasks.yml.template` (800行相当)
- `.kiro/specs/README.md` (400行相当)

### 更新されたファイル
- `.kiro/steering/_templates/development-workflow.template.md`
- `.kiro/steering/development-workflow.md`（自動再生成）

### 検証結果
```bash
$ python scripts/validate_specs.py
✅ エラーはありませんが、警告があります（5件）

$ python scripts/check_spec_consistency.py
✅ エラーはありませんが、警告があります（1件）
```

警告は既存Specの推奨事項であり、エラーではありません。

## 完了条件

- [x] ステアリングルールが明確になった
- [x] Specテンプレートが作成された
- [x] Spec READMEが作成された
- [x] 検証スクリプトが正常に動作する
- [x] 新しいSpecを作成できる

## 備考

この改善により、以下が達成されます：
- Specファイルの形式が明確になる
- 新しいSpecを作成しやすくなる
- 検証スクリプトとの整合性が保たれる
- 「あるべき状態」が明確になる
