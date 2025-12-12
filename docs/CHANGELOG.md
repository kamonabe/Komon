# Changelog

Komonの変更履歴を記録します。

このプロジェクトは[Semantic Versioning](https://semver.org/)に従います。

## [Unreleased]

## [1.26.0] - 2025-12-12

### Added

- **Discord/Teams Webhook通知対応**
  - `send_discord_alert()` 関数を追加（Discord Webhook API対応）
  - `send_teams_alert()` 関数を追加（Teams Webhook API対応）
  - 環境変数対応: `KOMON_DISCORD_WEBHOOK`, `KOMON_TEAMS_WEBHOOK`
  - 全通知スクリプトに統合: main.py, main_log_monitor.py, weekly_report.py, main_log_trend.py
  - 設定ファイルにdiscord/teamsセクションを追加
  - 30件のテストケース追加（21ユニット + 9統合テスト）
  - 既存のSlack通知との完全な互換性を維持
  - README.md, docs/EXAMPLES.mdにDiscord/Teams設定例を追加

## [1.25.7] - 2025-12-11

### Fixed

- **Docker環境でのkomon initial問題を完全修正**
  - `find`コマンドを使用してsettings.yml.sampleの実際の場所を動的検索
  - 環境依存のパス推測を完全に排除
  - Python バージョン、仮想環境、OS に関係なく動作
  - タイムアウト設定とエラーハンドリングを追加

## [1.25.6] - 2025-12-11

### Fixed

- **Docker環境でのkomon initial問題を修正**
  - `settings.yml.sample`の検索ロジックを動的検出に変更
  - `komon.__file__`から実際のパッケージ場所を取得するように改善
  - 環境依存のハードコードされたパスを排除
  - Docker、仮想環境、標準環境すべてで動作するように修正

## [1.25.5] - 2025-12-11

### Fixed

- **パッケージング設定の修正**
  - `package_data` から `data_files` に変更して設定ファイルサンプルを正しく配置
  - `komon initial` コマンドが確実に動作するように改善

## [1.25.4] - 2025-12-11

### Fixed

- **パッケージング問題の修正**
  - pip インストール後に `config/settings.yml.sample` が含まれない問題を修正
  - `setup.py` に `package_data` を追加して設定ファイルサンプルを正しくパッケージに含める
  - `komon initial` コマンドが正常に動作するように改善

## [1.25.3] - 2025-01-22

### Fixed

- **CLI実行環境の不具合修正**
  - pip インストール後に `komon advise` が動作しない問題を修正
  - subprocess呼び出しから適切なモジュールインポートに変更
  - 設定ディレクトリの自動検出機能を追加（`KOMON_CONFIG_DIR` → カレントディレクトリ → `~/.komon/`）
  - どのディレクトリからでもkomonコマンドが実行可能に改善

### Changed

- **CLI構造の全面リファクタリング**
  - argparseベースの適切なCLI構造に変更
  - 全コマンドを `src/komon/commands/` モジュールに移行
  - `get_config_dir()` と `ensure_config_dir()` 関数による自動ディレクトリ管理

## [1.25.2] - 2025-01-22

### Fixed

- **ネットワークチェック状態管理のバグ修正**
  - `NetworkStateManager.check_state_change()`でKeyErrorが発生する問題を修正
  - 期限切れ状態のクリーンアップ後にキーが存在しない場合の処理を改善
  - テストのタイムスタンプを保持期間内の値に修正

## [1.25.1] - 2025-01-22

### Added

- **`komon --version` / `komon -v` コマンド**
  - インストールされているKomonのバージョンを表示
  - 出力例: `Komon version 1.25.1`
  - トラブルシューティング時やサポート報告時に便利

### Changed

- **`komon initial` コマンドの改善**
  - `config/settings.yml.sample` をベースに対話的に設定を作成
  - 各設定項目でデフォルト値を表示し、Enter押下で維持、入力で変更
  - ユーザーフレンドリーな出力（何を維持し、何を変更したかを表示）
  - 主要な設定項目のみプロンプト（Slack、Email、Network check、Throttle等）
  - 複雑な3段階閾値構造はデフォルト値を使用（必要に応じて手動編集）

### Fixed

- **`komon initial` の設定キー名を修正**
  - `notifications` (正) ← `notification` (誤)
  - `throttle` (正) ← `notification_throttle` (誤)
  - Emailフィールド名: `from`, `to` (正) ← `from_address`, `to_address` (誤)

### Documentation

- **コマンドリファレンスに `--version` を追加**
  - 新しい「基本コマンド」セクションを作成
  - 使用例、出力例、注意事項を記載
  - コマンド一覧表とFAQセクションを更新

## [1.25.0] - 2025-12-08

### Added

- **ネットワーク疎通チェック機能（ping/http）**
  - REST API実行前の事前条件確認や外部通信不可時の早期気づきのため、ネットワーク疎通の軽量チェック機能を追加
  - ping疎通チェック（ICMPエコー）
  - http疎通チェック（GET/HEAD/POSTメソッド対応）
  - 状態変化時のみ通知（正常→異常、異常→正常）
  - NG状態のretention（24時間で自動削除）
  - CLI引数で有効化（opt-in設計）
    - `--with-net`: 全部（リソース・ログ + ping + http）
    - `--net-only`: ネットワークチェックのみ
    - `--ping-only`: pingのみ
    - `--http-only`: httpのみ
  - デフォルト動作は従来通り（ネットワークチェックなし）
  - 設定ファイルで有効/無効、対象ホスト/URL、タイムアウトを設定可能

### New Modules

- `src/komon/net/__init__.py` - ネットワークチェックモジュール
- `src/komon/net/ping_check.py` - ping疎通チェック
- `src/komon/net/http_check.py` - http疎通チェック
- `src/komon/net/state_manager.py` - ネットワーク状態管理

### Configuration

- `settings.yml`に`network_check`セクションを追加
  - `enabled`: ネットワークチェックの有効/無効（デフォルト: false）
  - `ping.targets`: ping対象ホストのリスト
  - `http.targets`: http対象URLのリスト
  - `state.retention_hours`: NG状態の保持時間（デフォルト: 24時間）

### Changed

- `scripts/advise.py` - ネットワークチェックを統合
  - `advise_network_check()` 関数を追加
  - CLI引数（`--with-net`, `--net-only`, `--ping-only`, `--http-only`）を追加
  - `--section=network` オプションのサポートを追加

### Developer Improvements

- **テストの追加**
  - ユニットテスト: 35件（ping_check, http_check, state_manager）
  - 統合テスト: 8件（CLI引数、設定ファイル、通知ポリシー）
  - 全545テストがパス、カバレッジ92%を維持

### Benefits

- **事前条件確認**: REST API実行前にネットワーク疎通を確認
- **早期気づき**: 外部通信不可時に早期に気づける
- **軽量性**: Komonの「軽量」思想を維持（opt-in設計）
- **状態変化のみ通知**: 通知疲れを防止

## [1.24.2] - 2025-12-04

### Fixed

- **`komon` コマンドで引数が渡されない問題を修正**
  - `komon advise --section status` 等のコマンドライン引数が正しく渡されるように修正
  - `src/komon/cli.py` の `subprocess.run()` に `sys.argv[2:]` を追加
  - `python scripts/advise.py --section status` は動作していたが、`komon advise --section status` では引数が無視されていた問題を解消

## [1.24.1] - 2025-12-04

### Fixed

- **`--section` オプションが機能しない問題を修正**
  - `komon advise --section status` 等で特定セクションのみ表示できるように修正
  - 各セクション処理後に `return` を追加
  - 全セクションが表示されてしまうバグを解消

## [1.24.0] - 2025-12-03

### Added

- **OS判定・汎用Linux対応（マルチディストリビューション対応）**
  - OS自動判定機能の実装（rhel / debian / suse / arch / unknown）
  - `/etc/os-release` を読み取ってOSファミリを判定
  - Amazon Linux 2023 を rhel ファミリとして扱う
  - 設定ファイルで手動上書き可能（`system.os_family`）
  - Windows ネイティブでは即エラー終了
  - WSL では Linux 扱いで動作
  - OS別のアドバイス出し分け
    - RHEL系: `sudo dnf update --security`
    - Debian系: `sudo apt update && sudo apt upgrade`
    - unknown: 汎用的なアドバイス
  - Debian系でのパッケージ系アドバイス抑制
    - 理由: パッケージ名の違いによる誤アドバイスを防止
    - Komonの哲学「誤ったアドバイスをしない」に基づく設計
  - ログパスの自動切替
    - RHEL系: `/var/log/messages`
    - Debian系: `/var/log/syslog`
    - unknown: ログアドバイスを抑制

### Changed

- **ドキュメントの更新**
  - README.md に「RHEL系推奨」を明記
  - 対応プラットフォームセクションの追加
  - docs/RECOMMENDED_RUNTIME.md の大幅更新
    - ベストエフォート対応の詳細を追加
    - 各ディストリビューションでの制限事項を明記
    - 動作する機能と制限される機能を明確化

### Developer Improvements

- 新規モジュール: `src/komon/os_detection.py`
  - `OSDetector` クラスの実装
  - `detect_os_family()` 関数
  - `get_package_manager_command()` 関数
  - `get_log_path()` 関数
  - `should_show_package_advice()` 関数
  - `is_wsl()` 関数
  - `check_windows()` 関数
- ログ解析モジュールの拡張
  - `get_recommended_log_path()` 関数
  - `should_show_log_advice()` 関数
- テストの追加
  - プロパティベーステスト: 7件（OS判定ロジック）
  - ユニットテスト: 29件（OSDetectorクラス）
  - 統合テスト: 9件（OS別アドバイス、ログパス切替）
  - 全テストがパス
- カバレッジ維持

## [1.23.0] - 2025-12-02

### Changed

- **`komon advise` 出力フォーマットの改善**
  - 現在のシステム状態を最初に表示（CPU/メモリ/ディスク）
  - プログレスバーで視覚的に分かりやすく表示
  - 閾値も数値で明確に表示
  - 警告時は上位プロセスも自動表示
  - ノイズを削減（CPU/メモリ0.0%のプロセスを非表示）
  - 通知履歴のデフォルト表示件数を5件に変更
  - `--verbose` オプションで詳細表示が可能
  - `--section` オプションで特定セクションのみ表示が可能
  - 設定ファイルで出力フォーマットをカスタマイズ可能

- **新しいヘルパー関数の追加**
  - `generate_progress_bar()`: パーセンテージをプログレスバーに変換
  - `get_status_info()`: 値と閾値から状態情報を取得
  - `display_system_status()`: システム状態を表示

- **設定ファイルの拡張**
  - `output`セクションを追加
  - `default_mode`: デフォルトの表示モード（normal/verbose）
  - `history_limit`: 通知履歴のデフォルト表示件数
  - `show_zero_cpu`: CPU/メモリ0.0%のプロセスを表示するか

### Developer Improvements

- テストの追加: ユニットテスト17件（プログレスバー生成、状態判定）
- カバレッジ維持: 全436テストがパス

## [1.22.0] - 2025-12-01

### Added

- **長時間実行プロセスの検出機能**
  - 特定スクリプトが長時間実行されている場合に検出
  - スクリプト名、PID、実行時間を表示
  - 実行時間を人間に読みやすい形式で表示（例: 2時間30分）
  - 設定で検出閾値を調整可能（デフォルト: 3600秒 = 1時間）
  - 対象拡張子: .py, .sh, .rb, .pl

- **long_running_detector.pyモジュールの追加**
  - `detect_long_running_processes()`関数で長時間実行プロセスを検出
  - `_format_duration()`関数で実行時間を人間に読みやすい形式に変換
  - エラーハンドリング（プロセス終了、アクセス拒否）

- **advise.pyの拡張**
  - `advise_long_running_processes()`関数を追加
  - 長時間実行プロセスの警告メッセージを表示
  - 設定ファイルから閾値と対象拡張子を読み込み

- **設定ファイルの拡張**
  - `long_running_detection`セクションを追加
  - `enabled`, `threshold_seconds`, `target_extensions`を設定可能

### Developer Improvements

- テストの追加: プロパティテスト5件、統合テスト7件、ユニットテスト11件
- カバレッジ92%を維持（long_running_detector.py: 94%）

## [1.21.0] - 2025-11-30

### Added

- **ログ急増時の末尾抜粋表示機能**
  - ログ急増検出時に末尾N行を自動抽出（デフォルト: 10行）
  - 通知メッセージにコードブロック形式で表示
  - 設定で表示行数を変更可能（`log_analysis.tail_lines`、0で無効化）
  - 長い行は自動的に切り詰め（デフォルト: 500文字）
  - 大きなログファイルでも高速動作（末尾のみ読み込み）

- **log_tail_extractor.pyモジュールの追加**
  - `extract_log_tail()`関数でログ末尾を効率的に抽出
  - ファイルを末尾から読み込む高速アルゴリズム
  - エラーハンドリング（ファイル不在、権限エラー）

- **main_log_monitor.pyの拡張**
  - ログ急増通知に末尾抜粋を追加
  - 設定ファイルから`tail_lines`と`max_line_length`を読み込み
  - エラー時も通知を継続（末尾抜粋なし）

- **設定ファイルの拡張**
  - `log_analysis.tail_lines`: 末尾抜粋の行数（デフォルト: 10）
  - `log_analysis.max_line_length`: 1行あたりの最大文字数（デフォルト: 500）

### Developer Improvements

- テストの追加: プロパティテスト3件、統合テスト6件、ユニットテスト8件
- カバレッジ92%を維持

## [1.20.0] - 2025-11-29

### Added

- **多重実行プロセスの検出機能**
  - cronなどによる同一スクリプトの多重起動を検出
  - `komon advise`で警告を表示
  - 設定ファイルで検出閾値を調整可能（デフォルト: 3個以上）
  - スクリプト名、実行数、PIDリストを表示
  - cron間隔の見直しやロックファイル使用を推奨

- **duplicate_detector.pyモジュールの追加**
  - `detect_duplicate_processes()`関数で多重実行を検出
  - `_extract_script_name()`関数でスクリプト名を抽出
  - 対象拡張子: .py, .sh, .rb, .pl
  - エラーハンドリングとログ出力を実装

- **advise.pyの拡張**
  - `advise_duplicate_processes()`関数を追加
  - 多重実行プロセスの警告表示機能
  - 設定ファイルから閾値と有効/無効を読み込み

- **設定ファイルの拡張**
  - `duplicate_process_detection`セクションを追加
  - `enabled`: 機能の有効/無効（デフォルト: true）
  - `threshold`: 警告閾値（デフォルト: 3）
  - `target_extensions`: 対象拡張子リスト

### Developer Improvements

- **テストの追加**
  - ユニットテスト: 15件
  - 統合テスト: 7件
  - プロパティテスト: 5件
  - 全379テストがパス、カバレッジ93%を維持

## [1.19.0] - 2025-11-28

### Added

- **Slack通知にプロセス情報を含める機能**
  - CPU/メモリ超過時に上位3プロセスの情報を自動追加
  - プロセス名と使用率（CPU: %、メモリ: MB）を表示
  - ディスク使用率の場合はプロセス情報は表示しない（取得困難なため）
  - 既存の通知機能に影響なし、後方互換性を維持

- **main.pyの拡張**
  - `handle_alerts()`関数にプロセス情報追加ロジックを統合
  - `_get_process_info_for_metric()`関数を新規追加
  - CPU/メモリの上位3プロセス情報をフォーマット

### Developer Improvements

- **テストの追加**
  - プロセス情報付き通知のユニットテスト: 10件
  - プロセス情報付き通知の統合テスト: 3件
  - 全352テストがパス、カバレッジ93%を維持

## [1.18.1] - 2025-11-27

### Developer Improvements

- **リリースノート自動生成機能**
  - CHANGELOGから該当バージョンを抽出
  - GitHub Releases用にフォーマット
  - `.kiro/RELEASE_NOTES.md`の「登録待ちリリース」セクションに自動追記
  - `python scripts/generate_release_notes.py v1.X.X` で実行

- **ステータス整合性チェック機能**
  - 4つのファイルのステータス整合性を自動チェック
    - `.kiro/specs/future-ideas.md` - アイデアのステータス
    - `.kiro/tasks/implementation-tasks.md` - 実装タスクのステータス
    - `.kiro/specs/{feature-name}/tasks.yml` - Spec別タスクのステータス
    - `.kiro/tasks/completed-tasks.md` - 完了タスクのアーカイブ
  - リリース時の確認漏れを防止
  - CI/CDで自動実行（GitHub Actions）
  - `python scripts/check_status_consistency.py` で手動実行可能

- **開発ワークフローの改善**
  - リリース手順を明確化（CHANGELOGの更新手順を追加）
  - Kiroのチェックポイントを追加
  - ステータス整合性チェックをリリース手順に統合

- **テストの追加**
  - リリースノート生成のテスト: 12件
  - ステータス整合性チェックのテスト: 12件
  - 全339テストがパス、カバレッジ93%を維持

## [1.18.0] - 2025-11-27

### Added

- **コンテキスト型アドバイス機能**
  - 高負荷プロセスに対して、プロセスの種類に応じた具体的なアドバイスを提供
  - プロセス名から種類を自動判定（node、docker、python、nginx、mysql等）
  - 各プロセスに適した対処法を提案（開発サーバーの停止方法、コンテナ管理等）
  - 詳細度を3段階（minimal/normal/detailed）で切り替え可能
  - カスタムパターンで独自のアドバイスを追加可能
  - `komon advise`コマンドで高負荷プロセスの詳細情報とアドバイスを表示

### New Modules

- `src/komon/contextual_advisor.py` - コンテキスト型アドバイス生成ロジック
  - プロセス情報の取得と分析
  - パターンマッチングによるプロセス種類の判定
  - アドバイスメッセージの生成とフォーマット

### Configuration

- `settings.yml`に`contextual_advice`セクションを追加
  - `enabled`: コンテキスト型アドバイスの有効/無効
  - `advice_level`: 詳細度（minimal/normal/detailed）
  - `top_processes_count`: 表示するプロセス数（デフォルト: 3）
  - `patterns`: カスタムパターンの定義

### Changed

- `scripts/advise.py` - コンテキスト型アドバイスを統合
  - `advise_contextual()`関数を追加
  - CPU/メモリ使用率が高い場合に自動的にアドバイスを表示

### Developer Improvements

- **テストの追加**
  - プロパティベーステスト: 5件（hypothesis使用）
    - Property 1: プロセス情報取得の正確性
    - Property 2: パターンマッチングの一貫性
    - Property 3: メッセージフォーマットの完全性
    - Property 4: 詳細度レベルの正確性
    - Property 5: エラーハンドリングの堅牢性
  - ユニットテスト: 25件（各関数の動作確認）
  - 統合テスト: 11件（実際の使用シナリオ）
  - 全315テストがパス、カバレッジ93%を維持

- **Spec文書の作成**
  - `.kiro/specs/contextual-advice/`: 要件定義、設計書、実装タスク（YML形式）
  - 7つの要件と5つの正確性プロパティを定義

### Benefits

- **具体的な対処法**: プロセスの種類に応じた適切なアドバイス
- **学習コスト削減**: 初心者でも適切な対応が可能
- **カスタマイズ性**: 独自のパターンを追加して環境に合わせた運用が可能
- **段階的な情報提供**: 詳細度を切り替えて必要な情報のみ表示

## [1.17.1] - 2025-11-26

### Fixed

- **scripts/main.pyのImportError修正**
  - `validate_settings`関数が存在しないエラーを修正
  - 正しい関数名`validate_threshold_config`を使用
  - cronジョブでの大量エラー発生を解消

### Developer Improvements

- **スクリプトファイルのインポートテスト追加**
  - `tests/test_scripts_import.py`を追加
  - scripts/配下の全実行スクリプトのインポートを検証
  - 実行時まで発覚しないImportErrorを防止

- **ステアリングルールの拡充**
  - `development-workflow.md`にスクリプトテストのセクションを追加
  - テンプレートから生成される汎用的なルールとして記載
  - 全273テストがパス、カバレッジ93%を維持

## [1.17.0] - 2025-11-26

### Added

- **段階的通知メッセージ機能**
  - 同一問題の繰り返し回数に応じてメッセージが段階的に変化
  - 1回目: 「ちょっと気になることがあります」（穏やかな表現）
  - 2回目: 「まだ続いてますね」（継続を示唆）
  - 3回目以降: 「そろそろ見た方がいいかも」（行動を促す）
  - 通知履歴（v1.11.0）を活用し、過去24時間以内の通知回数を自動判定
  - CPU、メモリ、ディスクの各メトリクスで独立してカウント
  - 設定ファイルでカスタムテンプレートや時間窓を変更可能

### Changed

- **analyzer.pyの拡張**
  - `analyze_usage()`に`use_progressive`パラメータを追加
  - 段階的メッセージ機能の有効/無効を切り替え可能
  - デフォルトは無効（後方互換性を維持）

- **設定ファイルの拡張**
  - `config/settings.yml.sample`に`progressive_notification`セクションを追加
  - 時間窓（デフォルト: 24時間）とカスタムテンプレートを設定可能

### Developer Improvements

- **新規モジュールの追加**
  - `src/komon/progressive_message.py`: 段階的メッセージ生成ロジック
  - 通知回数の取得、メッセージ生成、エラーハンドリング

- **テストの追加**
  - プロパティベーステスト: 5件（通知回数の正確性、メッセージの一貫性等）
  - ユニットテスト: 19件（各関数の動作確認）
  - 統合テスト: 6件（実際の使用シナリオ）
  - 全268テストがパス、カバレッジ93%を維持

- **Spec文書の作成**
  - `.kiro/specs/progressive-notification/`: 要件定義、設計書、実装タスク

## [1.16.2] - 2025-11-25

### Changed

- **エラーメッセージの改善**
  - settings.yml不在時に具体的な対処法を表示
  - YAML形式エラー時に分かりやすいメッセージ
  - 4つのスクリプト（main.py, advise.py, weekly_report.py, main_log_monitor.py）を修正

- **ドキュメントの正直化**
  - クイックスタートの所要時間を「5分」→「10分」に修正
  - 前提条件を明記（Linux、Python 3.10+、Git）
  - Slack設定をオプション扱いに変更

### 開発者向け改善

- **Specテンプレートの追加**
  - 要件定義（requirements.md）、設計書（design.md）、実装タスク（tasks.md）のテンプレートを作成
  - テンプレート使用ガイド（`.kiro/specs/_templates/README.md`）を追加
  - 品質チェックリストを各テンプレートに含める

- **GitHub Actions CI/CDの導入**
  - `tests.yml`: コード変更時に全テスト実行（Python 3.10/3.11/3.12）
  - `spec-validation.yml`: Spec/ドキュメント更新時に自動検証
  - リンティング（black, isort, flake8）を統合

- **Spec検証スクリプトの追加**
  - `scripts/validate_specs.py`: Spec構造の検証（Front Matter、必須セクション、フォーマット）
  - `scripts/check_spec_consistency.py`: Spec間の一貫性チェック（要件とタスクのトレーサビリティ）
  - CI/CDで自動実行され、品質を保証

- **既存Specのテンプレート準拠**
  - disk-trend-prediction, notification-throttle, progressive-threshold, weekly-health-reportの4件を修正
  - Front Matterの追加、必須セクションの補完、正確性プロパティの形式統一

## [1.16.1] - 2025-11-25

### Changed

- **通知履歴の表示件数をデフォルト10件に制限**
  - `komon advise`コマンドで通知履歴が多すぎて見づらい問題を改善
  - デフォルトで直近10件のみ表示するように変更
  - `--history N` オプションで表示件数を変更可能
  - `--history 0` で全件表示も可能（従来の動作）

## [1.16.0] - 2025-11-25

### Added

- **ディスク使用量の増加トレンド予測機能**
  - 過去7日分のディスク使用率データから線形回帰により将来の使用量を予測
  - 90%到達予測日を算出（「あとN日で90%に到達」）
  - 前日比10%以上の急激な増加を検出し、早期警告を発する
  - `komon advise`コマンドで予測結果を表示
  - 週次レポートにも予測結果を自動的に含める
  - 新規モジュール: `src/komon/disk_predictor.py`

### Changed

- `scripts/advise.py` - `advise_disk_prediction()`関数を追加
- `src/komon/weekly_data.py` - `collect_weekly_data()`にディスク予測を統合
- `src/komon/report_formatter.py` - `format_disk_prediction()`関数を追加
- `README.md` - ディスク使用量予測機能の説明を追加

### Developer Improvements

- **テストの追加**
  - プロパティベーステスト8件（hypothesis使用、各100回実行）
    - Property 1: 日次平均計算の正確性
    - Property 2: 欠損データの処理
    - Property 3: 線形回帰の正確性
    - Property 4: 90%到達予測の正確性
    - Property 5: 前日比計算の正確性
    - Property 6: 急激な変化検出の正確性
    - Property 7: 予測メッセージの完全性
    - Property 8: 警告の優先度順表示
  - ユニットテスト17件
  - 統合テスト5件
  - 全30テストが成功（既存208テスト + 新規30テスト = 合計238テスト）
  - カバレッジ94%を維持

### Benefits

- **事前の計画的な対応**: ディスクが逼迫する前に対応できる
- **急激な変化の早期検知**: 84%から90%に一気にジャンプするケースに対応
- **具体的な情報**: 「あと○日で危険」という明確な予測

### Requirements Validated

- 要件1: 過去データの取得と処理（受入基準1.1〜1.5）
- 要件2: 線形回帰による予測計算（受入基準2.1〜2.5）
- 要件3: 急激な変化の検出（受入基準3.1〜3.5）
- 要件4: 予測メッセージの生成（受入基準4.1〜4.5）
- 要件5: adviseコマンドへの統合（受入基準5.1〜5.5）
- 要件6: 週次レポートへの統合（受入基準6.1〜6.5）
- 要件7: テストによる検証（受入基準7.1〜7.5）

## [1.15.0] - 2025-11-24

### Added

- **通知頻度制御機能（同一アラートの抑制）**
  - 同一メトリクスの通知を設定間隔で抑制（デフォルト: 60分）
  - 閾値レベルが上昇した場合は即座に通知（警告→警戒、警戒→緊急）
  - 長時間継続する問題の再通知（エスカレーション、デフォルト: 180分）
  - 通知履歴を`data/notifications/throttle.json`に保存
  - `settings.yml`で有効/無効、通知間隔、再通知間隔を設定可能

### Changed

- `src/komon/notification.py` - NotificationThrottleクラスを追加
- `src/komon/analyzer.py` - analyze_usage_with_levels()関数を追加（閾値レベル情報を返す）
- `scripts/main.py` - 通知頻度制御を統合
- `settings.yml` - throttle設定セクションを追加
- `config/settings.yml.sample` - throttle設定の説明を追加
- `README.md` - 通知頻度制御の説明を追加

### Developer Improvements

- **テストの追加**
  - プロパティベーステスト4件（hypothesis使用）
  - ユニットテスト15件
  - 統合テスト8件
  - 全189テストが成功
  - カバレッジ維持

### Benefits

- **通知疲れの防止**: 同じ内容の通知が繰り返されることを防ぐ
- **重要な通知を見逃さない**: 状況が悪化した場合は即座に通知
- **長期問題の可視化**: 3時間継続する問題は再通知で注意喚起

## [1.14.0] - 2025-11-23

### Added

- **環境変数対応の強化（セキュリティ機能）**
  - Slack Webhook URLの環境変数読み込み機能を追加
  - `webhook_url: "env:KOMON_SLACK_WEBHOOK"` 形式をサポート
  - メールパスワードと同様の仕組みで認証情報を保護
  - 認証情報のGitコミット漏洩リスクを低減

### Security

- **セキュリティドキュメントの大幅拡充**
  - `docs/SECURITY.md` を実用的な内容に拡充（約10倍のボリューム）
  - 認証情報の管理方法を詳細に記載（環境変数の使い方）
  - ファイルパーミッション設定のベストプラクティス
  - cron実行時のセキュリティガイド
  - ログファイルアクセス権限の設定方法
  - 依存パッケージの管理とセキュリティスキャン
  - セキュリティチェックリストの追加
  - 定期メンテナンスガイドの追加（月次・四半期・年次）

### Changed

- `src/komon/notification.py` - Slack Webhook URLの環境変数対応を追加
- `config/settings.yml.sample` - 環境変数の使い方を明記
- `README.md` - セキュリティガイドへのリンクを追加

### Fixed

- **advise.pyの型エラー修正**
  - `advise_resource_usage`関数で3段階閾値形式に対応
  - `thresholds`が辞書型の場合に`warning`値を使用するように修正
  - 従来の単一値形式との後方互換性を維持

### Developer Improvements

- **テストの追加**
  - 環境変数読み込みのテスト2件を追加
  - 全162テストが成功
  - カバレッジ維持

## [1.13.0] - 2025-11-23

### Added

- **3段階閾値通知システム**
  - リソース使用率の閾値を3段階（警告/警戒/緊急）で設定可能に
  - 各レベルに応じた絵文字とメッセージを表示
    - 💛 警告（warning）: そろそろ気にかけておいた方がいいかも
    - 🧡 警戒（alert）: ちょっと気になる水準です
    - ❤️ 緊急（critical）: かなり逼迫しています！
  - 段階的な通知で早期警戒と適切な対応が可能に
  - 従来の単一閾値設定との完全な後方互換性を維持

### New Modules

- `src/komon/settings_validator.py` - 閾値設定の検証と正規化

### Configuration

- `settings.yml`の`thresholds`セクションを拡張
  - 3段階形式: `{warning: 70, alert: 80, critical: 90}`
  - 従来の単一値形式も引き続きサポート
  - 単一値は自動的に3段階形式に変換される

### Changed

- `src/komon/analyzer.py` - 3段階判定ロジックに対応
- `config/settings.yml.sample` - 3段階閾値の設定例を追加

### Developer Improvements

- **テストの追加**
  - プロパティベーステスト3件（hypothesis）
  - ユニットテスト12件
  - 統合テスト8件
  - 全160テストが成功
  - カバレッジ93%を維持

### Documentation

- README.mdに3段階閾値の説明を追加
- 設定例と移行ガイドを追加
- 3段階閾値のメリットを説明

## [1.12.0] - 2025-11-22

### Added

- **週次健全性レポート機能**
  - 毎週定期的にシステムの健全性レポートをSlack/メールで送信
  - CPU/メモリ/ディスク使用率の現状と先週比を表示
  - 過去7日間の警戒情報サマリーを含む
  - トレンド分析（安定/増加傾向/減少傾向）を表示
  - SSHログインせずにシステム状態を確認可能
  - 年末年始などの長期休暇前の健全性確認に最適

### New Modules

- `src/komon/weekly_data.py` - 週次データ収集と分析
- `src/komon/report_formatter.py` - レポートメッセージフォーマット
- `scripts/weekly_report.py` - 週次レポート生成スクリプト

### Configuration

- `settings.yml`に`weekly_report`セクションを追加
  - `enabled`: 週次レポートの有効/無効
  - `day_of_week`: レポート送信曜日（0=日曜, 1=月曜, ...）
  - `hour`, `minute`: レポート送信時刻
  - `notifications`: Slack/メール通知の個別設定

### Developer Improvements

- **テストの追加**
  - プロパティベーステスト6件（hypothesis）
  - ユニットテスト26件
  - 統合テスト6件
  - 全150テストが成功
  - カバレッジ92%を維持

### Documentation

- README.mdに週次レポートの使い方を追加
- cron設定例を追加（毎週月曜9時）
- プロジェクト構造に新モジュールを追加

## [1.11.2] - 2025-11-22

### Fixed

- **ログ傾向分析のバグ修正**
  - `log_trends.py`でデータ型エラーが発生していた問題を修正
  - state_dataが辞書形式の場合に`last_line`を正しく取得するように改善
  - `TypeError: unsupported operand type(s) for -: 'dict' and 'dict'` を解消
  - 後方互換性を保ちつつ、数値形式にも対応

## [1.11.1] - 2025-11-22

### Fixed

- **テストの安定性向上**
  - プロパティベーステストのデッドライン設定を修正
  - `test_limit_returns_correct_number`の実行時間制限を解除（`deadline=None`）
  - 全111テストが安定してパスするように改善

## [1.11.0] - 2025-11-22

### Added

- **通知履歴機能**
  - ローカルファイルに通知履歴を自動保存（最大100件、自動ローテーション）
  - `komon advise`コマンドで履歴を表示
  - `komon advise --history N`で直近N件のみ表示
  - Slack/メール通知が使えない環境でも検知情報を確認可能
  - 通知履歴は`notifications/queue.json`に保存

### Developer Improvements

- **テストの追加**
  - プロパティベーステスト（hypothesis）を導入
  - 通知履歴機能のテスト18件を追加（プロパティテスト7件、統合テスト6件、ユニットテスト5件）
  - 全111テストが成功
  - 6つの正確性プロパティを検証

### Documentation

- **プロジェクト管理構造の追加**
  - `.kiro/tasks/`フォルダを新設し、実装タスク管理を開始
  - `implementation-tasks.md`: future-ideasから実装タスクを分解・管理
  - README.md、PROJECT_STRUCTURE.md、docs/README.mdのディレクトリ構造を更新
  - 仕様管理（specs）とタスク管理（tasks）を明確に分離
- **Spec駆動開発**
  - `.kiro/specs/notification-history/`に要件定義、設計、タスクリストを作成
  - EARS形式の要件定義、正確性プロパティを含む設計書を整備

## [1.10.1] - 2025-11-22

### Changed

- **通知メッセージの改善**
  - 機械的な警告表現から、やさしい相談口調に変更
  - 「CPU使用率が高い状態です」→「CPUが頑張りすぎてるみたいです」
  - 「メモリ使用率が高い状態です」→「メモリ使用量が結構増えてますね」
  - 「ディスク使用率が高い状態です」→「ディスクの空きが少なくなってきました」
  - Komonの「やさしく見守る顧問」という思想をより明確に

### Developer Improvements

- **テストカバレッジの大幅向上**
  - テストカバレッジ: 47% → 95%（+48%）
  - テスト数: 46 → 93（+47テスト）
  - 新規テストファイル追加:
    - `tests/test_notification.py`: Slack/メール通知のテスト（9テスト）
    - `tests/test_log_watcher.py`: ログ監視機能のテスト（11テスト）
    - `tests/test_log_trends.py`: ログ傾向分析のテスト（17テスト）
    - `tests/test_cli.py`: CLIエントリーポイントのテスト（10テスト）

- **カバレッジ測定の改善**
  - CIFS/SMB共有環境でのSQLiteロック問題を修正
  - `.coveragerc`の追加（ローカルディスクへのデータ保存設定）
  - `run_coverage.sh`: カバレッジレポート生成スクリプトの追加
  - `setup_coverage_fix.sh`: カバレッジ設定の自動修正スクリプト

- **開発ツールの追加**
  - `check_coverage.py`: 簡易カバレッジチェックツール（coverageツール不要）

### Notes

- これらの改善は開発者向けで、エンドユーザーの機能には影響しません
- 全93テストがパス、本番環境での信頼性が向上しました

## [1.10.0] - 2025-11-21

### Changed

- **プロジェクト構造の大幅な整理**
  - `src/komon/`にコアモジュールを移動
  - `scripts/`に実行スクリプトを移動
  - `docs/`にドキュメントを集約
  - 標準的なPythonプロジェクト構造に準拠

### Added

- **テストコードの追加**
  - `test_analyzer.py`: 閾値判定とアラート生成のテスト（10個）
  - `test_log_analyzer.py`: ログ異常検知のテスト（6個）
  - `test_monitor.py`: リソース監視のテスト（7個、例外処理含む）
  - `test_history.py`: 履歴管理のテスト（9個）
  - `test_settings_validator.py`: 設定検証のテスト（14個）
  - `pytest.ini`: テスト設定ファイル（JUnit XMLレポート自動生成）
  - `requirements-dev.txt`: 開発用依存パッケージ
  - 全46個のテストが実装され、全てPASS
  - テストカバレッジ: コアモジュール5/9（約56%）

- **仕様駆動開発の基盤**
  - `.kiro/specs/komon-system.md`: 包括的なシステム仕様書
  - `.kiro/specs/testing-strategy.md`: テスト戦略と方針の文書化
  - `.kiro/specs/future-ideas.md`: 将来的な機能アイデア
  - リバースエンジニアリングにより既存コードから仕様を抽出

- **ドキュメントの充実**
  - `docs/PROJECT_STRUCTURE.md`: プロジェクト構造の詳細説明
  - `docs/CONTRIBUTING.md`: 貢献ガイドライン
  - `tests/README.md`: テストガイド
  - Linux専用方針の明確化

- **開発環境の改善**
  - `.gitignore`の更新（機密情報の保護強化）
  - `setup.py`の改善（新構造対応）

### Fixed

- なし（機能的な変更なし）

### Notes

- この更新は内部構造の整理が主で、既存機能は全て動作します
- `settings.yml`の場所や使い方に変更はありません
- `komon`コマンドは引き続き使用できます

---

## [1.9.0] - 2025-XX-XX

### Added

- 初期バージョン（詳細は過去のコミット履歴を参照）

---

## バージョニングポリシー

- **MAJOR**: 後方互換性のない変更
- **MINOR**: 後方互換性のある機能追加、大規模なリファクタリング
- **PATCH**: バグ修正、小規模な改善

## リンク

- [1.11.2]: https://github.com/kamonabe/Komon/releases/tag/v1.11.2
- [1.11.1]: https://github.com/kamonabe/Komon/releases/tag/v1.11.1
- [1.11.0]: https://github.com/kamonabe/Komon/releases/tag/v1.11.0
- [1.10.1]: https://github.com/kamonabe/Komon/releases/tag/v1.10.1
- [1.10.0]: https://github.com/kamonabe/Komon/releases/tag/v1.10.0
- [1.9.0]: https://github.com/kamonabe/Komon/releases/tag/v1.9.0
