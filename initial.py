import os
import yaml

def get_input(prompt, default=None, cast_func=str):
    user_input = input(f"{prompt} [デフォルト: {default}] : ")
    if user_input.strip() == "":
        return default
    try:
        return cast_func(user_input)
    except ValueError:
        print("⚠ 入力形式が正しくありません。デフォルト値を使用します。")
        return default

def run_initial_setup():
    print("🔧 Komon 初期設定を開始します...\n")

    # 既存ファイルがあればスキップ
    if os.path.exists("settings.yml"):
        print("⚠ settings.yml はすでに存在します。初期設定はスキップされました。")
        return

    # 使用率閾値の取得
    print("📊 リソース使用率の閾値設定：")
    cpu_threshold = get_input(" - CPU使用率の閾値（%）", 80, int)
    mem_threshold = get_input(" - MEMORY使用率の閾値（%）", 80, int)
    disk_threshold = get_input(" - DISK使用率の閾値（%）", 90, int)

    # Slack通知の設定
    slack_enabled = get_input("🔔 Slack通知を有効にしますか？ (True/False)", False, lambda x: x.lower() == "true")
    webhook_url = "https://hooks.slack.com/services/your/webhook/url"
    if slack_enabled:
        webhook_url = input("🔗 Webhook URLを入力してください（空欄の場合は後でsettings.ymlで編集可能です）: ").strip() or webhook_url

    # メール通知の設定
    email_enabled = get_input("📧 メール通知を有効にしますか？ (True/False)", False, lambda x: x.lower() == "true")

    settings_dict = {
        "thresholds": {
            "cpu": cpu_threshold,
            "memory": mem_threshold,
            "disk": disk_threshold
        },
        "log_monitor_targets": {
            "/var/log/messages": True,
            "systemd journal": True
        },
        "notification": {
            "slack": {
                "enabled": slack_enabled,
                "webhook_url": webhook_url
            },
            "email": {
                "enabled": email_enabled,
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "from_address": "komon@example.com",
                "to_address": "admin@example.com"
            }
        }
    }

    with open("settings.yml", "w") as f:
        yaml.dump(settings_dict, f, sort_keys=False)

    print("\n✅ settings.yml を作成しました！\n")
    print("🎯 次のステップ：")
    print("  → komon advise または python3 advise.py を実行してみましょう！")
    print("  → cron登録もおすすめです。\n")
    print("📁 補足：")
    print("  個別の監視ログを追加したい場合は、")
    print("  settings.yml の `log_monitor_targets` セクションにログファイルパスを追記してください。")

# komon CLI から実行される用
def main():
    run_initial_setup()

# 単体実行にも対応
if __name__ == "__main__":
    main()

