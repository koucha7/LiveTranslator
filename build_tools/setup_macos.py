"""
macOS Application Builder
py2appを使用したmacOSアプリケーション作成設定
"""

from setuptools import setup
import os
import sys

# アプリケーション情報
APP_NAME = "YouTube Live Translator"
APP_VERSION = "1.0.0"
MAIN_SCRIPT = "../main.py"

# py2appオプション
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "YouTubeライブ配信をリアルタイムで日本語に翻訳",
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
        'NSHumanReadableCopyright': "Copyright © 2024 LiveTranslator Team",
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14',
        'CFBundleIconFile': 'icon.icns',  # アイコンファイル
        'NSAppleScriptEnabled': False,
        'LSBackgroundOnly': False,
        'LSUIElement': False,
    },
    'packages': [
        'whisper',
        'openai', 
        'streamlit',
        'yt_dlp',
        'googletrans',
        'pydub',
        'numpy',
        'pandas',
        'plotly',
        'PIL',
        'dotenv',
    ],
    'includes': [
        'streamlit.web.cli',
        'plotly.express',
        'plotly.graph_objects',
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'scipy',
        'jupyter',
        'pytest',
    ],
    'resources': [
        '../config/.env.example',
        '../README.md',
        '../SETUP.md',
        '../LICENSE',
    ],
    'iconfile': '../assets/icon.icns',  # macOS用アイコン
}

# データファイル
DATA_FILES = [
    ('config', ['../config/.env.example']),
    ('docs', ['../README.md', '../SETUP.md', '../LICENSE']),
]

if __name__ == '__main__':
    setup(
        name=APP_NAME,
        version=APP_VERSION,
        app=[MAIN_SCRIPT],
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )