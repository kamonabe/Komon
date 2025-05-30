import yaml
from komon.analyzer import analyze_usage, load_thresholds
from komon.monitor import get_resource_usage
from komon.log_trends import analyze_log_trend


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

    # 提案①：OSアップデート
    if ask_yes_no("最近、OSやパッケージの更新は行いましたか？"):
        print("→ OKです。定期的な確認を続けていきましょう。")
    else:
        print("→ `sudo apt update && sudo apt upgrade` の実行をおすすめします。")

    # 提案②：メモリ高負荷
    mem_percent = usage.get("mem", 0)
    threshold_mem = thresholds.get("mem", 80)
    if mem_percent >= threshold_mem:
        if ask_yes_no(f"MEM使用率が{mem_percent}%と高めです。多く使っているプロセスを調べますか？"):
            print("→ `top` や `htop` を使ってみましょう。ChromeやDockerが原因のこともあります。")

    # 提案③：ディスク高負荷
    disk_percent = usage.get("disk", 0)
    threshold_disk = thresholds.get("disk", 80)
    if disk_percent >= threshold_disk:
        if ask_yes_no(f"ディスク使用率が{disk_percent}%と高めです。不要なファイルを整理しますか？"):
            print("→ `du -sh *` や `journalctl --vacuum-time=7d` で容量削減できます。")

    # 提案④：長時間稼働（7日以上）
    try:
        with open("/proc/uptime") as f:
            uptime_sec = float(f.readline().split()[0])
            days = int(uptime_sec // 86400)
            if days >= 7:
                if ask_yes_no(f"サーバが{days}日間連続稼働しています。再起動を検討しますか？"):
                    print("→ 長期間の稼働は不安定化の要因になります。適度な再起動は有効です。")
    except:
        pass  # 非Linux環境などでもスルー可

    # 提案⑤：メール通知が無効な場合
    notifications = config.get("notifications", {})
    if not notifications.get("email", {}).get("enabled", False):
        if ask_yes_no("メール通知が無効になっています。Slack以外でも通知を受け取りたいですか？"):
            print("→ `settings.yml` の email.enabled を true にして設定してみましょう。")

    # 提案⑥：CPU使用率が高い
    cpu_percent = usage.get("cpu", 0)
    threshold_cpu = thresholds.get("cpu", 85)
    if cpu_percent >= threshold_cpu:
        if ask_yes_no(f"CPU使用率が{cpu_percent}%と高い状態です。負荷の高いプロセスを確認しますか？"):
            print("→ `top` や `ps aux --sort=-%cpu` を使って原因プロセスを確認しましょう。")

    # 提案⑦：Komon自身の更新確認（ユーモア枠）
    if ask_yes_no("Komonのコードがしばらく更新されていない気がします。最新状態を確認しますか？"):
        print("→ `git pull` でリポジトリを最新状態に保てます。Komonは静かに進化を続けています。")

    # 提案⑧：ログ傾向分析
    print("\n📈 ログ傾向分析")
    for log_id, enabled in config.get("log_monitor_targets", {}).items():
        if enabled:
            result = analyze_log_trend(log_id)
            print(result)


if __name__ == "__main__":
    run_advise()
