---
inclusion: manual
---

# リリースプロセス

## リリース前チェックリスト

- [ ] 全テストがパス（`project-config.yml` の `testing.test_command`）
- [ ] カバレッジが目標値以上（`project-config.yml` の `testing.coverage_target`）
- [ ] 主要コマンドの手動動作確認
- [ ] 設定の有効/無効切り替えテスト
- [ ] 不正な設定でもクラッシュしないことを確認
- [ ] 後方互換性の確認（既存設定ファイルで動作する）
- [ ] ドキュメント更新済み（README, CHANGELOG）
- [ ] `project-config.yml` の `versioning.version_files` に定義された全ファイルのバージョンが一致

## cronジョブのテスト（該当する場合）

1. 手動実行テスト → 2. ログ確認 → 3. 1分待ってcron実行確認 → 4. エラーなし確認

## 既存テスト失敗時の判断

新機能と無関係の場合:
- 既存の問題として記録（Issue作成）
- 新機能のリリースは継続
- 別タスクとして修正を計画

新機能が原因の場合:
- リリースを延期
- 即座に修正
- 後方互換性を確認

## マージ → タグ → リリース

```bash
git checkout main
git merge feature/task-XXX-{feature-name}
git tag vX.X.X
git push origin main --tags
```

## タグ作成後の必須作業

1. 前バージョンの完了タスクを `completed-tasks.md` にアーカイブ
2. `python scripts/generate_release_notes.py vX.X.X` でリリースノート生成
3. GitHub Releasesに登録（RELEASE_NOTES.mdの内容をコピー）
4. 登録後、RELEASE_NOTES.mdの該当エントリを「登録済み」に移動

## PyPI公開（該当する場合）

タイミング: GitHub Releasesに登録後、CIチェックがクリアしたことを確認してから

```bash
python -m build
python -m twine upload dist/*
pip install komon==X.X.X  # 確認
```
