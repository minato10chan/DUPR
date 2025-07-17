"""
参加者管理ページ
参加者の追加、編集、削除を担当
"""

import streamlit as st
from src.ui_components import UIComponents


def render_participant_management_page():
    """参加者管理ページを表示"""
    st.header("👤 参加者管理")
    
    UIComponents.participant_management(
        st.session_state.users,
        st.session_state.current_participants
    ) 