---
inclusion: fileMatch
fileMatchPattern: ".kiro/tasks/**"
---

# タスク管理ルール

## 2階層タスク管理

| ファイル | 役割 | 粒度 |
|---------|------|------|
| `.kiro/tasks/implementation-tasks.md` | プロジェクト全体のタスク管理 | 機能単位（TASK-XXX） |
| `.kiro/tasks/completed-tasks.md` | 過去バージョンの完了タスク保存 | バージョン降順 |
| `.kiro/specs/{feature}/tasks.yml` | 個別機能の詳細な実装手順 | サブタスク単位 |

ステータス: 🔴 TODO / 🟡 In Progress / 🟢 Done / ⏸️ On Hold / ❌ Cancelled

## サブタスク完了時の即時更新

各サブタスク完了時に必ず両方のファイルを同期する:

1. Spec別タスクリスト: `[x]` を付ける
2. 実装タスクリスト: `[x]` を付ける + 進捗率を更新（例: 1/3 完了）
3. ユーザーに進捗報告

全サブタスク完了時:
- ステータスを 🟢 Done に変更
- 完了日とバージョンを記載（例: 完了日: 2025-11-22 (v1.11.0)）
- 完了条件を ✅ に変更

## 新しいタスク番号の決定

タスク番号の重複を防ぐため、必ず両方のファイルをチェックする:

```bash
grep -o "TASK-[0-9][0-9][0-9]" .kiro/tasks/implementation-tasks.md .kiro/tasks/completed-tasks.md | sort -u
```

## アーカイブルール

タイミング: 新バージョンのタグ作成直後

1. 前バージョンの完了タスクを `implementation-tasks.md` から特定
2. `completed-tasks.md` に移動（バージョン降順で配置）
3. `implementation-tasks.md` から削除
4. 両ファイルの更新履歴に記録
