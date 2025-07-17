"""
ユーザー管理ページ
ユーザーの登録、編集、削除を担当
"""

import streamlit as st
from src.data_manager import DataManager
from src.ui_components import UIComponents


def render_user_management_page():
    """ユーザー管理ページを表示"""
    st.header("👥 ユーザー管理")
    
    data_manager = DataManager()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("新規ユーザー登録")
        submitted, name, rating, memo = UIComponents.user_registration_form()
        
        if submitted:
            if not name.strip():
                st.warning("⚠️ 名前は必須です。例：山田太郎")
            elif data_manager.add_user(name, rating, memo):
                st.success(f"✅ {name} を登録しました！")
                st.rerun()
            else:
                st.error("❌ この名前は既に登録されています。他の名前を入力してください。")
    
    with col2:
        st.subheader("ユーザー一覧")
        UIComponents.user_list(
            st.session_state.users,
            on_delete=data_manager.delete_user
        )
    
    # レーティング更新
    if st.button("レーティングを更新", help="全ユーザーのレーティングを最新の戦績で再計算します。"):
        data_manager.update_user_ratings()
        st.success("レーティングを更新しました。")
        st.rerun() 