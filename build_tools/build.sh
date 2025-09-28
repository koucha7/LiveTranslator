#!/bin/bash
# Linux/macOS用ビルドスクリプト
# YouTube Live Translator のインストーラー作成

echo "🚀 YouTube Live Translator ビルド開始"
echo "====================================="

# Python確認
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 が見つかりません"
    exit 1
fi

# 権限確認
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  root権限での実行は推奨されません"
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ビルド実行
python3 build_tools/build.py

if [ $? -ne 0 ]; then
    echo "❌ ビルドに失敗しました"
    exit 1
fi

echo ""
echo "🎉 ビルド完了！"
echo "📁 配布ファイル: dist/"
echo ""

if [ -d "dist" ]; then
    echo "📦 作成されたファイル:"
    ls -lh dist/
fi

echo ""
echo "📋 次のステップ:"
echo "1. dist/ フォルダのファイルをテスト"
echo "2. アーカイブファイルを配布"
echo "3. GitHub Releases でリリース"