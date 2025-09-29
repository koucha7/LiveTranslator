"""
GUI Application for Y        # 設定値の保存用（無料版がデフォルト）
        self.settings = {
            'openai_api_key': '',
            'google_translate_api_key': '',
            'whisper_model': 'base',
            'use_whisper_api': False,
            'translation_engine': 'google',  # 無料版Google Translateがデフォルト
            'segment_duration': 10,
            'sample_rate': 16000,
            'chunk_size': 1024,
        } Translator
リアルタイム文字起こし・翻訳結果を表示するGUIアプリケーション
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import json
import os
from datetime import datetime
from typing import Optional

from .live_translator import LiveTranslator
from .config import config


class ConfigDialog:
    """設定ダイアログクラス"""
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.dialog = None
        
        # 設定値の保存用
        self.settings = {
            'openai_api_key': '',
            'google_translate_api_key': '',
            'whisper_model': 'base',
            'use_whisper_api': False,
            'translation_engine': 'google',  # デフォルトは無料版
            'segment_duration': 10,
            'sample_rate': 16000,
            'chunk_size': 1024,
        }
        
        self.create_dialog()
        
    def create_dialog(self):
        """設定ダイアログを作成"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("LiveTranslator - 設定")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # 現在の設定を読み込み
        self.load_current_settings()
        
        # ウィンドウを中央に配置
        self.center_window()
        
        # UIを作成
        self.create_widgets()
        
        # ウィンドウを表示
        self.dialog.focus_set()
        
    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
    def load_current_settings(self):
        """現在の設定を読み込み"""
        try:
            # configから現在の設定を取得
            config_dict = config.to_dict()
            
            # APIキーを取得
            api_keys = config.get_api_keys()
            self.settings['openai_api_key'] = api_keys.get('openai', '')
            self.settings['google_translate_api_key'] = api_keys.get('google_translate', '')
            
            # その他の設定
            if 'whisper' in config_dict:
                self.settings['whisper_model'] = config_dict['whisper'].get('model_name', 'base')
                self.settings['use_whisper_api'] = config_dict['whisper'].get('use_api', False)
                
            if 'translation' in config_dict:
                self.settings['translation_engine'] = config_dict['translation'].get('engine', 'google')
                
            if 'audio' in config_dict:
                self.settings['segment_duration'] = config_dict['audio'].get('segment_duration', 10)
                self.settings['sample_rate'] = config_dict['audio'].get('sample_rate', 16000)
                self.settings['chunk_size'] = config_dict['audio'].get('chunk_size', 1024)
                
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
            
    def create_widgets(self):
        """UIウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タブコントロール
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # APIキータブ
        self.create_api_tab(notebook)
        
        # 音声認識タブ
        self.create_speech_tab(notebook)
        
        # 翻訳タブ
        self.create_translation_tab(notebook)
        
        # 音声処理タブ
        self.create_audio_tab(notebook)
        
        # ボタンフレーム
        self.create_buttons(main_frame)
        
    def create_api_tab(self, parent):
        """APIキータブを作成"""
        api_frame = ttk.Frame(parent)
        parent.add(api_frame, text="APIキー")
        
        # 無料版についての説明
        free_frame = ttk.LabelFrame(api_frame, text="💡 無料版について", padding=10)
        free_frame.pack(fill=tk.X, padx=10, pady=5)
        
        free_text = """APIキーが未設定の場合、完全無料で利用できます：
• 音声認識: Whisperローカルモデル使用
• 翻訳: Google Translate無料版使用
• 追加料金: なし"""
        
        ttk.Label(free_frame, text=free_text, font=("Yu Gothic UI", 9), 
                 foreground="green").pack(anchor=tk.W)
        
        # APIキー設定フレーム
        ttk.Label(api_frame, text="APIキー設定（オプション）", font=("Yu Gothic UI", 12, "bold")).pack(pady=(20, 10))
        
        # OpenAI APIキー
        openai_frame = ttk.LabelFrame(api_frame, text="OpenAI API", padding=10)
        openai_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # OpenAI APIキー入力欄
        openai_key_frame = ttk.Frame(openai_frame)
        openai_key_frame.pack(fill=tk.X)
        
        ttk.Label(openai_key_frame, text="APIキー:").pack(anchor=tk.W)
        openai_entry_frame = ttk.Frame(openai_key_frame)
        openai_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.openai_key_var = tk.StringVar(value=self.settings['openai_api_key'])
        self.openai_entry = ttk.Entry(openai_entry_frame, textvariable=self.openai_key_var, show="*")
        self.openai_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.openai_show_var = tk.BooleanVar()
        ttk.Checkbutton(openai_entry_frame, text="表示", variable=self.openai_show_var, 
                       command=self.toggle_openai_visibility).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(openai_frame, text="音声認識（Whisper API）と翻訳（GPT）に使用（オプション）\n未設定の場合：ローカルWhisper + Google翻訳無料版を使用\n料金目安: 1時間のライブで約60-105円", 
                 font=("Yu Gothic UI", 9), foreground="gray").pack(anchor=tk.W, pady=(10, 0))
        
        # Google Translate APIキー
        google_frame = ttk.LabelFrame(api_frame, text="Google Translate API (オプション)", padding=10)
        google_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Google APIキー入力欄
        google_key_frame = ttk.Frame(google_frame)
        google_key_frame.pack(fill=tk.X)
        
        ttk.Label(google_key_frame, text="APIキー:").pack(anchor=tk.W)
        google_entry_frame = ttk.Frame(google_key_frame)
        google_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.google_key_var = tk.StringVar(value=self.settings['google_translate_api_key'])
        self.google_entry = ttk.Entry(google_entry_frame, textvariable=self.google_key_var, show="*")
        self.google_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.google_show_var = tk.BooleanVar()
        ttk.Checkbutton(google_entry_frame, text="表示", variable=self.google_show_var,
                       command=self.toggle_google_visibility).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(google_frame, text="Google翻訳エンジンを使用する場合に設定（無料版も利用可能）\n設定しない場合は無料のgoogletrans使用", 
                 font=("Yu Gothic UI", 9), foreground="gray").pack(anchor=tk.W, pady=(10, 0))
        
        # APIキー取得リンクの情報
        info_frame = ttk.LabelFrame(api_frame, text="APIキーの取得方法", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # OpenAI情報
        openai_info_frame = ttk.Frame(info_frame)
        openai_info_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(openai_info_frame, text="【OpenAI API】", font=("Yu Gothic UI", 9, "bold")).pack(anchor=tk.W)
        openai_link_frame = ttk.Frame(openai_info_frame)
        openai_link_frame.pack(fill=tk.X)
        
        ttk.Label(openai_link_frame, text="取得URL: ", font=("Yu Gothic UI", 9)).pack(side=tk.LEFT)
        ttk.Button(openai_link_frame, text="https://platform.openai.com/account/api-keys", 
                  command=lambda: self.open_url("https://platform.openai.com/account/api-keys")).pack(side=tk.LEFT)
        
        # Google情報  
        google_info_frame = ttk.Frame(info_frame)
        google_info_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(google_info_frame, text="【Google Translate API】", font=("Yu Gothic UI", 9, "bold")).pack(anchor=tk.W)
        google_link_frame = ttk.Frame(google_info_frame)
        google_link_frame.pack(fill=tk.X)
        
        ttk.Label(google_link_frame, text="取得URL: ", font=("Yu Gothic UI", 9)).pack(side=tk.LEFT)
        ttk.Button(google_link_frame, text="https://cloud.google.com/translate", 
                  command=lambda: self.open_url("https://cloud.google.com/translate/docs/setup")).pack(side=tk.LEFT)
        
        ttk.Label(info_frame, text="※ Google APIキーは任意です。設定しない場合は無料版を使用します。", 
                 font=("Yu Gothic UI", 9), foreground="green").pack(anchor=tk.W, pady=(10, 0))
        
    def create_speech_tab(self, parent):
        """音声認識タブを作成"""
        speech_frame = ttk.Frame(parent)
        parent.add(speech_frame, text="音声認識")
        
        ttk.Label(speech_frame, text="Whisper設定", font=("Yu Gothic UI", 12, "bold")).pack(pady=(10, 20))
        
        # Whisperモデル選択
        model_frame = ttk.LabelFrame(speech_frame, text="Whisperモデル", padding=10)
        model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(model_frame, text="モデルサイズ:").pack(anchor=tk.W)
        self.whisper_model_var = tk.StringVar(value=self.settings['whisper_model'])
        model_combo = ttk.Combobox(model_frame, textvariable=self.whisper_model_var, 
                                  values=['tiny', 'base', 'small', 'medium', 'large'], 
                                  state="readonly", width=20)
        model_combo.pack(anchor=tk.W, pady=(5, 10))
        
        ttk.Label(model_frame, text="大きいモデルほど精度が高いが処理時間が長くなります", 
                 font=("Yu Gothic UI", 9), foreground="gray").pack(anchor=tk.W)
        
        # API使用設定
        api_frame = ttk.LabelFrame(speech_frame, text="API設定", padding=10)
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.use_whisper_api_var = tk.BooleanVar(value=self.settings['use_whisper_api'])
        ttk.Checkbutton(api_frame, text="OpenAI Whisper APIを使用", 
                       variable=self.use_whisper_api_var).pack(anchor=tk.W)
        
        ttk.Label(api_frame, text="チェックすればクラウドAPI、未チェックはローカルモデルを使用", 
                 font=("Yu Gothic UI", 9), foreground="gray").pack(anchor=tk.W)
        
    def create_translation_tab(self, parent):
        """翻訳タブを作成"""
        translation_frame = ttk.Frame(parent)
        parent.add(translation_frame, text="翻訳")
        
        ttk.Label(translation_frame, text="翻訳エンジン設定", font=("Yu Gothic UI", 12, "bold")).pack(pady=(10, 20))
        
        # 翻訳エンジン選択
        engine_frame = ttk.LabelFrame(translation_frame, text="翻訳エンジン", padding=10)
        engine_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(engine_frame, text="エンジン:").pack(anchor=tk.W)
        self.translation_engine_var = tk.StringVar(value=self.settings['translation_engine'])
        engine_combo = ttk.Combobox(engine_frame, textvariable=self.translation_engine_var,
                                   values=['google', 'openai'], state="readonly", width=20)
        engine_combo.pack(anchor=tk.W, pady=(5, 10))
        
        ttk.Label(engine_frame, text="Google: Google翻訳による高速処理（無料）\nOpenAI: GPTによる高品質翻訳（APIキー必要）", 
                 font=("Yu Gothic UI", 9), foreground="gray").pack(anchor=tk.W)
        
    def create_audio_tab(self, parent):
        """音声処理タブを作成"""
        audio_frame = ttk.Frame(parent)
        parent.add(audio_frame, text="音声処理")
        
        ttk.Label(audio_frame, text="音声処理設定", font=("Yu Gothic UI", 12, "bold")).pack(pady=(10, 20))
        
        # セグメント長設定
        segment_frame = ttk.LabelFrame(audio_frame, text="音声セグメント", padding=10)
        segment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(segment_frame, text="セグメント長 (秒):").pack(anchor=tk.W)
        self.segment_duration_var = tk.IntVar(value=self.settings['segment_duration'])
        segment_spin = ttk.Spinbox(segment_frame, from_=5, to=60, textvariable=self.segment_duration_var, width=10)
        segment_spin.pack(anchor=tk.W, pady=(5, 10))
        
        ttk.Label(segment_frame, text="音声を分割する長さ（短いと応答性向上、長いと精度向上）", 
                 font=("Yu Gothic UI", 9), foreground="gray").pack(anchor=tk.W)
        
        # サンプルレート設定
        rate_frame = ttk.LabelFrame(audio_frame, text="オーディオ品質", padding=10)
        rate_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(rate_frame, text="サンプルレート (Hz):").pack(anchor=tk.W)
        self.sample_rate_var = tk.IntVar(value=self.settings['sample_rate'])
        rate_combo = ttk.Combobox(rate_frame, textvariable=self.sample_rate_var,
                                 values=[8000, 16000, 22050, 44100], state="readonly", width=10)
        rate_combo.pack(anchor=tk.W, pady=(5, 10))
        
        ttk.Label(rate_frame, text="チャンクサイズ:").pack(anchor=tk.W)
        self.chunk_size_var = tk.IntVar(value=self.settings['chunk_size'])
        chunk_spin = ttk.Spinbox(rate_frame, from_=512, to=4096, increment=512, 
                                textvariable=self.chunk_size_var, width=10)
        chunk_spin.pack(anchor=tk.W, pady=(5, 10))
        
    def create_buttons(self, parent):
        """ボタンを作成"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 左側：テストボタン
        ttk.Button(button_frame, text="接続テスト", command=self.test_connection).pack(side=tk.LEFT)
        
        # 右側：OK/キャンセルボタン
        ttk.Button(button_frame, text="キャンセル", command=self.cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="OK", command=self.save_settings).pack(side=tk.RIGHT)
        
    def test_connection(self):
        """API接続テスト"""
        openai_key = self.openai_key_var.get().strip()
        google_key = self.google_key_var.get().strip()
        
        test_results = []
        
        # OpenAI APIテスト
        if openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                
                # 簡単なテストリクエスト
                response = client.models.list()
                test_results.append("✓ OpenAI API: 接続成功")
                
            except Exception as e:
                test_results.append(f"✗ OpenAI API: 接続失敗\n  {str(e)}")
        else:
            test_results.append("- OpenAI API: キーが設定されていません")
        
        # Google Translate APIテスト
        if google_key:
            try:
                from google.cloud import translate_v2 as translate
                translate_client = translate.Client()
                
                # 簡単なテスト翻訳
                result = translate_client.translate("Hello", target_language='ja')
                test_results.append("✓ Google Translate API: 接続成功")
                
            except Exception as e:
                test_results.append(f"✗ Google Translate API: 接続失敗\n  {str(e)}")
        else:
            test_results.append("- Google Translate API: キーが設定されていません（無料版を使用）")
        
        # 結果表示
        result_text = "API接続テスト結果:\n" + "\n".join(test_results)
        messagebox.showinfo("接続テスト結果", result_text)
            
    def save_settings(self):
        """設定を保存"""
        try:
            # 環境変数として保存
            openai_key = self.openai_key_var.get().strip()
            google_key = self.google_key_var.get().strip()
            
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
                
            if google_key:
                os.environ['GOOGLE_TRANSLATE_API_KEY'] = google_key
            
            # .envファイルに保存（オプション）
            env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            
            try:
                # 既存の.envファイルを読み込み
                env_lines = []
                if os.path.exists(env_file):
                    with open(env_file, 'r', encoding='utf-8') as f:
                        env_lines = f.readlines()
                
                # APIキーの行を更新または追加
                openai_found = False
                google_found = False
                
                for i, line in enumerate(env_lines):
                    if line.startswith('OPENAI_API_KEY='):
                        if openai_key:
                            env_lines[i] = f'OPENAI_API_KEY={openai_key}\n'
                        openai_found = True
                    elif line.startswith('GOOGLE_TRANSLATE_API_KEY='):
                        if google_key:
                            env_lines[i] = f'GOOGLE_TRANSLATE_API_KEY={google_key}\n'
                        google_found = True
                
                # 新しいキーを追加
                if not openai_found and openai_key:
                    env_lines.append(f'OPENAI_API_KEY={openai_key}\n')
                if not google_found and google_key:
                    env_lines.append(f'GOOGLE_TRANSLATE_API_KEY={google_key}\n')
                
                # ファイルに書き込み
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.writelines(env_lines)
                    
            except Exception as e:
                print(f".env ファイル保存エラー: {e}")
            
            # 設定を更新
            try:
                settings_dict = {
                    'whisper_model': self.whisper_model_var.get(),
                    'use_whisper_api': self.use_whisper_api_var.get(),
                    'translation_engine': self.translation_engine_var.get(),
                    'segment_duration': self.segment_duration_var.get(),
                    'sample_rate': self.sample_rate_var.get(),
                    'chunk_size': self.chunk_size_var.get()
                }
                config.update_from_dict(settings_dict)
                    
            except Exception as e:
                print(f"設定更新エラー: {e}")
            
            # 保存された内容を表示
            saved_items = []
            if openai_key:
                saved_items.append("・OpenAI APIキー")
            if google_key:
                saved_items.append("・Google Translate APIキー")
            saved_items.extend([
                f"・Whisperモデル: {self.whisper_model_var.get()}",
                f"・翻訳エンジン: {self.translation_engine_var.get()}",
                f"・音声セグメント長: {self.segment_duration_var.get()}秒"
            ])
            
            message = "以下の設定を保存しました:\n\n" + "\n".join(saved_items)
            messagebox.showinfo("設定保存完了", message)
            
            # コールバック呼び出し
            if self.callback:
                self.callback()
                
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました:\n{str(e)}")
            
    def toggle_openai_visibility(self):
        """OpenAI APIキーの表示/非表示を切り替え"""
        if self.openai_show_var.get():
            self.openai_entry.config(show="")
        else:
            self.openai_entry.config(show="*")
            
    def toggle_google_visibility(self):
        """Google APIキーの表示/非表示を切り替え"""
        if self.google_show_var.get():
            self.google_entry.config(show="")
        else:
            self.google_entry.config(show="*")
            
    def open_url(self, url):
        """URLをブラウザで開く"""
        import webbrowser
        webbrowser.open(url)
    
    def cancel(self):
        """キャンセル"""
        self.dialog.destroy()


class LiveTranslatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Live Translator - リアルタイム文字起こし")
        self.root.geometry("1000x700")
        
        # データ管理
        self.translator: Optional[LiveTranslator] = None
        self.translation_queue = queue.Queue()
        self.is_running = False
        self.transcriptions = []
        
        # GUI要素の初期化
        self.setup_ui()
        
        # キューのチェックを開始
        self.check_queue()
        
    def setup_ui(self):
        """UIコンポーネントをセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 上部: URL入力とコントロール
        self.setup_control_panel(main_frame)
        
        # 中央: タブ形式の結果表示
        self.setup_result_tabs(main_frame)
        
        # 下部: ステータスバー
        self.setup_status_bar(main_frame)
        
    def setup_control_panel(self, parent):
        """コントロールパネルをセットアップ"""
        control_frame = ttk.LabelFrame(parent, text="設定", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # URL入力
        url_frame = ttk.Frame(control_frame)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(url_frame, text="YouTube URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        self.url_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        # ボタン群
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(button_frame, text="開始", command=self.start_translation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_translation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(button_frame, text="クリア", command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_button = ttk.Button(button_frame, text="保存", command=self.save_results)
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 設定ボタン
        self.config_button = ttk.Button(button_frame, text="設定", command=self.show_config)
        self.config_button.pack(side=tk.RIGHT)
        
    def setup_result_tabs(self, parent):
        """結果表示タブをセットアップ"""
        # タブコントロール
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # リアルタイム表示タブ
        self.setup_realtime_tab()
        
        # 履歴タブ
        self.setup_history_tab()
        
        # 統計タブ
        self.setup_stats_tab()
        
    def setup_realtime_tab(self):
        """リアルタイム表示タブをセットアップ"""
        realtime_frame = ttk.Frame(self.notebook)
        self.notebook.add(realtime_frame, text="リアルタイム")
        
        # 分割パネル
        paned = ttk.PanedWindow(realtime_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 英語音声認識結果
        english_frame = ttk.LabelFrame(paned, text="英語音声認識", padding=5)
        paned.add(english_frame, weight=1)
        
        self.english_text = scrolledtext.ScrolledText(
            english_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 11),
            bg="#f8f9fa"
        )
        self.english_text.pack(fill=tk.BOTH, expand=True)
        
        # 日本語翻訳結果
        japanese_frame = ttk.LabelFrame(paned, text="日本語翻訳", padding=5)
        paned.add(japanese_frame, weight=1)
        
        self.japanese_text = scrolledtext.ScrolledText(
            japanese_frame, 
            wrap=tk.WORD, 
            font=("Yu Gothic UI", 12),
            bg="#f0f8ff"
        )
        self.japanese_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_history_tab(self):
        """履歴タブをセットアップ"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="履歴")
        
        # ツリービュー
        columns = ("時刻", "英語", "日本語")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=15)
        
        # 列の設定
        self.history_tree.heading("時刻", text="時刻")
        self.history_tree.heading("英語", text="英語")
        self.history_tree.heading("日本語", text="日本語")
        
        self.history_tree.column("時刻", width=150, minwidth=100)
        self.history_tree.column("英語", width=400, minwidth=200)
        self.history_tree.column("日本語", width=400, minwidth=200)
        
        # スクロールバー
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        # パック
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
    def setup_stats_tab(self):
        """統計タブをセットアップ"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="統計")
        
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame, 
            wrap=tk.WORD, 
            font=("Yu Gothic UI", 10),
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_status_bar(self, parent):
        """ステータスバーをセットアップ"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="準備完了")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT)
        
        # プログレスバー
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))
        
    def start_translation(self):
        """翻訳開始"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("エラー", "YouTube URLを入力してください")
            return
            
        if self.is_running:
            return
            
        try:
            # UI状態更新
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.is_running = True
            self.progress.start()
            self.status_var.set("処理中...")
            
            # LiveTranslatorを初期化
            self.translator = LiveTranslator()
            
            # コールバック設定
            def on_transcription(text, translation):
                self.translation_queue.put(("transcription", text, translation))
                
            def on_error(error):
                self.translation_queue.put(("error", str(error)))
                
            def on_status(status):
                self.translation_queue.put(("status", status))
                
            # 翻訳開始（別スレッド）
            self.translation_thread = threading.Thread(
                target=self.run_translation,
                args=(url, on_transcription, on_error, on_status),
                daemon=True
            )
            self.translation_thread.start()
            
        except Exception as e:
            self.handle_error(f"開始エラー: {str(e)}")
            
    def run_translation(self, url, on_transcription, on_error, on_status):
        """翻訳実行（別スレッド）"""
        try:
            self.translator.process_live_stream(
                url,
                transcription_callback=on_transcription,
                error_callback=on_error,
                status_callback=on_status
            )
        except Exception as e:
            on_error(str(e))
            
    def stop_translation(self):
        """翻訳停止"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        if self.translator:
            self.translator.stop()
            
        # UI状態更新
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_var.set("停止しました")
        
    def clear_results(self):
        """結果をクリア"""
        self.english_text.delete(1.0, tk.END)
        self.japanese_text.delete(1.0, tk.END)
        
        # 履歴クリア
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        self.transcriptions.clear()
        self.update_stats()
        
    def save_results(self):
        """結果を保存"""
        if not self.transcriptions:
            messagebox.showinfo("情報", "保存する結果がありません")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.transcriptions, f, ensure_ascii=False, indent=2)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        for item in self.transcriptions:
                            f.write(f"[{item['timestamp']}]\n")
                            f.write(f"EN: {item['english']}\n")
                            f.write(f"JA: {item['japanese']}\n\n")
                            
                messagebox.showinfo("成功", f"結果を保存しました: {filename}")
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {str(e)}")
                
    def show_config(self):
        """設定ダイアログを表示"""
        config_window = ConfigDialog(self.root, self.on_config_updated)
        
    def on_config_updated(self):
        """設定が更新されたときの処理"""
        # 設定が更新された場合の処理（必要に応じて翻訳器を再初期化など）
        pass
        
    def check_queue(self):
        """キューをチェックして結果を更新"""
        try:
            while True:
                try:
                    item = self.translation_queue.get_nowait()
                    self.handle_queue_item(item)
                except queue.Empty:
                    break
        except Exception as e:
            print(f"Queue check error: {e}")
            
        # 次のチェックをスケジュール
        self.root.after(100, self.check_queue)
        
    def handle_queue_item(self, item):
        """キューアイテムを処理"""
        try:
            if item[0] == "transcription":
                self.add_transcription(item[1], item[2])
            elif item[0] == "error":
                self.handle_error(item[1])
            elif item[0] == "status":
                self.status_var.set(item[1])
        except Exception as e:
            print(f"Queue item handling error: {e}")
            
    def add_transcription(self, english_text, japanese_text):
        """文字起こし結果を追加"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # リアルタイム表示更新
        self.english_text.insert(tk.END, f"[{timestamp}] {english_text}\n")
        self.japanese_text.insert(tk.END, f"[{timestamp}] {japanese_text}\n")
        
        # 自動スクロール
        self.english_text.see(tk.END)
        self.japanese_text.see(tk.END)
        
        # 履歴に追加
        self.history_tree.insert("", tk.END, values=(timestamp, english_text, japanese_text))
        
        # データ保存
        self.transcriptions.append({
            "timestamp": timestamp,
            "english": english_text,
            "japanese": japanese_text
        })
        
        # 統計更新
        self.update_stats()
        
    def update_stats(self):
        """統計情報を更新"""
        stats = f"""処理統計:
==========================================

総文字起こし数: {len(self.transcriptions)}
英語文字数合計: {sum(len(item['english']) for item in self.transcriptions)}
日本語文字数合計: {sum(len(item['japanese']) for item in self.transcriptions)}

処理開始時刻: {self.transcriptions[0]['timestamp'] if self.transcriptions else 'N/A'}
最新処理時刻: {self.transcriptions[-1]['timestamp'] if self.transcriptions else 'N/A'}

設定情報:
------------------------------------------
音声モデル: {config.whisper.model_name}
翻訳エンジン: {config.translation.engine}
ソース言語: {config.translation.source_language}
ターゲット言語: {config.translation.target_language}
"""
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        self.stats_text.config(state=tk.DISABLED)
        
    def handle_error(self, error_message):
        """エラーハンドリング"""
        self.status_var.set(f"エラー: {error_message}")
        self.stop_translation()
        messagebox.showerror("エラー", error_message)
        
    def on_closing(self):
        """アプリケーション終了時の処理"""
        if self.is_running:
            self.stop_translation()
        self.root.destroy()


def run_gui():
    """GUIアプリケーションを実行"""
    root = tk.Tk()
    app = LiveTranslatorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    run_gui()