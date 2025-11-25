#!/usr/bin/env python3
"""
Specファイルの構造を検証するスクリプト

検証項目:
1. Front Matterの存在と必須フィールド
2. 必須セクションの存在
3. 受入基準のフォーマット
4. プロパティの定義
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class SpecValidator:
    """Spec文書の検証クラス"""
    
    REQUIRED_FRONTMATTER_FIELDS = {
        'requirements.md': ['title', 'feature', 'status', 'created', 'updated'],
        'design.md': ['title', 'feature', 'status', 'created', 'updated'],
        'tasks.md': ['title', 'feature', 'status', 'created', 'updated']
    }
    
    REQUIRED_SECTIONS = {
        'requirements.md': ['概要', '用語集', '受入基準'],
        'design.md': ['概要', 'アーキテクチャ', 'コンポーネントとインターフェース', '正確性プロパティ', 'テスト戦略'],
        'tasks.md': ['タスクチェックリスト']
    }
    
    def __init__(self, spec_dir: str = '.kiro/specs'):
        self.spec_dir = Path(spec_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """全てのSpecを検証"""
        print("🔍 Spec検証を開始します...\n")
        
        # テンプレートディレクトリは除外
        spec_features = [
            d for d in self.spec_dir.iterdir()
            if d.is_dir() and d.name not in ['_templates']
        ]
        
        if not spec_features:
            print("⚠️  検証対象のSpecが見つかりません")
            return True
        
        for feature_dir in spec_features:
            print(f"📁 {feature_dir.name} を検証中...")
            self._validate_feature(feature_dir)
            print()
        
        return self._report_results()
    
    def _validate_feature(self, feature_dir: Path):
        """1つの機能のSpecを検証"""
        for spec_type in ['requirements.md', 'design.md', 'tasks.md']:
            spec_file = feature_dir / spec_type
            
            if not spec_file.exists():
                self.warnings.append(f"{feature_dir.name}/{spec_type} が存在しません")
                continue
            
            self._validate_spec_file(spec_file, spec_type)
    
    def _validate_spec_file(self, spec_file: Path, spec_type: str):
        """個別のSpecファイルを検証"""
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Front Matter検証
        frontmatter = self._extract_frontmatter(content)
        if not frontmatter:
            self.errors.append(f"{spec_file.relative_to(self.spec_dir)}: Front Matterが見つかりません")
            return
        
        self._validate_frontmatter(spec_file, frontmatter, spec_type)
        
        # セクション検証
        self._validate_sections(spec_file, content, spec_type)
        
        # 特定ファイルの追加検証
        if spec_type == 'requirements.md':
            self._validate_requirements(spec_file, content)
        elif spec_type == 'design.md':
            self._validate_design(spec_file, content)
        elif spec_type == 'tasks.md':
            self._validate_tasks(spec_file, content)
    
    def _extract_frontmatter(self, content: str) -> Dict[str, str]:
        """Front Matterを抽出"""
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}
        
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        
        return frontmatter
    
    def _validate_frontmatter(self, spec_file: Path, frontmatter: Dict[str, str], spec_type: str):
        """Front Matterの必須フィールドを検証"""
        required_fields = self.REQUIRED_FRONTMATTER_FIELDS.get(spec_type, [])
        
        for field in required_fields:
            if field not in frontmatter or not frontmatter[field]:
                self.errors.append(
                    f"{spec_file.relative_to(self.spec_dir)}: "
                    f"Front Matterに必須フィールド '{field}' がありません"
                )
        
        # 日付フォーマット検証
        for date_field in ['created', 'updated']:
            if date_field in frontmatter:
                date_value = frontmatter[date_field]
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_value):
                    self.errors.append(
                        f"{spec_file.relative_to(self.spec_dir)}: "
                        f"'{date_field}' の日付フォーマットが不正です（YYYY-MM-DD形式で記述してください）"
                    )
    
    def _validate_sections(self, spec_file: Path, content: str, spec_type: str):
        """必須セクションの存在を検証"""
        required_sections = self.REQUIRED_SECTIONS.get(spec_type, [])
        
        for section in required_sections:
            # セクション見出しのパターン（## または ###）
            pattern = rf'^##+ {re.escape(section)}'
            if not re.search(pattern, content, re.MULTILINE):
                self.errors.append(
                    f"{spec_file.relative_to(self.spec_dir)}: "
                    f"必須セクション '{section}' が見つかりません"
                )
    
    def _validate_requirements(self, spec_file: Path, content: str):
        """requirements.mdの追加検証"""
        # 受入基準の数をチェック
        ac_pattern = r'### \[AC-\d+\]'
        ac_count = len(re.findall(ac_pattern, content))
        
        if ac_count < 3:
            self.warnings.append(
                f"{spec_file.relative_to(self.spec_dir)}: "
                f"受入基準が{ac_count}個しかありません（推奨: 3個以上）"
            )
        
        # WHEN-THENフォーマットのチェック
        when_then_pattern = r'\*\*WHEN\*\*.*?\*\*THEN\*\*'
        when_then_count = len(re.findall(when_then_pattern, content, re.DOTALL))
        
        if when_then_count == 0:
            self.warnings.append(
                f"{spec_file.relative_to(self.spec_dir)}: "
                f"WHEN-THEN形式の受入条件が見つかりません"
            )
    
    def _validate_design(self, spec_file: Path, content: str):
        """design.mdの追加検証"""
        # 正確性プロパティの数をチェック
        property_pattern = r'### プロパティ\d+:'
        property_count = len(re.findall(property_pattern, content))
        
        if property_count < 3:
            self.warnings.append(
                f"{spec_file.relative_to(self.spec_dir)}: "
                f"正確性プロパティが{property_count}個しかありません（推奨: 3個以上）"
            )
        
        # プロパティに検証対象の要件が記載されているかチェック
        property_sections = re.findall(
            r'### プロパティ\d+:.*?\n\*\*検証対象:.*?AC-\d+',
            content,
            re.DOTALL
        )
        
        if property_count > 0 and len(property_sections) < property_count:
            self.warnings.append(
                f"{spec_file.relative_to(self.spec_dir)}: "
                f"一部のプロパティに検証対象の要件（AC-XXX）が記載されていません"
            )
    
    def _validate_tasks(self, spec_file: Path, content: str):
        """tasks.mdの追加検証"""
        # タスクの数をチェック
        task_pattern = r'^- \[[ x]\] \d+\.'
        task_count = len(re.findall(task_pattern, content, re.MULTILINE))
        
        if task_count == 0:
            self.errors.append(
                f"{spec_file.relative_to(self.spec_dir)}: "
                f"タスクが1つも定義されていません"
            )
        
        # 要件とのトレーサビリティチェック
        tasks_with_requirements = re.findall(r'_要件:.*?AC-\d+', content)
        
        if task_count > 0 and len(tasks_with_requirements) < task_count * 0.5:
            self.warnings.append(
                f"{spec_file.relative_to(self.spec_dir)}: "
                f"多くのタスクに要件（AC-XXX）が記載されていません"
            )
    
    def _report_results(self) -> bool:
        """検証結果を報告"""
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ エラー: {len(self.errors)}件")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  警告: {len(self.warnings)}件")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ 全てのSpecが検証に合格しました！")
            return True
        elif not self.errors:
            print("\n✅ エラーはありませんが、警告があります")
            return True
        else:
            print("\n❌ 検証に失敗しました")
            return False


def main():
    """メイン処理"""
    validator = SpecValidator()
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
