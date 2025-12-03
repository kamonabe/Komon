# 対象環境（Recommended Runtime）

## 基本方針

Komonは**RHEL系Linux**での動作を推奨しています。

**重要**: RHEL系以外でも動作しますが、一部機能が制限されます。これは「誤ったアドバイスをしない」というKomonの哲学に基づく設計です。

---

## 推奨環境

### Python

- **バージョン**: 3.10以上
- **推奨**: 3.11, 3.12

**理由**:
- Python 3.10は2026年10月までサポート
- 型ヒント、match文などの新機能を活用
- パフォーマンスの向上

### オペレーティングシステム

**推奨**: RHEL系Linux（systemd対応）

**推奨ディストリビューション**:
- **AlmaLinux 9+** ⭐ 最も推奨（開発環境）
- **Rocky Linux 9+** ⭐ 推奨
- **Amazon Linux 2023+** ⭐ 推奨
- Fedora 38+
- CentOS Stream 9+

**理由**:
- パッケージ管理コマンドが統一（dnf）
- ログパスが統一（/var/log/messages）
- systemd対応でログ取得が簡素化
- Python 3.10以上が標準またはインストール可能
- 長期サポート（LTS）が提供されている

## ベストエフォート対応

以下の環境でも動作しますが、一部機能が制限されます：

### Debian系Linux

**対応ディストリビューション**:
- Ubuntu 22.04+
- Debian 12+
- Raspberry Pi OS（Debian 12ベース）

**制限事項**:
- パッケージ系のアドバイスが抑制されます
  - 理由: パッケージ名の違いにより誤ったアドバイスをしてしまう可能性があるため
- ログパスが自動的に `/var/log/syslog` に切り替わります
- パッケージ管理コマンドは `sudo apt update && sudo apt upgrade` が提案されます

### その他のLinux

**対応ディストリビューション**:
- SUSE系（openSUSE Leap 15.5+等）
- Arch系（Arch Linux、Manjaro等）

**制限事項**:
- OS固有のアドバイスが制限されます
- パッケージ管理コマンドは提案されますが、検証は不十分です

---

## 非対応環境

以下の環境は**非対応**です：

### Amazon Linux 2
- **理由**: Python 2.7が標準、サポート寿命が短い
- **代替**: Amazon Linux 2023を推奨

### CentOS 7以前
- **理由**: systemd未対応またはPython 3.10未対応
- **代替**: AlmaLinux 9+、Rocky Linux 9+を推奨

### Windows ネイティブ
- **現状**: 非対応（起動時にエラーメッセージを表示して終了）
- **代替**: WSL（Windows Subsystem for Linux）での実行を推奨
- **WSL対応**: WSL環境ではLinux扱いで動作します

### macOS
- **現状**: 対象外
- **将来**: 移植版の作成は歓迎します

## OS自動判定機能

Komonは実行環境のOSを自動判定し、適切なアドバイスを提供します：

### 判定方法

1. `/etc/os-release` を読み取り
2. OSファミリを判定（rhel / debian / suse / arch / unknown）
3. 判定結果に基づいてアドバイスを出し分け

### 手動上書き

設定ファイル（`settings.yml`）で手動上書きも可能です：

```yaml
system:
  os_family: auto  # auto / rhel / debian / suse / arch / unknown
```

- `auto`: 自動判定（推奨）
- `rhel`: RHEL系として扱う
- `debian`: Debian系として扱う
- `suse`: SUSE系として扱う
- `arch`: Arch系として扱う
- `unknown`: 不明なOSとして扱う（アドバイスが制限される）

### Windows/WSL検出

- **Windows ネイティブ**: `sys.platform == 'win32'` で検出し、エラーで終了
- **WSL**: `/proc/version` に `microsoft` が含まれる場合、Linux扱いで続行

---

## 各ディストリビューションでの動作確認状況

### AlmaLinux 9+ ⭐ 最も推奨
- **動作確認**: 完了（開発環境）
- **OS判定**: `rhel` ファミリ
- **Python**: 3.9標準、3.10+はEPEL
- **systemd**: 対応
- **パッケージ管理**: `dnf`
- **ログパス**: `/var/log/messages`
- **インストール**:
  ```bash
  sudo dnf install python3.11
  sudo dnf install python3.11-pip
  ```

### Rocky Linux 9+ ⭐ 推奨
- **動作確認**: 未実施（AlmaLinuxと互換性あり）
- **OS判定**: `rhel` ファミリ
- **Python**: 3.9標準、3.10+はEPEL
- **systemd**: 対応
- **パッケージ管理**: `dnf`
- **ログパス**: `/var/log/messages`
- **インストール**:
  ```bash
  sudo dnf install python3.11
  sudo dnf install python3.11-pip
  ```

### Amazon Linux 2023+ ⭐ 推奨
- **動作確認**: 未実施（systemd対応のため動作する見込み）
- **OS判定**: `rhel` ファミリ
- **Python**: 3.9標準、3.11も利用可能
- **systemd**: 対応
- **パッケージ管理**: `dnf`
- **ログパス**: `/var/log/messages`
- **インストール**:
  ```bash
  sudo dnf install python3.11
  sudo dnf install python3.11-pip
  ```

### Ubuntu 22.04+ ⚠️ ベストエフォート
- **動作確認**: 未実施（systemd対応のため動作する見込み）
- **OS判定**: `debian` ファミリ
- **Python**: 3.10標準
- **systemd**: 対応
- **パッケージ管理**: `apt`
- **ログパス**: `/var/log/syslog`
- **制限事項**: パッケージ系アドバイスが抑制される
- **インストール**:
  ```bash
  sudo apt update
  sudo apt install python3.10
  sudo apt install python3-pip
  ```

### Raspberry Pi OS ⚠️ ベストエフォート
- **動作確認**: 未実施
- **OS判定**: `debian` ファミリ
- **Python**: 3.11標準（Debian 12ベース）
- **systemd**: 対応
- **パッケージ管理**: `apt`
- **ログパス**: `/var/log/syslog`
- **制限事項**: パッケージ系アドバイスが抑制される
- **インストール**:
  ```bash
  sudo apt update
  sudo apt install python3.11
  sudo apt install python3-pip
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
