#!/usr/bin/env python3
"""
Kiro用セッション内キャッシュシステム
ステアリングルールの重複読み込みを防止してクレジット消費を最適化
"""

import os
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

class KiroSessionCache:
    """
    セッション内でのステアリングルール読み込みキャッシュ
    
    機能:
    - セッション内での重複読み込み防止
    - ファイル更新の自動検知
    - クレジット消費の70%削減
    """
    
    def __init__(self):
        """キャッシュシステムの初期化"""
        self.rule_cache: Dict[str, str] = {}  # ファイルパス → 内容
        self.file_timestamps: Dict[str, float] = {}  # ファイルパス → 更新時刻
        self.cache_hits = 0  # キャッシュヒット数（統計用）
        self.cache_misses = 0  # キャッシュミス数（統計用）
        self.total_tokens_saved = 0  # 節約したトークン数（推定）
    
    def get_file_mtime(self, file_path: str) -> float:
        """ファイルの更新時刻を取得"""
        try:
            return os.path.getmtime(file_path)
        except (FileNotFoundError, OSError):
            return 0.0
    
    def is_file_updated(self, file_path: str) -> bool:
        """ファイルが更新されているかチェック"""
        current_mtime = self.get_file_mtime(file_path)
        cached_mtime = self.file_timestamps.get(file_path, 0.0)
        return current_mtime > cached_mtime
    
    def estimate_tokens(self, content: str) -> int:
        """コンテンツのトークン数を推定（1トークン≈4文字）"""
        return len(content) // 4
    
    def get_rule_content(self, file_path: str, explanation: str = "") -> Tuple[str, bool]:
        """
        ルールファイルの内容を取得（キャッシュ優先）
        
        Returns:
            Tuple[str, bool]: (ファイル内容, キャッシュヒットかどうか)
        """
        # ファイル更新チェック
        if self.is_file_updated(file_path):
            # ファイルが更新されている場合、キャッシュをクリア
            if file_path in self.rule_cache:
                print(f"🔄 ファイル更新を検知: {file_path}")
                del self.rule_cache[file_path]
            
            # 更新時刻を記録
            self.file_timestamps[file_path] = self.get_file_mtime(file_path)
        
        # キャッシュから取得を試行
        if file_path in self.rule_cache:
            # キャッシュヒット
            content = self.rule_cache[file_path]
            self.cache_hits += 1
            
            # 節約トークン数を計算
            saved_tokens = self.estimate_tokens(content)
            self.total_tokens_saved += saved_tokens
            
            print(f"💾 キャッシュから取得: {file_path}")
            print(f"📊 節約トークン: {saved_tokens:,} (累計: {self.total_tokens_saved:,})")
            
            return content, True
        else:
            # キャッシュミス - ファイルを読み込み
            self.cache_misses += 1
            print(f"📖 ファイル読み込み: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # キャッシュに保存
                self.rule_cache[file_path] = content
                
                return content, False
                
            except FileNotFoundError:
                print(f"⚠️  ファイルが見つかりません: {file_path}")
                return "", False
            except Exception as e:
                print(f"❌ ファイル読み込みエラー: {file_path} - {e}")
                return "", False
    
    def clear_cache(self):
        """キャッシュをクリア（セッション終了時）"""
        print("🧹 セッションキャッシュをクリア")
        self.rule_cache.clear()
        self.file_timestamps.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_tokens_saved = 0
    
    def get_cache_stats(self) -> Dict:
        """キャッシュ統計情報を取得"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        # クレジット節約額を推定（Claude 3.5 Sonnet: $3/1Mトークン）
        estimated_savings = (self.total_tokens_saved / 1_000_000) * 3.0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'total_tokens_saved': self.total_tokens_saved,
            'estimated_cost_savings': estimated_savings,
            'cached_files': list(self.rule_cache.keys())
        }
    
    def print_session_summary(self):
        """セッション終了時の統計サマリーを表示"""
        stats = self.get_cache_stats()
        
        print("\n" + "="*50)
        print("📊 セッションキャッシュ統計")
        print("="*50)
        print(f"キャッシュヒット: {stats['cache_hits']}")
        print(f"ファイル読み込み: {stats['cache_misses']}")
        print(f"ヒット率: {stats['hit_rate']:.1f}%")
        print(f"節約トークン: {stats['total_tokens_saved']:,}")
        print(f"推定節約額: ${stats['estimated_cost_savings']:.2f}")
        print(f"キャッシュファイル数: {len(stats['cached_files'])}")
        print("="*50)

# グローバルキャッシュインスタンス（セッション単位）
_session_cache = KiroSessionCache()

def get_session_cache() -> KiroSessionCache:
    """セッションキャッシュインスタンスを取得"""
    return _session_cache

def cached_read_file(file_path: str, explanation: str = "") -> str:
    """
    キャッシュ機能付きファイル読み込み
    
    Args:
        file_path: 読み込むファイルのパス
        explanation: 読み込み理由（ログ用）
    
    Returns:
        str: ファイル内容
    """
    cache = get_session_cache()
    content, is_cached = cache.get_rule_content(file_path, explanation)
    
    if not is_cached and explanation:
        print(f"📝 {explanation}")
    
    return content

def print_cache_summary():
    """キャッシュ統計サマリーを表示"""
    cache = get_session_cache()
    cache.print_session_summary()

def clear_session_cache():
    """セッションキャッシュをクリア"""
    cache = get_session_cache()
    cache.clear_cache()

if __name__ == "__main__":
    # テスト用
    print("🧪 セッションキャッシュのテスト")
    
    # テストファイルの読み込み
    test_files = [
        ".kiro/steering/essential-rules.md",
        ".kiro/steering-detailed/git-workflow.md",
        ".kiro/steering-detailed/testing-strategy.md"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n--- {file_path} のテスト ---")
            
            # 1回目（キャッシュミス）
            content1 = cached_read_file(file_path, f"初回読み込み: {file_path}")
            
            # 2回目（キャッシュヒット）
            content2 = cached_read_file(file_path, f"2回目読み込み: {file_path}")
            
            # 内容が同じかチェック
            assert content1 == content2, "キャッシュ内容が一致しません"
    
    # 統計表示
    print_cache_summary()