"""
ステータス整合性チェックスクリプトのテスト
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestStatusConsistencyChecker:
    """StatusConsistencyCheckerのテスト"""
    
    def setup_method(self):
        """テスト前にscriptsディレクトリをパスに追加"""
        scripts_path = Path(__file__).parent.parent / "scripts"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
    
    def test_extract_feature_name_known_mappings(self):
        """既知のタスク名からfeature-nameを正しく抽出"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        
        # 既知のマッピング
        assert checker._extract_feature_name("コンテキストに応じた具体的アドバイス") == "contextual-advice"
        assert checker._extract_feature_name("段階的通知メッセージ") == "progressive-notification"
        assert checker._extract_feature_name("通知履歴") == "notification-history"
    
    def test_extract_feature_name_unknown(self):
        """未知のタスク名の場合はNoneを返す"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        
        assert checker._extract_feature_name("未知の機能") is None
    
    def test_get_completed_tasks_file_not_found(self):
        """implementation-tasks.mdが存在しない場合"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        checker.project_root = Path("/nonexistent")
        
        tasks = checker._get_completed_tasks()
        
        assert tasks == {}
        assert len(checker.errors) == 1
        assert "が見つかりません" in checker.errors[0]
    
    def test_check_all_no_completed_tasks(self):
        """完了タスクがない場合"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        
        with patch.object(checker, '_get_completed_tasks', return_value={}):
            result = checker.check_all()
        
        assert result is True
        assert len(checker.errors) == 0
        assert len(checker.warnings) == 0
    
    def test_check_future_ideas_status_file_not_found(self):
        """future-ideas.mdが存在しない場合"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        checker.project_root = Path("/nonexistent")
        
        task_info = {
            'name': 'テスト機能',
            'completed_date': '2025-11-27',
            'version': 'v1.18.0',
            'idea_id': 'IDEA-001',
            'feature_name': 'test-feature'
        }
        
        checker._check_future_ideas_status('TASK-001', task_info)
        
        assert len(checker.warnings) == 1
        assert "future-ideas.md が見つかりません" in checker.warnings[0]
    
    def test_check_future_ideas_status_no_idea_id(self):
        """元アイデアIDがない場合"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        
        task_info = {
            'name': 'テスト機能',
            'completed_date': '2025-11-27',
            'version': 'v1.18.0',
            'idea_id': None,
            'feature_name': 'test-feature'
        }
        
        checker._check_future_ideas_status('TASK-001', task_info)
        
        assert len(checker.warnings) == 1
        assert "元アイデアIDが見つかりません" in checker.warnings[0]
    
    def test_check_tasks_yml_status_no_feature_name(self):
        """feature-nameがない場合"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        
        task_info = {
            'name': 'テスト機能',
            'completed_date': '2025-11-27',
            'version': 'v1.18.0',
            'idea_id': 'IDEA-001',
            'feature_name': None
        }
        
        checker._check_tasks_yml_status('TASK-001', task_info)
        
        assert len(checker.warnings) == 1
        assert "feature-nameが推測できません" in checker.warnings[0]
    
    def test_check_tasks_yml_status_file_not_found(self):
        """tasks.ymlが存在しない場合"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        checker.project_root = Path("/nonexistent")
        
        task_info = {
            'name': 'テスト機能',
            'completed_date': '2025-11-27',
            'version': 'v1.18.0',
            'idea_id': 'IDEA-001',
            'feature_name': 'test-feature'
        }
        
        checker._check_tasks_yml_status('TASK-001', task_info)
        
        assert len(checker.warnings) == 1
        assert "が見つかりません" in checker.warnings[0]
    
    def test_report_results_all_ok(self):
        """エラーも警告もない場合"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        
        result = checker._report_results()
        
        assert result is True
    
    def test_report_results_with_errors(self):
        """エラーがある場合"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        checker.errors.append("エラー1")
        checker.errors.append("エラー2")
        
        result = checker._report_results()
        
        assert result is False
    
    def test_report_results_with_warnings_only(self):
        """警告のみの場合"""
        from check_status_consistency import StatusConsistencyChecker
        
        checker = StatusConsistencyChecker()
        checker.warnings.append("警告1")
        
        result = checker._report_results()
        
        assert result is True


class TestScriptImport:
    """スクリプトファイルのインポートテスト"""
    
    def setup_method(self):
        """テスト前にscriptsディレクトリをパスに追加"""
        scripts_path = Path(__file__).parent.parent / "scripts"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
    
    def test_script_imports(self):
        """check_status_consistency.pyが正常にインポートできることを確認"""
        try:
            import check_status_consistency
            assert hasattr(check_status_consistency, 'StatusConsistencyChecker')
            assert hasattr(check_status_consistency, 'main')
        except ImportError as e:
            pytest.fail(f"check_status_consistency.pyのインポートに失敗: {e}")
