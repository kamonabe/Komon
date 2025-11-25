#!/usr/bin/env python3
"""
Spec間の一貫性をチェックするスクリプト

検証項目:
1. requirements.md, design.md, tasks.mdのfeature名が一致
2. design.mdのプロパティがrequirements.mdの受入基準を参照
3. tasks.mdのタスクがrequirements.mdの受入基準を参照
4. 全ての受入基準がタスクでカバーされている
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class SpecConsistencyChecker:
    """Spec間の一貫性チェッククラス"""
    
    def __init__(self, spec_dir: str = '.kiro/specs'):
        self.spec_dir = Path(spec_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def check_all(self) -> bool:
        """全てのSpecの一貫性をチェック"""
        print("🔍 Spec一貫性チェックを開始します...\n")
        
        # テンプレートディレクトリは除外
        spec_features = [
            d for d in self.spec_dir.iterdir()
            if d.is_dir() and d.name not in ['_templates']
        ]
        
        if not spec_features:
            print("⚠️  チェック対象のSpecが見つかりません")
            return True
        
        for feature_dir in spec_features:
            print(f"📁 {feature_dir.name} をチェック中...")
            self._check_feature(feature_dir)
            print()
        
        return self._report_results()
    
    def _check_feature(self, feature_dir: Path):
        """1つの機能のSpec一貫性をチェック"""
        # 各ファイルの存在確認
        req_file = feature_dir / 'requirements.md'
        design_file = feature_dir / 'design.md'
        tasks_file = feature_dir / 'tasks.md'
        
        files_exist = {
            'requirements': req_file.exists(),
            'design': design_file.exists(),
            'tasks': tasks_file.exists()
        }
        
        if not all(files_exist.values()):
            missing = [k for k, v in files_exist.items() if not v]
            self.warnings.append(
                f"{feature_dir.name}: {', '.join(missing)}.md が存在しません"
            )
            return
        
        # Front Matterのfeature名一致チェック
        self._check_feature_names(feature_dir, req_file, design_file, tasks_file)
        
        # 受入基準の抽出
        acceptance_criteria = self._extract_acceptance_criteria(req_file)
        
        # プロパティと受入基準の対応チェック
        if design_file.exists():
            self._check_property_coverage(feature_dir, design_file, acceptance_criteria)
        
        # タスクと受入基準の対応チェック
        if tasks_file.exists():
            self._check_task_coverage(feature_dir, tasks_file, acceptance_criteria)
    
    def _check_feature_names(self, feature_dir: Path, req_file: Path, design_file: Path, tasks_file: Path):
        """feature名の一致をチェック"""
        feature_names = {}
        
        for file_path, file_type in [(req_file, 'requirements'), (design_file, 'design'), (tasks_file, 'tasks')]:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'^feature:\s*(.+)$', content, re.MULTILINE)
            if match:
                feature_names[file_type] = match.group(1).strip()
        
        if len(set(feature_names.values())) > 1:
            self.errors.append(
                f"{feature_dir.name}: feature名が一致しません "
                f"({', '.join(f'{k}={v}' for k, v in feature_names.items())})"
            )
    
    def _extract_acceptance_criteria(self, req_file: Path) -> Set[str]:
        """受入基準のIDを抽出"""
        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # AC-001, AC-002 などを抽出
        ac_pattern = r'\[AC-(\d+)\]'
        ac_ids = set(re.findall(ac_pattern, content))
        
        return ac_ids
    
    def _check_property_coverage(self, feature_dir: Path, design_file: Path, acceptance_criteria: Set[str]):
        """プロパティが受入基準を参照しているかチェック"""
        with open(design_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # プロパティセクションを抽出
        property_sections = re.findall(
            r'### プロパティ\d+:.*?\n\*\*検証対象:.*?$',
            content,
            re.DOTALL | re.MULTILINE
        )
        
        if not property_sections:
            return
        
        # 各プロパティが参照しているAC-XXXを抽出
        referenced_acs = set()
        for section in property_sections:
            ac_refs = re.findall(r'AC-(\d+)', section)
            referenced_acs.update(ac_refs)
        
        # 参照されていない受入基準
        unreferenced = acceptance_criteria - referenced_acs
        if unreferenced:
            self.warnings.append(
                f"{feature_dir.name}/design.md: "
                f"以下の受入基準がプロパティで参照されていません: "
                f"{', '.join(sorted(f'AC-{ac}' for ac in unreferenced))}"
            )
    
    def _check_task_coverage(self, feature_dir: Path, tasks_file: Path, acceptance_criteria: Set[str]):
        """タスクが受入基準をカバーしているかチェック"""
        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # タスクが参照しているAC-XXXを抽出
        referenced_acs = set(re.findall(r'AC-(\d+)', content))
        
        # カバーされていない受入基準
        uncovered = acceptance_criteria - referenced_acs
        if uncovered:
            self.warnings.append(
                f"{feature_dir.name}/tasks.md: "
                f"以下の受入基準がタスクでカバーされていません: "
                f"{', '.join(sorted(f'AC-{ac}' for ac in uncovered))}"
            )
        
        # 存在しない受入基準を参照している
        invalid_refs = referenced_acs - acceptance_criteria
        if invalid_refs:
            self.errors.append(
                f"{feature_dir.name}/tasks.md: "
                f"存在しない受入基準を参照しています: "
                f"{', '.join(sorted(f'AC-{ac}' for ac in invalid_refs))}"
            )
    
    def _report_results(self) -> bool:
        """チェック結果を報告"""
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
            print("\n✅ 全てのSpecの一貫性が確認されました！")
            return True
        elif not self.errors:
            print("\n✅ エラーはありませんが、警告があります")
            return True
        else:
            print("\n❌ 一貫性チェックに失敗しました")
            return False


def main():
    """メイン処理"""
    checker = SpecConsistencyChecker()
    success = checker.check_all()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
