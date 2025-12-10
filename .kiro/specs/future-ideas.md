---
title: Komon - Future Ideas & Improvements
status: ideas
version: draft
created: 2025-11-21
---

# Komon 将来の改善案

このドキュメントは、将来実装を検討したいアイデアを記録します。
優先度や実装時期は未定ですが、「Komonらしさ」を強化する方向性として保持します。

## 📖 このファイルと development-improvements.md の使い分け

### このファイル（future-ideas.md）
**対象**: **ユーザー向け機能**の追加・改善

**記録する内容**:
- ✅ 新機能の追加
- ✅ 既存機能の改善
- ✅ 通知メッセージの改善
- ✅ 検出機能の追加
- ✅ レポート機能の追加
- ✅ ユーザビリティの向上

**特徴**:
- ユーザーが直接体験する機能
- Komonの「やさしく見守る」価値を高める
- 「Komonで何ができるか」を増やす

**例**:
- 段階的通知メッセージ
- コンテキスト型アドバイス
- ディスク使用量予測
- 長時間実行プロセス検出
- State Snapshot & Diff Detection

---

### development-improvements.md
**対象**: **開発者向け基盤**の改善

**記録する内容**:
- ✅ 開発体制・プロセスの改善
- ✅ コード品質向上（型ヒント、リファクタリング等）
- ✅ セキュリティ強化
- ✅ テスト戦略の改善
- ✅ CI/CD・ビルドシステムの改善
- ✅ ドキュメント整備（開発者向け）
- ✅ 環境対応・拡張性（OS抽象化等）
- ✅ ステアリングルールの強化

**特徴**:
- ユーザーには直接見えない（間接的に恩恵）
- 開発者が体験する改善
- 「Komonをどう作るか」を改善

**例**:
- 型ヒント（mypy）の導入
- 脆弱性スキャンの自動化
- マルチLinuxディストリビューション対応
- AI開発ルールの明文化

---

### 判断に迷ったら

**質問1**: ユーザーが直接体験する機能か？
- YES → `future-ideas.md`（このファイル）
- NO → 次の質問へ

**質問2**: 開発者・保守者が体験する改善か？
- YES → `development-improvements.md`
- NO → どちらにも該当しない（記録不要かも）

**例**:
- 「週次レポート機能」→ ユーザーが体験 → `future-ideas.md`
- 「型ヒント追加」→ 開発者が体験 → `development-improvements.md`
- 「マルチOS対応」→ 開発基盤の拡張 → `development-improvements.md`
- 「英語版ドキュメント」→ ユーザー向けドキュメント → `development-improvements.md`

---

---

## 🔥 High Priority（優先度: 高）

### [IDEA-002] 学習機能（パターン認識）

**カテゴリ**: 機能強化  
**提案日**: 2025-11-21  
**ステータス**: アイデア段階

#### 概要
ユーザーの行動パターンを学習して、不要な通知を減らす。

#### 具体例
- 「毎週月曜10時はバックアップで負荷が高い」→ その時間は通知しない
- 「この人は夜型開発者」→ 深夜の通知は控えめに
- 「このプロセスはいつも動いてる」→ 正常として扱う

#### 検討事項
- 学習データの保存方法
- プライバシーへの配慮
- 誤学習のリスク
- シンプルさとのバランス

#### 実装難易度
中〜高（Komonの「シンプル」思想と相反する可能性あり）

---

### [IDEA-004] 週次レポート機能

**カテゴリ**: 機能追加  
**提案日**: 2025-11-21  
**ステータス**: アイデア段階

#### 概要
週に1回、振り返りレポートを送信。

#### 実装イメージ
```
📊 今週の振り返り (11/14 - 11/20)

気になったこと:
- 火曜日の15時頃、CPU使用率が3時間高止まりしてました
- ログが普段の2倍出てる日が2日ありました
- 先週より全体的にメモリ使用量が15%増えてます

何か心当たりありますか？
```

#### 検討事項
- 週次実行のcron設定
- レポート内容の粒度
- 通知先（Slack/メール）
- ユーザーが有効/無効を選べるように

---

### [IDEA-005] Git連携（軽量）

**カテゴリ**: 機能追加  
**提案日**: 2025-11-21  
**ステータス**: アイデア段階

#### 概要
Gitのコミット/デプロイと関連付けて分析。

#### 実装イメージ
```
💬 昨日デプロイしましたよね？

その後からメモリ使用量が20%増えてます。
関係あるかもしれません。

最近のコミット:
- feat: add caching layer (3日前)
- fix: memory leak in worker (昨日)
```

#### 検討事項
- `.git` ディレクトリの読み取り
- デプロイ検知の方法
- 因果関係の推測精度
- 実装コストとメリットのバランス

---

### [IDEA-006] 対話モード `komon chat`

**カテゴリ**: 機能追加  
**提案日**: 2025-11-21  
**ステータス**: アイデア段階

#### 概要
対話的にKomonに質問できるモード。

#### 実装イメージ
```bash
$ komon chat

💬 Komon: こんにちは。何か気になることはありますか？

> 最近メモリ使用量が増えてる気がする

💬 Komon: そうですね、先週と比べて平均15%増えてます。
特に node プロセスが増えてますね。

> どうすればいい？

💬 Komon: まず docker ps で不要なコンテナがないか確認してみてください。
あと、開発サーバーを複数起動してませんか？
```

#### 検討事項
- 自然言語処理の必要性（簡易的なキーワードマッチでも可？）
- 実装コスト vs メリット
- Komonの「シンプル」思想との整合性

#### 実装難易度
高（LLM連携が必要？または簡易的なパターンマッチ？）

---

### [IDEA-007] トレンド予測機能

**カテゴリ**: 機能追加  
**提案日**: 2025-11-21  
**ステータス**: アイデア段階

#### 概要
過去のトレンドから将来を予測。

#### 実装イメージ
```
💬 予測: このペースだとディスクが2週間後に90%超えそうです

最近のディスク使用量:
- 1週間前: 65%
- 今日: 75%
- 予測（2週間後）: 92%

そろそろログのクリーンアップを検討してみては？
```

#### 検討事項
- 予測アルゴリズムの精度
- 誤報のリスク
- 実装コスト

---

### [IDEA-013] トップ3増加ログの可視化

**カテゴリ**: 機能強化  
**提案日**: 2025-11-22  
**ステータス**: アイデア段階

#### 概要
ログ傾向分析の結果を「通知」だけでなく「魅せる」方向へ進化。

#### 実装イメージ
- 過去n日分と比較して最も増加率が高かった上位3件を通知
- または、matplotlib等でグラフ画像を生成してSlack投稿

#### 実装メモ
- `scripts/main_log_trend.py` を拡張
- グラフ生成は `matplotlib` を使用
- Slack APIで画像アップロード

#### 検討事項
- グラフ生成の依存関係追加（matplotlib）
- Komonの「軽量」思想とのバランス

#### 期待効果
- システム運用のモチベーション向上
- 定量的な把握が容易に

---

## 実装時のワークフロー

```
1. アイデアが出る
   ↓
2. このファイル（future-ideas.md）に記録
   ステータス: アイデア段階 or 検討中
   ↓
3. 実装を決定
   ↓
4. komon-system.md に仕様として追加
   ↓
5. 実装・テスト
   ↓
6. このファイルのステータスを「実装済み」に更新
   CHANGELOG.md に記録
   ↓
7. 次のバージョンでリリース
```

---

## 優先順位の考え方

**高優先度の条件**:
- Komonの「やさしく見守る」思想を強化する
- 実装コストが低い
- ユーザー体験を大きく改善する
- シンプルさを損なわない

**低優先度 or 見送りの条件**:
- エンタープライズ向け機能
- 複雑化を招く
- 既存ツールで代替可能
- 保守コストが高い

---

---

## 🔥 High Priority（優先度: 高）- 年末年始の健全確認対応

### [IDEA-018] 通知・表示内容の多言語化対応

**カテゴリ**: 機能追加  
**提案日**: 2025-11-23  
**ステータス**: アイデア段階  
**優先度**: 低（他のアイデアを優先）

#### 背景・課題
現在の通知やメッセージは日本語のみ。
将来的に英語や他の言語でも使えるようにしたい。
ただし、利用者が限定的な場合は必須ではない。

#### 改善案
**settings.ymlに言語設定を追加**

```yaml
general:
  language: ja  # ja, en, zh, ko, etc.
  # デフォルトは日本語
```

**メッセージテンプレートの多言語化**

```python
# messages.py
MESSAGES = {
    'ja': {
        'cpu_high': '💬 CPUが頑張りすぎてるみたいです（{usage}%）',
        'memory_high': '💬 メモリ使用率が高めです（{usage}%）',
    },
    'en': {
        'cpu_high': '💬 CPU usage is quite high ({usage}%)',
        'memory_high': '💬 Memory usage is high ({usage}%)',
    }
}
```

#### 実装メモ
- `src/komon/messages.py` を新規作成
- 全ての通知メッセージを多言語対応
- `settings.yml` から言語設定を読み込み
- デフォルトは日本語（ja）
- 対応言語: 日本語、英語、（将来的に中国語、韓国語等）

#### 検討事項
- 翻訳の品質維持
- 全メッセージの網羅的な対応
- 実装コスト vs 利用者数
- 「やさしい口調」の多言語表現の難しさ

#### 期待効果
- 国際的な利用者への対応
- オープンソースとしての汎用性向上
- ただし、現時点では優先度は低い

---

---

## 🔮 Future Evolution（将来の進化）

### [IDEA-019] State Snapshot & Diff Detection（状態スナップショット＆差分検知）

**カテゴリ**: 機能追加（大型）  
**提案日**: 2025-11-26  
**ステータス**: アイデア段階  
**優先度**: 中〜高（TASK-001完了後に検討）

#### 背景・課題

**ChatGPTとの対話から生まれた構想**:
- Linuxのクライアント利用者が増えている
- Windows→Linux移行者は「なんだか知らないけどパソコンが守ってくれる」と思い込みがち
- でもLinuxは利用者自身のセキュリティ意識に依存している
- Komonの無理のない処理範囲で、利用者のセキュリティ意識を補完できないか

**核心的な発想**:
- 「いつもと（もしくは前回と）何かが違う」を検知する
- シグネチャには頼らず、静的解析可能な範囲でのチェック
- EDRにはならない、軽量アドバイザーとしての立ち位置を維持

#### 改善案の全体像

**1. Snapshot（状態スナップショット）機能**

定期的に軽量なメタ情報を保存：
```yaml
snapshot:
  enabled: true
  interval_hours: 6  # 推奨6時間、1〜24で調整可能
  retention_days: 30  # 1ヶ月保存（約120件）
  baseline_window: 1  # 直近1件をベースライン（最大5件）
```

**保存内容（軽量メタ情報のみ）**:
- CPU/メモリ/ディスク/inode使用率
- プロセス総数、怪しいパスから起動しているプロセス
- LISTENポート一覧
- systemctl --failed のサービス名
- firewall状態、SSH設定の重要フラグ
- （必要なら）起動直後のエラー行を2〜3件

**保存頻度と件数**:
- デフォルト: 6時間ごと（0/6/12/18時）→ 1日4件
- 1ヶ月保存: 約120件
- ディスク使用量: 最大10MB程度（1件あたり数KB〜100KB）

**2. Baseline（比較対象）の扱い**

- **基本**: 直近1件をベースラインとして比較
- **補助**: 直近5件までを「珍しさ」「ノイズ」判断に使用
- **リセット**: `komon --baseline-reset` で基準をクリア

**3. Startup-Check モード（起動時軽量診断）**

PC/サーバ起動時に前回スナップショットと比較：
```bash
# systemd oneshot で実行
komon --startup-check
```

**出力例**:
```
[Komon Startup Check] 今日のひとこと：
前回より /var/log のサイズが大きく増えています。
必要であれば journalctl を確認してみてください。
```

**4. 通常モード vs ポーリングモード**

**通常モード（固定間隔）**:
- ユーザー指定の間隔（1分〜24時間）で実行
- cron / systemd-timer で非常駐
- シンプル・軽量

**ポーリングモード（異常時だけ間隔を詰める）**:
- Komonを常駐プロセスとして起動
- デフォルト: 6時間間隔
- 異常検知時: 15分 → 30分 → 1時間 → 2時間 → 6時間と戻す
- フラッピング対策（ヒステリシス）付き

**5. 異常レベル（Severity）の3段階化**

- 🟢 情報（INFO）: 新規LISTENポート等
- 🟡 注意（WARNING）: systemd failed等
- 🔴 異常（ALERT）: /tmpからの不審バイナリ、急激なディスク増加

#### 実装イメージ

**モジュール構成**:
```
komon/
├─ snapshot/          # 取得・保存・読み込み
├─ diff/              # 前回との比較
├─ severity/          # 異常レベルの判定
├─ startup/           # startup-check 機能
├─ polling/           # ポーリング内部ループ
└─ baseline/          # 基準の管理・リセット
```

**設定例**:
```yaml
snapshot:
  enabled: true
  interval_hours: 6
  retention_days: 30
  baseline_window: 1
  max_disk_usage_mb: 10

startup_check:
  enabled: true
  systemd_service: true

polling:
  enabled: false
  base_interval_minutes: 360
  min_interval_minutes: 15
  backoff_steps_minutes: [15, 30, 60, 120, 360]
```

#### 期待効果

**サーバ運用者向け**:
- 長期傾向の把握
- 設定変更の検知
- サービス異常の早期発見

**開発サーバ向け**:
- 起動時チェックで安心
- 頻繁な再起動環境との相性が良い
- 設定事故の早期発見

**クライアントLinux向け**:
- セキュリティ意識の補完
- 「いつもと違う」に気づくきっかけ
- Windows移行者の安心感

#### Komonらしさとの整合性

**✅ 軽量性**:
- スナップショットは要約メタ情報のみ
- 6時間間隔なら負荷はほぼゼロ
- 既存のpsutil、systemd情報の活用

**✅ アドバイザー性**:
- 「いつもと違うよ」という気づきを与える
- 判断は人間に委ねる
- EDRにならない明確な線引き

**✅ 実装の現実性**:
- 既存のKomonアーキテクチャに自然に組み込める
- 小さく刻んで段階的に実装可能
- 依存関係も増やさない

**✅ 哲学との一致**:
- 「自分が欲しいものを自分で作る」
- 「どこまでもカバーしますよ」ではない
- 「軽い顧問」としての立ち位置を維持

#### 実装の弱点（認識している穴）

**1. 短時間で完結する異常には弱い**:
- 2:00に侵入 → 2:10に荒らして 2:20に消える
- スナップショットは6時間ごとなので見逃す可能性

**2. 前回の状態がすでにおかしい問題**:
- 前回スナップショット取得時に、すでに侵害済みの場合
- Komonはその状態を「基準」として覚えてしまう
- → baseline reset で対応

**3. 6時間間隔ゆえの発見の遅さ**:
- 最長6時間は気づけない
- リアルタイム検知には絶対かなわない
- → ポーリングモードで緩和可能

**4. ノートPC・開発サーバ特有のスケジュールずれ**:
- 0, 6, 12, 18時に電源が付いているとは限らない
- → systemd-timer の Persistent=true で緩和

**5. 見えている情報がメタ情報だけ**:
- プロセス名・ポート・パスは分かるが、善悪の判断はできない
- → 人間の判断が必要（Komonらしさでもある）

**6. フォールスポジティブ／ノイズのリスク**:
- 開発環境では変化が多い
- 全部「前回と違う」として報告されるとノイズに
- → severity レベルと通知頻度制御で緩和

**7. マルウェア側から見ると回避しやすい**:
- 定期的にメタ情報だけ見られてるだけなら回避可能
- → Komonは「攻撃を防ぐ」道具ではなく「気づくきっかけ」の道具

#### 哲学の明文化

README / docs に必ず明示：
```
Komon は「軽量な顧問」であり、EDR ではありません。

- いつもと違う変化
- 忘れがちな危険設定
- 異常の"兆候"やちょっとした違和感

こうしたものに気づくための補助ツールです。

短時間で終わる攻撃や、高度な標的型攻撃を完全に防ぐことはできません。
より強力な防御が必要な場合は、EDR / SIEM など専門ツールと併用してください。
```

#### 実装ステップ（もし実装するなら）

**Phase 1: 基礎（軽量・確実）**
- snapshot取得（JSON保存）
- 前回との差分検出
- baseline reset

**Phase 2: 実用化（使ってみる）**
- startup-check モード
- systemd service サンプル
- 通知の文章調整

**Phase 3: 高度化（必要なら）**
- severity レベル
- ポーリングモード
- 5件履歴での「珍しさ」判定

#### 実装優先度

**今すぐやる必要はない**:
- TASK-001（段階的通知）が完了してから
- v1.12.0 or v1.13.0 のタイミング

**でも設計は今詰めておく価値がある**:
- この構想は Komonの将来性を大きく広げる
- クライアントLinux向けの価値が高い
- 「軽量EDR-lite」としての新しいポジション

#### 相棒（ChatGPT）の評価

**95点 / 100点**

**良いところ**:
- 哲学に完全一致
- 多くのユーザー層に刺さる
- 実装が軽くて簡単
- 過剰防御に寄らない
- Komonらしい優しさが強まっている
- 自然な将来性がある

**改善余地**:
- 異常レベルの定義は実装しながら微調整が必要
- polling mode のヒステリシスはチューニングしつつ詰める
- snapshot のデータ項目は実際の使い心地で見直す可能性あり

#### 開発者コメント

```
「自分が欲しいものを自分で作る」がKomonの動機。

ChatGPTとの対話で、この構想が自然に湧いてきた。
これは私が本当に欲しい機能だと思う。

完璧を目指すより「小さく動くもの」から得られる気づきが一番価値ある。

構想段階で完璧になることはない。
実際に組んで、まずは自分で使って、
体験から出た穴や改修項目を洗い出す。

逆にもう構想は十分できてきていて、
プロトタイプ開発に移った方がいい段階なのかもしれない。
```

#### 関連する既存機能

このアイデアは、以下の既存機能と連携します：
- エラー検知（monitor.py）
- Slack通知（notification.py）
- ログ分析（log_analyzer.py）
- 履歴管理（notification_history.py）

新規に必要な機能：
- 状態スナップショット取得（snapshot.py）
- 差分検出（diff.py）
- ベースライン管理（baseline.py）
- 起動時チェック（startup.py）
- ポーリングモード（polling.py）

#### Kiroからの追加提案（Phase 2以降で検討）

基本機能（Phase 1）を実装して使ってみた後、以下の拡張を検討する価値があります：

**1. スナップショット比較の「可視化」**
```bash
komon snapshot --compare --visual

【ディスク使用率の推移】
70% ████████████████░░░░ (7日前)
75% ██████████████████░░ (今日)
↑ +5% 増加
```
- CLIでもASCIIアートで視覚的に
- Komonの「優しさ」が増す

**2. 「正常パターン学習」の軽量版**
- 完全な機械学習ではなく、シンプルな統計（平均・標準偏差）
- 過去30日の平均値を「正常範囲」として記録
- 「いつもの範囲」から大きく外れたら通知
- false positive を減らせる

**3. 「変化の理由」を推測する軽量ロジック**
```
💬 ディスク使用率が前回より+15%増えています

【推測される理由】
✓ /var/log/messages が 2GB 増加
✓ docker イメージが 3個 増加

【推奨アクション】
sudo journalctl --vacuum-time=7d
docker system prune
```
- スナップショットに「どこが増えたか」も記録
- パターンマッチングで理由を推測

**4. 「startup-check」の結果を履歴化**
```bash
komon startup-history

【起動履歴】
2025-11-26 09:00 ✅ 正常
2025-11-25 18:30 ⚠️ /var/log 増加
2025-11-24 20:15 🔴 failed service 検出
```
- 「いつから異常だったか」が分かる
- トラブルシューティングに役立つ

**5. 「差分レポート」の定期送信**
- 週次レポート（IDEA-014）に「今週の変化」を追加
- 設定変更の見落としを防ぐ

**6. 「ロールバック支援」機能**
```
🔴 異常を検知しました

【ロールバック方法】
sudo systemctl stop suspicious.service
sudo systemctl disable suspicious.service
```
- 「元に戻す」方法を提案
- 初心者にも優しい

**7. 「比較モード」の柔軟化**
```bash
# 1週間前と比較
komon snapshot --compare --days-ago 7

# 「正常だった時」と比較
komon snapshot --compare --baseline-good
```
- 「いつから変わったか」を特定しやすい

**8. 「変化の重要度」を自動判定**
```python
importance = {
    'ssh_config_change': 'HIGH',      # セキュリティ
    'firewall_disabled': 'HIGH',      # セキュリティ
    'new_listen_port': 'MEDIUM',      # 要確認
    'process_count_change': 'LOW',    # 通常の変動
}
```
- 全ての変化を同じ重みで通知しない
- 重要度に応じて通知方法を変える

**実装の優先順位**:
1. まずは Phase 1（基本機能）を実装
2. 自分で使ってみて、本当に欲しい機能を見極める
3. 上記の提案から必要なものだけを選んで実装
4. Komonの「軽量・シンプル」を損なわない範囲で

---

### [IDEA-020] Pythonバージョン管理（CI/CD + サーバ環境）

**カテゴリ**: 開発環境管理・セキュリティ  
**提案日**: 2025-11-27  
**ステータス**: アイデア段階  
**優先度**: 中（サーバ環境チェックは重要、CI/CDチェックは低）

#### 背景・課題

**ChatGPTとの対話から生まれた発想**:
- GitHub ActionsでPython 3.10, 3.11, 3.12をテストしている
- 2026年10月にPython 3.10がEOL/EOSになる
- その時に`.github/workflows/ci.yml`を更新する必要がある
- でも忘れがち

**さらに重要な視点**:
- **サーバで動いているPythonバージョンがEOL/EOSになっていないか**
- CI/CDより、実際に動いているサーバの方が深刻
- EOL後はセキュリティパッチが出ない → 脆弱性が放置される
- でもサーバのPythonバージョンは意識しにくい

**危険度の比較**:
```
❌ 危険度: 高
サーバのPython 3.9がEOL → セキュリティパッチが出ない
→ 脆弱性が放置される
→ 実際に攻撃される可能性

⚠️ 危険度: 中
CI/CDのPython 3.10がEOL → テストが古いバージョンで動く
→ 新しいバージョンでの問題を見逃す可能性
→ でも本番環境は別
```

#### 改善案

**1. サーバ環境のPythonバージョンチェック（優先度: 高）**

```python
# scripts/check_server_python.py
import sys
import requests
from datetime import datetime, timedelta

def check_server_python_version():
    """サーバで動いているPythonバージョンをチェック"""
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # endoflife.date APIで確認
    response = requests.get('https://endoflife.date/api/python.json')
    versions = response.json()
    
    for v in versions:
        if v['cycle'] == current_version:
            eol_date = datetime.fromisoformat(v['eol'])
            today = datetime.now()
            
            if eol_date < today:
                print(f"❌ Python {current_version} はサポート終了しています")
                print(f"   EOL日: {v['eol']}")
                print(f"   セキュリティリスクがあります。アップグレードしてください。")
                return False
            
            elif eol_date < today + timedelta(days=180):
                print(f"⚠️  Python {current_version} は6ヶ月以内にEOLです")
                print(f"   EOL日: {v['eol']}")
                print(f"   アップグレードの計画を立ててください")
                return True
            
            else:
                print(f"✅ Python {current_version} はサポート中です")
                print(f"   EOL日: {v['eol']}")
                return True
    
    print(f"⚠️  Python {current_version} の情報が見つかりません")
    return True

if __name__ == '__main__':
    check_server_python_version()
```

**Komonに統合する場合**:

```bash
# 週次レポートに含める
komon weekly-report

📊 週次健全性レポート (2025-11-18 〜 2025-11-24)

【システム情報】
Python: 3.10.12 ⚠️ 2026年10月にEOL予定
  → アップグレードの計画を立ててください
OS: AlmaLinux 9.3 ✅ サポート中（2032年まで）

【リソース状況】
...
```

**または独立コマンド**:

```bash
# 環境チェック（月次実行を推奨）
komon check-environment

🔍 環境チェック

Python: 3.10.12 ⚠️ 2026年10月にEOL予定
  推奨バージョン: 3.11, 3.12
  アップグレード手順: https://docs.python.org/ja/3/using/unix.html

OS: AlmaLinux 9.3 ✅ サポート中（2032年まで）
```

**2. CI/CDのPythonバージョンチェック（優先度: 低）**

```python
# scripts/check_ci_python_versions.py
import requests
import yaml
from datetime import datetime, timedelta

def get_supported_python_versions():
    """endoflife.date APIからサポート中のPythonバージョンを取得"""
    response = requests.get('https://endoflife.date/api/python.json')
    versions = response.json()
    
    supported = []
    eol_soon = []
    
    for v in versions:
        eol_date = datetime.fromisoformat(v['eol'])
        today = datetime.now()
        
        if eol_date > today:
            supported.append(v['cycle'])
            
            # 6ヶ月以内にEOL
            if eol_date < today + timedelta(days=180):
                eol_soon.append({
                    'version': v['cycle'],
                    'eol_date': v['eol']
                })
    
    return supported, eol_soon

def get_ci_python_versions():
    """GitHub ActionsのPythonバージョンを取得"""
    with open('.github/workflows/ci.yml', 'r') as f:
        ci_config = yaml.safe_load(f)
    
    matrix = ci_config['jobs']['test']['strategy']['matrix']
    return matrix['python-version']

def main():
    supported, eol_soon = get_supported_python_versions()
    ci_versions = get_ci_python_versions()
    
    print("📋 CI/CD Pythonバージョンチェック")
    print(f"サポート中: {', '.join(supported)}")
    print(f"CI設定: {', '.join(ci_versions)}")
    
    # EOL間近の警告
    if eol_soon:
        print("\n⚠️  EOL間近のバージョン:")
        for v in eol_soon:
            print(f"  - Python {v['version']}: {v['eol_date']}にEOL")
    
    # CI設定の検証
    unsupported = [v for v in ci_versions if v not in supported]
    if unsupported:
        print(f"\n❌ サポート終了: {', '.join(unsupported)}")
        print("   .github/workflows/ci.yml を更新してください")
        exit(1)
    
    print("\n✅ 全てのバージョンがサポート中です")

if __name__ == '__main__':
    main()
```

**GitHub Actions統合**

```yaml
# .github/workflows/python-version-check.yml
name: Python Version Check

on:
  schedule:
    - cron: '0 0 1 * *'  # 毎月1日
  workflow_dispatch:  # 手動実行も可能

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install requests pyyaml
      
      - name: Check Python versions
        id: check
        run: |
          python scripts/check_python_versions.py
        continue-on-error: true
      
      - name: Create Issue if outdated
        if: steps.check.outcome == 'failure'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '⚠️ Pythonバージョンの更新が必要です',
              body: `CI設定のPythonバージョンにサポート終了のものが含まれています。\n\n` +
                    `.github/workflows/ci.yml を確認してください。\n\n` +
                    `詳細: https://github.com/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`,
              labels: ['maintenance', 'python-version']
            })
```

#### 実装メモ

**メリット**:
- ✅ **サーバ環境**: セキュリティリスクの早期発見（重要！）
- ✅ **CI/CD**: EOL/EOSの追跡を自動化
- ✅ 手動チェックの手間を削減
- ✅ 確実に検知できる
- ✅ 他プロジェクトにも応用可能（Node.js, Ruby等）
- ✅ 他の言語にも拡張可能（OS、ミドルウェア等）

**デメリット**:
- ❌ 実装コスト（サーバチェック: 1時間、CI/CDチェック: 2-3時間）
- ❌ メンテナンスコスト（API変更時）
- ❌ Pythonバージョンは年1回程度しか変わらない
- ❌ CI/CDチェックは手動管理でも十分（年1回、5分程度の作業）

#### 現実的な対応

**優先度1: サーバ環境チェック（推奨）**

```bash
# 月次で実行（cronまたはsystemd-timer）
0 9 1 * * python /path/to/scripts/check_server_python.py
```

または週次レポート（IDEA-014）に統合：
```python
# src/komon/weekly_data.py に追加
def get_python_version_status():
    """Pythonバージョンの状態を取得"""
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    # endoflife.date APIで確認...
    return {
        'version': current_version,
        'status': 'supported' | 'eol_soon' | 'eol',
        'eol_date': '2026-10-04'
    }
```

**優先度2: CI/CDチェック（手動管理でOK）**

1. カレンダーリマインダー設定
   ```
   2026年9月: Python 3.10 EOL確認
   → .github/workflows/ci.yml を更新
   ```

2. ドキュメント化
   ```markdown
   # docs/OPERATIONS.md
   
   ## Pythonバージョン管理
   
   ### サーバ環境
   - 確認頻度: 月1回（自動）
   - 確認方法: komon weekly-report または check-environment
   - 対応: OSのパッケージマネージャーでアップグレード
   
   ### CI/CD
   - 確認頻度: 年1回（9月）
   - 確認先: https://endoflife.date/python
   - 更新対象: .github/workflows/ci.yml
   ```

**将来（完全自動化）**:
- 複数プロジェクトで使う場合
- 他の言語（Node.js等）も管理したい場合
- チーム開発で忘れがちな作業を減らしたい場合
- GitHub Actions統合（Issue自動作成）

#### 検討事項

**実装する価値がある条件**:
- 複数プロジェクトを管理している
- 他の言語も同様に管理したい
- チーム開発で忘れがちな作業を減らしたい

**Komonの現状では**:
- 年1回、5分程度の手動作業で十分
- カレンダーリマインダーで対応可能
- 自動化は将来の検討課題

#### 期待効果（もし実装するなら）

- EOL/EOSの追跡を完全自動化
- 複数プロジェクトでの一貫した管理
- 「実際に走らせてみた」実証例として価値がある
- 他の言語（Node.js, Ruby等）にも応用可能

#### 実装ステップ（もし実装するなら）

**ステップ1**: future-ideas.mdに記録（✅ 完了）

**ステップ2**: 2026年9月にカレンダーリマインダー設定

**ステップ3**: 他プロジェクトでも同じ課題があれば実装検討

**ステップ4**: 実装する場合
1. `scripts/check_python_versions.py` を作成
2. GitHub Actionsで月次実行
3. Issue自動作成
4. 他の言語にも拡張（Node.js, Ruby等）

#### 開発者コメント

```
技術的には面白いアイデアだけど、
Komonの現状では手動管理で十分。

年1回、5分程度の作業を自動化するために
2-3時間かけて実装するのは、
費用対効果が合わない。

ただし、複数プロジェクトを管理するようになったり、
他の言語も同様に管理したくなったら、
その時に実装を検討する価値はある。

「今すぐやる必要はないけど、
 将来の選択肢として残しておく」
というのが、このアイデアの位置づけ。
```

---

---

---

### [IDEA-023] Webhook通知の統一化（マルチサービス対応）

**カテゴリ**: 機能強化・通知方式の標準化  
**提案日**: 2025-12-04  
**ステータス**: タスク化済み（TASK-019, 020, 021, 022）  
**優先度**: 中

#### 背景・課題

**ChatGPTとの対話から生まれた構想**:

現在のKomonは：
- Slack専用の通知実装（`send_slack_alert()`）
- Email専用の通知実装（`send_email_alert()`）
- サービスごとに個別実装が必要

**問題点**:
- Discord、Teams、その他のWebhookサービスを追加するたびに個別実装が必要
- サービス固有のリッチUI（BlockKit, Embed, AdaptiveCard等）を追うと複雑化
- Komonの「軽量・シンプル」思想と相反する

**Komonの強み**:
- 軽さ・シンプルさ・汎用性
- 「開発者向け軽量アドバイザー」の立ち位置

#### 改善案の全体像

**1. 設計思想（Design Philosophy）**

✔ **共通性を最優先**
- どの通知サービスにも依存しない「最小公約数のテキスト形式」に統一
- サービス固有のリッチUIは追わない

✔ **軽量・シンプルさを守る**
- Komonは「開発者向け軽量アドバイザー」
- 通知のリッチ化は追わない

✔ **fork / 外部拡張は歓迎、コアには入れない**
- Slack専用の豪華版、Discord専用のEmbed対応などは Komon-core には含めない
- 必要な人は、fork や外部の中継スクリプトで拡張してもらう

**2. 統一されたWebhook通知**

**設定ファイル**:
```yaml
notifiers:
  webhooks:
    - name: "slack"
      url: "env:KOMON_SLACK_WEBHOOK"
      kind: "slack"
      enabled: true
    
    - name: "discord"
      url: "env:KOMON_DISCORD_WEBHOOK"
      kind: "discord"
      enabled: true
    
    - name: "teams"
      url: "env:KOMON_TEAMS_WEBHOOK"
      kind: "teams"
      enabled: true
    
    - name: "generic"
      url: "env:KOMON_GENERIC_WEBHOOK"
      kind: "generic"
      enabled: true
```

**統一インターフェース**:
```python
def send_webhook_notification(notification, webhook_config):
    """統一されたWebhook通知"""
    kind = webhook_config.get('kind', 'generic')
    url = webhook_config['url']
    
    # kind に応じた最小限の整形
    payload = format_payload(notification, kind)
    
    # 共通のHTTP POST
    response = requests.post(url, json=payload, timeout=10)
    
    if 200 <= response.status_code < 300:
        logger.info("Webhook sent: kind=%s", kind)
    else:
        logger.warning("Webhook failed: kind=%s, status=%d", 
                      kind, response.status_code)
```

**3. メッセージフォーマット（統一されたテキスト形式）**

全サービスで成立する最小限のテキスト形式：

```
[Komon][CRITICAL] host=dev-server-01
CPU usage exceeds threshold (95%)

Advice:
- Check top processes
- Verify batch jobs
```

**特徴**:
- レベル（WARNING / ALERT / CRITICAL）
- ホスト名
- 短い説明
- シンプルなアドバイス（任意）
- 時刻（任意）

このフォーマットは Slack / Discord / Teams 全部で成立する。

**4. 成功/失敗判定の統一**

- 成功判定 = HTTP status 200〜299
- レスポンスボディは読まない（サービス差異を吸収しない）
- エラー時は Komon の内部ログへ warning を1行出すだけ

**5. やらないこと（非対応宣言）**

Komon-core では以下を実装しない：
- ❌ Slack BlockKit
- ❌ Discord Embed
- ❌ Teams Adaptive Card
- ❌ ボタン・スレッド返信・引用・画像添付などサービス固有拡張
- ❌ サービスごとの専用フォーマッター（基本としては入れない）

**理由**:
- Komonは「軽量アドバイザー」であり、「マルチチャネル通知の統合プロダクト」ではない
- サービス固有機能を追うと、Komonが「通知プロダクト」になってしまう
- 保守コストが増大し、Komonの軽量設計が崩れる

**6. 拡張のための逃げ道（やりたい人のための設計）**

Komon-core を軽く保ったまま、外部拡張は歓迎する：

**外部スクリプト連携**:
```
Komon-core → ローカル JSON 出力
外部プロセス → リッチ通知へ変換
```

**フォークしてサービス固有機能に対応**:
- `komon-slack-advanced` のような サードパーティ plugin 的拡張も自由
- Komon 本体には組み込まず、責務を明確に分離する

#### 実装アーキテクチャ

**新規モジュール**: `src/komon/webhook_notifier.py`

```python
class WebhookNotifier:
    """統一されたWebhook通知クラス"""
    
    SUPPORTED_KINDS = {
        'slack': SlackFormatter,
        'discord': DiscordFormatter,
        'teams': TeamsFormatter,
        'generic': GenericFormatter,  # デフォルト
    }
    
    def __init__(self, config):
        self.webhooks = config.get('notifiers', {}).get('webhooks', [])
    
    def send(self, notification):
        """全てのWebhookに通知を送信"""
        for webhook in self.webhooks:
            if not webhook.get('enabled', True):
                continue
            
            try:
                self._send_single(notification, webhook)
            except Exception as e:
                logger.error("Webhook failed: %s", e)
    
    def _send_single(self, notification, webhook):
        """単一のWebhookに送信"""
        kind = webhook.get('kind', 'generic')
        url = webhook['url']
        
        # 環境変数展開
        if url.startswith('env:'):
            url = os.getenv(url[4:])
        
        # フォーマット
        formatter = self.SUPPORTED_KINDS.get(kind, GenericFormatter)
        payload = formatter.format(notification)
        
        # 送信
        response = requests.post(url, json=payload, timeout=10)
        
        if 200 <= response.status_code < 300:
            logger.info("Webhook sent: kind=%s", kind)
        else:
            logger.warning("Webhook failed: kind=%s, status=%d", 
                          kind, response.status_code)
```

**フォーマッター**:
```python
class GenericFormatter:
    """汎用フォーマッター"""
    @staticmethod
    def format(notification):
        return {
            "text": f"[Komon][{notification['level']}] {notification['message']}"
        }

class SlackFormatter:
    """Slackフォーマッター（最小限）"""
    @staticmethod
    def format(notification):
        return {
            "text": f"[Komon][{notification['level']}] {notification['message']}"
        }

class DiscordFormatter:
    """Discordフォーマッター（最小限）"""
    @staticmethod
    def format(notification):
        return {
            "content": f"[Komon][{notification['level']}] {notification['message']}"
        }

class TeamsFormatter:
    """Teamsフォーマッター（最小限）"""
    @staticmethod
    def format(notification):
        return {
            "text": f"[Komon][{notification['level']}] {notification['message']}"
        }
```

#### 移行パス（後方互換性・安全性重視）

**Phase 1: 既存パターンでDiscord/Teamsを追加（v1.25.0）**

既存の `send_slack_alert()` と同じ形式で実装：

```python
# 新規追加（既存のSlack通知には一切触らない）
def send_discord_alert(message, webhook_url):
    """Discord通知（Slack形式を踏襲）"""
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload, timeout=10)
    # ...

def send_teams_alert(message, webhook_url):
    """Teams通知（Slack形式を踏襲）"""
    payload = {"text": message}
    response = requests.post(webhook_url, json=payload, timeout=10)
    # ...
```

設定ファイル：
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

**リスク**: ほぼゼロ（既存のSlack通知に影響なし）

---

**Phase 2: 統一Webhookを新規追加（v1.26.0）**

新方式を追加（旧方式も完全に動作）：

```yaml
# 旧方式（v1.X.X 〜 v1.25.0）- まだ動作する
notifications:
  slack:
    enabled: true
    webhook_url: "env:KOMON_SLACK_WEBHOOK"
  discord:
    enabled: false
    webhook_url: "env:KOMON_DISCORD_WEBHOOK"

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
```

**動作**:
- 新方式が設定されていれば、新方式を使用
- 新方式が未設定なら、旧方式を使用（フォールバック）
- 両方設定されている場合は、新方式を優先

**リスク**: 低（旧方式がフォールバック）

---

**Phase 3: 旧方式に非推奨警告（v1.27.0）**

旧形式の設定に警告を表示：

```
⚠️ 警告: 旧形式の通知設定は非推奨です
   新形式への移行をお願いします
   詳細: docs/MIGRATION.md
   
   旧形式は v2.0.0 で削除されます
```

**動作**: まだ動作する（警告のみ）

---

**Phase 4: 旧方式を削除（v2.0.0）**

個別実装を削除：
- `send_slack_alert()` を削除
- `send_discord_alert()` を削除
- `send_teams_alert()` を削除
- 旧形式の設定は動作しない
- 移行ガイド（`docs/MIGRATION.md`）を必ず用意

**動作**: 新方式のみ

#### 期待効果

**1. 拡張性の向上**
- Discord、Teams、その他のWebhookサービスを簡単に追加できる
- 新しいサービスは `kind` を追加するだけ

**2. 保守性の向上**
- 通知ロジックが統一される
- サービス固有の複雑さを排除

**3. Komonらしさの維持**
- 軽量・シンプルな設計を維持
- 「通知プロダクト」にならない明確な線引き

**4. 拡張の自由度**
- リッチ通知が欲しい人は外部で拡張できる
- Komon-core は軽く保てる

**5. 安全性の確保**
- 段階的な実装で既存機能への影響を最小化
- 各Phaseで検証してから次に進む
- 問題があれば即座にロールバック可能
- ユーザーに十分な移行期間を提供

#### 実装優先度

**今すぐやる必要はない**:
- 現在の Slack 通知で十分動作している
- 他のサービスへの要望が出てから実装

**でも設計は今詰めておく価値がある**:
- 将来の拡張性を確保
- 「どう実装するか」の方針が明確になる

#### 実装ステップ（もし実装するなら）

**ステップ1**: future-ideas.mdに記録（✅ 完了）

**ステップ2**: Phase 1の実装（v1.25.0）
- Specを作成（requirements.yml, design.yml, tasks.yml）
- `send_discord_alert()` を実装（Slack形式を踏襲）
- `send_teams_alert()` を実装（Slack形式を踏襲）
- 設定ファイルに `discord`, `teams` セクションを追加
- テストを追加（モック使用）
- **既存のSlack通知には一切触らない**

**ステップ3**: Phase 1の検証
- Discord/Teamsが実際に動作するか確認
- 既存のSlack通知に影響がないか確認
- 問題があれば修正

**ステップ4**: Phase 2の実装（v1.26.0）
- `WebhookNotifier` クラスを実装
- `kind` ごとのフォーマッターを実装
- 新形式の設定を追加
- 旧形式との共存ロジックを実装（フォールバック）
- テストを追加（モック使用）

**ステップ5**: Phase 2の検証
- 統一Webhookが実際に動作するか確認
- 旧形式のフォールバックが動作するか確認
- 実戦で使ってみて、問題がないか検証

**ステップ6**: Phase 3の実装（v1.27.0）
- 旧形式に非推奨警告を追加
- 移行ガイド（`docs/MIGRATION.md`）を作成
- ドキュメント更新

**ステップ7**: 移行期間（v1.27.0 〜 v1.99.0）
- 既存ユーザーに移行を促す
- 旧形式も動作する（互換性維持）
- 十分な移行期間を確保

**ステップ8**: Phase 4の実装（v2.0.0）
- 旧形式のサポート終了
- `send_slack_alert()`, `send_discord_alert()`, `send_teams_alert()` を削除
- 統一Webhookのみに

#### 開発者コメント

```
ChatGPTとの対話で生まれた構想。

「Slack / Discord / Teams を統一的に扱いたい」
「でもKomonの軽量さは守りたい」

この2つを両立する設計。

完璧を目指すより「小さく動くもの」から。
まずは基本機能を実装して、
実際に使ってみて、
体験から出た穴や改修項目を洗い出す。

リッチ通知は Komon-core の範囲外。
必要な人は外部で拡張してもらう。

この線引きが、Komonの「軽量・シンプル」を守る鍵。
```

#### 関連する既存機能

このアイデアは、以下の既存機能と連携します：
- Slack通知（`notification.py`）
- Email通知（`notification.py`）
- 通知履歴（`notification_history.py`）

新規に必要な機能：
- 統一Webhook通知（`webhook_notifier.py`）
- フォーマッター（`formatters.py`）
- 設定検証（`settings_validator.py`）

---

---

### [IDEA-024] ネットワーク疎通チェック機能（ping/http）

**カテゴリ**: 機能追加  
**提案日**: 2025-12-08  
**ステータス**: ✅ 実装済み (v1.25.0)  
**優先度**: 中

#### 背景・課題

**ユーザーからの要望**:
- REST API実行前の事前条件確認
- 外部通信不可時の早期気づき
- ネットワーク疎通の軽量チェック

**Komonの立ち位置**:
- 監視ツール化は目指さない
- あくまで「アドバイザ（診断補助）」の範囲
- 軽量性を最優先

#### 改善案の全体像

**1. 基本方針（重要）**

✔ **デフォルト動作は従来通り**
- `komon` 単体実行ではネットワークチェックしない
- ネットワークチェックはすべて opt-in（引数 or 設定で有効化）

✔ **軽量性を最優先**
- ping/http は最小限の処理のみ
- 外部に迷惑をかけない（デフォのhttp宛先は実在しない例示URL）

✔ **アラートは状態変化時だけ**
- 正常→異常、異常→正常のみ通知
- 状態管理は NGのみ保持 + retention（寿命）付き

✔ **既存の 5分 cron はそのまま維持**
- 互換性100%

**2. 実装ロードマップ（順序）**

**① ネットワークチェックのモジュール化**
```
komon/net/ping_check.py
komon/net/http_check.py
```
- ping と http を、それぞれ独立の関数として構築

**② komon advise にフックを追加**
- 既存の advise（システム・ログ診断）に以下を追加：
  - `--with-net`: 全部（リソース・ログ + ping + http）
  - `--net-only`: ping + http
  - `--ping-only`: pingのみ
  - `--http-only`: httpのみ

**③ CLI 引数の拡張（opt-inのみ）**
```bash
komon                # 従来どおり（ネットワークチェックなし）
komon --with-net     # 全部（リソース・ログ + ping + http）
komon --net-only     # ping + http
komon --ping-only    # pingのみ
komon --http-only    # httpのみ
```

**④ 状態ファイル（NGのみ保持）の実装**
```json
{
  "net.http:https://example.com": {
    "first_detected_at": "2025-12-08T12:00:00Z"
  }
}
```
- retention 超過した古いNGは自動削除

**⑤ 通知ポリシー（状態変化時のみ）**
- OK → NG：通知
- NG → OK：復旧通知
- NG → NG：通知なし（ログのみ）
- OK → OK：通知なし

**⑥ デフォルト例（ユーザー任意設定）**
- pingデフォルト例：127.0.0.1（外部に迷惑かけない）
- httpデフォルト例：https://komon-example.com（実在しないため、必ずエラーになり"例として差し替える"ことが明確）

**3. cron の取り扱い（複雑化を避ける思想）**

**基本（推奨・デフォルト）**:
```bash
*/5 * * * * /usr/local/bin/komon  # 従来どおり
```

**便利に使いたい人**:
```bash
*/5 * * * * /usr/local/bin/komon --with-net
```

**こだわり運用（上級者向け）**:
```bash
*/5  * * * * komon                 # リソース＆ログ
*/15 * * * * komon --net-only      # ネットワークだけ
```

**4. 設定ファイル例**

```yaml
network_check:
  enabled: false  # デフォルトは無効
  
  ping:
    targets:
      - host: "127.0.0.1"
        description: "ローカルホスト（例）"
    timeout: 3
    
  http:
    targets:
      - url: "https://komon-example.com"
        description: "例示URL（実在しない）"
        method: "GET"
    timeout: 10
    
  state:
    retention_hours: 24  # 24時間でNG状態を削除
    file_path: "/var/lib/komon/state.json"
```

#### 実装イメージ

**ping実装**:
```python
# komon/net/ping_check.py
import subprocess

def check_ping(host, timeout=3):
    """ping疎通チェック"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', str(timeout), host],
            capture_output=True,
            timeout=timeout + 1
        )
        return result.returncode == 0
    except Exception as e:
        logger.error("Ping failed: %s", e)
        return False
```

**http実装**:
```python
# komon/net/http_check.py
import requests

def check_http(url, timeout=10, method='GET'):
    """HTTP疎通チェック"""
    try:
        response = requests.request(
            method,
            url,
            timeout=timeout
        )
        return 200 <= response.status_code < 400
    except Exception as e:
        logger.error("HTTP check failed: %s", e)
        return False
```

**状態管理**:
```python
# komon/net/state_manager.py
import json
from datetime import datetime, timedelta

class NetworkStateManager:
    """ネットワークチェックの状態管理（NGのみ保持）"""
    
    def __init__(self, state_file, retention_hours=24):
        self.state_file = state_file
        self.retention_hours = retention_hours
        self.state = self._load()
    
    def _load(self):
        """状態ファイルを読み込み"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save(self):
        """状態ファイルに保存"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_and_update(self, check_id, is_ok):
        """状態をチェックして更新"""
        now = datetime.now().isoformat()
        
        # 古いNG状態を削除（retention）
        self._cleanup_old_states()
        
        # 状態変化の判定
        was_ng = check_id in self.state
        is_ng = not is_ok
        
        if is_ng and not was_ng:
            # OK → NG: 通知
            self.state[check_id] = {"first_detected_at": now}
            self._save()
            return "alert"
        
        elif not is_ng and was_ng:
            # NG → OK: 復旧通知
            del self.state[check_id]
            self._save()
            return "recovery"
        
        elif is_ng and was_ng:
            # NG → NG: 通知なし
            return "ongoing"
        
        else:
            # OK → OK: 通知なし
            return "ok"
    
    def _cleanup_old_states(self):
        """古いNG状態を削除"""
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        
        to_delete = []
        for check_id, info in self.state.items():
            detected_at = datetime.fromisoformat(info["first_detected_at"])
            if detected_at < cutoff:
                to_delete.append(check_id)
        
        for check_id in to_delete:
            del self.state[check_id]
        
        if to_delete:
            self._save()
```

#### 期待効果

**1. 実務的な価値**
- REST API実行前の事前条件確認
- 外部通信不可時の早期気づき
- ネットワーク疎通という実務で大事な要素を適切に補強

**2. Komonらしさの維持**
- 軽量・シンプル・非侵襲の哲学を完全維持
- 従来の動きを壊さない後方互換
- 監視ツール化しないように「状態変化通知のみ」の運用

**3. OSSとしての配慮**
- 外部への負荷ゼロ
- デフォルトのhttp宛先は実在しないURL
- ユーザーに設定を促す設計

**4. 長期運用の安全性**
- 状態ファイルのゴミが残らないクリーン設計
- retention付きで自動クリーンアップ

#### 実装優先度

**今すぐやる必要はない**:
- 現在のKomonで十分動作している
- 他の優先度の高いタスクを先に

**でも設計は今詰めておく価値がある**:
- 実務的な価値が高い
- Komonの哲学を完全に維持した設計
- 将来の実装がスムーズになる

#### 実装ステップ（もし実装するなら）

**ステップ1**: future-ideas.mdに記録（✅ 完了）

**ステップ2**: Spec作成
- requirements.yml: 要件定義
- design.yml: 設計書
- tasks.yml: 実装タスクリスト

**ステップ3**: 実装（ロードマップ順）
1. ネットワークチェックのモジュール化
2. komon advise にフックを追加
3. CLI 引数の拡張
4. 状態ファイルの実装
5. 通知ポリシーの実装
6. デフォルト例の設定

**ステップ4**: テスト
- プロパティベーステスト
- 統合テスト
- ユニットテスト

**ステップ5**: ドキュメント
- README.md更新
- CHANGELOG.md記録
- 設定例の追加

#### 開発者コメント

```
ユーザーからの要望で生まれたアイデア。

「ネットワーク疎通チェックが欲しい」
「でもKomonの軽量さは守りたい」

この2つを両立する設計。

デフォルト動作は一切変わらない。
opt-in設計で既存ユーザーへの影響ゼロ。
状態変化時のみ通知で、監視ツール化を避ける。

Komonの哲学を完全に維持した上で、
実務的な価値を追加する。

この設計なら、Komonらしさを損なわずに
実装できると思う。
```

---

## 更新履歴

- 2025-12-10: IDEA-021を削除（v1.23.0で実装済み、implemented-ideas.mdに移動完了）
- 2025-12-10: IDEA-021を実装済みに更新（v1.23.0で完了済み）
- 2025-12-08: REJECTED-001〜003を`rejected-ideas.md`に移動
- 2025-12-08: ネットワーク疎通チェック機能のアイデアを追加（IDEA-024）
- 2025-12-08: IDEA-023をタスク化（TASK-019, 020, 021, 022）、バージョン番号を修正
- 2025-12-04: Webhook通知の統一化のアイデアを追加（IDEA-023）
- 2025-12-03: OS判定・汎用Linux対応のアイデアを追加（IDEA-022）
- 2025-12-02: `komon advise` 出力フォーマットの改善アイデアを追加（IDEA-021）
- 2025-11-27: Pythonバージョン自動チェック機能のアイデアを追加（IDEA-020）
- 2025-11-26: State Snapshot & Diff Detection のアイデアを追加（IDEA-019）
- 2025-11-24: IDEA-008, IDEA-014, IDEA-015, IDEA-016を実装済みに更新（v1.11.0, v1.12.0, v1.13.0, v1.15.0）
- 2025-11-23: 特別研究プロジェクトセクションを追加、自己修復システム（RESEARCH-001）を詳細に記録
- 2025-11-23: 多言語化対応のアイデアを追加（IDEA-018）
- 2025-11-22: 年末年始の健全確認対応として4件のアイデアを追加（IDEA-014〜017）
- 2025-11-22: GitHubのIssueから8件のアイデアを統合（IDEA-008〜013, REJECTED-002〜003）
- 2025-11-22: IDEA-001を部分実装済みに更新（v1.10.1）
- 2025-11-21: 初版作成（IDEA-001〜007を追加）

