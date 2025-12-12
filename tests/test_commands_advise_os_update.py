"""
src/komon/commands/advise.py の OS更新関連機能のテスト

OS更新アドバイス機能をテストします。
"""

import unittest
import subprocess
from unittest.mock import patch, MagicMock
from io import StringIO

from src.komon.commands.advise import advise_os_update


class TestAdviseOSUpdate(unittest.TestCase):
    """advise_os_update関数のテスト"""
    
    @patch('src.komon.commands.advise.get_os_detector')
    @patch('subprocess.run')
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('sys.stdout', new_callable=StringIO)
    def test_advise_os_update_rhel_with_security_updates(self, mock_stdout, mock_ask_yes_no, mock_subprocess, mock_get_os_detector):
        """RHEL系でセキュリティ更新がある場合のテスト"""
        # OS検出をRHELに設定
        mock_detector = MagicMock()
        mock_detector.detect_os_family.return_value = "rhel"
        mock_detector.should_show_package_advice.return_value = True
        mock_get_os_detector.return_value = mock_detector
        
        # セキュリティ更新があることをモック
        security_result = MagicMock()
        security_result.returncode = 0
        security_result.stdout = "RHSA-2023:1234: package1 security update\nRHSA-2023:5678: package2 security update\n"
        
        # 通常更新もあることをモック
        normal_result = MagicMock()
        normal_result.returncode = 100
        normal_result.stdout = "package3.x86_64\npackage4.x86_64\n"
        
        # subprocess.runの戻り値を設定
        mock_subprocess.side_effect = [security_result, normal_result]
        
        # ユーザーがセキュリティ更新を適用することを選択
        mock_ask_yes_no.return_value = True
        
        advise_os_update()
        
        output = mock_stdout.getvalue()
        
        # 出力内容を確認
        self.assertIn("① セキュリティパッチの確認", output)
        self.assertIn("セキュリティ更新が", output)
        self.assertIn("RHSA-2023:1234", output)
        self.assertIn("RHSA-2023:5678", output)
        self.assertIn("セキュリティアップデートを適用しました", output)
        
        # subprocess.runが正しく呼ばれたことを確認
        self.assertEqual(mock_subprocess.call_count, 3)  # updateinfo list, check-update, upgrade --security
    
    @patch('src.komon.commands.advise.get_os_detector')
    @patch('subprocess.run')
    @patch('sys.stdout', new_callable=StringIO)
    def test_advise_os_update_rhel_no_security_updates(self, mock_stdout, mock_subprocess, mock_get_os_detector):
        """RHEL系でセキュリティ更新がない場合のテスト"""
        # OS検出をRHELに設定
        mock_detector = MagicMock()
        mock_detector.detect_os_family.return_value = "rhel"
        mock_detector.should_show_package_advice.return_value = True
        mock_get_os_detector.return_value = mock_detector
        
        # セキュリティ更新がないことをモック
        security_result = MagicMock()
        security_result.returncode = 0
        security_result.stdout = ""
        
        # 通常更新もないことをモック
        normal_result = MagicMock()
        normal_result.returncode = 0
        normal_result.stdout = ""
        
        mock_subprocess.side_effect = [security_result, normal_result]
        
        advise_os_update()
        
        output = mock_stdout.getvalue()
        
        # 出力内容を確認
        self.assertIn("① セキュリティパッチの確認", output)
        self.assertIn("セキュリティ更新はありません", output)
        self.assertIn("パッケージは最新の状態です", output)
    
    @patch('src.komon.commands.advise.get_os_detector')
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('sys.stdout', new_callable=StringIO)
    def test_advise_os_update_debian(self, mock_stdout, mock_ask_yes_no, mock_get_os_detector):
        """Debian系の場合のテスト"""
        # OS検出をDebianに設定
        mock_detector = MagicMock()
        mock_detector.detect_os_family.return_value = "debian"
        mock_detector.should_show_package_advice.return_value = True
        mock_get_os_detector.return_value = mock_detector
        
        # ユーザーが更新を拒否
        mock_ask_yes_no.return_value = False
        
        advise_os_update()
        
        output = mock_stdout.getvalue()
        
        # 出力内容を確認
        self.assertIn("① パッケージ更新の確認", output)
        self.assertIn("Debian系Linuxでは以下のコマンドで更新を確認できます", output)
        self.assertIn("sudo apt update", output)
        self.assertIn("sudo apt list --upgradable", output)
        self.assertIn("パッケージ更新は保留されました", output)
    
    @patch('src.komon.commands.advise.get_os_detector')
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('subprocess.run')
    @patch('sys.stdout', new_callable=StringIO)
    def test_advise_os_update_debian_with_updates(self, mock_stdout, mock_subprocess, mock_ask_yes_no, mock_get_os_detector):
        """Debian系でユーザーが更新を実行する場合のテスト"""
        # OS検出をDebianに設定
        mock_detector = MagicMock()
        mock_detector.detect_os_family.return_value = "debian"
        mock_detector.should_show_package_advice.return_value = True
        mock_get_os_detector.return_value = mock_detector
        
        # ユーザーが更新を実行することを選択
        mock_ask_yes_no.return_value = True
        
        advise_os_update()
        
        output = mock_stdout.getvalue()
        
        # 出力内容を確認
        self.assertIn("① パッケージ更新の確認", output)
        self.assertIn("パッケージ更新を実行します", output)
        self.assertIn("パッケージ更新が完了しました", output)
        
        # subprocess.runが2回呼ばれることを確認（apt update, apt upgrade）
        self.assertEqual(mock_subprocess.call_count, 2)
    
    @patch('src.komon.commands.advise.get_os_detector')
    @patch('sys.stdout', new_callable=StringIO)
    def test_advise_os_update_unknown_os(self, mock_stdout, mock_get_os_detector):
        """未知のOSの場合のテスト"""
        # OS検出を未知に設定
        mock_detector = MagicMock()
        mock_detector.detect_os_family.return_value = "unknown"
        mock_detector.should_show_package_advice.return_value = False
        mock_detector.get_package_manager_command.return_value = "pkg update"
        mock_get_os_detector.return_value = mock_detector
        
        advise_os_update()
        
        output = mock_stdout.getvalue()
        
        # 出力内容を確認
        self.assertIn("① パッケージ更新の確認", output)
        self.assertIn("OSファミリが不明なため", output)
        self.assertIn("pkg update", output)
    
    @patch('src.komon.commands.advise.get_os_detector')
    @patch('subprocess.run')
    @patch('sys.stdout', new_callable=StringIO)
    def test_advise_os_update_rhel_command_not_found(self, mock_stdout, mock_subprocess, mock_get_os_detector):
        """RHEL系でdnfコマンドが見つからない場合のテスト"""
        # OS検出をRHELに設定
        mock_detector = MagicMock()
        mock_detector.detect_os_family.return_value = "rhel"
        mock_detector.should_show_package_advice.return_value = True
        mock_get_os_detector.return_value = mock_detector
        
        # FileNotFoundErrorを発生させる
        mock_subprocess.side_effect = FileNotFoundError("dnf not found")
        
        advise_os_update()
        
        output = mock_stdout.getvalue()
        
        # エラーメッセージを確認
        self.assertIn("dnf が見つかりません", output)
    
    @patch('src.komon.commands.advise.get_os_detector')
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('subprocess.run')
    @patch('sys.stdout', new_callable=StringIO)
    def test_advise_os_update_debian_command_not_found(self, mock_stdout, mock_subprocess, mock_ask_yes_no, mock_get_os_detector):
        """Debian系でaptコマンドが見つからない場合のテスト"""
        # OS検出をDebianに設定
        mock_detector = MagicMock()
        mock_detector.detect_os_family.return_value = "debian"
        mock_detector.should_show_package_advice.return_value = True
        mock_get_os_detector.return_value = mock_detector
        
        # ユーザーが更新を実行することを選択
        mock_ask_yes_no.return_value = True
        
        # FileNotFoundErrorを発生させる
        mock_subprocess.side_effect = FileNotFoundError("apt not found")
        
        advise_os_update()
        
        output = mock_stdout.getvalue()
        
        # エラーメッセージを確認
        self.assertIn("① パッケージ更新の確認", output)
        self.assertIn("apt が見つかりません", output)
    
    @patch('src.komon.commands.advise.get_os_detector')
    @patch('subprocess.run')
    @patch('src.komon.commands.advise.ask_yes_no')
    @patch('sys.stdout', new_callable=StringIO)
    def test_advise_os_update_rhel_user_declines_security_update(self, mock_stdout, mock_ask_yes_no, mock_subprocess, mock_get_os_detector):
        """RHEL系でユーザーがセキュリティ更新を拒否する場合のテスト"""
        # OS検出をRHELに設定
        mock_detector = MagicMock()
        mock_detector.detect_os_family.return_value = "rhel"
        mock_detector.should_show_package_advice.return_value = True
        mock_get_os_detector.return_value = mock_detector
        
        # セキュリティ更新があることをモック
        security_result = MagicMock()
        security_result.returncode = 0
        security_result.stdout = "RHSA-2023:1234: package1 security update\n"
        
        # 通常更新もあることをモック
        normal_result = MagicMock()
        normal_result.returncode = 0
        normal_result.stdout = ""
        
        mock_subprocess.side_effect = [security_result, normal_result]
        
        # ユーザーがセキュリティ更新を拒否
        mock_ask_yes_no.return_value = False
        
        advise_os_update()
        
        output = mock_stdout.getvalue()
        
        # 出力内容を確認
        self.assertIn("セキュリティアップデートは保留されました", output)
        
        # upgrade --securityが呼ばれないことを確認（2回のみ：updateinfo list, check-update）
        self.assertEqual(mock_subprocess.call_count, 2)


if __name__ == '__main__':
    unittest.main()