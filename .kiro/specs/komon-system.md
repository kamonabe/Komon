---
title: Komon - 軽量サーバ監視システム
status: reverse-engineered
version: 1.10.1
created: 2025-11-21
updated: 2025-11-22
---

# Komon - 軽量アドバイザー型SOAR風監視ツール

## 概要

Komonは、開発者のための軽量アドバイザー型SOAR風ツールです。開発環境で発生するリソースの過剰使用、ログの急増、更新忘れなどを静かに見守り、必要なときだけやさしく通知・提案します。

### 設計思想
- 過剰監視しすぎず、必要な時だけ知らせる
- 内部構造がシンプルで拡張が容易
- 小規模な開発環境や個人サーバでも手軽に導入可能

### 想定ユースケース
- VPSや自宅サーバで常駐させ、自作スクリプトの影響を見守る
- 開発中のコードがどれだけリソースを消費するかを事前に把握
- ログ急増をSlackでやさしく教えてくれる存在

---

## システムアーキテクチャ

### プロジェクト構造

```
Komon/
├── src/komon/              # コアモジュール
│   ├── __init__.py
│   ├── monitor.py          # リソース使用率の収集
│   ├── analyzer.py         # 閾値判定とアラート生成
│   ├── history.py          # 使用履歴の保存・ローテーション
│   ├── notification.py     # Slack/メール通知
│   ├── log_watcher.py      # ログファイルの差分監視
│   ├── log_analyzer.py     # ログ異常検知
│   ├── log_trends.py       # ログ傾向分析（時系列比較）
│   ├── settings_validator.py  # 設定ファイルの検証
│   └── cli.py              # CLIエントリーポイント
├── scripts/                # 実行スクリプト
│   ├── main.py
│   ├── main_log_monitor.py
│   ├── main_log_trend.py
│   ├── advise.py
│   ├── initial.py
│   ├── status.py
│   ├── komon_guide.py
│   └── init.sh
├── config/                 # 設定ファイル
│   └── settings.yml.sample
├── docs/                   # ドキュメント
│   ├── README.md
│   ├── CHANGELOG.md
│   └── SECURITY.md
├── tests/                  # テストコード
├── data/                   # データ保存先（自動生成）
│   ├── usage_history/
│   └── logstats/
└── .kiro/specs/            # 仕様書
    └── komon-system.md
```

### 実行スクリプト

| スクリプト | 用途 | 推奨実行間隔 |
|-----------|------|-------------|
| `main.py` | リソース使用率監視 | 5分おき |
| `main_log_monitor.py` | ログ急増検知 | 5〜10分おき |
| `main_log_trend.py` | ログ傾向分析 | 1日1回 |
| `advise.py` | 対話型アドバイザー | 手動実行 |
| `initial.py` | 初期設定ウィザード | 初回のみ |
| `status.py` | 現在のステータス表示 | 手動実行 |
| `komon_guide.py` | ガイドメニュー | 手動実行 |

---

## 機能仕様

### 1. リソース監視機能

#### 1.1 監視対象
- **CPU使用率**: psutilによる全体使用率取得
- **メモリ使用率**: 物理メモリの使用率
- **ディスク使用率**: ルートパーティションの使用率
- **プロセス別詳細**: 上位5件のCPU/メモリ使用プロセス

#### 1.2 閾値判定
```yaml
thresholds:
  cpu: 85      # CPU使用率の警告閾値（%）
  mem: 80      # メモリ使用率の警告閾値（%）
  disk: 80     # ディスク使用率の警告閾値（%）
  proc_cpu: 20 # プロセス単位の高負荷判定閾値（%）
```

#### 1.3 履歴管理
- 使用率データをCSV/JSON形式で保存
- 最大95世代まで自動ローテーション
- プロセス別CPU情報も履歴に含める（v1.5.0〜）

### 2. ログ監視機能

#### 2.1 ログ急増検知（main_log_monitor.py）
- 前回実行時からの差分行数を取得
- 設定された閾値を超えた場合に警告
- 監視対象ログはsettings.ymlで設定可能

```yaml
log_monitor_targets:
  /var/log/messages: true
  /var/log/nginx/error.log: true
  systemd journal: false
```

#### 2.2 ログ傾向分析（main_log_trend.py）
- 過去の履歴データと比較してトレンドを検知
- 前日比での急増率を計算
- 複数日にわたる急増パターンの検出

```yaml
log_analysis:
  anomaly_threshold_percent: 30    # 急増とみなす割合（前日比）
  baseline_learning_rate: 0.1      # ベースライン更新の反映率
```

### 3. 通知機能

#### 3.1 Slack通知
- Incoming Webhookを使用
- リソース閾値超過時に即時通知
- ログ急増時に通知

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/xxxx/yyyy/zzzz"
```

#### 3.2 メール通知
- SMTP経由でメール送信
- TLS/STARTTLS対応
- パスワードは環境変数からの読み込みを推奨

```yaml
notifications:
  email:
    enabled: false
    smtp_server: "smtp.example.com"
    smtp_port: 587
    use_tls: true
    from: "komon@example.com"
    to: "user@example.com"
    username: "komon@example.com"
    password: "env:KOMON_EMAIL_PASSWORD"
```

### 4. 対話型アドバイザー機能（advise.py）

#### 4.1 提供される助言
1. **OSアップデート確認**
   - セキュリティパッチの有無確認（dnf updateinfo）
   - 通常パッケージの更新確認
   - 対話的な適用プロンプト

2. **リソース使用状況の分析**
   - 高メモリ使用プロセスの表示
   - 高CPU使用プロセスの詳細情報
   - ディスク整理の提案

3. **稼働時間チェック**
   - 長期稼働時の再起動提案
   - 本番/開発環境で文言を出し分け

4. **通知設定の確認**
   - メール通知が無効な場合の提案

5. **ログ傾向の分析**
   - 複数日にわたる急増パターンの検出
   - logrotate設定の見直し提案

6. **プロセス詳細情報**
   - 高負荷プロセスの詳細表示（PID、ユーザー、起動時間、コマンドライン）

#### 4.2 助言スキップ機能（v1.1.0〜）
- ユーザーが「n」を選択した助言を7日間非表示
- `komon_data/skip_advices.json`に記録
- 一定期間後に再提案される仕組み

### 5. 初期設定機能（initial.py）

#### 5.1 対話型セットアップ
- 閾値の設定（CPU/メモリ/ディスク）
- Slack通知の有効化とWebhook URL設定
- メール通知の有効化
- settings.ymlの自動生成

#### 5.2 既存設定の保護
- settings.ymlが既に存在する場合はスキップ

### 6. ステータス表示機能（status.py）

表示内容：
- リソース使用率と閾値
- 通知設定の状態
- ログ監視対象の一覧

### 7. ガイド機能（komon_guide.py）

対話型メニューで以下を案内：
1. Komonの全体像
2. 初期セットアップ手順
3. スクリプト一覧と使い方
4. cron登録の例
5. 通知設定の方法
6. よくある質問とトラブル対応

---

## データ構造

### 履歴データ保存先
```
data/
├── logstats/
│   ├── var_log_messages.pkl        # ログ統計データ
│   ├── systemd_journal.pkl
│   └── history/
│       ├── var_log_messages.json   # ログ履歴
│       └── systemd_journal.json
└── usage_history/
    ├── usage_001.csv               # リソース使用履歴
    ├── usage_002.csv
    └── ...（最大95世代）
```

### スキップ記録
```json
{
  "email_disabled": {
    "skipped_at": "2025-11-21T10:30:00"
  },
  "komon_update": {
    "skipped_at": "2025-11-20T15:45:00"
  }
}
```

---

## 技術スタック

### 動作環境
- **OS**: Linux（AlmaLinux 9で開発・動作確認）
  - RHEL系、Debian系、Ubuntu等でも動作想定
  - **Windows/macOSは対象外**（コミュニティによる移植は歓迎）
- **Python**: 3.9以上（3.11で動作確認済）

### 依存ライブラリ
```
psutil>=5.9.0      # システムリソース情報取得
PyYAML>=6.0        # 設定ファイル読み込み
requests>=2.31.0   # Slack通知用HTTP通信
```

### プラットフォーム方針

Komonは作者がLinux環境で実際に使用するために開発されています。
そのため、以下の方針で開発を進めています：

- **Linux環境での実用性を最優先**
- Linux固有の機能（systemd、dnf/apt等）を積極的に活用
- Windows/macOS対応は作者自身では行わない
- ただし、フォークによる移植は大歓迎

この方針により、Linux環境での品質と機能性を高く保つことができます。

---

## 運用方法

### Cron設定例
```bash
# リソース監視（5分おき）
*/5 * * * * cd /path/to/Komon && python scripts/main.py >> log/cron_main.log 2>&1

# ログ急増監視（5分おき）
*/5 * * * * cd /path/to/Komon && python scripts/main_log_monitor.py >> log/cron_monitor.log 2>&1

# ログ傾向分析（毎日3時）
0 3 * * * cd /path/to/Komon && python scripts/main_log_trend.py >> log/cron_trend.log 2>&1
```

### インストール

```bash
# 開発モードでインストール
pip install -e .

# または通常インストール
pip install .
```

### 手動実行

```bash
# インストール後
komon initial    # 初期設定
komon status     # ステータス確認
komon advise     # 対話型アドバイス
komon guide      # ガイド表示

# または直接実行
python scripts/initial.py
python scripts/status.py
python scripts/advise.py
python scripts/komon_guide.py
```

---

## セキュリティ考慮事項

1. **パスワード管理**
   - メール通知のパスワードは環境変数から読み込み
   - settings.ymlに平文で保存しない

2. **Webhook URL**
   - Slack Webhook URLは機密情報として扱う
   - リポジトリにコミットしない（.gitignore推奨）

3. **ログファイルアクセス**
   - システムログの読み取りには適切な権限が必要
   - 必要に応じてsudo権限での実行を検討

---

## 拡張性

### 通知手段の追加
- `komon/notification.py`に新しい通知関数を追加
- settings.ymlに対応する設定セクションを追加

### 監視項目の追加
- `komon/monitor.py`に新しい収集関数を追加
- `komon/analyzer.py`に対応する分析ロジックを追加

### 新しいログソースの追加
- `log_monitor_targets`に新しいパスを追加
- systemd journal以外のログソースにも対応可能

---

## 既知の制限事項

1. **プラットフォーム制限**
   - **Linux専用**（Windows/macOSは非対応）
   - OSアップデート確認機能はdnf（AlmaLinux/RHEL系）に依存
   - 他のディストリビューションでは一部機能が動作しない可能性
   - `/var/log`等のLinux標準パスを前提

2. **履歴データの上限**
   - 使用履歴は95世代まで（それ以上は自動削除）
   - 長期的なトレンド分析には外部ツールとの連携が必要

3. **リアルタイム性**
   - cron実行間隔に依存するため、完全なリアルタイム監視ではない
   - 瞬間的なスパイクは検知できない可能性

### 制限事項に対する方針

これらの制限は、意図的な設計判断です：

- **Linux専用**: 作者が実際に使用する環境に集中することで、品質を高く保つ
- **シンプルな履歴管理**: 複雑なデータベースを避け、保守性を優先
- **cron実行**: デーモン化せず、既存のcronインフラを活用

他のプラットフォームへの対応や、より高度な機能が必要な場合は、
フォークして独自に開発していただくことを推奨します。

---

## バージョン履歴

- **v1.10.1** (2025-11-22): 通知メッセージの口調改善（やさしい相談口調に変更）、テストカバレッジ95%達成（93テスト）、CIFS/SMB環境でのカバレッジ測定問題を解決
- **v1.10.0** (2025-11-21): プロジェクト構造の大幅整理（src/komon/、scripts/への移動）、テストコード追加（46テスト）、仕様駆動開発の基盤整備（specs/配下の文書化）
- **v1.9.0**: 初期バージョン（詳細は過去のコミット履歴を参照）
- **v1.7.0**: 高負荷プロセスの詳細表示機能追加
- **v1.6.0**: OSパッチ提案に具体的なコマンド追加
- **v1.5.0**: 使用履歴にプロセス別CPU情報を追加
- **v1.1.0**: 助言の一時スキップ機能追加
- **v1.0.0**: 初期リリース

---

## ライセンス

MIT License - 個人・商用利用、改変・再配布が自由

---

## 作者

開発者: [@kamonabe](https://github.com/kamonabe)

「自分が欲しいと思ったものを形にして公開してみる」がこのプロジェクトの原点です。
