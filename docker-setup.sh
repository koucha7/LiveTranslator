#!/bin/bash
# Docker配布用セットアップスクリプト

echo "🐳 YouTube Live Translator Docker セットアップ"
echo "============================================="

# Docker確認
if ! command -v docker &> /dev/null; then
    echo "❌ Docker が見つかりません"
    echo "   https://docs.docker.com/get-docker/ からインストールしてください"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose が見つかりません"
    echo "   https://docs.docker.com/compose/install/ からインストールしてください"
    exit 1
fi

# 設定ファイル確認
if [ ! -f "config/.env" ]; then
    echo "⚙️ 設定ファイルを作成中..."
    cp config/.env.example config/.env
    echo "✅ config/.env を作成しました"
    echo "⚠️  APIキーを設定してください"
    echo ""
    echo "編集するファイル: config/.env"
    echo "必要な設定: OPENAI_API_KEY"
    echo ""
    read -p "設定ファイルを編集しましたか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "設定ファイルを編集してから再度実行してください"
        exit 1
    fi
fi

# Docker イメージをビルド
echo "🔨 Docker イメージをビルド中..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Docker イメージのビルドに失敗しました"
    exit 1
fi

echo "✅ Docker イメージのビルド完了"

# コンテナ起動
echo "🚀 コンテナを起動中..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ コンテナの起動に失敗しました"
    exit 1
fi

echo "✅ コンテナが起動しました"

# 起動確認
echo "⏳ サービスの起動を待機中..."
sleep 10

if docker-compose ps | grep -q "Up"; then
    echo "🎉 セットアップ完了！"
    echo ""
    echo "📋 アクセス情報:"
    echo "   Web UI: http://localhost:8501"
    echo ""
    echo "📋 管理コマンド:"
    echo "   ログ確認: docker-compose logs -f"
    echo "   停止: docker-compose down"
    echo "   再起動: docker-compose restart"
    echo ""
    echo "🌐 ブラウザでアクセスしてください: http://localhost:8501"
else
    echo "⚠️ サービスが正常に起動していない可能性があります"
    echo "ログを確認してください: docker-compose logs"
    exit 1
fi