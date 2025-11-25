---
title: ディスク使用量の増加トレンド予測 - 設計書
feature: disk-trend-prediction
status: implemented
created: 2025-11-23
updated: 2025-11-25
---

# ディスク使用量の増加トレンド予測 - 設計書

## 概要

本機能は、過去7日分のディスク使用率データから線形回帰により将来の使用量を予測し、ディスク容量が90%に到達する予測日を算出します。また、前日比で10%以上の急激な増加を検出し、早期警告を発します。予測結果は`komon advise`コマンドおよび週次レポートで表示されます。

設計の主要な方針：
- 既存のusage_historyデータを活用
- 線形回帰による予測（最小二乗法）
- 急激な変化の早期検出（前日比10%以上）
- adviseコマンドと週次レポートへのシームレスな統合

## アーキテクチャ

### システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                    Komon システム                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────────────────────┐    │
│  │ scripts/     │      │ src/komon/                    │    │
│  │              │      │                                │    │
│  │ advise.py    │─────▶│ disk_predictor.py (新規)     │    │
│  │              │      │  - load_disk_history()        │    │
│  │ weekly_      │─────▶│  - predict_disk_trend()       │    │
│  │ report.py    │      │  - detect_rapid_change()      │    │
│  │              │      │  - format_prediction_message()│    │
│  └──────────────┘      └──────────────────────────────┘    │
│                                                               │
│                         ┌──────────────────────────────┐    │
│                         │ data/usage_history/          │    │
│                         │  - usage_YYYYMMDD_HHMMSS.csv │    │
│                         │  - usage_YYYYMMDD_HHMMSS.csv │    │
│                         │  - ...                        │    │
│                         └──────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### データフロー

1. **データ収集**: `data/usage_history/`から過去7日分のCSVファイルを読み込み
2. **データ処理**: 日次平均値を計算し、時系列データを構築
3. **予測計算**: 線形回帰により傾きを算出し、90%到達日を予測
4. **急激な変化検出**: 前日比を計算し、10%以上の増加を検出
5. **メッセージ生成**: 予測結果を分かりやすいメッセージに変換
6. **表示**: `advise`コマンドまたは週次レポートで表示

## コンポーネントとインターフェース

### 新規モジュール: `src/komon/disk_predictor.py`

#### 関数1: `load_disk_history(days: int = 7) -> list[tuple[datetime, float]]`

**目的**: 過去N日分のディスク使用率データを読み込む

**入力**:
- `days`: 読み込む日数（デフォルト: 7）

**出力**:
- `list[tuple[datetime, float]]`: [(日時, ディスク使用率), ...]

**処理**:
1. `data/usage_history/`ディレクトリから`usage_*.csv`ファイルを取得
2. 各ファイルから`disk`カラムの値を読み込み
3. ファイル名から日時を抽出
4. 過去N日分のデータをフィルタリング
5. 日付でソート

**エラーハンドリング**:
- ディレクトリが存在しない場合: 空リストを返す
- ファイルが読めない場合: そのファイルをスキップ
- 数値変換エラー: そのレコードをスキップ

#### 関数2: `calculate_daily_average(data: list[tuple[datetime, float]]) -> list[tuple[date, float]]`

**目的**: 時系列データから日次平均値を計算

**入力**:
- `data`: [(日時, ディスク使用率), ...]

**出力**:
- `list[tuple[date, float]]`: [(日付, 平均使用率), ...]

**処理**:
1. 日時を日付でグループ化
2. 各日付の平均値を計算
3. 日付でソート

#### 関数3: `predict_disk_trend(daily_data: list[tuple[date, float]]) -> dict`

**目的**: 線形回帰により将来のディスク使用量を予測

**入力**:
- `daily_data`: [(日付, 平均使用率), ...]

**出力**:
```python
{
    'slope': float,              # 傾き（%/日）
    'intercept': float,          # 切片
    'current_usage': float,      # 現在の使用率
    'days_to_90': int | None,    # 90%到達までの日数（Noneは該当なし）
    'prediction_date': str | None, # 90%到達予測日（YYYY-MM-DD形式）
    'trend': str                 # 'increasing', 'stable', 'decreasing'
}
```

**処理**:
1. データ件数が2件未満の場合: エラーを返す
2. 最小二乗法で傾きと切片を計算
3. 傾きから増加率を判定
4. 現在の使用率から90%到達までの日数を計算
5. 予測日を算出

**計算式**:
```
y = slope * x + intercept
days_to_90 = (90 - current_usage) / slope
```

#### 関数4: `detect_rapid_change(daily_data: list[tuple[date, float]]) -> dict`

**目的**: 前日比で急激な変化を検出

**入力**:
- `daily_data`: [(日付, 平均使用率), ...]

**出力**:
```python
{
    'is_rapid': bool,           # 急激な変化があるか
    'change_percent': float,    # 前日比の変化率（%）
    'previous_usage': float,    # 前日の使用率
    'current_usage': float      # 現在の使用率
}
```

**処理**:
1. データが2件未満の場合: `is_rapid=False`を返す
2. 最新日と前日のデータを取得
3. 差分を計算
4. 10%以上の増加の場合: `is_rapid=True`

#### 関数5: `format_prediction_message(prediction: dict, rapid_change: dict) -> str`

**目的**: 予測結果を分かりやすいメッセージに変換

**入力**:
- `prediction`: 予測結果
- `rapid_change`: 急激な変化の検出結果

**出力**:
- `str`: フォーマットされたメッセージ

**メッセージパターン**:

1. **急激な変化あり + 90%到達予測あり**:
```
⚠️ ディスク使用量が急激に増加しています！
前日比: +12.5%（75.0% → 87.5%）

このままだと、あと3日で90%に到達する見込みです。
予測到達日: 2025-11-28

💡 推奨アクション：
- 古いログファイルを削除: journalctl --vacuum-time=7d
- 不要なファイルを確認: du -sh /* | sort -h
```

2. **急激な変化あり + 90%到達予測なし**:
```
⚠️ ディスク使用量が急激に増加しています！
前日比: +11.0%（60.0% → 71.0%）

現在の増加率では90%到達まで余裕がありますが、
急激な変化が続く場合は注意が必要です。
```

3. **通常の増加 + 90%到達予測あり**:
```
📊 ディスク使用量の増加トレンド
現在の使用率: 82.5%
増加率: +1.2%/日

このままだと、あと6日で90%に到達する見込みです。
予測到達日: 2025-12-01

💡 推奨アクション：
- 古いログファイルを削除: journalctl --vacuum-time=7d
```

4. **安全な状態**:
```
✅ ディスク使用量は安定しています
現在の使用率: 65.0%
増加率: +0.3%/日

当面は問題ありません。
```

### 既存モジュールの拡張

#### `scripts/advise.py`

新規関数を追加:

```python
def advise_disk_prediction():
    """
    ディスク使用量の予測結果を表示します。
    """
    print("\n📊 ディスク使用量の予測")
    try:
        from komon.disk_predictor import (
            load_disk_history,
            calculate_daily_average,
            predict_disk_trend,
            detect_rapid_change,
            format_prediction_message
        )
        
        # データ読み込み
        history = load_disk_history(days=7)
        if len(history) < 2:
            print("→ データが不足しています。7日分のデータが必要です。")
            return
        
        # 日次平均を計算
        daily_data = calculate_daily_average(history)
        
        # 予測計算
        prediction = predict_disk_trend(daily_data)
        rapid_change = detect_rapid_change(daily_data)
        
        # メッセージ生成と表示
        message = format_prediction_message(prediction, rapid_change)
        print(message)
        
    except Exception as e:
        print(f"⚠️ 予測計算中にエラーが発生しました: {e}")
```

`run_advise()`関数に追加:
```python
def run_advise(history_limit: int = None):
    # ... 既存のコード ...
    
    advise_log_trend(config)
    advise_disk_prediction()  # ← 追加
    advise_process_breakdown(usage)
    # ... 既存のコード ...
```

#### `scripts/weekly_report.py`

`collect_weekly_data()`関数に予測結果を追加:

```python
def collect_weekly_data() -> dict:
    # ... 既存のコード ...
    
    # ディスク使用量の予測を追加
    try:
        from komon.disk_predictor import (
            load_disk_history,
            calculate_daily_average,
            predict_disk_trend,
            detect_rapid_change
        )
        
        history = load_disk_history(days=7)
        if len(history) >= 2:
            daily_data = calculate_daily_average(history)
            prediction = predict_disk_trend(daily_data)
            rapid_change = detect_rapid_change(daily_data)
            
            result['disk_prediction'] = {
                'prediction': prediction,
                'rapid_change': rapid_change
            }
    except Exception:
        result['disk_prediction'] = None
    
    return result
```

`src/komon/report_formatter.py`に予測セクションを追加:

```python
def format_disk_prediction(disk_prediction: dict | None) -> str:
    """
    ディスク使用量の予測をフォーマットします。
    """
    if not disk_prediction:
        return ""
    
    from komon.disk_predictor import format_prediction_message
    
    prediction = disk_prediction.get('prediction', {})
    rapid_change = disk_prediction.get('rapid_change', {})
    
    message = format_prediction_message(prediction, rapid_change)
    
    return f"\n## 📊 ディスク使用量の予測\n\n{message}\n"
```

## データモデル

### 履歴データ（CSV）

既存の`data/usage_history/usage_YYYYMMDD_HHMMSS.csv`を使用:

```csv
timestamp,cpu,mem,disk
2025-11-22 09:30:00,45.2,62.8,68.5
```

### 予測結果（辞書）

```python
{
    'slope': 1.2,                    # 傾き（%/日）
    'intercept': 60.0,               # 切片
    'current_usage': 68.5,           # 現在の使用率
    'days_to_90': 18,                # 90%到達までの日数
    'prediction_date': '2025-12-10', # 90%到達予測日
    'trend': 'increasing'            # トレンド
}
```

### 急激な変化検出結果（辞書）

```python
{
    'is_rapid': True,        # 急激な変化があるか
    'change_percent': 12.5,  # 前日比の変化率（%）
    'previous_usage': 75.0,  # 前日の使用率
    'current_usage': 87.5    # 現在の使用率
}
```

## 正確性プロパティ

*プロパティとは、システムの全ての有効な実行において成立すべき特性や振る舞いのことです。これらは人間が読める仕様と機械で検証可能な正確性保証の橋渡しとなります。*


### プロパティ1: 日次平均計算の正確性
*任意の*7日分のディスク使用率データに対して、日次平均を計算した結果は、各日のデータの算術平均と一致しなければならない
**検証対象: 要件 AC-001.1**

### プロパティ2: 欠損データの処理
*任意の*欠損を含むディスク使用率データに対して、予測は利用可能なデータのみを使用して実行され、欠損データは無視されなければならない
**検証対象: 要件 AC-001.4**

### プロパティ3: 線形回帰の正確性
*任意の*2点以上のデータセットに対して、最小二乗法で計算された傾きと切片は、数学的に正しい値でなければならない
**検証対象: 要件 AC-002.1**

### プロパティ4: 90%到達予測の正確性
*任意の*増加傾向（傾き > 0）のデータに対して、90%到達予測日は `(90 - current_usage) / slope` の計算式で算出された日数と一致しなければならない
**検証対象: 要件 AC-002.2**

### プロパティ5: 前日比計算の正確性
*任意の*2日以上のデータに対して、前日比は最新日と前日のディスク使用率の差分と一致しなければならない
**検証対象: 要件 AC-003.1**

### プロパティ6: 急激な変化検出の正確性
*任意の*前日比データに対して、10%以上の増加の場合は`is_rapid=True`、10%未満の場合は`is_rapid=False`でなければならない
**検証対象: 要件 AC-003.2, AC-003.3**

### プロパティ7: 予測メッセージの完全性
*任意の*予測結果に対して、生成されるメッセージは以下の要素を含まなければならない：増加トレンドの説明、90%到達予測日（存在する場合）、急激な変化の警告（検出された場合）、推奨アクション（警告がある場合）
**検証対象: 要件 AC-004.1, AC-004.2, AC-004.3, AC-004.4**

### プロパティ8: 警告の優先度順表示
*任意の*複数の警告を含む予測結果に対して、メッセージは優先度の高い順（急激な変化 > 90%到達予測 > 通常の増加）に表示されなければならない
**検証対象: 要件 AC-005.5**

## エラーハンドリング

### エラーケース1: データ不足

**状況**: 過去7日分のデータが2件未満

**処理**:
1. 予測計算をスキップ
2. 「データが不足しています。7日分のデータが必要です。」というメッセージを表示
3. 他の助言機能は継続

### エラーケース2: 不正なデータ

**状況**: ディスク使用率が数値として不正（文字列、NULL等）

**処理**:
1. そのレコードをスキップ
2. エラーをログに記録
3. 利用可能なデータで予測を継続

### エラーケース3: ファイル読み込みエラー

**状況**: `usage_history`ディレクトリが存在しない、またはファイルが読めない

**処理**:
1. 空のデータセットとして処理
2. 「データが不足しています」というメッセージを表示
3. 他の助言機能は継続

### エラーケース4: 予測計算エラー

**状況**: 線形回帰計算中に例外が発生

**処理**:
1. エラーをログに記録
2. 「予測計算中にエラーが発生しました」というメッセージを表示
3. 他の助言機能は継続

## テスト戦略

### プロパティベーステスト

**使用ライブラリ**: `hypothesis`

**テスト対象**:
1. `calculate_daily_average()` - 日次平均計算の正確性
2. `predict_disk_trend()` - 線形回帰と予測日計算の正確性
3. `detect_rapid_change()` - 前日比と急激な変化検出の正確性
4. `format_prediction_message()` - メッセージの完全性と優先度順

**テスト設定**:
- 各テストは最低100回実行
- データ生成範囲: ディスク使用率 0-100%、日数 2-30日

**プロパティテストの例**:

```python
from hypothesis import given, strategies as st
from datetime import date, timedelta

@given(
    st.lists(
        st.tuples(
            st.dates(min_value=date(2025, 1, 1), max_value=date(2025, 12, 31)),
            st.floats(min_value=0.0, max_value=100.0)
        ),
        min_size=2,
        max_size=30
    )
)
def test_linear_regression_accuracy(data):
    """
    **Feature: disk-trend-prediction, Property 3: 線形回帰の正確性**
    
    任意のデータセットに対して、最小二乗法で計算された傾きと切片は
    数学的に正しい値でなければならない
    """
    # テスト実装
    pass
```

### ユニットテスト

**テスト対象**:
1. `load_disk_history()` - ファイル読み込みとフィルタリング
2. エッジケース:
   - データ不足（1件以下）
   - 全て同一値
   - 傾きがゼロまたは負
   - 既に90%以上
   - 予測日が100年以上先
   - 前日データなし
   - 減少傾向

**テストケース例**:

```python
def test_load_disk_history_insufficient_data():
    """データが不足している場合、空リストを返す"""
    # テスト実装
    pass

def test_predict_disk_trend_all_same_values():
    """全て同一値の場合、傾きがゼロになる"""
    # テスト実装
    pass

def test_detect_rapid_change_decreasing():
    """減少傾向の場合、急激な変化として検出されない"""
    # テスト実装
    pass
```

### 統合テスト

**テスト対象**:
1. `advise.py` - `advise_disk_prediction()`関数の動作
2. `weekly_report.py` - 週次レポートへの統合
3. エンドツーエンド:
   - データ読み込み → 予測計算 → メッセージ生成 → 表示

**テストケース例**:

```python
def test_advise_disk_prediction_integration():
    """adviseコマンドで予測結果が表示される"""
    # テスト実装
    pass

def test_weekly_report_includes_prediction():
    """週次レポートに予測結果が含まれる"""
    # テスト実装
    pass
```

### テストカバレッジ目標

- 全体: 95%以上
- 新規モジュール（`disk_predictor.py`）: 98%以上
- エッジケース: 全てカバー

## 実装の考慮事項

### パフォーマンス

- 過去7日分のデータ読み込みは高速（< 100ms）
- 線形回帰計算は軽量（< 10ms）
- `advise`コマンドの実行時間への影響は最小限

### 拡張性

- 将来的に予測日数を設定可能にする余地を残す
- 他のメトリクス（CPU、メモリ）への拡張を考慮した設計

### 保守性

- 関数は単一責任の原則に従う
- 各関数は独立してテスト可能
- エラーハンドリングは一貫性を保つ

### セキュリティ

- ファイル読み込み時のパストラバーサル対策
- 数値変換時の例外処理

## 依存関係

### 既存モジュール

- `src/komon/weekly_data.py` - データ読み込みロジックを参考
- `scripts/advise.py` - 助言表示の統合先
- `scripts/weekly_report.py` - 週次レポートの統合先

### 外部ライブラリ

- `datetime` - 日付計算
- `pathlib` - ファイルパス操作
- `csv` - CSVファイル読み込み
- `hypothesis` - プロパティベーステスト（開発依存）

## 実装順序

1. `disk_predictor.py` の基本関数実装
   - `load_disk_history()`
   - `calculate_daily_average()`
2. 予測ロジックの実装
   - `predict_disk_trend()`
   - `detect_rapid_change()`
3. メッセージ生成の実装
   - `format_prediction_message()`
4. プロパティベーステストの作成
5. ユニットテストの作成
6. `advise.py` への統合
7. `weekly_report.py` への統合
8. 統合テストの作成
9. ドキュメント更新

## 参考資料

- 線形回帰（最小二乗法）: https://ja.wikipedia.org/wiki/最小二乗法
- Hypothesis ドキュメント: https://hypothesis.readthedocs.io/
- 既存の週次レポート実装: `src/komon/weekly_data.py`
