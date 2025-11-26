# タスク管理 - 使い方ガイド

## 概要

このディレクトリには、プロジェクト全体の**実装タスク管理**ファイルが格納されています。

Komonプロジェクトでは、2階層のタスク管理を採用しています：
1. **実装タスクリスト**（このディレクトリ）: プロジェクト全体のタスク管理
2. **Spec別タスクリスト**（`.kiro/specs/{feature-name}/tasks.md`）: 個別機能の詳細な実装手順

## ディレクトリ構造

```
.kiro/tasks/
├── README.md                          # このファイル
├── _templates/                        # タスクテンプレート（汎用）
│   └── implementation-tasks.template.md
├── implementation-tasks.md            # 実装タスクリスト（進行中・未着手）
└── completed-tasks.md                 # 完了タスクアーカイブ
```

## タスク管理の流れ

### 1. アイデアからタスクへ

```
.kiro/specs/future-ideas.md
    ↓ 実装を決定
.kiro/tasks/implementation-tasks.md に [TASK-XXX] として追加
    ↓ Spec作成
.kiro/specs/{feature-name}/tasks.md に詳細タスクを記載
    ↓ 実装
両方のタスクファイルを更新
    ↓ 次のバージョンリリース時
completed-tasks.md へアーカイブ
```

## アーカイブルール

- **implementation-tasks.md**: 進行中・未着手のタスク + 直近バージョンの完了タスク
- **completed-tasks.md**: 過去バージョンの完了タスク（バージョン降順）
- 次のバージョンがリリースされたら、前バージョンの完了タスクをアーカイブに移動

**例**: v1.18.0リリース時 → v1.17.0の完了タスクを `completed-tasks.md` に移動

### 2. タスクの追加

`implementation-tasks.md`に新しいタスクを追加します：

```markdown
### [TASK-XXX] タスク名
**元アイデア**: [IDEA-XXX] アイデア名  
**ステータス**: 🔴 TODO  
**優先度**: High/Medium/Low  
**見積もり**: 小/中/大（X-Y時間）

#### 背景
なぜこのタスクが必要か。

#### タスク分解
- [ ] サブタスク1
- [ ] サブタスク2

#### 完了条件
- 条件1
- 条件2

#### 依存関係
- なし
```

### 3. タスクステータス

- 🔴 **TODO**: 未着手
- 🟡 **In Progress**: 実装中
- 🟢 **Done**: 完了
- ⏸️ **On Hold**: 保留中
- ❌ **Cancelled**: キャンセル

### 4. タスク完了時の更新

タスクが完了したら、**必ず両方のファイルを更新**してください：

#### ステップ1: Spec別タスクリストを完了にする
```markdown
# .kiro/specs/{feature-name}/tasks.md
- [x] 1. Create module
- [x] 2. Write tests
- [x] 3. Update docs
```

#### ステップ2: 実装タスクリストを完了にする
```markdown
# .kiro/tasks/implementation-tasks.md
### [TASK-XXX] 機能名
**ステータス**: 🟢 Done
**完了日**: YYYY-MM-DD (vX.X.X)

#### タスク分解
- [x] サブタスク1
- [x] サブタスク2
```

#### ステップ3: 完了条件をチェックマークに変更
```markdown
#### 完了条件
- ✅ 条件1が満たされている
- ✅ 条件2が満たされている
```

## テンプレート化

### 新規プロジェクトでの使用

#### ステップ1: テンプレートとスクリプトをコピー

```bash
# Komonプロジェクトから
cp -r /path/to/komon/.kiro/tasks/_templates /path/to/myproject/.kiro/tasks/
cp /path/to/komon/scripts/generate_task_template.py /path/to/myproject/scripts/
```

#### ステップ2: プロジェクト設定を作成

```bash
cd /path/to/myproject
vim .kiro/steering/project-config.yml
```

#### ステップ3: タスクテンプレートを生成

```bash
python scripts/generate_task_template.py
```

⚠️ **注意**: このコマンドは既存の`implementation-tasks.md`を上書きします！

#### ステップ4: 実際のタスクを追加

生成されたテンプレートに、実際のタスク（TASK-001, TASK-002...）を追加します。

### 既存プロジェクトでの使用

既存プロジェクトでは、テンプレートは参考用として、実際のタスクは手動で管理してください。

テンプレートを更新したい場合：

```bash
# テンプレートを編集
vim .kiro/tasks/_templates/implementation-tasks.template.md

# 新規プロジェクト用に生成（既存ファイルは上書きされる）
python scripts/generate_task_template.py
```

## 優先順位の判断基準

**High Priority**:
- ユーザー体験を大きく改善する
- 実装コストが低〜中程度
- プロジェクトの思想を強化する
- 既存機能との親和性が高い

**Medium Priority**:
- 便利だが必須ではない
- 実装コストが中程度
- 特定のユースケースで有用

**Low Priority**:
- 実装コストが高い
- 効果が不確実
- まずは他の機能を優先すべき

## チェックリスト

タスク完了時は以下を確認：

- [ ] `.kiro/specs/{feature-name}/tasks.md` の全サブタスクが `[x]` になっている
- [ ] `.kiro/tasks/implementation-tasks.md` のステータスが 🟢 Done になっている
- [ ] `.kiro/tasks/implementation-tasks.md` のタスク分解が全て `[x]` になっている
- [ ] `.kiro/tasks/implementation-tasks.md` の完了条件が全て ✅ になっている
- [ ] 完了日とバージョンが記載されている
- [ ] `docs/CHANGELOG.md` に記録されている

## トラブルシューティング

### Q: Spec別タスクは完了しているが、実装タスクリストが未更新

**A**: 実装タスクリストを手動で更新してください。両方が一致している必要があります。

### Q: 新しい機能を追加する場合

**A**: 
1. `.kiro/tasks/implementation-tasks.md` に新しいTASK-XXXを追加
2. `.kiro/specs/{feature-name}/` フォルダを作成
3. `requirements.md`, `design.md`, `tasks.md` を作成
4. 実装開始

### Q: テンプレート生成で既存タスクが消えた

**A**: Git履歴から復元できます：

```bash
# 最新のコミットから復元
git show HEAD:.kiro/tasks/implementation-tasks.md > .kiro/tasks/implementation-tasks.md

# または特定のコミットから復元
git log --oneline -- .kiro/tasks/implementation-tasks.md
git show <commit-hash>:.kiro/tasks/implementation-tasks.md > .kiro/tasks/implementation-tasks.md
```

## まとめ

- **2階層管理**: プロジェクト全体（このディレクトリ）+ 機能別（Spec内）
- **常に同期**: 両方のタスクファイルを更新
- **テンプレート化**: 他のプロジェクトでも使える
- **トレーサビリティ**: アイデア → タスク → Spec → 実装

このアプローチにより、プロジェクトの進捗状況が常に正確に把握できます。
