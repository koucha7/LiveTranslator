#!/bin/bash
# セットアップスクリプト (setup.sh)
# YouTube Live Translator の初期セットアップを自動化

echo "🎥 YouTube Live Translator セットアップ開始"
echo "==============================================="

# Python バージョン確認
echo "📋 Python バージョン確認中..."
python_version=$(python --version 2>&1)
if [[ $python_version == *"Python 3."* ]]; then
    echo "✅ Python が見つかりました: $python_version"
else
    echo "❌ Python 3.8+ が必要です。Pythonをインストールしてください。"
    exit 1
fi

# pip 更新
echo "📦 pip を更新中..."
python -m pip install --upgrade pip

# 依存関係インストール
echo "📦 依存関係をインストール中..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依存関係のインストール完了"
else
    echo "❌ 依存関係のインストールに失敗しました"
    exit 1
fi

# ffmpeg 確認
echo "🎵 ffmpeg の確認中..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg が見つかりました"
else
    echo "⚠️  ffmpeg が見つかりません"
    echo "   以下のコマンドでインストールしてください："
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
    echo "   Windows: choco install ffmpeg"
fi

# 設定ファイル作成
echo "⚙️  設定ファイルを作成中..."
if [ ! -f "config/.env" ]; then
    cp config/.env.example config/.env
    echo "✅ .env ファイルを作成しました"
    echo "⚠️  config/.env ファイルを編集してAPIキーを設定してください"
else
    echo "✅ .env ファイルは既に存在します"
fi

# ディレクトリ作成
echo "📁 必要なディレクトリを作成中..."
mkdir -p temp
mkdir -p logs
echo "✅ ディレクトリ作成完了"

# 設定確認
echo "🔍 設定を確認中..."
python main.py config --validate

echo ""
echo "🎉 セットアップ完了！"
echo "==============================================="
echo ""
echo "📝 次のステップ："
echo "1. config/.env ファイルを編集してAPIキーを設定"
echo "   OPENAI_API_KEY=your_api_key_here"
echo ""
echo "2. Webアプリを起動："
echo "   python main.py web"
echo ""
echo "3. または、CLIで実行："
echo "   python main.py cli \"https://www.youtube.com/watch?v=LIVE_STREAM_ID\""
echo ""
echo "📚 詳細な使用方法は SETUP.md をご覧ください"