# {{project.name}}コミットメッセージルール

## 基本フォーマット

Conventional Commits形式を採用します：

```
<type>: <subject>

[optional body]

[optional footer]
```

### Type（必須）

| Type | 用途 | 例 |
|------|------|-----|
| `feat` | 新機能追加 | `feat: 通知履歴機能を追加` |
| `fix` | バグ修正 | `fix: ログ傾向分析のデータ型エラーを修正` |
| `docs` | ドキュメント変更のみ | `docs: READMEにアウトプットサンプルを追加` |
| `test` | テスト追加・修正 | `test: テストカバレッジを{{testing.coverage_target}}%に向上` |
| `refactor` | リファクタリング | `refactor: analyzer.pyの構造を整理` |
| `perf` | パフォーマンス改善 | `perf: ログ解析処理を最適化` |
| `chore` | ビルド・設定変更 | `chore: version.txtを1.13.0に更新` |
| `ci` | CI/CD関連 | {% if project.language == "python" %}`ci: Pythonバージョンを3.10/3.11/3.12に更新`{% endif %}{% if project.language == "node" %}`ci: Node.jsバージョンを18/20/22に更新`{% endif %} |
| `style` | コードスタイル修正 | {% if project.language == "python" %}`style: PEP8準拠に修正`{% endif %}{% if project.language == "node" %}`style: ESLint準拠に修正`{% endif %} |
| `revert` | コミット取り消し | `revert: "feat: 通知履歴機能を追加"` |

### Subject（必須）

- **{{communication.language_name}}で記述**
- **小文字で始める**（typeの後）
- **50文字以内を推奨**
- **命令形で書く**（「追加する」ではなく「追加」）
- **末尾にピリオドを付けない**

### Body（任意）

- 変更の理由や詳細を記述
- 72文字で改行
- {{communication.language_name}}でOK

### Footer（任意）

- Breaking Changes: `BREAKING CHANGE: 設定ファイル形式を変更`
- Issue参照: `Closes #123`
- バージョン情報: `(v1.16.0)`

## 実例

### ✅ 良い例

{% if communication.language == "ja" %}
```
feat: ディスク使用量の増加トレンド予測機能を実装

線形回帰を使用して、過去7日間のデータから
将来のディスク使用量を予測する機能を追加。

(v1.16.0)
```

```
fix: 通知履歴表示のフォーマットエラーを修正

日時フォーマットが不正な場合にクラッシュする
問題を修正。

Closes #45
```

```
docs: Python要件を{{environment.python_version}}以上に更新
```

```
ci: カバレッジチェックを警告のみに変更
```
{% endif %}

{% if communication.language == "en" %}
```
feat: implement disk usage trend prediction

Added feature to predict future disk usage
using linear regression on 7 days of data.

(v1.16.0)
```

```
fix: notification history format error

Fixed crash when date format is invalid.

Closes #45
```

```
docs: update Python requirement to {{environment.python_version}}+
```

```
ci: change coverage check to warning only
```
{% endif %}

### ❌ 悪い例

```
Fix: 通知履歴表示の改善  # typeが大文字
```

```
CI修正: カバレッジチェックを警告のみに変更  # 日本語type
```

```
通知履歴機能を追加  # typeがない
```

{% if communication.language == "ja" %}
```
feat: Added notification history feature.  # 英語、過去形、ピリオド
```
{% endif %}

{% if communication.language == "en" %}
```
feat: 通知履歴機能を追加  # 日本語subject
```
{% endif %}

## バージョンタグ付きコミット

リリース時のマージコミットには、バージョン情報を含めます：

{% if communication.language == "ja" %}
```
feat: ディスク使用量の増加トレンド予測機能を実装 (v1.16.0)
```

または

```
chore: v1.16.0リリース - ディスク使用量予測機能
```
{% endif %}

{% if communication.language == "en" %}
```
feat: implement disk usage trend prediction (v1.16.0)
```

or

```
chore: release v1.16.0 - disk usage prediction
```
{% endif %}

## ブレーキングチェンジ

後方互換性のない変更の場合：

{% if communication.language == "ja" %}
```
feat!: 設定ファイル形式をYAMLからTOMLに変更

BREAKING CHANGE: settings.ymlはsettings.tomlに変更されました。
既存の設定ファイルは手動で移行する必要があります。

(v2.0.0)
```
{% endif %}

{% if communication.language == "en" %}
```
feat!: change config format from YAML to TOML

BREAKING CHANGE: settings.yml is now settings.toml.
Existing config files must be migrated manually.

(v2.0.0)
```
{% endif %}

## Kiroへの指示

### コミットメッセージ提案時

1. **必ずConventional Commits形式を使用**
2. **typeは小文字の英語**
3. **subjectは{{communication.language_name}}**
4. **リリース時はバージョン情報を含める**

### チェックリスト

コミットメッセージを提案する前に確認：
- [ ] typeは定義された10種類のいずれかか？
- [ ] typeは小文字か？
- [ ] subjectは{{communication.language_name}}か？
- [ ] subjectは50文字以内か？
- [ ] subjectは命令形か？
- [ ] 末尾にピリオドがないか？

## 既存コミットの扱い

過去のコミットは修正しません。このルールは**今後のコミット**に適用します。

## まとめ

- **フォーマット**: `<type>: <subject>`
- **type**: 小文字英語（feat, fix, docs等）
- **subject**: {{communication.language_name}}、50文字以内、命令形
- **リリース時**: バージョン情報を含める

このルールにより、コミット履歴が統一され、CHANGELOGの自動生成も容易になります。
