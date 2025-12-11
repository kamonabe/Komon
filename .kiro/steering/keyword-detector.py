#!/usr/bin/env python3
"""
Kiro用キーワード自動判定システム
ユーザーメッセージから必要な詳細ルールを自動判定して読み込み指示を生成
セッション内キャッシュ対応版
"""

import re
import yaml
from pathlib import Path
from typing import List, Dict, Set, Tuple

# セッションキャッシュのインポート（テスト実行時の対応）
try:
    from .session_cache import cached_read_file, get_session_cache
except ImportError:
    # テスト実行時やスタンドアロン実行時の対応
    def cached_read_file(file_path: str, explanation: str = "") -> str:
        """キャッシュ機能なしのファイル読み込み（フォールバック）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def get_session_cache():
        """ダミーキャッシュオブジェクト（フォールバック）"""
        class DummyCache:
            def get_cache_stats(self):
                return {
                    'total_tokens_saved': 0,
                    'estimated_cost_savings': 0.0,
                    'hit_rate': 0.0
                }
        return DummyCache()

class KeywordDetector:
    def __init__(self, metadata_path: str = ".kiro/steering/rules-metadata.yml"):
        """キーワード検知システムの初期化"""
        self.metadata_path = Path(metadata_path)
        self.rules_metadata = self._load_metadata()
        self.keyword_map = self._build_keyword_map()
    
    def _load_metadata(self) -> Dict:
        """メタデータファイルを読み込み"""
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  メタデータファイルが見つかりません: {self.metadata_path}")
            return {}
    
    def _build_keyword_map(self) -> Dict[str, List[str]]:
        """キーワードマップを構築（キーワード → ルール名のマッピング）"""
        keyword_map = {}
        
        for rule_name, rule_config in self.rules_metadata.get('rules', {}).items():
            if rule_config.get('auto_load', False):
                keywords = rule_config.get('keywords', [])
                for keyword in keywords:
                    if keyword not in keyword_map:
                        keyword_map[keyword] = []
                    keyword_map[keyword].append(rule_name)
        
        return keyword_map
    
    def detect_keywords(self, user_message: str) -> Tuple[Set[str], Dict[str, List[str]]]:
        """
        ユーザーメッセージからキーワードを検知
        
        Returns:
            Tuple[Set[str], Dict[str, List[str]]]: (検知されたキーワード, ルール別ファイルパス)
        """
        detected_keywords = set()
        rules_to_load = {}
        
        # 大文字小文字を区別しない検索
        message_lower = user_message.lower()
        
        for keyword, rule_names in self.keyword_map.items():
            # キーワードが含まれているかチェック
            if keyword.lower() in message_lower:
                detected_keywords.add(keyword)
                
                for rule_name in rule_names:
                    rule_config = self.rules_metadata['rules'][rule_name]
                    file_path = rule_config.get('file_path')
                    
                    if file_path:
                        if rule_name not in rules_to_load:
                            rules_to_load[rule_name] = {
                                'file_path': file_path,
                                'description': rule_config.get('description', ''),
                                'priority': rule_config.get('priority', 'medium'),
                                'keywords': []
                            }
                        rules_to_load[rule_name]['keywords'].append(keyword)
        
        return detected_keywords, rules_to_load
    
    def generate_load_instructions(self, user_message: str) -> str:
        """
        ユーザーメッセージに基づいて読み込み指示を生成
        
        Returns:
            str: Kiro向けの読み込み指示（Markdown形式）
        """
        detected_keywords, rules_to_load = self.detect_keywords(user_message)
        
        if not detected_keywords:
            return "📝 基本ルールのみで対応可能です"
        
        # 優先度順にソート
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_rules = sorted(
            rules_to_load.items(),
            key=lambda x: priority_order.get(x[1]['priority'], 4)
        )
        
        instructions = []
        instructions.append("🔍 キーワード検知による詳細ルール読み込み")
        instructions.append("")
        
        # 検知されたキーワードを表示
        keyword_list = "、".join(f'「{kw}」' for kw in sorted(detected_keywords))
        instructions.append(f"**検知キーワード**: {keyword_list}")
        instructions.append("")
        
        # 読み込むべきルールを表示
        instructions.append("**読み込み対象**:")
        for rule_name, rule_info in sorted_rules:
            file_path = rule_info['file_path']
            description = rule_info['description']
            priority = rule_info['priority']
            keywords = "、".join(rule_info['keywords'])
            
            priority_emoji = {
                'critical': '🚨',
                'high': '⚡',
                'medium': '📋',
                'low': '📝'
            }.get(priority, '📄')
            
            instructions.append(f"- {priority_emoji} **{rule_name}**: `{file_path}`")
            instructions.append(f"  - {description}")
            instructions.append(f"  - 検知キーワード: {keywords}")
            instructions.append("")
        
        # Kiro向けの実行指示（キャッシュ対応）
        instructions.append("**Kiro実行指示**:")
        instructions.append("```python")
        instructions.append("# セッション内キャッシュを使用した効率的な読み込み")
        instructions.append("from .session_cache import cached_read_file")
        instructions.append("")
        for rule_name, rule_info in sorted_rules:
            file_path = rule_info['file_path']
            instructions.append(f"cached_read_file('{file_path}', '詳細ルール読み込み: {rule_name}')")
        instructions.append("```")
        
        # キャッシュ効果の表示
        cache = get_session_cache()
        stats = cache.get_cache_stats()
        if stats['total_tokens_saved'] > 0:
            instructions.append("")
            instructions.append("**💰 クレジット節約効果**:")
            instructions.append(f"- 節約トークン: {stats['total_tokens_saved']:,}")
            instructions.append(f"- 推定節約額: ${stats['estimated_cost_savings']:.2f}")
            instructions.append(f"- キャッシュヒット率: {stats['hit_rate']:.1f}%")
        
        return "\n".join(instructions)
    
    def get_implementation_rules(self) -> List[str]:
        """実装開始時に必要な全ルールのファイルパスを取得"""
        implementation_rules = []
        
        for rule_name, rule_config in self.rules_metadata.get('rules', {}).items():
            if rule_config.get('auto_load', False):
                triggers = rule_config.get('triggers', [])
                if any(trigger in ['implementation-start', 'task-start', 'code-implementation'] 
                       for trigger in triggers):
                    file_path = rule_config.get('file_path')
                    if file_path:
                        implementation_rules.append(file_path)
        
        return implementation_rules

def main():
    """テスト用のメイン関数"""
    detector = KeywordDetector()
    
    # テストケース
    test_messages = [
        "TASK-003を実装しよう",
        "バージョンアップしてリリースしたい", 
        "テストのカバレッジを確認したい",
        "ブランチを作成してコミットしよう",
        "Specの品質保証をしたい",
        "簡単な質問です"
    ]
    
    for message in test_messages:
        print(f"\n{'='*50}")
        print(f"テストメッセージ: {message}")
        print(f"{'='*50}")
        instructions = detector.generate_load_instructions(message)
        print(instructions)

if __name__ == "__main__":
    main()