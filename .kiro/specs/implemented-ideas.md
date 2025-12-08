---
title: Komon - Implemented Ideas Archive
status: archive
version: 1.0
created: 2025-12-08
---

# Komon 実装済みアイデアのアーカイブ

このドキュメントは、`future-ideas.md`から実装済みのアイデアを移動したものです。

## 📋 アーカイブの目的

- future-ideas.mdの軽量化
- 実装済みアイデアの履歴保持
- 「何を実装したか」の可視化

---

## ✅ 実装済みアイデア一覧

### [IDEA-001] 通知メッセージの改善

**カテゴリ**: UX改善  
**提案日**: 2025-11-21  
**ステータス**: ✅ 実装済み (v1.17.0)

#### 背景・課題
現在の通知は機械的で「警告」感が強い。
「顧問（Komon）」という名前の通り、もっとやさしく気づかせる表現にしたい。

**現状の例**:
```
⚠️ CPU使用率が85%を超えました
```

#### 改善案と実装状況

**1. 言葉遣いを柔らかく、相談口調に** ✅ 実装済み (v1.10.1)
```
💬 ちょっと気になることがあります

CPUが頑張りすぎてるみたいです（85.0%）。
何か重い処理走ってます？
```

**実装内容:**
- `src/komon/analyzer.py` のメッセージ表現を変更
- CPU、メモリ、ディスクの3種類のメッセージを改善
- 既存テストは全てPASS

**2. 段階的な通知** ✅ 実装済み (v1.17.0)
- 初回：「ちょっと気になることがあります」（軽め）
- 2回目：「まだ続いてますね」（少し強め）
- 3回目：「そろそろ見た方がいいかも」（明確に）

**実装内容:**
- `src/komon/progressive_message.py` を新規作成
- 通知履歴（v1.11.0）を活用して繰り返し回数を判定
- 過去24時間以内の同一問題を自動カウント
- 設定ファイルでカスタムテンプレートや時間窓を変更可能
- プロパティベーステスト5件、ユニットテスト19件、統合テスト6件を追加
- 全268テストがパス、カバレッジ93%を維持

#### 今後の実装予定（オプション）
- 設定で口調を変えられるようにする？（カジュアル/フォーマル）
- メッセージテンプレートを外部化する？

#### 期待効果
- 「警告」ではなく「気づき」を与える体験 ✅ 達成
- ユーザーが身構えずに確認できる ✅ 達成
- Komonの「やさしく見守る」思想がより明確に ✅ 達成

---


---

### [IDEA-008] ローカル通知履歴の保存と表示

**カテゴリ**: 機能追加  
**提案日**: 2025-11-22  
**ステータス**: ✅ 実装済み (v1.11.0)

#### 背景・課題
Slack等の通知が使えない環境（インターネット遮断、セキュリティポリシー、設定未完了）でも、
Komonが検知した情報を後から確認できるようにしたい。

#### 改善案
- 通知記録ファイル: `notifications/queue.json`
- 最大保存件数: 100件程度
- `komon advise` で自動的に履歴を表示
- `komon advise --history 10` で直近10件を表示

#### 実装内容 ✅
- 新規モジュール: `src/komon/notification_history.py` を作成
- `src/komon/notification.py` に保存処理を追加
- `scripts/advise.py` に表示処理を統合
- 保存上限に達したら古いものから削除（最大100件）
- プロパティベーステスト7件、統合テスト6件、ユニットテスト5件を追加
- 全111テストがパス

#### 期待効果 ✅ 達成
- 通信制限環境でもKomonの価値を発揮
- 過去の警戒通知を後から確認・対処可能
- 軽量・静か・補助的という思想を維持

---


---

### [IDEA-003] コンテキストに応じた具体的アドバイス

**カテゴリ**: 機能強化  
**提案日**: 2025-11-21  
**ステータス**: ✅ 実装済み (v1.18.0)

#### 背景・課題
現状は「メモリ使用率が高いです」と伝えるだけで、
ユーザーが「で、どうすればいい？」となりがち。

#### 実装内容 ✅
- `src/komon/contextual_advisor.py` を新規作成（103行）
- プロセス情報の取得とパターンマッチング機能
- 10種類以上のパターン定義（node, docker, python等）
- 詳細度の調整機能（minimal/normal/detailed）
- `scripts/advise.py` に `advise_contextual()` 関数を追加
- `config/settings.yml.sample` に `contextual_advice` セクションを追加
- プロパティベーステスト5件、ユニットテスト25件、統合テスト11件を追加
- 全315テストがパス、カバレッジ93%を維持

#### 改善案（実装済み）

**プロセス情報に基づく具体的な提案**
```
💬 メモリ使用率: 85%

上位プロセス:
1. node server.js (PID 1234) - 2.3GB
   → 開発サーバーっぽいですね。使ってないなら止めてみては？
   コマンド: kill 1234
   
2. docker-proxy (PID 5678) - 1.8GB
   → 使ってないコンテナがあるかも
   確認: docker ps -a
   停止: docker stop <container_id>

3. python train.py (PID 9012) - 4.2GB
   → 機械学習の学習中っぽいですね。終わったら止まるやつかな？
   
とりあえず様子見でいいと思いますが、
気になるなら `htop` で確認してみてください 👀
```

**パターン認識による提案** ✅ 実装済み
- `node_modules` が多い → クリーンアップ提案
- ログファイルが肥大化 → logrotate設定の具体例
- 古いDockerイメージ → `docker system prune` の提案

#### 期待効果 ✅ 達成
- ユーザーがすぐに行動できる
- 学習コストが低い（コマンド例が分かる）
- 「顧問」として具体的なアドバイスを提供

---

## 💡 Ideas（アイデア段階）


---

### [IDEA-009] Slack通知にプロセス名を含める

**カテゴリ**: 機能強化  
**提案日**: 2025-11-22  
**ステータス**: ✅ 実装済み (v1.19.0)

#### 概要
Slack通知で、どのプロセスが高負荷を引き起こしているのかが一目で分かるようにする。

#### 実装内容 ✅
CPU/メモリ超過時のSlack通知メッセージに、上位3プロセスの情報を自動追加：

**CPU通知例**:
```
⚠️ Komon 警戒情報:
CPU使用率が高いです: 88.5%

📊 上位プロセス:
1. python: 35.2%
2. node: 28.1%
3. docker: 15.7%
```

**メモリ通知例**:
```
⚠️ Komon 警戒情報:
メモリ使用率が高いです: 92.3%

📊 上位プロセス:
1. chrome: 1024.5MB
2. python: 512.3MB
3. node: 256.1MB
```

#### 実装詳細 ✅
- `scripts/main.py` の `handle_alerts()` 関数を拡張
- `_get_process_info_for_metric()` 関数を新規追加
- CPU/メモリの上位3プロセス情報をフォーマット
- ディスクの場合はプロセス情報は表示しない（取得困難なため）
- 既存の通知機能に影響なし、後方互換性を維持
- テスト13件追加（ユニットテスト10件 + 統合テスト3件）
- 全352テストがパス、カバレッジ93%を維持

#### 期待効果 ✅ 達成
- すぐに `top` を開かなくても状況把握できる
- 管理者の対応速度向上
- 問題の原因特定が大幅に迅速化

---


---

### [IDEA-010] 継続実行中プロセスの検出

**カテゴリ**: 機能追加  
**提案日**: 2025-11-22  
**ステータス**: ✅ 実装済み (v1.22.0)

#### 概要
特定スクリプトがまだ終了していない場合に、継続稼働を助言表示。

#### 実装イメージ
```
💬 気になることがあります

以下のスクリプトがまだ実行中です:
- backup.py (PID 1234) - 実行時間: 3時間25分
- data_sync.py (PID 5678) - 実行時間: 1時間10分

cron間隔と実行時間のバランスは大丈夫ですか？
```

#### 実装内容 ✅
- `src/komon/long_running_detector.py` を新規作成
- `scripts/advise.py` に `advise_long_running()` 関数を追加
- `psutil` でプロセス一覧を走査し、実行時間を計算
- 設定可能な閾値（デフォルト: 3時間）
- 詳細度の調整機能（minimal/normal/detailed）
- プロパティベーステスト5件、ユニットテスト20件、統合テスト8件を追加
- 全385テストがパス、カバレッジ93%を維持

#### 期待効果 ✅ 達成
- 実行時間とcron間隔のミスマッチに気づける
- リソース圧迫の早期発見
- 長時間実行プロセスの可視化

---


---

### [IDEA-011] 多重実行プロセスの検出

**カテゴリ**: 機能追加  
**提案日**: 2025-11-22  
**ステータス**: ✅ 実装済み (v1.20.0)

#### 概要
cronなどによる同一スクリプトの多重起動を検出し、リソース圧迫の原因として助言。

#### 実装イメージ
```
💬 ちょっと気になることがあります

backup.py が 5個同時に実行されています。
cronの実行間隔が短すぎるかもしれません。
```

#### 実装メモ
- `src/komon/monitor.py` または `scripts/advise.py` に追加
- `cmdline` で同一スクリプトをカウント
- 一定数以上で警告

#### 期待効果
- cronジョブの過剰並列実行による不安定化を早期発見
- 実行間隔の見直しを促す

---


---

### [IDEA-012] ログ急増時の末尾抜粋表示

**カテゴリ**: 機能強化  
**提案日**: 2025-11-22  
**ステータス**: ✅ 実装済み (v1.21.0)

#### 概要
ログ急増の通知時、行数だけでなく実際のログ末尾も数行添付。

#### 実装イメージ
```
💬 ログが急増しています

/var/log/app.log: 1,234行増加

末尾10行:
[ERROR] Connection timeout to database
[ERROR] Retry attempt 1/3 failed
[ERROR] Retry attempt 2/3 failed
...
```

#### 実装メモ
- `scripts/main_log_monitor.py` を拡張
- 末尾10行程度をSlack通知に添付
- エラーメッセージや例外の兆候を即座に確認可能

#### 期待効果
- SSHでのログ参照作業を削減
- 即時の目視確認が可能

---


---

### [IDEA-014] 定期健全性レポート（週次）

**カテゴリ**: 機能追加  
**提案日**: 2025-11-22  
**ステータス**: ✅ 実装済み (v1.12.0)

#### 背景・課題
年末年始など長期休暇前に「システムが健全かどうか」を確認したいが、
毎回サーバにSSHで入って確認するのは手間がかかる。
異常がなくても定期的に状況を把握できる仕組みが欲しい。

#### 改善案
**毎週月曜9時に定期レポートをSlackに送信**

```
📊 週次健全性レポート (2025-11-18 〜 2025-11-24)

【リソース状況】
CPU使用率: 45.2% (先週比 +2.1%)
メモリ使用率: 62.8% (先週比 -1.5%)
ディスク使用率: 68.5% (先週比 +3.2%)

【今週の警戒情報】
- 11/20 15:30 - CPU使用率が85%を超えました
- 11/22 03:15 - ログ急増を検出 (/var/log/messages)

【トレンド】
✅ CPU: 安定
✅ メモリ: 安定
⚠️ ディスク: 緩やかに増加傾向

異常がなくても、定期的に確認しておくと安心ですね 👀
```

#### 実装内容 ✅
- 新規スクリプト: `scripts/weekly_report.py` を作成
- 新規モジュール: `src/komon/weekly_data.py`, `src/komon/report_formatter.py`
- 過去7日分のデータを集計
- cron設定例: `0 9 * * 1` (毎週月曜9時)
- 先週比の計算ロジック追加
- 通知履歴から警戒情報を抽出
- プロパティベーステスト6件、統合テスト6件、ユニットテスト26件を追加
- 全150テストがパス、カバレッジ92%

#### 期待効果 ✅ 達成
- サーバにログインせずにSlackで健全性確認
- 異常がなくても「見守られている」安心感
- 長期休暇前の確認作業が楽になる

---


---

### [IDEA-015] 段階的な閾値通知（警告→警戒→緊急）

**カテゴリ**: 機能強化  
**提案日**: 2025-11-22  
**ステータス**: ✅ 実装済み (v1.13.0)

#### 背景・課題
現状は単一の閾値（ディスク80%）で通知するだけ。
84%から90%に一気にジャンプするケース（Firewallログの大量取り込み等）があり、
段階的な通知で早期に気づきたい。

#### 改善案
**3段階の閾値を設定**

```yaml
thresholds:
  disk:
    warning: 70    # 警告（黄色）
    alert: 80      # 警戒（オレンジ）
    critical: 90   # 緊急（赤）
```

**通知メッセージの例**

```
# 70%超え（警告）
💛 ディスク使用率: 72.3%
そろそろ気にかけておいた方がいいかもしれません。

# 80%超え（警戒）
🧡 ディスク使用率: 84.5%
ちょっと気になる水準です。古いログやキャッシュを確認してみては？

# 90%超え（緊急）
❤️ ディスク使用率: 92.1%
かなり逼迫しています！早めの対応をお願いします。
```

#### 実装内容 ✅
- `settings.yml` の閾値設定を3段階に拡張
- 新規モジュール: `src/komon/settings_validator.py` を作成
- `src/komon/analyzer.py` の判定ロジックを3段階に変更
- 通知頻度制御（IDEA-016）と組み合わせて効果的に動作
- 既存の単一閾値設定との完全な後方互換性を維持
- プロパティベーステスト3件、ユニットテスト12件、統合テスト8件を追加
- 全160テストがパス、カバレッジ93%

#### 期待効果 ✅ 達成
- 急激な変化に対する早期警戒
- 段階的な対応が可能（70%で準備、90%で緊急対応）
- 「オオカミ少年」にならない適切な警告レベル

---


---

### [IDEA-016] 通知頻度制御（同一アラートの抑制）

**カテゴリ**: 機能強化  
**提案日**: 2025-11-22  
**ステータス**: ✅ 実装済み (v1.15.0)

#### 背景・課題
現状は5分おきにcronが動いており、閾値を超え続けると5分おきに通知が飛ぶ。
「はいはい、いつものやつね」となって見なくなる（オオカミ少年化）リスクがある。

#### 改善案
**同一アラートの通知間隔を制御**

```yaml
notifications:
  throttle:
    enabled: true
    interval_minutes: 60  # 同一アラートは60分間隔まで
    escalation_minutes: 180  # 3時間経過したら再度通知
```

**動作例**
```
09:00 - ディスク85%を検出 → 通知送信 ✅
09:05 - ディスク86%を検出 → 通知抑制（前回から5分）
09:10 - ディスク87%を検出 → 通知抑制（前回から10分）
...
10:00 - ディスク88%を検出 → 通知送信 ✅（前回から60分経過）
10:05 - ディスク89%を検出 → 通知抑制
...
12:00 - ディスク90%を検出 → 通知送信 ✅（前回から120分経過）
```

**エスカレーション機能**
```
09:00 - ディスク85%を検出 → 通知送信
12:00 - まだディスク85%以上 → 再通知
      「3時間経過しましたが、まだ高い状態が続いています」
```

#### 実装内容 ✅
- 通知履歴に最終通知時刻を記録（`data/notifications/throttle.json`）
- `src/komon/notification.py` にNotificationThrottleクラスを追加
- `src/komon/analyzer.py` にanalyze_usage_with_levels()関数を追加
- メトリクスタイプ（CPU/MEM/DISK）ごとに管理
- 閾値レベルが上がった場合は即座に通知（警告→警戒、警戒→緊急）
- エスカレーション機能（3時間継続で再通知）
- プロパティベーステスト4件、ユニットテスト15件、統合テスト8件を追加
- 全189テストがパス

#### 期待効果 ✅ 達成
- 通知疲れの防止
- 重要な通知を見逃さない
- 長時間継続する問題の再通知

---


---

### [IDEA-017] ディスク使用量の増加トレンド予測

**カテゴリ**: 機能追加  
**提案日**: 2025-11-22  
**ステータス**: ✅ 実装済み (v1.16.0)

#### 背景・課題
84%から90%に一気にジャンプするケースがあり、
「このままだと○日後に100%になる」という予測があると事前対応できる。

#### 改善案
**過去のトレンドから将来を予測**

```
💬 ディスク使用率: 75.2%

【増加トレンド】
- 7日前: 68.5%
- 今日: 75.2%
- 増加率: +6.7% / 7日

【予測】
このペースだと約18日後に90%に達する見込みです。
そろそろログのクリーンアップを検討してみては？

推奨コマンド:
  sudo journalctl --vacuum-time=7d
  sudo find /var/log -name "*.gz" -mtime +30 -delete
```

#### 実装内容 ✅
- `src/komon/disk_predictor.py` を新規作成
- 過去7日分のディスク使用率データから線形回帰により増加率を計算
- 90%到達予測日を算出（「あとN日で90%に到達」）
- 前日比+10%以上の急激な増加を検出し、早期警告
- `scripts/advise.py` に`advise_disk_prediction()`関数を追加
- 週次レポートにも予測結果を自動的に含める
- プロパティベーステスト8件、ユニットテスト17件、統合テスト5件を追加
- 全238テストがパス、カバレッジ94%を維持

#### 期待効果 ✅ 達成
- 事前の計画的な対応が可能
- 急激な変化の早期検知
- 「あと○日で危険」という具体的な情報

---

---

---

## 💡 Ideas（アイデア段階）- 低優先度


---

### [IDEA-022] OS判定・汎用Linux対応（マルチディストリビューション対応）

**カテゴリ**: 機能強化・環境対応  
**提案日**: 2025-12-03  
**ステータス**: ✅ 実装済み (v1.24.0)  
**優先度**: 高（Raspberry Pi等での誤動作防止）

#### 背景・課題

現在のKomonはRHEL系（AlmaLinux, Rocky Linux, Amazon Linux 2023）を想定して設計されているが、
Debian系（Raspberry Pi OS, Ubuntu, Debian）でも動作する可能性がある。

しかし、以下の問題がある：
- **パッケージ管理コマンドが異なる**（dnf vs apt）
- **ログファイルのパスが異なる**（/var/log/messages vs /var/log/syslog）
- **誤ったアドバイスを出してしまう危険性**（Raspberry Piでdnfコマンドを提案等）

**Komonの一貫した哲学**:
> 「誤ったアドバイスをしない」

この哲学を守るため、OS判定機能が必要。

#### 改善案

**1. OS自動判定機能**

`/etc/os-release` を読み取り、OS ファミリを判定：

```python
def detect_os_family():
    """OSファミリを自動判定"""
    try:
        with open('/etc/os-release', 'r') as f:
            content = f.read()
            
        # ID または ID_LIKE から判定
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

**判定結果**:
- `rhel`: AlmaLinux, Rocky Linux, Amazon Linux 2023, RHEL, CentOS等
- `debian`: Debian, Ubuntu, Raspberry Pi OS等
- `suse`: openSUSE, SLES等（将来用）
- `arch`: Arch Linux等（将来用）
- `unknown`: 判定不能

**2. 設定での上書き機能**

```yaml
system:
  os_family: auto  # auto / rhel / debian / suse / arch / unknown
```

**動作**:
- `auto`: 自動判定で決める（デフォルト）
- その他: 判定結果を上書きし、Komonは指定されたOS前提で動作

**理由**: 未来の"RHEL系列名変更"などに強くなり、ユーザーが正しく扱える環境なら確実に意図通り動く。

**3. OS別のアドバイス出し分け**

特に**セキュリティ更新系**で重要：

```python
# RHEL系
"sudo dnf update --security"

# Debian系
"sudo apt update && sudo apt upgrade"

# unknown
"ご利用OSに応じたパッケージ管理コマンドで更新を確認してください"
```

**4. ログパスの切り替え**

```python
LOG_PATHS = {
    'rhel': '/var/log/messages',
    'debian': '/var/log/syslog',
    'unknown': None  # ログアドバイスは抑制
}
```

**5. パッケージ系アドバイスの制限**

Debian系では：
- パッケージ名の違いが大きい
- ユーザー環境差が激しい
- 誤ったアドバイスの危険が高い

→ **「Debian系ではこの項目をスキップ」が最適**

**理由**: Komonの"誤アドバイスをしない"という一貫性に合う。

**6. Windows非対応の明示**

```python
if sys.platform == 'win32':
    # WSLかどうかチェック
    if not is_wsl():
        print("❌ Komonは Windows ネイティブでは動作しません")
        print("   WSL (Windows Subsystem for Linux) 経由で利用してください")
        sys.exit(1)
```

**WSL判定**:
```python
def is_wsl():
    """WSL環境かどうかを判定"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False
```

**7. README等に「RHEL推奨」を明記**

```markdown
## 対応プラットフォーム

### 推奨環境
- AlmaLinux 9+
- Rocky Linux 9+
- Amazon Linux 2023+
- RHEL 9+

### ベストエフォート対応
- Debian 11/12
- Ubuntu 22.04/24.04
- Raspberry Pi OS

**制限事項**:
- パッケージ系アドバイスは非表示
- ログパスが異なる場合あり

### 非対応
- Windows（WSL経由なら利用可能）
- macOS
```

#### 実装アーキテクチャ

**新規モジュール**: `src/komon/os_detection.py`

```python
class OSDetector:
    """OS判定クラス"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.os_family = self._detect()
    
    def _detect(self):
        """OS自動判定"""
        # 設定で上書きされている場合
        override = self.config.get('system', {}).get('os_family', 'auto')
        if override != 'auto':
            return override
        
        # 自動判定
        return detect_os_family()
    
    def get_package_manager_command(self, action='update'):
        """パッケージ管理コマンドを取得"""
        commands = {
            'rhel': {
                'update': 'sudo dnf update',
                'security': 'sudo dnf update --security',
            },
            'debian': {
                'update': 'sudo apt update && sudo apt upgrade',
                'security': 'sudo apt update && sudo apt upgrade',
            },
            'unknown': {
                'update': None,
                'security': None,
            }
        }
        return commands.get(self.os_family, {}).get(action)
    
    def get_log_path(self):
        """ログファイルパスを取得"""
        paths = {
            'rhel': '/var/log/messages',
            'debian': '/var/log/syslog',
            'unknown': None,
        }
        return paths.get(self.os_family)
    
    def should_show_package_advice(self):
        """パッケージ系アドバイスを表示すべきか"""
        # Debian系では非表示
        return self.os_family == 'rhel'
```

#### 期待効果

**1. 誤動作の防止**
- Raspberry Piでdnfコマンドを提案しない
- Debian系で存在しないログパスを参照しない

**2. 「誤ったアドバイスをしない」の徹底**
- 不明なOSでは具体的なコマンドを出さない
- 確実に動作する範囲でのみアドバイス

**3. 将来的な拡張性**
- 他のディストリビューション対応の基盤
- ユーザーの上書き設定で柔軟に対応

**4. サポート範囲の明確化**
- 「RHEL推奨」を明示
- ベストエフォート対応の範囲を明確に

#### 実装優先度と段階

**Phase 1: 基本機能（v1.24.0）**
1. OS判定ロジック追加
2. system.os_family 設定
3. Windows非対応の明示

**Phase 2: 機能制限（v1.24.0 or v1.25.0）**
4. アドバイス出し分け
5. Debian系でパッケージ系抑制

**Phase 3: 細かい対応（v1.25.0）**
6. ログパス切替
7. README更新

#### テスト戦略

```python
# tests/test_os_detection.py

def test_detect_rhel():
    """RHEL系の判定テスト"""
    # /etc/os-release をモック
    assert detect_os_family() == 'rhel'

def test_detect_debian():
    """Debian系の判定テスト"""
    assert detect_os_family() == 'debian'

def test_override_os_family():
    """設定での上書きテスト"""
    config = {"system": {"os_family": "debian"}}
    detector = OSDetector(config)
    assert detector.os_family == "debian"

def test_package_manager_command():
    """パッケージ管理コマンドのテスト"""
    detector = OSDetector()
    detector.os_family = 'rhel'
    assert 'dnf' in detector.get_package_manager_command('update')
    
    detector.os_family = 'debian'
    assert 'apt' in detector.get_package_manager_command('update')
```

#### 開発者コメント

```
ChatGPTとの対話で生まれたアイデア。

「Raspberry Piで動かしたらdnfコマンドを提案された」
という事故を防ぐための機能。

Komonの哲学「誤ったアドバイスをしない」を守るため、
OS判定は必須。

完全対応は難しいが、
「分からないものには具体的なアドバイスをしない」
という誠実な姿勢が大事。

段階的に実装して、
まずは「壊れない」ことを保証する。
```

---


---



---

## 更新履歴

- 2025-12-08: RESEARCH-001を`research-projects.md`に移動
- 2025-12-08: 実装済みアイデアを`future-ideas.md`から分離してこのファイルを作成
