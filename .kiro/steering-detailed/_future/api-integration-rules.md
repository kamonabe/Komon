# API連携ルール（将来用ベース）

> **注意**: このルールは現在Komonでは使用していません。
> 将来、外部API連携が必要になった際に拡充してください。

## 基本方針

外部APIとの連携では、以下を重視します：
- 認証情報の安全な管理
- リトライ戦略
- エラーハンドリング
- レート制限への対応

## 認証情報の管理

### 環境変数の使用

```python
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

if not api_key or not api_secret:
    print("❌ API認証情報が設定されていません")
    logger.error("API credentials not set")
    sys.exit(1)
```

**ルール**:
- ✅ 環境変数から読み込む
- ❌ コードにハードコーディングしない
- ✅ `.env`ファイルは`.gitignore`に追加
- ✅ 設定ファイルにも含めない

## リトライ戦略

### 基本パターン

```python
import time
import requests

def call_api_with_retry(url, max_retries=3):
    """リトライ付きAPI呼び出し"""
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                timeout=(10, 30),  # (接続, 読み取り)
                headers={'Authorization': f'Bearer {api_key}'}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数バックオフ
                logger.warning("API timeout, retrying in %d seconds...", wait_time)
                time.sleep(wait_time)
            else:
                logger.error("API timeout after %d attempts", max_retries)
                raise
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # レート制限
                retry_after = int(e.response.headers.get('Retry-After', 60))
                logger.warning("Rate limited, waiting %d seconds", retry_after)
                time.sleep(retry_after)
            else:
                raise
```

**ルール**:
- タイムアウト: 接続10秒、読み取り30秒
- リトライ回数: 3回
- バックオフ: 指数バックオフ（2^n秒）
- レート制限: Retry-Afterヘッダーを確認

## エラーハンドリング

### 致命的エラー（処理停止）

以下のエラーは処理を停止し、`sys.exit(1)`で終了します：

- **401 Unauthorized**: 認証情報を確認
- **403 Forbidden**: 権限不足
- **404 Not Found**: エンドポイント誤り

```python
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code in [401, 403]:
        print(f"❌ API認証エラー: {e.response.status_code}")
        logger.error("API authentication failed: %s", e)
        sys.exit(1)
```

### 非致命的エラー（処理継続）

以下のエラーは処理を継続します：

- **429 Too Many Requests**: 待機してリトライ
- **500 Internal Server Error**: リトライ
- **503 Service Unavailable**: リトライ
- **Timeout**: リトライ

## レスポンスの検証

### ステータスコードの確認

```python
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    # 処理...
elif response.status_code == 404:
    logger.warning("Resource not found: %s", url)
    return None
else:
    logger.error("Unexpected status code: %d", response.status_code)
    raise
```

### JSONスキーマの検証

```python
def validate_response(data):
    """レスポンスの構造を検証"""
    required_fields = ['id', 'status', 'data']
    
    for field in required_fields:
        if field not in data:
            logger.warning("Missing field in response: %s", field)
            return False
    
    return True
```

## テスト戦略

### モックの使用（統合テスト）

```python
from unittest.mock import patch

@patch('requests.get')
def test_api_call_success(mock_get):
    """API呼び出し成功のテスト"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'id': '123',
        'status': 'success',
        'data': {'key': 'value'}
    }
    
    result = fetch_data()
    
    assert result['id'] == '123'
    assert result['status'] == 'success'
    mock_get.assert_called_once()


@patch('requests.get')
def test_api_call_retry(mock_get):
    """リトライ処理のテスト"""
    # 1回目: タイムアウト
    # 2回目: 成功
    mock_get.side_effect = [
        requests.exceptions.Timeout(),
        MagicMock(status_code=200, json=lambda: {'data': 'test'})
    ]
    
    result = call_api_with_retry('https://api.example.com')
    
    assert result['data'] == 'test'
    assert mock_get.call_count == 2


@patch('requests.get')
def test_api_call_rate_limit(mock_get):
    """レート制限のテスト"""
    response = MagicMock()
    response.status_code = 429
    response.headers = {'Retry-After': '1'}
    
    mock_get.return_value = response
    
    with pytest.raises(requests.exceptions.HTTPError):
        call_api_with_retry('https://api.example.com', max_retries=1)
```

### ユニットテスト

```python
def test_validate_response_valid():
    """レスポンス検証（正常）"""
    data = {'id': '123', 'status': 'ok', 'data': {}}
    assert validate_response(data) is True


def test_validate_response_missing_field():
    """レスポンス検証（フィールド不足）"""
    data = {'id': '123', 'status': 'ok'}
    assert validate_response(data) is False
```

## Kiroへの指示

### API連携実装時のチェックリスト

- [ ] 環境変数から認証情報を読み込んでいる
- [ ] タイムアウトを設定している（接続10秒、読み取り30秒）
- [ ] リトライ処理を実装している（3回、指数バックオフ）
- [ ] レート制限に対応している（Retry-Afterヘッダー確認）
- [ ] エラーハンドリングを実装している（致命的/非致命的の区別）
- [ ] レスポンスの検証を実装している
- [ ] モックを使った統合テストを作成している
- [ ] ユニットテストを作成している
- [ ] ログに機密情報を出力していない

---

## このルールを使用する際は

1. **プロジェクト固有のAPI仕様に合わせて拡充**
   - 認証方式（OAuth, API Key, JWT等）
   - エンドポイント一覧
   - レスポンス形式

2. **実際の経験に基づいて具体例を追加**
   - 実際に発生したエラーケース
   - パフォーマンスチューニング
   - ベストプラクティス

3. **`_future/`から`.kiro/steering/`に移動**
   ```bash
   mv .kiro/steering/_future/api-integration-rules.md .kiro/steering/
   ```

4. **README.mdに追加**
   - ステアリングルール一覧に追加
   - 使用開始を宣言
