"""
generate_release_notes.pyのテスト

テスト項目:
1. CHANGELOGからバージョン抽出
2. タイトル抽出
3. リリースノート生成
4. RELEASE_NOTES.mdへの追記
"""

import sys
import pytest
from pathlib import Path
from datetime import datetime

# scriptsディレクトリをパスに追加
scripts_path = Path(__file__).parent.parent / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

from generate_release_notes import ReleaseNotesGenerator


class TestReleaseNotesGenerator:
    """リリースノート生成のテスト"""
    
    def test_version_normalization(self):
        """バージョン番号の正規化（vの除去）"""
        gen1 = ReleaseNotesGenerator("v1.18.0")
        assert gen1.version == "1.18.0"
        
        gen2 = ReleaseNotesGenerator("1.18.0")
        assert gen2.version == "1.18.0"
    
    def test_extract_from_changelog_success(self, tmp_path):
        """CHANGELOGからバージョン抽出（成功）"""
        # テスト用CHANGELOG作成
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("""# Changelog

## [1.18.0] - 2025-11-27

### Added
- **新機能**
  - 説明

## [1.17.0] - 2025-11-26

### Added
- **別の機能**
""", encoding='utf-8')
        
        gen = ReleaseNotesGenerator("1.18.0")
        gen.changelog_path = changelog
        
        content = gen._extract_from_changelog()
        
        assert content is not None
        assert "[1.18.0]" in content
        assert "新機能" in content
        assert "[1.17.0]" not in content  # 次のバージョンは含まない
    
    def test_extract_from_changelog_not_found(self, tmp_path):
        """CHANGELOGからバージョン抽出（見つからない）"""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("""# Changelog

## [1.17.0] - 2025-11-26

### Added
- **機能**
""", encoding='utf-8')
        
        gen = ReleaseNotesGenerator("1.18.0")
        gen.changelog_path = changelog
        
        content = gen._extract_from_changelog()
        
        assert content is None
    
    def test_extract_title_from_added(self):
        """タイトル抽出（Addedセクションから）"""
        changelog_content = """## [1.18.0] - 2025-11-27

### Added
- **コンテキスト型アドバイス機能**
  - 説明
"""
        gen = ReleaseNotesGenerator("1.18.0")
        title = gen._extract_title(changelog_content)
        
        assert title == "コンテキスト型アドバイス機能"
    
    def test_extract_title_from_fixed(self):
        """タイトル抽出（Fixedセクションから）"""
        changelog_content = """## [1.17.1] - 2025-11-26

### Fixed
- **ImportError修正**
  - 説明
"""
        gen = ReleaseNotesGenerator("1.17.1")
        title = gen._extract_title(changelog_content)
        
        assert title == "ImportError修正"
    
    def test_extract_title_from_changed(self):
        """タイトル抽出（Changedセクションから）"""
        changelog_content = """## [1.16.2] - 2025-11-25

### Changed
- **エラーメッセージの改善**
  - 説明
"""
        gen = ReleaseNotesGenerator("1.16.2")
        title = gen._extract_title(changelog_content)
        
        assert title == "エラーメッセージの改善"
    
    def test_extract_title_fallback(self):
        """タイトル抽出（フォールバック）"""
        changelog_content = """## [1.16.0] - 2025-11-25

### Developer Improvements
- テストの追加
"""
        gen = ReleaseNotesGenerator("1.16.0")
        title = gen._extract_title(changelog_content)
        
        # 最初の行から抽出される
        assert title == "テストの追加"
    
    def test_format_release_note(self):
        """リリースノートのフォーマット"""
        changelog_content = """## [1.18.0] - 2025-11-27

### Added
- **新機能**
  - 説明
"""
        gen = ReleaseNotesGenerator("1.18.0")
        title = "新機能"
        
        release_note = gen._format_release_note(title, changelog_content)
        
        assert "### v1.18.0 - 新機能" in release_note
        assert "**作成日**:" in release_note
        assert "**Title**:" in release_note
        assert "v1.18.0 - 新機能" in release_note
        assert "**Notes**:" in release_note
        assert "### Added" in release_note
        assert "- **新機能**" in release_note
        # ## [1.18.0] - 2025-11-27 の行は除去されている
        assert "## [1.18.0]" not in release_note
    
    def test_append_to_release_notes_with_marker(self, tmp_path):
        """RELEASE_NOTES.mdへの追記（マーカーあり）"""
        release_notes = tmp_path / "RELEASE_NOTES.md"
        release_notes.write_text("""# GitHub Releases 登録用メモ

## 登録待ちリリース

<!-- Kiroがここに新しいリリース情報を追記します -->

---

## 登録済みリリース（アーカイブ）
""", encoding='utf-8')
        
        gen = ReleaseNotesGenerator("1.18.0")
        gen.release_notes_path = release_notes
        
        release_note = "### v1.18.0 - テスト\n**作成日**: 2025-11-27\n"
        gen._append_to_release_notes(release_note)
        
        content = release_notes.read_text(encoding='utf-8')
        
        assert "### v1.18.0 - テスト" in content
        assert "<!-- Kiroがここに新しいリリース情報を追記します -->" in content
        # マーカーの後に追記されている
        assert content.index("<!-- Kiroがここに新しいリリース情報を追記します -->") < content.index("### v1.18.0 - テスト")
    
    def test_append_to_release_notes_without_marker(self, tmp_path):
        """RELEASE_NOTES.mdへの追記（マーカーなし）"""
        release_notes = tmp_path / "RELEASE_NOTES.md"
        release_notes.write_text("""# GitHub Releases 登録用メモ

## 登録待ちリリース

---

## 登録済みリリース（アーカイブ）
""", encoding='utf-8')
        
        gen = ReleaseNotesGenerator("1.18.0")
        gen.release_notes_path = release_notes
        
        release_note = "### v1.18.0 - テスト\n**作成日**: 2025-11-27\n"
        gen._append_to_release_notes(release_note)
        
        content = release_notes.read_text(encoding='utf-8')
        
        assert "### v1.18.0 - テスト" in content
    
    def test_create_release_notes_file(self, tmp_path):
        """RELEASE_NOTES.mdの新規作成"""
        release_notes = tmp_path / "RELEASE_NOTES.md"
        
        gen = ReleaseNotesGenerator("1.18.0")
        gen.release_notes_path = release_notes
        
        gen._create_release_notes_file()
        
        assert release_notes.exists()
        content = release_notes.read_text(encoding='utf-8')
        assert "# GitHub Releases 登録用メモ" in content
        assert "## 登録待ちリリース" in content
        assert "<!-- Kiroがここに新しいリリース情報を追記します -->" in content


class TestScriptImport:
    """スクリプトのインポートテスト"""
    
    def test_script_imports(self):
        """generate_release_notes.pyが正常にインポートできる"""
        try:
            import generate_release_notes
            assert hasattr(generate_release_notes, 'ReleaseNotesGenerator')
            assert hasattr(generate_release_notes, 'main')
        except ImportError as e:
            pytest.fail(f"generate_release_notes.pyのインポートに失敗: {e}")
