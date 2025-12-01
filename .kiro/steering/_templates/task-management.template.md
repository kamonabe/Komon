# {{project.name}}プロジェクトのタスク管理ルール

## タスクファイルの構造

{{project.name}}プロジェクトでは、2階層のタスク管理を採用しています：

### 1. 実装タスクリスト（マスター）
**ファイル**: `.kiro/tasks/implementation-tasks.md`

- **役割**: プロジェクト全体のタスク管理（進行中・未着手 + 直近バージョンの完了タスク）
- **粒度**: 機能単位（TASK-001, TASK-002...）
- **ステータス**: 🔴 TODO / 🟡 In Progress / 🟢 Done / ⏸️ On Hold / ❌ Cancelled
- **更新タイミング**: タスク開始時、各サブタスク完了時に即座に同期、全タスク完了時

### 1-2. 完了タスクアーカイブ
**ファイル**: `.kiro/tasks/completed-tasks.md`

- **役割**: 過去バージョンの完了タスクを保存
- **整理**: バージョン降順（新しいものが上）
- **移動タイミング**: 次のバージョンリリース時

### 2. Spec別タスクリスト（詳細）
**ファイル**: `{{spec.location}}{feature-name}/tasks.md`

- **役割**: 個別機能の詳細な実装手順
- **粒度**: サブタスク単位（実装、テスト、ドキュメント）
- **ステータス**: `[ ]` / `[x]`
- **更新タイミング**: 各サブタスク完了時

## 🚨 重要：サブタスク完了時の即時更新ルール

各サブタスクが完了したら、**即座に両方のファイルを更新**してください：

### ステップ1: Spec別タスクリストを更新
```markdown
# {{spec.location}}{feature-name}/tasks.md
- [x] 1. Create module  ← 今完了した
- [ ] 2. Write tests    ← 次はこれ
- [ ] 3. Update docs
```

### ステップ2: 実装タスクリストも即座に同期
```markdown
# .kiro/tasks/implementation-tasks.md
### [TASK-XXX] 機能名
**ステータス**: 🟡 In Progress
**進捗**: 1/3 完了  ← 進捗率を追加

#### タスク分解
- [x] サブタスク1: モジュール作成 ← 即座にチェック
- [ ] サブタスク2: テスト作成
- [ ] サブタスク3: ドキュメント更新
```

### ステップ3: 全サブタスク完了時
```markdown
### [TASK-XXX] 機能名
**ステータス**: 🟢 Done  ← 完了に変更
**完了日**: YYYY-MM-DD (vX.X.X)
**進捗**: 3/3 完了

#### タスク分解
- [x] サブタスク1: モジュール作成
- [x] サブタスク2: テスト作成
- [x] サブタスク3: ドキュメント更新

#### 完了条件
- ✅ 条件1が満たされている
- ✅ 条件2が満たされている
```

### メリット

1. **中断・再開が容易**
   - 実装タスクリストを見るだけで「次は何をやるか」が分かる
   - Spec別タスクリストを確認する必要がない

2. **進捗の可視性**
   - 「1/3完了」のように進捗率が一目で分かる
   - チーム開発でも状況共有が容易

3. **仕様駆動開発との相性**
   - 小さく区切って進める
   - いつでも中断・再開できる
   - 確認コストが低い

## チェックリスト

### サブタスク完了時

- [ ] `{{spec.location}}{feature-name}/tasks.md` のサブタスクに `[x]` を付けた
- [ ] `.kiro/tasks/implementation-tasks.md` のタスク分解も `[x]` に同期した
- [ ] `.kiro/tasks/implementation-tasks.md` の進捗率を更新した（例: 1/3 完了）
- [ ] ユーザーに進捗を報告した

### 全タスク完了時

- [ ] `{{spec.location}}{feature-name}/tasks.md` の全サブタスクが `[x]` になっている
- [ ] `.kiro/tasks/implementation-tasks.md` のステータスが 🟢 Done になっている
- [ ] `.kiro/tasks/implementation-tasks.md` のタスク分解が全て `[x]` になっている
- [ ] `.kiro/tasks/implementation-tasks.md` の完了条件が全て ✅ になっている
- [ ] 完了日とバージョンが記載されている
- [ ] `{{changelog.location}}` に記録されている

## Kiro AIへの指示

### サブタスク完了時（即座に実行）

各サブタスクが完了したら、**即座に**以下を実行してください：

1. **Spec別タスクリストを更新**
   ```markdown
   # {{spec.location}}{feature-name}/tasks.md
   - [x] 1. Create module  ← チェックマークを付ける
   ```

2. **実装タスクリストも即座に同期**
   ```markdown
   # .kiro/tasks/implementation-tasks.md
   #### タスク分解
   - [x] サブタスク1: モジュール作成  ← 同期
   ```

3. **進捗率を更新**
   ```markdown
   **進捗**: 1/3 完了  ← 計算して更新
   ```

4. **ユーザーに報告**
   ```
   ✅ サブタスク1「モジュール作成」が完了しました
   進捗: 1/3 完了
   
   次のサブタスク: テスト作成
   ```

### 全サブタスク完了時

全てのサブタスクが完了したら：

1. **ステータスを🟢 Doneに変更**
2. **完了日を記録**
3. **完了条件を✅に変更**
4. **CHANGELOGに記録**
5. **ユーザーに完了報告**

## 例：正しい完了状態

### Spec別タスクリスト
```markdown
# {{spec.location}}notification-history/tasks.md
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
{% if project.type == "cli-tool" %}
- ✅ 通知が自動的に保存される
- ✅ `{{project.name|lower}} advise` で履歴が表示される
- ✅ 最大100件の制限が機能する
{% endif %}
```

## トラブルシューティング

### Q: Spec別タスクは完了しているが、実装タスクリストが未更新
**A**: 実装タスクリストを手動で更新してください。両方が一致している必要があります。

### Q: 新しい機能を追加する場合
**A**: 
1. `.kiro/tasks/implementation-tasks.md` に新しいTASK-XXXを追加
2. `{{spec.location}}{feature-name}/` フォルダを作成
3. {% for file in spec.required_files %}`{{file}}`{% if not loop.last %}, {% endif %}{% endfor %} を作成
4. 実装開始

## アーカイブルール

### タスク完了時（実装完了直後）
1. タスクが🟢 Doneになったら、そのまま`implementation-tasks.md`に残す
2. 直近バージョンの完了タスクは見やすさのため残しておく
3. **この時点ではアーカイブしない**

### 🚨 新バージョンリリース時（必須作業）

**タイミング**: 新しいバージョン（vX.Y.Z）のタグを作成した直後

**Kiroの必須作業**:
1. **前バージョンの完了タスクを特定**
   - 例: v1.19.0をリリース → v1.18.0の完了タスクを探す
   - `implementation-tasks.md`で「完了日: YYYY-MM-DD (v1.18.0)」を検索

2. **completed-tasks.mdに移動**
   - v1.18.0セクションを作成（バージョン降順で配置）
   - タスク全体をコピー＆ペースト
   - `implementation-tasks.md`から削除

3. **更新履歴を記録**
   - 両ファイルの「更新履歴」セクションに記録
   - 日付とタスク番号を明記

**具体例**:
```
v1.19.0をリリース
  ↓
v1.18.0の完了タスク（TASK-003）をcompleted-tasks.mdに移動
  ↓
implementation-tasks.mdには直近バージョン（v1.19.0）のみ残る
```

### Kiroへの厳格な指示

**新バージョンのタグ作成後、必ず以下を実行**:

```markdown
📋 アーカイブ作業（必須）

1. 前バージョンの完了タスクを確認
   - implementation-tasks.mdで前バージョンを検索
   - 例: 「完了日: 2025-11-27 (v1.18.0)」

2. completed-tasks.mdに移動
   - 新しいバージョンセクションを作成
   - タスク全体を移動
   - バージョン降順で配置

3. implementation-tasks.mdから削除
   - 移動したタスクを削除
   - 直近バージョンのみ残す

4. 更新履歴を記録
   - 両ファイルに記録

この作業を完了してから、次のステップに進んでください。
```

### チェックリスト（リリース時）

- [ ] 新バージョンのタグを作成した
- [ ] 前バージョンの完了タスクを特定した
- [ ] completed-tasks.mdに移動した
- [ ] implementation-tasks.mdから削除した
- [ ] 両ファイルの更新履歴を記録した
- [ ] 上記が全て完了してから次のステップに進んだ

## まとめ

- **2つのタスクファイルは常に同期させる**
- **完了時は必ず両方を更新する**
- **不一致を見つけたら即座に修正する**
- **次のバージョンリリース時に前バージョンの完了タスクをアーカイブ**

これにより、プロジェクトの進捗状況が常に正確に把握でき、タスクリストも見やすく保たれます。
