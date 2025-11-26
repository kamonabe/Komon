# パフォーマンス基準（将来用ベース）

> **注意**: このルールは現在Komonでは使用していません。
> 将来、パフォーマンス要件が明確になった際に拡充してください。

## 基本方針

パフォーマンスでは、以下を重視します：
- 応答時間の目標設定
- メモリ使用量の制限
- ファイルサイズの管理
- 計測と改善のサイクル

## 応答時間の目標

### CLIコマンド

```
- 即座に応答: 100ms以内
- 高速: 1秒以内
- 許容範囲: 5秒以内
- 遅い: 5秒以上（改善が必要）
```

**例**:
```python
import time

def measure_execution_time(func):
    """実行時間を計測するデコレータ"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        
        if elapsed > 5.0:
            logger.warning("%s took %.2f seconds (slow)", func.__name__, elapsed)
        elif elapsed > 1.0:
            logger.info("%s took %.2f seconds", func.__name__, elapsed)
        
        return result
    return wrapper

@measure_execution_time
def process_data(data):
    # 処理...
    pass
```

### バッチ処理

```
- 小規模（100件）: 1秒以内
- 中規模（1,000件）: 10秒以内
- 大規模（10,000件）: 60秒以内
```

**ルール**:
- ✅ 処理時間を計測
- ✅ 5秒以上かかる処理は進捗表示
- ✅ 大量データはバッチ処理
- ❌ 同期処理で長時間ブロックしない

## メモリ使用量の制限

### 目標値

```
- 通常動作: 50MB以下
- 大量データ処理: 200MB以下
- 警告: 500MB以上
```

**計測方法**:
```python
import psutil
import os

def get_memory_usage():
    """現在のメモリ使用量を取得（MB）"""
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    return memory_mb

# 使用例
memory_before = get_memory_usage()
process_large_data(data)
memory_after = get_memory_usage()

logger.info("Memory usage: %.2f MB -> %.2f MB (delta: %.2f MB)",
            memory_before, memory_after, memory_after - memory_before)

if memory_after > 500:
    logger.warning("High memory usage: %.2f MB", memory_after)
```

**ルール**:
- ✅ 大量データは分割処理
- ✅ 不要なデータは即座に解放
- ✅ ジェネレータを活用
- ❌ 全データをメモリに展開しない

### メモリ効率的な処理

```python
# ❌ 悪い例: 全データをメモリに展開
def process_all_at_once(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()  # 全行をメモリに読み込む
    
    for line in lines:
        process_line(line)

# ✅ 良い例: 1行ずつ処理
def process_line_by_line(file_path):
    with open(file_path, 'r') as f:
        for line in f:  # 1行ずつ読み込む
            process_line(line)

# ✅ 良い例: ジェネレータを使用
def read_large_file(file_path):
    """大きなファイルを効率的に読み込む"""
    with open(file_path, 'r') as f:
        for line in f:
            yield line.strip()

for line in read_large_file('large_file.txt'):
    process_line(line)
```

## ファイルサイズの管理

### 目標値

```
- ログファイル: 10MB以下（自動ローテーション）
- 履歴ファイル: 1MB以下（古いデータを削除）
- データベース: 100MB以下（定期的にクリーンアップ）
```

**ローテーション例**:
```python
import os
from pathlib import Path

def rotate_log_file(log_path, max_size_mb=10):
    """ログファイルをローテーション"""
    if not os.path.exists(log_path):
        return
    
    file_size_mb = os.path.getsize(log_path) / 1024 / 1024
    
    if file_size_mb > max_size_mb:
        # バックアップを作成
        backup_path = f"{log_path}.1"
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(log_path, backup_path)
        
        logger.info("Rotated log file: %.2f MB", file_size_mb)
```

**ルール**:
- ✅ ファイルサイズを定期的にチェック
- ✅ 大きくなったら自動ローテーション
- ✅ 古いデータは削除または圧縮
- ❌ 無制限に肥大化させない

## データベースのパフォーマンス

### インデックスの使用

```python
# 頻繁に検索するカラムにインデックス
conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON table(created_at)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON table(status)')
```

### クエリの最適化

```python
# ❌ 悪い例: N+1クエリ
def get_all_records_with_details():
    records = conn.execute('SELECT id FROM records').fetchall()
    results = []
    for record in records:
        detail = conn.execute('SELECT * FROM details WHERE record_id = ?', 
                             (record['id'],)).fetchone()
        results.append({'record': record, 'detail': detail})
    return results

# ✅ 良い例: JOINを使用
def get_all_records_with_details_optimized():
    return conn.execute('''
        SELECT r.*, d.*
        FROM records r
        LEFT JOIN details d ON r.id = d.record_id
    ''').fetchall()
```

**ルール**:
- ✅ インデックスを適切に設定
- ✅ JOINを使ってN+1クエリを回避
- ✅ 必要なカラムのみ取得（SELECT *を避ける）
- ✅ LIMITで取得件数を制限

## 計測と改善

### プロファイリング

```python
import cProfile
import pstats

def profile_function(func):
    """関数のプロファイリング"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 上位10件を表示
    
    return result

# 使用例
profile_function(lambda: process_large_data(data))
```

### ベンチマーク

```python
import timeit

def benchmark_function(func, iterations=100):
    """関数のベンチマーク"""
    elapsed = timeit.timeit(func, number=iterations)
    avg_time = elapsed / iterations
    
    print(f"Average time: {avg_time*1000:.2f} ms ({iterations} iterations)")
    return avg_time

# 使用例
benchmark_function(lambda: process_data(sample_data))
```

**ルール**:
- ✅ パフォーマンス問題が疑われる箇所をプロファイリング
- ✅ 改善前後でベンチマーク
- ✅ 定期的にパフォーマンステスト
- ❌ 推測で最適化しない（計測してから）

## テスト戦略

### パフォーマンステスト

```python
import time
import pytest

def test_response_time():
    """応答時間のテスト"""
    start = time.time()
    result = process_data(sample_data)
    elapsed = time.time() - start
    
    assert elapsed < 1.0, f"Too slow: {elapsed:.2f} seconds"
    assert result is not None


def test_memory_usage():
    """メモリ使用量のテスト"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / 1024 / 1024
    
    process_large_data(large_dataset)
    
    memory_after = process.memory_info().rss / 1024 / 1024
    memory_delta = memory_after - memory_before
    
    assert memory_delta < 200, f"Too much memory: {memory_delta:.2f} MB"


@pytest.mark.slow
def test_large_dataset_processing():
    """大量データ処理のテスト"""
    large_data = generate_large_dataset(10000)
    
    start = time.time()
    result = process_data(large_data)
    elapsed = time.time() - start
    
    assert elapsed < 60.0, f"Too slow for large dataset: {elapsed:.2f} seconds"
    assert len(result) == 10000
```

**ルール**:
- ✅ 応答時間のテストを作成
- ✅ メモリ使用量のテストを作成
- ✅ 大量データでのテストを作成
- ✅ `@pytest.mark.slow`で分離

## Kiroへの指示

### パフォーマンス実装時のチェックリスト

- [ ] 応答時間の目標を設定している
- [ ] 実行時間を計測している
- [ ] メモリ使用量を計測している
- [ ] 大量データは分割処理している
- [ ] ファイルサイズを管理している（ローテーション）
- [ ] データベースにインデックスを設定している
- [ ] N+1クエリを回避している
- [ ] パフォーマンステストを作成している

---

## このルールを使用する際は

1. **プロジェクト固有の目標値を設定**
   - ユーザー要件に基づく
   - 実測値を基準にする
   - 段階的に改善

2. **ボトルネックを特定**
   - プロファイリングツールを使用
   - ログから遅い処理を特定
   - ユーザーフィードバックを収集

3. **継続的に計測**
   - CI/CDでパフォーマンステスト
   - 本番環境でモニタリング
   - 定期的にレビュー

4. **`_future/`から`.kiro/steering/`に移動**
   ```bash
   mv .kiro/steering/_future/performance-standards.md .kiro/steering/
   ```
