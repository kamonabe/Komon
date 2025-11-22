#!/usr/bin/env python3
"""
簡易カバレッジチェックスクリプト
テストファイルと実装ファイルを比較して、テストされていないモジュールを特定します。
"""

import os
from pathlib import Path

# 実装ファイルのディレクトリ
SRC_DIR = Path("src/komon")
# テストファイルのディレクトリ
TEST_DIR = Path("tests")

def get_python_files(directory):
    """指定ディレクトリ内のPythonファイルを取得"""
    return [f.stem for f in directory.glob("*.py") if f.stem != "__init__"]

def main():
    # 実装ファイルを取得
    src_files = set(get_python_files(SRC_DIR))
    
    # テストファイルを取得（test_プレフィックスを除去）
    test_files = set()
    for f in TEST_DIR.glob("test_*.py"):
        # test_analyzer.py -> analyzer
        module_name = f.stem.replace("test_", "")
        test_files.add(module_name)
    
    # テスト済みとテスト未実施を分類
    tested = src_files & test_files
    untested = src_files - test_files
    
    print("=" * 60)
    print("Komon テストカバレッジ分析")
    print("=" * 60)
    print()
    
    print(f"📊 実装ファイル数: {len(src_files)}")
    print(f"✅ テスト済み: {len(tested)}")
    print(f"❌ 未テスト: {len(untested)}")
    print(f"📈 カバレッジ率: {len(tested) / len(src_files) * 100:.1f}%")
    print()
    
    print("=" * 60)
    print("✅ テスト済みモジュール")
    print("=" * 60)
    for module in sorted(tested):
        test_file = TEST_DIR / f"test_{module}.py"
        if test_file.exists():
            # テスト数をカウント
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                test_count = content.count("def test_")
            print(f"  • {module}.py ({test_count} tests)")
    print()
    
    print("=" * 60)
    print("❌ 未テストモジュール")
    print("=" * 60)
    for module in sorted(untested):
        src_file = SRC_DIR / f"{module}.py"
        if src_file.exists():
            # 行数をカウント
            with open(src_file, 'r', encoding='utf-8') as f:
                lines = len([l for l in f if l.strip() and not l.strip().startswith('#')])
            print(f"  • {module}.py (~{lines} lines)")
    print()
    
    print("=" * 60)
    print("推奨アクション")
    print("=" * 60)
    if untested:
        print("以下のモジュールのテストを追加することを推奨します：")
        for module in sorted(untested):
            print(f"  1. tests/test_{module}.py を作成")
        print()
        print("優先度:")
        priority_modules = {
            "notification": "高 - 外部サービス連携",
            "log_watcher": "高 - ファイルI/O処理",
            "log_trends": "中 - データ分析ロジック",
            "cli": "低 - エントリーポイント"
        }
        for module in sorted(untested):
            if module in priority_modules:
                print(f"  • {module}: {priority_modules[module]}")
    else:
        print("✨ 全てのモジュールにテストが存在します！")
    print()

if __name__ == "__main__":
    main()
