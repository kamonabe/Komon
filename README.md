# Komon（顧問）

**Komon は、開発者のための軽量アドバイザー型SOAR風ツールです。**  
開発環境で発生するリソースの過剰使用、ログの急増、更新忘れなどを静かに見守り、  
必要なときだけやさしく通知・提案してくれます。

Komon は CLI コマンド形式（`komon advise`, `komon status`）にも対応しており、日常的に扱いやすい設計です。

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
| ✅ CLI通知（`advise.py` = `komon advise`） | 対話機能あり      | ログ傾向・使用率傾向・OS更新確認など複数の助言を表示 |
| ✅ CLIステータス表示（`status.py` = `komon status`） | v1.3.0で追加 | 現在の使用率や通知設定・ログ監視対象を一覧表示 |
| ✅ 助言の一時スキップ機能              | v1.1.0で追加         | `skip_advices.json` に記録され、約1週間は非表示になります |
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
  anomaly_threshold_percent: 30
  baseline_learning_rate: 0.1

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

## 🧪 CLIコマンド一覧

Komon では以下のコマンドが使用できます：

| コマンド          | 内容                             |
|------------------|----------------------------------|
| `komon advise`   | 対話型の改善アドバイス機能を実行 |
| `komon status`   | 現在の監視状態を一覧表示         |

各コマンドは `python3 advise.py` や `python3 status.py` のように単体でも実行できます。

---

## 📊 保存と通知の仕組み

- リソース閾値超過時は即時通知（Slack／メール）
- ログ傾向の急増も履歴と比較して通知
- 履歴ファイルは最大95件まで自動ローテーション保存
- 通知方式は個別にON/OFF切り替え可能

---

## 🗨️ Komonの改善提案スキップについて

`komon advise` では、`n` を選ぶことで特定の助言を最大7日間非表示にできます。  
スキップ情報は `skip_advices.json` に記録され、期間経過後に再提示されます。

---

## 📁 ディレクトリ構成（例）

```
Komon/
├── main.py
├── advise.py
├── status.py
├── main_log_monitor.py
├── main_log_trend.py
├── settings.yml
├── version.txt
├── CHANGELOG.md
├── komon/
│   ├── cli.py
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
│       └── history/
├── log/
│   └── komon_error.log
└── README.md
```

---

## 🕒 Cron による定期実行（例）

```bash
*/5 * * * * cd /home/youruser/Komon && /usr/bin/python3 main.py >> log/cron_main.log 2>&1
*/5 * * * * cd /home/youruser/Komon && /usr/bin/python3 main_log_monitor.py >> log/cron_main_monitor.log 2>&1
0 3 * * * cd /home/youruser/Komon && /usr/bin/python3 main_log_trend.py >> log/cron_main_trend.log 2>&1
```

---

## 🚀 導入方法（開発中）

```bash
git clone https://github.com/kanonabe/Komon.git
cd Komon
pip install -e .
komon status
```

---

## 📄 ライセンス

MIT License により、個人・商用利用、改変・再配布が自由に許可されています。

---

## ⚠️ 免責事項

Komon は個人開発のプロジェクトであり、利用によって生じた問題や損害について、開発者（@kamonabe）は一切の責任を負いません。  
本ツールの利用・導入はすべてご自身の判断と責任にてお願いいたします。

うまく動かない場合もあるかもしれませんが、申し訳ありませんが対応できないこともあります。  
なるべく分かりやすい設計を心がけていますので、ソースコードを読みながらご自身での調整をお願いできればと思います。

---

## ✨ Komonの進化

このプロジェクトは、人間の開発者 Kamonabe と、AIの相棒（ChatGPT）による共同開発で育てられています。  
「こういうツールがほしいよね」という素朴な想いからスタートし、対話を重ねながらここまで形になってきました。

改変や派生を通じて、別の名前で新しく育っていくことも大歓迎です。  
その際、**完全に同じ内容をコピーする場合はクレジットを残していただけると嬉しいです。**

---

## 👤 作者について

開発者：[@kamonabe](https://github.com/kamonabe)  
「自分が欲しいと思ったものを形にして公開してみる」がこのプロジェクトの原点です。
