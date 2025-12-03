# Komonコマンドリファレンス

このドキュメントでは、Komonで使用できる全てのコマンドを体系的に説明します。

## 📖 目次

- [日常使用コマンド](#-日常使用コマンド)
- [監視・レポートコマンド](#-監視レポートコマンド)
- [初期設定・ガイド](#-初期設定ガイド)
- [開発・メンテナンスコマンド](#-開発メンテナンスコマンド)
- [コマンド実行方法](#-コマンド実行方法)

---

## 🎯 日常使用コマンド

開発者が日常的に使用するコマンドです。

### `komon advise` / `python scripts/advise.py`

**対話型アドバイザー** - システムの状態を分析して改善提案を表示します。

```bash
# 基本的な使い方
komon advise

# 詳細表示モード（全ての情報を表示）
komon advise --verbose

# 特定のセクションのみ表示
komon advise --section status    # システム状態のみ
komon advise --section alerts    # 警戒情報のみ
komon advise --section process   # プロセス情報のみ
komon advise --section history   # 通知履歴のみ

# 通知履歴の表示件数を指定
komon advise --history 10        # 直近10件のみ表示
komon advise --history 0         # 全件表示
```

**表示内容**:
- 現在のシステム状態（CPU、メモリ、ディスク）
- 警戒情報（閾値超過の警告）
- 改善提案（セキュリティパッチ、システムパッチ）
- 多重実行プロセスの検出
- 長時間実行プロセスの検出
- ディスク使用量の予測
- 通知履歴（最新5件、または指定件数）

**オプション**:
- `--verbose`: 全ての情報を詳細表示
- `--section <name>`: 特定セクションのみ表示
  - `status`: システム状態
  - `alerts`: 警戒情報
  - `advice`: 改善提案
  - `process`: プロセス情報
  - `prediction`: ディスク予測
  - `history`: 通知履歴
- `--history <N>`: 通知履歴の表示件数（0で全件）

**使用例**:
```bash
# 朝の確認
komon advise

# 詳細な状態確認
komon advise --verbose

# 通知履歴だけ確認
komon advise --section history --history 20
```

---

### `komon status` / `python scripts/status.py`

**ステータス表示** - 現在のシステム状態を簡潔に表示します。

```bash
komon status
```

**表示内容**:
- CPU使用率
- メモリ使用率
- ディスク使用率
- 各リソースの閾値との比較

**使用例**:
```bash
# 現在の状態を確認
komon status

# cronで定期的に記録
*/30 * * * * komon status >> /var/log/komon/status.log
```

---

### `komon guide` / `python scripts/komon_guide.py`

**ガイドメニュー** - Komonの使い方を対話的に案内します。

```bash
komon guide
```

**機能**:
- 初期設定の確認
- 各コマンドの説明
- トラブルシューティング
- 設定ファイルの編集

**使用例**:
```bash
# 使い方が分からない時
komon guide

# 設定を変更したい時
komon guide
# → メニューから「設定ファイルを編集」を選択
```

---

## 📊 監視・レポートコマンド

cron等で定期実行するコマンドです。

### `python scripts/main.py`

**リソース監視** - CPU、メモリ、ディスクの使用率を監視し、閾値超過時に通知します。

```bash
python scripts/main.py
```

**機能**:
- リソース使用率の監視
- 3段階閾値判定（警告/警戒/緊急）
- 高負荷プロセスの検出
- Slack/Email通知
- 通知履歴の保存

**cron設定例**:
```bash
# 5分おきに実行
*/5 * * * * cd /path/to/Komon && python scripts/main.py >> log/main.log 2>&1
```

---

### `python scripts/main_log_monitor.py`

**ログ急増監視** - ログファイルの行数を監視し、急増時に通知します。

```bash
python scripts/main_log_monitor.py
```

**機能**:
- ログファイルの行数カウント
- 前日比での急増検出
- ログ末尾の抜粋表示（デフォルト10行）
- Slack/Email通知

**cron設定例**:
```bash
# 5分おきに実行
*/5 * * * * cd /path/to/Komon && python scripts/main_log_monitor.py >> log/monitor.log 2>&1
```

---

### `python scripts/main_log_trend.py`

**ログ傾向分析** - 過去7日間のログから異常なパターンを検出します。

```bash
python scripts/main_log_trend.py
```

**機能**:
- 過去7日間のログ統計分析
- 異常な増加パターンの検出
- トレンド判定（安定/増加傾向/減少傾向）
- Slack/Email通知

**cron設定例**:
```bash
# 毎日3時に実行
0 3 * * * cd /path/to/Komon && python scripts/main_log_trend.py >> log/trend.log 2>&1
```

---

### `python scripts/weekly_report.py`

**週次健全性レポート** - 過去7日分のリソースデータを集計してレポートを生成します。

```bash
python scripts/weekly_report.py
```

**機能**:
- 過去7日分のリソース使用率集計
- 先週比の増減表示
- 今週の警戒情報サマリー
- ディスク使用量の予測
- トレンド判定
- Slack/Email通知

**cron設定例**:
```bash
# 毎週月曜9時に実行
0 9 * * 1 cd /path/to/Komon && python scripts/weekly_report.py >> log/weekly_report.log 2>&1
```

---

## 🚀 初期設定・ガイド

初回セットアップ時に使用するコマンドです。

### `komon initial` / `python scripts/initial.py`

**初期設定ウィザード** - Komonの初期設定を対話的に行います。

```bash
komon initial
```

**設定内容**:
- 設定ファイル（settings.yml）の作成
- 監視対象の選択
- 閾値の設定
- 通知設定（Slack/Email）
- データディレクトリの作成

**使用例**:
```bash
# 初回インストール後
komon initial

# 設定をやり直したい時
komon initial
# → 既存の設定を上書き確認
```

---

### `bash scripts/init.sh`

**環境初期化スクリプト** - 開発環境のセットアップを自動化します。

```bash
bash scripts/init.sh
```

**機能**:
- 必要なディレクトリの作成
- 設定ファイルのコピー
- 依存パッケージのインストール確認

**使用例**:
```bash
# 開発環境のセットアップ
bash scripts/init.sh
```

---

## 🔧 開発・メンテナンスコマンド

開発者やメンテナンス時に使用するコマンドです。

### `python scripts/check_coverage.py`

**カバレッジ分析** - テストカバレッジを分析し、未テストのファイルを検出します。

```bash
python scripts/check_coverage.py
```

**機能**:
- 実装ファイルとテストファイルの対応確認
- 未テストファイルの検出
- カバレッジレポートの生成

**使用例**:
```bash
# カバレッジを確認
python scripts/check_coverage.py

# 詳細なカバレッジレポート
bash run_coverage.sh
```

---

### `python scripts/generate_release_notes.py`

**リリースノート自動生成** - CHANGELOGからGitHub Releases用のリリースノートを生成します。

```bash
python scripts/generate_release_notes.py <version>
```

**機能**:
- CHANGELOGから該当バージョンを抽出
- GitHub Releases用にフォーマット
- `.kiro/RELEASE_NOTES.md`に追記

**使用例**:
```bash
# v1.23.0のリリースノートを生成
python scripts/generate_release_notes.py v1.23.0
```

---

### `python scripts/check_status_consistency.py`

**ステータス整合性チェック** - タスク管理ファイルのステータス整合性を検証します。

```bash
python scripts/check_status_consistency.py
```

**機能**:
- future-ideas.mdとimplementation-tasks.mdのステータス一致確認
- tasks.ymlのtask-id/feature-name記載確認
- 完了タスクのアーカイブ状況確認

**使用例**:
```bash
# GitHub push前に実行
python scripts/check_status_consistency.py
```

---

### `python scripts/validate_specs.py`

**Spec構造検証** - Spec文書の構造を検証します。

```bash
python scripts/validate_specs.py
```

**機能**:
- Front Matterの必須フィールド確認
- 日付フォーマット確認
- 必須セクションの存在確認
- 受入基準・プロパティ・タスクの数チェック

**使用例**:
```bash
# Spec作成後に実行
python scripts/validate_specs.py
```

---

### `python scripts/check_spec_consistency.py`

**Spec一貫性検証** - Spec文書間の一貫性を検証します。

```bash
python scripts/check_spec_consistency.py
```

**機能**:
- 3ファイル間のfeature名一致確認
- 存在しない受入基準の参照チェック
- プロパティと受入基準の対応確認
- タスクと受入基準のカバレッジ確認

**使用例**:
```bash
# Spec作成後に実行
python scripts/check_spec_consistency.py
```

---

### `python scripts/generate_steering_rules.py`

**ステアリングルール生成** - テンプレートからステアリングルールを生成します。

```bash
python scripts/generate_steering_rules.py
```

**機能**:
- テンプレート（.template.md）を読み込み
- project-config.ymlの設定を適用
- ステアリングルール（.md）を生成

**使用例**:
```bash
# ステアリングルールを再生成
python scripts/generate_steering_rules.py
```

---

### `python scripts/generate_task_template.py`

**タスクテンプレート生成** - タスク管理ファイルのテンプレートを生成します。

```bash
python scripts/generate_task_template.py
```

**機能**:
- implementation-tasks.mdのテンプレート生成
- project-config.ymlの設定を適用

**使用例**:
```bash
# タスクテンプレートを再生成
python scripts/generate_task_template.py
```

---

### `python scripts/generate_spec_templates.py`

**Specテンプレート生成** - 新しいSpec文書のテンプレートを生成します。

```bash
python scripts/generate_spec_templates.py <feature-name>
```

**機能**:
- requirements.yml, design.yml, tasks.ymlを生成
- Front Matterを自動設定
- 基本構造を作成

**使用例**:
```bash
# 新機能のSpecを作成
python scripts/generate_spec_templates.py notification-history
```

---

### `python scripts/convert_specs_to_yaml.py`

**Spec YAML変換** - Markdown形式のSpecをYAML形式に変換します。

```bash
python scripts/convert_specs_to_yaml.py
```

**機能**:
- requirements.md → requirements.yml
- design.md → design.yml
- tasks.md → tasks.yml

**使用例**:
```bash
# Specを構造化YAML形式に変換
python scripts/convert_specs_to_yaml.py
```

---

### `python scripts/convert_steering_to_yaml.py`

**ステアリングルールYAML変換** - ステアリングルールをYAML形式に変換します。

```bash
python scripts/convert_steering_to_yaml.py
```

**機能**:
- ステアリングルール（.md）をYAML形式に変換
- Front Matterを抽出

**使用例**:
```bash
# ステアリングルールをYAML形式に変換
python scripts/convert_steering_to_yaml.py
```

---

### `python scripts/add_version_to_specs.py`

**Specにバージョン情報追加** - 完了したSpecにバージョン情報を追加します。

```bash
python scripts/add_version_to_specs.py
```

**機能**:
- 完了したSpecのFront Matterにバージョン情報を追加
- 完了日を記録

**使用例**:
```bash
# リリース後に実行
python scripts/add_version_to_specs.py
```

---

### `bash scripts/setup_coverage_fix.sh`

**カバレッジ設定修正** - pytest-covの設定を修正します。

```bash
bash scripts/setup_coverage_fix.sh
```

**機能**:
- pytest.iniの設定を修正
- カバレッジ計測の問題を解決

**使用例**:
```bash
# カバレッジが正しく計測されない場合
bash scripts/setup_coverage_fix.sh
```

---

## 💡 コマンド実行方法

Komonのコマンドは、以下の2つの方法で実行できます。

### 方法1: `komon` コマンド（推奨）

PyPIからインストールした場合、`komon`コマンドが使用できます。

```bash
# インストール
pip install komon

# 実行
komon advise
komon status
komon initial
komon guide
```

### 方法2: `python scripts/` から直接実行

開発版やGitHubからクローンした場合は、スクリプトを直接実行します。

```bash
# クローン
git clone https://github.com/kamonabe/Komon.git
cd Komon

# 実行
python scripts/advise.py
python scripts/status.py
python scripts/initial.py
python scripts/komon_guide.py
```

### cron実行時の注意

cron実行時は、フルパスを指定することを推奨します。

```bash
# Pythonのパスを確認
which python3
# → /usr/bin/python3

# cronに設定
*/5 * * * * cd /path/to/Komon && /usr/bin/python3 scripts/main.py >> log/main.log 2>&1
```

---

## 📝 コマンド一覧表

| コマンド | 用途 | 頻度 | 実行方法 |
|---------|------|------|---------|
| `komon advise` | 対話型アドバイザー | 日常 | 手動 |
| `komon status` | ステータス表示 | 日常 | 手動 |
| `komon guide` | ガイドメニュー | 初回/困った時 | 手動 |
| `komon initial` | 初期設定 | 初回のみ | 手動 |
| `main.py` | リソース監視 | 定期 | cron |
| `main_log_monitor.py` | ログ急増監視 | 定期 | cron |
| `main_log_trend.py` | ログ傾向分析 | 定期 | cron |
| `weekly_report.py` | 週次レポート | 定期 | cron |
| `check_coverage.py` | カバレッジ分析 | 開発時 | 手動 |
| `generate_release_notes.py` | リリースノート生成 | リリース時 | 手動 |
| `check_status_consistency.py` | ステータス整合性チェック | push前 | 手動 |
| `validate_specs.py` | Spec構造検証 | Spec作成時 | 手動 |
| `check_spec_consistency.py` | Spec一貫性検証 | Spec作成時 | 手動 |

---

## 🔗 関連ドキュメント

- [README.md](../README.md) - プロジェクト概要
- [詳細ドキュメント](README.md) - 機能の詳細説明
- [セキュリティガイド](SECURITY.md) - セキュリティベストプラクティス
- [変更履歴](CHANGELOG.md) - バージョンごとの変更内容

---

## ❓ よくある質問

### Q: どのコマンドを日常的に使えばいいですか？

**A**: 以下の3つを覚えておけば十分です：

```bash
komon advise    # システム状態の確認
komon status    # 簡易ステータス確認
komon guide     # 使い方が分からない時
```

### Q: cronで実行すべきコマンドは？

**A**: 以下の4つを推奨します：

```bash
# 必須
*/5 * * * * python scripts/main.py              # リソース監視

# 推奨
*/5 * * * * python scripts/main_log_monitor.py  # ログ監視
0 3 * * * python scripts/main_log_trend.py      # ログ傾向分析
0 9 * * 1 python scripts/weekly_report.py       # 週次レポート
```

### Q: 開発者向けコマンドはどれですか？

**A**: 以下のコマンドは開発・メンテナンス時に使用します：

- `check_coverage.py` - テストカバレッジ確認
- `validate_specs.py` - Spec検証
- `generate_release_notes.py` - リリースノート生成
- `check_status_consistency.py` - タスク整合性チェック

通常のユーザーは使用する必要はありません。

---

このドキュメントは、Komon v1.23.0時点の情報です。
最新情報は[GitHub](https://github.com/kamonabe/Komon)を参照してください。
