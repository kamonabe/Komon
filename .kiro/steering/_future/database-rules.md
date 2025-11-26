# データベース操作ルール（将来用ベース）

> **注意**: このルールは現在Komonでは使用していません。
> 将来、データベース操作が必要になった際に拡充してください。

## 基本方針

データベース操作では、以下を重視します：
- トランザクション管理
- SQLインジェクション対策
- パフォーマンス
- テスト容易性

## データベース接続

### 接続情報の管理

```python
import os
import sqlite3  # または psycopg2, pymysql等

def create_connection():
    """データベース接続を作成"""
    db_path = os.getenv('DB_PATH', 'data/app.db')
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 辞書形式で取得
        return conn
    except sqlite3.Error as e:
        logger.error("Failed to connect to database: %s", e)
        raise
```

**ルール**:
- ✅ 接続情報は環境変数から読み込む
- ✅ 接続プールを使用する（本番環境）
- ✅ 接続は必ずクローズする（`with`文推奨）

## トランザクション管理

### 基本パターン

```python
def update_multiple_records(conn, records):
    """複数レコードを更新（トランザクション）"""
    try:
        conn.execute('BEGIN')
        
        for record in records:
            conn.execute(
                'UPDATE table SET column = ? WHERE id = ?',
                (record['value'], record['id'])
            )
        
        conn.commit()
        logger.info("Updated %d records", len(records))
        
    except Exception as e:
        conn.rollback()
        logger.error("Failed to update records: %s", e, exc_info=True)
        raise
```

**ルール**:
- ✅ 複数行の更新は必ずトランザクション
- ✅ エラー時は自動ロールバック
- ❌ 長時間のトランザクションは避ける

## SQLインジェクション対策

### パラメータ化クエリ

**✅ 良い例**:
```python
def fetch_record(conn, record_id):
    """レコードを取得（安全）"""
    cursor = conn.execute(
        'SELECT * FROM table WHERE id = ?',
        (record_id,)
    )
    return cursor.fetchone()
```

**❌ 悪い例**:
```python
def fetch_record_unsafe(conn, record_id):
    """レコードを取得（危険）"""
    cursor = conn.execute(
        f'SELECT * FROM table WHERE id = {record_id}'
    )
    return cursor.fetchone()
```

**ルール**:
- ✅ 必ずパラメータ化クエリを使用
- ❌ 文字列連結でクエリを構築しない
- ❌ f-stringでクエリを構築しない

## スキーマ管理

### マイグレーション

```python
def migrate_v1_to_v2(conn):
    """スキーマをv1からv2に移行"""
    try:
        conn.execute('BEGIN')
        
        # カラム追加
        conn.execute('ALTER TABLE table ADD COLUMN new_column TEXT')
        
        # バージョン更新
        conn.execute('UPDATE schema_version SET version = 2')
        
        conn.commit()
        logger.info("Migrated schema to v2")
        
    except Exception as e:
        conn.rollback()
        logger.error("Migration failed: %s", e, exc_info=True)
        raise
```

**ルール**:
- ✅ スキーマ変更は必ずマイグレーションスクリプト
- ✅ ロールバック手順も用意
- ✅ バージョン管理テーブルを使用
- ✅ 本番適用前にステージング環境で検証

## パフォーマンス

### インデックスの使用

```python
def create_indexes(conn):
    """インデックスを作成"""
    conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON table(created_at)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON table(status)')
    logger.info("Indexes created")
```

### バッチ処理

```python
def insert_batch(conn, records):
    """バッチ挿入（高速）"""
    conn.executemany(
        'INSERT INTO table (id, value) VALUES (?, ?)',
        [(r['id'], r['value']) for r in records]
    )
    conn.commit()
    logger.info("Inserted %d records", len(records))
```

**ルール**:
- ✅ 頻繁に検索するカラムにはインデックス
- ✅ 大量データはバッチ処理
- ❌ N+1クエリは避ける

## テスト戦略

### 統合テスト（実DB使用）

```python
def test_database_operations(tmp_path):
    """データベース操作のテスト"""
    # 一時DBを作成
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    
    # スキーマ作成
    conn.execute('''
        CREATE TABLE records (
            id TEXT PRIMARY KEY,
            value TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # データ挿入
    conn.execute(
        'INSERT INTO records (id, value, created_at) VALUES (?, ?, ?)',
        ('123', 'test', datetime.now())
    )
    conn.commit()
    
    # 検証
    cursor = conn.execute('SELECT * FROM records WHERE id = ?', ('123',))
    result = cursor.fetchone()
    assert result[0] == '123'
    assert result[1] == 'test'
    
    conn.close()


def test_transaction_rollback(tmp_path):
    """トランザクションロールバックのテスト"""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    
    # スキーマ作成
    conn.execute('CREATE TABLE records (id TEXT PRIMARY KEY, value TEXT)')
    
    # トランザクション開始
    conn.execute('BEGIN')
    conn.execute('INSERT INTO records VALUES (?, ?)', ('1', 'test'))
    
    # ロールバック
    conn.rollback()
    
    # 検証（データが存在しない）
    cursor = conn.execute('SELECT COUNT(*) FROM records')
    count = cursor.fetchone()[0]
    assert count == 0
    
    conn.close()
```

### ユニットテスト（モック使用）

```python
from unittest.mock import MagicMock

def test_fetch_record_with_mock():
    """レコード取得のテスト（モック）"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {'id': '123', 'value': 'test'}
    mock_conn.execute.return_value = mock_cursor
    
    result = fetch_record(mock_conn, '123')
    
    assert result['id'] == '123'
    mock_conn.execute.assert_called_once_with(
        'SELECT * FROM table WHERE id = ?',
        ('123',)
    )
```

**ルール**:
- ✅ 統合テストは実DB（SQLite in-memory推奨）
- ✅ ユニットテストはモック
- ✅ テスト後は必ずクリーンアップ（`tmp_path`使用）
- ❌ 本番DBでテストしない

## エラーハンドリング

### データベース固有のエラー

```python
import sqlite3

try:
    conn.execute('INSERT INTO table VALUES (?, ?)', (id, value))
    conn.commit()
except sqlite3.IntegrityError:
    print(f"⚠️ レコードID {id} は既に存在します")
    logger.warning("Duplicate record ID: %s", id)
    # 既存データを更新
    conn.execute('UPDATE table SET value = ? WHERE id = ?', (value, id))
    conn.commit()
except sqlite3.OperationalError as e:
    print(f"❌ データベースエラー: {e}")
    logger.error("Database error: %s", e, exc_info=True)
    sys.exit(1)
```

**ルール**:
- ✅ IntegrityError: 重複データ（処理継続）
- ✅ OperationalError: DB接続エラー（処理停止）
- ✅ エラーメッセージはユーザーフレンドリーに

## Kiroへの指示

### データベース実装時のチェックリスト

- [ ] 接続情報は環境変数から読み込んでいる
- [ ] パラメータ化クエリを使用している（SQLインジェクション対策）
- [ ] トランザクション管理を実装している
- [ ] エラー時のロールバックを実装している
- [ ] インデックスを適切に設定している
- [ ] 統合テストを作成している（`tmp_path`使用）
- [ ] ユニットテストを作成している
- [ ] マイグレーションスクリプトを作成している（スキーマ変更時）

---

## このルールを使用する際は

1. **使用するDBに合わせて調整**
   - SQLite: 軽量、開発・テスト向け
   - PostgreSQL: 本番環境向け
   - MySQL: 本番環境向け

2. **プロジェクト固有のスキーマを定義**
   - テーブル設計
   - インデックス設計
   - リレーション設計

3. **実際の経験に基づいて拡充**
   - パフォーマンスチューニング
   - バックアップ・リストア手順
   - 運用ノウハウ

4. **`_future/`から`.kiro/steering/`に移動**
   ```bash
   mv .kiro/steering/_future/database-rules.md .kiro/steering/
   ```
