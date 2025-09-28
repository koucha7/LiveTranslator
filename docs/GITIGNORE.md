# .gitignore Configuration Guide

## 📋 Gitignoreの構成

YouTube Live Translatorプロジェクトでは、複数の`.gitignore`ファイルを使用してファイル管理を行っています。

### 🗂️ ファイル構成

```
LiveTranslator/
├── .gitignore              # メインのgitignore
├── config/.gitignore       # 設定ファイル用
├── temp/.gitignore         # 一時ファイル用
├── build_tools/.gitignore  # ビルドツール用
└── temp/.gitkeep          # 空ディレクトリ保持用
```

### 🔒 無視されるファイル・ディレクトリ

#### 🔑 機密情報
- `.env`, `config/.env` - API キー等の環境変数
- `api_keys.txt`, `credentials.json` - 認証情報
- `secrets.json` - 秘密鍵やトークン

#### 📁 一時・キャッシュファイル
- `temp/` - 音声処理の一時ファイル
- `cache/` - 翻訳キャッシュ
- `logs/` - ログファイル
- `*.log` - 各種ログ

#### 🎵 メディアファイル
- `*.wav`, `*.mp3`, `*.mp4` - 音声・動画ファイル
- `audio_segments/` - 音声セグメント
- `media_cache/` - メディアキャッシュ

#### 🔨 ビルド成果物
- `build/`, `dist/` - ビルド出力
- `*.exe`, `*.msi`, `*.dmg` - インストーラー
- `*.zip`, `*.tar.gz` - アーカイブファイル

#### 🐍 Python関連
- `__pycache__/` - Pythonキャッシュ
- `*.pyc` - コンパイル済みPython
- `venv/`, `.venv/` - 仮想環境

#### 💻 開発環境
- `.vscode/`, `.idea/` - IDE設定
- `.DS_Store`, `Thumbs.db` - OS生成ファイル

### 📝 カスタマイズ

#### ローカル設定を無視したい場合
```gitignore
# ローカル設定ファイル
config/local_settings.json
my_custom_config.json
```

#### 特定のモデルファイルを無視したい場合
```gitignore
# 大きなモデルファイル
models/large_model.bin
whisper_models/large.pt
```

#### テスト用ファイルを無視したい場合
```gitignore
# テスト用メディア
test_audio/
sample_videos/
```

### 🚨 注意事項

#### 必ず無視すべきファイル
- **APIキー**: OpenAI、Google Translate等
- **認証情報**: トークン、証明書
- **個人情報**: ユーザーデータ、設定

#### 無視してはいけないファイル
- `.env.example` - 設定例ファイル
- `requirements.txt` - 依存関係
- `README.md` - ドキュメント

### 🔧 メンテナンス

#### 新しいファイルタイプを追加する場合
1. 該当する`.gitignore`に追加
2. 既存のリポジトリから削除が必要な場合:
   ```bash
   git rm --cached <filename>
   git commit -m "Remove tracked file"
   ```

#### キャッシュされたファイルを削除する場合
```bash
# 全てのキャッシュファイルを削除
git rm -r --cached .
git add .
git commit -m "Update .gitignore"
```

### 📚 参考リンク

- [Git公式 gitignore ドキュメント](https://git-scm.com/docs/gitignore)
- [GitHub gitignore テンプレート](https://github.com/github/gitignore)
- [Python用 gitignore テンプレート](https://github.com/github/gitignore/blob/main/Python.gitignore)