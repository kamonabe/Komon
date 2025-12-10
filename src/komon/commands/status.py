"""
Status command implementation

システムステータス表示コマンドの実装を提供します。
"""

import yaml
from pathlib import Path
from komon.monitor import collect_resource_usage
from komon.analyzer import load_thresholds


def load_config(config_dir: Path):
    """設定ファイルを読み込む"""
    config_file = config_dir / "settings.yml"
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ settings.yml が見つかりません")
        print("")
        print("初回セットアップを実行してください：")
        print("  komon initial")
        print("")
        print("または、サンプルファイルをコピー：")
        print("  cp config/settings.yml.sample settings.yml")
        raise SystemExit(1)
    except yaml.YAMLError as e:
        print(f"❌ settings.yml の形式が不正です: {e}")
        print("")
        print("config/settings.yml.sampleを参考に修正してください")
        raise SystemExit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        raise SystemExit(1)


def run_status(config_dir: Path):
    """
    ステータス表示のメイン実行関数
    
    Args:
        config_dir: 設定ディレクトリのパス
    """
    print("📊 Komon ステータス")

    config = load_config(config_dir)
    usage = collect_resource_usage()
    thresholds = load_thresholds(config)

    print("\n【リソース使用率】")
    for key in ["cpu", "mem", "disk"]:
        val = usage.get(key)
        th = thresholds.get(key)
        print(f" - {key.upper()}: {val:.1f}%（閾値: {th}％）")

    print("\n【通知設定】")
    notifications = config.get("notifications", {})
    slack = notifications.get("slack", {}).get("enabled", False)
    email = notifications.get("email", {}).get("enabled", False)
    print(f" - Slack通知: {'有効' if slack else '無効'}")
    print(f" - メール通知: {'有効' if email else '無効'}")

    print("\n【ログ監視対象】")
    logs = config.get("log_monitor_targets", {})
    if not logs:
        print(" - 監視対象なし")
    for log, enabled in logs.items():
        print(f" - {log}: {'✅ 有効' if enabled else '❌ 無効'}")