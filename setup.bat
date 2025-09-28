@echo off
REM セットアップスクリプト (setup.bat)
REM YouTube Live Translator の初期セットアップを自動化 (Windows用)

echo 🎥 YouTube Live Translator セットアップ開始
echo ===============================================

REM Python バージョン確認
echo 📋 Python バージョン確認中...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python が見つかりません。Python 3.8+ をインストールしてください。
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python が見つかりました: %python_version%

REM pip 更新
echo 📦 pip を更新中...
python -m pip install --upgrade pip

REM 依存関係インストール
echo 📦 依存関係をインストール中...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ 依存関係のインストールに失敗しました
    pause
    exit /b 1
)
echo ✅ 依存関係のインストール完了

REM ffmpeg 確認
echo 🎵 ffmpeg の確認中...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  ffmpeg が見つかりません
    echo    以下のコマンドでインストールしてください：
    echo    Windows: choco install ffmpeg
    echo    または https://ffmpeg.org/download.html からダウンロード
) else (
    echo ✅ ffmpeg が見つかりました
)

REM 設定ファイル作成
echo ⚙️  設定ファイルを作成中...
if not exist "config\.env" (
    copy "config\.env.example" "config\.env"
    echo ✅ .env ファイルを作成しました
    echo ⚠️  config\.env ファイルを編集してAPIキーを設定してください
) else (
    echo ✅ .env ファイルは既に存在します
)

REM ディレクトリ作成
echo 📁 必要なディレクトリを作成中...
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
echo ✅ ディレクトリ作成完了

REM 設定確認
echo 🔍 設定を確認中...
python main.py config --validate

echo.
echo 🎉 セットアップ完了！
echo ===============================================
echo.
echo 📝 次のステップ：
echo 1. config\.env ファイルを編集してAPIキーを設定
echo    OPENAI_API_KEY=your_api_key_here
echo.
echo 2. Webアプリを起動：
echo    python main.py web
echo.
echo 3. または、CLIで実行：
echo    python main.py cli "https://www.youtube.com/watch?v=LIVE_STREAM_ID"
echo.
echo 📚 詳細な使用方法は SETUP.md をご覧ください

pause