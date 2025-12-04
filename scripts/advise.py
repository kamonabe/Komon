import argparse
import datetime
import json
import os
import re
import subprocess
import time
import logging

import yaml
import psutil
from komon.analyzer import analyze_usage, load_thresholds
from komon.monitor import collect_detailed_resource_usage
from komon.log_trends import analyze_log_trend, detect_repeated_spikes
from komon.notification_history import load_notification_history, format_notification
from komon.duplicate_detector import detect_duplicate_processes
from komon.long_running_detector import detect_long_running_processes
from komon.os_detection import get_os_detector

SKIP_FILE = "data/komon_data/skip_advices.json"

logger = logging.getLogger(__name__)


def generate_progress_bar(percent: float, width: int = 10) -> str:
    """
    パーセンテージをプログレスバーに変換します。
    
    Args:
        percent: パーセンテージ（0-100）
        width: バーの幅（デフォルト: 10）
    
    Returns:
        プログレスバー文字列（例: "[████░░░░░░]"）
    """
    if percent < 0:
        percent = 0
    elif percent > 100:
        percent = 100
    
    filled = int(percent * width / 100)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}]"


def get_status_info(value: float, thresholds: dict) -> tuple:
    """
    値と閾値から状態情報を取得します。
    
    Args:
        value: 現在の値
        thresholds: 閾値辞書（warning, alert, critical）
    
    Returns:
        (アイコン, 状態名) のタプル
    """
    warning = thresholds.get("warning", 80)
    alert = thresholds.get("alert", 90)
    critical = thresholds.get("critical", 95)
    
    if value >= critical:
        return "🔥", "危険"
    elif value >= alert:
        return "⚠️", "警戒"
    elif value >= warning:
        return "⚠️", "警告"
    else:
        return "✅", "正常"

def display_system_status(usage: dict, thresholds: dict, verbose: bool = False):
    """
    現在のシステム状態を表示します。
    
    Args:
        usage: リソース使用状況
        thresholds: 閾値設定
        verbose: 詳細表示モード
    """
    print("📊 現在のシステム状態")
    
    # CPU
    cpu_value = usage.get("cpu", 0.0)
    cpu_thresholds = thresholds.get("cpu", {})
    if isinstance(cpu_thresholds, (int, float)):
        cpu_thresholds = {"warning": cpu_thresholds, "alert": 90, "critical": 95}
    cpu_icon, cpu_status = get_status_info(cpu_value, cpu_thresholds)
    cpu_bar = generate_progress_bar(cpu_value)
    cpu_warning = cpu_thresholds.get("warning", 80)
    print(f"CPU:     {cpu_bar} {cpu_value:.1f}% / {cpu_warning}% {cpu_icon}")
    
    # メモリ
    mem_value = usage.get("mem", 0.0)
    mem_thresholds = thresholds.get("mem", {})
    if isinstance(mem_thresholds, (int, float)):
        mem_thresholds = {"warning": mem_thresholds, "alert": 90, "critical": 95}
    mem_icon, mem_status = get_status_info(mem_value, mem_thresholds)
    mem_bar = generate_progress_bar(mem_value)
    mem_warning = mem_thresholds.get("warning", 80)
    print(f"メモリ:  {mem_bar} {mem_value:.1f}% / {mem_warning}% {mem_icon}")
    
    # ディスク
    disk_value = usage.get("disk", 0.0)
    disk_thresholds = thresholds.get("disk", {})
    if isinstance(disk_thresholds, (int, float)):
        disk_thresholds = {"warning": disk_thresholds, "alert": 90, "critical": 95}
    disk_icon, disk_status = get_status_info(disk_value, disk_thresholds)
    disk_bar = generate_progress_bar(disk_value)
    disk_warning = disk_thresholds.get("warning", 80)
    print(f"ディスク: {disk_bar} {disk_value:.1f}% / {disk_warning}% {disk_icon}")
    
    # 詳細表示モード: 警告時は上位プロセスも表示
    if verbose or cpu_value >= cpu_warning or mem_value >= mem_warning:
        print("\n📌 上位プロセス:")
        
        # CPU上位プロセス
        if cpu_value >= cpu_warning or verbose:
            cpu_details = usage.get("cpu_by_process", [])
            if cpu_details:
                print("  CPU:")
                for proc in cpu_details[:3]:
                    if proc['cpu'] > 0.0:  # 0.0%のプロセスは非表示
                        print(f"    - {proc['name']}: {proc['cpu']}%")
        
        # メモリ上位プロセス
        if mem_value >= mem_warning or verbose:
            mem_details = usage.get("mem_by_process", [])
            if mem_details:
                print("  メモリ:")
                for proc in mem_details[:3]:
                    if proc['mem'] > 0:  # 0MBのプロセスは非表示
                        print(f"    - {proc['name']}: {proc['mem']} MB")


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

def advise_os_update(config: dict = None):
    """
    OS別のパッケージ更新アドバイスを表示します。
    
    Args:
        config: 設定辞書
    """
    # OS判定
    detector = get_os_detector(config)
    os_family = detector.detect_os_family()
    
    # パッケージアドバイスを表示すべきか確認
    if not detector.should_show_package_advice():
        print("① パッケージ更新の確認")
        
        # unknown OSの場合は特別なメッセージ
        if os_family == 'unknown':
            print("→ OSファミリが不明なため、具体的なアドバイスを控えています。")
            print("   ご利用OSに応じたパッケージ管理コマンドで更新を確認してください。")
        else:
            # debian, suse, archなどの場合
            print(f"→ {os_family}系OSでは、パッケージ名の違いにより")
            print("   具体的なアドバイスを控えています。")
            print("   ご利用OSに応じたパッケージ管理コマンドで更新を確認してください。")
        
        # 汎用的なコマンド例を表示
        cmd = detector.get_package_manager_command()
        if cmd:
            print(f"\n💡 パッケージ更新コマンド例:")
            print(f"   {cmd}")
        return
    
    # RHEL系の場合は従来通りの詳細なアドバイス
    if os_family == 'rhel':
        try:
            sec_result = subprocess.run([
                "dnf", "updateinfo", "list", "security", "available"
            ], capture_output=True, text=True)
            sec_lines = sec_result.stdout.strip().splitlines()
            sec_updates = [line for line in sec_lines if re.match(r"^RHSA-\d{4}:", line)]

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
            print("→ dnf が見つかりません。RHEL系Linuxであることを確認してください。")
        except Exception as e:
            print(f"⚠ アップデート確認中にエラーが発生しました: {e}")
    
    # Debian系の場合はシンプルなアドバイス
    elif os_family == 'debian':
        try:
            print("① パッケージ更新の確認")
            print("→ Debian系Linuxでは以下のコマンドで更新を確認できます：")
            print("   sudo apt update")
            print("   sudo apt list --upgradable")
            
            if ask_yes_no("\nパッケージ更新を実行しますか？"):
                print("\n→ パッケージ更新を実行します...")
                subprocess.run(["sudo", "apt", "update"])
                subprocess.run(["sudo", "apt", "upgrade", "-y"])
                print("→ パッケージ更新が完了しました。再起動が必要な場合があります。")
            else:
                print("→ パッケージ更新は保留されました。")
                print("\n💡 手動で更新する場合は以下のコマンドを実行してください：")
                print("   sudo apt update && sudo apt upgrade -y")
        
        except FileNotFoundError:
            print("→ apt が見つかりません。Debian系Linuxであることを確認してください。")
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


def advise_long_running_processes(config):
    """
    長時間実行プロセスの警告を表示します。
    """
    print("\n⏱️  長時間実行プロセスの検出")
    
    # 設定から閾値と対象拡張子を取得
    long_running_config = config.get("long_running_detection", {})
    threshold_seconds = long_running_config.get("threshold_seconds", 3600)
    target_extensions = long_running_config.get("target_extensions", ['.py', '.sh', '.rb', '.pl'])
    enabled = long_running_config.get("enabled", True)
    
    if not enabled:
        print("→ 長時間実行プロセスの検出は無効化されています。")
        return
    
    try:
        long_running = detect_long_running_processes(
            threshold_seconds=threshold_seconds,
            target_extensions=target_extensions
        )
        
        if not long_running:
            print("→ 長時間実行プロセスは検出されませんでした。")
            return
        
        print("⚠️ 以下のスクリプトが長時間実行されています：\n")
        
        for proc in long_running:
            script = proc['script']
            pid = proc['pid']
            runtime_formatted = proc['runtime_formatted']
            
            print(f"  • {script} (PID: {pid})")
            print(f"    実行時間: {runtime_formatted}\n")
        
        print("【推奨対応】")
        print("  - スクリプトが正常に動作しているか確認してください")
        print("  - cron間隔がスクリプトの実行時間より短い場合は見直してください")
        print("  - 必要に応じてプロセスを停止してください")
    
    except Exception as e:
        logger.error("Failed to detect long-running processes: %s", e, exc_info=True)
        print(f"⚠️ 長時間実行プロセスの検出に失敗しました: {e}")


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


def run_advise(history_limit: int = None, verbose: bool = False, section: str = None):
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
    
    # 設定ファイルからデフォルト値を取得
    output_config = config.get("output", {})
    if history_limit is None:
        history_limit = output_config.get("history_limit", 5)
    
    # セクション指定がある場合は該当セクションのみ表示
    if section:
        if section == "status":
            display_system_status(usage, thresholds, verbose)
            return
        elif section == "alerts":
            print("🔔 警戒情報")
            if alerts:
                for alert in alerts:
                    print(f"- {alert}")
            else:
                print("（なし）")
            return
        elif section == "advice":
            print("💡 改善提案")
            advise_os_update(config)
            advise_resource_usage(usage, thresholds)
            advise_uptime(config.get("profile", {}))
            advise_email_disabled(config)
            advise_komon_update()
            return
        elif section == "log":
            advise_log_trend(config)
            return
        elif section == "disk":
            advise_disk_prediction()
            return
        elif section == "process":
            advise_duplicate_processes(config)
            advise_long_running_processes(config)
            if verbose:
                advise_process_breakdown(usage)
            advise_process_details(thresholds, config)
            return
        elif section == "history":
            advise_notification_history(limit=history_limit)
            return
        else:
            print(f"❌ 不明なセクション: {section}")
            print("利用可能なセクション: status, alerts, advice, log, disk, process, history")
            sys.exit(1)
    
    # 全セクション表示（デフォルト）
    # 1. システム状態を最初に表示
    display_system_status(usage, thresholds, verbose)
    
    # 2. 警戒情報
    print("\n🔔 警戒情報")
    if alerts:
        for alert in alerts:
            print(f"- {alert}")
    else:
        print("（なし）")

    # 3. 改善提案
    print("\n💡 改善提案")
    advise_os_update(config)
    if not verbose:
        # 通常モードではリソース使用率の対話的な質問をスキップ
        pass
    else:
        advise_resource_usage(usage, thresholds)
    advise_uptime(config.get("profile", {}))
    advise_email_disabled(config)
    advise_komon_update()
    
    # 4. ログ傾向分析
    if verbose:
        advise_log_trend(config)
    
    # 5. ディスク使用量の予測
    if verbose:
        advise_disk_prediction()
    
    # 6. プロセス関連
    advise_duplicate_processes(config)
    advise_long_running_processes(config)
    if verbose:
        advise_process_breakdown(usage)
        advise_process_details(thresholds, config)
    
    # 7. 通知履歴を表示
    advise_notification_history(limit=history_limit)
    
    # フッター
    if not verbose:
        print("\n詳細: komon advise --verbose")


def run():
    parser = argparse.ArgumentParser(description="Komonの助言を表示します")
    parser.add_argument(
        "--history",
        type=int,
        metavar="N",
        default=None,
        help="通知履歴の表示件数（デフォルト: 設定ファイルの値、0で全件表示）"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="詳細表示モード（全ての情報を表示）"
    )
    parser.add_argument(
        "--section",
        type=str,
        choices=["status", "alerts", "advice", "log", "disk", "process", "history"],
        help="特定のセクションのみ表示"
    )
    args = parser.parse_args()
    
    # 0が指定された場合は全件表示（Noneを渡す）
    history_limit = None if args.history == 0 else args.history
    run_advise(history_limit=history_limit, verbose=args.verbose, section=args.section)


if __name__ == "__main__":
    run()
