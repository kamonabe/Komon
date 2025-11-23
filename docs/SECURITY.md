# 🛡️ Security Policy

## � 脆弱性の報告について

Komon は個人開発プロジェクトですが、もしこのソフトウェアに脆弱性や重大なバグを発見された場合は、以下の方法でご連絡いただけると助かります。

- GitHub Issues を使用して公開報告する（推奨）
- 公開が適さない場合は、[GitHubのPrivate Vulnerability Reporting](https://github.com/kamonabe/Komon/security/advisories)（※有効化されていれば）をご利用ください。

## 🛠 修正方針

- 再現性のある脆弱性については、確認後できる限り早急に修正を行います。
- 報告内容が Komon の思想や設計範囲外である場合、対応を見送る可能性があります（例：GUI未対応など）。

## 🔐 対応の対象外となるもの（例）

- 古いPythonバージョンでのみ発生する非互換問題
- 外部環境に強く依存するセキュリティリスク（例：cron設定の権限）
- Komon 本体の使用方法外での想定外利用

---

## 🔒 セキュリティのベストプラクティス

Komonを安全に運用するための推奨事項です。

### 1. 認証情報の管理

#### Slack Webhook URL

Komonでは、Webhook URLの設定方法を2つから選べます：

**方法A: 環境変数を使う（推奨）**

`settings.yml`に`env:`で始まる値を書くと、環境変数から読み込みます：

```yaml
# settings.yml
notifications:
  slack:
    webhook_url: "env:KOMON_SLACK_WEBHOOK"  # ← env:で始まる
```

```bash
# 環境変数で設定
export KOMON_SLACK_WEBHOOK="https://hooks.slack.com/services/xxxx/yyyy/zzzz"

# または .bashrc / .bash_profile に追加して永続化
echo 'export KOMON_SLACK_WEBHOOK="https://hooks.slack.com/services/xxxx/yyyy/zzzz"' >> ~/.bashrc
```

**メリット**:
- ✅ 設定ファイルに機密情報を書かない
- ✅ Gitにコミットしても安全
- ✅ 環境ごとに異なる値を使える（dev/staging/production）

---

**方法B: 直接記載する（シンプル）**

`settings.yml`に直接URLを書くこともできます：

```yaml
# settings.yml
notifications:
  slack:
    webhook_url: "https://hooks.slack.com/services/xxxx/yyyy/zzzz"  # ← 直接記載
```

**メリット**:
- ✅ シンプルで分かりやすい
- ✅ 環境変数の設定が不要

**注意点**:
- ⚠️ `.gitignore`に`settings.yml`を追加して、Gitにコミットしないようにする
- ⚠️ 個人開発や、設定ファイルを共有しない環境向け

---

**どちらを選ぶべき？**

- **チーム開発・本番環境**: 方法A（環境変数）を推奨
- **個人開発・開発環境**: 方法B（直接記載）でもOK（ただし`.gitignore`で保護）

#### メールパスワード

メールパスワードも同様に、環境変数または直接記載が選べます：

**推奨: 環境変数を使用**
```yaml
# settings.yml
notifications:
  email:
    password: "env:KOMON_EMAIL_PASSWORD"  # ← env:で始まる
```

```bash
# 環境変数で設定
export KOMON_EMAIL_PASSWORD="your_password_here"
```

**仕組み**: `env:`で始まる値は、自動的に環境変数から読み込まれます。

### 2. ファイルパーミッション

#### settings.yml の保護
```bash
# 所有者のみ読み書き可能に設定
chmod 600 settings.yml

# 確認
ls -la settings.yml
# -rw------- 1 user user 1234 Nov 23 10:00 settings.yml
```

#### データディレクトリの保護
```bash
# dataディレクトリ全体を保護
chmod 700 data/
chmod 600 data/notifications/queue.json

# ログディレクトリも同様に
chmod 700 log/
chmod 600 log/*.log
```

### 3. cron実行時のセキュリティ

#### 環境変数の引き継ぎ
```bash
# crontabで環境変数を設定
# crontab -e

# 環境変数を定義
KOMON_SLACK_WEBHOOK=https://hooks.slack.com/services/xxxx/yyyy/zzzz
KOMON_EMAIL_PASSWORD=your_password_here

# Komon実行
*/5 * * * * cd /path/to/Komon && /usr/bin/python3 scripts/main.py >> log/main.log 2>&1
```

#### 実行ユーザーの制限
```bash
# 専用ユーザーで実行（推奨）
sudo useradd -r -s /bin/bash komon
sudo chown -R komon:komon /path/to/Komon

# komon ユーザーのcrontabに設定
sudo crontab -u komon -e
```

### 4. ログファイルアクセス権限

Komonは `/var/log/` 配下のログを監視するため、適切な権限が必要です。

#### 方法1: adm グループに追加（推奨）
```bash
# ユーザーを adm グループに追加
sudo usermod -aG adm $USER

# 再ログインして確認
groups
# user adm cdrom sudo dip plugdev ...
```

#### 方法2: 特定ログファイルのみ読み取り許可
```bash
# 特定ログファイルの読み取り権限を付与
sudo chmod 644 /var/log/messages
sudo chmod 644 /var/log/nginx/error.log
```

#### 方法3: sudoを使用（非推奨）
```bash
# crontabでsudoを使う（セキュリティリスクあり）
*/5 * * * * cd /path/to/Komon && sudo /usr/bin/python3 scripts/main.py
```

**注意**: sudo実行は権限昇格のリスクがあるため、可能な限り避けてください。

### 5. 依存パッケージの管理

#### 定期的な更新
```bash
# 依存パッケージの更新確認
pip list --outdated

# 更新（慎重に）
pip install --upgrade psutil requests pyyaml

# または requirements.txt を更新
pip install -r requirements.txt --upgrade
```

#### 脆弱性スキャン
```bash
# pipのセキュリティチェック（pip-audit推奨）
pip install pip-audit
pip-audit

# または safety を使用
pip install safety
safety check
```

### 6. ネットワークセキュリティ

#### Slack Webhook の保護
- Webhook URLは**秘密情報**として扱う
- Gitリポジトリにコミットしない
- `.gitignore` に `settings.yml` を追加

```bash
# .gitignore に追加
echo "settings.yml" >> .gitignore
echo "data/" >> .gitignore
echo "log/" >> .gitignore
```

#### SMTP接続の暗号化
```yaml
# settings.yml
notifications:
  email:
    use_tls: true  # 必ずTLSを有効化
    smtp_port: 587  # STARTTLS用ポート
```

### 7. データ保護

#### 通知履歴の定期クリーンアップ
```bash
# 古い通知履歴を削除（90日以上前）
find data/notifications/ -name "*.json" -mtime +90 -delete

# ログファイルのローテーション
find log/ -name "*.log" -mtime +30 -delete
```

#### バックアップ
```bash
# 設定ファイルのバックアップ
cp settings.yml settings.yml.backup

# データディレクトリのバックアップ
tar -czf komon_backup_$(date +%Y%m%d).tar.gz settings.yml data/
```

### 8. 最小権限の原則

Komonは以下の権限のみを必要とします：

**必要な権限**:
- `/var/log/` 配下のログファイル読み取り
- `data/` ディレクトリへの書き込み
- `log/` ディレクトリへの書き込み
- ネットワーク接続（Slack/メール通知時）

**不要な権限**:
- root権限（通常は不要）
- システムファイルの書き込み
- 他ユーザーのファイルアクセス

---

## 🚨 既知の制限事項

### 1. Webhook URLの露出リスク
- `settings.yml` をGitにコミットすると、Webhook URLが漏洩する可能性があります
- 必ず環境変数を使用するか、`.gitignore` に追加してください

### 2. ログファイルの機密情報
- 監視対象のログファイルに機密情報が含まれる場合、Komonの通知にも含まれる可能性があります
- ログ急増時の末尾抜粋表示（将来実装予定）では特に注意が必要です

### 3. cron実行時の環境変数
- cronは通常のシェル環境とは異なるため、環境変数が引き継がれない場合があります
- crontab内で明示的に環境変数を設定してください

### 4. 平文パスワード
- 現在、メールパスワードは環境変数で管理していますが、プロセス一覧から見える可能性があります
- より安全な方法として、キーリング（keyring）の使用を検討中です

---

## 📋 セキュリティチェックリスト

Komonを本番環境にデプロイする前に、以下を確認してください：

- [ ] `settings.yml` のパーミッションが `600` になっている
- [ ] Slack Webhook URLが環境変数で管理されている
- [ ] メールパスワードが環境変数で管理されている
- [ ] `.gitignore` に `settings.yml` が追加されている
- [ ] cron実行ユーザーが適切に設定されている
- [ ] ログファイルへのアクセス権限が最小限になっている
- [ ] 依存パッケージが最新版に更新されている
- [ ] `data/` と `log/` ディレクトリのパーミッションが適切
- [ ] バックアップ戦略が確立されている
- [ ] 定期的なセキュリティスキャンが計画されている

---

## 🔄 定期的なセキュリティメンテナンス

### 月次タスク
- [ ] 依存パッケージの脆弱性スキャン（`pip-audit`）
- [ ] ログファイルのクリーンアップ
- [ ] 通知履歴のクリーンアップ

### 四半期タスク
- [ ] 依存パッケージの更新
- [ ] Webhook URLのローテーション（必要に応じて）
- [ ] バックアップの動作確認

### 年次タスク
- [ ] セキュリティポリシーの見直し
- [ ] アクセス権限の監査
- [ ] 不要なログファイルの削除

---

## 🤝 協力のお願い

Komonは、あくまで個人の開発者が「自分のためにほしかった道具」として作っています。  
それでも多くの人に役立てば嬉しいと思っています。  
報告・改善提案・フィードバックなど、お気軽にお寄せください！

セキュリティに関する改善提案も大歓迎です。