import yaml
from komon.log_watcher import LogWatcher
from komon.log_analyzer import check_log_anomaly
from komon.notification import send_slack_alert, send_email_alert, send_discord_alert, send_teams_alert, send_notification_with_fallback
from komon.log_tail_extractor import extract_log_tail


def main():
    import sys
    
    # 設定ファイルの読み込み
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

    # ログ監視と差分行数取得
    watcher = LogWatcher()
    diff_results = watcher.watch_logs()  # {'/var/log/messages': 50, ...}

    # ログ末尾抜粋の設定を取得
    log_analysis_cfg = config.get("log_analysis", {})
    tail_lines = log_analysis_cfg.get("tail_lines", 10)
    max_line_length = log_analysis_cfg.get("max_line_length", 500)

    alerts = []
    alert_details = []  # (alert, log_path, tail_lines)のタプルリスト
    
    for path, line_count in diff_results.items():
        alert = check_log_anomaly(path, line_count, config)
        if alert:
            print(f"⚠️ {alert}")
            alerts.append(alert)
            
            # ログ末尾を抽出（設定で有効な場合）
            tail_content = []
            if tail_lines > 0:
                try:
                    tail_content = extract_log_tail(path, tail_lines, max_line_length)
                except Exception as e:
                    print(f"⚠️ ログ末尾の抽出に失敗: {e}")
                    # エラーでも通知は継続
            
            alert_details.append((alert, path, tail_content))

    # 警戒がある場合は通知
    if alerts:
        # メッセージを作成
        message_parts = ["⚠️ Komon ログ警戒情報:"]
        
        for alert, log_path, tail_content in alert_details:
            message_parts.append(f"\n- {alert}")
            
            # 末尾抜粋を追加
            if tail_content:
                message_parts.append(f"\n📄 ログファイル: {log_path}")
                message_parts.append(f"📋 末尾 {len(tail_content)} 行:")
                message_parts.append("```")
                message_parts.extend(tail_content)
                message_parts.append("```")
        
        message = "\n".join(message_parts)
        
        notification_cfg = config.get("notifications", {})
        
        # ログ監視のメタデータ
        total_lines = sum(diff_results.values())
        metadata = {
            "metric_type": "log",
            "metric_value": float(total_lines)
        }

        # 統一Webhook通知（新形式 + フォールバック）
        send_notification_with_fallback(
            message=message,
            settings=config,
            metadata=metadata,
            title="Komon ログ異常検知",
            level="warning"
        )

    else:
        print("✅ ログに異常はありません。")


if __name__ == "__main__":
    main()
