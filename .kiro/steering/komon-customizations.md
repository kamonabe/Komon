---
inclusion: auto
name: komon-customizations
description: Komon固有のカスタマイズ、CLIコマンド、テスト戦略、開発哲学
---

# Komon固有のカスタマイズ

## プロジェクト固有のコマンド

```bash
komon advise          # 対話型アドバイザー
komon status          # ステータス表示
komon guide           # ガイドメニュー
komon initial         # 初期設定ウィザード
```

## 特殊な開発ルール

- ログ監視機能: テスト時はモックログファイルを使用、実際のシステムログは触らない
- OS検知機能: AlmaLinux 9（メイン）+ Ubuntu 22.04（サブ）でテスト、Docker推奨
- 通知機能: 実際の通知を送らない（モック必須）、Webhook URLは環境変数管理、テスト時は `KOMON_TEST_MODE=1`
- ネットワークチェック: 外部への実際の接続は避ける、モックレスポンス使用、タイムアウト短め

## Komon固有のテスト戦略

- プロパティベーステスト: hypothesis を積極使用（ディスク予測、重複検知、長時間実行検知）
- 統合テスト: 実際のシステムリソース使用テストは慎重に、CI/CD環境を考慮
- カバレッジ: コアモジュール（monitor, analyzer, notification）は `project-config.yml` の `testing.coverage_core_modules` を参照

## 依存関係

必須: psutil, PyYAML, requests
開発: pytest, hypothesis, pytest-cov

## 開発の哲学

「やさしい監視」: 過剰な通知をしない、段階的な警告（警告→警戒→緊急）、通知疲れを防ぐ。
Komonは「顧問」として積極的にアドバイスする。ユーザーの行動を促す。
