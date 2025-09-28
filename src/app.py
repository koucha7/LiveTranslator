"""
Streamlit Web Interface for Live Translator
YouTubeライブ翻訳ツールのWebインターフェース
"""

import streamlit as st
import time
import threading
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import asdict

# 自作モジュールをインポート
from live_translator import LiveTranslator, ProcessingState, TranscriptionResult
from translator import TranslationEngine

# ページ設定
st.set_page_config(
    page_title="YouTube Live Translator",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #4ECDC4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-running {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-stopped {
        color: #F44336;
        font-weight: bold;
    }
    .status-error {
        color: #FF9800;
        font-weight: bold;
    }
    .transcription-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4ECDC4;
    }
    .translation-box {
        background-color: #fff8e1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #FF6B6B;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """セッション状態の初期化"""
    if 'translator' not in st.session_state:
        st.session_state.translator = None
    
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    
    if 'transcriptions' not in st.session_state:
        st.session_state.transcriptions = []
    
    if 'current_stats' not in st.session_state:
        st.session_state.current_stats = {}
    
    if 'current_state' not in st.session_state:
        st.session_state.current_state = ProcessingState.STOPPED

def create_translator(config):
    """翻訳器を作成"""
    translator = LiveTranslator(
        whisper_model=config['whisper_model'],
        use_whisper_api=config['use_whisper_api'],
        translation_engine=config['translation_engine'],
        segment_duration=config['segment_duration']
    )
    
    # コールバック設定
    translator.set_transcription_callback(on_transcription)
    translator.set_error_callback(on_error)
    translator.set_state_callback(on_state_change)
    
    return translator

def on_transcription(result: TranscriptionResult):
    """文字起こし結果のコールバック"""
    st.session_state.transcriptions.append({
        'timestamp': datetime.fromtimestamp(result.timestamp),
        'original': result.original_text,
        'translated': result.translated_text,
        'confidence': result.confidence,
        'language': result.language
    })
    
    # 最大1000件まで保持
    if len(st.session_state.transcriptions) > 1000:
        st.session_state.transcriptions = st.session_state.transcriptions[-1000:]

def on_error(error_message: str):
    """エラーコールバック"""
    st.error(f"エラー: {error_message}")

def on_state_change(state: ProcessingState):
    """状態変更コールバック"""
    st.session_state.current_state = state
    st.session_state.is_running = (state == ProcessingState.RUNNING)

def render_sidebar():
    """サイドバーのレンダリング"""
    st.sidebar.title("⚙️ 設定")
    
    # 基本設定
    st.sidebar.subheader("🎵 音声設定")
    whisper_model = st.sidebar.selectbox(
        "Whisperモデル",
        ["tiny", "base", "small", "medium", "large"],
        index=1,
        help="大きなモデルほど精度が高いが処理時間も長くなります"
    )
    
    use_whisper_api = st.sidebar.checkbox(
        "OpenAI Whisper APIを使用",
        value=False,
        help="APIを使用すると処理が高速になりますが料金が発生します"
    )
    
    # 翻訳設定
    st.sidebar.subheader("🌍 翻訳設定")
    translation_engine = st.sidebar.selectbox(
        "翻訳エンジン",
        [TranslationEngine.OPENAI, TranslationEngine.GOOGLE],
        index=0,
        format_func=lambda x: "OpenAI GPT" if x == TranslationEngine.OPENAI else "Google Translate"
    )
    
    source_language = st.sidebar.selectbox(
        "元言語",
        ["en", "ja", "ko", "zh", "es", "fr", "de", "ru"],
        index=0,
        format_func=lambda x: {
            "en": "英語", "ja": "日本語", "ko": "韓国語", "zh": "中国語",
            "es": "スペイン語", "fr": "フランス語", "de": "ドイツ語", "ru": "ロシア語"
        }.get(x, x)
    )
    
    target_language = st.sidebar.selectbox(
        "翻訳先言語",
        ["ja", "en", "ko", "zh", "es", "fr", "de", "ru"],
        index=0,
        format_func=lambda x: {
            "en": "英語", "ja": "日本語", "ko": "韓国語", "zh": "中国語",
            "es": "スペイン語", "fr": "フランス語", "de": "ドイツ語", "ru": "ロシア語"
        }.get(x, x)
    )
    
    # 詳細設定
    st.sidebar.subheader("🔧 詳細設定")
    segment_duration = st.sidebar.slider(
        "音声セグメント長（秒）",
        min_value=5,
        max_value=30,
        value=10,
        help="短いと応答性が良いが処理負荷が高くなります"
    )
    
    return {
        'whisper_model': whisper_model,
        'use_whisper_api': use_whisper_api,
        'translation_engine': translation_engine,
        'source_language': source_language,
        'target_language': target_language,
        'segment_duration': segment_duration
    }

def render_main_interface(config):
    """メインインターフェースのレンダリング"""
    st.markdown('<h1 class="main-header">🎥 YouTube Live Translator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">YouTubeライブ配信をリアルタイムで翻訳</p>', unsafe_allow_html=True)
    
    # URL入力
    col1, col2 = st.columns([3, 1])
    
    with col1:
        youtube_url = st.text_input(
            "YouTube ライブ配信URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="YouTubeのライブ配信URLを入力してください"
        )
    
    with col2:
        st.write("")  # スペース調整
        st.write("")  # スペース調整
        
        if st.session_state.is_running:
            if st.button("⏹️ 停止", type="secondary", use_container_width=True):
                if st.session_state.translator:
                    st.session_state.translator.stop_translation()
                    st.success("翻訳を停止しました")
        else:
            if st.button("▶️ 開始", type="primary", use_container_width=True):
                if not youtube_url:
                    st.error("YouTubeのURLを入力してください")
                else:
                    start_translation(youtube_url, config)
    
    # 状態表示
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        state_text = st.session_state.current_state.value.upper()
        if st.session_state.current_state == ProcessingState.RUNNING:
            st.markdown(f'<p class="status-running">🔴 {state_text}</p>', unsafe_allow_html=True)
        elif st.session_state.current_state == ProcessingState.ERROR:
            st.markdown(f'<p class="status-error">⚠️ {state_text}</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="status-stopped">⚪ {state_text}</p>', unsafe_allow_html=True)
    
    with status_col2:
        transcription_count = len(st.session_state.transcriptions)
        st.metric("処理済みセグメント", transcription_count)
    
    with status_col3:
        if st.session_state.translator:
            stats = st.session_state.translator.get_stats()
            error_count = stats.get('errors', 0)
            st.metric("エラー数", error_count)

def start_translation(url: str, config: Dict[str, Any]):
    """翻訳開始"""
    try:
        # 翻訳器作成
        st.session_state.translator = create_translator(config)
        
        # 言語設定
        st.session_state.translator.configure(
            source_language=config['source_language'],
            target_language=config['target_language'],
            segment_duration=config['segment_duration']
        )
        
        # 翻訳開始
        if st.session_state.translator.start_translation(url):
            st.success("翻訳を開始しました！")
            st.session_state.transcriptions.clear()  # 履歴クリア
        else:
            st.error("翻訳の開始に失敗しました")
            
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

def render_transcriptions():
    """文字起こし結果の表示"""
    if not st.session_state.transcriptions:
        st.info("まだ文字起こし結果はありません。YouTubeライブ配信を開始してください。")
        return
    
    st.subheader("📝 リアルタイム文字起こし")
    
    # 最新の結果を上に表示
    recent_transcriptions = st.session_state.transcriptions[-20:]  # 最新20件
    recent_transcriptions.reverse()
    
    for trans in recent_transcriptions:
        timestamp_str = trans['timestamp'].strftime("%H:%M:%S")
        confidence_str = f"{trans['confidence']:.2f}" if trans['confidence'] else "N/A"
        
        # 原文
        st.markdown(
            f'<div class="transcription-box">'
            f'<strong>🕐 {timestamp_str}</strong> (信頼度: {confidence_str})<br>'
            f'<strong>原文:</strong> {trans["original"]}'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # 翻訳
        if trans['translated']:
            st.markdown(
                f'<div class="translation-box">'
                f'<strong>翻訳:</strong> {trans["translated"]}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("翻訳に失敗しました")
        
        st.markdown("---")

def render_statistics():
    """統計情報の表示"""
    if not st.session_state.translator:
        return
    
    stats = st.session_state.translator.get_stats()
    
    if stats['segments_processed'] == 0:
        st.info("まだ統計データはありません")
        return
    
    st.subheader("📊 統計情報")
    
    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("処理セグメント数", stats['segments_processed'])
    
    with col2:
        avg_time = stats.get('avg_processing_time', 0)
        st.metric("平均処理時間", f"{avg_time:.2f}秒")
    
    with col3:
        cache_hit_rate = stats.get('cache_hit_rate', 0)
        st.metric("キャッシュヒット率", f"{cache_hit_rate:.1%}")
    
    with col4:
        st.metric("エラー数", stats['errors'])
    
    # グラフ表示
    if len(st.session_state.transcriptions) > 1:
        # 時系列グラフ
        df = pd.DataFrame(st.session_state.transcriptions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = px.line(
            df, 
            x='timestamp', 
            y='confidence',
            title='信頼度の推移',
            labels={'timestamp': '時刻', 'confidence': '信頼度'}
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    """メイン関数"""
    initialize_session_state()
    
    # サイドバー設定
    config = render_sidebar()
    
    # メインインターフェース
    render_main_interface(config)
    
    # タブ表示
    tab1, tab2, tab3 = st.tabs(["📝 文字起こし", "📊 統計", "ℹ️ ヘルプ"])
    
    with tab1:
        render_transcriptions()
    
    with tab2:
        render_statistics()
    
    with tab3:
        render_help()
    
    # 自動更新（開発用）
    if st.session_state.is_running:
        time.sleep(2)
        st.rerun()

def render_help():
    """ヘルプ情報の表示"""
    st.subheader("ℹ️ 使用方法")
    
    st.markdown("""
    ### 🚀 セットアップ
    1. **APIキーの設定**: `.env`ファイルにOpenAI APIキーを設定
    2. **依存関係のインストール**: `pip install -r requirements.txt`
    3. **ffmpegのインストール**: 音声処理に必要
    
    ### 📋 使用手順
    1. **設定**: サイドバーでWhisperモデルと翻訳エンジンを選択
    2. **URL入力**: YouTubeライブ配信のURLを入力
    3. **開始**: 「開始」ボタンをクリック
    4. **確認**: リアルタイムで文字起こしと翻訳が表示されます
    
    ### ⚠️ 注意事項
    - ライブ配信のみ対応（録画動画は非対応）
    - API使用量に応じて料金が発生する場合があります
    - 音声品質により認識精度が変わります
    
    ### 🔧 推奨設定
    - **高精度重視**: Whisperモデル「medium」、OpenAI翻訳
    - **高速処理重視**: Whisperモデル「base」、Google翻訳
    - **バランス型**: Whisperモデル「small」、OpenAI翻訳
    """)
    
    st.subheader("🆘 トラブルシューティング")
    
    with st.expander("音声が認識されない"):
        st.write("""
        - ライブ配信が実際に進行中か確認してください
        - 音声セグメント長を短くしてみてください（5-10秒）
        - 配信の音量が十分か確認してください
        """)
    
    with st.expander("翻訳が表示されない"):
        st.write("""
        - APIキーが正しく設定されているか確認してください
        - インターネット接続を確認してください
        - 統計タブでエラー数を確認してください
        """)
    
    with st.expander("処理が遅い"):
        st.write("""
        - Whisperモデルを軽いもの（tiny, base）に変更してください
        - 音声セグメント長を長くしてください（15-20秒）
        - OpenAI Whisper APIの使用を検討してください
        """)

if __name__ == "__main__":
    main()