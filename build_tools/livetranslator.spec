"""
Build Configuration for PyInstaller
YouTube Live Translator用のビルド設定
"""

# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリ
ROOT_DIR = Path(os.getcwd())

# アプリケーション情報
APP_NAME = "YouTube Live Translator"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "YouTubeライブ配信をリアルタイムで日本語に翻訳"
APP_AUTHOR = "LiveTranslator Team"

# メインスクリプト
MAIN_SCRIPT = str(ROOT_DIR / "main.py")

# 追加するデータファイル
datas = [
    (str(ROOT_DIR / "src"), "src"),
    (str(ROOT_DIR / "config" / ".env.example"), "config"),
    (str(ROOT_DIR / "README.md"), "."),
    (str(ROOT_DIR / "SETUP.md"), "."),
    (str(ROOT_DIR / "LICENSE"), "."),
]

# 隠れたインポート（PyInstallerが自動検出できないモジュール）
hiddenimports = [
    'whisper',
    'openai',
    'streamlit',
    'streamlit.web.cli',
    'yt_dlp',
    'deep_translator',
    # 'pydub',
    # 'pyaudio',
    'numpy',
    'pandas',
    'plotly',
    'plotly.express',
    'plotly.graph_objects',
    'PIL',
    'PIL.Image',
    'dotenv',
    'threading',
    'src.youtube_extractor',
    'src.speech_recognition',
    'src.translator',
    'src.live_translator',
    'src.app',
    'src.gui_app',
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'audioop',
    'pyaudioop',
    'wave',
    'queue',
    'logging',
    'tempfile',
    'subprocess',
    'io',
    'wave',
    'asyncio',
    'aiohttp',
    'websockets',
]

# 除外するモジュール
excludes = [
    'matplotlib',
    'scipy',
    'jupyter',
    'notebook',
    'IPython',
    'pytest',
    'sphinx',
    'pydub',
    'pyaudio',
]

# 実行時フック
runtime_hooks = []

# アイコンファイル（存在する場合）
icon_path = ROOT_DIR / "assets" / "icon.ico"
icon = str(icon_path) if icon_path.exists() else None

# PyInstaller設定
a = Analysis(
    [MAIN_SCRIPT],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=runtime_hooks,
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 重複ファイルの除去
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 実行ファイルの設定
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LiveTranslator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUIアプリとして実行（コンソール非表示）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
    version_file=None,
)

# ディレクトリモードでの配布
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LiveTranslator",
)

# macOS用の設定（macOSでビルドする場合）
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=icon,
        bundle_identifier="com.livetranslator.app",
        version=APP_VERSION,
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleShortVersionString': APP_VERSION,
            'CFBundleVersion': APP_VERSION,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleName': APP_NAME,
            'CFBundleDocumentTypes': []
        },
    )