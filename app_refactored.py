"""
ピックルボール練習試合ダブルス組み合わせ管理システム
リファクタリング版 - モジュール分割された構造
"""

import streamlit as st
from src.data_manager import DataManager
from src.pages import (
    user_management,
    participant_management,
    round_generation,
    match_results,
    statistics
)
from pathlib import Path


def initialize_session_state():
    """セッション状態の初期化"""
    if 'users' not in st.session_state:
        st.session_state.users = []
    if 'current_participants' not in st.session_state:
        st.session_state.current_participants = []
    if 'rounds' not in st.session_state:
        st.session_state.rounds = []
    if 'pair_history' not in st.session_state:
        st.session_state.pair_history = {}
    if 'bye_history' not in st.session_state:
        st.session_state.bye_history = {}
    if 'match_history' not in st.session_state:
        st.session_state.match_history = {}


def main():
    """メインアプリケーション"""
    st.set_page_config(
        page_title="ピックルボール練習試合管理システム",
        page_icon="🏓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # セッション状態初期化
    initialize_session_state()
    
    # データ読み込み
    data_manager = DataManager()
    data_manager.load_data()
    
    # ヘッダー
    st.title("🏓 ピックルボール練習試合管理システム")
    st.markdown("""
        <div style='font-size:18px; font-weight:bold;'>ピックルボール練習試合<br>ダブルス組み合わせ管理</div>
        <div style='font-size:13px; color:gray;'>参加者管理・ペアリング・試合記録を<br>かんたんに！</div>
        """, unsafe_allow_html=True)
    
    # タブ形式のナビゲーション（スマホ対応）
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 ユーザー管理",
        "👥 参加者管理",
        "🎯 ラウンド生成・結果管理",
        "📈 統計・履歴"
    ])
    
    with tab1:
        user_management.render_user_management_page()
    
    with tab2:
        participant_management.render_participant_management_page()
    
    with tab3:
        round_generation.render_round_generation_page()
    
    with tab4:
        statistics.render_statistics_page()
    
    # フッター
    st.markdown("---")
    st.markdown("ピックルボール練習試合管理システム v2.0 (リファクタリング版)")


if __name__ == "__main__":
    main() 