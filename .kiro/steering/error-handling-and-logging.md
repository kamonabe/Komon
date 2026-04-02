---
inclusion: fileMatch
fileMatchPattern: "src/**/*.py"
---

# エラーハンドリングとログ出力の標準

## 基本方針

エラーが発生しても可能な限り処理を継続する。ユーザー向けには日本語、開発者向けには英語。

## print() と logging の使い分け

| 場面 | 手段 | 言語 | 例 |
|------|------|------|-----|
| CLI実行結果・即時フィードバック | `print()` | 日本語+絵文字 | `print("✅ 通知を送信しました")` |
| バックグラウンドログ・デバッグ | `logging` | 英語 | `logger.info("Notification sent")` |
| 重要なエラー | 両方 | 両方 | print + logger.error |

## ログレベル

| レベル | 用途 | 例 |
|--------|------|-----|
| DEBUG | 変数値、処理の詳細な流れ | `logger.debug("Loading: %s", path)` |
| INFO | 処理の開始/完了、成功記録 | `logger.info("Notification sent")` |
| WARNING | 問題ではないが注意すべき状況 | `logger.warning("File not found, using default")` |
| ERROR | エラー発生、処理は継続 | `logger.error("Failed: %s", e, exc_info=True)` |
| CRITICAL | 使わない（軽量ツールのため） | — |

## エラーの致命度判断

致命的（`sys.exit(1)`で停止）:
- 設定ファイルが存在しない
- 設定ファイルの形式が完全に不正
- 必須の環境変数が未設定で実行不可能

非致命的（処理を継続）:
- 履歴ファイルの読み込み失敗 → 空データで継続
- 通知の送信失敗 → ログに記録して継続
- 一部のログファイルが読めない → 他のファイルを処理

## 標準パターン

```python
# 非致命的エラー
try:
    save_history(data)
except Exception as e:
    print(f"⚠️ 履歴の保存に失敗: {e}")
    logger.error("Failed to save history: %s", e, exc_info=True)

# 致命的エラー
try:
    config = load_config("settings.yml")
except FileNotFoundError:
    print("❌ 設定ファイルが見つかりません: settings.yml")
    print("   config/settings.yml.sample をコピーして作成してください。")
    sys.exit(1)

# リトライ
for attempt in range(max_retries):
    try:
        send_notification(message)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            logger.warning("Failed (attempt %d/%d): %s", attempt + 1, max_retries, e)
            time.sleep(2 ** attempt)
        else:
            print(f"❌ 送信に失敗しました（{max_retries}回試行）")
            logger.error("Failed after %d attempts: %s", max_retries, e, exc_info=True)
```

## カスタム例外

ドメイン固有のエラーにはカスタム例外を使用:
- `ValidationError`: 設定検証エラー
- `ThresholdError`: 閾値設定エラー
- `NotificationError`: 通知送信エラー

例外メッセージは英語で記述する。

## ロギング設定

```python
import logging
logger = logging.getLogger(__name__)

# 環境変数でログレベルを制御
# KOMON_LOG_LEVEL=DEBUG python scripts/advise.py
```
