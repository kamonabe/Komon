# Specファイル形式の問題

## 発生日時
2025-11-30

## 問題の概要

TASK-007「ログ急増時の末尾抜粋表示」のSpec作成時に、
`.md`形式でファイルを作成したが、検証スクリプトは`.yml`形式を期待していた。

## 発生した状況

1. Kiroが`requirements.md`, `design.md`, `tasks.md`を作成
2. `python3 scripts/validate_specs.py`を実行
3. 以下の警告が表示された：
   ```
   ⚠️  警告: 3件
     • log-tail-excerpt/requirements.yml が存在しません
     • log-tail-excerpt/design.yml が存在しません
     • log-tail-excerpt/tasks.yml が存在しません
   ```
4. 手動で`.md`を`.yml`にリネーム

## 根本原因

### 1. ステアリングルールの記述

`.kiro/steering/development-workflow.md`には以下の記述がある：

```markdown
### 3. Spec作成（mainブランチ）
**フォルダ**: `.kiro/specs/{feature-name}/`

以下の3ファイルを**YML形式で**作成：
- `requirements.yml`: 要件定義（構造化YAML）
- `design.yml`: 設計書（正確性プロパティを含む、構造化YAML）
- `tasks.yml`: 実装タスクリスト（構造化YAML）

**テンプレート**: `.kiro/specs/_templates/` を参照

**この時点ではまだmainブランチでOK**
```

**明確に「YML形式で」と書かれている。**

### 2. Kiroの判断ミス

- ステアリングルールを読んだはずだが、`.md`形式で作成してしまった
- Markdown形式の方が書きやすいと判断した可能性
- 既存のSpecファイルを参照せずに作成した

### 3. 既存Specファイルの確認不足

既存のSpecファイル（例: `disk-trend-prediction/`）を確認すれば、
`.yml`形式であることが分かったはず。

```bash
$ ls .kiro/specs/disk-trend-prediction/
design.yml  requirements.yml  tasks.yml
```

## 影響

- 軽微：手動リネームで対応可能
- 時間ロス：約1分
- 検証スクリプトの実行が1回余分に必要

## 改善案

### 案1: Kiroの動作改善（AI側）

**Spec作成前に既存Specを参照する**

```
1. Spec作成を開始
   ↓
2. 既存Specディレクトリを確認
   ls .kiro/specs/disk-trend-prediction/
   ↓
3. ファイル形式を確認（.yml）
   ↓
4. 同じ形式で作成
```

**メリット**:
- 既存の慣習に自動的に従う
- ステアリングルールの読み間違いを防ぐ

**デメリット**:
- 既存Specがない場合は判断できない

### 案2: ステアリングルールの強調（ルール側）

**より明確な記述に変更**

```markdown
### 3. Spec作成（mainブランチ）

⚠️ **重要**: ファイル形式は必ず`.yml`です。`.md`ではありません。

以下の3ファイルを作成：
- `requirements.yml` ← YAMLファイル
- `design.yml` ← YAMLファイル
- `tasks.yml` ← YAMLファイル
```

**メリット**:
- 誤解の余地がない
- 視覚的に目立つ

**デメリット**:
- ルールが冗長になる

### 案3: テンプレートの活用（プロセス側）

**テンプレートファイルを用意**

```bash
.kiro/specs/_templates/
├── requirements.template.yml
├── design.template.yml
└── tasks.template.yml
```

**Kiroの動作**:
```
1. テンプレートをコピー
   cp .kiro/specs/_templates/requirements.template.yml \
      .kiro/specs/log-tail-excerpt/requirements.yml

2. テンプレートの内容を埋める
```

**メリット**:
- ファイル形式を間違えない
- 構造が統一される
- Front Matterも自動的に含まれる

**デメリット**:
- テンプレートの保守が必要

### 案4: 検証スクリプトの柔軟化（ツール側）

**`.md`と`.yml`の両方を許容**

```python
# scripts/validate_specs.py
def find_spec_file(spec_dir, base_name):
    """requirements, design, tasksファイルを探す"""
    for ext in ['.yml', '.yaml', '.md']:
        path = spec_dir / f"{base_name}{ext}"
        if path.exists():
            return path
    return None
```

**メリット**:
- 柔軟性が高い
- 既存Specとの互換性

**デメリット**:
- 形式が統一されない
- YAMLパーサーでMarkdownを読めない

## 推奨する改善策

**優先度1: 案3（テンプレートの活用）**
- 最も確実
- 構造の統一にも貢献
- Front Matterの自動化

**優先度2: 案1（既存Specの参照）**
- Kiroの動作改善
- 自動的に慣習に従う

**優先度3: 案2（ルールの強調）**
- 補助的な対策
- 視覚的に分かりやすく

## 実装タイミング

- **今すぐ**: 案2（ルールの強調）← 簡単
- **次のSpec作成時**: 案1（既存Specの参照）← Kiroの学習
- **時間があるとき**: 案3（テンプレート作成）← 最も効果的

## 関連ファイル

- `.kiro/steering/development-workflow.md`: ステアリングルール
- `scripts/validate_specs.py`: 検証スクリプト
- `.kiro/specs/_templates/`: テンプレートディレクトリ（未作成）

## 記録者

Kiro（AI）

## ユーザーコメント

> 一旦待って今のmdをymlに変える処理はそもそもymlで作っていれば問題ない部分だと思うんだよね
> 開発は一旦このまま進めるけど、別途開発プロセスを見直すシーンで材料としたいから、
> どこかにこの問題を新規ファイルで残しておいてもらっていい？

→ この記録ファイルを作成しました。
