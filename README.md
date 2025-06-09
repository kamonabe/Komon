# Komon（顧問）

**Komon は、開発者のための軽量アドバイザー型SOAR風ツールです。**
開発環境で発生するリソースの過剰使用、ログの急増、更新忘れなどを静かに見守り、
必要なときだけやさしく通知・提案してくれます。

🛠 Komon は内部構造がシンプルなため、通知手段の追加や監視項目の拡張が容易です。

---

## 🔧 特徴（機能ステータス）

| 機能                                 | 状況                | 備考 |
|--------------------------------------|---------------------|------|
| ✅ CPU / メモリ / ディスクの監視      | 実装済              | `psutil` による取得・分析 |
| ✅ 閾値判定と警戒通知                 | 実装済              | `settings.yml` で設定可能 |
| ✅ Slack通知／メール通知              | 実装済              | 通知ON/OFF、両方対応 |
| ✅ 使用履歴の世代保存                 | 実装済              | 最大95世代まで自動ローテーション |
| ✅ ログ傾向分析（ログ量の推移比較）   | 実装済              | 履歴ベースで急増を検知。Slack／メール通知対応 |
| ✅ CLI通知（`advise.py` = `komon advise`） | 対話機能あり          | ログ傾向・使用率傾向・OS更新確認など複数の助言を表示 |
| ✅ 助言の一時スキップ機能              | v1.1.0で追加         | `skip_advices.json` に記録され、約1週間は非表示になります |
| ✅ pip / OS更新の提案                  | 実装済              | `sudo apt update` の提案など |
| ✅ systemctl 再起動の提案              | 実装済              | 本番・開発環境で文言を出し分け |
| ✅ バージョン管理（`version.txt`）     | 実装済              | 手動更新で管理 |
| ✅ CHANGELOGによる更新履歴記録        | 実装済              | `CHANGELOG.md` に追記形式で管理 |
| ✅ 使用履歴にプロセス別CPU情報を追加        | v1.5.0で追加         | 上位5件のプロセス名＋使用率を記録・表示 |
| ✅ OSパッチ提案に具体コマンドを追加         | v1.6.0で改善         | `sudo dnf update` などの提案付きで実行方法が明確に |


---

## 🌟 想定ユースケース

- **VPSや自宅サーバ**で常駐させ、自作スクリプトの影響を見守る
- 開発中のコードが**どれだけリソースを消費するか**を事前に把握
- **昨日ログ急増してたよ**とSlackでやさしく教えてくれる存在

※ Komon は「過剰監視しすぎず、必要な時だけ知らせる」設計思想で開発されています。

---

## ⚙️ 設定ファイル（`settings.yml`）

```yaml
profile:
  usage: "dev"  # "production" または "dev"。本番環境では一部の助言が変化します。

thresholds:  # リソース使用率に対する警告の閾値（％）
  cpu: 85    # CPU 使用率がこの値を超えると警告します
  mem: 80    # メモリ使用率の閾値
  disk: 80   # ディスク使用率の閾値

notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/xxxx/yyyy/zzzz"  # Slack の Webhook URL

  email:
    enabled: false  # メール通知を有効にする場合は true にしてください
    smtp_server: "smtp.example.com"  # SMTP サーバのホスト名
    smtp_port: 587
    use_tls: true  # STARTTLS を使うかどうか
    from: "komon@example.com"
    to: "user@example.com"
    username: "komon@example.com"
    password: "env:KOMON_EMAIL_PASSWORD"  # パスワードは環境変数からの読み込みを推奨

log_monitor_targets:  # 監視対象のログファイル（true: 監視する / false: 無視する）
  /var/log/messages: true
  /var/log/nginx/error.log: true
  systemd journal: false  # systemd journal を監視する場合は true に

  # 任意で追加のログも指定可能（絶対パス推奨）
  # /home/user/logs/custom.log: true

log_analysis:
  anomaly_threshold_percent: 30     # 急増とみなす割合（前日比）
  baseline_learning_rate: 0.1       # ベースライン更新の反映率（0〜1）
```

---

## 📊 保存と通知の仕組み

- **リソース閾値超過時**は即時通知（Slack／メール）
- **ログ傾向の急増**も履歴と比較して通知対象に
- **履歴ファイル（CSVやJSON）**は最大95件まで自動ローテーション保存
- 通知方式は個別にON/OFF切り替え可能

---

## 🗨️ Komonの改善提案スキップについて

`komon advise` は、実行時に様々なシステム改善の提案（助言）を行いますが、
「今回は必要ない」「当面対応しない」といった提案に対しては `n`（いいえ）を選ぶことで、
**最大7日間、その助言をスキップ（非表示）**することができます。

この情報は `skip_advices.json` に記録され、Komonが定期的にチェックします。
一時的に非表示にしても、その後一定期間をおいて再提案される仕組みです。

---

## 📁 ディレクトリ構成（例）

```
Komon/
├── main.py
├── advise.py
├── initial.py
├── komon_guide.py
├── main_log_monitor.py
├── main_log_trend.py
├── settings.yml
├── version.txt
├── CHANGELOG.md
├── komon/
│   ├── analyzer.py
│   ├── history.py
│   ├── monitor.py
│   ├── notification.py
│   ├── log_watcher.py
│   ├── log_analyzer.py
│   ├── log_trends.py
│   ├── settings_validator.py
│   └── cli.py
├── data/
│   └── logstats/
│       ├── var_log_messages.pkl
│       ├── systemd_journal.pkl
│       └── history/
│           ├── var_log_messages.json
│           └── systemd_journal.json
├── log/
│   └── komon_error.log
└── README.md
```

---

## 🕒 Cron による定期実行（例）

| 対象スクリプト        | 推奨間隔   | 用途                     |
|------------------------|------------|--------------------------|
| `main.py`              | 5分おき    | リソース使用率の監視     |
| `main_log_monitor.py`  | 5〜10分おき | ログ急増（行数）の検知   |
| `main_log_trend.py`    | 1日1回     | ログ傾向の中長期比較     |

例：

```bash
*/5 * * * * cd /your/path/to/Komon && /usr/bin/python3 main.py >> log/cron_main.log 2>&1
*/5 * * * * cd /your/path/to/Komon && /usr/bin/python3 main_log_monitor.py >> log/cron_monitor.log 2>&1
0 3 * * * cd /your/path/to/Komon && /usr/bin/python3 main_log_trend.py >> log/cron_trend.log 2>&1
```

---

## 🚀 最初の5分でできる導入方法

Komon の導入はとてもシンプルです。以下のコマンドを順番に実行してください：

```bash
git clone https://github.com/kamonabe/Komon.git
cd Komon
bash init.sh
komon initial # または /usr/bin/python3 initial.py
komon advise # または /usr/bin/python3 advise.py
```

これだけで初期設定とサンプル実行が完了し、Slack通知やログ監視などの基本動作を確認できます。
通知・監視対象の詳細設定は settings.yml で変更可能です。

---

## 📄 ライセンス

MIT License により、個人・商用利用、改変・再配布が自由に許可されています。

---

## ✨ Komonの進化

このプロジェクトは Kamonabe によって作られました。
改変や派生を通じて、別の名前で新しく育っていくことも大歓迎です。
その場合はご自由にどうぞ。
ただ、もし完全に同じ内容をコピーする場合は、クレジットを残していただけると嬉しいです。

---

## 👤 作者について

開発者：[@kamonabe](https://github.com/kamonabe)
「自分が欲しいと思ったものを形にして公開してみる」がこのプロジェクトの原点です。

