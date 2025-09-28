"""
Live Translator Main System
YouTubeライブ配信のリアルタイム翻訳システム
"""

import os
import sys
import time
import threading
import logging
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from queue import Queue
from enum import Enum

# 自作モジュールをインポート
from youtube_extractor import YouTubeLiveAudioExtractor
from speech_recognition import SpeechRecognizer
from translator import Translator, TranslationEngine, TranslationCache

class ProcessingState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

@dataclass
class TranscriptionResult:
    """文字起こし結果"""
    timestamp: float
    original_text: str
    translated_text: Optional[str]
    confidence: float
    language: str

class LiveTranslator:
    def __init__(
        self,
        whisper_model: str = "base",
        use_whisper_api: bool = False,
        translation_engine: TranslationEngine = TranslationEngine.OPENAI,
        segment_duration: int = 10,
        cache_size: int = 500
    ):
        self.logger = self._setup_logger()
        
        # コンポーネント初期化
        self.audio_extractor = YouTubeLiveAudioExtractor()
        self.speech_recognizer = SpeechRecognizer(whisper_model, use_whisper_api)
        self.translator = Translator(translation_engine)
        self.translation_cache = TranslationCache(cache_size)
        
        # 設定
        self.segment_duration = segment_duration
        self.source_language = "en"
        self.target_language = "ja"
        
        # 状態管理
        self.state = ProcessingState.STOPPED
        self.current_url = None
        
        # キューとスレッド
        self.audio_queue = Queue()
        self.result_queue = Queue()
        self.workers = []
        
        # コールバック
        self.transcription_callback: Optional[Callable[[TranscriptionResult], None]] = None
        self.error_callback: Optional[Callable[[str], None]] = None
        self.state_callback: Optional[Callable[[ProcessingState], None]] = None
        
        # 統計情報
        self.stats = {
            "segments_processed": 0,
            "total_audio_time": 0.0,
            "total_processing_time": 0.0,
            "errors": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def _setup_logger(self) -> logging.Logger:
        """ログの設定"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def set_transcription_callback(self, callback: Callable[[TranscriptionResult], None]):
        """文字起こし結果のコールバックを設定"""
        self.transcription_callback = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        """エラーコールバックを設定"""
        self.error_callback = callback
    
    def set_state_callback(self, callback: Callable[[ProcessingState], None]):
        """状態変更コールバックを設定"""
        self.state_callback = callback
    
    def _update_state(self, new_state: ProcessingState):
        """状態を更新"""
        if self.state != new_state:
            self.state = new_state
            self.logger.info(f"状態変更: {new_state.value}")
            
            if self.state_callback:
                try:
                    self.state_callback(new_state)
                except Exception as e:
                    self.logger.error(f"状態コールバックエラー: {e}")
    
    def _handle_error(self, error_message: str):
        """エラーハンドリング"""
        self.logger.error(error_message)
        self.stats["errors"] += 1
        self._update_state(ProcessingState.ERROR)
        
        if self.error_callback:
            try:
                self.error_callback(error_message)
            except Exception as e:
                self.logger.error(f"エラーコールバックエラー: {e}")
    
    def _audio_processing_worker(self):
        """音声処理ワーカー"""
        while self.state in [ProcessingState.RUNNING, ProcessingState.STARTING]:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get(timeout=1)
                    
                    if audio_data is None:  # 終了シグナル
                        break
                    
                    start_time = time.time()
                    
                    # 音声認識
                    transcription = self.speech_recognizer.transcribe_audio_data(
                        audio_data, 
                        self.source_language
                    )
                    
                    if transcription and transcription.strip():
                        # キャッシュから翻訳を確認
                        cached_translation = self.translation_cache.get(
                            transcription, 
                            self.source_language, 
                            self.target_language
                        )
                        
                        if cached_translation:
                            translation = cached_translation
                            self.stats["cache_hits"] += 1
                        else:
                            # 翻訳実行
                            translation = self.translator.translate_text(
                                transcription,
                                self.source_language,
                                self.target_language
                            )
                            
                            if translation:
                                self.translation_cache.set(
                                    transcription,
                                    self.source_language,
                                    self.target_language,
                                    translation
                                )
                            
                            self.stats["cache_misses"] += 1
                        
                        # 信頼度計算
                        confidence = self.translator.get_translation_confidence(
                            transcription, 
                            translation or ""
                        )
                        
                        # 結果作成
                        result = TranscriptionResult(
                            timestamp=time.time(),
                            original_text=transcription,
                            translated_text=translation,
                            confidence=confidence,
                            language=self.source_language
                        )
                        
                        # コールバック実行
                        if self.transcription_callback:
                            try:
                                self.transcription_callback(result)
                            except Exception as e:
                                self.logger.error(f"転写コールバックエラー: {e}")
                        
                        # 統計更新
                        processing_time = time.time() - start_time
                        self.stats["segments_processed"] += 1
                        self.stats["total_processing_time"] += processing_time
                        self.stats["total_audio_time"] += self.segment_duration
                        
                        self.logger.info(
                            f"処理完了 - 元: '{transcription}' "
                            f"翻訳: '{translation}' 信頼度: {confidence:.2f}"
                        )
                    
                else:
                    time.sleep(0.1)  # キューが空の場合は待機
                    
            except Exception as e:
                self._handle_error(f"音声処理エラー: {e}")
                time.sleep(1)  # エラー後は待機
    
    def _audio_callback(self, audio_data: bytes):
        """音声データのコールバック"""
        try:
            # 音声検出
            if self.speech_recognizer.is_speech_detected(audio_data):
                self.audio_queue.put(audio_data)
            else:
                self.logger.debug("音声が検出されませんでした")
                
        except Exception as e:
            self.logger.error(f"音声コールバックエラー: {e}")
    
    def start_translation(self, youtube_url: str) -> bool:
        """翻訳を開始"""
        try:
            if self.state != ProcessingState.STOPPED:
                self.logger.warning("既に実行中です")
                return False
            
            self._update_state(ProcessingState.STARTING)
            self.current_url = youtube_url
            
            # YouTube URLの検証
            if not self.audio_extractor.is_live_stream(youtube_url):
                self._handle_error("指定されたURLはライブ配信ではありません")
                return False
            
            # ストリーム情報取得
            stream_info = self.audio_extractor.get_stream_info(youtube_url)
            if not stream_info:
                self._handle_error("ストリーム情報の取得に失敗しました")
                return False
            
            self.logger.info(f"配信開始: {stream_info['title']}")
            
            # ワーカースレッド開始
            worker_thread = threading.Thread(target=self._audio_processing_worker)
            worker_thread.daemon = True
            worker_thread.start()
            self.workers.append(worker_thread)
            
            # 音声抽出開始
            self.audio_extractor.start_continuous_extraction(
                youtube_url,
                self._audio_callback,
                self.segment_duration
            )
            
            self._update_state(ProcessingState.RUNNING)
            return True
            
        except Exception as e:
            self._handle_error(f"翻訳開始エラー: {e}")
            return False
    
    def stop_translation(self):
        """翻訳を停止"""
        try:
            self._update_state(ProcessingState.STOPPING)
            
            # 音声抽出停止
            self.audio_extractor.stop_extraction()
            
            # ワーカー停止
            self.audio_queue.put(None)  # 終了シグナル
            
            # スレッド終了待機
            for worker in self.workers:
                worker.join(timeout=5)
            
            self.workers.clear()
            
            # キュークリア
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except:
                    break
            
            self._update_state(ProcessingState.STOPPED)
            self.logger.info("翻訳を停止しました")
            
        except Exception as e:
            self._handle_error(f"翻訳停止エラー: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        stats = self.stats.copy()
        
        # 計算統計を追加
        if stats["segments_processed"] > 0:
            stats["avg_processing_time"] = (
                stats["total_processing_time"] / stats["segments_processed"]
            )
            stats["processing_speed_ratio"] = (
                stats["total_audio_time"] / stats["total_processing_time"]
            )
        else:
            stats["avg_processing_time"] = 0.0
            stats["processing_speed_ratio"] = 0.0
        
        # キャッシュ効果
        total_requests = stats["cache_hits"] + stats["cache_misses"]
        if total_requests > 0:
            stats["cache_hit_rate"] = stats["cache_hits"] / total_requests
        else:
            stats["cache_hit_rate"] = 0.0
        
        return stats
    
    def reset_stats(self):
        """統計情報をリセット"""
        self.stats = {
            "segments_processed": 0,
            "total_audio_time": 0.0,
            "total_processing_time": 0.0,
            "errors": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def configure(
        self,
        source_language: str = None,
        target_language: str = None,
        segment_duration: int = None
    ):
        """設定を変更"""
        if source_language:
            self.source_language = source_language
            
        if target_language:
            self.target_language = target_language
            
        if segment_duration:
            self.segment_duration = segment_duration
        
        self.logger.info(
            f"設定更新 - 元言語: {self.source_language}, "
            f"対象言語: {self.target_language}, "
            f"セグメント長: {self.segment_duration}秒"
        )


# 使用例とテスト用関数
def test_live_translator():
    """テスト用関数"""
    translator = LiveTranslator()
    
    # コールバック設定
    def transcription_callback(result: TranscriptionResult):
        print(f"\n[{time.strftime('%H:%M:%S')}]")
        print(f"原文: {result.original_text}")
        print(f"翻訳: {result.translated_text}")
        print(f"信頼度: {result.confidence:.2f}")
    
    def error_callback(error: str):
        print(f"エラー: {error}")
    
    def state_callback(state: ProcessingState):
        print(f"状態: {state.value}")
    
    translator.set_transcription_callback(transcription_callback)
    translator.set_error_callback(error_callback)
    translator.set_state_callback(state_callback)
    
    # テスト用URL（実際のライブ配信URLに置き換え）
    test_url = "https://www.youtube.com/watch?v=jfKfPfyJRdk"
    
    print("翻訳開始...")
    if translator.start_translation(test_url):
        try:
            # 60秒間実行
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n中断されました")
        finally:
            print("翻訳停止...")
            translator.stop_translation()
            
            # 統計表示
            stats = translator.get_stats()
            print(f"\n統計情報:")
            print(f"処理セグメント数: {stats['segments_processed']}")
            print(f"平均処理時間: {stats['avg_processing_time']:.2f}秒")
            print(f"キャッシュヒット率: {stats['cache_hit_rate']:.2%}")
            print(f"エラー数: {stats['errors']}")
    else:
        print("翻訳の開始に失敗しました")


if __name__ == "__main__":
    test_live_translator()