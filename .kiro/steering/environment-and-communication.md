---
title: 環境とコミュニケーションルール
inclusion: always
---

# Komon開発環境とコミュニケーションルール

## 開発環境

### ターゲットプラットフォーム
**AlmaLinux 9**（RHEL系Linux）

Komonは**Linux環境専用**として開発されています。

### 動作確認コマンド

Kiroが提示するコマンドは、**必ずAlmaLinuxで実行可能**なものにしてください。

#### ✅ 使用可能なコマンド

```bash
# ファイル操作
ls, cat, grep, find, wc, head, tail

# Git操作
git status, git branch, git checkout, git merge, git tag

# Python実行
python, python -m pytest, pip

# プロセス確認
ps aux, top, htop

# システム情報
df -h, free -m, uptime

# テキスト処理
sed, awk, cut, sort, uniq
```

#### ❌ 使用禁止コマンド

```bash
# Windowsコマンド
findstr, dir, type, del

# macOS専用
pbcopy, pbpaste, open

# 他のLinuxディストリビューション専用
apt, apt-get (Debian/Ubuntu)
pacman (Arch Linux)
```

#### パッケージ管理

AlmaLinuxでは**dnf**または**yum**を使用：

```bash
# パッケージインストール
sudo dnf install <package>
sudo yum install <package>

# パッケージ検索
dnf search <package>
```

### シェル環境

- デフォルトシェル: **bash**
- コマンド区切り: `&&` または `;`
- パイプ: `|`

## コミュニケーションルール

### 言語

**Kiroとユーザーのやり取りは必ず日本語で行う**

#### ✅ 正しい例

```
Kiro: 「通知履歴機能の実装が完了しました。テストは111件全てパスしています。
       v1.11.0としてリリースすることを提案します。」

ユーザー: 「ありがとう！v1.11.0でリリースします」
```

#### ❌ 間違った例

```
Kiro: "The notification history feature has been implemented. 
       All 111 tests passed. I suggest releasing as v1.11.0."

ユーザー: 「ありがとう！v1.11.0でリリースします」
```

### 日本語使用の範囲

#### 日本語で記述するもの

- **ユーザーとの会話**: 必ず日本語
- **コミットメッセージ**: 日本語推奨
- **ドキュメント**: 日本語（README.md, CHANGELOG.md等）
- **コメント**: 日本語推奨

#### 英語で記述するもの

- **コード**: 変数名、関数名、クラス名は英語
- **テストケース名**: 英語でもOK（ただし日本語でも可）
- **Spec文書**: 英語（requirements.md, design.md, tasks.md）
  - ただし、ユーザーへの説明は日本語で行う

### Specモードでの注意

Specモード（仕様駆動開発）では、以下のように使い分けます：

```
1. Spec文書作成（英語）
   - requirements.md: EARS形式の要件定義（英語）
   - design.md: 設計書（英語）
   - tasks.md: タスクリスト（英語）

2. ユーザーへの報告（日本語）
   Kiro: 「requirements.mdを作成しました。
          6つの要件を定義しています。確認をお願いします。」

3. 実装中の説明（日本語）
   Kiro: 「notification_history.pyを実装中です。
          save_notification関数を追加しました。」

4. 完了報告（日本語）
   Kiro: 「実装が完了しました。テストは全てパスしています。」
```

### コマンド提示時のフォーマット

動作確認コマンドを提示する際は、以下の形式で：

```markdown
## 動作確認

以下のコマンドで動作を確認できます：

\`\`\`bash
# テスト実行
python -m pytest tests/ -v

# カバレッジ確認
bash run_coverage.sh

# 通知履歴の表示
python scripts/advise.py --history 10
\`\`\`
```

### エラーメッセージの説明

エラーが発生した場合は、日本語で説明：

```
❌ エラーが発生しました

エラー内容:
  ModuleNotFoundError: No module named 'hypothesis'

原因:
  hypothesisパッケージがインストールされていません。

解決方法:
  以下のコマンドでインストールしてください：
  
  pip install -r requirements-dev.txt
```

## Kiroへの指示

### 必ず守ること

1. **ユーザーとの会話は100%日本語**
   - Specモードでも、ユーザーへの報告は日本語
   - 英語で返答してしまった場合は、即座に日本語で言い直す

2. **コマンドはAlmaLinux対応**
   - `findstr`などWindowsコマンドは使わない
   - `grep`, `awk`, `sed`などLinux標準コマンドを使う

3. **環境を意識した提案**
   - パッケージインストールは`dnf`または`yum`
   - シェルスクリプトは`bash`で記述

### チェックリスト

コマンドを提示する前に確認：

- [ ] AlmaLinuxで実行可能か？
- [ ] Windowsコマンドを使っていないか？
- [ ] ユーザーへの説明は日本語か？
- [ ] エラーメッセージの説明は日本語か？

## まとめ

- **開発環境**: AlmaLinux 9（RHEL系）
- **コマンド**: Linux標準コマンドのみ使用
- **パッケージ管理**: dnf/yum
- **コミュニケーション**: 必ず日本語
- **Spec文書**: 英語でOK（ただし説明は日本語）

このルールにより、ユーザーとKiroのコミュニケーションが円滑になり、
環境に適したコマンドが提示されます。
