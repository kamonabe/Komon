# Komon仕様駆動開発ワークフロー

## 開発の基本方針

Komonプロジェクトは**仕様駆動開発（Spec-Driven Development）**を採用しています。

## アイデアから実装までの流れ

### 1. アイデア段階
**ファイル**: `.kiro/specs/future-ideas.md`

- 新機能のアイデアはまず`future-ideas.md`に追加
- アイデアの検討・熟成期間を設ける
- 実装に値するかどうかを判断

### 2. 実装決定
**ファイル**: `.kiro/tasks/implementation-tasks.md`

- 実装を決定したアイデアを`TASK-XXX`として追加
- 優先度、見積もり、背景を記載
- タスク分解を行う

### 3. Spec作成（mainブランチ）
**フォルダ**: `.kiro/specs/{feature-name}/`

以下の3ファイルを**日本語で**作成：
- `requirements.md`: 要件定義- `design.md`: 設計書（正確性プロパティを含む）- `tasks.md`: 実装タスクリスト
**この時点ではまだmainブランチでOK**

### 4. 🚨 実装開始前の必須チェック 🚨

**Kiroは実装を開始する前に、必ず以下を実行します：**

1. **現在のブランチを確認**
   ```bash
   git branch
   ```

2. **mainブランチにいる場合は停止**
   - ユーザーに「開発ブランチを作成してください」と依頼
   - ブランチ名を提案: `feature/task-XXX-{feature-name}`
   - ユーザーがブランチを作成するまで**実装を開始しない**

3. **開発ブランチにいることを確認してから実装開始**

**ブランチ作成コマンド（ユーザーが実行）**:
```bash
git checkout main
git checkout -b feature/task-XXX-{feature-name}
```

**ブランチ命名規則**:
- `feature/task-001-progressive-notification`
- `feature/task-003-contextual-advice`
- `bugfix/fix-memory-leak` (バグ修正の場合)

### 5. 実装フェーズ（Kiroが連続で進める）

Kiroは以下を**連続して自律的に**実行します：

1. コード実装
2. テスト作成（プロパティテスト + 統合テスト + ユニットテスト）3. ドキュメント更新（README.md, CHANGELOG.md）
4. タスクファイルの更新

**ユーザーの介入は不要**です。実装完了後に報告します。

### 6. 完了報告とマージ

Kiroが以下を報告：
- 実装内容のサマリー
- テスト結果（全テストパス確認）
- 提案するバージョン番号（例: v1.12.0）

**ユーザーが最終確認**して：
1. バージョン番号を決定
2. mainブランチにマージ
3. バージョンタグを作成

```bash
git checkout main
git merge feature/task-XXX-{feature-name}
git tag v1.X.X
git push origin main --tags
```

### 7. GitHub Releases用の情報を準備

**重要**: バージョンタグを作成した後、GitHub Releases登録用の情報を`.kiro/RELEASE_NOTES.md`に追記します。

Kiroが以下を自動的に追記：
- **Release Title**: `v1.X.X - 機能名`
- **Release Notes**: CHANGELOG.mdから該当バージョンの内容を抽出

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

- requirements.md, design.md, tasks.md の作成（日本語で）
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

Komonでは**しっかりしたテスト**を維持します：

### 必須テスト
1. **プロパティベーステスト**（hypothesis使用）
   - 正確性プロパティを検証
   - 不変条件のテスト
   
2. **統合テスト**
   - 既存機能との統合確認
   - エンドツーエンドの動作確認
   
3. **ユニットテスト**
   - 個別関数の動作確認
   - エッジケースのテスト

### テストカバレッジ
- 目標: 95%以上を維持
- 全テストがパスすることを確認

## テスト戦略の詳細

Komonでは、**3層テスト構造**を採用し、異なる観点から品質を保証します。

### テストの3層構造

#### 1. プロパティベーステスト（Property-Based Testing）
**目的**: 仕様の正確性を数学的に検証する

**対象**:
- 不変条件（Invariants）
- 数学的な性質（例: 線形回帰の正確性、平均値計算）
- 境界値の挙動

**ファイル命名**: `test_{module}_properties.py`

**例（Komonの場合）**:
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

**書くべきプロパティ**:
- ✅ 計算結果の正確性（例: 平均値、傾き、閾値判定）
- ✅ 不変条件（例: ソート後も要素数は同じ、閾値の順序性）
- ✅ 境界値の挙動（例: 0%, 100%, 閾値ちょうど）
- ✅ 冪等性（例: 同じ入力で同じ出力）

**書かなくて良いもの**:
- ❌ ファイルI/O
- ❌ 外部API呼び出し
- ❌ 複数モジュールの連携

#### 2. 統合テスト（Integration Testing）

**目的**: 複数モジュールの連携を検証する

**対象**:
- モジュール間のデータフロー
- ファイルI/O（実ファイル使用）
- エンドツーエンドの動作
- CLIコマンドの実行結果

**ファイル命名**: `test_{module}_integration.py`

**例（Komonの場合）**:
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

**書くべきテスト**:
- ✅ CLIコマンドの実行結果
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

**例（Komonの場合）**:
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

**ルール**:
- ✅ `tmp_path`を使う（自動クリーンアップ）
- ❌ 実際のプロジェクトディレクトリにファイルを作らない
- ❌ テスト後に手動でファイルを削除しない

#### モックの使用

外部依存をモックする場合、`unittest.mock`または`pytest-mock`を使用します。

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

#### ステップ2: プロパティテストを作成

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

#### ステップ3: 統合テストを作成

```python
# tests/test_{module}_integration.py

def test_end_to_end_with_data(tmp_path, capsys):
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

#### ステップ4: ユニットテストを作成

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

### テストカバレッジの目標

- **全体**: 95%以上
- **新規モジュール**: 90%以上（初回実装時）
- **既存モジュール**: 現状維持または向上

**カバレッジ確認**:
```bash
bash run_coverage.sh
# htmlcov/index.html で確認
```

### スクリプトファイルのテスト

`scripts/`配下の実行スクリプトも、最低限のインポートテストを追加します。

**目的**: 実行時まで発覚しないImportErrorを防ぐ

**対象**:
- `scripts/main.py` - メイン監視スクリプト
- `scripts/advise.py` - アドバイス表示
- `scripts/status.py` - ステータス表示
- その他の実行スクリプト

**テスト内容**:
- ✅ インポートが成功すること
- ✅ 主要な関数が存在すること
- ✅ 依存モジュールが正しくインポートされること

**ファイル命名**: `test_scripts_import.py`

**例**:
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

- [ ] design.mdの正確性プロパティを全てプロパティテストで検証した
- [ ] CLIコマンドや複数モジュールの連携を統合テストで検証した
- [ ] エッジケースをユニットテストで検証した
- [ ] 全テストに`**検証要件: AC-XXX**`を記載した
- [ ] モックは外部APIのみに使用した
- [ ] ファイルI/Oは`tmp_path`を使用した
- [ ] スクリプトファイルのインポートテストを追加した（新規スクリプト追加時）
- [ ] カバレッジが95%以上を維持している

#### テスト実行の順序

実装完了後、Kiroは以下の順序でテストを実行します：

1. **ユニットテスト**（高速）
   ```bash
   python -m pytest tests/test_{module}_unit.py -v
   ```

2. **プロパティテスト**（中速）
   ```bash
   python -m pytest tests/test_{module}_properties.py -v
   ```

3. **統合テスト**（低速）
   ```bash
   python -m pytest tests/test_{module}_integration.py -v
   ```

4. **全テスト + カバレッジ**
   ```bash
   bash run_coverage.sh
   ```

### トラブルシューティング

#### Q: プロパティテストと統合テストの境界が曖昧

**A**: 以下の基準で判断してください：
- ファイルI/Oがある → 統合テスト
- 複数モジュールを使う → 統合テスト
- 純粋な計算ロジック → プロパティテスト

#### Q: モックを使うべきか実ファイルを使うべきか迷う

**A**:
- 外部API（Slack, Email） → モック
- ファイルI/O → 実ファイル（`tmp_path`）
- 内部モジュール → モックしない

#### Q: テストが遅い

**A**: 以下を確認してください：
- プロパティテストの`max_examples`を減らす（デフォルト100）
- 統合テストで不要なファイル作成を減らす
- `pytest -n auto`で並列実行

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
1. future-ideas.md に [IDEA-001] として記載（mainブランチ）
   ↓
2. 実装を決定 → implementation-tasks.md に [TASK-001] 追加（mainブランチ）
   ↓
3. .kiro/specs/progressive-notification/ を作成（mainブランチ）
   - requirements.md: 要件定義
   - design.md: 設計書
   - tasks.md: タスクリスト
   ↓
4. ユーザー「TASK-001の実装を開始しよう」
   ↓
5. Kiro「Specモードで進めます。まず現在のブランチを確認します」
   git branch  # → mainブランチにいることを確認
   ↓
6. Kiro「開発ブランチを作成してください：
         git checkout -b feature/task-001-progressive-notification」
   ↓
7. ユーザーがブランチを作成
   git checkout -b feature/task-001-progressive-notification
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
12. mainにマージしてタグ作成
    git checkout main
    git merge feature/task-001-progressive-notification
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

### mainブランチで作業してOK

以下の作業は**mainブランチで直接**行います：

- ドキュメント整備（README, CHANGELOG等）
- future-ideas.mdへのアイデア追加
- implementation-tasks.mdへのタスク追加
- Spec作成（requirements.md, design.md, tasks.md）
- ステアリングルールの追加・更新

### 開発ブランチを切る必要がある

以下の作業は**必ず開発ブランチ**を作成してから行います：

- **コード実装**（src/配下の変更）
- **テスト追加**（tests/配下の変更）
- **設定ファイル変更**（settings.yml, setup.py等）
- **依存パッケージ変更**（requirements.txt等）

### ブランチ命名規則

```
feature/task-XXX-{feature-name}     # 新機能
bugfix/{issue-description}     # バグ修正
refactor/{module-name}         # リファクタリング

例:
- feature/task-001-progressive-notification
- feature/task-003-contextual-advice
- bugfix/fix-memory-leak
- refactor/analyzer-module
```

### 🚨 Kiroへの厳格な指示 🚨

#### 実装開始前の必須手順（絶対に守る）

**TASK-XXXの実装を開始する際、Kiroは以下を必ず実行：**

1. **「Specモードで進めます」と宣言**
2. **現在のブランチを確認**
   ```bash
   git branch
   ```
3. **mainブランチにいる場合**:
   - ❌ **絶対にコード実装を開始しない**
   - ✅ ユーザーに以下を依頼:
     ```
     実装を開始する前に、開発ブランチを作成してください：
     
     git checkout -b feature/task-XXX-{feature-name}
     
     ブランチ作成後、実装を開始します。
     ```
   - ⏸️ ユーザーの返答を待つ

4. **開発ブランチにいることを確認してから実装開始**

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
4. ユーザーにmainへのマージを依頼
5. バージョンタグ作成後、GitHub Releases用の情報を`.kiro/RELEASE_NOTES.md`に追記

#### チェックリスト（実装開始前）

- [ ] `git branch` でブランチを確認した
- [ ] mainブランチの場合、ユーザーにブランチ作成を依頼した
- [ ] 開発ブランチにいることを確認した
- [ ] 上記が全て完了してから実装を開始した

#### チェックリスト（実装完了後）

- [ ] テストが全てパスした
- [ ] カバレッジを確認した（`bash run_coverage.sh`）
- [ ] カバレッジが変わっている場合、README.mdのバッジを更新した
- [ ] バージョン番号を提案した
- [ ] GitHub Releases用の情報を`.kiro/RELEASE_NOTES.md`に追記した

## まとめ

- **小さな追加機能**: Specモードで自律的に進める
- **大きな変更**: Vibeモードで仕様を詰めてからSpecモードへ
- **テスト品質**: しっかり維持（95%カバレッジ目標）
- **ドキュメント**: Kiroが自動更新
- **バージョン**: Kiroが提案、ユーザーが決定
- **ブランチ**: Spec作成はmain、コード実装は開発ブランチ

このワークフローにより、効率的かつ品質の高い開発が可能になります。