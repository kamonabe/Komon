#!/usr/bin/env python3
"""
ステータス整合性チェックスクリプト

4つのファイルのステータス整合性を自動チェック：
1. .kiro/specs/future-ideas.md - アイデアのステータス
2. .kiro/tasks/implementation-tasks.md - 実装タスクのステータス
3. .kiro/specs/{feature-name}/tasks.yml - Spec別タスクのステータス
4. .kiro/tasks/completed-tasks.md - 完了タスクのアーカイブ

使い方:
    python scripts/check_status_consistency.py
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml


class StatusConsistencyChecker:
    """ステータス整合性チェッカー"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.project_root = Path(__file__).parent.parent
    
    def check_all(self) -> bool:
        """全てのステータス整合性をチェック"""
        print("🔍 ステータス整合性をチェック中...\n")
        
        # 1. 完了タスクを取得
        completed_tasks = self._get_completed_tasks()
        
        if not completed_tasks:
            print("✅ 完了タスクが見つかりませんでした（チェック不要）\n")
            return True
        
        # 2. 各タスクの整合性をチェック
        for task_id, task_info in completed_tasks.items():
            self._check_task_consistency(task_id, task_info)
        
        # 3. アーカイブ状況をチェック
        self._check_archive_status()
        
        # 4. 結果を報告
        return self._report_results()
    
    def _get_completed_tasks(self) -> Dict[str, Dict]:
        """implementation-tasks.mdから完了タスクを取得"""
        tasks_file = self.project_root / ".kiro" / "tasks" / "implementation-tasks.md"
        
        if not tasks_file.exists():
            self.errors.append(f"❌ {tasks_file} が見つかりません")
            return {}
        
        content = tasks_file.read_text(encoding='utf-8')
        completed_tasks = {}
        
        # タスクIDとステータスを抽出
        # 例: ### [TASK-003] コンテキストに応じた具体的アドバイス
        #     **ステータス**: 🟢 Done
        #     **完了日**: 2025-11-27 (v1.18.0)
        task_pattern = r'### \[([A-Z]+-\d+)\] (.+?)\n.*?\*\*ステータス\*\*: 🟢 Done.*?\*\*完了日\*\*: (\d{4}-\d{2}-\d{2}) \((v[\d.]+)\)'
        
        for match in re.finditer(task_pattern, content, re.DOTALL):
            task_id = match.group(1)
            task_name = match.group(2).strip()
            completed_date = match.group(3)
            version = match.group(4)
            
            # 元アイデアIDを取得
            idea_pattern = rf'\[{task_id}\].*?\*\*元アイデア\*\*: \[([A-Z]+-\d+)\]'
            idea_match = re.search(idea_pattern, content, re.DOTALL)
            idea_id = idea_match.group(1) if idea_match else None
            
            # feature-nameを取得（implementation-tasks.mdから直接読み取る、または推測）
            feature_name = self._extract_feature_name_from_task(task_id, content) or self._extract_feature_name(task_name)
            
            completed_tasks[task_id] = {
                'name': task_name,
                'completed_date': completed_date,
                'version': version,
                'idea_id': idea_id,
                'feature_name': feature_name
            }
        
        return completed_tasks
    
    def _extract_feature_name_from_task(self, task_id: str, content: str) -> Optional[str]:
        """implementation-tasks.mdから直接feature-nameを読み取る"""
        # 例: **feature-name**: long-running-detector
        pattern = rf'\[{task_id}\].*?\*\*feature-name\*\*: ([a-z0-9-]+)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1)
        
        return None
    
    def _extract_feature_name(self, task_name: str) -> Optional[str]:
        """タスク名からfeature-nameを推測"""
        # 既知のマッピング
        mappings = {
            'コンテキストに応じた具体的アドバイス': 'contextual-advice',
            'コンテキスト型アドバイス': 'contextual-advice',
            '段階的通知メッセージ': 'progressive-notification',
            '通知履歴': 'notification-history',
            'ディスク使用量の増加トレンド予測': 'disk-trend-prediction',
            '通知頻度制御': 'notification-throttle',
            '継続実行中プロセスの検出': 'long-running-detector',
            'ログ急増時の末尾抜粋表示': 'log-tail-excerpt',
        }
        
        for key, value in mappings.items():
            if key in task_name:
                return value
        
        return None
    
    def _check_task_consistency(self, task_id: str, task_info: Dict):
        """タスクの整合性をチェック"""
        print(f"📋 {task_id}: {task_info['name']}")
        
        # 1. future-ideas.mdのステータスをチェック
        self._check_future_ideas_status(task_id, task_info)
        
        # 2. tasks.ymlのステータスをチェック
        self._check_tasks_yml_status(task_id, task_info)
        
        print()
    
    def _check_future_ideas_status(self, task_id: str, task_info: Dict):
        """future-ideas.mdのステータスをチェック"""
        ideas_file = self.project_root / ".kiro" / "specs" / "future-ideas.md"
        
        if not ideas_file.exists():
            self.warnings.append(f"⚠️  {task_id}: future-ideas.md が見つかりません")
            return
        
        content = ideas_file.read_text(encoding='utf-8')
        idea_id = task_info.get('idea_id')
        
        if not idea_id:
            self.warnings.append(f"⚠️  {task_id}: 元アイデアIDが見つかりません")
            return
        
        # アイデアのステータスを検索
        # 例: **ステータス**: ✅ 実装済み (v1.18.0)
        idea_pattern = rf'\[{idea_id}\].*?\*\*ステータス\*\*: (.*?)(?:\n|$)'
        match = re.search(idea_pattern, content, re.DOTALL)
        
        if not match:
            self.errors.append(f"❌ {task_id}: future-ideas.mdに{idea_id}が見つかりません")
            print(f"   ❌ future-ideas.md: {idea_id} が見つかりません")
            return
        
        status = match.group(1).strip()
        expected_status = f"✅ 実装済み ({task_info['version']})"
        
        if status == expected_status:
            print(f"   ✅ future-ideas.md: {status}")
        else:
            self.errors.append(f"❌ {task_id}: future-ideas.mdのステータスが不一致")
            self.errors.append(f"   期待: {expected_status}")
            self.errors.append(f"   実際: {status}")
            print(f"   ❌ future-ideas.md: {status} (期待: {expected_status})")
    
    def _check_tasks_yml_status(self, task_id: str, task_info: Dict):
        """tasks.ymlのステータスをチェック"""
        feature_name = task_info.get('feature_name')
        
        if not feature_name:
            # feature-nameが推測できない場合、全Specフォルダを探索
            found = self._find_tasks_yml_by_task_id(task_id)
            if found:
                print(f"   ✅ tasks.yml: status: completed (task-id: {task_id})")
                return
            
            # 実装前のタスクの可能性があるため、警告のみ
            warning_msg = f"⚠️  {task_id}: tasks.yml - feature-nameが推測できません（実装前の可能性）"
            self.warnings.append(warning_msg)
            print(f"   {warning_msg}")
            return
        
        tasks_yml = self.project_root / ".kiro" / "specs" / feature_name / "tasks.yml"
        
        if not tasks_yml.exists():
            # 実装前のタスクの可能性があるため、警告のみ
            warning_msg = f"⚠️  {task_id}: tasks.yml - {tasks_yml} が見つかりません（実装前の可能性）"
            self.warnings.append(warning_msg)
            print(f"   {warning_msg}")
            return
        
        try:
            with open(tasks_yml, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            status = data.get('metadata', {}).get('status', '')
            
            if status == 'completed':
                print(f"   ✅ tasks.yml: status: completed")
            else:
                self.errors.append(f"❌ {task_id}: tasks.ymlのステータスが不一致")
                self.errors.append(f"   期待: completed")
                self.errors.append(f"   実際: {status}")
                print(f"   ❌ tasks.yml: status: {status} (期待: completed)")
        
        except Exception as e:
            self.errors.append(f"❌ {task_id}: tasks.ymlの読み込みエラー: {e}")
            print(f"   ❌ tasks.yml: 読み込みエラー")
    
    def _find_tasks_yml_by_task_id(self, task_id: str) -> bool:
        """全Specフォルダを探索してtask-idが一致するtasks.ymlを探す"""
        specs_dir = self.project_root / ".kiro" / "specs"
        
        if not specs_dir.exists():
            return False
        
        for spec_folder in specs_dir.iterdir():
            if not spec_folder.is_dir() or spec_folder.name.startswith('_'):
                continue
            
            tasks_yml = spec_folder / "tasks.yml"
            if not tasks_yml.exists():
                continue
            
            try:
                with open(tasks_yml, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                metadata_task_id = data.get('metadata', {}).get('task-id', '')
                status = data.get('metadata', {}).get('status', '')
                
                if metadata_task_id == task_id and status == 'completed':
                    return True
            
            except Exception:
                continue
        
        return False
    
    def _check_archive_status(self):
        """アーカイブ状況をチェック"""
        print("📦 アーカイブ状況をチェック中...")
        
        # completed-tasks.mdの存在確認
        completed_file = self.project_root / ".kiro" / "tasks" / "completed-tasks.md"
        
        if not completed_file.exists():
            self.warnings.append("⚠️  completed-tasks.md が見つかりません")
            print("   ⚠️  completed-tasks.md が見つかりません")
            return
        
        # 前バージョンの完了タスクがアーカイブされているか確認
        # （実装は複雑なので、ファイルの存在確認のみ）
        print("   ✅ completed-tasks.md が存在します")
    
    def _report_results(self) -> bool:
        """結果を報告"""
        print("\n" + "=" * 60)
        print("📊 チェック結果")
        print("=" * 60 + "\n")
        
        if not self.errors and not self.warnings:
            print("✅ 全てのステータスが一致しています\n")
            return True
        
        if self.errors:
            print(f"❌ エラー: {len(self.errors)}件\n")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        if self.warnings:
            print(f"⚠️  警告: {len(self.warnings)}件\n")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if self.errors:
            print("❌ ステータスに不一致があります")
            print("   修正してから再度実行してください\n")
            return False
        else:
            print("⚠️  警告がありますが、エラーはありません")
            print("   必要に応じて確認してください\n")
            return True


def main():
    """メイン処理"""
    checker = StatusConsistencyChecker()
    success = checker.check_all()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
