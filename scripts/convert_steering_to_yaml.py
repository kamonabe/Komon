#!/usr/bin/env python3
"""
ステアリングルールをYAML形式に変換するスクリプト

使い方:
    python scripts/convert_steering_to_yaml.py
"""

import yaml
from pathlib import Path


def convert_steering_rules():
    """ステアリングルールをYAML化"""
    
    steering_rules = {
        'versioning-rules': {
            'priority': 'high',
            'applies-to': ['release', 'versioning', 'changelog'],
            'triggers': ['implementation-complete', 'changelog-update'],
            'description': 'Semantic Versioningに基づくバージョン番号の決定ルール'
        },
        'development-workflow': {
            'priority': 'high',
            'applies-to': ['implementation', 'spec-creation', 'task-management'],
            'triggers': ['task-start', 'spec-creation', 'implementation-start'],
            'description': '仕様駆動開発のワークフロー'
        },
        'task-management': {
            'priority': 'medium',
            'applies-to': ['task-management'],
            'triggers': ['task-complete', 'task-update'],
            'description': 'タスク管理の2階層構造ルール'
        },
        'spec-quality-assurance': {
            'priority': 'high',
            'applies-to': ['spec-creation', 'implementation-start'],
            'triggers': ['spec-complete', 'implementation-start'],
            'description': 'Spec品質保証と検証スクリプト実行ルール'
        },
        'error-handling-and-logging': {
            'priority': 'medium',
            'applies-to': ['implementation', 'error-handling'],
            'triggers': ['code-implementation'],
            'description': 'エラーハンドリングとログ出力の標準'
        },
        'environment-and-communication': {
            'priority': 'high',
            'applies-to': ['all'],
            'triggers': ['always'],
            'description': '開発環境とコミュニケーション言語のルール'
        },
        'commit-message-rules': {
            'priority': 'low',
            'applies-to': ['commit'],
            'triggers': ['commit-creation'],
            'description': 'Conventional Commits形式のコミットメッセージルール'
        }
    }
    
    # メタデータファイルを作成
    metadata_path = Path('.kiro/steering/rules-metadata.yml')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump({
            'version': '1.0.0',
            'updated': '2025-11-26',
            'description': 'Kiroが処理するステアリングルールのメタデータ',
            'rules': steering_rules
        }, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print(f"✅ {metadata_path} 作成")
    
    # 各ルールファイルにFront Matterを追加
    steering_dir = Path('.kiro/steering')
    for rule_name, metadata in steering_rules.items():
        rule_file = steering_dir / f'{rule_name}.md'
        if not rule_file.exists():
            continue
        
        content = rule_file.read_text(encoding='utf-8')
        
        # 既存のFront Matterを削除
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # 新しいFront Matterを追加
        front_matter = {
            'rule-id': rule_name,
            'priority': metadata['priority'],
            'applies-to': metadata['applies-to'],
            'triggers': metadata['triggers'],
            'description': metadata['description']
        }
        
        new_content = '---\n'
        new_content += yaml.dump(front_matter, allow_unicode=True, sort_keys=False, default_flow_style=False)
        new_content += '---\n\n'
        new_content += content
        
        rule_file.write_text(new_content, encoding='utf-8')
        print(f"✅ {rule_file.name} にFront Matter追加")


def main():
    """メイン処理"""
    print("📦 ステアリングルールYAML変換スクリプト")
    print("=" * 60)
    
    convert_steering_rules()
    
    print("\n" + "=" * 60)
    print("✅ 変換完了！")
    print("\n次のステップ:")
    print("1. .kiro/steering/rules-metadata.yml を確認")
    print("2. 各ルールファイルのFront Matterを確認")
    print("3. git add .kiro/steering/")


if __name__ == '__main__':
    main()
