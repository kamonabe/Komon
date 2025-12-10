---
rule-id: ai-security-guardrails
priority: critical
applies-to:
- all
- spec-creation
- implementation
- code-review
triggers:
- always
- user-input
- file-upload
- code-generation
description: AI自身が機密情報を検知して警告するガードレール
---

---
rule-id: ai-security-guardrails
priority: critical
applies-to:
- all
- spec-creation
- implementation
- code-review
triggers:
- always
- user-input
- file-upload
- code-generation
description: AI自身が機密情報を検知して警告するガードレール
---

# AI セキュリティガードレール

## 基本方針

**Kiroは機密情報を検知したら、処理を中断してユーザーに警告する**

「過剰防衛くらいがちょうどいい」という原則に基づき、疑わしい情報は全て警告する。

## 🚨 検知すべき機密情報パターン

### 1. 認証情報（最優先）

**パターン**:
- APIキー: `AKIA[0-9A-Z]{16}`, `sk-[a-zA-Z0-9]{32,}`
- Webhook URL: `https://hooks.slack.com/services/`
- パスワード: `password\s*[:=]\s*["'][^"']+["']`
- トークン: `token\s*[:=]`, `bearer\s+[a-zA-Z0-9\-._~+/]+=*`
- 秘密鍵: `BEGIN PRIVATE KEY`, `BEGIN RSA PRIVATE KEY`

**検知時の対応**:
```
🚨 機密情報を検知しました

【検知内容】
- Slack Webhook URL
- ファイル: settings.yml (23行目)

【リスク】
この情報が漏洩すると、第三者があなたのSlackチャンネルに
メッセージを送信できます。

【推奨対応】
1. 環境変数に移行してください：
   webhook_url: "env:KOMON_SLACK_WEBHOOK"

2. コードを修正してください：
   環境変数から読み込むロジックを追加

3. 既存のWebhook URLを無効化してください

処理を中断します。安全化してから再度お試しください。
```

### 2. インフラ情報

**パターン**:
- プライベートIP: `10\.[0-9]+\.[0-9]+\.[0-9]+`, `192\.168\.`
- VPC CIDR: `172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]+\.[0-9]+`
- 内部ドメイン: `*.internal.*`, `*.local`, `*.corp`
- サーバー名: `prod-`, `staging-`, 実際のホスト名

**検知時の対応**:
```
⚠️ インフラ情報を検知しました

【検知内容】
- プライベートIPアドレス: 10.0.12.23
- 内部サーバー名: mss-prod-detector-01.internal.example.co.jp

【推奨対応】
抽象化してください：
- IPアドレス → <INTERNAL_IP>
- サーバー名 → secure-detector-node-A

このまま進めますか？（y/n）
```

### 3. 個人情報

**パターン**:
- メールアドレス: `[a-zA-Z0-9._%+-]+@(?!example\.com)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- 電話番号: `0[0-9]{1,4}-[0-9]{1,4}-[0-9]{4}`
- 実名: 文脈から判断（"田中太郎さん"等）

**検知時の対応**:
```
⚠️ 個人情報を検知しました

【検知内容】
- メールアドレス: tanaka@company.co.jp

【推奨対応】
ダミー値に置換してください：
- メールアドレス → user@example.com
- 実名 → <USER_NAME>
```

### 4. 本番ログ・機密ログ

**パターン**:
- "本番", "production", "prod"
- "顧客", "customer", "client"
- "社内", "internal", "confidential"
- 実際のログファイルパス

**検知時の対応**:
```
🚨 本番ログの可能性があります

【検知内容】
- "本番サーバのログです"という記述
- 実際のログファイルパス: /var/log/production/app.log

【リスク】
本番ログには個人情報や機密情報が含まれる可能性があります。

【推奨対応】
マスキング済みの擬似ログを作成してください：
1. 個人情報を <USER>, <EMAIL> に置換
2. IPアドレスを <IP> に置換
3. 顧客名を <CLIENT> に置換

処理を中断します。
```

### 5. 顧客・企業情報

**パターン**:
- 顧客名（文脈から判断）
- 社名（実在する企業名）
- プロジェクトコード
- 契約情報

**検知時の対応**:
```
⚠️ 顧客情報を検知しました

【検知内容】
- "A社へのアラートメール設定"

【推奨対応】
架空化してください：
- 顧客名 → Client-A, Customer-X
- 社名 → Example Corp
```

## 🛡️ 検知レベル

### Level 1: CRITICAL（処理を即座に中断）
- APIキー、パスワード、秘密鍵
- Webhook URL
- 本番ログ

### Level 2: WARNING（警告して確認）
- プライベートIP
- 内部ドメイン
- メールアドレス
- 顧客名

### Level 3: INFO（情報提供のみ）
- ファイルパスに"production"が含まれる
- 設定ファイルに実値が含まれる

## 🔍 検知タイミング

### 1. ユーザー入力時（最優先）
- ファイルアップロード時
- コピー＆ペースト時
- チャット入力時

### 2. Spec作成時
- requirements.yml作成時
- design.yml作成時
- tasks.yml作成時

### 3. コード実装時
- 設定ファイル生成時
- コード生成時
- テストデータ生成時

### 4. ドキュメント作成時
- README.md更新時
- CHANGELOG.md更新時

## 📝 安全化の推奨パターン

### パターン1: 環境変数化
```yaml
# ❌ 危険
webhook_url: "https://hooks.slack.com/services/XXX/YYY/ZZZ"

# ✅ 安全
webhook_url: "env:KOMON_SLACK_WEBHOOK"
```

### パターン2: 抽象化
```yaml
# ❌ 危険
server: "mss-prod-detector-01.internal.company.co.jp"
ip: "10.0.12.23"

# ✅ 安全
server: "secure-detector-node-A"
ip: "<INTERNAL_IP>"
```

### パターン3: ダミー値化
```yaml
# ❌ 危険
email: "tanaka@company.co.jp"
customer: "A社"

# ✅ 安全
email: "user@example.com"
customer: "Client-A"
```

### パターン4: マスキング
```bash
# ❌ 危険
2025-01-22 10:22:01 User tanaka logged in from 10.0.12.23

# ✅ 安全
2025-01-22 10:22:01 User <USER> logged in from <IP>
```

## 🚦 Kiroの動作フロー

```
1. ユーザー入力を受信
   ↓
2. 機密情報パターンをスキャン
   ↓
3. 検知した場合
   ├─ CRITICAL → 処理を中断、警告を表示
   ├─ WARNING → 警告を表示、確認を求める
   └─ INFO → 情報を表示、処理を継続
   ↓
4. 安全化の提案
   ↓
5. ユーザーが安全化
   ↓
6. 処理を再開
```

## 🎯 Kiroへの指示

### 常時監視

Kiroは以下を**常に監視**してください：

- [ ] APIキー、パスワード、秘密鍵
- [ ] Webhook URL
- [ ] プライベートIP、内部ドメイン
- [ ] メールアドレス（example.com以外）
- [ ] 本番ログの可能性
- [ ] 顧客名、社名

### 検知時の対応

1. **処理を中断**（CRITICALの場合）
2. **警告メッセージを表示**
3. **安全化の方法を提案**
4. **ユーザーの確認を待つ**

### 例外パターン

以下は検知しても警告しない：
- `example.com`, `localhost`, `127.0.0.1`
- サンプルコード内のダミー値
- ドキュメント内の説明用の例

## まとめ

- **過剰防衛くらいがちょうどいい**
- **疑わしい情報は全て警告**
- **個別要素を個別形態のまま実装に組み込まない**
- **Specは構造だけ、実値は外部に逃がす**

このルールにより、AI側でも機密情報漏洩を防ぎます。