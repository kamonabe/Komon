"""
Guide command implementation

ガイドコマンドの実装を提供します。
"""

from pathlib import Path


def show_menu():
    """メニューを表示してユーザーの選択を取得"""
    print("\n📘 ようこそ Komon ガイドセンターへ！\n")
    print("何を案内しましょうか？\n")
    print("[1] Komonってなに？（全体像）")
    print("[2] 初期セットアップの手順")
    print("[3] スクリプト一覧と使い方")
    print("[4] cron登録の例")
    print("[5] 通知設定の方法")
    print("[6] よくある質問とトラブル対応")
    print("[0] 終了")
    return input("\n番号を入力してください: ").strip()


def guide_1():
    """Komonの概要説明"""
    print("\n🔹 Komonってなに？\n")
    print("Komonは、軽量SOAR風の監視＆運用支援ツールです。")
    print("CPU・メモリ・ディスクの使用率やログの急増などを監視し、Slackやメールで通知します。")
    print("小規模な開発環境や個人サーバでも、手軽に導入・活用できるよう設計されています。")


def guide_2():
    """初期セットアップの手順説明"""
    print("\n🔹 初期セットアップの手順\n")
    print("1. `pip install komon` でKomonをインストールします")
    print("2. `komon initial` を実行して、初期設定ファイル（settings.yml）を作成します。")
    print("3. 設定ファイルを編集して、通知先やしきい値を調整します。")


def guide_3():
    """コマンド一覧と使い方説明"""
    print("\n🔹 コマンド一覧と使い方\n")
    print("- komon advise    ：CLIアドバイザー（現在の状況をガイド付きで確認）")
    print("- komon status    ：システムステータスの表示")
    print("- komon initial   ：初期設定ファイルの作成")
    print("- komon guide     ：このガイド（使い方の説明）")
    print("\n詳細なオプションは各コマンドに --help を付けて確認できます。")


def guide_4():
    """cron登録の例説明"""
    print("\n🔹 cron登録の例\n")
    print("以下のように登録すると1分ごとに自動監視されます：\n")
    print("  # Komonの監視を1分ごとに実行")
    print("  * * * * * komon advise --section alerts >> /var/log/komon.log 2>&1")
    print("\n注意：")
    print("- cronで実行する場合は、フルパスを使用することを推奨します")
    print("- ログファイルの場所は適宜調整してください")


def guide_5():
    """通知設定の方法説明"""
    print("\n🔹 通知設定の方法\n")
    print("初期設定時にSlackやメールの通知を有効化できます。")
    print("後から設定ファイル（settings.yml）の `notifications` セクションを編集して")
    print("Webhook URLや宛先を設定してください。")
    print("\n設定ファイルの場所：")
    print("- 現在のディレクトリの settings.yml")
    print("- または ~/.komon/settings.yml")


def guide_6():
    """よくある質問とトラブル対応説明"""
    print("\n🔹 よくある質問とトラブル対応\n")
    print("- Q: settings.yml を作り直したい")
    print("  A: `komon initial` を再実行してください。")
    print()
    print("- Q: Slack通知が届かない")
    print("  A: Webhook URLの設定ミスやネットワーク制限を確認してください。")
    print()
    print("- Q: cronが動いていない")
    print("  A: `crontab -e` の内容を確認し、ログファイル出力をチェックしてみてください。")
    print()
    print("- Q: 設定ファイルが見つからない")
    print("  A: `komon initial` で設定ファイルを作成してください。")


def run_guide(config_dir: Path):
    """
    ガイドのメイン実行関数
    
    Args:
        config_dir: 設定ディレクトリのパス（現在は使用していないが、将来の拡張用）
    """
    while True:
        choice = show_menu()
        if choice == "1":
            guide_1()
        elif choice == "2":
            guide_2()
        elif choice == "3":
            guide_3()
        elif choice == "4":
            guide_4()
        elif choice == "5":
            guide_5()
        elif choice == "6":
            guide_6()
        elif choice == "0":
            print("\n👋 ご利用ありがとうございました！")
            break
        else:
            print("\n⚠️ 無効な選択です。0〜6の番号を入力してください。")