# komon_guide.py

def show_menu():
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
    print("\n🔹 Komonってなに？\n")
    print("Komonは、軽量SOAR風の監視＆運用支援ツールです。")
    print("CPU・メモリ・ディスクの使用率やログの急増などを監視し、Slackやメールで通知します。")
    print("小規模な開発環境や個人サーバでも、手軽に導入・活用できるよう設計されています。")


def guide_2():
    print("\n🔹 初期セットアップの手順\n")
    print("1. `bash init.sh` を実行します（依存ライブラリをインストール）")
    print("2. `komon initial` または `python3 initial.py` を実行して、初期設定ファイル（settings.yml）を作成します。")


def guide_3():
    print("\n🔹 スクリプト一覧と使い方\n")
    print("- main.py              ：CPU/メモリ/ディスク使用率の監視")
    print("- main_log_monitor.py  ：ログ急増の監視")
    print("- main_log_trend.py    ：ログの傾向分析（過去推移からトレンドを検知）")
    print("- advise.py            ：CLIアドバイザー（現在の状況をガイド付きで確認）")


def guide_4():
    print("\n🔹 cron登録の例\n")
    print("以下のように登録すると1分ごとに自動監視されます：\n")
    print("  * * * * * cd /your/path/to/Komon && python3 main.py >> logs/main.log 2>&1")


def guide_5():
    print("\n🔹 通知設定の方法\n")
    print("初期設定時にSlackやメールの通知を有効化できます。")
    print("後から `settings.yml` の `notification` セクションを編集してWebhook URLや宛先を設定してください。")


def guide_6():
    print("\n🔹 よくある質問とトラブル対応\n")
    print("- Q: settings.yml を作り直したい\n  A: `python3 initial.py` を再実行してください。")
    print("- Q: Slack通知が届かない\n  A: Webhook URLの設定ミスやネットワーク制限を確認してください。")
    print("- Q: cronが動いていない\n  A: `crontab -e` の内容を確認し、ログファイル出力をチェックしてみてください。")


def main():
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


if __name__ == "__main__":
    main()

