#!/usr/bin/env python3
"""
Specテンプレート生成スクリプト

YAMLテンプレートから新しいSpec機能を作成します。

使い方:
    python scripts/generate_spec_templates.py <feature-name>
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime


def create_spec_from_templates(feature_name: str):
    """テンプレートから新しいSpecを作成"""
    
    # 出力ディレクトリ
    spec_dir = Path(f".kiro/specs/{feature_name}")
    if spec_dir.exists():
        print(f"❌ Specディレクトリが既に存在します: {spec_dir}")
        sys.exit(1)
    
    spec_dir.mkdir(parents=True)
    print(f"📁 ディレクトリ作成: {spec_dir}")
    
    # テンプレートディレクトリ
    template_dir = Path(".kiro/specs/_templates")
    
    # 現在の日付
    today = datetime.now().strftime("%Y-%m-%d")
    
    # requirements.yml
    req_template = {
        'metadata': {
            'title': f'{feature_name} - 要件定義',
            'feature': feature_name,
            'status': 'draft',
            'created': today,
            'updated': today,
            'complexity': 'medium',
            'estimated-hours': 8,
            'dependencies': []
        },
        'overview': {
            'description': '（機能の概要を記述）'
        },
        'acceptance-criteria': [
            {
                'id': 'AC-001',
                'title': '基準名',
                'priority': 'high',
                'type': 'functional',
                'user-story': 'ユーザーストーリーを記述',
                'conditions': [
                    {
                        'when': '条件',
                        'then': '期待される結果'
                    }
                ]
            }
        ]
    }
    
    req_path = spec_dir / 'requirements.yml'
    with open(req_path, 'w', encoding='utf-8') as f:
        yaml.dump(req_template, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"✅ 作成: requirements.yml")
    
    # design.yml
    design_template = {
        'metadata': {
            'title': f'{feature_name} - 設計書',
            'feature': feature_name,
            'status': 'draft',
            'created': today,
            'updated': today
        },
        'correctness-properties': [
            {
                'id': 'P1',
                'title': 'プロパティ名',
                'type': 'invariant',
                'description': 'プロパティの説明',
                'validates': ['AC-001'],
                'test-strategy': 'property-based'
            }
        ]
    }
    
    design_path = spec_dir / 'design.yml'
    with open(design_path, 'w', encoding='utf-8') as f:
        yaml.dump(design_template, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"✅ 作成: design.yml")
    
    # tasks.yml
    tasks_template = {
        'metadata': {
            'title': f'{feature_name} - 実装タスク',
            'feature': feature_name,
            'status': 'draft',
            'created': today,
            'updated': today
        },
        'tasks': [
            {
                'id': 'T1',
                'title': 'Create module',
                'status': 'todo',
                'priority': 'high',
                'estimated-hours': 4,
                'depends-on': [],
                'validates': ['AC-001']
            },
            {
                'id': 'T2',
                'title': 'Write tests',
                'status': 'todo',
                'priority': 'high',
                'estimated-hours': 3,
                'depends-on': ['T1'],
                'validates': ['AC-001']
            },
            {
                'id': 'T3',
                'title': 'Update documentation',
                'status': 'todo',
                'priority': 'medium',
                'estimated-hours': 1,
                'depends-on': ['T1', 'T2'],
                'validates': []
            }
        ]
    }
    
    tasks_path = spec_dir / 'tasks.yml'
    with open(tasks_path, 'w', encoding='utf-8') as f:
        yaml.dump(tasks_template, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"✅ 作成: tasks.yml")
    
    print(f"\n🎉 Spec作成完了: {feature_name}")
    print(f"\n次のステップ:")
    print(f"1. {spec_dir}/requirements.yml を編集")
    print(f"2. {spec_dir}/design.yml を編集")
    print(f"3. {spec_dir}/tasks.yml を編集")
    print(f"4. Kiroに「{feature_name}の実装を開始しよう」と伝える")


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使い方: python scripts/generate_spec_templates.py <feature-name>")
        print("例: python scripts/generate_spec_templates.py my-new-feature")
        sys.exit(1)
    
    feature_name = sys.argv[1]
    
    print("=" * 60)
    print("Spec Template Generator")
    print("=" * 60)
    print()
    
    create_spec_from_templates(feature_name)


if __name__ == '__main__':
    main()
