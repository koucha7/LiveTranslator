# Distribution Guide - YouTube Live Translator
# 配布ガイド

## 📦 配布方法一覧

### 1. Windows インストーラー (.exe)
**対象**: Windows 10/11 ユーザー
**特徴**: ワンクリックインストール、自動更新対応

```bash
# ビルド方法
cd build_tools
build.bat
```

**配布ファイル**:
- `LiveTranslator-1.0.0-setup.exe` (インストーラー)
- `LiveTranslator-1.0.0-windows-portable.zip` (ポータブル版)

### 2. macOS アプリケーション (.app)
**対象**: macOS 10.14+ ユーザー
**特徴**: ネイティブアプリケーション、Finder統合

```bash
# ビルド方法 (macOSで実行)
cd build_tools
python setup_macos.py py2app
```

**配布ファイル**:
- `LiveTranslator-1.0.0-macos.zip`

### 3. Linux実行ファイル
**対象**: Linux ユーザー
**特徴**: 依存関係込み、ポータブル

```bash
# ビルド方法
cd build_tools
bash build.sh
```

**配布ファイル**:
- `LiveTranslator-1.0.0-linux-portable.tar.gz`

### 4. Docker イメージ
**対象**: 全プラットフォーム
**特徴**: 環境構築不要、サーバー展開可能

```bash
# 使用方法
docker pull livetranslator/youtube-live-translator:latest
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key livetranslator/youtube-live-translator
```

### 5. Python Package (pip)
**対象**: 開発者、カスタマイズ希望者
**特徴**: ソースコード直接実行

```bash
# インストール方法
git clone https://github.com/livetranslator/youtube-live-translator.git
cd youtube-live-translator
pip install -r requirements.txt
python main.py web
```

## 🚀 自動配布システム

GitHub Actionsによる自動ビルド・配布システムを構築済み：

### リリース手順
1. バージョンタグを作成
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. GitHub Actionsが自動実行
   - Windows, macOS, Linux版をビルド
   - Docker イメージをビルド・プッシュ
   - GitHub Releases にアップロード

3. ユーザーがダウンロード可能

### 配布プラットフォーム

#### GitHub Releases
- **URL**: https://github.com/livetranslator/youtube-live-translator/releases
- **対象**: すべてのプラットフォーム
- **利点**: 無料、バージョン管理、リリースノート

#### Docker Hub
- **URL**: https://hub.docker.com/r/livetranslator/youtube-live-translator
- **対象**: Docker ユーザー
- **利点**: 自動ビルド、タグ管理

#### Microsoft Store (将来予定)
- **対象**: Windows ユーザー
- **利点**: 自動更新、セキュリティ

#### Mac App Store (将来予定)
- **対象**: macOS ユーザー
- **利点**: 自動更新、セキュリティ

## 📋 配布前チェックリスト

### ✅ ビルド確認
- [ ] Windows実行ファイルが正常動作
- [ ] macOSアプリケーションが正常動作
- [ ] Linux実行ファイルが正常動作
- [ ] Dockerイメージが正常動作

### ✅ セキュリティ確認
- [ ] ウイルススキャン完了
- [ ] 依存関係の脆弱性確認
- [ ] コード署名 (Windows/macOS)

### ✅ ドキュメント確認
- [ ] README.md 更新
- [ ] SETUP.md 更新
- [ ] CHANGELOG.md 更新
- [ ] リリースノート作成

### ✅ 機能テスト
- [ ] 音声認識テスト
- [ ] 翻訳機能テスト
- [ ] UI動作テスト
- [ ] エラーハンドリングテスト

## 🔧 カスタムビルド

### 企業向けカスタマイズ
```bash
# ブランディング変更
export APP_NAME="Company Live Translator"
export APP_AUTHOR="Company Name"
python build_tools/build.py
```

### 特定用途向け最適化
```bash
# 軽量版 (Whisper tiny のみ)
export WHISPER_MODELS="tiny"
export BUILD_VARIANT="lite"
python build_tools/build.py
```

## 📊 配布統計

配布後の統計を取得する仕組み：

### GitHub Analytics
- ダウンロード数
- 地域別統計
- バージョン別統計

### Docker Hub Analytics
- プル数
- 地域別統計

### 使用状況レポート (オプション)
プライバシーに配慮した使用統計の収集

## 🆘 配布サポート

### ユーザーサポート
- GitHub Issues
- Discord サーバー
- メールサポート

### 開発者向け
- API ドキュメント
- プラグイン開発ガイド
- コントリビューションガイド

## 📄 ライセンス・法的事項

### オープンソースライセンス
- メインコード: MIT License
- 依存関係: 各ライブラリのライセンスに従う

### 商用利用
- 個人・教育利用: 無料
- 商用利用: 無料（APIコスト除く）
- エンタープライズサポート: 有料オプション

### プライバシー
- 音声データ: ローカル処理、外部送信なし（API使用時除く）
- 使用統計: 匿名化、オプトイン

## 🔄 更新システム

### 自動更新 (将来実装予定)
- バックグラウンド更新チェック
- 段階的ロールアウト
- ロールバック機能

### 手動更新
- GitHub Releases から最新版ダウンロード
- インストーラー実行で上書きインストール
- 設定ファイル保持