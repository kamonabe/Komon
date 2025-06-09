## [1.0.0] - 2025-06-01
### 初期リリース
- CPU / メモリ / ディスク使用率の監視
- 閾値による警告とSlack／メール通知
- 使用履歴のローテーション保存（最大95世代）
- ログ急増検知（ベースライン比較）
- `komon advise` 対話型アドバイス機能
- pip / OS更新提案、systemctl再起動の助言
- `version.txt` による手動バージョン管理

## [1.1.0] - 2025-06-01
### Added
- `komon advise` に「提案スキップ記録（skip_advices.json）」機能を追加。
  同一提案について、`n` を選んだ場合は1週間再提案を控えるようになりました。

## [1.2.0] - 2025-06-03
### Changed
- `komon advise` の「OSやパッケージの更新確認」処理を大幅に強化。
  - AlmaLinux向けに `dnf` を使用したパッケージ更新確認に対応。
  - セキュリティパッチとそれ以外のパッチを分離して確認・表示。
  - 各カテゴリで件数と例を最大10件表示。
  - セキュリティパッチについては対話形式で適用確認を実施し、`dnf upgrade -y` による自動適用に対応。

### Fixed
- セキュリティパッチが未適用でも「更新なし」と誤認される問題を防ぐため、dnfの標準出力解析を改良。

## [1.2.1] - 2025-06-03
### Fixed
- セキュリティパッチ確認時に `dnf updateinfo list security` が常に1件表示される不具合を修正。
  - フィルタ条件を `RHSA-` を含む行のみに限定し、不要な出力（メタデータ情報等）を排除。
  - 本来パッチが存在しない状況でも「更新あり」と誤表示される問題が解消されました。

## [1.3.0] - 2025-06-04
### Added
- `komon status` コマンドを新規実装。
  - 現在のCPU / メモリ / ディスク使用率を表示。
  - `settings.yml` に定義された各リソースの閾値を併記。
  - Slack / メール通知の有効・無効状態を表示。
  - ログ監視対象の有効／無効一覧を表示。
- `komon` コマンドが `advise.py` および `status.py` をルートディレクトリから呼び出せるように改良。
  - `komon advise` や `komon status` など、CLI形式での実行に対応。
  - 同時に、`python3 advise.py` や `python3 status.py` による直接実行も引き続きサポート。

### Changed
- CLIルーター (`komon/cli.py`) を汎用化し、動的にルート直下のスクリプトを読み込む構成に変更。
  - コマンド追加時の拡張性が向上。

### Internal
- `setup.py` に `console_scripts` を定義し、`komon` コマンドのインストール／実行を可能に。

## [1.3.1] - 2025-06-04
### Fixed
- CLIのUsage表示 (`komon [advise|status]`) において、同じ文字列が複数箇所に分散していた問題を解消。
  - `available_commands` リストでコマンド一覧を一元管理する構成に変更し、将来的なコマンド追加やUsage表示の更新漏れを防止。
  - メンテナンス性・可読性が向上。

## [1.4.0] - 2025-06-05
### 🚀 新機能
- `initial.py` を追加し、対話形式で `settings.yml` を作成できる初期設定スクリプトを導入
- `komon initial` コマンド対応（`cli.py` にてラップ）
- `komon_guide.py` を新規追加し、初心者向けの操作ガイドをCLI形式で提供

### 🛠 改善・修正
- `initial.py` 実行時、Slack通知が有効な場合にWebhook URLを入力可能に
- `initial.py` で既存の `settings.yml` がある場合は上書きせずスキップするよう修正

### 🧼 内部整理
- `init.sh` に `komon initial` 実行の案内を追記
- `requirements.txt` にバージョン明記（例: `psutil>=5.9.0`）

## [1.5.0] - 2025-06-06
### 機能追加
- プロセス単位でのCPU使用率（top N）を収集・保存する `collect_detailed_resource_usage()` を新実装
- `main.py` の収集ロジックを `collect_detailed_resource_usage()` に変更し、JSON履歴へ `cpu_by_process` を出力する形式に拡張
- `advise.py` にて、CPU使用率の内訳（プロセス別）を📌補足情報として常時出力する機能を追加

### 改善
- `usage_history.json` のフォーマット変更に対応した新しい改善アドバイスの追加（プロセス可視化）

### 注意事項
- `usage_history.json` に `cpu_by_process` が追加されます。旧バージョンとの互換性に注意してください

## [1.6.0] - 2025-06-09
### 改善
- `komon advise` にて、セキュリティ以外のパッケージ更新が検出された場合に、対応コマンド `sudo dnf upgrade -y` を案内表示するよう改善
- ユーザーが気づきから次の行動に移りやすくなり、UX向上に寄与
