#!/bin/bash
# Coverage SQLiteロック問題の修正スクリプト

echo "=========================================="
echo "Coverage設定の修正"
echo "=========================================="
echo ""

# 1. 古い.coverageファイルを削除
echo "1. 古い.coverageファイルをクリーンアップ..."
rm -f .coverage .coverage.* 2>/dev/null
echo "   ✅ 完了"
echo ""

# 2. .coveragercを作成（ローカルディスクに保存）
echo "2. .coveragercを作成..."
cat > .coveragerc << 'EOF'
[run]
source = src/komon
parallel = False
concurrency = thread
# CIFS/SMB共有上のSQLiteロック問題を回避するため、ローカルディスクに保存
data_file = /home/kamodev/.coverage_devproject101
omit = 
    */tests/*
    */test_*.py
    */__pycache__/*
    */site-packages/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
EOF
echo "   ✅ 完了"
echo ""

# 3. run_coverage.shを更新（pytest-covを使わない方式）
echo "3. run_coverage.shを更新..."
cat > run_coverage.sh << 'EOF'
#!/bin/bash
# カバレッジレポート生成スクリプト（CIFS対応版）

# 環境変数でローカルディスクを指定
export COVERAGE_FILE=/home/kamodev/.coverage_devproject101

# 古いカバレッジデータを削除
rm -f "$COVERAGE_FILE" 2>/dev/null

echo "=========================================="
echo "テスト実行中..."
echo "=========================================="

# coverage CLI のみを使用（pytest-covは使わない）
coverage run --source=src/komon -m pytest tests/ --no-cov -q

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "カバレッジレポート"
    echo "=========================================="
    coverage report -m
    
    echo ""
    echo "=========================================="
    echo "HTMLレポート生成中..."
    echo "=========================================="
    coverage html
    echo "✅ HTMLレポートを htmlcov/index.html に生成しました"
else
    echo "❌ テストが失敗しました"
    exit 1
fi
EOF
chmod +x run_coverage.sh
echo "   ✅ 完了"
echo ""

echo "=========================================="
echo "✅ 設定完了！"
echo "=========================================="
echo ""
echo "次のコマンドでカバレッジレポートを生成できます："
echo "  bash run_coverage.sh"
echo ""
