@echo off
REM Windows用ビルドスクリプト
REM YouTube Live Translator のインストーラー作成

echo 🚀 YouTube Live Translator ビルド開始
echo =====================================

REM 管理者権限チェック
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  管理者権限が必要です。管理者として実行してください。
    pause
    exit /b 1
)

REM Python確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python が見つかりません
    pause
    exit /b 1
)

REM ビルド実行
python build_tools\build.py

if %errorlevel% neq 0 (
    echo ❌ ビルドに失敗しました
    pause
    exit /b 1
)

echo.
echo 🎉 ビルド完了！
echo 📁 配布ファイル: dist\
echo.
echo 📦 作成されたファイル:
dir /b dist\

echo.
echo 📋 次のステップ:
echo 1. dist\ フォルダの LiveTranslator-*-setup.exe をテスト
echo 2. dist\ フォルダの LiveTranslator-*-portable.zip を配布
echo 3. GitHub Releases でリリース

pause