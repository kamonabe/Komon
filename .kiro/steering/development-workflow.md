---
inclusion: auto
name: development-workflow
description: 実装、TASK-、開発開始、Spec作成、仕様駆動開発のワークフロー
---

# 仕様駆動開発ワークフロー

## 開発フロー全体像

```
アイデア → タスク化 → Spec作成(main) → ブランチ作成 → 実装 → テスト → レビュー → マージ → リリース
```

## フェーズ1: アイデア → タスク化

1. `future-ideas.md` にアイデアを記録
2. 実装決定 → `implementation-tasks.md` に TASK-XXX として追加
3. タスク番号は `implementation-tasks.md` と `completed-tasks.md` の両方を確認して重複を防ぐ

## フェーズ2: Spec作成（mainブランチ）

`.kiro/specs/{feature-name}/` に以下を YAML形式 で作成:
- `requirements.yml`: 要件定義（受入基準を含む）
- `design.yml`: 設計書（正確性プロパティ、レジリエンス設計を含む）
- `tasks.yml`: 実装タスクリスト

作成前の必須確認:
- 既存Specの構造を確認（`ls .kiro/specs/` で形式を把握）
- ファイル拡張子は `.yml`（`.md` ではない）
- `yaml.safe_load()` でパース可能であること

Spec完成後、`project-config.yml` の `quality.spec_validation` に定義されたスクリプトで自動検証される（hookで実行）。

## フェーズ3: 実装

実装開始時にhookがブランチ安全性を自動検証する。mainブランチでのコード変更は自動的にブロックされる。

サブタスクごとに以下を実行:
1. コード実装
2. タスクファイルを即時更新（Spec別 + 実装タスクリスト両方）
3. 進捗報告（例: 「✅ サブタスク1完了、進捗: 1/3」）

## フェーズ4: 完了報告とバージョン決定

実装完了時に報告する内容:
- 実装内容のサマリー
- テスト結果（全テストパス確認）
- カバレッジ（`project-config.yml` の目標値と比較）
- 提案するバージョン番号（`versioning-rules.md` の判断フローに従う）

ユーザーがバージョン番号を決定したら、`project-config.yml` の `versioning.version_files` に定義された全ファイルを順番に更新する。

## フェーズ5: マージとリリース

1. push前品質チェック（hookで自動実行）
2. ユーザーがmainにマージ・タグ作成
3. 前バージョンの完了タスクを `completed-tasks.md` にアーカイブ
4. `python scripts/generate_release_notes.py vX.X.X` でリリースノート生成
5. PyPI公開（該当する場合、CIチェック通過後）

## 開発モードの使い分け

| モード | 使用場面 | 特徴 |
|--------|---------|------|
| Specモード | 新機能追加、小規模変更 | Kiroが自律的に進める |
| Vibeモード | 既存コードの大幅変更、設計見直し | ユーザーと対話しながら進める |

判断基準: 既存機能への影響が大きい場合 → Vibeモードで仕様を詰めてからSpecモードに移行。

## 自律実行の範囲

Kiroが自律的に進めて良いこと:
- Spec作成（YAML形式）
- コード実装・テスト作成
- ドキュメント更新（README, CHANGELOG）
- タスクファイルの更新
- リリースノートの生成

ユーザー確認が必要なこと:
- 既存機能に大きな影響がある変更
- バージョン番号の最終決定
- アイデアの実装判断（future-ideas → implementation-tasks）

## レジリエンス設計（Spec作成時の必須検討事項）

`design.yml` 作成時、以下を必ず検討し `resilience` セクションに記載する:

1. サーキットブレイカー: adopted / not-adopted / delegated
2. 通知スパム防止: 通知機能がある場合
3. Baseline自動リセット: baseline使用機能の場合
4. データ欠損時のフォールバック
5. タイムアウト・リトライ戦略

各項目に `rationale`（理由）を必ず記載。「検討したが採用しない」も設計判断として記録する。
