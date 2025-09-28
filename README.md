# YouTube Live Translator

YouTubeの英語ライブ配信をリアルタイムで日本語に翻訳・文字起こしするツールです。

## 機能

- YouTubeライブ配信から音声をリアルタイム取得
- OpenAI Whisperによる英語音声認識
- 日本語への自動翻訳（OpenAI GPT / Google Translate対応）
- リアルタイム文字起こし表示
- Webベースの直感的なUI

## 📥 インストール方法

### ダウンロード (推奨)
**最新リリース**: [GitHub Releases](https://github.com/livetranslator/youtube-live-translator/releases)

#### Windows
- `LiveTranslator-*-setup.exe`: インストーラー版 (推奨)
- `LiveTranslator-*-windows-portable.zip`: ポータブル版

#### macOS
- `LiveTranslator-*-macos.zip`: アプリケーション版

#### Linux
- `LiveTranslator-*-linux-portable.tar.gz`: ポータブル版

#### Docker
```bash
docker pull livetranslator/youtube-live-translator:latest
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key livetranslator/youtube-live-translator
```

### 開発者向けセットアップ

#### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

#### 2. 環境設定

`config/.env`ファイルを作成し、以下のAPIキーを設定：

```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_TRANSLATE_API_KEY=your_google_translate_key_here  # オプション
```

#### 3. 実行

```bash
# Webアプリ起動
python main.py web

# または従来の方法
streamlit run src/app.py
```

## 🔨 配布版の作成

開発者が配布用バイナリを作成する場合：

```bash
# Windows
cd build_tools
build.bat

# Linux/macOS  
cd build_tools
bash build.sh

# Docker
docker build -t livetranslator .
```

詳細は [DISTRIBUTION.md](DISTRIBUTION.md) をご覧ください。

## 使用方法

1. WebブラウザでUIを開く
2. YouTubeライブ配信のURLを入力
3. 「開始」ボタンをクリック
4. リアルタイムで日本語字幕が表示されます

## 技術スタック

- **音声取得**: yt-dlp
- **音声認識**: OpenAI Whisper
- **翻訳**: OpenAI GPT-3.5/4 または Google Translate
- **UI**: Streamlit
- **音声処理**: PyAudio, pydub

## 💰 料金について

### 完全無料で使用可能
- **音声認識**: Whisperローカルモデル使用
- **翻訳**: Google Translate無料版使用
- **追加料金**: なし

### 有料API使用時の料金目安
- **OpenAI Whisper API**: 音声1分あたり約$0.006（約0.9円）
- **OpenAI GPT翻訳**: 翻訳1回あたり約$0.001-0.003（約0.15-0.45円）
- **1時間のライブ配信**: 約$0.4-0.7（約60-105円）

詳細は[SETUP.md](SETUP.md)の「API使用量の目安」をご確認ください。

## 注意事項

- ライブ配信の音声品質によって認識精度が変わります
- API使用量に応じて料金が発生する場合があります（上記参照）
- 一部のライブ配信では音声取得が制限される場合があります

## ライセンス

MIT License