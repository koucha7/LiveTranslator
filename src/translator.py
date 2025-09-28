"""
Translation Module
OpenAI GPTとGoogle Translateを使用した翻訳モジュール
"""

import os
import logging
import time
from typing import Optional, List, Dict, Any
from enum import Enum
import openai
from googletrans import Translator as GoogleTranslator
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class TranslationEngine(Enum):
    OPENAI = "openai"
    GOOGLE = "google"

class Translator:
    def __init__(self, engine: TranslationEngine = TranslationEngine.OPENAI):
        self.engine = engine
        self.logger = self._setup_logger()
        
        # 初期化
        if engine == TranslationEngine.OPENAI:
            self._init_openai()
        else:
            self._init_google()
        
        # レート制限対策
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms間隔
    
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
    
    def _init_openai(self):
        """OpenAI APIの初期化"""
        try:
            self.client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.google_translator = None
            self.logger.info("OpenAI APIを初期化しました")
        except Exception as e:
            self.logger.error(f"OpenAI API初期化エラー: {e}")
            raise
    
    def _init_google(self):
        """Google Translate APIの初期化"""
        try:
            self.google_translator = GoogleTranslator()
            self.client = None
            self.logger.info("Google Translate APIを初期化しました")
        except Exception as e:
            self.logger.error(f"Google Translate API初期化エラー: {e}")
            raise
    
    def _rate_limit(self):
        """レート制限の実装"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def translate_text(
        self, 
        text: str, 
        source_lang: str = "en", 
        target_lang: str = "ja",
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        テキストを翻訳
        
        Args:
            text: 翻訳するテキスト
            source_lang: 元言語（en, ja, etc.）
            target_lang: 翻訳先言語（ja, en, etc.）
            context: 翻訳の文脈情報（OpenAIのみ）
        
        Returns:
            翻訳されたテキスト
        """
        if not text.strip():
            return ""
        
        try:
            self._rate_limit()
            
            if self.engine == TranslationEngine.OPENAI:
                return self._translate_with_openai(text, source_lang, target_lang, context)
            else:
                return self._translate_with_google(text, source_lang, target_lang)
                
        except Exception as e:
            self.logger.error(f"翻訳エラー: {e}")
            return None
    
    def _translate_with_openai(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """OpenAI GPTで翻訳"""
        try:
            # 言語コードを言語名に変換
            lang_names = {
                "en": "English",
                "ja": "Japanese",
                "ko": "Korean",
                "zh": "Chinese",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "ru": "Russian"
            }
            
            source_name = lang_names.get(source_lang, source_lang)
            target_name = lang_names.get(target_lang, target_lang)
            
            # プロンプト作成
            system_prompt = f"""You are a professional translator. Translate the given {source_name} text to {target_name}.
Please provide only the translation without any explanations or additional text.
Keep the tone and style of the original text.
If the text contains technical terms or proper nouns, preserve them appropriately."""
            
            user_prompt = text
            
            # 文脈情報がある場合は追加
            if context:
                user_prompt = f"Context: {context}\n\nText to translate: {text}"
            
            response = self.client.chat.completions.create(
                model=os.getenv("GPT_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=int(os.getenv("MAX_TOKENS", "150")),
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI翻訳エラー: {e}")
            return None
    
    def _translate_with_google(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> Optional[str]:
        """Google Translateで翻訳"""
        try:
            result = self.google_translator.translate(
                text, 
                src=source_lang, 
                dest=target_lang
            )
            return result.text
            
        except Exception as e:
            self.logger.error(f"Google Translate翻訳エラー: {e}")
            return None
    
    def translate_batch(
        self, 
        texts: List[str], 
        source_lang: str = "en", 
        target_lang: str = "ja"
    ) -> List[Optional[str]]:
        """
        複数のテキストを一括翻訳
        
        Args:
            texts: 翻訳するテキストのリスト
            source_lang: 元言語
            target_lang: 翻訳先言語
        
        Returns:
            翻訳結果のリスト
        """
        results = []
        
        for text in texts:
            translated = self.translate_text(text, source_lang, target_lang)
            results.append(translated)
        
        return results
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        テキストの言語を検出
        
        Args:
            text: 検出するテキスト
        
        Returns:
            言語コード（en, ja, etc.）
        """
        if not text.strip():
            return None
        
        try:
            if self.engine == TranslationEngine.GOOGLE:
                detected = self.google_translator.detect(text)
                return detected.lang
            else:
                # OpenAIで言語検出
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "Detect the language of the given text. Respond with only the ISO 639-1 language code (e.g., 'en', 'ja', 'ko')."
                        },
                        {"role": "user", "content": text}
                    ],
                    max_tokens=10,
                    temperature=0
                )
                return response.choices[0].message.content.strip().lower()
                
        except Exception as e:
            self.logger.error(f"言語検出エラー: {e}")
            return None
    
    def get_translation_confidence(self, original: str, translated: str) -> float:
        """
        翻訳の信頼度を評価（簡易版）
        
        Args:
            original: 元のテキスト
            translated: 翻訳されたテキスト
        
        Returns:
            信頼度スコア（0.0-1.0）
        """
        try:
            # 簡易的な信頼度計算
            # 実際の実装ではより高度な評価手法を使用
            
            if not original.strip() or not translated.strip():
                return 0.0
            
            # 長さの比較
            length_ratio = min(len(translated), len(original)) / max(len(translated), len(original))
            
            # 空でない翻訳があれば基本点
            base_score = 0.7 if translated.strip() else 0.0
            
            # 長さの妥当性を考慮
            confidence = base_score * length_ratio
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"信頼度評価エラー: {e}")
            return 0.0


class TranslationCache:
    """翻訳結果のキャッシュ"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, str] = {}
        self.max_size = max_size
        self.access_order: List[str] = []
    
    def _make_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """キャッシュキーを生成"""
        return f"{source_lang}->{target_lang}:{hash(text)}"
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """キャッシュから翻訳結果を取得"""
        key = self._make_key(text, source_lang, target_lang)
        
        if key in self.cache:
            # アクセス順序を更新
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        
        return None
    
    def set(self, text: str, source_lang: str, target_lang: str, translation: str):
        """翻訳結果をキャッシュに保存"""
        key = self._make_key(text, source_lang, target_lang)
        
        # キャッシュサイズ制限
        if len(self.cache) >= self.max_size and key not in self.cache:
            # 最も古いエントリを削除
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = translation
        
        if key not in self.access_order:
            self.access_order.append(key)
    
    def clear(self):
        """キャッシュをクリア"""
        self.cache.clear()
        self.access_order.clear()


# 使用例とテスト用関数
def test_translator():
    """テスト用関数"""
    # OpenAI翻訳テスト
    if os.getenv("OPENAI_API_KEY"):
        translator = Translator(TranslationEngine.OPENAI)
        
        test_text = "Hello, how are you today?"
        result = translator.translate_text(test_text, "en", "ja")
        print(f"OpenAI翻訳: {test_text} -> {result}")
        
        # 言語検出テスト
        detected = translator.detect_language(test_text)
        print(f"検出言語: {detected}")
    
    # Google翻訳テスト
    google_translator = Translator(TranslationEngine.GOOGLE)
    test_text = "Good morning!"
    result = google_translator.translate_text(test_text, "en", "ja")
    print(f"Google翻訳: {test_text} -> {result}")


if __name__ == "__main__":
    test_translator()