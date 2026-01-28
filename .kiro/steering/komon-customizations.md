---
rule-id: komon-customizations
priority: normal
applies-to: [komon]
triggers: [always]
description: Komon固有のカスタマイズルール
---

# Komon固有のカスタマイズ

このファイルにはKomon固有のルールのみを記載します。
共通ルールは `../../../.kiro/steering/` を参照してください。

---

## 🎯 Komonプロジェクト固有の設定

### テストカバレッジ目標
- **Komon目標**: 95%以上（共通目標より高い）
- **現在の達成率**: 92%
- **次の目標**: 95%到達

### プロジェクト固有のコマンド
```bash
# Komon専用コマンド
komon advise          # 対話型アドバイザー
komon status          # ステータス表示
komon guide           # ガイドメニュー
komon initial         # 初期設定ウィザード
```

### 特殊な開発ルール

#### 1. ログ監視機能
- システムログへのアクセスが必要
- テスト時はモックログファイルを使用
- 実際のシステムログは触らない

#### 2. OS検知機能
- 複数ディストリビューションでテスト必須
- AlmaLinux 9（メイン）
- Ubuntu 22.04（サブ）
- テスト環境: Docker推奨

#### 3. 通知機能
- 実際の通知を送らないこと（モック必須）
- Webhook URLは環境変数で管理
- テスト時は `KOMON_TEST_MODE=1` を設定

#### 4. ネットワークチェック機能
- 外部への実際の接続は避ける
- モックレスポンスを使用
- タイムアウト設定を短めに（テスト高速化）

---

## 📚 共通ルール参照

以下のルールはワークスペース共通です：
- **必須ルール**: `../../../.kiro/steering/essential-rules.md`
- **開発標準**: `../../../.kiro/steering/development-standards.md`
- **Git/SSH設定**: `../../../.kiro/steering/git-ssh-setup.md`

---

## 🔧 Komon固有の自動化システム

### Context効率化システム（実験的機能）
Komonでは以下の自動化システムを実装済み：

#### 1. auto-loader.md
ステアリングルールの自動読み込みシステム

#### 2. keyword-detector.py
キーワード検知による動的ルール読み込み

#### 3. session-cache.py
セッションキャッシュによる高速化

#### 4. cache-usage-guide.md
キャッシュ使用ガイド

これらはKomon固有の実験的機能です。
他のプロジェクトへの展開は慎重に検討してください。

---

## 🧪 Komon固有のテスト戦略

### プロパティベーステスト
- hypothesis を積極的に使用
- 特にディスク予測、重複検知、長時間実行検知で有効

### 統合テスト
- 実際のシステムリソースを使用するテストは慎重に
- CI/CD環境での実行を考慮

### カバレッジ目標
- 全体: 95%以上
- コアモジュール（monitor, analyzer, notification）: 98%以上
- CLIコマンド: 90%以上

---

## 📦 Komon固有の依存関係

### 必須依存
- psutil: システムリソース監視
- PyYAML: 設定ファイル管理
- requests: HTTP通知

### 開発依存
- pytest: テストフレームワーク
- hypothesis: プロパティベーステスト
- pytest-cov: カバレッジ測定

---

## 🚀 Komon固有のリリースプロセス

### PyPI公開
Komonは PyPI に公開されています：
```bash
# ビルド
python -m build

# アップロード
twine upload dist/*
```

### バージョニング
- メジャー: 破壊的変更
- マイナー: 新機能追加
- パッチ: バグ修正

### リリースチェックリスト
- [ ] CHANGELOG.md更新
- [ ] version.txt更新
- [ ] テスト実行（カバレッジ92%以上）
- [ ] README.mdのバージョン番号更新
- [ ] タグ作成
- [ ] PyPI公開
- [ ] GitHub Releaseノート作成

---

## 🎯 Komon開発の哲学

### 「やさしい監視」
- 過剰な通知をしない
- 段階的な警告（警告→警戒→緊急）
- 通知疲れを防ぐ

### 「翁のような存在」ではない
- Komonは「顧問」として積極的にアドバイス
- Okina（翁）とは対照的なアプローチ
- ユーザーの行動を促す

---

**最終更新**: 2025-01-28
**管理者**: kamonabe
