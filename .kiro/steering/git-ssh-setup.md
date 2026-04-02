---
inclusion: manual
---

# Git & SSH 設定ガイド

> 実際の値は `project-config.yml` の `git.user` セクションで管理。
> 以下のプレースホルダーを自分の情報に読み替えてください。

## 初期設定（一度だけ実行）

```bash
# 1. Git設定
git config --global user.name "<GIT_USER_NAME>"
git config --global user.email "<GIT_USER_EMAIL>"

# 2. SSH鍵生成
ssh-keygen -t ed25519 -C "<GIT_USER_EMAIL>"

# 3. 公開鍵をGitHubに登録
cat ~/.ssh/id_ed25519.pub

# 4. ssh-agent自動起動
cat >> ~/.bashrc << 'EOF'
if [ -z "$SSH_AUTH_SOCK" ]; then
    eval "$(ssh-agent -s)" > /dev/null 2>&1
    ssh-add ~/.ssh/id_ed25519 2>/dev/null
fi
EOF

# 5. 便利エイリアス
echo "alias git-ready='ssh-add ~/.ssh/id_ed25519 && echo \"Git準備完了！\"'" >> ~/.bashrc
source ~/.bashrc
```

## 確認方法

```bash
git config --global --list | grep -E "(user\.name|user\.email)"
ssh -T git@github.com
```

## 新プロジェクトでのSSH設定

```bash
git remote set-url origin git@github.com:<GITHUB_ACCOUNT>/PROJECT_NAME.git
```

## トラブルシューティング

- 意図しないユーザー名 → `git config --local --list` で確認
- パスフレーズ毎回要求 → `ssh-add -l` で確認、`ssh-add ~/.ssh/id_ed25519`
- HTTPS接続 → `git remote -v` で確認、SSH URLに変更
