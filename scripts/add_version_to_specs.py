#!/usr/bin/env python3
"""
既存のSpecファイルにversionフィールドを追加するスクリプト
"""

import os
import yaml
from pathlib import Path


def add_version_to_spec(spec_file: Path):
    """Specファイルにversionフィールドを追加"""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # YAMLをパース
        data = yaml.safe_load(content)
        
        if not isinstance(data, dict) or 'metadata' not in data:
            print(f"⚠️  {spec_file}: metadataが見つかりません")
            return False
        
        # 既にversionがある場合はスキップ
        if 'version' in data['metadata']:
            print(f"✅ {spec_file}: 既にversionがあります")
            return True
        
        # metadataセクションの後にversionを追加
        lines = content.split('\n')
        new_lines = []
        in_metadata = False
        version_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # metadataセクションの開始
            if line.strip() == 'metadata:':
                in_metadata = True
            
            # metadataセクション内でupdatedの後にversionを追加
            if in_metadata and not version_added:
                if 'updated:' in line:
                    # インデントを取得
                    indent = len(line) - len(line.lstrip())
                    # version, last_validated, validation_passedを追加
                    new_lines.append(' ' * indent + 'version: "1.0.0"  # Specのバージョン')
                    new_lines.append(' ' * indent + 'last_validated: null  # YYYY-MM-DD or null')
                    new_lines.append(' ' * indent + 'validation_passed: null  # true | false | null')
                    version_added = True
                    in_metadata = False
        
        if not version_added:
            print(f"⚠️  {spec_file}: versionを追加できませんでした")
            return False
        
        # ファイルに書き込み
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ {spec_file}: versionを追加しました")
        return True
        
    except Exception as e:
        print(f"❌ {spec_file}: エラー - {e}")
        return False


def main():
    """メイン処理"""
    spec_dir = Path('.kiro/specs')
    
    if not spec_dir.exists():
        print("❌ .kiro/specsディレクトリが見つかりません")
        return 1
    
    print("🔧 既存のSpecファイルにversionフィールドを追加します...\n")
    
    success_count = 0
    total_count = 0
    
    # 各機能ディレクトリを処理
    for feature_dir in spec_dir.iterdir():
        if not feature_dir.is_dir() or feature_dir.name in ['_templates']:
            continue
        
        print(f"\n📁 {feature_dir.name}")
        
        for spec_type in ['requirements.yml', 'design.yml', 'tasks.yml']:
            spec_file = feature_dir / spec_type
            
            if not spec_file.exists():
                continue
            
            total_count += 1
            if add_version_to_spec(spec_file):
                success_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ 完了: {success_count}/{total_count}ファイル")
    
    if success_count == total_count:
        print("\n全てのSpecファイルにversionを追加しました")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count}ファイルで失敗しました")
        return 1


if __name__ == '__main__':
    exit(main())
