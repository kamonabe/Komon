# Komonプロジェクトのタスク管理ルール

## タスクファイルの構造

Komonプロジェクトでは、2階層のタスク管理を採用しています：

### 1. 実装タスクリスト（マスター）
**ファイル**: `.kiro/tasks/implementation-tasks.md`

- **役割**: プロジェクト全体のタスク管理（進行中・未着手 + 直近バージョンの完了タスク）
- **粒度**: 機能単位（TASK-001, TASK-002...）
- **ステータス**: 🔴 TODO / 🟡 In Progress / 🟢 Done / ⏸️ On Hold / ❌ Cancelled
- **更新タイミング**: タスク開始時、完了時

### 1-2. 完了タスクアーカイブ
**ファイル**: `.kiro/tasks/completed-tasks.md`

- **役割**: 過去バージョンの完了タスクを保存
- **整理**: バージョン降順（新しいものが上）
- **移動タイミング**: 次のバージョンリリース時

### 2. Spec別タスクリスト（詳細）
**ファイル**: `.kiro/specs/{feature-name}/tasks.md`

- **役割**: 個別機能の詳細な実装手順
- **粒度**: サブタスク単位（実装、テスト、ドキュメント）
- **ステータス**: `[ ]` / `[x]`
- **更新タイミング**: 各サブタスク完了時

## 🚨 重要：タスク完了時の更新ルール

タスクが完了したら、**必ず両方のファイルを更新**してください：

### ステップ1: Spec別タスクリストを完了にする
```markdown
# .kiro/specs/{feature-name}/tasks.md
- [x] 1. Create module
- [x] 2. Write tests
- [x] 3. Update docs
```

### ステップ2: 実装タスクリストを完了にする
```markdown
# .kiro/tasks/implementation-tasks.md
### [TASK-XXX] 機能名
**ステータス**: 🟢 Done
**完了日**: YYYY-MM-DD (vX.X.X)

#### タスク分解
- [x] サブタスク1
- [x] サブタスク2
```

### ステップ3: 完了条件をチェックマークに変更
```markdown
#### 完了条件
- ✅ 条件1が満たされている
- ✅ 条件2が満たされている
```

## チェックリスト

タスク完了時は以下を確認：

- [ ] `.kiro/specs/{feature-name}/tasks.md` の全サブタスクが `[x]` になっている
- [ ] `.kiro/tasks/implementation-tasks.md` のステータスが 🟢 Done になっている
- [ ] `.kiro/tasks/implementation-tasks.md` のタスク分解が全て `[x]` になっている
- [ ] `.kiro/tasks/implementation-tasks.md` の完了条件が全て ✅ になっている
- [ ] 完了日とバージョンが記載されている
- [ ] `docs/CHANGELOG.md` に記録されている

## Kiro AIへの指示

タスク完了を報告する際は、以下を確認してください：

1. **Spec別タスクリスト**（`.kiro/specs/{feature-name}/tasks.md`）が全て `[x]` になっているか
2. **実装タスクリスト**（`.kiro/tasks/implementation-tasks.md`）のステータスが 🟢 Done になっているか
3. 両方が一致していない場合は、ユーザーに確認して両方を更新する

## 例：正しい完了状態

### Spec別タスクリスト
```markdown
# .kiro/specs/notification-history/tasks.md
- [x] 1. Create notification history module
- [x] 2. Implement formatting
- [x] 3. Integrate with notification system
- [x] 4. Extend advise command
- [x] 5. Ensure all tests pass
- [x] 6. Update documentation
```

### 実装タスクリスト
```markdown
# .kiro/tasks/implementation-tasks.md
### [TASK-002] ローカル通知履歴の保存と表示
**ステータス**: 🟢 Done
**完了日**: 2025-11-22 (v1.11.0)

#### タスク分解
- [x] 通知記録ファイルの設計
- [x] 保存処理の追加
- [x] 表示処理の統合
- [x] テストケースの追加
- [x] ドキュメント更新

#### 完了条件
- ✅ 通知が自動的に保存される
- ✅ `komon advise` で履歴が表示される
- ✅ 最大100件の制限が機能する
```

## トラブルシューティング

### Q: Spec別タスクは完了しているが、実装タスクリストが未更新
**A**: 実装タスクリストを手動で更新してください。両方が一致している必要があります。

### Q: 新しい機能を追加する場合
**A**: 
1. `.kiro/tasks/implementation-tasks.md` に新しいTASK-XXXを追加
2. `.kiro/specs/{feature-name}/` フォルダを作成
3. `requirements.md`, `design.md`, `tasks.md` を作成
4. 実装開始

## アーカイブルール

### タスク完了時
1. タスクが🟢 Doneになったら、そのまま`implementation-tasks.md`に残す
2. 直近バージョンの完了タスクは見やすさのため残しておく

### 次のバージョンリリース時
1. 前バージョンの完了タスクを`completed-tasks.md`に移動
2. `completed-tasks.md`はバージョン降順で整理（新しいものが上）

**例**: v1.18.0リリース時 → v1.17.0の完了タスク（TASK-001）を`completed-tasks.md`に移動

## まとめ

- **2つのタスクファイルは常に同期させる**
- **完了時は必ず両方を更新する**
- **不一致を見つけたら即座に修正する**
- **次のバージョンリリース時に前バージョンの完了タスクをアーカイブ**

これにより、プロジェクトの進捗状況が常に正確に把握でき、タスクリストも見やすく保たれます。