# Komon（顧問）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/kamonabe/Komon/workflows/Tests/badge.svg)](https://github.com/kamonabe/Komon/actions/workflows/tests.yml)
[![Spec Validation](https://github.com/kamonabe/Komon/workflows/Spec%20and%20Documentation%20Validation/badge.svg)](https://github.com/kamonabe/Komon/actions/workflows/spec-validation.yml)
[![Test Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)](htmlcov/index.html)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)](https://www.linux.org/)

**Komon は、開発者のための軽量アドバイザー型SOAR風ツールです。**

開発環境で発生するリソースの過剰使用、ログの急増、更新忘れなどを静かに見守り、必要なときだけやさしく通知・提案してくれます。

🛠 Komon は内部構造がシンプルなため、通知手段の追加や監視項目の拡張が容易です。

---

## 📖 目次

- [このような結果が得られます](#-このような結果が得られます)
- [なぜKomonなのか？](#-なぜkomonなのか)
- [他の監視ツールとの関係](#-他の監視ツールとの関係)
- [プロジェクト構造](#-プロジェクト構造)
- [クイックスタート](#-クイックスタート)
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

📈 ログ傾向分析
📊 /var/log/messages: 前日比 +45.2% の急増の可能性
📊 /var/log/httpd/access_log: 正常範囲（前日比 +2.1%）

📊 ディスク使用量の予測
✅ ディスク使用量は安定しています
現在の使用率: 68.5%
増加率: +0.3%/日

当面は問題ありません。

📌 CPU使用率の内訳：
- systemd: 0.0%
- kthreadd: 0.0%
- pool_workqueue_: 0.0%

📌 メモリ使用率の内訳：
- firewalld: 41.4 MB
- python: 30.4 MB
- polkitd: 22.7 MB
- NetworkManager: 18.9 MB

🧐 高負荷プロセスの詳細情報（CPU使用率が高いもの）
→ 現在、高負荷なプロセスは検出されていません。

📜 通知履歴
💾 [2025-11-22 21:01:28] MEM: 85.0 - Test alert
📝 [2025-11-22 21:01:27] LOG: 1000.0 - Test email alert
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
├── src/komon/              # コアモジュール
│   ├── monitor.py          # リソース監視
│   ├── analyzer.py         # 閾値判定・分析
│   ├── notification.py     # 通知機能
│   ├── notification_history.py  # 通知履歴管理
│   ├── history.py          # 履歴管理
│   ├── log_watcher.py      # ログ監視
│   ├── log_analyzer.py     # ログ分析
│   ├── log_trends.py       # ログ傾向分析
│   ├── weekly_data.py      # 週次データ収集
│   ├── report_formatter.py # レポートフォーマット
│   ├── settings_validator.py  # 設定検証
│   └── cli.py              # CLIエントリーポイント
├── scripts/                # 実行スクリプト
│   ├── main.py             # リソース監視メイン
│   ├── main_log_monitor.py # ログ急増監視
│   ├── main_log_trend.py   # ログ傾向分析
│   ├── weekly_report.py    # 週次健全性レポート
│   ├── advise.py           # 対話型アドバイザー
│   ├── initial.py          # 初期設定
│   ├── status.py           # ステータス表示
│   ├── komon_guide.py      # ガイドメニュー
│   ├── check_coverage.py   # カバレッジ分析
│   ├── setup_coverage_fix.sh # カバレッジ設定修正
│   └── init.sh             # 初期化スクリプト
├── config/                 # 設定ファイル
│   └── settings.yml.sample # 設定サンプル
├── docs/                   # ドキュメント
│   ├── README.md           # 詳細ドキュメント
│   ├── CHANGELOG.md        # 変更履歴
│   └── SECURITY.md         # セキュリティ情報
├── tests/                  # テストコード（94%カバレッジ、238テスト）
├── data/                   # データ保存先（自動生成）
│   ├── usage_history/      # リソース使用履歴
│   ├── notifications/      # 通知履歴
│   ├── komon_data/         # Komon内部データ
│   └── logstats/           # ログ統計データ
├── .kiro/                  # Kiro IDE設定
│   ├── specs/              # 仕様書
│   │   ├── komon-system.md     # システム仕様
│   │   ├── future-ideas.md     # 将来の改善案
│   │   ├── testing-strategy.md # テスト戦略
│   │   └── notification-history/ # 通知履歴機能spec
│   ├── tasks/              # タスク管理
│   │   └── implementation-tasks.md # 実装タスクリスト
│   └── steering/           # 開発ルール
│       ├── task-management.md
│       ├── development-workflow.md
│       └── environment-and-communication.md
├── requirements.txt        # Python依存パッケージ
├── setup.py                # インストール設定
├── LICENSE                 # ライセンス
└── version.txt             # バージョン情報
```

---

## 🚀 クイックスタート（所要時間: 約10分）

### 前提条件
- Linux環境（AlmaLinux 9推奨）
- Python 3.10以上
- Git

### 1. インストール

```bash
# リポジトリをクローン（1分）
git clone https://github.com/kamonabe/Komon.git
cd Komon

# 依存パッケージをインストール（2分）
pip install -r requirements.txt

# または開発モードでインストール
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
# リソース監視
python scripts/main.py

# ステータス確認
python scripts/status.py

# 対話型アドバイザー
python scripts/advise.py

# 通知履歴を表示
python scripts/advise.py --history

# 直近10件の通知履歴のみ表示
python scripts/advise.py --history 10

# 週次健全性レポート
python scripts/weekly_report.py
```

### Slack通知の設定（オプション）

Slack通知を使う場合は、Webhook URLを取得してください：

1. [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)にアクセス
2. "Create New App" → "Incoming Webhooks"を選択
3. URLをコピーして`settings.yml`の`notifications.slack.webhook_url`に設定

**注意**: Slack通知は必須ではありません。通知なしでも`komon advise`コマンドで状態確認できます。

### 主な機能

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

- [詳細ドキュメント](docs/README.md)
- [システム仕様書](.kiro/specs/komon-system.md)
- [変更履歴](docs/CHANGELOG.md)
- [セキュリティガイド](docs/SECURITY.md) - 認証情報の管理、ファイルパーミッション、セキュリティベストプラクティス

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

**テストカバレッジ: 94%** (238テスト、全てパス)

詳細は [tests/README.md](tests/README.md) を参照してください。

---

## 🐧 対応プラットフォーム

Komonは**Linux環境での動作を前提**として開発されています。

- **主な対象**: AlmaLinux、RHEL系、Ubuntu、Debian系など
- **動作確認環境**: AlmaLinux 9

### Windows / macOS について

現時点では、作者自身がWindows版やmacOS版を開発する予定はありません。
ただし、フォークして他のプラットフォーム向けに移植していただくことは大歓迎です！

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
