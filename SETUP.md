# YouTube Live Translator のセットアップと使用方法

## 🚀 クイックスタート

### 1. 依存関係のインストール

```bash
# Python 3.8+ が必要です
pip install -r requirements.txt
```

### 2. 環境設定

`config/.env`ファイルを作成（`.env.example`をコピー）：

```bash
cp config/.env.example config/.env
```

`.env`ファイルを編集してAPIキーを設定：

```env
OPENAI_API_KEY=your_openai_api_key_here
# Google Translate APIキー（オプション）
GOOGLE_TRANSLATE_API_KEY=your_google_translate_key_here
```

### 3. ffmpegのインストール（重要）

音声処理にffmpegが必要です：

**Windows:**
```bash
# Chocolatey使用
choco install ffmpeg

# または https://ffmpeg.org/download.html からダウンロード
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. 実行

#### Webインターフェース（推奨）
```bash
python main.py web
```

ブラウザで `http://localhost:8501` を開く

#### コマンドライン
```bash
python main.py cli "https://www.youtube.com/watch?v=LIVE_STREAM_ID"
```

## 📱 Webインターフェース使用方法

1. **設定**：サイドバーでWhisperモデルと翻訳エンジンを選択
2. **URL入力**：YouTubeライブ配信のURLを入力
3. **開始**：「▶️ 開始」ボタンをクリック
4. **確認**：リアルタイムで文字起こしと翻訳が表示されます

### 推奨設定

| 用途 | Whisperモデル | 翻訳エンジン | 特徴 |
|------|---------------|--------------|------|
| 高精度 | medium/large | OpenAI | 精度最高、処理時間長 |
| バランス | small | OpenAI | 精度と速度のバランス |
| 高速 | base/tiny | Google | 高速、やや低精度 |

## 🛠️ コマンドライン使用方法

### 基本使用法
```bash
python main.py cli "YOUTUBE_LIVE_URL"
```

### オプション
```bash
python main.py cli "YOUTUBE_LIVE_URL" \
  --model small \
  --engine openai \
  --source en \
  --target ja \
  --duration 10
```

### 利用可能なオプション

- `--model`: Whisperモデル (tiny, base, small, medium, large)
- `--api`: OpenAI Whisper APIを使用
- `--engine`: 翻訳エンジン (openai, google)
- `--source`: 元言語 (en, ja, ko, zh, etc.)
- `--target`: 翻訳先言語 (ja, en, ko, zh, etc.)
- `--duration`: 音声セグメント長（秒）
- `--debug`: デバッグモード

### 設定確認
```bash
python main.py config --validate
```

## 🔧 詳細設定

### 環境変数一覧

| 変数名 | デフォルト | 説明 |
|--------|------------|------|
| `OPENAI_API_KEY` | - | OpenAI APIキー（必須） |
| `GOOGLE_TRANSLATE_API_KEY` | - | Google Translate APIキー（オプション） |
| `WHISPER_MODEL` | base | デフォルトWhisperモデル |
| `USE_WHISPER_API` | false | Whisper API使用フラグ |
| `TRANSLATION_ENGINE` | openai | 翻訳エンジン |
| `GPT_MODEL` | gpt-3.5-turbo | GPTモデル |
| `MAX_TOKENS` | 150 | 翻訳最大トークン数 |
| `AUDIO_CHUNK_SIZE` | 1024 | 音声チャンクサイズ |
| `AUDIO_SAMPLE_RATE` | 16000 | サンプリングレート |
| `STREAMLIT_PORT` | 8501 | Webアプリポート |

### パフォーマンス調整

#### 高速化設定
```env
WHISPER_MODEL=tiny
USE_WHISPER_API=true
TRANSLATION_ENGINE=google
AUDIO_SEGMENT_DURATION=5
```

#### 高精度設定
```env
WHISPER_MODEL=medium
USE_WHISPER_API=false
TRANSLATION_ENGINE=openai
GPT_MODEL=gpt-4
MAX_TOKENS=200
```

## ⚠️ 注意事項とトラブルシューティング

### 制限事項
- **ライブ配信のみ対応**：録画動画は非対応
- **音声品質依存**：配信の音声品質により認識精度が変わります
- **API料金**：OpenAI API使用時は利用量に応じて料金が発生

### よくある問題

#### 音声が認識されない
- ライブ配信が実際に進行中か確認
- ffmpegが正しくインストールされているか確認
- 音声セグメント長を調整（5-15秒）
- 配信の音量を確認

#### 翻訳が表示されない
- APIキーが正しく設定されているか確認
- インターネット接続を確認
- ログでエラーメッセージを確認

#### 処理が遅い
```bash
# 軽量設定で試す
python main.py cli "URL" --model tiny --engine google --duration 15
```

#### メモリ不足
- Whisperモデルを小さいものに変更
- 音声セグメント長を短くする
- 不要なプロセスを終了

### ログ確認
```bash
# ログファイルを確認
cat translator.log

# リアルタイムログ監視
tail -f translator.log
```

## 🔍 API使用量の目安

### OpenAI Whisper API
- 音声1分あたり約$0.006
- 1時間のライブ配信で約$0.36

### OpenAI GPT翻訳
- 翻訳1回あたり約$0.001-0.003
- セグメント数により変動

### 節約のコツ
- ローカルWhisperモデルを使用
- Google Translateを使用
- 音声セグメント長を長めに設定
- キャッシュを活用（自動的に実装済み）

## 📈 パフォーマンス指標

### 処理速度の目安
| モデル | 処理速度 | 精度 | メモリ使用量 |
|--------|----------|------|--------------|
| tiny | 10x リアルタイム | 低 | ~1GB |
| base | 5x リアルタイム | 中 | ~1GB |
| small | 3x リアルタイム | 高 | ~2GB |
| medium | 2x リアルタイム | 高+ | ~5GB |
| large | 1x リアルタイム | 最高 | ~10GB |

### 推奨システム要件
- **最小**: CPU 4コア、RAM 4GB、ストレージ 2GB
- **推奨**: CPU 8コア、RAM 8GB、ストレージ 5GB
- **高性能**: GPU対応、RAM 16GB+

## 🆘 サポート

### ログレベル設定
```bash
# デバッグモードで実行
python main.py cli "URL" --debug
```

### 問題報告時の情報
1. 実行環境（OS, Pythonバージョン）
2. 使用した設定
3. エラーメッセージ
4. ログファイル内容
5. YouTubeのURL（可能であれば）

### よくある質問（FAQ）

**Q: プライベートライブ配信は対応していますか？**
A: 公開されているライブ配信のみ対応しています。

**Q: 複数の配信を同時に翻訳できますか？**
A: 現在は1つの配信のみ対応しています。

**Q: 日本語から英語への翻訳は可能ですか？**
A: はい、設定で言語を変更することで双方向翻訳が可能です。

**Q: スマートフォンで使用できますか？**
A: Webインターフェースはモバイル対応していますが、処理はPCで行う必要があります。