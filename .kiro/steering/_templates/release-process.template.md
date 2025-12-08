# {{project.name}} リリースプロセス

## 基本方針

{{project.name}}プロジェクトでは、**リリース前の徹底的な確認**を重視します。

## リリース前の最終確認

実装完了後、リリース前に以下を確認します：

### 基本チェックリスト

- [ ] **全テストがパス**
{% if project.language == "python" %}
  ```bash
  bash run_coverage.sh
  ```
{% endif %}

- [ ] **カバレッジが目標値以上**
  - 目標: {{testing.coverage_target}}%以上（90%以上なら許容）

- [ ] **実際に動作確認（手動実行）**
{% if project.type == "cli-tool" %}
  ```bash
  # 主要コマンドを実行
  {{project.name|lower}} advise
  {{project.name|lower}} status
  ```
{% endif %}

### 手動動作確認チェックリスト

新機能の手動確認を行います：

**基本動作確認**:
- [ ] 主要コマンドが正常に実行できる
- [ ] 設定ファイルが正しく読み込まれる
- [ ] 新機能が期待通り動作する
- [ ] エラーなく実行完了する

**設定変更テスト**:
- [ ] 機能の有効/無効切り替え（`enabled: true/false`）
- [ ] 詳細度の変更（該当する場合: minimal/normal/detailed）
- [ ] カスタム設定の動作確認
- [ ] デフォルト値での動作確認

**エラーハンドリング**:
- [ ] 不正な設定でもクラッシュしない
- [ ] エラーメッセージが分かりやすい（{{communication.language_name}}、原因と対処法）
- [ ] ログに詳細情報が記録される

**後方互換性**:
- [ ] 既存機能に影響がない
- [ ] 既存の設定ファイルで動作する
- [ ] 新機能を無効化しても従来通り動作する

- [ ] **ドキュメントが更新されている**
  - README.md
  - {{changelog.location}}
  - version.txt

- [ ] **CHANGELOGが記録されている**
  - `[Unreleased]`セクションに変更内容を記載

{% if project.type == "cli-tool" %}
### cronジョブのテスト（該当する場合）

cronジョブで実行されるスクリプトは、以下を確認：

1. **手動実行テスト**
{% if project.language == "python" %}
   ```bash
   python scripts/main.py
   ```
{% endif %}

2. **ログ確認**
   ```bash
   tail -20 log/main.log
   ```

3. **1分待ってcron実行を確認**
   ```bash
   # 1分後
   tail -5 log/main.log
   ```

4. **エラーがないことを確認**
   - ImportError
   - 設定ファイルエラー
   - 実行時エラー
{% endif %}

### リリース判断

全てのチェックが完了したら、リリース可能です：

1. ✅ 全テストパス
2. ✅ カバレッジ目標達成
3. ✅ 手動動作確認OK
{% if project.type == "cli-tool" %}
4. ✅ cronジョブ正常動作（該当する場合）
{% endif %}
5. ✅ ドキュメント更新完了

**リリース手順**:
1. {{git.main_branch}}にマージ
2. バージョンタグ作成
3. リモートにプッシュ
4. GitHub Releasesに登録
5. RELEASE_NOTES.mdをアーカイブ

## 既存テストの失敗への対応

新機能実装中に既存テストが失敗した場合の対応方針：

### 1. 新機能と関係ない場合

**判断基準**:
- 失敗したテストが新機能のコードに触れていない
- 以前から存在していた問題の可能性がある
- 新機能を無効化してもテストが失敗する

**対応**:
- ✅ 既存の問題として記録（GitHub Issue作成）
- ✅ 新機能のリリースは継続
- ✅ 別タスクとして修正を計画
- ✅ {{changelog.location}}に「既知の問題」として記載（必要に応じて）

**例**:
```
TASK-003実装中に、notification_throttleのプロパティテスト2件が
DeadlineExceededで失敗。新機能とは無関係なため、Issue #XXXとして記録し、
vX.X.Xのリリースは継続。
```

### 2. 新機能が原因の場合

**判断基準**:
- 失敗したテストが新機能のコードに関連している
- 新機能を無効化するとテストがパスする
- 既存機能の動作が変わった

**対応**:
- ❌ リリースを延期
- ✅ 即座に修正
- ✅ リリース前に全テストパスを確認
- ✅ 後方互換性を確認

**修正方針**:
1. 既存機能への影響を最小化
2. 新機能を無効化できるようにする（`enabled: false`）
3. デフォルト値で従来通り動作するようにする

## マージ時のトラブルシューティング

{{git.main_branch}}ブランチへのマージでエラーが発生した場合の対処法：

### エラー: "Your local changes would be overwritten by merge"

**原因**: {{git.main_branch}}ブランチに未コミットの変更が残っている

**対処法**:
```bash
# 1. 現在の状態を確認
git status

# 2. 変更を破棄してクリーンな状態に
git reset --hard HEAD
git clean -fd

# 3. 状態確認
git status

# 4. 再度マージ
git merge {{git.branch_prefix.feature}}XXX-feature-name
```

### エラー: "unable to create file ... No such file or directory"

**原因**: ディレクトリが存在しない

**対処法**:
```bash
# 必要なディレクトリを作成
mkdir -p .kiro/steering
mkdir -p .kiro/tasks
mkdir -p {{spec.location}}

# 再度マージ
git merge {{git.branch_prefix.feature}}XXX-feature-name
```

### マージ後の確認

```bash
# マージ結果を確認
git status

# ログ確認
git log --oneline -5

# リモートにプッシュ
git push origin {{git.main_branch}}
```

## GitHub Releases登録後の作業

バージョンタグをプッシュした後、以下の手順でGitHub Releasesに登録します：

### 1. RELEASE_NOTES.mdから情報をコピー

`.kiro/RELEASE_NOTES.md`の「登録待ちリリース」セクションから、該当バージョンの情報をコピーします。

### 2. GitHub Releasesに登録

1. GitHubのリリースページにアクセス: `https://github.com/{user}/{repo}/releases/new`
2. 以下の情報を入力：
   - **Tag**: `vX.X.X`（既に作成済み）
   - **Title**: `vX.X.X - 機能名`
   - **Description**: RELEASE_NOTES.mdの内容をコピー＆ペースト
3. 「Publish release」をクリック

### 3. RELEASE_NOTES.mdをアーカイブ

GitHub Releasesに登録完了後、`.kiro/RELEASE_NOTES.md`を更新：

```markdown
## 登録待ちリリース

<!-- Kiroがここに新しいリリース情報を追記します -->

---

## 登録済みリリース（アーカイブ）

### ✅ vX.X.X - 機能名
**作成日**: YYYY-MM-DD  
**登録日**: YYYY-MM-DD  
**GitHub Release**: https://github.com/{user}/{repo}/releases/tag/vX.X.X

---
```

**重要**: 登録日とGitHub ReleaseのURLを必ず記載してください。

## まとめ

- **リリース前**: 徹底的な確認（テスト、手動動作確認、ドキュメント）
- **既存テスト失敗**: 新機能と関係ない場合は継続、関係ある場合は修正
- **マージエラー**: 状態確認とクリーンアップで対処
- **GitHub Releases**: RELEASE_NOTES.mdから情報をコピーして登録

このプロセスにより、高品質なリリースが実現されます。
