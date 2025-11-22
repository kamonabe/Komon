# Komon 運用ガイド

このドキュメントでは、Komonの運用に関する情報を提供します。

## 環境構築

### Python環境の要件

**推奨バージョン：**
- Python 3.9以上（3.11で動作確認済み）
- AlmaLinux 9 / RHEL系 / Ubuntu / Debian系

### 仮想環境（venv）の使用

システムPythonを汚さないため、仮想環境の使用を推奨します。

#### 仮想環境の作成と有効化

```bash
# プロジェクトディレクトリに移動
cd /path/to/komon

# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt

# 開発用パッケージもインストールする場合
pip install -r requirements-dev.txt
```

#### 仮想環境の確認

```bash
# 仮想環境が有効か確認
which python
# 出力例: /path/to/komon/venv/bin/python

# Pythonバージョン確認
python --version
```

#### 仮想環境の無効化

```bash
deactivate
```

### システムPythonを使う場合

仮想環境を使わない場合は、システム全体にインストールします：

```bash
# システム全体にインストール
sudo pip3 install -r requirements.txt

# または、ユーザーローカルにインストール
pip3 install --user -r requirements.txt
```

**注意：** システムPythonを使う場合、他のプロジェクトとの依存関係の競合に注意してください。

### cron実行時の注意点

仮想環境を使用している場合、cronから実行する際は仮想環境のPythonを明示的に指定します：

```bash
# 仮想環境のPythonを使用
* * * * * cd /path/to/komon && /path/to/komon/venv/bin/python scripts/main.py >> log/main.log 2>&1

# または、仮想環境を有効化してから実行
* * * * * cd /path/to/komon && source venv/bin/activate && python scripts/main.py >> log/main.log 2>&1
```

システムPythonを使用している場合：

```bash
# システムPythonを使用
* * * * * cd /path/to/komon && python3 scripts/main.py >> log/main.log 2>&1
```

### 依存パッケージの確認

```bash
# インストール済みパッケージの確認
pip list

# 必要なパッケージが揃っているか確認
pip check

# requirements.txtとの差分確認
pip freeze | diff - requirements.txt
```

### パッケージの更新

```bash
# 依存パッケージを最新化
pip install --upgrade -r requirements.txt

# 特定のパッケージのみ更新
pip install --upgrade psutil
```

## ログ管理

### ログファイルの種類

Komonは以下のログファイルを生成します：

| ログファイル | 用途 | 生成タイミング |
|------------|------|--------------|
| `log/main.log` | メイン監視スクリプトの実行ログ | cron実行時の標準出力/エラー出力 |
| `log/komon_error.log` | 設定ファイル検証エラーログ | settings.yml検証失敗時 |

### ログローテーションの設定

Komonのログファイルは時間とともに増大するため、Linuxの標準機能である `logrotate` を使用した管理を推奨します。

#### logrotate設定例

`/etc/logrotate.d/komon` を作成し、以下の内容を記述します：

```
/path/to/komon/log/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    create 0644 your_user your_group
}
```

**設定の説明：**
- `daily`: 毎日ローテーション
- `rotate 7`: 7世代分保持
- `compress`: 古いログを圧縮（gzip）
- `delaycompress`: 1世代前のログは圧縮しない（直近の確認用）
- `missingok`: ログファイルが存在しなくてもエラーにしない
- `notifempty`: 空のログファイルはローテーションしない
- `copytruncate`: ファイルをコピーしてから切り詰める（プロセス再起動不要）
- `create`: 新しいログファイルのパーミッション設定

#### 設定の適用

```bash
# 設定ファイルを作成
sudo vi /etc/logrotate.d/komon

# 設定のテスト（実際には実行されない）
sudo logrotate -d /etc/logrotate.d/komon

# 手動で即座に実行（テスト用）
sudo logrotate -f /etc/logrotate.d/komon
```

#### カスタマイズ例

**週次ローテーション、30日分保持：**
```
/path/to/komon/log/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

**サイズベースのローテーション（10MB超過時）：**
```
/path/to/komon/log/*.log {
    size 10M
    rotate 5
    compress
    missingok
    notifempty
    copytruncate
}
```

## cron設定のベストプラクティス

### 推奨設定

```bash
# 1分ごとに監視実行
* * * * * cd /path/to/komon && python3 scripts/main.py >> log/main.log 2>&1
```

### 注意点

- **絶対パスの使用**: cronの環境変数は限定的なため、`cd`で作業ディレクトリを明示
- **ログ出力**: `>> log/main.log 2>&1` で標準出力とエラー出力の両方を記録
- **実行権限**: cronを実行するユーザーがKomonディレクトリとログディレクトリへの書き込み権限を持つこと

### cron設定の確認

```bash
# 現在のcron設定を確認
crontab -l

# cron設定を編集
crontab -e
```

## ディスク容量管理

### 容量確認

```bash
# ログディレクトリの使用量確認
du -sh /path/to/komon/log

# 詳細表示
du -h /path/to/komon/log/*
```

### 手動クリーンアップ

logrotateを設定していない場合や緊急時：

```bash
# 古いログを手動削除（7日以前）
find /path/to/komon/log -name "*.log" -mtime +7 -delete

# 古いログを圧縮
gzip /path/to/komon/log/*.log.1
```

## トラブルシューティング

### ログが出力されない

**確認項目：**
1. ディレクトリの書き込み権限
   ```bash
   ls -ld /path/to/komon/log
   ```

2. cronが実行されているか
   ```bash
   grep CRON /var/log/syslog
   ```

3. Pythonスクリプトが正常に動作するか
   ```bash
   cd /path/to/komon
   python3 scripts/main.py
   ```

### ログが肥大化している

1. logrotateが動作しているか確認
   ```bash
   sudo cat /var/log/logrotate.log
   ```

2. 手動でローテーション実行
   ```bash
   sudo logrotate -f /etc/logrotate.d/komon
   ```

### komon_error.logにエラーが記録される

`settings.yml` の設定に問題がある可能性があります：

```bash
# エラーログを確認
cat log/komon_error.log

# 設定ファイルを検証
python3 -c "from komon.settings_validator import validate_settings; validate_settings('settings.yml')"
```

## 監視とアラート

### ログ監視の追加

Komon自身のログもシステムログとして監視対象に追加できます：

```yaml
# settings.yml
log_monitoring:
  enabled: true
  paths:
    - /var/log/messages
    - /path/to/komon/log/komon_error.log  # Komon自身のエラーログも監視
```

### アラート通知の確認

通知が正常に送信されているか確認：

```bash
# main.logで通知送信の記録を確認
grep "警戒情報" log/main.log
```

## パフォーマンス最適化

### 実行頻度の調整

システムの負荷に応じてcronの実行頻度を調整：

```bash
# 軽量な監視: 5分ごと
*/5 * * * * cd /path/to/komon && python3 scripts/main.py >> log/main.log 2>&1

# 標準的な監視: 1分ごと（推奨）
* * * * * cd /path/to/komon && python3 scripts/main.py >> log/main.log 2>&1
```

### ログ出力の抑制

詳細なログが不要な場合：

```bash
# エラー出力のみ記録
* * * * * cd /path/to/komon && python3 scripts/main.py 2>> log/main.log
```

## バックアップ

### 設定ファイルのバックアップ

```bash
# 設定ファイルをバックアップ
cp settings.yml settings.yml.backup

# 日付付きバックアップ
cp settings.yml settings.yml.$(date +%Y%m%d)
```

### 履歴データのバックアップ

```bash
# 使用履歴データをバックアップ
tar czf komon_history_$(date +%Y%m%d).tar.gz history/
```

## セキュリティ

### ファイルパーミッション

```bash
# 推奨パーミッション設定
chmod 600 settings.yml          # 設定ファイル（機密情報含む）
chmod 755 log                   # ログディレクトリ
chmod 644 log/*.log             # ログファイル
```

### 機密情報の管理

`settings.yml` にはSlack Webhookやメールパスワードなどの機密情報が含まれます：

- バージョン管理システムにコミットしない（`.gitignore`に追加済み）
- 適切なファイルパーミッションを設定
- 定期的にWebhook URLやパスワードをローテーション

---

## 参考リンク

- [logrotate マニュアル](https://linux.die.net/man/8/logrotate)
- [cron 設定ガイド](https://crontab.guru/)
- [Komon プロジェクト構造](PROJECT_STRUCTURE.md)
