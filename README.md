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
| ✅ pip / OS更新の提案                  | 実装済              | `sudo apt update` の提案など |
| ✅ systemctl 再起動の提案              | 実装済              | 本番・開発環境で文言を出し分け |
| ✅ バージョン管理（`version.txt`）     | 実装済              | 手動更新で管理 |
| ✅ CHANGELOGによる更新履歴記録        | 実装済              | `CHANGELOG.md` に追記形式で管理 |

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
  usage: "dev"  # "production" または "dev"

thresholds:
  cpu: 85
  mem: 80
  disk: 80

log_analysis:
  anomaly_threshold_percent: 30  # ログ傾向の増加を警戒とみなす割合（%）
  baseline_learning_rate: 0.1    # ベースライン更新時の学習率（10%）

notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/xxxx/yyyy/zzzz"
  email:
    enabled: false
    smtp_server: "smtp.example.com"
    smtp_port: 587
    from: "komon@example.com"
    to: "user@example.com"
    username: "komon@example.com"
    password: "env:KOMON_EMAIL_PASSWORD"

log_monitor_targets:
  /var/log/messages: true
  /var/log/syslog: false
  /var/log/nginx/error.log: true
  systemd journal: false
```

---

## 📊 保存と通知の仕組み

- **リソース閾値超過時**は即時通知（Slack／メール）
- **ログ傾向の急増**も履歴と比較して通知対象に
- **履歴ファイル（CSVやJSON）**は最大95件まで自動ローテーション保存
- 通知方式は個別にON/OFF切り替え可能

---

## 📁 ディレクトリ構成（例）

```
Komon/
├── main.py
├── advise.py
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
│   └── settings_validator.py
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

## 💬 今後のロードマップ

- [x] ログ急増検知（ベースライン比較）
- [x] 使用履歴からの異常傾向検出（スパイク通知）
- [x] `komon advise` による対話型通知
- [x] pip / OS更新の提案（自動実行は行わない）
- [x] systemctlの再起動／任意コマンドの提案
- [ ] komon_error.logの異常自動検知

---

## 🚀 導入方法（開発中）

```bash
git clone https://github.com/kanonabe/Komon.git
cd Komon
python main.py
```

※ `settings.yml` をルートディレクトリに配置してから実行してください。

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
