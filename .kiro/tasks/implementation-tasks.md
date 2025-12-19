---
title: Komon - Implementation Task List
status: active
created: 2025-11-22
updated: 2025-11-26
---

# Komon 実装タスクリスト

このドキュメントは、`specs/future-ideas.md` のアイデアを実装可能なタスクに分解し、進捗を管理します。

**注意**: 完了したタスク（v1.17.0以前）は `completed-tasks.md` に移動されています。

---

## タスクステータス

- 🔴 **TODO**: 未着手
- 🟡 **In Progress**: 実装中
- 🟢 **Done**: 完了
- ⏸️ **On Hold**: 保留中
- ❌ **Cancelled**: キャンセル

---

## 💡 Medium Priority Tasks

### [TASK-006] 多重実行プロセスの検出
**元アイデア**: [IDEA-011] 多重実行プロセスの検出 (実装済み)  
**ステータス**: 🟢 Done  
**優先度**: Medium  
**見積もり**: 中（3-4時間）  
**完了日**: 2025-11-29 (v1.20.0)

#### 背景
cronなどによる同一スクリプトの多重起動を検出し、リソース圧迫の原因として助言。

#### タスク分解
- [x] `src/komon/duplicate_detector.py` モジュールの作成
  - `detect_duplicate_processes()` 関数の実装
  - `_extract_script_name()` 関数の実装
  - エラーハンドリングとログ出力
- [x] `scripts/advise.py` の拡張
  - `advise_duplicate_processes()` 関数の追加
  - メイン処理への統合
- [x] 設定ファイルの拡張
  - `duplicate_process_detection` セクションの追加
  - 閾値と有効/無効の設定
- [x] テストケースの追加
  - ユニットテスト: 15件
  - 統合テスト: 7件
  - プロパティテスト: 5件
- [x] ドキュメント更新
  - README.md の機能一覧に追加
  - CHANGELOG.md の更新

#### 完了条件
- ✅ 同一スクリプトの多重実行が検出される
- ✅ 設定で閾値を変更できる
- ✅ テストが追加され、全379テストがパス
- ✅ カバレッジ93%を維持
- ✅ `komon advise` で警告が表示される

#### 実装詳細
- `duplicate_detector.py`: 多重実行検出ロジック
- `advise.py`: 警告表示機能
- `settings.yml.sample`: 設定項目の追加
- 対象拡張子: .py, .sh, .rb, .pl
- デフォルト閾値: 3個以上

#### 依存関係
- TASK-005と並行実装可能（同じプロセス走査ロジックを共有）

---

## 🔮 Low Priority / Future Tasks

### [TASK-008] 学習機能（パターン認識）
**元アイデア**: [IDEA-002] 学習機能（パターン認識）  
**ステータス**: ⏸️ On Hold  
**優先度**: Low  
**見積もり**: 大（20時間以上）

#### 背景
ユーザーの行動パターンを学習して、不要な通知を減らす。

#### 検討事項
- 実装難易度が高い
- Komonの「シンプル」思想と相反する可能性
- まずは他の高優先度タスクを完了させてから検討

---

### [TASK-009] 週次レポート機能
**元アイデア**: [IDEA-004] 週次レポート機能  
**ステータス**: 🔴 TODO  
**優先度**: Low  
**見積もり**: 中（6-8時間）

#### 背景
週に1回、振り返りレポートを送信。

#### タスク分解（概要のみ）
- [ ] 週次データの集計ロジック
- [ ] レポートメッセージの作成
- [ ] cron設定の追加
- [ ] 設定で有効/無効を切り替え可能に

---

### [TASK-010] トレンド予測機能
**元アイデア**: [IDEA-007] トレンド予測機能  
**ステータス**: 🔴 TODO  
**優先度**: Low  
**見積もり**: 大（10-15時間）

#### 背景
過去のトレンドから将来を予測。

#### 検討事項
- 予測アルゴリズムの精度が課題
- まずは基本機能を充実させてから検討

---

### [TASK-011] トップ3増加ログの可視化
**元アイデア**: [IDEA-013] トップ3増加ログの可視化  
**ステータス**: 🔴 TODO  
**優先度**: Low  
**見積もり**: 中（5-7時間）

#### 背景
ログ傾向分析の結果を「通知」だけでなく「魅せる」方向へ進化。

#### 検討事項
- matplotlib依存の追加が必要
- Komonの「軽量」思想とのバランスを考慮

---

## 実装ワークフロー

```
1. future-ideas.md でアイデアを検討
   ↓
2. 実装を決定したら、このファイルにタスク化
   ↓
3. タスクステータスを更新しながら実装
   ↓
4. テスト・レビュー
   ↓
5. ステータスを 🟢 Done に更新
   ↓
6. CHANGELOG.md に記録
   ↓
7. future-ideas.md のステータスを「実装済み」に更新
```

---

### [TASK-018] OS判定・汎用Linux対応（マルチディストリビューション対応）
**元アイデア**: [IDEA-022] OS判定・汎用Linux対応 (実装済み)  
**feature-name**: os-detection-multi-distro  
**ステータス**: 🟢 Done  
**完了日**: 2025-12-03 (v1.24.0)  
**優先度**: High  
**見積もり**: 中（4-6時間）  
**担当**: 未定

#### 背景
現在のKomonはRHEL系（AlmaLinux, Rocky Linux, Amazon Linux 2023）を想定して設計されているが、
Debian系（Raspberry Pi OS, Ubuntu, Debian）でも動作する可能性がある。

**現状の問題点**:
- ❌ パッケージ管理コマンドが異なる（dnf vs apt）
- ❌ ログファイルのパスが異なる（/var/log/messages vs /var/log/syslog）
- ❌ 誤ったアドバイスを出してしまう危険性（Raspberry Piでdnfコマンドを提案等）

**Komonの哲学**:
> 「誤ったアドバイスをしない」

この哲学を守るため、OS判定機能が必要。

#### タスク分解

**Phase 1: 基本機能（v1.24.0）**
- [x] OS判定ロジックの実装
  - `/etc/os-release` を読み取り
  - OS ファミリを判定（rhel / debian / suse / arch / unknown）
  - Amazon Linux 2023 は rhel ファミリとして扱う
- [x] 新規モジュール `src/komon/os_detection.py` の作成
  - `OSDetector` クラスの実装
  - `detect_os_family()` 関数
  - `get_package_manager_command()` 関数
  - `get_log_path()` 関数
  - `should_show_package_advice()` 関数
- [x] 設定ファイルの拡張
  - `system.os_family` 設定の追加（auto / rhel / debian / suse / arch / unknown）
  - デフォルトは `auto`（自動判定）
- [x] Windows非対応の明示
  - `sys.platform == 'win32'` でチェック
  - WSL判定機能の実装（`is_wsl()` 関数）
  - Windows ネイティブでは即エラー終了
  - WSL なら Linux 扱いで続行
- [x] テストケースの追加
  - プロパティベーステスト: 7件（OS判定ロジック）
  - ユニットテスト: 29件（OSDetectorクラス）
  - 全36テストがパス
- [x] ドキュメント更新（Phase 1）
  - README.md に「RHEL推奨」を明記
  - 対応プラットフォームセクションの更新
  - docs/RECOMMENDED_RUNTIME.md の更新

**Phase 2: 機能制限（v1.24.0 or v1.25.0）**
- [x] アドバイス出し分けの実装
  - RHEL系: `sudo dnf update --security`
  - Debian系: `sudo apt update && sudo apt upgrade`
  - unknown: 具体的なコマンドを出さない
- [x] Debian系でのパッケージ系アドバイス抑制
  - `should_show_package_advice()` の活用
  - パッケージ名の違いによる誤アドバイスを防止
- [x] テストケースの追加（Phase 2）
  - 統合テスト: OS別のアドバイス出し分け（3件）
  - 統合テスト: Debian系でのパッケージ系抑制

**Phase 3: 細かい対応（v1.24.0）**
- [x] ログパス切替の実装
  - RHEL系: `/var/log/messages`
  - Debian系: `/var/log/syslog`
  - unknown: ログアドバイスは抑制
- [x] ログ解析モジュールの拡張
  - `get_recommended_log_path()` 関数の追加
  - `should_show_log_advice()` 関数の追加
- [x] 統合テストの追加
  - ログパス切替のテスト（6件）
- [x] ドキュメント更新（Phase 3）
  - docs/RECOMMENDED_RUNTIME.md の更新
  - ベストエフォート対応の詳細を追加
  - 制限事項の明記
  - docs/CHANGELOG.md の更新

#### 完了条件
- ✅ OS自動判定が動作する（rhel / debian / suse / arch / unknown）
- ✅ Amazon Linux 2023 が rhel ファミリとして判定される
- ✅ 設定で OS ファミリを上書きできる（system.os_family）
- ✅ Windows ネイティブでは即エラー終了する
- ✅ WSL では Linux 扱いで動作する
- ✅ OS別にアドバイスが出し分けられる
- ✅ Debian系ではパッケージ系アドバイスがスキップされる
- ✅ ログパスが OS 別に切り替わる
- ✅ unknown OSではログアドバイスが抑制される
- ✅ README.md に「RHEL推奨」が明記される
- ✅ docs/RECOMMENDED_RUNTIME.md が更新される
- ✅ 全504テストがパス
- ✅ カバレッジを維持

#### 実装イメージ

**OS判定ロジック**:
```python
# src/komon/os_detection.py
def detect_os_family():
    """OSファミリを自動判定"""
    try:
        with open('/etc/os-release', 'r') as f:
            content = f.read()
            
        if 'rhel' in content or 'fedora' in content or 'centos' in content:
            return 'rhel'
        elif 'debian' in content or 'ubuntu' in content:
            return 'debian'
        elif 'suse' in content:
            return 'suse'
        elif 'arch' in content:
            return 'arch'
        else:
            return 'unknown'
    except FileNotFoundError:
        return 'unknown'
```

**設定例**:
```yaml
system:
  os_family: auto  # auto / rhel / debian / suse / arch / unknown
```

**アドバイス出し分け**:
```python
# RHEL系
"sudo dnf update --security"

# Debian系
"sudo apt update && sudo apt upgrade"

# unknown
"ご利用OSに応じたパッケージ管理コマンドで更新を確認してください"
```

#### 期待効果
- Raspberry Pi等での誤動作防止
- 「誤ったアドバイスをしない」という一貫性の維持
- 将来的な他ディストリビューション対応の基盤
- サポート範囲の明確化

---

### [TASK-019] Webhook通知統一化 Phase 1: Discord/Teams対応
**元アイデア**: [IDEA-023] Webhook通知の統一化（Phase 1）  
**ステータス**: 🟢 Done  
**優先度**: Medium  
**見積もり**: 小（2-3時間）  
**対象バージョン**: v1.26.0  
**完了日**: 2025-12-12 (v1.26.0)

#### 背景
既存のSlack通知と同じ形式で、Discord/Teams通知を追加する。既存のSlack通知には一切触らず、新規機能として追加することでリスクを最小化。

#### タスク分解
- [x] `src/komon/notification.py` の拡張
  - `send_discord_alert()` 関数の追加（Slack形式を踏襲）
  - `send_teams_alert()` 関数の追加（Slack形式を踏襲）
  - エラーハンドリングとログ出力
  - `send_teams_alert()` 関数の追加（Slack形式を踏襲）
  - エラーハンドリングとログ出力
- [x] 設定ファイルの拡張
  - `discord` セクションの追加
  - `teams` セクションの追加
  - 環境変数対応（`KOMON_DISCORD_WEBHOOK`, `KOMON_TEAMS_WEBHOOK`）
- [x] 通知送信ロジックの統合
  - `scripts/main.py` の拡張
  - `scripts/main_log_monitor.py` の拡張
  - `scripts/weekly_report.py` の拡張
  - `scripts/main_log_trend.py` の拡張
  - `discord` セクションの追加
  - `teams` セクションの追加
  - 環境変数対応（`KOMON_DISCORD_WEBHOOK`, `KOMON_TEAMS_WEBHOOK`）
- [x] テストケースの追加
  - ユニットテスト: Discord通知のテスト（モック使用）
  - ユニットテスト: Teams通知のテスト（モック使用）
  - 統合テスト: 既存のSlack通知に影響がないことを確認
- [x] ドキュメント更新
  - README.md: Discord/Teams通知の設定方法を追加
  - docs/EXAMPLES.md: 設定例を追加
  - README.md: Discord/Teams通知の設定方法を追加
  - docs/EXAMPLES.md: 設定例を追加

#### 完了条件
- ✅ Discord通知が動作する
- ✅ Teams通知が動作する
- ✅ 既存のSlack通知に影響がない
- ✅ 全テストがパス（21件のユニットテスト + 9件の統合テスト）
- ✅ カバレッジを維持

#### 実装詳細
- `send_discord_alert()` 関数: Discord Webhook API対応（204ステータスコード）
- `send_teams_alert()` 関数: Teams Webhook API対応（200ステータスコード）
- 環境変数対応: `KOMON_DISCORD_WEBHOOK`, `KOMON_TEAMS_WEBHOOK`
- 全通知スクリプトに統合: main.py, main_log_monitor.py, weekly_report.py, main_log_trend.py
- 設定例追加: README.md, docs/EXAMPLES.md

#### 期待効果
- Discord/Teamsユーザーも同じ通知を受信可能
- 既存のSlack通知との完全な互換性
- 環境変数による安全な認証情報管理
- 統一されたエラーハンドリングと履歴保存

---

## 🎉 TASK-019 実装完了

**実装内容**:
1. ✅ Discord/Teams通知関数の追加
2. ✅ 設定ファイルの拡張
3. ✅ 全通知スクリプトへの統合
4. ✅ 30件のテストケース追加
5. ✅ ドキュメント更新

**テスト結果**: 全30テスト（21ユニット + 9統合）がパス
**実装時間**: 約2時間（見積もり通り）
**対象バージョン**: v1.26.0

次のフェーズ（TASK-020: 統一Webhook実装）の準備が整いました。

#### 完了条件（元の記載）
- ✅ Discord通知が動作する
- ✅ Teams通知が動作する
- ✅ 既存のSlack通知に影響がない
- ✅ 全テストがパス
- ✅ カバレッジを維持

#### 実装イメージ

**Discord通知**:
```python
def send_discord_alert(message, webhook_url):
    """Discord通知（Slack形式を踏襲）"""
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload, timeout=10)
    response.raise_for_status()
```

**Teams通知**:
```python
def send_teams_alert(message, webhook_url):
    """Teams通知（Slack形式を踏襲）"""
    payload = {"text": message}
    response = requests.post(webhook_url, json=payload, timeout=10)
    response.raise_for_status()
```

**設定例**:
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "env:KOMON_SLACK_WEBHOOK"
  
  discord:
    enabled: false
    webhook_url: "env:KOMON_DISCORD_WEBHOOK"
  
  teams:
    enabled: false
    webhook_url: "env:KOMON_TEAMS_WEBHOOK"
```

---

### [TASK-020] Webhook通知統一化 Phase 2: 統一Webhook実装
**元アイデア**: [IDEA-023] Webhook通知の統一化（Phase 2）  
**ステータス**: � InD Progress 
**優先度**: Medium  
**見積もり**: 中（4-5時間）  
**対象バージョン**: v1.26.0  
**依存**: TASK-019完了後

#### 背景
新しい統一Webhook方式を追加。旧方式（個別関数）も完全に動作し、フォールバックとして機能する。

#### タスク分解
- [x] `src/komon/webhook_notifier.py` モジュールの作成
  - `WebhookNotifier` クラスの実装
  - `send()` メソッドの実装
  - `kind` ごとのフォーマッター選択ロジック
- [x] `src/komon/formatters.py` モジュールの作成
  - `GenericFormatter` クラスの実装
  - `SlackFormatter` クラスの実装
  - `DiscordFormatter` クラスの実装
  - `TeamsFormatter` クラスの実装
- [x] 設定ファイルの拡張
  - `notifiers.webhooks` セクションの追加
  - 旧形式との共存ロジック（フォールバック）
- [x] 既存コードの拡張
  - 新形式が設定されていれば新方式を使用
  - 新形式が未設定なら旧方式を使用（フォールバック）
- [x] テストケースの追加
  - ユニットテスト: `WebhookNotifier` のテスト
  - ユニットテスト: 各フォーマッターのテスト
  - 統合テスト: 新旧形式の共存テスト
  - 統合テスト: フォールバックのテスト
- [x] ドキュメント更新
  - README.md: 新形式の設定方法を追加
  - docs/CHANGELOG.md: 変更履歴を追加

#### 完了条件
- ✅ 統一Webhookが動作する
- ✅ 旧形式のフォールバックが動作する
- ✅ 新旧形式が共存できる
- ✅ 全テストがパス（50件以上のテストケース追加）
- ✅ カバレッジを維持
- ✅ 全通知スクリプトに統合完了
- ✅ ドキュメント更新完了

#### 実装イメージ

**統一Webhook**:
```python
class WebhookNotifier:
    def __init__(self, webhooks):
        self.webhooks = webhooks
    
    def send(self, notification):
        for webhook in self.webhooks:
            if not webhook.get('enabled', True):
                continue
            
            formatter = self._get_formatter(webhook['kind'])
            payload = formatter.format(notification)
            
            response = requests.post(webhook['url'], json=payload, timeout=10)
            response.raise_for_status()
```

**設定例**:
```yaml
# 新方式（v1.26.0）- 推奨
notifiers:
  webhooks:
    - name: "slack"
      url: "env:KOMON_SLACK_WEBHOOK"
      kind: "slack"
      enabled: true
    
    - name: "discord"
      url: "env:KOMON_DISCORD_WEBHOOK"
      kind: "discord"
      enabled: false

# 旧方式（v1.X.X 〜 v1.25.0）- まだ動作する
notifications:
  slack:
    enabled: true
    webhook_url: "env:KOMON_SLACK_WEBHOOK"
```

---

### [TASK-021] Webhook通知統一化 Phase 3: 非推奨警告
**元アイデア**: [IDEA-023] Webhook通知の統一化（Phase 3）  
**ステータス**: 🔴 TODO  
**優先度**: Low  
**見積もり**: 小（1-2時間）  
**対象バージョン**: v1.27.0  
**依存**: TASK-020完了後

#### 背景
旧形式の設定に非推奨警告を表示し、ユーザーに新形式への移行を促す。旧形式はまだ動作する。

#### タスク分解
- [ ] 非推奨警告の実装
  - 旧形式の設定を検知
  - 警告メッセージの表示
  - ログへの記録
- [ ] 移行ガイドの作成
  - `docs/MIGRATION.md` の作成
  - 旧形式から新形式への移行手順
  - 設定例の提供
- [ ] ドキュメント更新
  - README.md: 非推奨警告の説明を追加
  - docs/CHANGELOG.md: 非推奨化を記録

#### 完了条件
- ✅ 旧形式の設定で警告が表示される
- ✅ 旧形式はまだ動作する
- ✅ 移行ガイドが完成している
- ✅ 全テストがパス

#### 実装イメージ

**警告メッセージ**:
```
⚠️ 警告: 旧形式の通知設定は非推奨です
   新形式への移行をお願いします
   詳細: docs/MIGRATION.md
   
   旧形式は v2.0.0 で削除されます
```

---

### [TASK-022] Webhook通知統一化 Phase 4: 旧方式削除
**元アイデア**: [IDEA-023] Webhook通知の統一化（Phase 4）  
**ステータス**: 🔴 TODO  
**優先度**: Low  
**見積もり**: 小（1-2時間）  
**対象バージョン**: v2.0.0  
**依存**: TASK-021完了後、十分な移行期間（v1.27.0 〜 v1.99.0）

#### 背景
旧形式のサポートを終了し、統一Webhookのみに移行する。これは破壊的変更（MAJOR）。

#### タスク分解
- [ ] 旧方式の削除
  - `send_slack_alert()` 関数の削除
  - `send_discord_alert()` 関数の削除
  - `send_teams_alert()` 関数の削除
  - 旧形式の設定サポートの削除
- [ ] エラーメッセージの実装
  - 旧形式の設定を検知した場合のエラー表示
  - 移行ガイドへの誘導
- [ ] テストケースの更新
  - 旧方式のテストを削除
  - 統一Webhookのテストのみに
- [ ] ドキュメント更新
  - README.md: 旧形式の記述を削除
  - docs/MIGRATION.md: v2.0.0への移行手順を追加
  - docs/CHANGELOG.md: 破壊的変更を記録

#### 完了条件
- ✅ 旧方式が完全に削除されている
- ✅ 統一Webhookのみが動作する
- ✅ 旧形式の設定でエラーが表示される
- ✅ 移行ガイドが完成している
- ✅ 全テストがパス

#### 実装イメージ

**エラーメッセージ**:
```
❌ エラー: 旧形式の通知設定は v2.0.0 で削除されました
   
   新形式への移行が必要です
   詳細: docs/MIGRATION.md
```

---

### [TASK-023] ネットワーク疎通チェック機能（ping/http）
**元アイデア**: [IDEA-024] ネットワーク疎通チェック機能（ping/http）  
**feature-name**: network-connectivity-check  
**ステータス**: 🟢 Done  
**完了日**: 2025-12-08 (v1.25.0)  
**優先度**: Medium  
**見積もり**: 中（6-8時間）

#### 背景
REST API実行前の事前条件確認や外部通信不可時の早期気づきのため、ネットワーク疎通の軽量チェック機能を追加。Komonの「アドバイザ（診断補助）」の範囲内で、軽量性を最優先。

**Komonの哲学を完全維持**:
- ✅ デフォルト動作は従来通り（`komon` 単体実行ではチェックしない）
- ✅ すべて opt-in（引数 or 設定で有効化）
- ✅ 軽量性を最優先
- ✅ 状態変化時のみ通知（正常→異常、異常→正常）

#### タスク分解

**Phase 1: 基本モジュール実装**
- [x] `src/komon/net/` ディレクトリの作成
- [x] `src/komon/net/__init__.py` の作成
- [x] `src/komon/net/ping_check.py` の実装
  - `check_ping()` 関数の実装
  - タイムアウト処理
  - エラーハンドリング
- [x] `src/komon/net/http_check.py` の実装
  - `check_http()` 関数の実装
  - GET/HEAD/POSTメソッド対応
  - タイムアウト処理
  - エラーハンドリング
- [x] `src/komon/net/state_manager.py` の実装
  - `NetworkStateManager` クラスの実装
  - NG状態のみ保持（OK状態は保持しない）
  - retention（寿命）付き自動削除
  - 状態ファイルの読み書き

**Phase 2: CLI引数の拡張**
- [x] `scripts/advise.py` の拡張
  - `--with-net` オプションの追加（全部：リソース・ログ + ping + http）
  - `--net-only` オプションの追加（ping + http のみ）
  - `--ping-only` オプションの追加（ping のみ）
  - `--http-only` オプションの追加（http のみ）
  - デフォルト動作は従来通り（ネットワークチェックなし）

**Phase 3: 設定ファイルの拡張**
- [x] `config/settings.yml.sample` の拡張
  - `network_check` セクションの追加
  - `ping.targets` の設定（デフォルト: 127.0.0.1）
  - `http.targets` の設定（デフォルト: https://komon-example.com）
  - `state.retention_hours` の設定（デフォルト: 24時間）
  - `enabled: false` をデフォルトに設定

**Phase 4: 通知ポリシーの実装**
- [x] 状態変化検知ロジックの実装
  - OK → NG：通知
  - NG → OK：復旧通知
  - NG → NG：通知なし（ログのみ）
  - OK → OK：通知なし
- [x] 通知メッセージのフォーマット
  - ping失敗時のメッセージ
  - http失敗時のメッセージ
  - 復旧時のメッセージ

**Phase 5: テストケースの追加**
- [x] ユニットテスト: `test_ping_check.py`（10件）
  - 正常系（ping成功）
  - 異常系（ping失敗、タイムアウト）
  - エラーハンドリング
- [x] ユニットテスト: `test_http_check.py`（10件）
  - 正常系（http成功、各メソッド）
  - 異常系（http失敗、タイムアウト）
  - エラーハンドリング
- [x] ユニットテスト: `test_state_manager.py`（15件）
  - 状態の保存・読み込み
  - retention による自動削除
  - 状態変化の検知
- [x] 統合テスト: `test_network_check_integration.py`（8件）
  - CLI引数の動作確認
  - 設定ファイルの読み込み
  - 通知ポリシーの動作確認

**Phase 6: ドキュメント更新**
- [x] README.md の更新
  - ネットワークチェック機能の説明
  - CLI引数の使い方
  - 設定例
- [x] docs/EXAMPLES.md の更新
  - 基本的な使い方
  - cron設定例
  - 上級者向け設定例
- [x] docs/CHANGELOG.md の更新
- [x] `.kiro/tasks/implementation-tasks.md` の更新

#### 完了条件
- ✅ ping疎通チェックが動作する
- ✅ http疎通チェックが動作する
- ✅ CLI引数（`--with-net`, `--net-only`, `--ping-only`, `--http-only`）が動作する
- ✅ デフォルト動作は従来通り（ネットワークチェックなし）
- ✅ 状態変化時のみ通知される
- ✅ NG状態のretentionが動作する
- ✅ 設定ファイルで有効/無効を切り替えられる
- ✅ 全545テストがパス（43件追加）
- ✅ カバレッジ92%を維持
- ✅ ドキュメントが更新されている

#### 実装イメージ

**CLI使用例**:
```bash
# 従来どおり（ネットワークチェックなし）
komon

# 全部（リソース・ログ + ping + http）
komon --with-net

# ネットワークチェックのみ
komon --net-only

# pingのみ
komon --ping-only

# httpのみ
komon --http-only
```

**設定例**:
```yaml
network_check:
  enabled: false  # デフォルトは無効
  
  ping:
    targets:
      - host: "127.0.0.1"
        description: "ローカルホスト（例）"
      - host: "8.8.8.8"
        description: "Google DNS"
    timeout: 3
    
  http:
    targets:
      - url: "https://api.example.com/health"
        description: "APIヘルスチェック"
        method: "GET"
      - url: "https://www.google.com"
        description: "外部接続確認"
        method: "HEAD"
    timeout: 10
    
  state:
    retention_hours: 24  # 24時間でNG状態を削除
    file_path: "data/network_state.json"
```

**cron設定例**:
```bash
# 基本（推奨・デフォルト）
*/5 * * * * /usr/local/bin/komon

# 便利に使いたい人
*/5 * * * * /usr/local/bin/komon --with-net

# こだわり運用（上級者向け）
*/5  * * * * komon                 # リソース＆ログ
*/15 * * * * komon --net-only      # ネットワークだけ
```

#### 期待効果
- REST API実行前の事前条件確認が可能
- 外部通信不可時の早期気づき
- ネットワーク疎通の軽量チェック
- Komonの「アドバイザ」としての価値向上
- opt-in設計により既存ユーザーへの影響ゼロ

#### 依存関係
- 既存機能との依存なし（完全に独立した新機能）
- TASK-019, 020との並行実装可能

---

## 優先順位の判断基準

**High Priority**:
- ユーザー体験を大きく改善する
- 実装コストが低〜中程度
- Komonの思想を強化する
- 既存機能との親和性が高い

**Medium Priority**:
- 便利だが必須ではない
- 実装コストが中程度
- 特定のユースケースで有用

**Low Priority**:
- 実装コストが高い
- 効果が不確実
- まずは他の機能を優先すべき

---

## アーカイブルール

- 次のバージョンがリリースされたら、前バージョンの完了タスクを `completed-tasks.md` に移動
- 直近バージョン（v1.18.0）の完了タスクはこのファイルに残す
- アーカイブは `completed-tasks.md` でバージョン降順に整理

## 更新履歴

- 2025-12-08: TASK-023を完了に更新（v1.25.0）
- 2025-12-08: TASK-023を追加（IDEA-024: ネットワーク疎通チェック機能）
- 2025-12-08: TASK-019, 020, 021, 022を追加（IDEA-023: Webhook通知の統一化、4フェーズに分割）
- 2025-12-03: v1.23.0の完了タスクを `completed-tasks.md` に移動（TASK-017）
- 2025-12-03: TASK-018を追加（IDEA-022: OS判定・汎用Linux対応）
- 2025-12-02: TASK-017を追加（IDEA-021: `komon advise` 出力フォーマットの改善）
- 2025-12-02: v1.22.0の完了タスクを `completed-tasks.md` に移動（TASK-005）
- 2025-12-01: v1.21.0の完了タスクを `completed-tasks.md` に移動（TASK-007）
- 2025-11-29: v1.19.0の完了タスクを `completed-tasks.md` に移動（TASK-004）
- 2025-11-29: v1.18.0の完了タスクを `completed-tasks.md` に移動（TASK-003）
- 2025-11-28: TASK-004を完了に更新（v1.19.0）
- 2025-11-27: v1.17.0の完了タスクを `completed-tasks.md` に移動（TASK-001）
- 2025-11-27: TASK-003を完了に更新（v1.18.0）
- 2025-11-26: タスクリストをアーカイブ方式に変更、v1.16.0以前の完了タスクを `completed-tasks.md` に移動
- 2025-11-26: TASK-001を完了に更新（v1.17.0）
- 2025-11-25: TASK-015を完了に更新（v1.16.0）
- 2025-11-24: TASK-014を完了に更新（v1.15.0）
- 2025-11-23: TASK-016を完了に更新（v1.14.0）
- 2025-11-23: TASK-013を完了に更新（v1.13.0）
- 2025-11-22: 年末年始の健全確認対応として4タスクを追加（TASK-012〜015）
- 2025-11-22: TASK-002を完了に更新（v1.11.0）
- 2025-11-22: 初版作成（future-ideas.md から11タスクを抽出）
