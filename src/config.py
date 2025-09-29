"""
Configuration Module
設定管理モジュール
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

@dataclass
class AudioConfig:
    """音声設定"""
    chunk_size: int = 1024
    sample_rate: int = 16000
    channels: int = 1
    segment_duration: int = 10
    
@dataclass
class WhisperConfig:
    """Whisper設定"""
    model_name: str = "base"
    use_api: bool = False
    language: str = "en"
    
@dataclass
class TranslationConfig:
    """翻訳設定"""
    engine: str = "google"  # openai or google (デフォルトは無料のgoogle)
    source_language: str = "en"
    target_language: str = "ja"
    gpt_model: str = "gpt-3.5-turbo"
    max_tokens: int = 150
    
@dataclass
class UIConfig:
    """UI設定"""
    port: int = 8501
    debug_mode: bool = False
    max_transcriptions: int = 1000
    auto_refresh_interval: int = 2

class Config:
    """メイン設定クラス"""
    
    def __init__(self):
        self.audio = AudioConfig()
        self.whisper = WhisperConfig()
        self.translation = TranslationConfig()
        self.ui = UIConfig()
        
        # 環境変数から設定を読み込み
        self._load_from_env()
    
    def _load_from_env(self):
        """環境変数から設定を読み込み"""
        # Audio settings
        self.audio.chunk_size = int(os.getenv("AUDIO_CHUNK_SIZE", self.audio.chunk_size))
        self.audio.sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE", self.audio.sample_rate))
        self.audio.channels = int(os.getenv("AUDIO_CHANNELS", self.audio.channels))
        
        # Whisper settings
        self.whisper.model_name = os.getenv("WHISPER_MODEL", self.whisper.model_name)
        self.whisper.use_api = os.getenv("USE_WHISPER_API", "false").lower() == "true"
        
        # Translation settings
        self.translation.engine = os.getenv("TRANSLATION_ENGINE", self.translation.engine)
        self.translation.gpt_model = os.getenv("GPT_MODEL", self.translation.gpt_model)
        self.translation.max_tokens = int(os.getenv("MAX_TOKENS", self.translation.max_tokens))
        
        # UI settings
        self.ui.port = int(os.getenv("STREAMLIT_PORT", self.ui.port))
        self.ui.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    def get_api_keys(self) -> Dict[str, Optional[str]]:
        """APIキーを取得"""
        return {
            "openai": os.getenv("OPENAI_API_KEY"),
            "google_translate": os.getenv("GOOGLE_TRANSLATE_API_KEY")
        }
    
    def validate(self) -> bool:
        """設定の妥当性を検証"""
        api_keys = self.get_api_keys()
        
        # OpenAI APIキーの確認と自動フォールバック
        if self.whisper.use_api or self.translation.engine == "openai":
            if not api_keys["openai"]:
                print("OpenAI APIキーが設定されていません。無料版に切り替えます:")
                print("- 音声認識: Whisperローカルモデル使用")
                print("- 翻訳: Google Translate無料版使用")
                
                # 無料版設定に自動切り替え
                self.whisper.use_api = False
                self.translation.engine = "google"
        
        # Google Translate APIキーの確認
        if self.translation.engine == "google":
            if not api_keys["google_translate"]:
                print("Google Translate無料版を使用します (googletrans)")
        
        return True
    
    def update_from_dict(self, settings: Dict[str, Any]):
        """辞書から設定を更新"""
        if 'whisper_model' in settings:
            self.whisper.model_name = settings['whisper_model']
        if 'use_whisper_api' in settings:
            self.whisper.use_api = settings['use_whisper_api']
        if 'translation_engine' in settings:
            self.translation.engine = settings['translation_engine']
        if 'segment_duration' in settings:
            self.audio.segment_duration = settings['segment_duration']
        if 'sample_rate' in settings:
            self.audio.sample_rate = settings['sample_rate']
        if 'chunk_size' in settings:
            self.audio.chunk_size = settings['chunk_size']
    
    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書として取得"""
        return {
            "audio": {
                "chunk_size": self.audio.chunk_size,
                "sample_rate": self.audio.sample_rate,
                "channels": self.audio.channels,
                "segment_duration": self.audio.segment_duration
            },
            "whisper": {
                "model_name": self.whisper.model_name,
                "use_api": self.whisper.use_api,
                "language": self.whisper.language
            },
            "translation": {
                "engine": self.translation.engine,
                "source_language": self.translation.source_language,
                "target_language": self.translation.target_language,
                "gpt_model": self.translation.gpt_model,
                "max_tokens": self.translation.max_tokens
            },
            "ui": {
                "port": self.ui.port,
                "debug_mode": self.ui.debug_mode,
                "max_transcriptions": self.ui.max_transcriptions,
                "auto_refresh_interval": self.ui.auto_refresh_interval
            }
        }

# グローバル設定インスタンス
config = Config()