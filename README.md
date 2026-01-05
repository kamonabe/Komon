# Komon（顧問）

[![PyPI version](https://img.shields.io/pypi/v/komon.svg)](https://pypi.org/project/komon/)
[![PyPI downloads](https://img.shields.io/pypi/dm/komon)](https://pypi.org/project/komon/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/kamonabe/Komon/workflows/Tests/badge.svg)](https://github.com/kamonabe/Komon/actions/workflows/tests.yml)
[![Spec Validation](https://github.com/kamonabe/Komon/workflows/Spec%20and%20Documentation%20Validation/badge.svg)](https://github.com/kamonabe/Komon/actions/workflows/spec-validation.yml)
[![Test Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)](htmlcov/index.html)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)](https://www.linux.org/)

---

## 🌏 Language / 言語

- **[日本語版](#日本語版)** ⬇️ このまま下にスクロール
- **[English Version](#english-version)** ⬇️ Scroll down to English section

---

# 日本語版

**Komon は、開発者のための軽量アドバイザー型SOARツールです。**

開発環境で発生するリソースの過剰使用、ログの急増、更新忘れなどを静かに見守り、必要なときだけやさしく通知・提案してくれます。

🛠 Komon は内部構造がシンプルなため、通知手段の追加や監視項目の拡張が容易です。

---

## 📖 目次

- [このような結果が得られます](#-このような結果が得られます)
- [なぜKomonなのか？](#-なぜkomonなのか)
- [他の監視ツールとの関係](#-他の監視ツールとの関係)
- [プロジェクト構造](#-プロジェクト構造)
- [クイックスタート](#-クイックスタート所要時間-約5分)
- [コマンドリファレンス](#-コマンドリファレンス)
- [設定](#️-設定)
- [定期実行](#-定期実行cron)
- [ドキュメント](#-ドキュメント)
- [開発](#-開発)
- [対応プラットフォーム](#-対応プラットフォーム)
- [FAQ](#-faq)
- [コントリビューション](#-コントリビューション)
- [ライセンス](#-ライセンス)

---

## 🎯 このような結果が得られます

`komon advise` コマンドを実行すると、システムの状態を分析して対話的に改善提案を行います：

```bash
$ python scripts/advise.py

📊 現在のシステム状態
CPU:     [█░░░░░░░░░] 12.3% / 80% ✅
メモリ:  [████░░░░░░] 45.2% / 85% ✅
ディスク: [███████░░░] 67.8% / 90% ✅

🔔 警戒情報
（なし）

💡 改善提案

① セキュリティパッチの確認
→ セキュリティ更新はありません。

② システムパッチ（セキュリティ以外）の確認
→ セキュリティ以外の更新が 384 件あります。例：
   - NetworkManager.x86_64               1:1.54.0-3.el9_7                                 baseos    
   - NetworkManager-libnm.x86_64         1:1.54.0-3.el9_7                                 baseos    
   - NetworkManager-team.x86_64          1:1.54.0-3.el9_7                                 baseos    
   ...

💡 以下のコマンドでこれらをまとめて適用できます：
   sudo dnf upgrade -y

🔄 多重実行プロセスの検出
→ 多重実行プロセスは検出されませんでした。

⏱️  長時間実行プロセスの検出
⚠️ 以下のスクリプトが長時間実行されています：

  • shellIntegration-bash.sh (PID: 12345)
    実行時間: 1時間2分

【推奨対応】
  - スクリプトが正常に動作しているか確認してください
  - cron間隔がスクリプトの実行時間より短い場合は見直してください
  - 必要に応じてプロセスを停止してください

📜 通知履歴（最新5件）
💿 [2025-11-22 12:51:44] DISK: 96.7% - 警戒
📊 [2025-11-22 12:51:44] MEMORY: 91.3% - 警戒
🔥 [2025-11-22 12:51:44] CPU: 88.5% - 警戒

詳細: komon advise --verbose
```

**新機能（v1.23.0〜）**:
- 現在のシステム状態を最初に表示（プログレスバー付き）
- 視覚的に分かりやすい表示
- ノイズを削減（0.0%のプロセスを非表示）
- 通知履歴のデフォルト表示件数を5件に変更
- `--verbose` オプションで詳細表示
- `--section` オプションで特定セクションのみ表示

**コンテキスト型アドバイス（v1.18.0〜）**:
高負荷プロセスが検出された場合、プロセスの種類に応じた具体的なアドバイスを表示します。

```bash
【CPU使用率が高い場合】
1. node (PID: 12345) - CPU: 45.0%, メモリ: 30.0%
   💡 開発サーバーやビルドプロセスの可能性があります
   
2. docker (PID: 23456) - CPU: 35.0%, メモリ: 25.0%
   💡 コンテナが高負荷です。不要なコンテナを停止してみてください
   
3. python (PID: 34567) - CPU: 25.0%, メモリ: 20.0%
   💡 機械学習の学習プロセスやデータ処理スクリプトの可能性があります

📜 通知履歴
📊 [2025-11-22 21:01:28] MEM: 85.0 - Test alert
📋 [2025-11-22 21:01:27] LOG: 1000.0 - Test email alert
💾 [2025-11-22 20:59:08] MEM: 85.0 - Test alert
```

リソース使用率が閾値を超えた場合は、以下のようなやさしい通知が届きます：

```
💬 ちょっと気になることがあります

CPUが頑張りすぎてるみたいです（92.3%）。
何か重い処理走ってます？
```

これらの通知は、Slackやメールで受け取ることも可能です。また、通知履歴として自動的に保存され、後から `komon advise --history` で確認できます。

### 段階的通知メッセージ（v1.17.0〜）

同じ問題が繰り返し発生した場合、通知メッセージが段階的に変化します：

- **1回目**: 「ちょっと気になることがあります」（穏やかな表現）
- **2回目**: 「まだ続いてますね」（継続を示唆）
- **3回目以降**: 「そろそろ見た方がいいかも」（行動を促す）

これにより、問題の緊急度を適切に把握でき、「通知疲れ」を防ぎます。

---

## 🤔 なぜKomonなのか？

既存の監視ツール（Prometheus、Zabbix、Nagios等）と比較して：

- **軽量**: 依存関係が少なく、すぐに導入できる
- **開発者フレンドリー**: 開発環境での使用を想定した設計
- **やさしい通知**: 技術的すぎない、人間らしい表現
- **拡張しやすい**: Pythonで書かれており、カスタマイズが容易
- **段階的な警告**: 3段階閾値で通知疲れを防止

Komonは、大規模な監視システムではなく、**個人開発者や小規模チーム向けの軽量アドバイザー**です。

---

## 🤝 他の監視ツールとの関係

Komonは軽量（メモリ使用量: 約30MB）なので、ZabbixやPrometheusなどの既存監視ツールと**併用しても問題ありません**。

本番環境では大規模な監視システムが必須になってきますが、開発者向けに別途Komonを入れることで、より小回りの利いた監視をプラスすることも可能です。

### 併用する場合の例

- **Zabbix/Prometheus**: インフラ全体の監視、SLA保証
- **Komon**: 開発者個人の「気づき」、プロセス単位の細かい監視

大規模監視では拾いきれない「開発者目線の気づき」を、Komonの「やさしい通知」で受け取る、といった使い方ができます。

もちろん、小規模環境や開発サーバーでの**Komon単体**の利用も想定しています。

### 併用時の注意点

本番環境で既存の監視ツールと併用する場合は、事前に十分なテストを行ってください。特に以下の点を確認することをおすすめします：

- リソース使用量の影響（CPU、メモリ、ディスクI/O）
- ログ出力の重複や競合
- 通知の重複（同じ事象で複数のツールから通知が来ないか）
- cron実行タイミングの調整

---

## 📁 プロジェクト構造

```
Komon/
├── src/komon/                      # コアモジュール
│   ├── monitor.py                  # リソース監視
│   ├── analyzer.py                 # 閾値判定・分析
│   ├── contextual_advisor.py       # コンテキスト型アドバイス
│   ├── notification.py             # 通知機能
│   ├── notification_history.py     # 通知履歴管理
│   ├── history.py                  # 履歴管理
│   ├── log_watcher.py              # ログ監視
│   ├── log_analyzer.py             # ログ分析
│   ├── log_trends.py               # ログ傾向分析
│   ├── weekly_data.py              # 週次データ収集
│   ├── report_formatter.py         # レポートフォーマット
│   ├── settings_validator.py       # 設定検証
│   └── cli.py                      # CLIエントリーポイント
├── scripts/                        # 実行スクリプト
│   ├── main.py                     # リソース監視メイン
│   ├── main_log_monitor.py         # ログ急増監視
│   ├── main_log_trend.py           # ログ傾向分析
│   ├── weekly_report.py            # 週次健全性レポート
│   ├── advise.py                   # 対話型アドバイザー
│   ├── initial.py                  # 初期設定
│   ├── status.py                   # ステータス表示
│   ├── komon_guide.py              # ガイドメニュー
│   ├── check_coverage.py           # カバレッジ分析
│   ├── setup_coverage_fix.sh       # カバレッジ設定修正
│   ├── generate_release_notes.py   # リリースノート自動生成
│   ├── check_status_consistency.py # ステータス整合性チェック
│   └── init.sh                     # 初期化スクリプト
├── config/                         # 設定ファイル
│   └── settings.yml.sample         # 設定サンプル
├── docs/                           # ドキュメント
│   ├── README.md                   # 詳細ドキュメント
│   ├── CHANGELOG.md                # 変更履歴
│   └── SECURITY.md                 # セキュリティ情報
├── tests/                          # テストコード（92%カバレッジ）
├── data/                           # データ保存先（自動生成）
│   ├── usage_history/              # リソース使用履歴
│   ├── notifications/              # 通知履歴
│   ├── komon_data/                 # Komon内部データ
│   └── logstats/                   # ログ統計データ
├── .kiro/                          # Kiro IDE設定
│   ├── specs/                      # 仕様書
│   │   ├── komon-system.md         # システム仕様
│   │   ├── future-ideas.md         # 未実装アイデア
│   │   ├── implemented-ideas.md    # 実装済みアイデア
│   │   ├── research-projects.md    # 研究プロジェクト
│   │   ├── rejected-ideas.md       # 見送りアイデア
│   │   ├── testing-strategy.md     # テスト戦略
│   │   └── notification-history/   # 通知履歴機能spec
│   ├── tasks/                      # タスク管理
│   │   ├── implementation-tasks.md # 実装タスクリスト（進行中・未着手）
│   │   └── completed-tasks.md      # 完了タスクアーカイブ
│   └── steering/                   # 開発ルール
│       ├── task-management.md
│       ├── development-workflow.md
│       └── environment-and-communication.md
├── requirements.txt                # Python依存パッケージ
├── setup.py                        # インストール設定
├── LICENSE                         # ライセンス
└── version.txt                     # バージョン情報
```

---

## 🚀 クイックスタート（所要時間: 約5分）

### 前提条件
- Linux環境（AlmaLinux 9推奨）
- Python 3.10以上

### 1. インストール

```bash
# PyPIからインストール（推奨）
pip install komon

# または開発版（GitHub）
git clone https://github.com/kamonabe/Komon.git
cd Komon
pip install -e .
```

### 2. 初期設定（5分）

```bash
# 初期設定ウィザードを実行
python scripts/initial.py

# または（インストール済みの場合）
komon initial
```

### 3. 動作確認（1分）

```bash
# 対話型アドバイザー
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

# または、スクリプトから直接実行
python scripts/main.py      # リソース監視
python scripts/status.py    # ステータス確認
python scripts/advise.py    # 対話型アドバイザー
python scripts/weekly_report.py  # 週次健全性レポート
```

### 通知設定（オプション）

Komonは複数の通知方式に対応しています：

#### 🆕 統一Webhook通知（v1.26.0〜）- 推奨

複数の通知サービスを統一されたインターフェースで管理できます：

```yaml
# settings.yml
notifiers:
  webhooks:
    - name: "slack"
      url: "env:KOMON_SLACK_WEBHOOK"
      kind: "slack"
      enabled: true
    
    - name: "discord"
      url: "env:KOMON_DISCORD_WEBHOOK"
      kind: "discord"
      enabled: false
    
    - name: "teams"
      url: "env:KOMON_TEAMS_WEBHOOK"
      kind: "teams"
      enabled: false
```

**メリット**:
- 複数サービスの一元管理
- サービス別の最適化されたメッセージフォーマット
- 新しい通知サービスの追加が容易
- 旧形式との完全な互換性（フォールバック機能）

#### 個別通知設定（従来形式）

旧形式も引き続きサポートされています：

**Slack通知**
1. [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)にアクセス
2. "Create New App" → "Incoming Webhooks"を選択
3. URLをコピーして`settings.yml`の`notifications.slack.webhook_url`に設定

**Discord通知（v1.26.0〜）**
1. Discordサーバーの設定 → 連携サービス → ウェブフック
2. "ウェブフックを作成"をクリック
3. URLをコピーして`settings.yml`の`notifications.discord.webhook_url`に設定

**Microsoft Teams通知（v1.26.0〜）**
1. Teamsチャンネルの設定 → コネクタ → Incoming Webhook
2. "構成"をクリックしてWebhookを作成
3. URLをコピーして`settings.yml`の`notifications.teams.webhook_url`に設定

**注意**: 通知は必須ではありません。通知なしでも`komon advise`コマンドで状態確認できます。

### 主な機能

#### 🌐 ネットワーク疎通チェック（v1.25.0〜）

外部サービスやAPIへの疎通を定期的に確認し、接続障害を早期検知します。

**特徴**:
- Pingチェック（ICMP）とHTTPチェック（GET/POST）に対応
- 複数のターゲットを同時監視
- 状態変化時のみ通知（正常→異常、異常→正常）
- 通知スパム防止機能（同一アラートの抑制）
- opt-in設計（デフォルト無効、CLI引数で有効化）

**使用例**:
```bash
# ネットワークチェックを有効化して実行
komon advise --with-net

# ネットワークチェックのみ実行
komon advise --net-only

# Pingチェックのみ実行
komon advise --ping-only

# HTTPチェックのみ実行
komon advise --http-only

# 特定セクションのみ表示
komon advise --section network
```

**設定例**:
```yaml
network_check:
  enabled: false  # デフォルトは無効（opt-in）
  ping:
    enabled: true
    targets:
      - host: "8.8.8.8"
        name: "Google DNS"
      - host: "1.1.1.1"
        name: "Cloudflare DNS"
    timeout: 2
    count: 3
  http:
    enabled: true
    targets:
      - url: "https://api.example.com/health"
        name: "API Health Check"
        method: "GET"
        timeout: 5
        expected_status: 200
```

**通知例**:
```
🌐 ネットワーク疎通チェック

⚠️ 接続障害を検出しました:
- Google DNS (8.8.8.8): Ping失敗
- API Health Check: HTTP 503 (期待値: 200)

✅ 正常な接続:
- Cloudflare DNS (1.1.1.1): Ping成功
```

#### 📊 ディスク使用量の増加トレンド予測（v1.16.0〜）

過去7日分のディスク使用率データから線形回帰により将来の使用量を予測し、ディスク容量が90%に到達する予測日を算出します。

**特徴**:
- 過去7日分のデータから増加率を計算
- 90%到達予測日を表示（「あとN日で90%に到達」）
- 前日比10%以上の急激な増加を検出
- `komon advise` コマンドで予測結果を表示
- 週次レポートにも自動的に含まれる

**使用例**:
```bash
$ python scripts/advise.py

📊 ディスク使用量の予測
⚠️ ディスク使用量が急激に増加しています！
前日比: +12.5%（75.0% → 87.5%）

このままだと、あと3日で90%に到達する見込みです。
予測到達日: 2025-11-28

💡 推奨アクション：
- 古いログファイルを削除: journalctl --vacuum-time=7d
- 不要なファイルを確認: du -sh /* | sort -h
```

安全な状態の場合:
```bash
📊 ディスク使用量の予測
✅ ディスク使用量は安定しています
現在の使用率: 65.0%
増加率: +0.3%/日

当面は問題ありません。
```

#### 📜 通知履歴の保存と表示（v1.11.0〜）

Slack等の通知が使えない環境でも、Komonが検知した情報を後から確認できます。

**特徴**:
- 通知が自動的にローカルファイルに保存される（最大100件）
- `komon advise --history` で履歴を表示
- `komon advise --history 10` で直近10件のみ表示

#### 📊 週次健全性レポート（v1.12.0〜）

異常がなくても定期的にシステムの状況を把握できます。

**特徴**:
- 過去7日分のリソースデータを集計
- 先週比の増減を表示
- 今週の警戒情報サマリー
- トレンド判定（安定/増加傾向/減少傾向）
- ディスク使用量の予測も含まれる

#### 🚨 段階的な閾値通知（v1.13.0〜）

3段階の閾値（警告/警戒/緊急）で段階的に通知します。

**特徴**:
- 💛 警告（70%）: 「そろそろ気にかけておいた方がいいかも」
- 🧡 警戒（80%）: 「ちょっと気になる水準です」
- ❤️ 緊急（90%）: 「かなり逼迫しています！」

#### 🔕 通知頻度制御（v1.15.0〜）

同一アラートの通知を抑制し、通知疲れを防止します。

**特徴**:
- 同一アラートは設定間隔（デフォルト: 60分）で抑制
- 閾値レベルが上がった場合は即座に通知（85%→90%等）
- 長時間継続する問題の再通知（エスカレーション機能）

#### 💡 コンテキスト型アドバイス（v1.18.0〜）

高負荷プロセスに対して、プロセスの種類に応じた具体的なアドバイスを提供します。

**特徴**:
- プロセス名から種類を自動判定（node、docker、python、nginx等）
- 各プロセスに適した対処法を提案
- 詳細度を3段階（minimal/normal/detailed）で切り替え可能
- カスタムパターンで独自のアドバイスを追加可能

**対応プロセス**:
- **node**: 開発サーバー、ビルドプロセス
- **docker**: コンテナ管理
- **python**: 機械学習、データ処理
- **nginx/apache**: Webサーバー
- **mysql/postgres**: データベース
- **java**: Javaアプリケーション
- その他多数

#### 📊 Slack通知にプロセス情報を含める（v1.19.0〜）

Slack通知で、どのプロセスが高負荷を引き起こしているのかが一目で分かるようになりました。

**特徴**:
- CPU/メモリ超過時に上位3プロセスの情報を自動追加
- プロセス名と使用率を表示
- 既存の通知機能に影響なし

**通知例**:
```
⚠️ Komon 警戒情報:
CPU使用率が高いです: 88.5%

📊 上位プロセス:
1. python: 35.2%
2. node: 28.1%
3. docker: 15.7%
```

#### 🔍 多重実行プロセスの検出（v1.20.0〜）

cronなどによる同一スクリプトの多重起動を検出し、リソース圧迫の原因として警告します。

**特徴**:
- 同一スクリプトの多重実行を自動検出
- スクリプト名、実行数、PIDリストを表示
- 設定ファイルで検出閾値を調整可能（デフォルト: 3個以上）
- 対象拡張子: .py, .sh, .rb, .pl

**警告例**:
```
⚠️ 多重実行プロセスを検出しました:

スクリプト: backup.sh
実行数: 5個
PID: [12345, 12346, 12347, 12348, 12349]

💡 提案:
- cron間隔の見直しを検討してください
- ロックファイルの使用を検討してください
```

#### ⏱️ 長時間実行プロセスの検出（v1.22.0〜）

特定スクリプトが長時間実行されている場合に検出し、継続稼働を助言表示します。

**特徴**:
- 長時間実行プロセスを自動検出
- スクリプト名、PID、実行時間を表示
- 実行時間を人間に読みやすい形式で表示（例: 2時間30分）
- 設定ファイルで検出閾値を調整可能（デフォルト: 3600秒 = 1時間）
- 対象拡張子: .py, .sh, .rb, .pl

**警告例**:
```
⚠️ 長時間実行プロセスを検出しました:

スクリプト: backup.py (PID: 12345)
実行時間: 2時間30分

💡 提案:
- スクリプトが正常に動作しているか確認してください
- cron間隔がスクリプトの実行時間より短い場合は見直してください
```

#### 📋 ログ急増時の末尾抜粋表示（v1.21.0〜）

ログ急増の通知時、実際のログ内容も数行添付することで、問題の内容を即座に把握できます。

**特徴**:
- ログ急増検出時に末尾N行を自動抽出（デフォルト: 10行）
- 通知メッセージにコードブロック形式で表示
- 設定で表示行数を変更可能（0で無効化）
- 長い行は自動的に切り詰め（デフォルト: 500文字）
- 大きなログファイルでも高速動作（末尾のみ読み込み）

**通知例**:
```
⚠️ Komon ログ警戒情報:

- /var/log/messages: 前日比 +45.2% の急増の可能性

📄 ログファイル: /var/log/messages
📋 末尾 10 行:
Nov 30 10:15:23 server systemd: Starting service...
Nov 30 10:15:24 server app: Error: Connection timeout
Nov 30 10:15:24 server app: Retrying connection...
Nov 30 10:15:25 server app: Error: Connection timeout
Nov 30 10:15:25 server app: Max retries exceeded
```

**設定例**:
```yaml
log_analysis:
  tail_lines: 10          # 末尾抜粋の行数（0で無効化）
  max_line_length: 500    # 1行あたりの最大文字数
```

**メモリ通知例**:
```
⚠️ Komon 警戒情報:
メモリ使用率が高いです: 92.3%

📊 上位プロセス:
1. chrome: 1024.5MB
2. python: 512.3MB
3. node: 256.1MB
```

**使用例**:
```bash
$ python scripts/advise.py

🧐 高負荷プロセスの詳細情報（CPU使用率が高いもの）

1. node (PID: 12345) - CPU: 45.0%, メモリ: 30.0%
   💡 開発サーバーやビルドプロセスの可能性があります
   
   コマンド: /usr/bin/node server.js
   停止方法: kill 12345

2. docker (PID: 23456) - CPU: 35.0%, メモリ: 25.0%
   💡 コンテナが高負荷です。不要なコンテナを停止してみてください
   
   コマンド: /usr/bin/dockerd
   停止方法: docker stop <container_id>
```

---

## 📋 コマンドリファレンス

Komonで使用できる主要なコマンドの一覧です。

### 日常使用コマンド

| コマンド | 説明 | 使用例 |
|---------|------|--------|
| `komon advise` | 対話型アドバイザー（システム状態の分析と改善提案） | `komon advise --verbose` |
| `komon status` | 現在のシステム状態を簡潔に表示 | `komon status` |
| `komon guide` | 使い方を対話的に案内 | `komon guide` |
| `komon initial` | 初期設定ウィザード | `komon initial` |

### 監視・レポートコマンド（cron実行用）

| コマンド | 説明 | 推奨頻度 |
|---------|------|---------|
| `python scripts/main.py` | リソース監視（CPU/メモリ/ディスク） | 5分おき |
| `python scripts/main_log_monitor.py` | ログ急増監視 | 5分おき |
| `python scripts/main_log_trend.py` | ログ傾向分析（過去7日間） | 毎日3時 |
| `python scripts/weekly_report.py` | 週次健全性レポート | 毎週月曜9時 |

### 開発・メンテナンスコマンド

| コマンド | 説明 | 使用タイミング |
|---------|------|---------------|
| `python scripts/check_coverage.py` | テストカバレッジ分析 | 開発時 |
| `python scripts/generate_release_notes.py` | リリースノート自動生成 | リリース時 |
| `python scripts/check_status_consistency.py` | タスク整合性チェック | push前 |
| `python scripts/validate_specs.py` | Spec構造検証 | Spec作成時 |

### adviseコマンドのオプション

```bash
# 詳細表示モード
komon advise --verbose

# 特定セクションのみ表示
komon advise --section status    # システム状態のみ
komon advise --section alerts    # 警戒情報のみ
komon advise --section process   # プロセス情報のみ
komon advise --section history   # 通知履歴のみ
komon advise --section network   # ネットワーク疎通チェックのみ

# 通知履歴の表示件数を指定
komon advise --history 10        # 直近10件
komon advise --history 0         # 全件表示
```

📖 **詳細なコマンドリファレンス**: [docs/COMMAND_REFERENCE.md](docs/COMMAND_REFERENCE.md)

---

## ⚙️ 設定

`settings.yml`を作成して、監視項目や通知設定をカスタマイズできます。

サンプルファイル: `config/settings.yml.sample`

### 3段階閾値設定（推奨）

v1.13.0から、リソース使用率の閾値を3段階（警告/警戒/緊急）で設定できるようになりました。

```yaml
thresholds:
  cpu:
    warning: 70   # 💛 警告: そろそろ気にかけておいた方がいいかも
    alert: 85     # 🧡 警戒: ちょっと気になる水準です
    critical: 95  # ❤️ 緊急: かなり逼迫しています！
  mem:
    warning: 70
    alert: 80
    critical: 90
  disk:
    warning: 70
    alert: 80
    critical: 90

notifications:
  slack:
    enabled: true
    webhook_url: "env:KOMON_SLACK_WEBHOOK"  # 環境変数推奨（セキュリティ向上）
  email:
    enabled: false
    password: "env:KOMON_EMAIL_PASSWORD"  # 環境変数推奨
```

**セキュリティ注意**: Webhook URLやパスワードは環境変数で管理することを推奨します。詳細は[セキュリティガイド](docs/SECURITY.md)を参照してください。

### ネットワーク疎通チェック設定（v1.25.0〜）

外部サービスやAPIへの疎通を定期的に確認します。

```yaml
network_check:
  enabled: false  # デフォルトは無効（opt-in）
  ping:
    enabled: true
    targets:
      - host: "8.8.8.8"
        name: "Google DNS"
      - host: "1.1.1.1"
        name: "Cloudflare DNS"
    timeout: 2
    count: 3
  http:
    enabled: true
    targets:
      - url: "https://api.example.com/health"
        name: "API Health Check"
        method: "GET"
        timeout: 5
        expected_status: 200
```

**⚠️ 注意**: `network_check.http.targets`の例示URL（`https://api.example.com/health`）は実在しません。必ず実際の監視対象URLに差し替えてください。

### 出力フォーマット設定（v1.23.0〜）

`output`セクションで出力フォーマットをカスタマイズできます。

```yaml
output:
  default_mode: "normal"  # "normal" または "verbose"
  history_limit: 5        # 通知履歴のデフォルト表示件数
  show_zero_cpu: false    # CPU/メモリ0.0%のプロセスを表示するか
```

### 従来の単一閾値設定（後方互換性あり）

従来の単一値形式も引き続きサポートされています。

```yaml
thresholds:
  cpu: 85
  mem: 80
  disk: 80
```

単一値を指定した場合、自動的に3段階形式に変換されます：
- 警告: 閾値 - 10
- 警戒: 閾値
- 緊急: 閾値 + 10

### 3段階閾値のメリット

- **早期警戒**: 70%で警告、80%で警戒、90%で緊急と段階的に通知
- **適切な対応**: レベルに応じて対応の緊急度を判断できる
- **オオカミ少年化の防止**: 段階的な表現で通知疲れを軽減

### 通知頻度制御（v1.15.0〜）

同一アラートの繰り返し通知を抑制し、「通知疲れ」を防ぎます。

```yaml
throttle:
  enabled: true  # 通知頻度制御を有効化
  interval_minutes: 60  # 同一アラートの通知間隔（分）
  escalation_minutes: 180  # 長時間継続する問題の再通知間隔（分）
```

**主な機能**:
- **通知抑制**: 同一メトリクスの通知を60分間隔で制御
- **レベル上昇時の即時通知**: 警告→警戒、警戒→緊急の場合は即座に通知
- **エスカレーション**: 3時間継続する問題は再通知（「3時間経過しましたが、まだ高い状態が続いています」）

詳細は [docs/README.md](docs/README.md) を参照してください。

---

## 🕒 定期実行（Cron）

```bash
# リソース監視（5分おき）
*/5 * * * * cd /path/to/Komon && /usr/bin/python3 scripts/main.py >> log/main.log 2>&1

# ログ監視（5分おき）
*/5 * * * * cd /path/to/Komon && /usr/bin/python3 scripts/main_log_monitor.py >> log/monitor.log 2>&1

# ログ傾向分析（毎日3時）
0 3 * * * cd /path/to/Komon && /usr/bin/python3 scripts/main_log_trend.py >> log/trend.log 2>&1

# 週次健全性レポート（毎週月曜9時）
0 9 * * 1 cd /path/to/Komon && /usr/bin/python3 scripts/weekly_report.py >> log/weekly_report.log 2>&1
```

**注意**: 環境によってPythonコマンドが異なる場合があります：
- `/usr/bin/python3` (RHEL系、Ubuntu等)
- `python3` (PATH設定済みの場合)
- `python` (エイリアス設定済みの場合)
- `venv/bin/python` (仮想環境を使用する場合)

`which python3` コマンドで実際のパスを確認してください。

---

## 📚 ドキュメント

### ユーザー向け

- [コマンドリファレンス](docs/COMMAND_REFERENCE.md) - 全コマンドの詳細説明
- [詳細ドキュメント](docs/README.md)
- [システム仕様書](.kiro/specs/komon-system.md)
- [変更履歴](docs/CHANGELOG.md)
- [セキュリティガイド](docs/SECURITY.md) - 認証情報の管理、ファイルパーミッション、セキュリティベストプラクティス
- [対象環境の詳細](docs/RECOMMENDED_RUNTIME.md) - 各ディストリビューションでの動作確認状況、インストール手順
- [企業向け導入ガイド](docs/ENTERPRISE_GUIDE.md) - 企業環境での導入方法、複数サーバ運用、セキュリティ考慮事項

### 開発者向け

- [AI開発ルール](docs/AI_DEVELOPMENT_RULES.md) - AI支援開発のベストプラクティス、粒度の判断基準

---

## 🔧 開発

### 仕様駆動開発

このプロジェクトは仕様駆動開発（Spec-Driven Development）を採用しています。

仕様書: `.kiro/specs/komon-system.md`

### テスト実行

```bash
# 開発用パッケージをインストール
pip install -r requirements-dev.txt

# テストを実行
python -m pytest tests/ -v

# カバレッジレポートを生成（推奨）
bash run_coverage.sh

# HTMLレポートを確認
# htmlcov/index.html をブラウザで開く
```

**テストカバレッジ: 92%**

詳細は [tests/README.md](tests/README.md) を参照してください。

---

## 🐧 対応プラットフォーム

### 推奨環境（Recommended Runtime）

Komonは**RHEL系Linux**での動作を推奨しています：

- **Python**: 3.10以上（推奨: 3.11, 3.12）
- **OS**: RHEL系Linux（systemd対応）
  - **AlmaLinux 9+** ⭐ 最も推奨
  - **Rocky Linux 9+** ⭐ 推奨
  - **Amazon Linux 2023+** ⭐ 推奨
  - Fedora 38+
  - CentOS Stream 9+

### ベストエフォート対応

以下の環境でも動作しますが、一部機能が制限されます：

- **Debian系Linux**
  - Ubuntu 22.04+
  - Debian 12+
  - Raspberry Pi OS（Debian 12ベース）
  
  **制限事項**:
  - パッケージ系のアドバイスが抑制されます（パッケージ名の違いによる誤アドバイスを防ぐため）
  - ログパスが自動的に `/var/log/syslog` に切り替わります

- **その他のLinux**
  - SUSE系、Arch系でも基本機能は動作する可能性があります
  - ただし、OS固有のアドバイスは制限されます

**重要**: RHEL系以外では、Komonの「誤ったアドバイスをしない」という哲学に基づき、一部のアドバイスが抑制されます。

### 非対応環境

- **Amazon Linux 2**（Python 2.7標準、サポート寿命が短い）
- **CentOS 7以前**（systemd未対応またはPython 3.10未対応）
- **Windows ネイティブ**（現時点では非対応）
  - WSL（Windows Subsystem for Linux）では動作します
- **macOS**（現時点では対象外）

### 詳細情報

各ディストリビューションでの動作確認状況、インストール手順の差異、トラブルシューティングについては、以下のドキュメントを参照してください：

📖 **[対象環境の詳細（RECOMMENDED_RUNTIME.md）](docs/RECOMMENDED_RUNTIME.md)**

### OS自動判定機能

Komonは実行環境のOSを自動判定し、適切なアドバイスを提供します：

- `/etc/os-release` を読み取ってOSファミリを判定
- 設定ファイル（`system.os_family`）で手動上書きも可能
- Windows ネイティブでは起動時にエラーメッセージを表示して終了
- WSL環境ではLinux扱いで動作

### Windows / macOS について

- **Windows**: WSL（Windows Subsystem for Linux）での実行を推奨します
- **macOS**: 現時点では対象外ですが、移植版の作成は歓迎します

もし移植版を作成された場合は、ぜひお知らせください。
READMEにリンクを掲載させていただきます。

---

## ❓ FAQ

<details>
<summary><strong>Q: Windowsで動きますか？</strong></summary>

現時点ではLinux専用です。Windows版の移植は歓迎しますが、作者自身は開発予定がありません。
</details>

<details>
<summary><strong>Q: 通知が届きません</strong></summary>

1. `settings.yml`の設定を確認してください
2. Slack Webhook URLが正しいか確認してください
3. `python scripts/status.py`でステータスを確認してください
</details>

<details>
<summary><strong>Q: どのくらいのリソースを消費しますか？</strong></summary>

Komon自体は非常に軽量です（メモリ使用量: 約30MB）。5分おきの実行でも、システムへの影響はほとんどありません。
</details>

---

## 🤝 コントリビューション

バグ報告、機能提案、プルリクエストを歓迎します！

- **バグ報告**: [Issues](https://github.com/kamonabe/Komon/issues)で報告してください
- **機能提案**: [Discussions](https://github.com/kamonabe/Komon/discussions)で議論しましょう
- **プルリクエスト**: [CONTRIBUTING.md](docs/CONTRIBUTING.md)を参照してください

### 移植版の募集

Windows版やmacOS版を作成された方は、ぜひお知らせください！
READMEにリンクを掲載させていただきます。

---

## ⭐ このプロジェクトが役に立ったら

GitHubで⭐スターをつけていただけると、開発の励みになります！

---

## 📄 ライセンス

MIT License - 個人・商用利用、改変・再配布が自由

---

## 👤 作者

**かもなべ技術研究所 / Kamo-Tech Lab**  
開発者: [@kamonabe](https://github.com/kamonabe)

「自分が欲しいと思ったものを形にして公開してみる」がこのプロジェクトの原点です。

### 開発方針

- Linux環境での実用性を最優先
- シンプルで拡張しやすい設計
- 過剰な機能追加よりも、コアな機能の安定性を重視
- 他のプラットフォームへの移植は、コミュニティに委ねる

---
---

# English Version

**Komon is a lightweight advisor-type SOAR-inspired tool for developers.**

It quietly monitors resource overuse, log surges, and update oversights in your development environment, and gently notifies and suggests actions only when necessary.

🛠 Komon has a simple internal structure, making it easy to add notification methods and extend monitoring items.

**Note**: Komon's output messages are currently in Japanese only. However, the code is well-documented and the configuration files use English keys, making it accessible for English-speaking developers who want to understand or modify the tool.

---

## 📖 Table of Contents

- [Sample Output](#-sample-output)
- [Why Komon?](#-why-komon)
- [Relationship with Other Monitoring Tools](#-relationship-with-other-monitoring-tools)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start-takes-5-minutes)
- [Command Reference](#-command-reference)
- [Configuration](#️-configuration)
- [Scheduled Execution](#-scheduled-execution-cron)
- [Documentation](#-documentation)
- [Development](#-development)
- [Supported Platforms](#-supported-platforms)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Sample Output

Running the `komon advise` command analyzes system status and provides interactive improvement suggestions:

```bash
$ python scripts/advise.py

📊 Current System Status
CPU:     [█░░░░░░░░░] 12.3% / 80% ✅
Memory:  [████░░░░░░] 45.2% / 85% ✅
Disk:    [███████░░░] 67.8% / 90% ✅

🔔 Alert Information
(None)

💡 Improvement Suggestions

① Security Patch Check
→ No security updates available.

② System Patches (Non-Security)
→ 384 non-security updates available. Examples:
   - NetworkManager.x86_64               1:1.54.0-3.el9_7                                 baseos    
   - NetworkManager-libnm.x86_64         1:1.54.0-3.el9_7                                 baseos    
   ...

💡 You can apply these updates with:
   sudo dnf upgrade -y

🔄 Duplicate Process Detection
→ No duplicate processes detected.

⏱️  Long-Running Process Detection
⚠️ The following scripts have been running for a long time:

  • shellIntegration-bash.sh (PID: 12345)
    Runtime: 1 hour 2 minutes

【Recommended Actions】
  - Verify the script is functioning normally
  - Review cron intervals if shorter than script execution time
  - Stop the process if necessary

📜 Notification History (Latest 5)
💿 [12:51:44] DISK: 96.7% - Alert
📊 [12:51:44] MEMORY: 91.3% - Alert
🔥 [12:51:44] CPU: 88.5% - Alert

Details: komon advise --verbose
```

**New Features (v1.23.0~)**:
- Display current system status first (with progress bars)
- Visually clear presentation
- Reduced noise (hide 0.0% processes)
- Changed default notification history display to 5 items
- `--verbose` option for detailed display
- `--section` option to display specific sections only

**Contextual Advice (v1.18.0~)**:
When high-load processes are detected, specific advice is provided based on the process type.

When resource usage exceeds thresholds, you'll receive gentle notifications like:

```
💬 Something to note

CPU seems to be working hard (92.3%).
Is there a heavy process running?
```

These notifications can also be received via Slack or email. Additionally, they are automatically saved as notification history and can be reviewed later with `komon advise --history`.

### Progressive Notification Messages (v1.17.0~)

When the same issue occurs repeatedly, notification messages change progressively:

- **1st time**: "Something to note" (gentle expression)
- **2nd time**: "Still continuing" (indicates persistence)
- **3rd time and beyond**: "Might want to check this soon" (prompts action)

This helps you properly gauge issue urgency and prevents "notification fatigue."

---

## 🤔 Why Komon?

Compared to existing monitoring tools (Prometheus, Zabbix, Nagios, etc.):

- **Lightweight**: Few dependencies, quick to deploy
- **Developer-Friendly**: Designed for use in development environments
- **Gentle Notifications**: Human-like expressions, not overly technical
- **Easy to Extend**: Written in Python, easy to customize
- **Progressive Warnings**: 3-level thresholds prevent notification fatigue

Komon is not a large-scale monitoring system, but a **lightweight advisor for individual developers and small teams**.

---

## 🤝 Relationship with Other Monitoring Tools

Komon is lightweight (memory usage: ~30MB), so it can be **used alongside** existing monitoring tools like Zabbix or Prometheus without issues.

While large-scale monitoring systems become essential in production environments, adding Komon separately for developers enables more agile monitoring.

### Example of Combined Use

- **Zabbix/Prometheus**: Infrastructure-wide monitoring, SLA guarantees
- **Komon**: Individual developer "awareness," fine-grained process-level monitoring

You can receive "developer-perspective insights" that large-scale monitoring might miss through Komon's "gentle notifications."

Of course, **standalone Komon use** in small-scale environments or development servers is also intended.

### Notes on Combined Use

When using alongside existing monitoring tools in production environments, please conduct thorough testing beforehand. We especially recommend verifying:

- Resource usage impact (CPU, memory, disk I/O)
- Log output duplication or conflicts
- Notification duplication (multiple tools notifying for the same event)
- Cron execution timing adjustments

---

## 📁 Project Structure

```
Komon/
├── src/komon/                      # Core modules
│   ├── monitor.py                  # Resource monitoring
│   ├── analyzer.py                 # Threshold judgment & analysis
│   ├── contextual_advisor.py       # Contextual advice
│   ├── notification.py             # Notification functionality
│   ├── notification_history.py     # Notification history management
│   ├── history.py                  # History management
│   ├── log_watcher.py              # Log monitoring
│   ├── log_analyzer.py             # Log analysis
│   ├── log_trends.py               # Log trend analysis
│   ├── weekly_data.py              # Weekly data collection
│   ├── report_formatter.py         # Report formatting
│   ├── settings_validator.py       # Settings validation
│   └── cli.py                      # CLI entry point
├── scripts/                        # Execution scripts
│   ├── main.py                     # Resource monitoring main
│   ├── main_log_monitor.py         # Log surge monitoring
│   ├── main_log_trend.py           # Log trend analysis
│   ├── weekly_report.py            # Weekly health report
│   ├── advise.py                   # Interactive advisor
│   ├── initial.py                  # Initial setup
│   ├── status.py                   # Status display
│   ├── komon_guide.py              # Guide menu
│   ├── check_coverage.py           # Coverage analysis
│   ├── setup_coverage_fix.sh       # Coverage setup fix
│   ├── generate_release_notes.py   # Auto-generate release notes
│   ├── check_status_consistency.py # Status consistency check
│   └── init.sh                     # Initialization script
├── config/                         # Configuration files
│   └── settings.yml.sample         # Configuration sample
├── docs/                           # Documentation
│   ├── README.md                   # Detailed documentation
│   ├── CHANGELOG.md                # Change history
│   └── SECURITY.md                 # Security information
├── tests/                          # Test code (92% coverage)
├── data/                           # Data storage (auto-generated)
│   ├── usage_history/              # Resource usage history
│   ├── notifications/              # Notification history
│   ├── komon_data/                 # Komon internal data
│   └── logstats/                   # Log statistics data
├── .kiro/                          # Kiro IDE configuration
│   ├── specs/                      # Specifications
│   ├── tasks/                      # Task management
│   └── steering/                   # Development rules
├── requirements.txt                # Python dependencies
├── setup.py                        # Installation configuration
├── LICENSE                         # License
└── version.txt                     # Version information
```

---

## 🚀 Quick Start (Takes ~5 minutes)

### Prerequisites
- Linux environment (AlmaLinux 9 recommended)
- Python 3.10 or higher

### 1. Installation

```bash
# Install from PyPI (recommended)
pip install komon

# Or development version (GitHub)
git clone https://github.com/kamonabe/Komon.git
cd Komon
pip install -e .
```

### 2. Initial Setup (5 minutes)

```bash
# Run initial setup wizard
python scripts/initial.py

# Or (if installed)
komon initial
```

### 3. Verification (1 minute)

```bash
# Interactive advisor
komon advise

# Verbose mode (display all information)
komon advise --verbose

# Display specific sections only
komon advise --section status    # System status only
komon advise --section alerts    # Alert information only
komon advise --section process   # Process information only
komon advise --section history   # Notification history only

# Specify notification history display count
komon advise --history 10        # Latest 10 items only
komon advise --history 0         # Display all

# Or run directly from scripts
python scripts/main.py      # Resource monitoring
python scripts/status.py    # Status check
python scripts/advise.py    # Interactive advisor
python scripts/weekly_report.py  # Weekly health report
```

### Slack Notification Setup (Optional)

To use Slack notifications, obtain a Webhook URL:

1. Access [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
2. Select "Create New App" → "Incoming Webhooks"
3. Copy the URL and set it in `settings.yml` under `notifications.slack.webhook_url`

**Note**: Slack notifications are not required. You can check status with the `komon advise` command without notifications.

### Main Features

#### 🌐 Network Connectivity Check (v1.25.0~)

Periodically checks connectivity to external services and APIs for early detection of connection failures.

**Features**:
- Supports Ping check (ICMP) and HTTP check (GET/POST)
- Monitors multiple targets simultaneously
- Notifies only on state changes (normal→abnormal, abnormal→normal)
- Notification spam prevention (suppresses duplicate alerts)
- Opt-in design (disabled by default, enabled via CLI argument)

**Usage Examples**:
```bash
# Enable network check
komon advise --with-net

# Network check only
komon advise --net-only

# Ping check only
komon advise --ping-only

# HTTP check only
komon advise --http-only

# Display specific section only
komon advise --section network
```

#### 📊 Disk Usage Trend Prediction (v1.16.0~)

Predicts future usage from 7 days of disk usage data using linear regression, calculating the predicted date when disk capacity will reach 90%.

**Features**:
- Calculates growth rate from past 7 days of data
- Displays predicted date to reach 90% ("Will reach 90% in N days")
- Detects rapid increases of 10% or more compared to previous day
- Displays prediction results in `komon advise` command
- Automatically included in weekly reports

#### 📜 Notification History Storage and Display (v1.11.0~)

Even in environments where Slack notifications aren't available, you can review information detected by Komon later.

**Features**:
- Notifications automatically saved to local file (max 100 items)
- Display history with `komon advise --history`
- Display only latest 10 items with `komon advise --history 10`

#### 📊 Weekly Health Report (v1.12.0~)

Regularly understand system status even when there are no anomalies.

**Features**:
- Aggregates resource data from past 7 days
- Displays week-over-week changes
- Summary of this week's alert information
- Trend judgment (stable/increasing/decreasing)
- Includes disk usage prediction

#### 🚨 Progressive Threshold Notifications (v1.13.0~)

Notifies progressively with 3-level thresholds (warning/alert/critical).

**Features**:
- 💛 Warning (70%): "Might want to start paying attention"
- 🧡 Alert (80%): "This is a concerning level"
- ❤️ Critical (90%): "Quite tight!"

#### 🔕 Notification Frequency Control (v1.15.0~)

Suppresses duplicate alert notifications to prevent notification fatigue.

**Features**:
- Duplicate alerts suppressed at configured interval (default: 60 minutes)
- Immediate notification when threshold level increases (85%→90%, etc.)
- Re-notification for long-lasting issues (escalation feature)

#### 💡 Contextual Advice (v1.18.0~)

Provides specific advice for high-load processes based on process type.

**Features**:
- Automatically determines process type from process name (node, docker, python, nginx, etc.)
- Suggests appropriate actions for each process
- 3 levels of detail (minimal/normal/detailed)
- Add custom advice with custom patterns

**Supported Processes**:
- **node**: Development servers, build processes
- **docker**: Container management
- **python**: Machine learning, data processing
- **nginx/apache**: Web servers
- **mysql/postgres**: Databases
- **java**: Java applications
- And many more

#### 📊 Include Process Information in Slack Notifications (v1.19.0~)

Slack notifications now show at a glance which processes are causing high load.

**Features**:
- Automatically adds top 3 process information when CPU/memory exceeds threshold
- Displays process name and usage rate
- No impact on existing notification functionality

#### 🔍 Duplicate Process Detection (v1.20.0~)

Detects multiple instances of the same script (e.g., from cron) and warns as a cause of resource pressure.

**Features**:
- Automatically detects duplicate script execution
- Displays script name, execution count, PID list
- Adjustable detection threshold in config file (default: 3 or more)
- Target extensions: .py, .sh, .rb, .pl

#### ⏱️ Long-Running Process Detection (v1.22.0~)

Detects when specific scripts have been running for a long time and displays advisory information for continued operation.

**Features**:
- Automatically detects long-running processes
- Displays script name, PID, runtime
- Displays runtime in human-readable format (e.g., 2 hours 30 minutes)
- Adjustable detection threshold in config file (default: 3600 seconds = 1 hour)
- Target extensions: .py, .sh, .rb, .pl

#### 📋 Log Tail Excerpt Display on Log Surge (v1.21.0~)

When log surge is detected, actual log content is also attached for a few lines, allowing immediate understanding of the issue.

**Features**:
- Automatically extracts last N lines when log surge detected (default: 10 lines)
- Displays in code block format in notification message
- Display line count configurable in settings (0 to disable)
- Long lines automatically truncated (default: 500 characters)
- Fast operation even with large log files (reads only tail)

---

## 📋 Command Reference

List of main commands available in Komon.

### Daily Use Commands

| Command | Description | Usage Example |
|---------|-------------|---------------|
| `komon advise` | Interactive advisor (system status analysis and improvement suggestions) | `komon advise --verbose` |
| `komon status` | Display current system status concisely | `komon status` |
| `komon guide` | Interactive usage guide | `komon guide` |
| `komon initial` | Initial setup wizard | `komon initial` |

### Monitoring & Report Commands (for cron execution)

| Command | Description | Recommended Frequency |
|---------|-------------|----------------------|
| `python scripts/main.py` | Resource monitoring (CPU/Memory/Disk) | Every 5 minutes |
| `python scripts/main_log_monitor.py` | Log surge monitoring | Every 5 minutes |
| `python scripts/main_log_trend.py` | Log trend analysis (past 7 days) | Daily at 3 AM |
| `python scripts/weekly_report.py` | Weekly health report | Every Monday at 9 AM |

### Development & Maintenance Commands

| Command | Description | Usage Timing |
|---------|-------------|--------------|
| `python scripts/check_coverage.py` | Test coverage analysis | During development |
| `python scripts/generate_release_notes.py` | Auto-generate release notes | At release |
| `python scripts/check_status_consistency.py` | Task consistency check | Before push |
| `python scripts/validate_specs.py` | Spec structure validation | When creating specs |

### advise Command Options

```bash
# Verbose mode
komon advise --verbose

# Display specific sections only
komon advise --section status    # System status only
komon advise --section alerts    # Alert information only
komon advise --section process   # Process information only
komon advise --section history   # Notification history only
komon advise --section network   # Network connectivity check only

# Specify notification history display count
komon advise --history 10        # Latest 10 items
komon advise --history 0         # Display all
```

📖 **Detailed Command Reference**: [docs/COMMAND_REFERENCE.md](docs/COMMAND_REFERENCE.md)

---

## ⚙️ Configuration

Create `settings.yml` to customize monitoring items and notification settings.

Sample file: `config/settings.yml.sample`

### 3-Level Threshold Settings (Recommended)

From v1.13.0, resource usage thresholds can be set in 3 levels (warning/alert/critical).

```yaml
thresholds:
  cpu:
    warning: 70   # 💛 Warning: Might want to start paying attention
    alert: 85     # 🧡 Alert: This is a concerning level
    critical: 95  # ❤️ Critical: Quite tight!
  mem:
    warning: 70
    alert: 80
    critical: 90
  disk:
    warning: 70
    alert: 80
    critical: 90

notifications:
  slack:
    enabled: true
    webhook_url: "env:KOMON_SLACK_WEBHOOK"  # Environment variable recommended (improved security)
  email:
    enabled: false
    password: "env:KOMON_EMAIL_PASSWORD"  # Environment variable recommended
```

**Security Note**: We recommend managing Webhook URLs and passwords via environment variables. See [Security Guide](docs/SECURITY.md) for details.

### Network Connectivity Check Settings (v1.25.0~)

Periodically checks connectivity to external services and APIs.

```yaml
network_check:
  enabled: false  # Disabled by default (opt-in)
  ping:
    enabled: true
    targets:
      - host: "8.8.8.8"
        name: "Google DNS"
      - host: "1.1.1.1"
        name: "Cloudflare DNS"
    timeout: 2
    count: 3
  http:
    enabled: true
    targets:
      - url: "https://api.example.com/health"
        name: "API Health Check"
        method: "GET"
        timeout: 5
        expected_status: 200
```

**⚠️ Note**: The example URL in `network_check.http.targets` (`https://api.example.com/health`) does not exist. Be sure to replace it with your actual monitoring target URL.

### Output Format Settings (v1.23.0~)

Customize output format in the `output` section.

```yaml
output:
  default_mode: "normal"  # "normal" or "verbose"
  history_limit: 5        # Default notification history display count
  show_zero_cpu: false    # Whether to display processes with 0.0% CPU/memory
```

### Legacy Single Threshold Settings (Backward Compatible)

The legacy single-value format is still supported.

```yaml
thresholds:
  cpu: 85
  mem: 80
  disk: 80
```

When a single value is specified, it's automatically converted to 3-level format:
- Warning: threshold - 10
- Alert: threshold
- Critical: threshold + 10

### Benefits of 3-Level Thresholds

- **Early Warning**: Progressive notifications at 70% warning, 80% alert, 90% critical
- **Appropriate Response**: Judge response urgency based on level
- **Prevent Crying Wolf**: Progressive expressions reduce notification fatigue

### Notification Frequency Control (v1.15.0~)

Suppresses repeated notifications for the same alert to prevent "notification fatigue."

```yaml
throttle:
  enabled: true  # Enable notification frequency control
  interval_minutes: 60  # Notification interval for same alert (minutes)
  escalation_minutes: 180  # Re-notification interval for long-lasting issues (minutes)
```

**Main Features**:
- **Notification Suppression**: Controls notifications for same metric at 60-minute intervals
- **Immediate Notification on Level Increase**: Immediate notification when warning→alert, alert→critical
- **Escalation**: Re-notifies for issues lasting 3 hours ("3 hours have passed, but high state continues")

See [docs/README.md](docs/README.md) for details.

---

## 🕒 Scheduled Execution (Cron)

```bash
# Resource monitoring (every 5 minutes)
*/5 * * * * cd /path/to/Komon && /usr/bin/python3 scripts/main.py >> log/main.log 2>&1

# Log monitoring (every 5 minutes)
*/5 * * * * cd /path/to/Komon && /usr/bin/python3 scripts/main_log_monitor.py >> log/monitor.log 2>&1

# Log trend analysis (daily at 3 AM)
0 3 * * * cd /path/to/Komon && /usr/bin/python3 scripts/main_log_trend.py >> log/trend.log 2>&1

# Weekly health report (every Monday at 9 AM)
0 9 * * 1 cd /path/to/Komon && /usr/bin/python3 scripts/weekly_report.py >> log/weekly_report.log 2>&1
```

**Note**: Python command may differ depending on environment:
- `/usr/bin/python3` (RHEL-based, Ubuntu, etc.)
- `python3` (when PATH is configured)
- `python` (when alias is configured)
- `venv/bin/python` (when using virtual environment)

Check actual path with `which python3` command.

---

## 📚 Documentation

### For Users

- [Command Reference](docs/COMMAND_REFERENCE.md) - Detailed explanation of all commands
- [Detailed Documentation](docs/README.md)
- [System Specification](.kiro/specs/komon-system.md)
- [Change History](docs/CHANGELOG.md)
- [Security Guide](docs/SECURITY.md) - Credential management, file permissions, security best practices
- [Recommended Runtime Details](docs/RECOMMENDED_RUNTIME.md) - Operation verification status for each distribution, installation procedures
- [Enterprise Deployment Guide](docs/ENTERPRISE_GUIDE.md) - Deployment in enterprise environments, multi-server operations, security considerations

### For Developers

- [AI Development Rules](docs/AI_DEVELOPMENT_RULES.md) - Best practices for AI-assisted development, granularity judgment criteria

---

## 🔧 Development

### Spec-Driven Development

This project adopts Spec-Driven Development.

Specification: `.kiro/specs/komon-system.md`

### Running Tests

```bash
# Install development packages
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/ -v

# Generate coverage report (recommended)
bash run_coverage.sh

# View HTML report
# Open htmlcov/index.html in browser
```

**Test Coverage: 92%**

See [tests/README.md](tests/README.md) for details.

---

## 🐧 Supported Platforms

### Recommended Environment (Recommended Runtime)

Komon is recommended for **RHEL-based Linux**:

- **Python**: 3.10 or higher (recommended: 3.11, 3.12)
- **OS**: RHEL-based Linux (systemd support)
  - **AlmaLinux 9+** ⭐ Most recommended
  - **Rocky Linux 9+** ⭐ Recommended
  - **Amazon Linux 2023+** ⭐ Recommended
  - Fedora 38+
  - CentOS Stream 9+

### Best Effort Support

Also works in the following environments, but with some feature limitations:

- **Debian-based Linux**
  - Ubuntu 22.04+
  - Debian 12+
  - Raspberry Pi OS (Debian 12-based)
  
  **Limitations**:
  - Package-related advice is suppressed (to prevent incorrect advice due to package name differences)
  - Log path automatically switches to `/var/log/syslog`

- **Other Linux**
  - SUSE-based, Arch-based may work for basic features
  - However, OS-specific advice is limited

**Important**: On non-RHEL systems, some advice is suppressed based on Komon's philosophy of "not giving incorrect advice."

### Unsupported Environments

- **Amazon Linux 2** (Python 2.7 standard, short support lifespan)
- **CentOS 7 or earlier** (no systemd support or Python 3.10 incompatible)
- **Windows Native** (currently unsupported)
  - Works on WSL (Windows Subsystem for Linux)
- **macOS** (currently out of scope)

### Detailed Information

For operation verification status on each distribution, installation procedure differences, and troubleshooting, see:

📖 **[Recommended Runtime Details (RECOMMENDED_RUNTIME.md)](docs/RECOMMENDED_RUNTIME.md)**

### Automatic OS Detection

Komon automatically detects the execution environment OS and provides appropriate advice:

- Reads `/etc/os-release` to determine OS family
- Manual override possible in config file (`system.os_family`)
- Displays error message and exits on Windows native startup
- Works as Linux in WSL environment

### About Windows / macOS

- **Windows**: We recommend running on WSL (Windows Subsystem for Linux)
- **macOS**: Currently out of scope, but ported versions are welcome

If you create a ported version, please let us know.
We'll add a link in the README.

---

## ❓ FAQ

<details>
<summary><strong>Q: Does it work on Windows?</strong></summary>

Currently Linux-only. Windows ports are welcome, but the author has no plans to develop one.
</details>

<details>
<summary><strong>Q: Notifications aren't arriving</strong></summary>

1. Check `settings.yml` configuration
2. Verify Slack Webhook URL is correct
3. Check status with `python scripts/status.py`
</details>

<details>
<summary><strong>Q: How much resources does it consume?</strong></summary>

Komon itself is very lightweight (memory usage: ~30MB). Even with 5-minute execution intervals, system impact is minimal.
</details>

<details>
<summary><strong>Q: Output is in Japanese - can I use it?</strong></summary>

Yes! While Komon's output messages are in Japanese, the code is well-documented in English, and configuration files use English keys. English-speaking developers can:
- Understand the code structure and modify it
- Configure settings using English keys in `settings.yml`
- Read technical documentation and comments in the codebase
- Contribute to the project

If you're interested in creating an English output version, contributions are welcome!
</details>

---

## 🤝 Contributing

Bug reports, feature suggestions, and pull requests are welcome!

- **Bug Reports**: Report at [Issues](https://github.com/kamonabe/Komon/issues)
- **Feature Suggestions**: Discuss at [Discussions](https://github.com/kamonabe/Komon/discussions)
- **Pull Requests**: See [CONTRIBUTING.md](docs/CONTRIBUTING.md)

### Seeking Ported Versions

If you create Windows or macOS versions, please let us know!
We'll add links in the README.

---

## ⭐ If This Project Helps You

Starring on GitHub encourages development!

---

## 📄 License

MIT License - Free for personal and commercial use, modification, and redistribution

---

## 👤 Author

**Kamo-Tech Lab**  
Developer: [@kamonabe](https://github.com/kamonabe)

"Creating and sharing what I wanted to have" is the origin of this project.

### Development Policy

- Prioritize practicality in Linux environments
- Simple and extensible design
- Emphasize core feature stability over excessive feature additions
- Leave porting to other platforms to the community
