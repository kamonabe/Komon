"""
CLIエントリーポイント

komonコマンドのメイン処理を提供します。
"""

import sys
import os
import subprocess
from komon import __version__


def main():
    """CLIのメインエントリーポイント"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    
    # バージョン表示
    if command in ["--version", "-v"]:
        print(f"Komon version {__version__}")
        return
    
    # scriptsディレクトリのパスを取得
    # インストールされている場合は、カレントディレクトリのscriptsを使用
    scripts_dir = os.path.join(os.getcwd(), "scripts")
    
    if not os.path.exists(scripts_dir):
        print("❌ scriptsディレクトリが見つかりません。")
        print("   プロジェクトのルートディレクトリで実行してください。")
        return
    
    # コマンドに対応するスクリプトを実行
    script_map = {
        "initial": "initial.py",
        "status": "status.py",
        "advise": "advise.py",
        "guide": "komon_guide.py",
    }
    
    if command in script_map:
        script_path = os.path.join(scripts_dir, script_map[command])
        if os.path.exists(script_path):
            # Pythonスクリプトを実行（追加の引数も渡す）
            subprocess.run([sys.executable, script_path] + sys.argv[2:])
        else:
            print(f"❌ スクリプトが見つかりません: {script_path}")
    else:
        print(f"❌ 不明なコマンド: {command}")
        print_usage()


def print_usage():
    """使用方法を表示"""
    print("""
Komon - 軽量アドバイザー型SOAR風監視ツール

使用方法:
  komon initial       初期設定を実行
  komon status        現在のステータスを表示
  komon advise        対話型アドバイザーを実行
  komon guide         ガイドメニューを表示
  komon --version     バージョン情報を表示

詳細は docs/README.md を参照してください。
""")


if __name__ == "__main__":
    main()
