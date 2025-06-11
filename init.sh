#!/bin/bash

echo "🛠 Komon 初期セットアップを開始します..."

# 1. logディレクトリ作成
if [ ! -d "log" ]; then
  mkdir log
  echo "[✔] log/ ディレクトリを作成しました。"
else
  echo "[ℹ] log/ ディレクトリは既に存在します。"
fi

# 2. Python依存ライブラリのインストール
if [ -f "requirements.txt" ]; then
  echo "[🔄] Pythonライブラリをインストール中..."
  pip install -r requirements.txt
  echo "[✔] 依存ライブラリのインストールが完了しました。"
else
  echo "[⚠] requirements.txt が見つかりません。スキップします。"
fi

# 3. settings.ymlの生成（雛形がある場合）
if [ ! -f "settings.yml" ]; then
  if [ -f "settings.example.yml" ]; then
    cp settings.example.yml settings.yml
    echo "[✔] settings.yml を生成しました。"
  else
    echo "[⚠] settings.example.yml が見つかりません。settings.yml を手動で用意してください。"
  fi
else
  echo "[ℹ] settings.yml は既に存在します。"
fi

# 4. Komonのインストール（開発モード）
if [ -f "setup.py" ]; then
  echo "[🔄] Komon を開発モードでインストール中..."
  pip install -e .
  echo "[✔] Komon のインストールが完了しました。"
else
  echo "[⚠] setup.py が見つかりません。'komon' コマンドは使えない可能性があります。"
fi

# 5. 実行可能スクリプト紹介
echo
echo "📘 実行可能なスクリプト一覧:"
echo " - main.py              ：CPU/メモリ/ディスク使用率の監視"
echo " - main_log_monitor.py  ：ログ急増の監視"
echo " - main_log_trend.py    ：ログトレンド分析"
echo " - advise.py            ：対話型アドバイザー"
echo

# 6. crontab登録案内
echo "📅 推奨crontab設定（参考）:"
echo "  * * * * * cd /your/path/to/Komon && python3 main.py >> log/main.log 2>&1"
echo

# 7. 初期設定の案内
echo "📦 初期設定を行うには："
echo "  komon initial または python3 initial.py を実行してください。"
echo

echo "🎉 Komon 初期セットアップが完了しました！"

