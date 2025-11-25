# エラーハンドリングとログ出力の標準

## 基本方針

{{project.name}}は**軽量{% if project.type == "cli-tool" %}アドバイザー型ツール{% endif %}{% if project.type == "library" %}ライブラリ{% endif %}{% if project.type == "web-app" %}Webアプリケーション{% endif %}**であり、エラーが発生しても可能な限り処理を継続します。

ユーザー向けには分かりやすい{{communication.language_name}}メッセージを表示し、開発者向けには詳細なログを記録します。

## `print()`と`logging`の使い分け

### `print()`を使う場面（ユーザー向け即時フィードバック）

**用途**:
{% if project.type == "cli-tool" %}
- CLIコマンドの実行結果（`{{project.name|lower}} advise`, `{{project.name|lower}} monitor`）
{% endif %}
- 成功/警告/エラーの即時表示
- 進捗状況の表示
- 対話的な確認メッセージ

**特徴**:
- {{communication.language_name}}メッセージ
{% if communication.use_emoji %}
- 絵文字付き（✅ ⚠️ ❌）
{% endif %}
- 原因と対処法を記載

**例**:
{% if communication.language == "ja" %}
```python
print("✅ Slack通知を送信しました")
print("⚠️ 環境変数 KOMON_SLACK_WEBHOOK が設定されていません")
print("❌ メール通知エラー: SMTP接続に失敗しました")
```
{% endif %}

{% if communication.language == "en" %}
```python
print("✅ Slack notification sent successfully")
print("⚠️ Environment variable KOMON_SLACK_WEBHOOK is not set")
print("❌ Email notification error: SMTP connection failed")
```
{% endif %}

### `logging`を使う場面（開発者向け記録）

**用途**:
- cron実行時のバックグラウンドログ
- デバッグ情報
- 詳細なエラートレース
- パフォーマンス計測

**特徴**:
- 英語メッセージ
- 詳細な技術情報
- スタックトレース付き

**例**:
```python
logger.info("Notification sent successfully")
logger.warning("History file not found, using empty data")
logger.error("Failed to save notification history: %s", e, exc_info=True)
```

### 両方使う場面

**重要なエラー**:
- `print()`でユーザーに即座に通知
- `logging.error()`で詳細を記録

**例**:
{% if communication.language == "ja" %}
```python
try:
    send_notification(message)
except Exception as e:
    print(f"❌ 通知の送信に失敗しました: {e}")
    logger.error("Notification failed: %s", e, exc_info=True)
```
{% endif %}

{% if communication.language == "en" %}
```python
try:
    send_notification(message)
except Exception as e:
    print(f"❌ Failed to send notification: {e}")
    logger.error("Notification failed: %s", e, exc_info=True)
```
{% endif %}

## ログレベルの使い分け

### DEBUG（開発時のデバッグ情報）

**用途**:
- 変数の値
- 処理の詳細な流れ
- ファイルパスやデータ構造

**例**:
```python
logger.debug("Loading history file: %s", file_path)
logger.debug("Parsed %d records from CSV", len(records))
logger.debug("Threshold values: warning=%d, alert=%d, critical=%d", w, a, c)
```

### INFO（正常な処理の記録）

**用途**:
- 処理の開始/完了
- 重要な処理の成功
- 定期実行の記録

**例**:
```python
logger.info("Notification sent successfully")
logger.info("Weekly report generated: %s", report_path)
logger.info("Monitoring started with interval: %d seconds", interval)
```

### WARNING（問題ではないが注意すべき状況）

**用途**:
- ファイルが見つからない（デフォルト値を使用）
- データが不完全（一部をスキップ）
- 非推奨の設定を使用

**例**:
```python
logger.warning("History file not found, using empty data")
logger.warning("Throttle history file corrupted, recreating")
logger.warning("Using deprecated single threshold format")
```

### ERROR（エラーが発生したが処理は継続）

**用途**:
- 通知の送信失敗
- 履歴ファイルの保存失敗
- 一部のログファイルが読めない

**例**:
```python
logger.error("Failed to save notification history: %s", e)
logger.error("SMTP connection failed: %s", e)
logger.error("Log file not readable: %s", log_path)
```

### CRITICAL（使わない）

**理由**: {{project.name}}は軽量ツールなので、致命的エラーは想定しない。

致命的なエラー（設定ファイルが存在しない等）は`sys.exit(1)`で終了する。

## エラーハンドリングの方針

### 処理を停止するエラー（致命的）

以下のエラーは処理を停止し、`sys.exit(1)`で終了します：

- **設定ファイルが存在しない**
{% if communication.language == "ja" %}
  ```python
  try:
      config = load_config("settings.yml")
  except FileNotFoundError:
      print("❌ 設定ファイルが見つかりません: settings.yml")
      print("   config/settings.yml.sample をコピーして作成してください。")
      logger.critical("Configuration file not found")
      sys.exit(1)
  ```
{% endif %}

{% if communication.language == "en" %}
  ```python
  try:
      config = load_config("settings.yml")
  except FileNotFoundError:
      print("❌ Configuration file not found: settings.yml")
      print("   Please copy config/settings.yml.sample and create it.")
      logger.critical("Configuration file not found")
      sys.exit(1)
  ```
{% endif %}

- **設定ファイルの形式が完全に不正**
{% if communication.language == "ja" %}
  ```python
  try:
      thresholds = validate_threshold_config(config)
  except ValidationError as e:
      print(f"❌ 設定エラー: {e}")
      logger.error("Configuration validation failed: %s", e)
      sys.exit(1)
  ```
{% endif %}

{% if communication.language == "en" %}
  ```python
  try:
      thresholds = validate_threshold_config(config)
  except ValidationError as e:
      print(f"❌ Configuration error: {e}")
      logger.error("Configuration validation failed: %s", e)
      sys.exit(1)
  ```
{% endif %}

- **必須の環境変数が未設定（実行不可能）**
{% if communication.language == "ja" %}
  ```python
  webhook_url = os.getenv("KOMON_SLACK_WEBHOOK")
  if not webhook_url:
      print("❌ 環境変数 KOMON_SLACK_WEBHOOK が設定されていません")
      print("   通知機能を使用するには環境変数を設定してください。")
      sys.exit(1)
  ```
{% endif %}

{% if communication.language == "en" %}
  ```python
  webhook_url = os.getenv("APP_SLACK_WEBHOOK")
  if not webhook_url:
      print("❌ Environment variable APP_SLACK_WEBHOOK is not set")
      print("   Please set the environment variable to use notification feature.")
      sys.exit(1)
  ```
{% endif %}

### 処理を継続するエラー（非致命的）

以下のエラーは処理を継続します：

- **履歴ファイルの読み込み失敗** → 空データで継続
{% if communication.language == "ja" %}
  ```python
  try:
      history = load_history(file_path)
  except Exception as e:
      print(f"⚠️ 履歴ファイルの読み込みに失敗: {e}")
      logger.warning("Failed to load history, using empty data: %s", e)
      history = []
  ```
{% endif %}

{% if communication.language == "en" %}
  ```python
  try:
      history = load_history(file_path)
  except Exception as e:
      print(f"⚠️ Failed to load history file: {e}")
      logger.warning("Failed to load history, using empty data: %s", e)
      history = []
  ```
{% endif %}

- **通知の送信失敗** → ログに記録して継続
{% if communication.language == "ja" %}
  ```python
  try:
      send_slack_alert(message, webhook_url)
  except Exception as e:
      print(f"❌ Slack通知エラー: {e}")
      logger.error("Slack notification failed: %s", e, exc_info=True)
      # 処理は継続
  ```
{% endif %}

{% if communication.language == "en" %}
  ```python
  try:
      send_slack_alert(message, webhook_url)
  except Exception as e:
      print(f"❌ Slack notification error: {e}")
      logger.error("Slack notification failed: %s", e, exc_info=True)
      # Continue processing
  ```
{% endif %}

- **一部のログファイルが読めない** → 他のファイルを処理
{% if communication.language == "ja" %}
  ```python
  for log_path in log_paths:
      try:
          analyze_log(log_path)
      except Exception as e:
          print(f"⚠️ ログファイルの解析に失敗: {log_path}")
          logger.error("Failed to analyze log: %s", log_path, exc_info=True)
          continue  # 次のファイルへ
  ```
{% endif %}

{% if communication.language == "en" %}
  ```python
  for log_path in log_paths:
      try:
          analyze_log(log_path)
      except Exception as e:
          print(f"⚠️ Failed to analyze log file: {log_path}")
          logger.error("Failed to analyze log: %s", log_path, exc_info=True)
          continue  # Next file
  ```
{% endif %}

### カスタム例外を作る場合

**ドメイン固有のエラー**:
- `ValidationError`: 設定検証エラー
- `ThresholdError`: 閾値設定エラー
- `NotificationError`: 通知送信エラー

**例**:
```python
class ValidationError(Exception):
    """設定検証エラー"""
    pass

class ThresholdError(Exception):
    """閾値設定エラー"""
    pass
```

**使い方**:
{% if communication.language == "ja" %}
```python
def validate_threshold_config(config: dict) -> dict:
    if "thresholds" not in config:
        raise ValidationError("閾値設定が見つかりません")
    
    # 検証処理...
```
{% endif %}

{% if communication.language == "en" %}
```python
def validate_threshold_config(config: dict) -> dict:
    if "thresholds" not in config:
        raise ValidationError("Threshold configuration not found")
    
    # Validation logic...
```
{% endif %}

### 例外メッセージの言語

- **ユーザー向け（`print()`）**: {{communication.language_name}}、原因と対処法
{% if communication.language == "ja" %}
  ```python
  print("❌ 設定ファイルが見つかりません: settings.yml")
  print("   config/settings.yml.sample をコピーして作成してください。")
  ```
{% endif %}

{% if communication.language == "en" %}
  ```python
  print("❌ Configuration file not found: settings.yml")
  print("   Please copy config/settings.yml.sample and create it.")
  ```
{% endif %}

- **開発者向け（`logging`、例外メッセージ）**: 英語、詳細情報
  ```python
  raise ValidationError("Threshold configuration is invalid: warning >= alert")
  logger.error("Failed to parse configuration file: %s", e)
  ```

## 標準的なエラーハンドリングパターン

### パターン1: 非致命的エラー（処理継続）

{% if communication.language == "ja" %}
```python
try:
    save_notification_history(data)
except Exception as e:
    print(f"⚠️ 通知履歴の保存に失敗: {e}")
    logger.error("Failed to save notification history: %s", e, exc_info=True)
    # 処理は継続
```
{% endif %}

{% if communication.language == "en" %}
```python
try:
    save_notification_history(data)
except Exception as e:
    print(f"⚠️ Failed to save notification history: {e}")
    logger.error("Failed to save notification history: %s", e, exc_info=True)
    # Continue processing
```
{% endif %}

### パターン2: 致命的エラー（処理停止）

{% if communication.language == "ja" %}
```python
try:
    config = load_config("settings.yml")
except FileNotFoundError:
    print("❌ 設定ファイルが見つかりません: settings.yml")
    print("   config/settings.yml.sample をコピーして作成してください。")
    logger.critical("Configuration file not found")
    sys.exit(1)
```
{% endif %}

{% if communication.language == "en" %}
```python
try:
    config = load_config("settings.yml")
except FileNotFoundError:
    print("❌ Configuration file not found: settings.yml")
    print("   Please copy config/settings.yml.sample and create it.")
    logger.critical("Configuration file not found")
    sys.exit(1)
```
{% endif %}

### パターン3: カスタム例外

{% if communication.language == "ja" %}
```python
try:
    thresholds = validate_threshold_config(config)
except ValidationError as e:
    print(f"❌ 設定エラー: {e}")
    logger.error("Configuration validation failed: %s", e)
    sys.exit(1)
```
{% endif %}

{% if communication.language == "en" %}
```python
try:
    thresholds = validate_threshold_config(config)
except ValidationError as e:
    print(f"❌ Configuration error: {e}")
    logger.error("Configuration validation failed: %s", e)
    sys.exit(1)
```
{% endif %}

### パターン4: リトライ処理

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        send_notification(message)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            logger.warning("Notification failed (attempt %d/%d): %s", 
                          attempt + 1, max_retries, e)
            time.sleep(2 ** attempt)  # 指数バックオフ
        else:
{% if communication.language == "ja" %}
            print(f"❌ 通知の送信に失敗しました（{max_retries}回試行）")
{% endif %}
{% if communication.language == "en" %}
            print(f"❌ Failed to send notification ({max_retries} attempts)")
{% endif %}
            logger.error("Notification failed after %d attempts: %s", 
                        max_retries, e, exc_info=True)
```

### パターン5: ファイル操作のエラーハンドリング

{% if communication.language == "ja" %}
```python
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    logger.warning("File not found, using default: %s", file_path)
    data = {}
except json.JSONDecodeError as e:
    print(f"⚠️ ファイルの形式が不正です: {file_path}")
    logger.error("JSON decode error: %s", e)
    data = {}
except Exception as e:
    print(f"⚠️ ファイルの読み込みに失敗: {file_path}")
    logger.error("Failed to read file: %s", e, exc_info=True)
    data = {}
```
{% endif %}

{% if communication.language == "en" %}
```python
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    logger.warning("File not found, using default: %s", file_path)
    data = {}
except json.JSONDecodeError as e:
    print(f"⚠️ Invalid file format: {file_path}")
    logger.error("JSON decode error: %s", e)
    data = {}
except Exception as e:
    print(f"⚠️ Failed to read file: {file_path}")
    logger.error("Failed to read file: %s", e, exc_info=True)
    data = {}
```
{% endif %}

## ロギング設定

### 基本設定

```python
import logging

# ロガーの取得
logger = logging.getLogger(__name__)

# 設定（モジュールの初期化時に1回だけ）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/{{project.name|lower}}.log'),
        logging.StreamHandler()  # コンソールにも出力
    ]
)
```

### 環境変数でログレベルを制御

```python
import os

log_level = os.getenv('{{project.name|upper}}_LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
```

**使い方**:
```bash
# デバッグモードで実行
{{project.name|upper}}_LOG_LEVEL=DEBUG python scripts/advise.py

# 本番環境（エラーのみ）
{{project.name|upper}}_LOG_LEVEL=ERROR python scripts/main.py
```

## Kiroへの指示

### コード実装時のチェックリスト

- [ ] ユーザー向けメッセージは`print()`で{{communication.language_name}}{% if communication.use_emoji %}、絵文字付き{% endif %}
- [ ] 開発者向けログは`logging`で英語、詳細情報
- [ ] 致命的エラーは`sys.exit(1)`で終了
- [ ] 非致命的エラーは処理を継続
- [ ] 例外メッセージは英語で記述
- [ ] `exc_info=True`でスタックトレースを記録
- [ ] ログレベルを適切に使い分け

## トラブルシューティング

### Q: `print()`と`logging`のどちらを使うか迷う

**A**: 以下の基準で判断してください：
- ユーザーが即座に見る必要がある → `print()`
- 後で確認するログ → `logging`
- 重要なエラー → 両方

### Q: エラーメッセージは{{communication.language_name}}？英語？

**A**:
- `print()`のメッセージ: {{communication.language_name}}（ユーザー向け）
- `logging`のメッセージ: 英語（開発者向け）
- 例外メッセージ: 英語（コード内で使用）

### Q: 処理を継続すべきか停止すべきか迷う

**A**: 以下の基準で判断してください：
- ユーザーが手動で修正する必要がある → 停止（`sys.exit(1)`）
- 自動的にリカバリー可能 → 継続（警告を表示）

## まとめ

- **`print()`**: ユーザー向け、{{communication.language_name}}{% if communication.use_emoji %}、絵文字付き{% endif %}
- **`logging`**: 開発者向け、英語、詳細情報
- **致命的エラー**: `sys.exit(1)`で停止
- **非致命的エラー**: 処理を継続、警告を表示
- **例外メッセージ**: 英語で記述
- **ログレベル**: DEBUG < INFO < WARNING < ERROR

このルールにより、ユーザーにも開発者にも分かりやすいエラーハンドリングが実現されます。
