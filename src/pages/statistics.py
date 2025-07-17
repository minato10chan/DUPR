"""
統計・履歴ページ
統計情報と履歴の表示を担当
"""

import streamlit as st
from src.ui_components import UIComponents


def render_statistics_page():
    """統計・履歴ページを表示"""
    st.header("📈 統計・履歴")
    
    # 基本統計
    UIComponents.statistics_display(
        st.session_state.users,
        st.session_state.pair_history,
        st.session_state.bye_history
    )
    
    # 組み合わせ多様性分析
    st.markdown("---")
    UIComponents.diversity_analysis_display(
        st.session_state.pair_history,
        st.session_state.match_history
    ) 