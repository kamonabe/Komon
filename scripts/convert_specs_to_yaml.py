#!/usr/bin/env python3
"""
既存のMarkdown SpecをYAML形式に変換するスクリプト

使い方:
    python scripts/convert_specs_to_yaml.py
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime


def parse_front_matter(content: str) -> tuple[dict, str]:
    """Front MatterとMarkdown本文を分離"""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    front_matter = yaml.safe_load(parts[1])
    body = parts[2].strip()
    return front_matter, body


def parse_requirements_md(md_path: Path) -> dict:
    """requirements.mdをYAML形式に変換"""
    content = md_path.read_text(encoding='utf-8')
    front_matter, body = parse_front_matter(content)
    
    # 概要セクションを抽出
    overview_match = re.search(r'## 概要\n\n(.*?)(?=\n##|$)', body, re.DOTALL)
    overview = overview_match.group(1).strip() if overview_match else ""
    
    # 受入基準を抽出
    ac_pattern = r'### \[AC-(\d+)\] (.+?)\n\n(.*?)(?=\n###|\Z)'
    acceptance_criteria = []
    
    for match in re.finditer(ac_pattern, body, re.DOTALL):
        ac_id = f"AC-{match.group(1)}"
        title = match.group(2).strip()
        ac_body = match.group(3).strip()
        
        # ユーザーストーリーを抽出
        story_match = re.search(r'\*\*ユーザーストーリー:\*\* (.+?)(?=\n\n|\Z)', ac_body, re.DOTALL)
        user_story = story_match.group(1).strip() if story_match else ""
        
        # WHEN-THENを抽出
        conditions = []
        when_then_pattern = r'\*\*WHEN\*\* (.+?) \*\*THEN\*\* (.+?)(?=\n|$)'
        for wt_match in re.finditer(when_then_pattern, ac_body):
            conditions.append({
                'when': wt_match.group(1).strip().rstrip('、').rstrip(','),
                'then': wt_match.group(2).strip().rstrip('こと')
            })
        
        acceptance_criteria.append({
            'id': ac_id,
            'title': title,
            'priority': 'high',  # デフォルト
            'type': 'functional',  # デフォルト
            'user-story': user_story,
            'conditions': conditions
        })
    
    return {
        'metadata': {
            'title': front_matter.get('title', ''),
            'feature': front_matter.get('feature', ''),
            'status': front_matter.get('status', 'draft'),
            'created': front_matter.get('created', ''),
            'updated': front_matter.get('updated', ''),
            'complexity': 'medium',  # デフォルト
            'estimated-hours': 8,  # デフォルト
            'dependencies': []
        },
        'overview': {
            'description': overview
        },
        'acceptance-criteria': acceptance_criteria
    }


def parse_design_md(md_path: Path) -> dict:
    """design.mdをYAML形式に変換"""
    content = md_path.read_text(encoding='utf-8')
    front_matter, body = parse_front_matter(content)
    
    # 正確性プロパティを抽出
    property_pattern = r'### プロパティ(\d+): (.+?)\n(.*?)\n\*\*検証対象: 要件 (.+?)\*\*'
    properties = []
    
    for match in re.finditer(property_pattern, body, re.DOTALL):
        prop_id = f"P{match.group(1)}"
        title = match.group(2).strip()
        description = match.group(3).strip()
        validates = [v.strip() for v in match.group(4).split(',')]
        
        properties.append({
            'id': prop_id,
            'title': title,
            'type': 'invariant',  # デフォルト
            'description': description,
            'validates': validates,
            'test-strategy': 'property-based'
        })
    
    return {
        'metadata': {
            'title': front_matter.get('title', ''),
            'feature': front_matter.get('feature', ''),
            'status': front_matter.get('status', 'draft'),
            'created': front_matter.get('created', ''),
            'updated': front_matter.get('updated', '')
        },
        'correctness-properties': properties
    }


def parse_tasks_md(md_path: Path) -> dict:
    """tasks.mdをYAML形式に変換"""
    content = md_path.read_text(encoding='utf-8')
    front_matter, body = parse_front_matter(content)
    
    # タスクを抽出
    task_pattern = r'- \[(x| )\] (\d+(?:\.\d+)?)\. (.+?)(?:\n  - _要件: (.+?)_)?(?=\n- \[|\Z)'
    tasks = []
    
    for match in re.finditer(task_pattern, body, re.DOTALL):
        is_done = match.group(1) == 'x'
        task_id = f"T{match.group(2).replace('.', '-')}"
        title = match.group(3).strip()
        validates_text = match.group(4)
        validates = [v.strip() for v in validates_text.split(',')] if validates_text else []
        
        tasks.append({
            'id': task_id,
            'title': title,
            'status': 'done' if is_done else 'todo',
            'priority': 'high',  # デフォルト
            'estimated-hours': 2,  # デフォルト
            'depends-on': [],
            'validates': validates
        })
    
    return {
        'metadata': {
            'title': front_matter.get('title', ''),
            'feature': front_matter.get('feature', ''),
            'status': front_matter.get('status', 'draft'),
            'created': front_matter.get('created', ''),
            'updated': front_matter.get('updated', '')
        },
        'tasks': tasks
    }


def convert_spec_to_yaml(spec_dir: Path):
    """1つのSpec機能をYAML化"""
    print(f"\n🔄 変換中: {spec_dir.name}")
    
    # requirements.md
    req_md = spec_dir / 'requirements.md'
    if req_md.exists():
        req_yaml = parse_requirements_md(req_md)
        req_yaml_path = spec_dir / 'requirements.yml'
        with open(req_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(req_yaml, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"  ✅ requirements.yml 作成")
    
    # design.md
    design_md = spec_dir / 'design.md'
    if design_md.exists():
        design_yaml = parse_design_md(design_md)
        design_yaml_path = spec_dir / 'design.yml'
        with open(design_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(design_yaml, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"  ✅ design.yml 作成")
    
    # tasks.md
    tasks_md = spec_dir / 'tasks.md'
    if tasks_md.exists():
        tasks_yaml = parse_tasks_md(tasks_md)
        tasks_yaml_path = spec_dir / 'tasks.yml'
        with open(tasks_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(tasks_yaml, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"  ✅ tasks.yml 作成")


def main():
    """メイン処理"""
    print("📦 Spec YAML変換スクリプト")
    print("=" * 60)
    
    specs_dir = Path('.kiro/specs')
    
    # 各機能ディレクトリを処理
    for spec_dir in specs_dir.iterdir():
        if not spec_dir.is_dir():
            continue
        if spec_dir.name.startswith('_'):
            continue
        
        convert_spec_to_yaml(spec_dir)
    
    print("\n" + "=" * 60)
    print("✅ 変換完了！")
    print("\n次のステップ:")
    print("1. 生成されたYAMLファイルを確認")
    print("2. 問題なければ古いMarkdownファイルを削除")
    print("3. git add .kiro/specs/")


if __name__ == '__main__':
    main()
