# セキュリティガイドライン（将来用ベース）

> **注意**: このルールは現在Komonでは使用していません。
> 将来、セキュリティ要件が高まった際に拡充してください。

## 基本方針

セキュリティでは、以下を重視します：
- 機密情報の安全な管理
- ログへの機密情報の非出力
- 入力値の検証
- 最小権限の原則

## 機密情報の管理

### 環境変数の使用

**✅ 良い例**:
```python
import os

api_key = os.getenv('API_KEY')
db_password = os.getenv('DB_PASSWORD')

if not api_key:
    logger.error("API_KEY is not set")
    sys.exit(1)
```

**❌ 悪い例**:
```python
# ハードコーディング（絶対にしない）
api_key = "sk-1234567890abcdef"
db_password = "my_secret_password"
```

**ルール**:
- ✅ 機密情報は環境変数から読み込む
- ❌ コードにハードコーディングしない
- ❌ 設定ファイルにも含めない
- ✅ `.env`ファイルは`.gitignore`に追加

### .envファイルの管理

```bash
# .env（Gitにコミットしない）
API_KEY=your-api-key-here
DB_PASSWORD=your-password-here
```

```bash
# .env.sample（Gitにコミットする）
API_KEY=your-api-key-here
DB_PASSWORD=your-password-here
```

```python
# .envファイルの読み込み
from dotenv import load_dotenv

load_dotenv()  # .envファイルを読み込む
api_key = os.getenv('API_KEY')
```

## ログ出力の注意

### 機密情報を含めない

**✅ 良い例**:
```python
logger.info("User logged in: user_id=%s", user_id)
logger.info("API call successful: endpoint=%s, status=%d", endpoint, status_code)
logger.debug("Request headers: %s", {k: v for k, v in headers.items() if k != 'Authorization'})
```

**❌ 悪い例**:
```python
logger.info("User logged in: %s", user_data)  # パスワードが含まれる可能性
logger.info("API call: %s", request)  # APIキーが含まれる可能性
logger.debug("Request headers: %s", headers)  # Authorizationヘッダーが含まれる
```

**ルール**:
- ❌ パスワード、APIキー、トークンをログに出力しない
- ❌ 個人情報（メールアドレス、電話番号等）をログに出力しない
- ✅ ログに出力する前に機密情報をマスク
- ✅ デバッグログは本番環境で無効化

### 機密情報のマスキング

```python
def mask_sensitive_data(data):
    """機密情報をマスク"""
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if key.lower() in ['password', 'api_key', 'token', 'secret']:
                masked[key] = '***MASKED***'
            else:
                masked[key] = value
        return masked
    return data

# 使用例
logger.info("User data: %s", mask_sensitive_data(user_data))
```

## エラーメッセージの注意

### 詳細を含めない

**✅ 良い例**:
```python
try:
    result = process_data(data)
except Exception as e:
    print("❌ データ処理に失敗しました")
    logger.error("Data processing failed: %s", e, exc_info=True)
```

**❌ 悪い例**:
```python
try:
    result = process_data(data)
except Exception as e:
    print(f"❌ エラー: {e}")  # スタックトレースが表示される可能性
    print(f"❌ データ: {data}")  # 機密情報が含まれる可能性
```

**ルール**:
- ✅ ユーザー向けメッセージは簡潔に
- ✅ 詳細はログに記録（開発者向け）
- ❌ スタックトレースをユーザーに表示しない
- ❌ 内部実装の詳細を露出しない

## 入力値の検証

### バリデーション

```python
def validate_user_input(user_id):
    """ユーザー入力を検証"""
    # 型チェック
    if not isinstance(user_id, str):
        raise ValueError("user_id must be string")
    
    # 長さチェック
    if len(user_id) > 100:
        raise ValueError("user_id too long")
    
    # 形式チェック（英数字のみ）
    if not user_id.isalnum():
        raise ValueError("user_id must be alphanumeric")
    
    return user_id
```

**ルール**:
- ✅ 全ての外部入力を検証
- ✅ 型、長さ、形式をチェック
- ✅ ホワイトリスト方式（許可するものを明示）
- ❌ ブラックリスト方式（禁止するものを列挙）は避ける

## ファイル操作のセキュリティ

### パストラバーサル対策

```python
import os
from pathlib import Path

def safe_file_path(base_dir, filename):
    """安全なファイルパスを生成"""
    # ベースディレクトリを絶対パスに
    base = Path(base_dir).resolve()
    
    # ファイルパスを結合
    file_path = (base / filename).resolve()
    
    # ベースディレクトリ外へのアクセスを防ぐ
    if not str(file_path).startswith(str(base)):
        raise ValueError("Invalid file path")
    
    return file_path

# 使用例
try:
    file_path = safe_file_path('/data', user_filename)
    with open(file_path, 'r') as f:
        content = f.read()
except ValueError:
    print("❌ 不正なファイルパスです")
```

**ルール**:
- ✅ ファイルパスを検証
- ✅ ベースディレクトリ外へのアクセスを防ぐ
- ❌ ユーザー入力をそのままファイルパスに使用しない

## 依存パッケージのセキュリティ

### 脆弱性チェック

```bash
# 脆弱性スキャン
pip install safety
safety check

# または
pip install pip-audit
pip-audit
```

**ルール**:
- ✅ 定期的に脆弱性スキャン
- ✅ セキュリティパッチは速やかに適用
- ✅ 使用していないパッケージは削除
- ✅ バージョンを固定（requirements.txt）

## テスト戦略

### セキュリティテスト

```python
def test_api_key_not_in_logs(caplog):
    """APIキーがログに出力されないことを確認"""
    api_key = "secret-key-12345"
    
    # API呼び出し
    call_api(api_key)
    
    # ログを確認
    for record in caplog.records:
        assert api_key not in record.message


def test_input_validation():
    """入力値検証のテスト"""
    # 正常な入力
    assert validate_user_input("user123") == "user123"
    
    # 不正な入力
    with pytest.raises(ValueError):
        validate_user_input("user@123")  # 記号を含む
    
    with pytest.raises(ValueError):
        validate_user_input("a" * 101)  # 長すぎる


def test_path_traversal_prevention():
    """パストラバーサル対策のテスト"""
    base_dir = "/data"
    
    # 正常なパス
    assert safe_file_path(base_dir, "file.txt")
    
    # 不正なパス
    with pytest.raises(ValueError):
        safe_file_path(base_dir, "../etc/passwd")
```

## Kiroへの指示

### セキュリティ実装時のチェックリスト

- [ ] 機密情報は環境変数から読み込んでいる
- [ ] `.env`ファイルを`.gitignore`に追加している
- [ ] ログに機密情報を出力していない
- [ ] エラーメッセージに詳細を含めていない
- [ ] 全ての外部入力を検証している
- [ ] パストラバーサル対策を実装している
- [ ] 依存パッケージの脆弱性をチェックしている
- [ ] セキュリティテストを作成している

---

## このルールを使用する際は

1. **プロジェクト固有のセキュリティ要件を追加**
   - 認証・認可の仕組み
   - データ暗号化の要件
   - アクセス制御

2. **脅威モデリングを実施**
   - 想定される攻撃を列挙
   - 対策を検討
   - 優先度を決定

3. **セキュリティレビューを実施**
   - コードレビュー
   - ペネトレーションテスト
   - 脆弱性診断

4. **`_future/`から`.kiro/steering/`に移動**
   ```bash
   mv .kiro/steering/_future/security-guidelines.md .kiro/steering/
   ```
