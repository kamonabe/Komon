"""
スクリプトファイルのインポートテスト

scripts/配下のファイルが正常にインポートできることを確認する。
"""

import sys
import pytest
from pathlib import Path


class TestScriptsImport:
    """スクリプトファイルのインポートテスト"""
    
    def setup_method(self):
        """テスト前にscriptsディレクトリをパスに追加"""
        scripts_path = Path(__file__).parent.parent / "scripts"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
    
    def test_main_script_imports(self):
        """main.pyが正常にインポートできることを確認"""
        try:
            import main
            assert hasattr(main, 'main')
            assert hasattr(main, 'load_config')
            assert hasattr(main, 'handle_alerts')
        except ImportError as e:
            pytest.fail(f"main.pyのインポートに失敗: {e}")
    
    def test_advise_script_imports(self):
        """advise.pyが正常にインポートできることを確認"""
        try:
            import advise
            assert hasattr(advise, 'run')
            assert hasattr(advise, 'run_advise')
        except ImportError as e:
            pytest.fail(f"advise.pyのインポートに失敗: {e}")
    
    def test_status_script_imports(self):
        """status.pyが正常にインポートできることを確認"""
        try:
            import status
            assert hasattr(status, 'show_status')
            assert hasattr(status, 'show')
        except ImportError as e:
            pytest.fail(f"status.pyのインポートに失敗: {e}")
    
    def test_komon_guide_script_imports(self):
        """komon_guide.pyが正常にインポートできることを確認"""
        try:
            import komon_guide
            assert hasattr(komon_guide, 'main')
        except ImportError as e:
            pytest.fail(f"komon_guide.pyのインポートに失敗: {e}")
    
    def test_initial_script_imports(self):
        """initial.pyが正常にインポートできることを確認"""
        try:
            import initial
            assert hasattr(initial, 'main')
        except ImportError as e:
            pytest.fail(f"initial.pyのインポートに失敗: {e}")


class TestModulesImport:
    """モジュールのインポートテスト"""
    
    def test_contextual_advisor_imports(self):
        """contextual_advisor.pyが正常にインポートできることを確認"""
        try:
            from src.komon import contextual_advisor
            assert hasattr(contextual_advisor, 'get_contextual_advice')
            assert hasattr(contextual_advisor, '_get_top_processes')
            assert hasattr(contextual_advisor, '_match_pattern')
            assert hasattr(contextual_advisor, '_format_advice')
            assert hasattr(contextual_advisor, 'DEFAULT_PATTERNS')
        except ImportError as e:
            pytest.fail(f"contextual_advisor.pyのインポートに失敗: {e}")
