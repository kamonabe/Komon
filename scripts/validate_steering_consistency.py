#!/usr/bin/env python3
"""
ステアリングルールの整合性検証スクリプト

Context効率化の整合性を検証する：
1. 索引の参照先が存在するか
2. rules-metadata.ymlの設定が適切か
3. 階層構造が正しいか
"""

import yaml
from pathlib import Path
import sys


def validate_index_references():
    """索引の参照先が存在するかチェック"""
    steering_dir = Path('.kiro/steering')
    steering_detailed_dir = Path('.kiro/steering-detailed')
    index_path = steering_dir / 'steering-rules-index.md'
    
    if not index_path.exists():
        print("❌ steering-rules-index.md not found")
        return False
    
    content = index_path.read_text(encoding='utf-8')
    
    # **詳細**: `xxx.md` のパターンを抽出
    import re
    references = re.findall(r'\*\*詳細\*\*: `([^`]+)`', content)
    
    errors = []
    for ref in references:
        # パスに応じて適切なディレクトリを選択
        if ref.startswith('.kiro/steering-detailed/'):
            # .kiro/steering-detailed/ で始まる場合は、プロジェクトルートから相対パス
            ref_path = Path(ref)
        elif ref.startswith('steering-detailed/'):
            # steering-detailed/ で始まる場合は、.kiro/ からの相対パス
            ref_path = Path('.kiro') / ref
        else:
            # その他の場合は .kiro/steering/ からの相対パス
            ref_path = steering_dir / ref
        
        if not ref_path.exists():
            errors.append(f"Referenced file not found: {ref} (checked: {ref_path})")
    
    if errors:
        print("❌ Index reference errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print(f"✅ Index references: {len(references)} files validated")
    return True


def validate_metadata_settings():
    """rules-metadata.ymlの設定が適切かチェック"""
    metadata_path = Path('.kiro/steering/rules-metadata.yml')
    
    if not metadata_path.exists():
        print("❌ rules-metadata.yml not found")
        return False
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        metadata = data.get('rules', {})
    
    # initial_load: true のルールが3つ以下か
    initial_load_rules = [
        rule_id for rule_id, rule_meta in metadata.items()
        if isinstance(rule_meta, dict) and rule_meta.get('initial_load', False)
    ]
    
    if len(initial_load_rules) > 3:
        print(f"⚠️  Warning: Too many initial_load rules: {len(initial_load_rules)}")
        print(f"   Recommended: 3 or less")
        print(f"   Current: {', '.join(initial_load_rules)}")
    
    # steering-rules-index が initial_load: true か
    if 'steering-rules-index' not in metadata:
        print("❌ steering-rules-index not found in metadata")
        return False
    
    if not metadata['steering-rules-index'].get('initial_load', False):
        print("❌ steering-rules-index must have initial_load: true")
        return False
    
    print(f"✅ Metadata settings: {len(initial_load_rules)} initial_load rules")
    return True


def validate_hierarchy():
    """階層構造が正しいかチェック"""
    metadata_path = Path('.kiro/steering/rules-metadata.yml')
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        metadata = data.get('rules', {})
    
    # Level 1 (initial_load: true)
    level_1 = [
        rule_id for rule_id, rule_meta in metadata.items()
        if isinstance(rule_meta, dict) and rule_meta.get('initial_load', False)
    ]
    
    # Level 2 (initial_load: false)
    level_2 = [
        rule_id for rule_id, rule_meta in metadata.items()
        if isinstance(rule_meta, dict) and not rule_meta.get('initial_load', False)
    ]
    
    print(f"✅ Hierarchy:")
    print(f"   Level 1 (initial load): {len(level_1)} rules")
    for rule_id in level_1:
        print(f"      - {rule_id}")
    print(f"   Level 2 (on-demand): {len(level_2)} rules")
    for rule_id in level_2:
        print(f"      - {rule_id}")
    
    return True


def validate_auto_generated_flag():
    """索引ファイルが自動生成フラグを持っているかチェック"""
    index_path = Path('.kiro/steering/steering-rules-index.md')
    
    if not index_path.exists():
        print("❌ steering-rules-index.md not found")
        return False
    
    content = index_path.read_text(encoding='utf-8')
    
    if 'auto-generated: true' not in content:
        print("⚠️  Warning: steering-rules-index.md is not marked as auto-generated")
        print("   Please regenerate with: python scripts/generate_steering_index.py")
        return False
    
    print("✅ Auto-generated flag: present")
    return True


def main():
    """全ての検証を実行"""
    print("🔍 Validating steering rules consistency...\n")
    
    results = []
    
    # 検証1: 索引の参照先
    print("1. Validating index references...")
    results.append(validate_index_references())
    print()
    
    # 検証2: メタデータ設定
    print("2. Validating metadata settings...")
    results.append(validate_metadata_settings())
    print()
    
    # 検証3: 階層構造
    print("3. Validating hierarchy...")
    results.append(validate_hierarchy())
    print()
    
    # 検証4: 自動生成フラグ
    print("4. Validating auto-generated flag...")
    results.append(validate_auto_generated_flag())
    print()
    
    # 結果サマリー
    if all(results):
        print("✅ All validations passed!")
        return 0
    else:
        print("❌ Some validations failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
