# main.py

from komon.monitor import collect_resource_usage
from komon.analyzer import load_thresholds, analyze_usage
from komon.history import rotate_history, save_current_usage

def main():
    usage = collect_resource_usage()
    thresholds = load_thresholds()
    alerts = analyze_usage(usage, thresholds)

    print("🧠 Komon Resource Report")
    for k, v in usage.items():
        print(f"  {k.upper()}: {v:.1f}%")

    if alerts:
        print("\n⚠️ 警戒情報あり")
        for k, v in alerts.items():
            print(f"  🚨 {k.upper()} 使用率が高すぎます: {v:.1f}%")
    else:
        print("\n✅ 問題なし：使用率はしきい値以下です")

    # === 履歴のローテーションと保存 ===
    rotate_history(max_generations=95)
    save_current_usage(usage)

if __name__ == "__main__":
    main()
