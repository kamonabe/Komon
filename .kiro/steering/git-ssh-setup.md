# Git & SSH 設定ガイド

> **注意**: このファイルの実際の値は `project-config.yml` の `git.user` セクションで管理します。
> 以下のプレースホルダーを自分の情報に読み替えてください。
>
> | プレースホルダー | 参照先 |
> |---|---|
> | `<GIT_USER_NAME>` | `git.user.name` |
> | `<GIT_USER_EMAIL>` | `git.user.email` |
> | `<GITHUB_ACCOUNT>` | `git.user.github_account` |

## 🎯 目的
全プロジェクト共通のGit設定とSSH認証設定を管理し、
正しいアカウントでのコミット・プッシュを実現する。

## ⚙️ 初期設定（一度だけ実行）

### 1. Git設定
```bash
git config --global user.name "<GIT_USER_NAME>"
git config --global user.email "<GIT_USER_EMAIL>"
```

### 2. SSH鍵生成
```bash
ssh-keygen -t ed25519 -C "<GIT_USER_EMAIL>"
# パスフレーズを設定（セキュリティのため）
```

### 3. GitHubにSSH公開鍵を登録
```bash
cat ~/.ssh/id_ed25519.pub
# 出力された公開鍵をGitHub Settings > SSH and GPG keys に登録
```

### 4. ssh-agent自動起動設定
```bash
cat >> ~/.bashrc << 'EOF'
# SSH Agent auto-start
if [ -z "$SSH_AUTH_SOCK" ]; then
    eval "$(ssh-agent -s)" > /dev/null 2>&1
    ssh-add ~/.ssh/id_ed25519 2>/dev/null
fi
EOF
```

### 5. 便利エイリアス追加
```bash
echo "alias git-ready='ssh-add ~/.ssh/id_ed25519 && echo \"Git準備完了！\"'" >> ~/.bashrc
source ~/.bashrc
```

## 🔄 日常運用

### サーバー再起動後（1回のみ）
```bash
git-ready
# または
ssh -T git@github.com
```

### 新プロジェクトでのSSH設定
```bash
git remote set-url origin git@github.com:<GITHUB_ACCOUNT>/PROJECT_NAME.git
```

## ✅ 設定確認方法

### Git設定確認
```bash
git config --global --list | grep -E "(user\.name|user\.email)"
# 出力: user.name=<GIT_USER_NAME>, user.email=<GIT_USER_EMAIL>
```

### SSH接続確認
```bash
ssh -T git@github.com
# 出力: Hi <GITHUB_ACCOUNT>! You've successfully authenticated...
```

### コミット作者確認
```bash
git log --format="%h %an <%ae> %s" -1
# 出力: [hash] <GIT_USER_NAME> <<GIT_USER_EMAIL>> [message]
```

## 🚨 トラブルシューティング

### 意図しないユーザー名でコミットされる場合
- Git設定を再確認
- プロジェクトのローカル設定を確認: `git config --local --list`

### パスフレーズを毎回求められる場合
- ssh-agent状態確認: `ssh-add -l`
- 必要に応じて: `ssh-add ~/.ssh/id_ed25519`

### HTTPS接続になっている場合
```bash
git remote -v  # 確認
git remote set-url origin git@github.com:<GITHUB_ACCOUNT>/PROJECT_NAME.git  # 修正
```

## 📋 チェックリスト

新プロジェクト開始時:
- [ ] Git設定確認
- [ ] SSH接続確認  
- [ ] リモートURLがSSH形式
- [ ] テストコミット・プッシュ実行
- [ ] 作者名が正しいアカウントになっている

## 🎯 適用プロジェクト

- ✅ Komon
- ✅ Okina
- 🔄 今後の新プロジェクト全て