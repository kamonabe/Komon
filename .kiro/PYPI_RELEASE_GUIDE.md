# PyPIリリース手順

## 📦 手動リリース手順（現在の方法）

### 1. バージョン更新

```bash
# version.txtを更新
echo "1.23.0" > version.txt

# src/komon/__init__.pyを更新
vim src/komon/__init__.py
# __version__ = "1.23.0" に変更

# CHANGELOGを更新
vim docs/CHANGELOG.md
# [Unreleased] を [1.23.0] - YYYY-MM-DD に変更

# project-config.ymlを更新
vim .kiro/steering/project-config.yml
# current_version: "1.23.0" に変更
```

### 2. テスト実行

```bash
# 全テスト実行
bash run_coverage.sh

# 動作確認
python scripts/advise.py
```

### 3. コミット＆タグ

```bash
git add version.txt src/komon/__init__.py docs/CHANGELOG.md .kiro/steering/project-config.yml
git commit -m "chore: bump version to 1.23.0"
git push

git tag v1.23.0
git push origin v1.23.0
```

### 4. PyPIにアップロード

```bash
# 古いビルドを削除
rm -rf dist/ build/ src/*.egg-info

# ビルド
python3 -m build

# アップロード
python3 -m twine upload dist/*
```

### 5. GitHub Releasesを作成

1. https://github.com/kamonabe/Komon/releases/new にアクセス
2. Tag: `v1.23.0` を選択
3. Title: `v1.23.0 - 機能名`
4. Description: CHANGELOGから内容をコピー
5. "Publish release" をクリック

## ⚠️ 注意事項

- PyPIは一度アップロードしたバージョンを削除できない
- アップロード前に必ずテストを実行
- version.txt、src/komon/__init__.py、CHANGELOG.md、project-config.ymlの4ファイルを忘れずに更新

## 🔮 将来の自動化

慣れてきたら `.github/workflows/publish-to-pypi.yml` を作成して自動化を検討。
詳細は開発ワークフローのドキュメントを参照。

## 📊 リリース履歴

- v1.22.0 (2025-12-01): 初回PyPI公開
