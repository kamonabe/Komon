#!/usr/bin/env python3
"""
ステアリングルール生成スクリプト

テンプレートとproject-config.ymlから、プロジェクト固有のステアリングルールを生成します。
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


def generate_steering_rules(config: dict, output_dir: str = ".kiro/steering"):
    """テンプレートからステアリングルールを生成"""
    
    template_dir = Path(".kiro/steering/_templates")
    if not template_dir.exists():
        print(f"❌ テンプレートディレクトリが見つかりません: {template_dir}")
        sys.exit(1)
    
    # ルールメタデータを読み込み
    metadata_path = template_dir / "rule-metadata.yml"
    if not metadata_path.exists():
        print(f"❌ ルールメタデータが見つかりません: {metadata_path}")
        sys.exit(1)
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata_config = yaml.safe_load(f)
    
    rule_metadata = metadata_config.get('rules', {})
    
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
    
    # テンプレートファイルを取得
    templates = list(template_dir.glob("*.template.md"))
    
    if not templates:
        print(f"⚠️ テンプレートファイルが見つかりません: {template_dir}")
        return
    
    print(f"📝 {len(templates)}個のテンプレートを処理します...\n")
    
    # 各テンプレートを処理
    for template_path in sorted(templates):
        template_name = template_path.name
        
        try:
            # テンプレートを読み込み
            template = env.get_template(template_name)
            
            # レンダリング
            content = template.render(**config)
            
            # 出力ファイル名（.template を削除）
            output_name = template_name.replace('.template', '')
            rule_id = output_name.replace('.md', '')
            output_path = Path(output_dir) / output_name
            
            # Front Matterを追加
            metadata = rule_metadata.get(rule_id, {})
            if metadata:
                front_matter = {
                    'rule-id': rule_id,
                    'priority': metadata.get('priority', 'medium'),
                    'applies-to': metadata.get('applies-to', []),
                    'triggers': metadata.get('triggers', []),
                    'description': metadata.get('description', '')
                }
                
                output = '---\n'
                output += yaml.dump(front_matter, allow_unicode=True, sort_keys=False, default_flow_style=False)
                output += '---\n\n'
                output += content
            else:
                output = content
            
            # ファイルに書き込み
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            
            print(f"✅ Generated: {output_name} (with Front Matter)")
            
        except Exception as e:
            print(f"❌ Error processing {template_name}: {e}")
            sys.exit(1)
    
    print(f"\n🎉 全てのステアリングルールを生成しました！")
    print(f"   出力先: {output_dir}/")


def main():
    """メイン処理"""
    print("=" * 60)
    print("Komon Steering Rules Generator")
    print("=" * 60)
    print()
    
    # プロジェクト設定を読み込み
    print("📖 プロジェクト設定を読み込んでいます...")
    config = load_project_config()
    print(f"   プロジェクト: {config['project']['name']}")
    print(f"   タイプ: {config['project']['type']}")
    print(f"   言語: {config['project']['language']}")
    print()
    
    # ステアリングルールを生成
    generate_steering_rules(config)


if __name__ == '__main__':
    main()
