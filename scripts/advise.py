import argparse
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
from komon.notification_history import load_notification_history, format_notification
from komon.duplicate_detector import detect_duplicate_processes

SKIP_FILE = "data/komon_data/skip_advices.json"

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
    # 3段階閾値形式に対応（warning値を使用）
    mem_threshold = thresholds.get("mem", {}).get("warning", 80) if isinstance(thresholds.get("mem"), dict) else thresholds.get("mem", 80)
    disk_threshold = thresholds.get("disk", {}).get("warning", 80) if isinstance(thresholds.get("disk"), dict) else thresholds.get("disk", 80)
    cpu_threshold = thresholds.get("cpu", {}).get("warning", 85) if isinstance(thresholds.get("cpu"), dict) else thresholds.get("cpu", 85)
    
    if usage.get("mem", 0) >= mem_threshold:
        if ask_yes_no(f"\nMEM使用率が{usage['mem']}%と高めです。多く使っているプロセスを調べますか？"):
            print("→ 上位メモリ使用プロセスを表示します。\n")
            try:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'username', 'cmdline']):
                    processes.append(proc.info)
                processes.sort(key=lambda p: p['memory_percent'], reverse=True)
                for proc in processes[:5]:
                    mem = f"{proc['memory_percent']:.1f}%"
                    name = proc.get('name', '(不明)')
                    user = proc.get('username', '(不明)')
                    pid = proc.get('pid', '-')
                    cmd = ' '.join(proc.get('cmdline', [])) if proc.get('cmdline') else '(不明)'
                    print(f"- PID: {pid}, USER: {user}")
                    print(f"  MEM: {mem}, NAME: {name}")
                    print(f"  CMD: {cmd}\n")
            except Exception as e:
                print(f"⚠ プロセス情報の取得中にエラーが発生しました: {e}")

    if usage.get("disk", 0) >= disk_threshold:
        if ask_yes_no(f"ディスク使用率が{usage['disk']}%と高めです。不要なファイルを整理しますか？"):
            print("→ `du -sh *` や `journalctl --vacuum-time=7d` を活用しましょう。")

    if usage.get("cpu", 0) >= cpu_threshold:
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

def advise_process_details(thresholds: dict, config: dict = None):
    """
    高負荷プロセスの詳細情報を表示します。
    
    contextual_adviceが有効な場合は、コンテキスト型アドバイスを表示します。
    無効な場合は、従来のプロセス情報のみを表示します。
    """
    # contextual_adviceの設定を確認
    contextual_config = config.get("contextual_advice", {}) if config else {}
    contextual_enabled = contextual_config.get("enabled", False)
    
    print("\n🧐 高負荷プロセスの詳細情報（CPU使用率が高いもの）")
    
    # contextual_adviceが有効な場合
    if contextual_enabled:
        try:
            from komon.contextual_advisor import get_contextual_advice
            
            # CPU使用率でコンテキストアドバイスを取得
            result = get_contextual_advice("cpu", config, contextual_config.get("advice_level", "normal"))
            
            if result["top_processes"]:
                print(result["formatted_message"])
            else:
                print("→ 現在、高負荷なプロセスは検出されていません。")
            return
            
        except Exception as e:
            logger.error("Failed to get contextual advice: %s", e, exc_info=True)
            print(f"⚠️ コンテキストアドバイスの取得に失敗しました: {e}")
            # フォールバック: 従来の表示に切り替え
    
    # contextual_adviceが無効な場合、または取得失敗時
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

def advise_duplicate_processes(config):
    """
    多重実行プロセスの警告を表示します。
    """
    print("\n🔄 多重実行プロセスの検出")
    
    # 設定から閾値を取得
    threshold = config.get("duplicate_process_detection", {}).get("threshold", 3)
    enabled = config.get("duplicate_process_detection", {}).get("enabled", True)
    
    if not enabled:
        print("→ 多重実行プロセスの検出は無効化されています。")
        return
    
    try:
        duplicates = detect_duplicate_processes(threshold=threshold)
        
        if not duplicates:
            print("→ 多重実行プロセスは検出されませんでした。")
            return
        
        print("⚠️ 以下のスクリプトが複数同時実行されています：\n")
        
        for dup in duplicates:
            script = dup['script']
            count = dup['count']
            pids = dup['pids']
            
            # PIDリストを整形（最大5個まで表示）
            if len(pids) <= 5:
                pid_str = ', '.join(map(str, pids))
            else:
                pid_str = ', '.join(map(str, pids[:5])) + f', ... (他{len(pids)-5}個)'
            
            print(f"  • {script}: {count}個のプロセス")
            print(f"    PID: {pid_str}\n")
        
        print("【推奨対応】")
        print("  - cron間隔を見直してください")
        print("  - スクリプトの実行時間を短縮してください")
        print("  - ロックファイルで多重実行を防止してください")
    
    except Exception as e:
        logger.error("Failed to detect duplicate processes: %s", e, exc_info=True)
        print(f"⚠️ 多重実行プロセスの検出に失敗しました: {e}")


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

def advise_disk_prediction():
    """
    ディスク使用量の予測結果を表示します。
    """
    print("\n📊 ディスク使用量の予測")
    try:
        from komon.disk_predictor import (
            load_disk_history,
            calculate_daily_average,
            predict_disk_trend,
            detect_rapid_change,
            format_prediction_message
        )
        
        # データ読み込み
        history = load_disk_history(days=7)
        if len(history) < 2:
            print("→ データが不足しています。7日分のデータが必要です。")
            return
        
        # 日次平均を計算
        daily_data = calculate_daily_average(history)
        
        # 予測計算
        prediction = predict_disk_trend(daily_data)
        rapid_change = detect_rapid_change(daily_data)
        
        # メッセージ生成と表示
        message = format_prediction_message(prediction, rapid_change)
        print(message)
        
    except Exception as e:
        print(f"⚠️ 予測計算中にエラーが発生しました: {e}")


def advise_notification_history(limit: int = None):
    """
    通知履歴を表示します。
    
    Args:
        limit: 表示する最大件数（Noneの場合は全件）
    """
    print("\n📜 通知履歴")
    try:
        history = load_notification_history(limit=limit)
        if not history:
            print("→ 通知履歴はありません。")
            return
        
        for notification in history:
            print(format_notification(notification))
    except Exception as e:
        print(f"⚠️ 通知履歴の読み込みに失敗: {e}")


def run_advise(history_limit: int = None):
    import sys
    
    try:
        with open("settings.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ settings.yml が見つかりません")
        print("")
        print("初回セットアップを実行してください：")
        print("  python scripts/initial.py")
        print("")
        print("または、サンプルファイルをコピー：")
        print("  cp config/settings.yml.sample settings.yml")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ settings.yml の形式が不正です: {e}")
        print("")
        print("config/settings.yml.sampleを参考に修正してください")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)

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
    advise_disk_prediction()  # ディスク使用量の予測を追加
    advise_duplicate_processes(config)  # 多重実行プロセスの検出を追加
    advise_process_breakdown(usage)
    advise_process_details(thresholds, config)
    
    # 通知履歴を表示
    advise_notification_history(limit=history_limit)


def run():
    parser = argparse.ArgumentParser(description="Komonの助言を表示します")
    parser.add_argument(
        "--history",
        type=int,
        metavar="N",
        default=10,
        help="通知履歴の表示件数（デフォルト: 10件、0で全件表示）"
    )
    args = parser.parse_args()
    
    # 0が指定された場合は全件表示（Noneを渡す）
    history_limit = None if args.history == 0 else args.history
    run_advise(history_limit=history_limit)


if __name__ == "__main__":
    run()
