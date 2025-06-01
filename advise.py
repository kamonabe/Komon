import yaml
from komon.analyzer import analyze_usage, load_thresholds
from komon.monitor import get_resource_usage
from komon.log_trends import analyze_log_trend, detect_repeated_spikes

def ask_yes_no(question: str) -> bool:
    """y/n 質問の簡易ユーティリティ"""
    while True:
        ans = input(f"{question} [y/n] > ").strip().lower()
        if ans in ("y", "yes"):
            return True
        elif ans in ("n", "no"):
            return False
        else:
            print("→ y または n で答えてください。")

def advise_os_update():
    if ask_yes_no("最近、OSやパッケージの更新は行いましたか？"):
        print("→ OKです。定期的な確認を続けていきましょう。")
    else:
        print("→ `sudo apt update && sudo apt upgrade` の実行をおすすめします。")

def advise_high_memory(usage, thresholds):
    mem_percent = usage.get("mem", 0)
    threshold_mem = thresholds.get("mem", 80)
    if mem_percent >= threshold_mem:
        if ask_yes_no(f"MEM使用率が{mem_percent}%と高めです。多く使っているプロセスを調べますか？"):
            print("→ 実メモリを多く使用しているプロセスを確認しましょう。")
            print("   - `top` または `htop` でリアルタイムにメモリ消費プロセスを確認")
            print("   - `ps aux --sort=-%mem | head` で上位プロセスを一覧表示")
            print("   - Chrome, Docker, Python などが原因の場合があります")

def advise_high_disk(usage, thresholds):
    disk_percent = usage.get("disk", 0)
    threshold_disk = thresholds.get("disk", 80)
    if disk_percent >= threshold_disk:
        if ask_yes_no(f"ディスク使用率が{disk_percent}%と高めです。不要なファイルを整理しますか？"):
            print("→ ディスクを圧迫しているファイル・ディレクトリを調査しましょう。")
            print("   - `du -sh *` や `ncdu` でサイズの大きいフォルダを特定")
            print("   - `journalctl --vacuum-time=7d` で古いログを削除")
            print("   - 不要なキャッシュやバックアップファイルの削除も検討")

def advise_uptime(profile):
    try:
        with open("/proc/uptime") as f:
            uptime_sec = float(f.readline().split()[0])
            days = int(uptime_sec // 86400)
            if days >= 7:
                if ask_yes_no(f"サーバが{days}日間連続稼働しています。再起動を検討しますか？"):
                    if profile.get("usage") == "production":
                        print("→ 本番環境では安定性確保のため、定期再起動を検討しましょう。")
                    else:
                        print("→ 長期間の稼働は不安定化の要因になります。必要に応じて再起動を。")
    except:
        pass

def advise_email_disabled(config):
    notifications = config.get("notifications", {})
    if not notifications.get("email", {}).get("enabled", False):
        if ask_yes_no("メール通知が無効になっています。Slack以外でも通知を受け取りたいですか？"):
            print("→ `settings.yml` の email.enabled を true にして設定してみましょう。")

def advise_high_cpu(usage, thresholds):
    cpu_percent = usage.get("cpu", 0)
    threshold_cpu = thresholds.get("cpu", 85)
    if cpu_percent >= threshold_cpu:
        if ask_yes_no(f"CPU使用率が{cpu_percent}%と高い状態です。負荷の高いプロセスを確認しますか？"):
            print("→ 高負荷なプロセスを調査し、必要に応じて停止や調整を検討しましょう。")
            print("   - `top` でCPU使用率の高いプロセスを確認")
            print("   - `ps aux --sort=-%cpu | head` で上位プロセスを一覧表示")
            print("   - 一時的なビルド処理やバックグラウンドジョブに注意")

def advise_komon_update():
    if ask_yes_no("Komonのコードがしばらく更新されていない気がします。最新状態を確認しますか？"):
        print("→ `git pull` でリポジトリを最新状態に保てます。Komonは静かに進化を続けています。")

def advise_log_trend(config):
    print("\n📈 ログ傾向分析")
    suspicious_logs = []
    for log_id, enabled in config.get("log_monitor_targets", {}).items():
        if enabled:
            result = analyze_log_trend(log_id)
            print(result)
            if detect_repeated_spikes(log_id):
                suspicious_logs.append(log_id)

    if suspicious_logs:
        print("\n💡 最近、複数日にわたってログが急増しているものがあります。")
        for log in suspicious_logs:
            print(f"   - {log}")
        print("→ `logrotate` の設定や、アプリのログ出力レベルの調整を検討しましょう。")

def run_advise():
    try:
        with open("settings.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ settings.yml の読み込みに失敗しました: {e}")
        return

    usage = get_resource_usage()
    thresholds = load_thresholds(config)
    alerts = analyze_usage(usage, thresholds)

    print("🔔 警戒情報")
    if alerts:
        for alert in alerts:
            print(f"- {alert}")
    else:
        print("（なし）")

    print("\n💡 改善提案")
    advise_os_update()
    advise_high_memory(usage, thresholds)
    advise_high_disk(usage, thresholds)
    advise_uptime(config.get("profile", {}))
    advise_email_disabled(config)
    advise_high_cpu(usage, thresholds)
    advise_komon_update()
    advise_log_trend(config)

if __name__ == "__main__":
    run_advise()
