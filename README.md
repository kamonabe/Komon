# Komon（顧問）

**Komon は、開発者のための軽量アドバイザー型SOAR風ツールです。**

開発環境で発生するリソースの過剰使用、ログの急増、更新忘れなどを静かに見守り、必要なときだけやさしく通知・提案してくれます。

🛠 Komon は内部構造がシンプルなため、通知手段の追加や監視項目の拡張が容易です。

---

## 📁 プロジェクト構造

```
Komon/
├── src/komon/              # コアモジュール
│   ├── monitor.py          # リソース監視
│   ├── analyzer.py         # 閾値判定・分析
│   ├── notification.py     # 通知機能
│   ├── history.py          # 履歴管理
│   ├── log_watcher.py      # ログ監視
│   ├── log_analyzer.py     # ログ分析
│   ├── log_trends.py       # ログ傾向分析
│   ├── settings_validator.py  # 設定検証
│   └── cli.py              # CLIエントリーポイント
├── scripts/                # 実行スクリプト
│   ├── main.py             # リソース監視メイン
│   ├── main_log_monitor.py # ログ急増監視
│   ├── main_log_trend.py   # ログ傾向分析
│   ├── advise.py           # 対話型アドバイザー
│   ├── initial.py          # 初期設定
│   ├── status.py           # ステータス表示
│   ├── komon_guide.py      # ガイドメニュー
│   └── init.sh             # 初期化スクリプト
├── config/                 # 設定ファイル
│   └── settings.yml.sample # 設定サンプル
├── docs/                   # ドキュメント
│   ├── README.md           # 詳細ドキュメント
│   ├── CHANGELOG.md        # 変更履歴
│   └── SECURITY.md         # セキュリティ情報
├── tests/                  # テストコード（今後追加予定）
├── data/                   # データ保存先（自動生成）
│   ├── usage_history/      # リソース使用履歴
│   └── logstats/           # ログ統計データ
├── .kiro/                  # Kiro IDE設定
│   ├── specs/              # 仕様書
│   │   ├── komon-system.md     # システム仕様
│   │   ├── future-ideas.md     # 将来の改善案
│   │   └── testing-strategy.md # テスト戦略
│   └── tasks/              # タスク管理
│       └── implementation-tasks.md # 実装タスクリスト
├── requirements.txt        # Python依存パッケージ
├── setup.py                # インストール設定
├── LICENSE                 # ライセンス
└── version.txt             # バージョン情報
```

---

## 🚀 クイックスタート

### 1. インストール

```bash
# リポジトリをクローン
git clone https://github.com/kamonabe/Komon.git
cd Komon

# 依存パッケージをインストール
pip install -r requirements.txt

# または開発モードでインストール
pip install -e .
```

### 2. 初期設定

```bash
# 初期設定ウィザードを実行
python scripts/initial.py

# または（インストール済みの場合）
komon initial
```

### 3. 実行

```bash
# リソース監視
python scripts/main.py

# ステータス確認
python scripts/status.py

# 対話型アドバイザー
python scripts/advise.py
```

---

## ⚙️ 設定

`settings.yml`を作成して、監視項目や通知設定をカスタマイズできます。

サンプルファイル: `config/settings.yml.sample`

```yaml
thresholds:
  cpu: 85
  mem: 80
  disk: 80

notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/..."
  email:
    enabled: false
```

詳細は [docs/README.md](docs/README.md) を参照してください。

---

## 🕒 定期実行（Cron）

```bash
# リソース監視（5分おき）
*/5 * * * * cd /path/to/Komon && python scripts/main.py >> log/main.log 2>&1

# ログ監視（5分おき）
*/5 * * * * cd /path/to/Komon && python scripts/main_log_monitor.py >> log/monitor.log 2>&1

# ログ傾向分析（毎日3時）
0 3 * * * cd /path/to/Komon && python scripts/main_log_trend.py >> log/trend.log 2>&1
```

---

## 📚 ドキュメント

- [詳細ドキュメント](docs/README.md)
- [システム仕様書](.kiro/specs/komon-system.md)
- [変更履歴](docs/CHANGELOG.md)

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

**テストカバレッジ: 95%** (93テスト、全てパス)

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
