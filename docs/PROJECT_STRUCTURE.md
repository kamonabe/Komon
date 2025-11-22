# Komonプロジェクト構造

このドキュメントでは、Komonプロジェクトのディレクトリ構造とファイル配置について説明します。

## ディレクトリ構造

```
Komon/
├── src/komon/              # コアモジュール（Pythonパッケージ）
├── scripts/                # 実行スクリプト
├── config/                 # 設定ファイルのサンプル
├── docs/                   # ドキュメント
├── tests/                  # テストコード
├── data/                   # 実行時データ（自動生成）
├── log/                    # ログファイル（自動生成）
└── .kiro/                  # Kiro IDE設定
```

## 各ディレクトリの詳細

### src/komon/

Komonのコアロジックを含むPythonパッケージです。

- `__init__.py`: パッケージ初期化
- `monitor.py`: リソース監視機能
- `analyzer.py`: データ分析・閾値判定
- `notification.py`: 通知機能（Slack/メール）
- `notification_history.py`: 通知履歴管理
- `history.py`: 履歴管理
- `log_watcher.py`: ログファイル監視
- `log_analyzer.py`: ログ異常検知
- `log_trends.py`: ログ傾向分析
- `settings_validator.py`: 設定ファイル検証
- `cli.py`: CLIエントリーポイント

### scripts/

実行可能なスクリプトファイルです。

- `main.py`: リソース監視のメインスクリプト
- `main_log_monitor.py`: ログ急増監視
- `main_log_trend.py`: ログ傾向分析
- `advise.py`: 対話型アドバイザー
- `initial.py`: 初期設定ウィザード
- `status.py`: ステータス表示
- `komon_guide.py`: ガイドメニュー
- `init.sh`: 初期化シェルスクリプト

### config/

設定ファイルのサンプルを格納します。

- `settings.yml.sample`: 設定ファイルのサンプル

実際の`settings.yml`はプロジェクトルートに配置します。

### docs/

プロジェクトのドキュメントを格納します。

- `README.md`: 詳細なドキュメント
- `CHANGELOG.md`: 変更履歴
- `SECURITY.md`: セキュリティ情報
- `PROJECT_STRUCTURE.md`: このファイル

### tests/

テストコードを格納します。

```
tests/
├── conftest.py                              # pytest設定
├── test_monitor.py                          # リソース監視テスト
├── test_analyzer.py                         # 分析機能テスト
├── test_notification.py                     # 通知機能テスト
├── test_notification_history_properties.py  # 通知履歴プロパティテスト
├── test_notification_integration.py         # 通知統合テスト
├── test_history.py                          # 履歴管理テスト
├── test_log_watcher.py                      # ログ監視テスト
├── test_log_analyzer.py                     # ログ分析テスト
├── test_log_trends.py                       # ログ傾向分析テスト
├── test_settings_validator.py               # 設定検証テスト
├── test_cli.py                              # CLIテスト
├── test_advise_command.py                   # adviseコマンドテスト
└── README.md                                # テストドキュメント
```

**テストカバレッジ: 95%**（111テスト、全てパス）

### data/

実行時に自動生成されるデータディレクトリです。

```
data/
├── usage_history/          # リソース使用履歴（CSV）
│   ├── usage_20251121_120000.csv
│   └── ...
└── logstats/               # ログ統計データ
    ├── var_log_messages.pkl
    ├── systemd_journal.pkl
    └── history/
        ├── var_log_messages.json
        └── systemd_journal.json
```

### log/

ログファイルを格納します（自動生成）。

```
log/
├── komon_error.log         # エラーログ
├── cron_main.log           # cron実行ログ
├── cron_monitor.log
└── cron_trend.log
```

### .kiro/

Kiro IDE用の設定とspecファイルを格納します。

```
.kiro/
├── specs/                      # 仕様書
│   ├── komon-system.md         # システム仕様書
│   ├── future-ideas.md         # 将来の改善案
│   ├── testing-strategy.md     # テスト戦略
│   └── notification-history/   # 通知履歴機能spec
│       ├── requirements.md
│       ├── design.md
│       └── tasks.md
├── tasks/                      # タスク管理
│   └── implementation-tasks.md # 実装タスクリスト
└── steering/                   # ステアリングルール
    ├── task-management.md
    ├── development-workflow.md
    └── environment-and-communication.md
```

## ファイル配置の原則

### 1. コアロジックとスクリプトの分離

- **コアロジック**: `src/komon/`に配置
  - 再利用可能な関数・クラス
  - ビジネスロジック
  - ユニットテスト可能な単位

- **実行スクリプト**: `scripts/`に配置
  - エントリーポイント
  - コマンドライン引数の処理
  - コアモジュールの呼び出し

### 2. 設定とデータの分離

- **設定**: `config/`にサンプル、ルートに実ファイル
- **データ**: `data/`に自動生成
- **ログ**: `log/`に自動生成

### 3. ドキュメントの集約

すべてのドキュメントは`docs/`に集約します。

## インポートパス

### src/komon/からのインポート

```python
from komon.monitor import collect_resource_usage
from komon.analyzer import analyze_usage
from komon.notification import send_slack_alert
```

### scripts/からの実行

scriptsフォルダのファイルは、プロジェクトルートから実行されることを想定しています。

```bash
# プロジェクトルートから実行
cd /path/to/Komon
python scripts/main.py
```

または、Pythonパスを設定：

```bash
export PYTHONPATH=/path/to/Komon/src:$PYTHONPATH
python scripts/main.py
```

### インストール後

`pip install -e .`でインストールすると、`komon`コマンドが使えるようになります。

```bash
komon initial
komon status
komon advise
```

## 開発ワークフロー

### 1. 新機能の追加

1. `.kiro/specs/komon-system.md`に仕様を追記
2. `src/komon/`に新しいモジュールを作成
3. `tests/`にテストを追加
4. `scripts/`に実行スクリプトを追加（必要に応じて）
5. `docs/README.md`にドキュメントを追記

### 2. バグ修正

1. `tests/`に再現テストを追加
2. `src/komon/`のコードを修正
3. テストが通ることを確認
4. `docs/CHANGELOG.md`に記録

### 3. リリース

1. `version.txt`を更新
2. `docs/CHANGELOG.md`を更新
3. タグを作成してプッシュ

## まとめ

この構造により、以下のメリットがあります：

- **保守性**: コアロジックとスクリプトが分離され、変更が容易
- **テスト性**: モジュール単位でテスト可能
- **拡張性**: 新機能の追加が明確な場所に配置できる
- **可読性**: ファイルの役割が明確で、新規参加者も理解しやすい
- **仕様駆動**: specファイルを中心とした開発が可能
