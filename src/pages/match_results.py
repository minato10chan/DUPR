"""
試合結果ページ
試合結果の記録と表示を担当
"""

import streamlit as st
from src.match_manager import MatchManager
from src.ui_components import UIComponents


def render_match_results_page():
    """試合結果ページを表示"""
    st.header("📊 試合結果")
    
    if not st.session_state.rounds:
        st.info("ラウンドが生成されていません。")
        return
    
    match_manager = MatchManager()
    
    # テーブル表示
    st.subheader("全ラウンド一覧")
    UIComponents.match_table_display(st.session_state.rounds)
    
    # 詳細表示
    st.subheader("詳細表示")
    for i, round_data in enumerate(st.session_state.rounds):
        with st.expander(f"ラウンド {round_data['round']} 詳細"):
            for j, match in enumerate(round_data['matches']):
                st.write(f"**コート{match['court']}**")
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**チーム1**: {match['team1'][0]} & {match['team1'][1]}")
                
                with col2:
                    st.write(f"**チーム2**: {match['team2'][0]} & {match['team2'][1]}")
                
                with col3:
                    if not round_data['completed']:
                        with st.form(f"score_form_{i}_{j}"):
                            score1 = st.number_input("スコア1", min_value=0, value=match['score1'], key=f"score1_{i}_{j}")
                            score2 = st.number_input("スコア2", min_value=0, value=match['score2'], key=f"score2_{i}_{j}")
                            
                            if st.form_submit_button("記録"):
                                match_manager.record_match_result(i, j, score1, score2)
                                st.rerun()
                    else:
                        st.write(f"**スコア**: {match['score1']} - {match['score2']}")
    
    # ラウンド概要
    summary = match_manager.get_round_summary()
    st.subheader("ラウンド概要")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総ラウンド数", summary['total_rounds'])
    
    with col2:
        st.metric("完了ラウンド数", summary['completed_rounds'])
    
    with col3:
        st.metric("総試合数", summary['total_matches'])
    
    with col4:
        st.metric("完了試合数", summary['completed_matches']) 