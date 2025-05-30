import yaml
from komon.analyzer import analyze_usage, load_thresholds
from komon.monitor import get_resource_usage


def run_advise():
    try:
        # 設定ファイルの読み込み
        with open("settings.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ settings.yml の読み込みに失敗しました: {e}")
        return

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
    # 今後ここにAI的なアドバイスも含める予定
    suggestions = [
        "- OSやパッケージの更新確認をおすすめします（将来的に自動提案予定）",
        "- 長時間稼働中のプロセスがあれば、不要なものを見直してみましょう（今後自動分析予定）"
    ]
    for s in suggestions:
        print(s)


if __name__ == "__main__":
    run_advise()
