#!/usr/bin/env python3
"""
YouTube Live Translator
コマンドライン実行スクリプト
"""

import sys
import os
import argparse
import logging

# パスの設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.live_translator import LiveTranslator, ProcessingState, TranscriptionResult
from src.translator import TranslationEngine
from src.config import config

def setup_logging(debug: bool = False):
    """ログの設定"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('translator.log')
        ]
    )

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="YouTube Live Translator - YouTubeライブ配信の日本語文字起こしツール\n引数なしで実行するとGUIモードで起動します。",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # サブコマンド
    subparsers = parser.add_subparsers(dest='command', help='実行モード')
    
    # GUIモード
    gui_parser = subparsers.add_parser('gui', help='GUIアプリケーションを起動')
    gui_parser.add_argument('--debug', action='store_true', help='デバッグモード')
    
    # Webアプリモード
    web_parser = subparsers.add_parser('web', help='Webインターフェースを起動')
    web_parser.add_argument('--port', type=int, default=8501, help='ポート番号')
    web_parser.add_argument('--debug', action='store_true', help='デバッグモード')
    
    # CLIモード
    cli_parser = subparsers.add_parser('cli', help='コマンドライン実行')
    cli_parser.add_argument('url', help='YouTubeライブ配信のURL')
    cli_parser.add_argument('--model', default='base', 
                           choices=['tiny', 'base', 'small', 'medium', 'large'],
                           help='Whisperモデル')
    cli_parser.add_argument('--api', action='store_true', help='OpenAI Whisper APIを使用（デフォルト：ローカルWhisper）')
    cli_parser.add_argument('--engine', choices=['openai', 'google'], default='google',
                           help='翻訳エンジン (デフォルト: google無料版)')
    cli_parser.add_argument('--source', default='en', help='元言語')
    cli_parser.add_argument('--target', default='ja', help='翻訳先言語')
    cli_parser.add_argument('--duration', type=int, default=10, help='音声セグメント長（秒）')
    cli_parser.add_argument('--debug', action='store_true', help='デバッグモード')
    
    # 設定確認モード
    config_parser = subparsers.add_parser('config', help='設定を確認')
    config_parser.add_argument('--validate', action='store_true', help='設定を検証')
    
    args = parser.parse_args()
    
    # コマンドが指定されていない場合はデフォルトでGUIモードを起動
    if not args.command:
        # GUIモード用のデフォルト引数を作成
        args.command = 'gui'
        args.debug = False
    
    # ログ設定
    setup_logging(getattr(args, 'debug', False))
    
    if args.command == 'gui':
        run_gui_app(args)
    elif args.command == 'web':
        run_web_app(args)
    elif args.command == 'cli':
        run_cli_mode(args)
    elif args.command == 'config':
        show_config(args)

def run_gui_app(args):
    """GUIアプリを実行"""
    try:
        from src.gui_app import run_gui
        
        # ログ設定
        setup_logging(args.debug)
        
        # GUIアプリケーション起動
        run_gui()
        
    except ImportError as e:
        import tkinter.messagebox as msgbox
        msgbox.showerror("エラー", f"GUI関連のモジュールがインストールされていません:\n{e}\n\ntkinterがインストールされていることを確認してください")
    except Exception as e:
        import tkinter.messagebox as msgbox
        msgbox.showerror("エラー", f"GUIアプリ実行エラー:\n{e}")

def run_web_app(args):
    """Webアプリを実行"""
    try:
        import streamlit as st
        from streamlit import config as st_config
        
        # Streamlit設定
        st_config.set_option('server.port', args.port)
        st_config.set_option('server.headless', True)
        st_config.set_option('server.enableXsrfProtection', False)
        
        # アプリ実行
        os.system(f"streamlit run src/app.py --server.port {args.port}")
        
    except ImportError:
        print("エラー: Streamlitがインストールされていません")
        print("pip install streamlit でインストールしてください")
    except Exception as e:
        print(f"Webアプリ実行エラー: {e}")

def run_cli_mode(args):
    """CLIモードで実行"""
    try:
        # 設定確認
        config.validate()
        
        # 翻訳エンジン設定（デフォルトは無料のGoogle）
        engine = TranslationEngine.OPENAI if args.engine == 'openai' else TranslationEngine.GOOGLE
        
        # 翻訳器作成
        translator = LiveTranslator(
            whisper_model=args.model,
            use_whisper_api=args.api,
            translation_engine=engine,
            segment_duration=args.duration
        )
        
        # 言語設定
        translator.configure(
            source_language=args.source,
            target_language=args.target,
            segment_duration=args.duration
        )
        
        # コールバック設定
        def transcription_callback(result: TranscriptionResult):
            print(f"\n[{result.timestamp}]")
            print(f"原文: {result.original_text}")
            print(f"翻訳: {result.translated_text}")
            print(f"信頼度: {result.confidence:.2f}")
            print("-" * 50)
        
        def error_callback(error: str):
            print(f"エラー: {error}", file=sys.stderr)
        
        def state_callback(state: ProcessingState):
            print(f"状態: {state.value}")
        
        translator.set_transcription_callback(transcription_callback)
        translator.set_error_callback(error_callback)
        translator.set_state_callback(state_callback)
        
        print(f"YouTube Live Translator 開始")
        print(f"URL: {args.url}")
        print(f"モデル: {args.model}")
        print(f"翻訳エンジン: {args.engine}")
        print(f"言語: {args.source} -> {args.target}")
        print("Ctrl+C で停止")
        print("=" * 50)
        
        # 翻訳開始
        if translator.start_translation(args.url):
            try:
                # 無限ループで実行
                import time
                while True:
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n翻訳を停止しています...")
                translator.stop_translation()
                
                # 統計表示
                stats = translator.get_stats()
                print(f"\n統計情報:")
                print(f"処理セグメント数: {stats['segments_processed']}")
                print(f"平均処理時間: {stats.get('avg_processing_time', 0):.2f}秒")
                print(f"キャッシュヒット率: {stats.get('cache_hit_rate', 0):.2%}")
                print(f"エラー数: {stats['errors']}")
                
                print("終了しました")
        else:
            print("翻訳の開始に失敗しました", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"実行エラー: {e}", file=sys.stderr)
        sys.exit(1)

def show_config(args):
    """設定を表示"""
    try:
        # 設定情報を構築
        config_text = "現在の設定:\n" + "=" * 40 + "\n"
        
        config_dict = config.to_dict()
        
        for section, values in config_dict.items():
            config_text += f"\n[{section.upper()}]\n"
            for key, value in values.items():
                config_text += f"  {key}: {value}\n"
        
        config_text += f"\nAPIキー:\n"
        api_keys = config.get_api_keys()
        for key, value in api_keys.items():
            status = "設定済み" if value else "未設定"
            config_text += f"  {key}: {status}\n"
        
        if args.validate:
            config_text += f"\n設定検証:\n"
            try:
                config.validate()
                config_text += "  ✓ 設定は有効です\n"
            except Exception as e:
                config_text += f"  ✗ 設定エラー: {e}\n"
        
        # コンソールが利用可能な場合は通常の出力
        try:
            print(config_text)
        except:
            # GUIモードで実行されている場合はメッセージボックスで表示
            try:
                import tkinter as tk
                import tkinter.messagebox as msgbox
                import tkinter.scrolledtext as scrolledtext
                
                root = tk.Tk()
                root.title("LiveTranslator - 設定情報")
                root.geometry("600x500")
                
                text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Yu Gothic UI", 10))
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(tk.END, config_text)
                text_widget.config(state=tk.DISABLED)
                
                root.mainloop()
            except:
                # 最後の手段：簡単なメッセージボックス
                import tkinter.messagebox as msgbox
                msgbox.showinfo("設定情報", config_text[:500] + "..." if len(config_text) > 500 else config_text)
                
    except Exception as e:
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror("エラー", f"設定表示エラー: {e}")
        except:
            print(f"設定表示エラー: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()