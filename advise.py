import datetime
import json
import os
import re
import subprocess
import time

import yaml
import psutil
from komon.analyzer import analyze_usage, load_thresholds
from komon.monitor import collect_detailed_resource_usage
from komon.log_trends import analyze_log_trend, detect_repeated_spikes

SKIP_FILE = "komon_data/skip_advices.json"

def ask_yes_no(question: str) -> bool:
    while True:
        ans = input(f"{question} [y/n] > ").strip().lower()
        if ans in ("y", "yes"):
            return True
        elif ans in ("n", "no"):
            return False
        print("→ y または n で答えてください。")

def should_skip(key: str, days: int = 7) -> bool:
    if not os.path.exists(SKIP_FILE):
        return False
    try:
        with open(SKIP_FILE, "r", encoding="utf-8") as f:
            skip_data = json.load(f)
        skipped_at = skip_data.get(key, {}).get("skipped_at")
        if not skipped_at:
            return False
        skipped_time = datetime.datetime.fromisoformat(skipped_at)
        return (datetime.datetime.now() - skipped_time).days < days
    except Exception:
        return False

def record_skip(key: str):
    try:
        data = {}
        if os.path.exists(SKIP_FILE):
            with open(SKIP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        data[key] = {"skipped_at": datetime.datetime.now().isoformat()}
        os.makedirs(os.path.dirname(SKIP_FILE), exist_ok=True)
        with open(SKIP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠ スキップ記録に失敗しました: {e}")

def skippable_advice(key: str, question: str, action: callable):
    if should_skip(key):
        return
    if ask_yes_no(question):
        action()
    else:
        record_skip(key)

def advise_os_update():
    try:
        sec_result = subprocess.run([
            "dnf", "updateinfo", "list", "security", "available"
        ], capture_output=True, text=True)
        sec_lines = sec_result.stdout.strip().splitlines()
        sec_updates = [line for line in sec_lines if re.match(r"^RHSA-\\d{4}:", line)]

        print("① セキュリティパッチの確認")
        if sec_updates:
            print(f"→ セキュリティ更新が {len(sec_updates)} 件あります。例：")
            for line in sec_updates[:10]:
                print(f"   - {line}")
            if ask_yes_no("これらのセキュリティパッチを適用しますか？"):
                subprocess.run(["sudo", "dnf", "upgrade", "--security", "-y"])
                print("→ セキュリティアップデートを適用しました。再起動が必要な場合があります。")
            else:
                print("→ セキュリティアップデートは保留されました。")
        else:
            print("→ セキュリティ更新はありません。")

        print("\n② システムパッチ（セキュリティ以外）の確認")
        result = subprocess.run(["dnf", "check-update"], capture_output=True, text=True)
        if result.returncode == 100:
            all_lines = result.stdout.strip().splitlines()
            normal_updates = [
                line for line in all_lines
                if line and not line.startswith(("Last metadata", "Obsoleting"))
            ]
            if normal_updates:
                print(f"→ セキュリティ以外の更新が {len(normal_updates)} 件あります。例：")
                for line in normal_updates[:10]:
                    print(f"   - {line}")
                print("\n💡 以下のコマンドでこれらをまとめて適用できます：")
                print("   sudo dnf upgrade -y")
            else:
                print("→ セキュリティ以外の更新は見つかりませんでした。")
        else:
            print("→ パッケージは最新の状態です。")

    except FileNotFoundError:
        print("→ dnf が見つかりません。AlmaLinuxであることを確認してください。")
    except Exception as e:
        print(f"⚠ アップデート確認中にエラーが発生しました: {e}")

def advise_resource_usage(usage: dict, thresholds: dict):
    if usage.get("mem", 0) >= thresholds.get("mem", 80):
        if ask_yes_no(f"MEM使用率が{usage['mem']}%と高めです。多く使っているプロセスを調べますか？"):
            print("→ `top` や `ps aux --sort=-%mem | head` で上位プロセスを確認しましょう。")

    if usage.get("disk", 0) >= thresholds.get("disk", 80):
        if ask_yes_no(f"ディスク使用率が{usage['disk']}%と高めです。不要なファイルを整理しますか？"):
            print("→ `du -sh *` や `journalctl --vacuum-time=7d` を活用しましょう。")

    if usage.get("cpu", 0) >= thresholds.get("cpu", 85):
        if ask_yes_no(f"CPU使用率が{usage['cpu']}%と高い状態です。負荷の高いプロセスを確認しますか？"):
            print("→ `top` や `ps aux --sort=-%cpu | head` で高負荷プロセスを確認できます。")

def advise_uptime(profile):
    try:
        with open("/proc/uptime") as f:
            uptime_sec = float(f.readline().split()[0])
            days = int(uptime_sec // 86400)
            if days >= 7 and ask_yes_no(f"サーバが{days}日間連続稼働しています。再起動を検討しますか？"):
                if profile.get("usage") == "production":
                    print("→ 本番環境では定期的な再起動も安定性向上につながります。")
                else:
                    print("→ 長期間の稼働は不安定化の要因になります。再起動を検討しましょう。")
    except:
        pass

def advise_email_disabled(config):
    if not config.get("notifications", {}).get("email", {}).get("enabled", False):
        def action():
            print("→ `settings.yml` の email.enabled を true に設定しましょう。")
        skippable_advice("email_disabled", "メール通知が無効です。Slack以外でも通知を受け取りたいですか？", action)

def advise_process_breakdown(usage: dict):
    cpu_details = usage.get("cpu_by_process", [])
    mem_details = usage.get("mem_by_process", [])

    if cpu_details:
        print("\n📌 CPU使用率の内訳：")
        for proc in cpu_details:
            print(f"- {proc['name']}: {proc['cpu']}%")

    if mem_details:
        print("\n📌 メモリ使用率の内訳：")
        for proc in mem_details:
            print(f"- {proc['name']}: {proc['mem']} MB")

def advise_process_details(thresholds: dict):
    print("\n🧐 高負荷プロセスの詳細情報（CPU使用率が高いもの）")
    cpu_threshold = thresholds.get("proc_cpu", 20)
    found = False

    for proc in psutil.process_iter(['pid', 'cpu_percent', 'memory_percent', 'create_time', 'username', 'ppid', 'cmdline']):
        try:
            cpu = proc.info['cpu_percent']
            if cpu is None or cpu < cpu_threshold:
                continue

            found = True
            mem = proc.info.get('memory_percent', 0.0)
            uptime_sec = time.time() - proc.info['create_time']
            uptime_str = str(datetime.timedelta(seconds=int(uptime_sec)))
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else '(不明)'

            print(f"- PID: {proc.info['pid']}, USER: {proc.info['username']}")
            print(f"  CPU: {cpu:.1f}%, MEM: {mem:.1f}%")
            print(f"  起動後: {uptime_str}, PPID: {proc.info['ppid']}")
            print(f"  CMD: {cmdline}\n")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not found:
        print("→ 現在、高負荷なプロセスは検出されていません。")

def advise_komon_update():
    def action():
        print("→ `git pull` でKomonを最新に保てます。改善が進んでいるかもしれません。")
    skippable_advice("komon_update", "Komonのコードがしばらく更新されていません。最新状態を確認しますか？", action)

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
        print("\n💡 複数日にわたってログが急増しているものがあります。")
        for log in suspicious_logs:
            print(f"   - {log}")
        print("→ `logrotate` 設定や出力レベルの見直しを検討しましょう。")

def run_advise():
    try:
        with open("settings.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ settings.yml の読み込みに失敗しました: {e}")
        return

    usage = collect_detailed_resource_usage()
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
    advise_resource_usage(usage, thresholds)
    advise_uptime(config.get("profile", {}))
    advise_email_disabled(config)
    advise_komon_update()
    advise_log_trend(config)
    advise_process_breakdown(usage)
    advise_process_details(thresholds)

def run():
    run_advise()

if __name__ == "__main__":
    run_advise()
