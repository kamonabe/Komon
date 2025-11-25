#!/usr/bin/env python3
"""
タスクテンプレート生成スクリプト

テンプレートとproject-config.ymlから、プロジェクト固有のタスク管理ファイルを生成します。
"""

import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import sys


def load_project_config(config_path: str = ".kiro/steering/project-config.yml") -> dict:
    """プロジェクト設定を読み込む"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ 設定ファイルが見つかりません: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ YAML解析エラー: {e}")
        sys.exit(1)


def generate_task_template(config: dict, output_path: str = ".kiro/tasks/implementation-tasks.md"):
    """テンプレートからタスク管理ファイルを生成"""
    
    template_dir = Path(".kiro/tasks/_templates")
    if not template_dir.exists():
        print(f"❌ テンプレートディレクトリが見つかりません: {template_dir}")
        sys.exit(1)
    
    template_file = template_dir / "implementation-tasks.template.md"
    if not template_file.exists():
        print(f"❌ テンプレートファイルが見つかりません: {template_file}")
        sys.exit(1)
    
    # Jinja2環境の設定
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # カスタムフィルターを追加
    def basename_filter(path):
        """パスからファイル名を取得"""
        return Path(path).name
    
    env.filters['basename'] = basename_filter
    
    try:
        # テンプレートを読み込み
        template = env.get_template("implementation-tasks.template.md")
        
        # レンダリング
        output = template.render(**config)
        
        # ファイルに書き込み
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"✅ Generated: {output_file}")
        
    except Exception as e:
        print(f"❌ Error processing template: {e}")
        sys.exit(1)


def main():
    """メイン処理"""
    print("=" * 60)
    print("Komon Task Template Generator")
    print("=" * 60)
    print()
    
    # プロジェクト設定を読み込み
    print("📖 プロジェクト設定を読み込んでいます...")
    config = load_project_config()
    print(f"   プロジェクト: {config['project']['name']}")
    print(f"   タイプ: {config['project']['type']}")
    print(f"   言語: {config['project']['language']}")
    print()
    
    # 確認メッセージ
    print("⚠️  注意: このスクリプトは既存の implementation-tasks.md を上書きします。")
    print("   既存のタスク内容は失われます。")
    print()
    response = input("続行しますか？ (y/N): ")
    
    if response.lower() != 'y':
        print("❌ キャンセルしました。")
        sys.exit(0)
    
    # タスクテンプレートを生成
    print("\n📝 タスクテンプレートを生成しています...")
    generate_task_template(config)
    
    print("\n🎉 タスクテンプレートを生成しました！")
    print("   出力先: .kiro/tasks/implementation-tasks.md")
    print()
    print("💡 ヒント: 実際のタスク（TASK-XXX）は手動で追加してください。")


if __name__ == '__main__':
    main()

