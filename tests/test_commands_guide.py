"""
src/komon/commands/guide.py のテスト

ガイドコマンドの関数をテストします。
"""

import unittest
import tempfile
import io
from unittest.mock import patch
from io import StringIO
from pathlib import Path

from src.komon.commands.guide import (
    show_menu,
    guide_1,
    guide_2,
    guide_3,
    guide_4,
    guide_5,
    guide_6,
    run_guide
)


class TestGuideCommands(unittest.TestCase):
    """guide.pyの関数テスト"""
    
    def test_show_menu_display(self):
        """メニュー表示のテスト"""
        with patch('builtins.input', return_value='1'):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                result = show_menu()
                output = fake_out.getvalue()
        
        # メニュー項目が表示されることを確認
        self.assertIn("Komon ガイドセンター", output)
        self.assertIn("[1] Komonってなに？", output)
        self.assertIn("[2] 初期セットアップ", output)
        self.assertIn("[0] 終了", output)
        
        # 入力値が返されることを確認
        self.assertEqual(result, '1')
    
    def test_show_menu_different_inputs(self):
        """異なる入力値のテスト"""
        test_inputs = ['0', '2', '3', '4', '5', '6']
        
        for test_input in test_inputs:
            with patch('builtins.input', return_value=test_input):
                result = show_menu()
                self.assertEqual(result, test_input)
    
    def test_show_menu_whitespace_handling(self):
        """空白文字の処理テスト"""
        with patch('builtins.input', return_value='  2  '):
            result = show_menu()
            self.assertEqual(result, '2')  # strip()されることを確認
    
    def test_guide_1_display(self):
        """guide_1の表示内容テスト"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            guide_1()
            output = fake_out.getvalue()
        
        # 重要なキーワードが含まれることを確認
        self.assertIn("Komonってなに？", output)
        self.assertIn("軽量SOAR風", output)
        self.assertIn("監視＆運用支援ツール", output)
        self.assertIn("CPU・メモリ・ディスク", output)
        self.assertIn("Slack", output)


    def test_guide_2_setup_instructions(self):
        """初期セットアップガイドのテスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_2()
        
        output = captured_output.getvalue()
        
        # セットアップ手順が表示されることを確認
        self.assertIn("🔹 初期セットアップの手順", output)
        self.assertIn("pip install komon", output)
        self.assertIn("komon initial", output)
    
    def test_guide_3_commands_list(self):
        """コマンド一覧ガイドのテスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_3()
        
        output = captured_output.getvalue()
        
        # コマンド一覧が表示されることを確認
        self.assertIn("🔹 コマンド一覧と使い方", output)
        self.assertIn("komon advise", output)
        self.assertIn("komon status", output)
        self.assertIn("komon initial", output)
        self.assertIn("komon guide", output)
    
    def test_guide_4_cron_examples(self):
        """cron登録例ガイドのテスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_4()
        
        output = captured_output.getvalue()
        
        # cron例が表示されることを確認
        self.assertIn("🔹 cron登録の例", output)
        self.assertIn("* * * * *", output)
        self.assertIn("komon advise", output)
    
    def test_guide_5_notification_settings(self):
        """通知設定ガイドのテスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_5()
        
        output = captured_output.getvalue()
        
        # 通知設定説明が表示されることを確認
        self.assertIn("🔹 通知設定の方法", output)
        self.assertIn("settings.yml", output)
        self.assertIn("notifications", output)
    
    def test_guide_6_faq(self):
        """FAQ ガイドのテスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_6()
        
        output = captured_output.getvalue()
        
        # FAQ内容が表示されることを確認
        self.assertIn("🔹 よくある質問とトラブル対応", output)
        self.assertIn("settings.yml を作り直したい", output)
        self.assertIn("Slack通知が届かない", output)
    
    @patch('builtins.input')
    def test_run_guide_complete_flow(self, mock_input):
        """ガイド全体のフローテスト"""
        # 各ガイドを順番に選択してから終了
        mock_input.side_effect = ['1', '2', '3', '4', '5', '6', '0']
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                run_guide(config_dir)
            
            output = captured_output.getvalue()
            
            # 各ガイドの内容が表示されることを確認
            self.assertIn("Komonは、軽量SOAR風の監視", output)  # guide_1
            self.assertIn("初期セットアップの手順", output)      # guide_2
            self.assertIn("コマンド一覧と使い方", output)        # guide_3
            self.assertIn("cron登録の例", output)             # guide_4
            self.assertIn("通知設定の方法", output)            # guide_5
            self.assertIn("よくある質問とトラブル対応", output)   # guide_6
            self.assertIn("👋 ご利用ありがとうございました", output)
    
    @patch('builtins.input')
    def test_run_guide_invalid_choice(self, mock_input):
        """無効な選択肢のテスト"""
        mock_input.side_effect = ['9', '0']  # 無効な選択肢の後に終了
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                run_guide(config_dir)
            
            output = captured_output.getvalue()
            
            # エラーメッセージが表示されることを確認
            self.assertIn("⚠️ 無効な選択です", output)
            self.assertIn("👋 ご利用ありがとうございました", output)
    def test_guide_2_display(self):
        """guide_2関数の表示テスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_2()
        
        output = captured_output.getvalue()
        self.assertIn("初期セットアップの手順", output)
        self.assertIn("pip install komon", output)
        self.assertIn("komon initial", output)
        self.assertIn("settings.yml", output)

    def test_guide_3_display(self):
        """guide_3関数の表示テスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_3()
        
        output = captured_output.getvalue()
        self.assertIn("コマンド一覧と使い方", output)
        self.assertIn("komon advise", output)
        self.assertIn("komon status", output)
        self.assertIn("komon initial", output)
        self.assertIn("komon guide", output)

    def test_guide_4_display(self):
        """guide_4関数の表示テスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_4()
        
        output = captured_output.getvalue()
        self.assertIn("cron登録の例", output)
        self.assertIn("* * * * *", output)
        self.assertIn("komon advise", output)
        self.assertIn("フルパス", output)

    def test_guide_5_display(self):
        """guide_5関数の表示テスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_5()
        
        output = captured_output.getvalue()
        self.assertIn("通知設定の方法", output)
        self.assertIn("Slack", output)
        self.assertIn("メール", output)
        self.assertIn("settings.yml", output)
        self.assertIn("notifications", output)

    def test_guide_6_display(self):
        """guide_6関数の表示テスト"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            guide_6()
        
        output = captured_output.getvalue()
        self.assertIn("よくある質問とトラブル対応", output)
        self.assertIn("settings.yml を作り直したい", output)
        self.assertIn("Slack通知が届かない", output)
        self.assertIn("cronが動いていない", output)
        self.assertIn("設定ファイルが見つからない", output)

    @patch('builtins.input')
    def test_run_guide_choice_1(self, mock_input):
        """run_guide関数でchoice=1のテスト"""
        mock_input.side_effect = ["1", "0"]  # 1を選択してから0で終了
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            run_guide(Path("/tmp"))
        
        output = captured_output.getvalue()
        self.assertIn("Komonってなに？", output)
        self.assertIn("軽量SOAR風", output)

    @patch('builtins.input')
    def test_run_guide_choice_2(self, mock_input):
        """run_guide関数でchoice=2のテスト"""
        mock_input.side_effect = ["2", "0"]  # 2を選択してから0で終了
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            run_guide(Path("/tmp"))
        
        output = captured_output.getvalue()
        self.assertIn("初期セットアップの手順", output)

    @patch('builtins.input')
    def test_run_guide_choice_3(self, mock_input):
        """run_guide関数でchoice=3のテスト"""
        mock_input.side_effect = ["3", "0"]  # 3を選択してから0で終了
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            run_guide(Path("/tmp"))
        
        output = captured_output.getvalue()
        self.assertIn("コマンド一覧と使い方", output)

    @patch('builtins.input')
    def test_run_guide_choice_4(self, mock_input):
        """run_guide関数でchoice=4のテスト"""
        mock_input.side_effect = ["4", "0"]  # 4を選択してから0で終了
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            run_guide(Path("/tmp"))
        
        output = captured_output.getvalue()
        self.assertIn("cron登録の例", output)

    @patch('builtins.input')
    def test_run_guide_choice_5(self, mock_input):
        """run_guide関数でchoice=5のテスト"""
        mock_input.side_effect = ["5", "0"]  # 5を選択してから0で終了
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            run_guide(Path("/tmp"))
        
        output = captured_output.getvalue()
        self.assertIn("通知設定の方法", output)

    @patch('builtins.input')
    def test_run_guide_choice_6(self, mock_input):
        """run_guide関数でchoice=6のテスト"""
        mock_input.side_effect = ["6", "0"]  # 6を選択してから0で終了
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            run_guide(Path("/tmp"))
        
        output = captured_output.getvalue()
        self.assertIn("よくある質問とトラブル対応", output)

    @patch('builtins.input')
    def test_run_guide_invalid_choice(self, mock_input):
        """run_guide関数で無効な選択のテスト"""
        mock_input.side_effect = ["9", "0"]  # 無効な選択してから0で終了
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            run_guide(Path("/tmp"))
        
        output = captured_output.getvalue()
        self.assertIn("無効な選択です", output)

    @patch('builtins.input')
    def test_run_guide_exit_message(self, mock_input):
        """run_guide関数の終了メッセージテスト"""
        mock_input.side_effect = ["0"]  # 0で終了
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            run_guide(Path("/tmp"))
        
        output = captured_output.getvalue()
        self.assertIn("ご利用ありがとうございました", output)


if __name__ == '__main__':
    unittest.main()