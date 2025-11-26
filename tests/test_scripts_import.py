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
