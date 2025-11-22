#!/bin/bash
# カバレッジレポート生成スクリプト

# 古いカバレッジデータを削除
rm -f .coverage .coverage.* 2>/dev/null

# 一時的にHOMEディレクトリに.coverageファイルを作成する設定
export COVERAGE_FILE="/tmp/.coverage.$$"

# カバレッジ測定付きでテスト実行
echo "テスト実行中..."
coverage run --source=src/komon -m pytest tests/ --no-cov -q

# レポート生成
echo ""
echo "=========================================="
echo "カバレッジレポート"
echo "=========================================="
coverage report -m

# HTMLレポート生成
coverage html -d htmlcov
echo ""
echo "HTMLレポートを htmlcov/index.html に生成しました"

# クリーンアップ
rm -f "$COVERAGE_FILE" 2>/dev/null
