"""
Initial setup command implementation

初期セットアップコマンドの実装を提供します。
"""

import os
import yaml
from pathlib import Path
import komon


def get_input(prompt, default, value_type="str"):
    """
    ユーザー入力を取得する
    
    Args:
        prompt: 表示するプロンプト
        default: デフォルト値
        value_type: 値の型（"str", "int", "bool"）
    
    Returns:
        ユーザー入力またはデフォルト値
    """
    # デフォルト値を文字列化
    default_str = str(default)
    
    # プロンプト表示
    user_input = input(f"  {prompt}: {default_str} [Enter=そのまま / 値入力=変更] > ").strip()
    
    # 空入力の場合はデフォルト値
    if user_input == "":
        print(f"  → {default_str} のまま（デフォルト）")
        return default
    
    # 型変換
    try:
        if value_type == "int":
            result = int(user_input)
            print(f"  → {result} に設定しました")
            return result
        elif value_type == "bool":
            result = user_input.lower() in ["true", "yes", "y", "1"]
            print(f"  → {result} に設定しました")
            return result
        else:  # str
            print(f"  → {user_input} に設定しました")
            return user_input
    except ValueError:
        print(f"  ⚠ 入力形式が正しくありません。デフォルト値 {default_str} を使用します。")
        return default


def run_initial_setup(config_dir: Path):
    """
    初期セットアップのメイン実行関数
    
    Args:
        config_dir: 設定ディレクトリのパス
    """
    print("🔧 Komon 初期設定を開始します...\n")

    # 設定ファイルのパス
    settings_file = config_dir / "settings.yml"
    
    # 既存ファイルがあればスキップ
    if settings_file.exists():
        print("⚠ settings.yml はすでに存在します。初期設定はスキップされました。")
        return

    # config/settings.yml.sample を読み込む
    # 開発環境とインストール環境の両方に対応
    
    # komonパッケージの実際のインストール場所を動的に検出
    komon_package_path = Path(komon.__file__).parent
    
    sample_paths = [
        Path("config/settings.yml.sample"),  # 開発環境
        komon_package_path.parent / "config" / "settings.yml.sample",  # インストール環境（動的検出）
    ]
    
    sample_path = None
    for path in sample_paths:
        if path.exists():
            sample_path = path
            break
    
    if sample_path is None:
        print("❌ settings.yml.sample が見つかりません。")
        print("   以下の場所を確認してください：")
        for path in sample_paths:
            print(f"   - {path}")
        return

    with open(sample_path, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)

    print(f"📋 {sample_path} から設定を読み込みました。")
    print("   各項目を確認します。変更しない場合はEnterを押してください。\n")

    # 1. リソース使用率の閾値設定
    print("📊 リソース使用率の閾値設定：")
    print("  ℹ️  3段階閾値（warning/alert/critical）はそのまま使用します")
    print("  ℹ️  詳細な調整は settings.yml で編集してください")
    print()

    # 2. Slack通知設定
    print("🔔 Slack通知設定：")
    settings["notifications"]["slack"]["enabled"] = get_input(
        "有効化",
        settings["notifications"]["slack"]["enabled"],
        "bool"
    )
    if settings["notifications"]["slack"]["enabled"]:
        settings["notifications"]["slack"]["webhook_url"] = get_input(
            "Webhook URL",
            settings["notifications"]["slack"]["webhook_url"],
            "str"
        )
    print()

    # 3. メール通知設定
    print("📧 メール通知設定：")
    settings["notifications"]["email"]["enabled"] = get_input(
        "有効化",
        settings["notifications"]["email"]["enabled"],
        "bool"
    )
    if settings["notifications"]["email"]["enabled"]:
        settings["notifications"]["email"]["smtp_server"] = get_input(
            "SMTPサーバー",
            settings["notifications"]["email"]["smtp_server"],
            "str"
        )
        settings["notifications"]["email"]["smtp_port"] = get_input(
            "SMTPポート",
            settings["notifications"]["email"]["smtp_port"],
            "int"
        )
        settings["notifications"]["email"]["from"] = get_input(
            "送信元アドレス",
            settings["notifications"]["email"]["from"],
            "str"
        )
        settings["notifications"]["email"]["to"] = get_input(
            "送信先アドレス",
            settings["notifications"]["email"]["to"],
            "str"
        )
    print()

    # 4. ネットワークチェック設定
    if "network_check" in settings:
        print("🌐 ネットワークチェック設定：")
        settings["network_check"]["enabled"] = get_input(
            "有効化",
            settings["network_check"]["enabled"],
            "bool"
        )
        if settings["network_check"]["enabled"]:
            print("  ℹ️  詳細設定（監視対象URL等）は settings.yml で編集できます")
        print()

    # 5. 通知スパム防止設定
    if "throttle" in settings:
        print("🚦 通知スパム防止設定：")
        settings["throttle"]["enabled"] = get_input(
            "有効化",
            settings["throttle"]["enabled"],
            "bool"
        )
        print()

    # 6. 段階的通知メッセージ設定
    if "progressive_notification" in settings:
        print("📢 段階的通知メッセージ設定：")
        settings["progressive_notification"]["enabled"] = get_input(
            "有効化",
            settings["progressive_notification"]["enabled"],
            "bool"
        )
        print()

    # 7. コンテキストアドバイス設定
    if "contextual_advice" in settings:
        print("💡 コンテキストアドバイス設定：")
        settings["contextual_advice"]["enabled"] = get_input(
            "有効化",
            settings["contextual_advice"]["enabled"],
            "bool"
        )
        print()

    # 設定ディレクトリを作成
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # settings.yml を作成
    with open(settings_file, "w", encoding="utf-8") as f:
        yaml.dump(settings, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"✅ {settings_file} を作成しました！\n")
    print("🎯 次のステップ：")
    print("  → komon advise を実行してみましょう！")
    print("  → cron登録もおすすめです。\n")
    print("📁 補足：")
    print(f"  詳細な設定は {settings_file} を直接編集してください。")