"""
CLIエントリーポイント

komonコマンドのメイン処理を提供します。
"""

import sys
import os
import argparse
from pathlib import Path
from komon import __version__


def get_config_dir():
    """設定ディレクトリのパスを取得"""
    # 1. 環境変数 KOMON_CONFIG_DIR が設定されている場合
    if "KOMON_CONFIG_DIR" in os.environ:
        return Path(os.environ["KOMON_CONFIG_DIR"])
    
    # 2. カレントディレクトリに settings.yml がある場合（開発環境）
    current_dir = Path.cwd()
    if (current_dir / "settings.yml").exists():
        return current_dir
    
    # 3. ホームディレクトリの .komon/ を使用（インストール環境）
    home_config = Path.home() / ".komon"
    return home_config


def ensure_config_dir():
    """設定ディレクトリが存在することを確認し、必要に応じて作成"""
    config_dir = get_config_dir()
    
    # ディレクトリが存在しない場合は作成
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 設定ディレクトリを作成しました: {config_dir}")
    
    # データディレクトリも作成
    data_dir = config_dir / "data"
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir


def main():
    """CLIのメインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="Komon - 軽量アドバイザー型SOAR風監視ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"Komon version {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="利用可能なコマンド")
    
    # initial コマンド
    initial_parser = subparsers.add_parser("initial", help="初期設定を実行")
    
    # status コマンド
    status_parser = subparsers.add_parser("status", help="現在のステータスを表示")
    status_parser.add_argument("--verbose", action="store_true", help="詳細表示")
    
    # advise コマンド
    advise_parser = subparsers.add_parser("advise", help="対話型アドバイザーを実行")
    advise_parser.add_argument("--history", type=int, metavar="N", help="通知履歴の表示件数")
    advise_parser.add_argument("--verbose", action="store_true", help="詳細表示モード")
    advise_parser.add_argument("--section", choices=["status", "alerts", "advice", "log", "disk", "process", "history", "network"], help="特定のセクションのみ表示")
    advise_parser.add_argument("--with-net", action="store_true", help="全部（リソース・ログ + ping + http）")
    advise_parser.add_argument("--net-only", action="store_true", help="ネットワークチェックのみ（ping + http）")
    advise_parser.add_argument("--ping-only", action="store_true", help="pingチェックのみ")
    advise_parser.add_argument("--http-only", action="store_true", help="httpチェックのみ")
    
    # guide コマンド
    guide_parser = subparsers.add_parser("guide", help="ガイドメニューを表示")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 設定ディレクトリを確保
    config_dir = ensure_config_dir()
    
    # 各コマンドに設定ディレクトリを渡して実行
    if args.command == "initial":
        from komon.commands.initial import run_initial_setup
        run_initial_setup(config_dir)
    elif args.command == "status":
        from komon.commands.status import run_status
        run_status(config_dir)
    elif args.command == "advise":
        from komon.commands.advise import run_advise
        
        # ネットワークチェックオプションの処理
        net_mode = None
        if args.with_net:
            net_mode = "with_net"
        elif args.net_only:
            net_mode = "net_only"
        elif args.ping_only:
            net_mode = "ping_only"
        elif args.http_only:
            net_mode = "http_only"
        
        # 0が指定された場合は全件表示（Noneを渡す）
        history_limit = None if args.history == 0 else args.history
        
        run_advise(
            config_dir=config_dir,
            history_limit=history_limit,
            verbose=args.verbose,
            section=args.section,
            net_mode=net_mode
        )
    elif args.command == "guide":
        from komon.commands.guide import run_guide
        run_guide(config_dir)


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
