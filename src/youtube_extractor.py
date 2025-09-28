"""
YouTube Live Audio Extractor
YouTubeライブ配信から音声を抽出するモジュール
"""

import os
import sys
import subprocess
import tempfile
import threading
import time
import logging
from typing import Optional, Generator, Callable
from queue import Queue
import yt_dlp
from pydub import AudioSegment
import io

class YouTubeLiveAudioExtractor:
    def __init__(self, output_dir: str = "temp"):
        self.output_dir = output_dir
        self.is_streaming = False
        self.audio_queue = Queue()
        self.logger = self._setup_logger()
        
        # yt-dlpの設定
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
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
    
    def is_live_stream(self, url: str) -> bool:
        """URLがライブ配信かどうかを確認"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('is_live', False)
        except Exception as e:
            self.logger.error(f"ライブ配信確認エラー: {e}")
            return False
    
    def get_stream_info(self, url: str) -> Optional[dict]:
        """ストリーム情報を取得"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration'),
                    'is_live': info.get('is_live', False),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'formats': info.get('formats', [])
                }
        except Exception as e:
            self.logger.error(f"ストリーム情報取得エラー: {e}")
            return None
    
    def extract_audio_segment(self, url: str, duration: int = 10) -> Optional[bytes]:
        """指定した時間分の音声セグメントを抽出"""
        try:
            # 一時ファイル作成
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # ffmpegでライブストリームから音声を抽出
            cmd = [
                'ffmpeg',
                '-i', url,
                '-t', str(duration),
                '-vn',  # 映像なし
                '-acodec', 'pcm_s16le',
                '-ar', '16000',  # 16kHz sampling rate
                '-ac', '1',  # モノラル
                '-y',  # 上書き
                temp_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration + 10
            )
            
            if result.returncode != 0:
                self.logger.error(f"ffmpeg エラー: {result.stderr}")
                return None
            
            # 音声データを読み込み
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # 一時ファイル削除
            os.unlink(temp_path)
            
            return audio_data
            
        except subprocess.TimeoutExpired:
            self.logger.error("音声抽出がタイムアウトしました")
            return None
        except Exception as e:
            self.logger.error(f"音声抽出エラー: {e}")
            return None
    
    def get_best_audio_url(self, url: str) -> Optional[str]:
        """最適な音声ストリームURLを取得"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                # 音声のみのフォーマットを優先的に選択
                audio_formats = [
                    f for f in formats 
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none'
                ]
                
                if not audio_formats:
                    # 音声付きフォーマットを選択
                    audio_formats = [
                        f for f in formats 
                        if f.get('acodec') != 'none'
                    ]
                
                if audio_formats:
                    # 最高品質の音声を選択
                    best_audio = max(
                        audio_formats, 
                        key=lambda x: x.get('abr', 0) or 0
                    )
                    return best_audio.get('url')
                
                return None
                
        except Exception as e:
            self.logger.error(f"音声URL取得エラー: {e}")
            return None
    
    def start_continuous_extraction(
        self, 
        url: str, 
        callback: Callable[[bytes], None],
        segment_duration: int = 10
    ) -> None:
        """連続的な音声抽出を開始"""
        self.is_streaming = True
        
        def extraction_worker():
            audio_url = self.get_best_audio_url(url)
            if not audio_url:
                self.logger.error("音声URLの取得に失敗しました")
                return
            
            self.logger.info(f"音声抽出開始: {url}")
            
            while self.is_streaming:
                try:
                    audio_data = self.extract_audio_segment(
                        audio_url, 
                        segment_duration
                    )
                    
                    if audio_data:
                        callback(audio_data)
                    else:
                        self.logger.warning("音声データの取得に失敗しました")
                        time.sleep(1)  # エラー時は少し待機
                        
                except Exception as e:
                    self.logger.error(f"音声抽出エラー: {e}")
                    time.sleep(2)  # エラー時は待機
        
        # バックグラウンドで実行
        extraction_thread = threading.Thread(target=extraction_worker)
        extraction_thread.daemon = True
        extraction_thread.start()
    
    def stop_extraction(self) -> None:
        """音声抽出を停止"""
        self.is_streaming = False
        self.logger.info("音声抽出を停止しました")
    
    def convert_to_wav(self, audio_data: bytes, target_sr: int = 16000) -> bytes:
        """音声データをWAV形式に変換"""
        try:
            # pydubで音声データを処理
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            
            # サンプリングレートと形式を調整
            audio = audio.set_frame_rate(target_sr)
            audio = audio.set_channels(1)  # モノラル
            audio = audio.set_sample_width(2)  # 16-bit
            
            # WAVとして出力
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format="wav")
            return output_buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"音声変換エラー: {e}")
            return audio_data  # 変換失敗時は元データを返す


# 使用例とテスト用関数
def test_extractor():
    """テスト用関数"""
    extractor = YouTubeLiveAudioExtractor()
    
    # テスト用YouTube URL（実際のライブ配信URLに置き換えてください）
    test_url = "https://www.youtube.com/watch?v=jfKfPfyJRdk"  # 24/7 lofi stream
    
    # ストリーム情報取得テスト
    info = extractor.get_stream_info(test_url)
    if info:
        print(f"タイトル: {info['title']}")
        print(f"ライブ配信: {info['is_live']}")
        print(f"アップローダー: {info['uploader']}")
    
    # 音声抽出テスト
    def audio_callback(audio_data):
        print(f"音声データ受信: {len(audio_data)} bytes")
    
    extractor.start_continuous_extraction(test_url, audio_callback, 5)
    
    # 30秒間実行
    time.sleep(30)
    extractor.stop_extraction()


if __name__ == "__main__":
    test_extractor()