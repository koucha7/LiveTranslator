"""
Speech Recognition Module
OpenAI Whisperを使用した音声認識モジュール
"""

import os
import io
import logging
import tempfile
import wave
from typing import Optional, Union
import whisper
import openai
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class SpeechRecognizer:
    def __init__(self, model_name: str = "base", use_api: bool = False):
        self.logger = self._setup_logger()
        self.use_api = use_api
        
        if use_api:
            # OpenAI APIを使用
            self.client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = None
            self.logger.info("OpenAI Whisper APIを使用します")
        else:
            # ローカルWhisperモデルを使用
            try:
                self.model = whisper.load_model(model_name)
                self.client = None
                self.logger.info(f"Whisperモデル '{model_name}' を読み込みました")
            except Exception as e:
                self.logger.error(f"Whisperモデルの読み込みに失敗: {e}")
                raise
    
    def _setup_logger(self) -> logging.Logger:
        """ログの設定"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def transcribe_audio_data(self, audio_data: bytes, language: str = "en") -> Optional[str]:
        """
        音声データを文字起こし
        
        Args:
            audio_data: WAV形式の音声データ
            language: 音声の言語コード (en, ja, etc.)
        
        Returns:
            文字起こし結果のテキスト
        """
        try:
            if self.use_api:
                return self._transcribe_with_api(audio_data, language)
            else:
                return self._transcribe_with_local_model(audio_data, language)
                
        except Exception as e:
            self.logger.error(f"音声認識エラー: {e}")
            return None
    
    def _transcribe_with_api(self, audio_data: bytes, language: str) -> Optional[str]:
        """OpenAI APIで音声認識"""
        try:
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # APIで音声認識
            with open(temp_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="text"  # テキスト形式で取得
                )
            
            # 一時ファイル削除
            os.unlink(temp_path)
            
            if isinstance(transcript, str):
                return transcript.strip()
            else:
                return transcript.text.strip() if hasattr(transcript, 'text') else str(transcript).strip()
                
        except Exception as e:
            self.logger.error(f"OpenAI API音声認識エラー: {e}")
            return None
    
    def _transcribe_with_local_model(self, audio_data: bytes, language: str) -> Optional[str]:
        """ローカルWhisperモデルで音声認識"""
        try:
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Whisperで音声認識
            result = self.model.transcribe(
                temp_path,
                language=language,
                fp16=False  # CPUの場合はFalse
            )
            
            # 一時ファイル削除
            os.unlink(temp_path)
            
            return result.get("text", "").strip()
            
        except Exception as e:
            self.logger.error(f"ローカルWhisper音声認識エラー: {e}")
            return None
    
    def transcribe_file(self, file_path: str, language: str = "en") -> Optional[str]:
        """
        音声ファイルを文字起こし
        
        Args:
            file_path: 音声ファイルのパス
            language: 音声の言語コード
        
        Returns:
            文字起こし結果のテキスト
        """
        try:
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            return self.transcribe_audio_data(audio_data, language)
            
        except Exception as e:
            self.logger.error(f"ファイル読み込みエラー: {e}")
            return None
    
    def is_speech_detected(self, audio_data: bytes, threshold: int = 1000) -> bool:
        """
        音声データに音声が含まれているかを判定
        
        Args:
            audio_data: 音声データ
            threshold: 音声検出のしきい値
        
        Returns:
            音声が検出された場合True
        """
        try:
            # 簡単な音量ベースの検出
            # 実際の実装ではVAD (Voice Activity Detection) を使用することが推奨
            audio_stream = io.BytesIO(audio_data)
            
            with wave.open(audio_stream, 'rb') as wave_file:
                frames = wave_file.readframes(wave_file.getnframes())
                
            # 音声データのRMS値を計算
            import numpy as np
            audio_array = np.frombuffer(frames, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_array**2))
            
            return rms > threshold
            
        except Exception as e:
            self.logger.error(f"音声検出エラー: {e}")
            return True  # エラー時は音声ありと判定


class WhisperConfig:
    """Whisperの設定クラス"""
    
    # 利用可能なモデル
    MODELS = {
        "tiny": "最小モデル（高速、低精度）",
        "base": "基本モデル（バランス型）",
        "small": "小型モデル（やや高精度）",
        "medium": "中型モデル（高精度）",
        "large": "大型モデル（最高精度、低速）"
    }
    
    # 言語コード
    LANGUAGES = {
        "en": "English",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "ru": "Russian"
    }
    
    @classmethod
    def get_recommended_model(cls, speed_priority: bool = True) -> str:
        """
        推奨モデルを取得
        
        Args:
            speed_priority: 速度を優先する場合True、精度を優先する場合False
        
        Returns:
            推奨モデル名
        """
        return "base" if speed_priority else "small"


# 使用例とテスト用関数
def test_speech_recognizer():
    """テスト用関数"""
    # ローカルモデルでテスト
    recognizer = SpeechRecognizer(model_name="base", use_api=False)
    
    # テスト用音声ファイルがある場合
    test_file = "test_audio.wav"
    if os.path.exists(test_file):
        result = recognizer.transcribe_file(test_file, language="en")
        print(f"認識結果: {result}")
    else:
        print("テスト用音声ファイルが見つかりません")
    
    # APIでテスト（APIキーが設定されている場合）
    if os.getenv("OPENAI_API_KEY"):
        api_recognizer = SpeechRecognizer(use_api=True)
        print("OpenAI API認識テスト準備完了")


if __name__ == "__main__":
    test_speech_recognizer()