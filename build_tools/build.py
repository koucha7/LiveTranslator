#!/usr/bin/env python3
"""
Build Script for YouTube Live Translator
配布用バイナリのビルドスクリプト
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import argparse
import zipfile
import tarfile

class Builder:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        self.platform = platform.system().lower()
        self.version = "1.0.0"
        
    def clean(self):
        """ビルドディレクトリをクリーンアップ"""
        print("🧹 ビルドディレクトリをクリーンアップ中...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  ✅ {dir_path} を削除しました")
        
        # __pycache__ も削除
        for pycache in self.root_dir.rglob("__pycache__"):
            shutil.rmtree(pycache)
        
        print("✅ クリーンアップ完了")
    
    def install_build_deps(self):
        """ビルド用依存関係をインストール"""
        print("📦 ビルド用依存関係をインストール中...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.root_dir / "requirements-build.txt")
            ], check=True)
            print("✅ ビルド用依存関係のインストール完了")
        except subprocess.CalledProcessError as e:
            print(f"❌ ビルド用依存関係のインストールに失敗: {e}")
            sys.exit(1)
    
    def build_executable(self):
        """実行ファイルをビルド"""
        print("🔨 実行ファイルをビルド中...")
        
        spec_file = self.root_dir / "build_tools" / "livetranslator.spec"
        
        try:
            subprocess.run([
                "pyinstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ], cwd=self.root_dir, check=True)
            print("✅ 実行ファイルのビルド完了")
        except subprocess.CalledProcessError as e:
            print(f"❌ 実行ファイルのビルドに失敗: {e}")
            sys.exit(1)
    
    def create_installer_windows(self):
        """Windows用インストーラーを作成"""
        if self.platform != "windows":
            print("⚠️ Windows用インストーラーはWindowsでのみ作成できます")
            return
        
        print("📦 Windows用インストーラーを作成中...")
        
        # Inno Setup スクリプトを作成
        inno_script = self.create_inno_setup_script()
        
        try:
            subprocess.run([
                "iscc",  # Inno Setup Compiler
                str(inno_script)
            ], check=True)
            print("✅ Windows用インストーラーの作成完了")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️ Windows用インストーラーの作成に失敗: {e}")
            print("   Inno Setupがインストールされていない可能性があります")
    
    def create_inno_setup_script(self):
        """Inno Setup スクリプトを作成"""
        script_content = f'''
[Setup]
AppName=YouTube Live Translator
AppVersion={self.version}
AppPublisher=LiveTranslator Team
AppPublisherURL=https://github.com/livetranslator/livetranslator
AppSupportURL=https://github.com/livetranslator/livetranslator/issues
AppUpdatesURL=https://github.com/livetranslator/livetranslator/releases
DefaultDirName={{autopf}}\\LiveTranslator
DefaultGroupName=YouTube Live Translator
AllowNoIcons=yes
LicenseFile={self.root_dir}\\LICENSE
OutputDir={self.dist_dir}
OutputBaseFilename=LiveTranslator-{self.version}-setup
SetupIconFile={self.root_dir}\\assets\\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\\Japanese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "{self.dist_dir}\\LiveTranslator\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{self.root_dir}\\README.md"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{self.root_dir}\\SETUP.md"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{self.root_dir}\\LICENSE"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\YouTube Live Translator"; Filename: "{{app}}\\LiveTranslator.exe"
Name: "{{group}}\\{{cm:ProgramOnTheWeb,YouTube Live Translator}}"; Filename: "https://github.com/livetranslator/livetranslator"
Name: "{{group}}\\{{cm:UninstallProgram,YouTube Live Translator}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\YouTube Live Translator"; Filename: "{{app}}\\LiveTranslator.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\YouTube Live Translator"; Filename: "{{app}}\\LiveTranslator.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\LiveTranslator.exe"; Parameters: "config --validate"; Description: "{{cm:LaunchProgram,YouTube Live Translator}}"; Flags: nowait postinstall skipifsilent
'''
        
        script_path = self.root_dir / "build_tools" / "installer.iss"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return script_path
    
    def create_portable_archive(self):
        """ポータブル版のアーカイブを作成"""
        print("📦 ポータブル版アーカイブを作成中...")
        
        dist_folder = self.dist_dir / "LiveTranslator"
        if not dist_folder.exists():
            print("❌ 配布フォルダが見つかりません")
            return
        
        # プラットフォーム別のアーカイブ形式
        if self.platform == "windows":
            archive_name = f"LiveTranslator-{self.version}-windows-portable.zip"
            archive_path = self.dist_dir / archive_name
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in dist_folder.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(dist_folder)
                        zipf.write(file_path, arcname)
        else:
            archive_name = f"LiveTranslator-{self.version}-{self.platform}-portable.tar.gz"
            archive_path = self.dist_dir / archive_name
            
            with tarfile.open(archive_path, 'w:gz') as tarf:
                tarf.add(dist_folder, arcname="LiveTranslator")
        
        print(f"✅ ポータブル版アーカイブを作成: {archive_name}")
    
    def create_assets(self):
        """アセット（アイコンなど）を作成"""
        print("🎨 アセットを作成中...")
        
        assets_dir = self.root_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # 簡単なアイコンファイルを作成（実際のプロジェクトでは適切なアイコンを用意）
        icon_path = assets_dir / "icon.ico"
        if not icon_path.exists():
            # プレースホルダーアイコンの作成（実際にはデザイナーが作成）
            print("  ⚠️ アイコンファイルがありません。assets/icon.ico を作成してください")
    
    def post_build_tasks(self):
        """ビルド後のタスク"""
        print("📋 ビルド後のタスクを実行中...")
        
        # README をコピー
        dist_folder = self.dist_dir / "LiveTranslator"
        if dist_folder.exists():
            for file_name in ["README.md", "SETUP.md", "LICENSE"]:
                src = self.root_dir / file_name
                dst = dist_folder / file_name
                if src.exists() and not dst.exists():
                    shutil.copy2(src, dst)
        
        # 設定例ファイルをコピー
        config_src = self.root_dir / "config" / ".env.example"
        config_dst = dist_folder / "config" / ".env.example"
        if config_src.exists():
            config_dst.parent.mkdir(exist_ok=True)
            shutil.copy2(config_src, config_dst)
        
        print("✅ ビルド後のタスク完了")
    
    def build_all(self):
        """全体のビルドプロセスを実行"""
        print(f"🚀 YouTube Live Translator v{self.version} のビルドを開始")
        print(f"📋 プラットフォーム: {self.platform}")
        print("=" * 50)
        
        try:
            self.clean()
            self.install_build_deps()
            self.create_assets()
            self.build_executable()
            self.post_build_tasks()
            
            if self.platform == "windows":
                self.create_installer_windows()
            
            self.create_portable_archive()
            
            print("=" * 50)
            print("🎉 ビルド完了！")
            print(f"📁 配布ファイルは {self.dist_dir} にあります")
            
            # 作成されたファイルをリスト表示
            if self.dist_dir.exists():
                print("📦 作成されたファイル:")
                for file_path in self.dist_dir.iterdir():
                    if file_path.is_file():
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        print(f"  📄 {file_path.name} ({size_mb:.1f} MB)")
            
        except Exception as e:
            print(f"❌ ビルド中にエラーが発生しました: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="YouTube Live Translator ビルドスクリプト")
    parser.add_argument("--clean", action="store_true", help="クリーンアップのみ実行")
    parser.add_argument("--no-installer", action="store_true", help="インストーラー作成をスキップ")
    
    args = parser.parse_args()
    
    builder = Builder()
    
    if args.clean:
        builder.clean()
    else:
        builder.build_all()

if __name__ == "__main__":
    main()