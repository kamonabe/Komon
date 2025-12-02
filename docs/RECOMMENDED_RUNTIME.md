# 対象環境（Recommended Runtime）

## 基本方針

Komonは以下の環境での動作を**想定**しています。

**重要**: これは「サポート」ではなく「想定環境」です。上記以外の環境でも動作する可能性がありますが、動作保証はしていません。

---

## 対象環境

### Python

- **バージョン**: 3.10以上
- **推奨**: 3.11, 3.12

**理由**:
- Python 3.10は2026年10月までサポート
- 型ヒント、match文などの新機能を活用
- パフォーマンスの向上

### オペレーティングシステム

**必須条件**: systemdが使えるLinux

**想定ディストリビューション**:
- AlmaLinux 9+
- Rocky Linux 9+
- Ubuntu 22.04+
- Amazon Linux 2023+

**理由**:
- systemd統一でログ取得が簡素化（journalctl）
- Python 3.10以上が標準またはインストール可能
- 長期サポート（LTS）が提供されている

---

## 対象外環境

以下の環境は**対象外**です：

### Amazon Linux 2
- **理由**: Python 2.7が標準、サポート寿命が短い
- **代替**: Amazon Linux 2023を推奨

### CentOS 7以前
- **理由**: systemd未対応またはPython 3.10未対応
- **代替**: AlmaLinux 9+、Rocky Linux 9+を推奨

### Windows、macOS
- **現状**: 対象外
- **将来**: 要望が多ければ検討

---

## 各ディストリビューションでの動作確認状況

### AlmaLinux 9+ ✅
- **動作確認**: 完了（開発環境）
- **Python**: 3.9標準、3.10+はEPEL
- **systemd**: 対応
- **インストール**:
  ```bash
  sudo dnf install python3.11
  sudo dnf install python3.11-pip
  ```

### Rocky Linux 9+ ✅
- **動作確認**: 未実施（AlmaLinuxと互換性あり）
- **Python**: 3.9標準、3.10+はEPEL
- **systemd**: 対応
- **インストール**:
  ```bash
  sudo dnf install python3.11
  sudo dnf install python3.11-pip
  ```

### Ubuntu 22.04+ ⚠️
- **動作確認**: 未実施（systemd対応のため動作する見込み）
- **Python**: 3.10標準
- **systemd**: 対応
- **インストール**:
  ```bash
  sudo apt update
  sudo apt install python3.10
  sudo apt install python3-pip
  ```

### Amazon Linux 2023+ ⚠️
- **動作確認**: 未実施（systemd対応のため動作する見込み）
- **Python**: 3.9標準、3.11も利用可能
- **systemd**: 対応
- **インストール**:
  ```bash
  sudo dnf install python3.11
  sudo dnf install python3.11-pip
  ```

**凡例**:
- ✅ 動作確認済み
- ⚠️ 動作する見込み（未確認）
- ❌ 動作しない

---

## インストール手順の差異

### RHEL系（AlmaLinux, Rocky Linux, Amazon Linux）

```bash
# Python 3.11のインストール
sudo dnf install python3.11 python3.11-pip

# Komonのインストール
pip3.11 install komon

# または開発版
git clone https://github.com/kamonabe/Komon.git
cd Komon
pip3.11 install -e .
```

### Debian系（Ubuntu）

```bash
# Python 3.10のインストール（標準で入っている場合が多い）
sudo apt update
sudo apt install python3.10 python3-pip

# Komonのインストール
pip3 install komon

# または開発版
git clone https://github.com/kamonabe/Komon.git
cd Komon
pip3 install -e .
```

---

## 依存パッケージ

### 必須パッケージ

```
psutil>=5.9.0      # システムリソース情報取得
PyYAML>=6.0        # 設定ファイル読み込み
requests>=2.31.0   # HTTP通信（Slack/Email通知）
```

### 開発用パッケージ

```
pytest>=7.4.0           # テストフレームワーク
pytest-cov>=4.1.0       # カバレッジ測定
hypothesis>=6.82.0      # プロパティベーステスト
freezegun>=1.2.2        # 時刻モック
```

---

## トラブルシューティング

### Python 3.10が見つからない

**RHEL系**:
```bash
# EPELリポジトリを有効化
sudo dnf install epel-release
sudo dnf install python3.11
```

**Debian系**:
```bash
# deadsnakesリポジトリを追加（Ubuntu 20.04以前）
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10
```

### systemdが使えない

Komonはsystemd（journalctl）を前提としています。systemdが使えない環境では、一部機能が動作しない可能性があります。

**確認方法**:
```bash
systemctl --version
```

### パッケージのインストールに失敗する

**権限エラー**:
```bash
# ユーザーローカルにインストール
pip3 install --user komon
```

**依存関係エラー**:
```bash
# 開発用パッケージをインストール
sudo dnf install python3-devel gcc
# または
sudo apt install python3-dev build-essential
```

---

## 動作確認方法

インストール後、以下のコマンドで動作確認できます：

```bash
# バージョン確認
komon --version

# 設定ファイルのサンプル作成
cp config/settings.yml.sample settings.yml

# 動作確認（1回実行）
python scripts/main.py

# アドバイス表示
komon advise
```

---

## フィードバック

他のディストリビューションでの動作確認報告を歓迎します！

**報告方法**:
1. GitHub Issue: https://github.com/kamonabe/Komon/issues
2. 報告内容:
   - ディストリビューション名とバージョン
   - Pythonバージョン
   - 動作状況（成功/失敗）
   - エラーメッセージ（失敗の場合）

---

## 更新履歴

- 2025-11-30: 初版作成
