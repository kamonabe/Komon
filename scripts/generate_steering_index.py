#!/usr/bin/env python3
"""
ステアリングルール索引の自動生成スクリプト

各ルールファイルから概要を抽出し、steering-rules-index.mdを自動生成する。
これにより、索引と詳細ルールの一貫性を保証する。
"""

import yaml
from pathlib import Path
import re


def extract_overview_from_rule(rule_path: Path) -> dict:
    """ルールファイルから概要情報を抽出"""
    content = rule_path.read_text(encoding='utf-8')
    
    # Front Matterを抽出
    front_matter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if front_matter_match:
        front_matter = yaml.safe_load(front_matter_match.group(1))
    else:
        front_matter = {}
    
    # 基本方針セクションを抽出（最初の##まで）
    basic_policy_match = re.search(
        r'## 基本方針\n\n(.*?)(?=\n##|\Z)', 
        content, 
        re.DOTALL
    )
    basic_policy = basic_policy_match.group(1).strip() if basic_policy_match else ""
    
    # 最初の段落を概要として抽出（Front Matterの後、最初の##まで）
    overview_match = re.search(
        r'---\n\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    overview = overview_match.group(1).strip() if overview_match else ""
    
    return {
        'rule_id': front_matter.get('rule-id', rule_path.stem),
        'description': front_matter.get('description', ''),
        'priority': front_matter.get('priority', 'medium'),
        'overview': overview[:200] + '...' if len(overview) > 200 else overview,
        'basic_policy': basic_policy[:300] + '...' if len(basic_policy) > 300 else basic_policy,
    }


def load_rules_metadata() -> dict:
    """rules-metadata.ymlを読み込む"""
    metadata_path = Path('.kiro/steering/rules-metadata.yml')
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        # 'rules'キーの下にルール定義がある
        return data.get('rules', {})


def generate_index():
    """索引ファイルを自動生成"""
    steering_dir = Path('.kiro/steering')
    steering_detailed_dir = Path('.kiro/steering-detailed')
    metadata = load_rules_metadata()
    
    # 階層ごとにルールを分類
    level_1_rules = []  # 常に読み込む
    level_2_rules = []  # オンデマンド読み込み
    
    for rule_id, rule_meta in metadata.items():
        if rule_id == 'steering-rules-index':
            continue  # 索引自身はスキップ
        
        # Level 1ルールは.kiro/steering/、Level 2ルールは.kiro/steering-detailed/から読み込み
        if rule_meta.get('initial_load', False):
            rule_path = steering_dir / f"{rule_id}.md"
        else:
            rule_path = steering_detailed_dir / f"{rule_id}.md"
        
        if not rule_path.exists():
            print(f"⚠️  Warning: {rule_path} not found")
            continue
        
        rule_info = extract_overview_from_rule(rule_path)
        rule_info['metadata'] = rule_meta
        
        if rule_meta.get('initial_load', False):
            level_1_rules.append(rule_info)
        else:
            level_2_rules.append(rule_info)
    
    # 索引ファイルを生成
    index_content = generate_index_content(level_1_rules, level_2_rules)
    
    index_path = steering_dir / 'steering-rules-index.md'
    index_path.write_text(index_content, encoding='utf-8')
    
    print(f"✅ Generated: {index_path}")
    print(f"   Level 1 (initial load): {len(level_1_rules)} rules")
    print(f"   Level 2 (on-demand): {len(level_2_rules)} rules")


def generate_index_content(level_1_rules: list, level_2_rules: list) -> str:
    """索引ファイルの内容を生成"""
    import datetime
    
    content = """---
rule-id: steering-rules-index
priority: critical
applies-to: [all]
triggers: [always]
description: 全ステアリングルールの索引と概要（自動生成）
auto-generated: true
generator: scripts/generate_steering_index.py
---

# ステアリングルール索引

このファイルは全てのステアリングルールの概要を提供します。
詳細が必要な場合は、各ルールファイルを参照してください。

**⚠️ 注意**: このファイルは自動生成されます。直接編集しないでください。

---

## 📚 アクティブなルール一覧

### Level 1: 常に読み込むルール（初期読み込み）

これらのルールは常に読み込まれます（約1,000行）。

"""
    
    # Level 1ルールを追加
    for i, rule in enumerate(level_1_rules, 1):
        content += f"""
### {i}. {rule['rule_id']}

**概要**: {rule['description']}

**優先度**: {rule['metadata']['priority']}

**基本方針**:
{rule['basic_policy']}

**詳細**: `{rule['rule_id']}.md`

---
"""
    
    content += """
### Level 2: オンデマンド読み込みルール（必要に応じて）

これらのルールは必要に応じて読み込まれます（約4,000行）。

"""
    
    # Level 2ルールを追加
    for i, rule in enumerate(level_2_rules, 1):
        content += f"""
### {i}. {rule['rule_id']}

**概要**: {rule['description']}

**優先度**: {rule['metadata']['priority']}

**適用場面**: {', '.join(rule['metadata'].get('applies-to', []))}

**トリガー**: {', '.join(rule['metadata'].get('triggers', []))}

**基本方針**:
{rule['basic_policy']}

**詳細**: `.kiro/steering-detailed/{rule['rule_id']}.md`

---
"""
    
    content += """
## 🔍 使い方

### 簡単な質問の場合

この索引から回答できます。詳細が必要な場合は、該当するルールファイルを自動的に読み込みます。

### 実装開始の場合

必要な全てのルールを自動的に読み込みます：
- development-workflow.md
- git-workflow.md
- error-handling-and-logging.md
- testing-strategy.md

### 詳細が必要な場合

「詳しく教えて」と言っていただければ、該当するルールファイルを読み込んで詳細を説明します。

---

## 🔄 更新履歴

このファイルは `scripts/generate_steering_index.py` により自動生成されます。

更新方法:
```bash
python scripts/generate_steering_index.py
```

---

## 📊 統計

- **Level 1ルール**: {len(level_1_rules)}ファイル（常に読み込む）
- **Level 2ルール**: {len(level_2_rules)}ファイル（オンデマンド）
- **合計**: {len(level_1_rules) + len(level_2_rules)}ファイル

---

**自動生成日時**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # f-stringで統計セクションを生成
    stats_section = f"""## 📊 統計

- **Level 1ルール**: {len(level_1_rules)}ファイル（常に読み込む）
- **Level 2ルール**: {len(level_2_rules)}ファイル（オンデマンド）
- **合計**: {len(level_1_rules) + len(level_2_rules)}ファイル

---

**自動生成日時**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # 統計セクションを置換
    content = content.replace(
        '## 📊 統計\n\n- **Level 1ルール**: {len(level_1_rules)}ファイル（常に読み込む）\n- **Level 2ルール**: {len(level_2_rules)}ファイル（オンデマンド）\n- **合計**: {len(level_1_rules) + len(level_2_rules)}ファイル\n\n---\n\n**自動生成日時**: {datetime.datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}',
        stats_section
    )
    
    return content


if __name__ == '__main__':
    generate_index()
