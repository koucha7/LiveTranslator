# YouTube Live Translator - Docker Version
# マルチステージビルドでサイズを最適化

# ベースイメージ
FROM python:3.11-slim as base

# 作業ディレクトリ
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ビルドステージ
FROM base as builder

# Python依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 実行ステージ
FROM base as runtime

# 非rootユーザーを作成
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Python依存関係をコピー
COPY --from=builder /root/.local /home/app/.local
ENV PATH=/home/app/.local/bin:$PATH

# アプリケーションファイルをコピー
COPY --chown=app:app . .

# 設定ディレクトリの権限設定
RUN mkdir -p config temp logs && \
    chmod 755 config temp logs

# 環境変数
ENV PYTHONPATH=/home/app
ENV PYTHONUNBUFFERED=1

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python main.py config --validate || exit 1

# ポート公開
EXPOSE 8501

# エントリーポイント
ENTRYPOINT ["python", "main.py"]
CMD ["web", "--port", "8501"]