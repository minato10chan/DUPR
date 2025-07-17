"""
ラウンド生成ページ
ラウンドの生成と管理を担当
"""

import streamlit as st
from src.match_manager import MatchManager
from src.ui_components import UIComponents


def render_round_generation_page():
    """ラウンド生成ページを表示"""
    st.header("🎯 ラウンド生成")
    
    if not st.session_state.current_participants:
        st.error("参加者がいません。参加者管理で参加者を追加してください。")
        return
    
    match_manager = MatchManager()
    
    # 参加者変更時のラウンド再生成処理
    if st.session_state.get('regenerate_rounds', False):
        if match_manager.regenerate_rounds_for_participant_changes(court_count=2, consider_level=False):
            st.success("参加者変更に基づいてラウンドを再生成しました。")
        else:
            st.error("ラウンドの再生成に失敗しました。")
        st.session_state.regenerate_rounds = False
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ラウンド生成設定")
        submitted, round_count, court_count, consider_level = UIComponents.round_generation_form()
        
        if submitted:
            if match_manager.generate_rounds(round_count, court_count, consider_level):
                st.success(f"{round_count}ラウンドを生成しました。")
                st.rerun()
            else:
                st.error("ラウンドの生成に失敗しました。")
    
    with col2:
        st.subheader("現在の参加者状況")
        
        # 参加者ステータス概要
        status_summary = match_manager.get_participant_status_summary()
        active_count = match_manager.get_active_participants_count()
        
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("総参加者", status_summary['total'])
        with col_b:
            st.metric("アクティブ", status_summary['active'], delta=active_count)
        with col_c:
            st.metric("一時無効", status_summary['inactive'])
        with col_d:
            st.metric("退場", status_summary['left'])
        
        # 組み合わせ多様性の状況
        if st.session_state.pair_history:
            st.markdown("### 🎯 組み合わせ多様性状況")
            
            # ペア履歴の統計
            pair_counts = list(st.session_state.pair_history.values())
            if pair_counts:
                avg_pairs = sum(pair_counts) / len(pair_counts)
                max_pairs = max(pair_counts)
                min_pairs = min(pair_counts)
                
                col_x, col_y, col_z = st.columns(3)
                with col_x:
                    st.metric("平均ペア回数", f"{avg_pairs:.1f}")
                with col_y:
                    st.metric("最多ペア回数", max_pairs)
                with col_z:
                    st.metric("最少ペア回数", min_pairs)
                
                # 多様性の評価
                if max_pairs - min_pairs <= 1:
                    st.success("✅ ペア組み合わせは良好な多様性を保っています")
                elif max_pairs - min_pairs <= 2:
                    st.info("ℹ️ ペア組み合わせは適度な多様性を保っています")
                else:
                    st.warning("⚠️ ペア組み合わせの多様性に改善の余地があります")
        
        # 参加者変更履歴の表示
        if hasattr(st.session_state, 'participant_changes') and st.session_state.participant_changes:
            with st.expander("📋 最近の参加者変更履歴"):
                for change in st.session_state.participant_changes[-3:]:  # 最新3件
                    st.write(f"**{change['timestamp']}**: {change['action']} - {change['participant']}")
        
        st.write("**アクティブ参加者一覧**:")
        for participant in st.session_state.current_participants:
            if participant.get('status') == 'active' and participant.get('active', True):
                st.write(f"• {participant['name']} (レーティング: {participant['rating']})")
            elif participant.get('status') == 'inactive':
                st.write(f"• ⏸️ {participant['name']} (一時無効)")
            elif participant.get('status') == 'left':
                st.write(f"• 🔴 {participant['name']} (退場)")
    
    # ラウンド一覧（改善版）
    if st.session_state.rounds:
        st.subheader("生成されたラウンド")
        
        # 全ラウンド一覧テーブル（結果ページから統合）
        st.markdown("### 📊 全ラウンド一覧")
        
        # バイプレイヤー情報を追加（ステータスを考慮）
        active_participants = [p for p in st.session_state.current_participants if p.get('status') == 'active' and p.get('active', True)]
        active_names = set()
        for round_data in st.session_state.rounds:
            for match in round_data['matches']:
                active_names.update(match['team1'])
                active_names.update(match['team2'])
        
        bye_players = [p['name'] for p in active_participants if p['name'] not in active_names]
        if bye_players:
            st.warning(f"⚠️ バイプレイヤー: {', '.join(bye_players)}")
        
        # 一時無効・退場プレイヤーの表示
        inactive_players = [p['name'] for p in st.session_state.current_participants if p.get('status') == 'inactive']
        left_players = [p['name'] for p in st.session_state.current_participants if p.get('status') == 'left']
        if inactive_players:
            st.info(f"⏸️ 一時無効プレイヤー: {', '.join(inactive_players)}")
        if left_players:
            st.error(f"🔴 退場プレイヤー: {', '.join(left_players)}")
        
        # テーブル表示を改善
        if st.session_state.rounds:
            # テーブルデータ作成
            table_data = []
            max_courts = max(len(round_data['matches']) for round_data in st.session_state.rounds)
            
            for court in range(1, max_courts + 1):
                row = [f"コート{court}"]
                for round_data in st.session_state.rounds:
                    if court <= len(round_data['matches']):
                        match = round_data['matches'][court - 1]
                        team1_str = f"{match['team1'][0]} & {match['team1'][1]}"
                        team2_str = f"{match['team2'][0]} & {match['team2'][1]}"
                        score_str = f"{match['score1']} - {match['score2']}"
                        
                        if match['winner'] == 'team1':
                            display_str = f"🏆 **{team1_str}** vs {team2_str}<br><small>{score_str}</small>"
                        elif match['winner'] == 'team2':
                            display_str = f"{team1_str} vs 🏆 **{team2_str}**<br><small>{score_str}</small>"
                        else:
                            display_str = f"{team1_str} vs {team2_str}<br><small>{score_str}</small>"
                        
                        row.append(display_str)
                    else:
                        row.append(" ")
                table_data.append(row)
            
            # ヘッダー行
            header = ["コート"] + [f"ラウンド{r['round']}" for r in st.session_state.rounds]
            table_data.insert(0, header)
            
            # テーブル表示（HTMLでスタイリング）
            html_table = "<table style='width:100%; border-collapse:collapse; margin:10px 0;'>"
            for i, row in enumerate(table_data):
                html_table += "<tr>"
                for j, cell in enumerate(row):
                    if i == 0:  # ヘッダー行
                        html_table += f"<th style='border:1px solid #ddd; padding:8px; background-color:#f8f9fa; text-align:center;'>{cell}</th>"
                    else:
                        html_table += f"<td style='border:1px solid #ddd; padding:8px; text-align:center;'>{cell}</td>"
                html_table += "</tr>"
            html_table += "</table>"
            
            st.markdown(html_table, unsafe_allow_html=True)
        
        # ラウンド概要
        summary = match_manager.get_round_summary()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("総ラウンド数", summary['total_rounds'])
        with col2:
            st.metric("完了ラウンド数", summary['completed_rounds'])
        with col3:
            st.metric("総試合数", summary['total_matches'])
        with col4:
            st.metric("完了試合数", summary['completed_matches'])
        
        st.markdown("---")
        st.markdown("### 🎯 ラウンド詳細")
        
        # 各ラウンドの詳細表示
        for i, round_data in enumerate(st.session_state.rounds):
            round_status = "✅ 完了" if round_data['completed'] else "⏳ 進行中"
            
            with st.expander(f"ラウンド {round_data['round']} - {round_status}", expanded=True):
                # ラウンド操作ボタン
                col_a, col_b, col_c = st.columns([1, 1, 2])
                
                with col_a:
                    if not round_data['completed']:
                        if st.button("✅ 完了にする", key=f"complete_{i}", type="primary"):
                            match_manager.complete_round(i)
                            st.rerun()
                
                with col_b:
                    if st.button("🗑️ 削除", key=f"delete_round_{i}"):
                        match_manager.delete_round(i)
                        st.rerun()
                
                with col_c:
                    st.markdown(f"<small>作成日時: {round_data['created_at'][:19]}</small>", unsafe_allow_html=True)
                
                # このラウンドのバイプレイヤーを表示
                round_active_names = set()
                for match in round_data['matches']:
                    round_active_names.update(match['team1'])
                    round_active_names.update(match['team2'])
                
                round_bye_players = [p['name'] for p in active_participants if p['name'] not in round_active_names]
                if round_bye_players:
                    st.info(f"🔄 このラウンドのバイプレイヤー: {', '.join(round_bye_players)}")
                
                # 試合一覧
                st.markdown("### 試合一覧")
                
                for j, match in enumerate(round_data['matches']):
                    # 試合カード
                    match_card_style = """
                    <div style='border:1px solid #ddd; border-radius:8px; padding:15px; margin:10px 0; 
                    background-color: #f8f9fa;'>
                    """
                    
                    team1_str = f"{match['team1'][0]} & {match['team1'][1]}"
                    team2_str = f"{match['team2'][0]} & {match['team2'][1]}"
                    score_str = f"{match['score1']} - {match['score2']}"
                    
                    # 勝敗表示
                    if match['winner'] == 'team1':
                        winner_display = f"🏆 **{team1_str}** vs {team2_str}"
                    elif match['winner'] == 'team2':
                        winner_display = f"{team1_str} vs 🏆 **{team2_str}**"
                    else:
                        winner_display = f"{team1_str} vs {team2_str}"
                    
                    match_card_style += f"""
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <strong>コート{match['court']}</strong><br>
                            {winner_display}<br>
                            <small>スコア: {score_str}</small>
                        </div>
                    """
                    
                    # スコア入力（未完了ラウンドの場合）
                    if not round_data['completed']:
                        # スコア入力フォーム
                        with st.container():
                            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                            
                            with col1:
                                score1 = st.number_input("スコア1", min_value=0, value=match['score1'], 
                                                       key=f"score1_{i}_{j}", label_visibility="collapsed")
                            
                            with col2:
                                score2 = st.number_input("スコア2", min_value=0, value=match['score2'], 
                                                       key=f"score2_{i}_{j}", label_visibility="collapsed")
                            
                            with col3:
                                if st.button("記録", key=f"record_{i}_{j}", type="secondary"):
                                    match_manager.record_match_result(i, j, score1, score2)
                                    st.rerun()
                            
                            with col4:
                                st.markdown(f"<small>対戦回数: {match['match_count']}</small>", unsafe_allow_html=True)
                    
                    match_card_style += """
                    </div>
                    </div>
                    """
                    
                    st.markdown(match_card_style, unsafe_allow_html=True) 