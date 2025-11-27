#!/usr/bin/env python3
"""
GitHub Releases用のリリースノートを自動生成

使い方:
  python scripts/generate_release_notes.py v1.18.0
  python scripts/generate_release_notes.py 1.18.0  # vなしでもOK

機能:
  1. CHANGELOG.mdから該当バージョンのセクションを抽出
  2. GitHub Releases用にフォーマット
  3. .kiro/RELEASE_NOTES.mdの「登録待ちリリース」セクションに自動追記
"""

import re
import sys
from datetime import datetime
from pathlib import Path


class ReleaseNotesGenerator:
    """リリースノート生成クラス"""
    
    def __init__(self, version: str):
        self.version = version.lstrip('v')  # vを除去
        self.changelog_path = Path('docs/CHANGELOG.md')
        self.release_notes_path = Path('.kiro/RELEASE_NOTES.md')
    
    def generate(self) -> bool:
        """リリースノートを生成"""
        print(f"🔍 v{self.version} のリリースノートを生成中...\n")
        
        # 1. CHANGELOGから該当バージョンを抽出
        changelog_content = self._extract_from_changelog()
        
        if not changelog_content:
            print(f"❌ v{self.version} がCHANGELOG.mdに見つかりません")
            print(f"   場所: {self.changelog_path}")
            return False
        
        # 2. タイトルを抽出
        title = self._extract_title(changelog_content)
        
        # 3. リリースノートを生成
        release_note = self._format_release_note(title, changelog_content)
        
        # 4. RELEASE_NOTES.mdに追記
        self._append_to_release_notes(release_note)
        
        print("✅ リリースノートを生成しました\n")
        print("=" * 60)
        print(release_note)
        print("=" * 60)
        print(f"\n📝 次のステップ:")
        print(f"   1. .kiro/RELEASE_NOTES.md を確認")
        print(f"   2. GitHub Releasesにコピー＆ペースト")
        print(f"   3. 登録完了後、RELEASE_NOTES.mdをアーカイブ")
        
        return True
    
    def _extract_from_changelog(self) -> str:
        """CHANGELOGから該当バージョンのセクションを抽出"""
        if not self.changelog_path.exists():
            return None
        
        with open(self.changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # ## [1.18.0] - 2025-11-27 から次の ## まで（または末尾まで）
        pattern = rf'## \[{re.escape(self.version)}\].*?(?=\n## |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(0)
        return None
    
    def _extract_title(self, changelog_content: str) -> str:
        """タイトルを抽出（最初の機能名）"""
        # ### Added の最初の項目から抽出
        pattern = r'### Added\s*\n\s*-\s*\*\*(.*?)\*\*'
        match = re.search(pattern, changelog_content)
        
        if match:
            return match.group(1)
        
        # Addedがない場合はFixedから
        pattern = r'### Fixed\s*\n\s*-\s*\*\*(.*?)\*\*'
        match = re.search(pattern, changelog_content)
        
        if match:
            return match.group(1)
        
        # それでもない場合はChangedから
        pattern = r'### Changed\s*\n\s*-\s*\*\*(.*?)\*\*'
        match = re.search(pattern, changelog_content)
        
        if match:
            return match.group(1)
        
        # 最終手段: 最初の行から抽出
        lines = changelog_content.split('\n')
        for line in lines:
            if line.strip().startswith('-'):
                # - **機能名** の形式
                match = re.search(r'\*\*(.*?)\*\*', line)
                if match:
                    return match.group(1)
                # - 機能名 の形式
                return line.strip().lstrip('- ').split(':')[0]
        
        return "バグ修正と改善"
    
    def _format_release_note(self, title: str, changelog_content: str) -> str:
        """GitHub Releases用にフォーマット"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # CHANGELOGの内容から ## [version] - date の行を除去
        content = re.sub(r'^## \[.*?\] - .*?\n', '', changelog_content)
        
        return f"""### v{self.version} - {title}
**作成日**: {today}

**Title**:
v{self.version} - {title}

**Notes**:
{content.strip()}

---
"""
    
    def _append_to_release_notes(self, release_note: str):
        """RELEASE_NOTES.mdに追記"""
        if not self.release_notes_path.exists():
            print(f"⚠️  {self.release_notes_path} が存在しません")
            print(f"   新規作成します")
            self._create_release_notes_file()
        
        with open(self.release_notes_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # "登録待ちリリース" セクションの後に追記
        marker = "<!-- Kiroがここに新しいリリース情報を追記します -->"
        
        if marker in content:
            content = content.replace(
                marker,
                f"{marker}\n\n{release_note}"
            )
        else:
            # マーカーがない場合は "登録待ちリリース" の後に追加
            pattern = r'(## 登録待ちリリース\s*\n)'
            if re.search(pattern, content):
                content = re.sub(
                    pattern,
                    rf'\1\n{release_note}\n',
                    content
                )
            else:
                # それでもない場合は末尾に追加
                content += f"\n\n{release_note}"
        
        with open(self.release_notes_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_release_notes_file(self):
        """RELEASE_NOTES.mdを新規作成"""
        template = """# GitHub Releases 登録用メモ

**このファイルはGitHubにアップロードしません（.gitignoreに記載）**

このファイルには、Kiroが自動的にGitHub Releases登録用の情報を追記します。
ユーザーはこの情報をコピーしてGitHub Releasesに登録してください。

---

## 登録待ちリリース

<!-- Kiroがここに新しいリリース情報を追記します -->

---

## 登録済みリリース（アーカイブ）

"""
        with open(self.release_notes_path, 'w', encoding='utf-8') as f:
            f.write(template)


def main():
    """メイン処理"""
    if len(sys.argv) != 2:
        print("使い方: python scripts/generate_release_notes.py v1.18.0")
        print("        python scripts/generate_release_notes.py 1.18.0")
        sys.exit(1)
    
    version = sys.argv[1]
    generator = ReleaseNotesGenerator(version)
    
    success = generator.generate()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
