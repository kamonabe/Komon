from komon.analyzer import analyze_usage, load_thresholds
from komon.monitor import get_resource_usage
import yaml

def run_advise():
    # 設定ファイルの読み込み
    with open("settings.yml") as f:
        config = yaml.safe_load(f)

    # 現在のリソース使用状況を取得
    usage = get_resource_usage()

    # 閾値を元にアラートを判定
    thresholds = load_thresholds(config)
    alerts = analyze_usage(usage, thresholds)

    # 表示部（CLI出力）
    print("🔔 警戒情報")
    if alerts:
        for alert in alerts:
            print(f"- {alert}")
    else:
        print("（なし）")

    print("\n💡 改善提案")
    print("- OSやパッケージの更新確認をおすすめします（将来的に自動提案予定）")

if __name__ == "__main__":
    run_advise()
