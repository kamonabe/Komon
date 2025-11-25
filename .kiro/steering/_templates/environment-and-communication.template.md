# {{project.name}}開発環境とコミュニケーションルール

## 開発環境

### ターゲットプラットフォーム
**{{environment.platform}}**{% if environment.platform_type %}（{{environment.platform_type}}系Linux）{% endif %}

{% if project.type == "cli-tool" %}
{{project.name}}は**Linux環境専用**として開発されています。
{% endif %}

### 動作確認コマンド

Kiroが提示するコマンドは、**必ず{{environment.platform}}で実行可能**なものにしてください。

#### ✅ 使用可能なコマンド

```bash
# ファイル操作
ls, cat, grep, find, wc, head, tail

# Git操作
git status, git branch, git checkout, git merge, git tag

{% if project.language == "python" %}
# Python実行
python, python -m {{testing.framework}}, pip
{% endif %}

{% if project.language == "node" %}
# Node.js実行
node, npm, yarn
{% endif %}

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

{% if environment.package_manager == "dnf/yum" %}
# 他のLinuxディストリビューション専用
apt, apt-get (Debian/Ubuntu)
pacman (Arch Linux)
{% endif %}

{% if environment.package_manager == "apt" %}
# 他のLinuxディストリビューション専用
dnf, yum (RHEL/AlmaLinux)
pacman (Arch Linux)
{% endif %}
```

#### パッケージ管理

{% if environment.package_manager == "dnf/yum" %}
{{environment.platform}}では**dnf**または**yum**を使用：

```bash
# パッケージインストール
sudo dnf install <package>
sudo yum install <package>

# パッケージ検索
dnf search <package>
```
{% endif %}

{% if environment.package_manager == "apt" %}
{{environment.platform}}では**apt**を使用：

```bash
# パッケージインストール
sudo apt install <package>

# パッケージ検索
apt search <package>
```
{% endif %}

{% if environment.package_manager == "brew" %}
{{environment.platform}}では**Homebrew**を使用：

```bash
# パッケージインストール
brew install <package>

# パッケージ検索
brew search <package>
```
{% endif %}

### シェル環境

- デフォルトシェル: **{{environment.shell}}**
- コマンド区切り: `&&` または `;`
- パイプ: `|`

## コミュニケーションルール

### 言語

**Kiroとユーザーのやり取りは必ず{{communication.language_name}}で行う**

{% if communication.language == "ja" %}
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
{% endif %}

{% if communication.language == "en" %}
#### ✅ Correct Example

```
Kiro: "The notification history feature has been implemented. 
       All 111 tests passed. I suggest releasing as v1.11.0."

User: "Thanks! Let's release as v1.11.0"
```

#### ❌ Wrong Example

```
Kiro: 「通知履歴機能の実装が完了しました。」

User: "Thanks! Let's release as v1.11.0"
```
{% endif %}

### {{communication.language_name}}使用の範囲

#### {{communication.language_name}}で記述するもの

- **ユーザーとの会話**: 必ず{{communication.language_name}}
- **コミットメッセージ**: {{communication.language_name}}推奨
- **ドキュメント**: {{communication.language_name}}（README.md, CHANGELOG.md等）
- **コメント**: {{communication.language_name}}推奨
- **Spec文書**: {{communication.language_name}}（requirements.md, design.md, tasks.md）
  - 利用者は{{communication.language_name}}話者なので、全て{{communication.language_name}}で統一

#### 英語で記述するもの

- **コード**: 変数名、関数名、クラス名は英語
- **テストケース名**: 英語でもOK（ただし{{communication.language_name}}でも可）

### Specモードでの注意

Specモード（仕様駆動開発）では、**全て{{communication.language_name}}**で記述します：

{% if communication.language == "ja" %}
```
1. Spec文書作成（日本語）
   - requirements.md: 要件定義（日本語）
   - design.md: 設計書（日本語）
   - tasks.md: タスクリスト（日本語）

2. ユーザーへの報告（日本語）
   Kiro: 「requirements.mdを作成しました。
          6つの要件を定義しています。確認をお願いします。」

3. 実装中の説明（日本語）
   Kiro: 「notification_history.pyを実装中です。
          save_notification関数を追加しました。」

4. 完了報告（日本語）
   Kiro: 「実装が完了しました。テストは全てパスしています。」
```

**重要**: Spec文書は利用者（日本語話者）が読むものなので、英語で書かないこと。
{% endif %}

{% if communication.language == "en" %}
```
1. Spec Document Creation (English)
   - requirements.md: Requirements definition (English)
   - design.md: Design document (English)
   - tasks.md: Task list (English)

2. User Reporting (English)
   Kiro: "Created requirements.md.
          Defined 6 requirements. Please review."

3. Implementation Explanation (English)
   Kiro: "Implementing notification_history.py.
          Added save_notification function."

4. Completion Report (English)
   Kiro: "Implementation completed. All tests passed."
```

**Important**: Spec documents are for users, so write in English.
{% endif %}

### コマンド提示時のフォーマット

動作確認コマンドを提示する際は、以下の形式で：

{% if communication.language == "ja" %}
```markdown
## 動作確認

以下のコマンドで動作を確認できます：

\`\`\`bash
{% if project.language == "python" %}
# テスト実行
python -m {{testing.framework}} tests/ -v

# カバレッジ確認
bash run_coverage.sh
{% endif %}

{% if project.language == "node" %}
# テスト実行
npm test

# カバレッジ確認
npm run coverage
{% endif %}
\`\`\`
```
{% endif %}

{% if communication.language == "en" %}
```markdown
## Verification

You can verify the functionality with the following commands:

\`\`\`bash
{% if project.language == "python" %}
# Run tests
python -m {{testing.framework}} tests/ -v

# Check coverage
bash run_coverage.sh
{% endif %}

{% if project.language == "node" %}
# Run tests
npm test

# Check coverage
npm run coverage
{% endif %}
\`\`\`
```
{% endif %}

### エラーメッセージの説明

{% if communication.language == "ja" %}
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
{% endif %}

{% if communication.language == "en" %}
When an error occurs, explain in English:

```
❌ Error occurred

Error:
  ModuleNotFoundError: No module named 'hypothesis'

Cause:
  The hypothesis package is not installed.

Solution:
  Install it with the following command:
  
  pip install -r requirements-dev.txt
```
{% endif %}

## Kiroへの指示

### 必ず守ること

1. **ユーザーとの会話は100%{{communication.language_name}}**
   - Specモードでも、ユーザーへの報告は{{communication.language_name}}
{% if communication.language == "ja" %}
   - 英語で返答してしまった場合は、即座に日本語で言い直す
{% endif %}

2. **コマンドは{{environment.platform}}対応**
{% if environment.platform_type == "RHEL" %}
   - `findstr`などWindowsコマンドは使わない
   - `grep`, `awk`, `sed`などLinux標準コマンドを使う
{% endif %}

3. **環境を意識した提案**
{% if environment.package_manager == "dnf/yum" %}
   - パッケージインストールは`dnf`または`yum`
{% endif %}
{% if environment.package_manager == "apt" %}
   - パッケージインストールは`apt`
{% endif %}
   - シェルスクリプトは`{{environment.shell}}`で記述

### チェックリスト

コマンドを提示する前に確認：

- [ ] {{environment.platform}}で実行可能か？
- [ ] Windowsコマンドを使っていないか？
- [ ] ユーザーへの説明は{{communication.language_name}}か？
- [ ] エラーメッセージの説明は{{communication.language_name}}か？

## まとめ

- **開発環境**: {{environment.platform}}{% if environment.platform_type %}（{{environment.platform_type}}系）{% endif %}
- **コマンド**: Linux標準コマンドのみ使用
- **パッケージ管理**: {{environment.package_manager}}
- **コミュニケーション**: 必ず{{communication.language_name}}
- **Spec文書**: {{communication.language_name}}で統一

このルールにより、ユーザーとKiroのコミュニケーションが円滑になり、
環境に適したコマンドが提示されます。
