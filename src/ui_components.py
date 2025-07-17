"""
UIコンポーネントモジュール
再利用可能なUIコンポーネントを定義
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Dict, Optional


class UIComponents:
    """UIコンポーネントクラス"""
    
    @staticmethod
    def user_registration_form() -> tuple:
        """ユーザー登録フォーム（ユーザーフレンドリー版）"""
        st.markdown("""
        <div style='background:#f0f2f6;padding:0.7em 1em 0.7em 1em;border-radius:8px;margin-bottom:1em;'>
        <b>【使い方】</b> 必須項目を入力し、「<span style='color:#fff;background:#FF6B6B;padding:2px 8px;border-radius:4px;'> 195 登録</span>」ボタンを押してください。
        </div>
        """, unsafe_allow_html=True)
        with st.form("user_registration"):
            name = st.text_input("名前 *", placeholder="例：山田太郎")
            rating = st.slider("初期レーティング", 800, 1600, 1200, help="初期値は1200。800〜1600の範囲で設定できます。")
            memo = st.text_area("メモ (任意)", placeholder="例：左利き、初心者 など")
            
            submitted = st.form_submit_button(
                label=" 195 登録",
                help="入力内容でユーザーを登録します。"
            )
            return submitted, name, rating, memo
    
    @staticmethod
    def user_list(users: List[Dict], on_delete=None):
        """ユーザー一覧表示"""
        if not users:
            st.info("登録されたユーザーがいません。")
            return
        
        for i, user in enumerate(users):
            with st.expander(f"{user['name']} (レーティング: {user['rating']})"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**戦績**: {user['wins']}勝 {user['total_matches']}試合")
                    if user['total_matches'] > 0:
                        win_rate = user['wins'] / user['total_matches'] * 100
                        st.write(f"**勝率**: {win_rate:.1f}%")
                    st.write(f"**メモ**: {user.get('memo', '')}")
                
                with col_b:
                    if st.button(f"削除", key=f"delete_{i}"):
                        if on_delete:
                            on_delete(i)
    
    @staticmethod
    def participant_management(users: List[Dict], participants: List[Dict]):
        """参加者管理UI"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("参加者追加")
            
            # 登録ユーザーからの選択
            st.write("**登録ユーザーから追加**")
            if users:
                search = st.text_input("ユーザー検索")
                filtered_users = [user for user in users 
                                if search.lower() in user['name'].lower()]
                
                for user in filtered_users:
                    if st.button(f"➕ {user['name']} (レーティング: {user['rating']})", 
                               key=f"add_user_{user['name']}"):
                        if not any(p['name'] == user['name'] for p in participants):
                            participant = {
                                'name': user['name'],
                                'rating': user['rating'],
                                'active': True,
                                'number': len(participants) + 1,
                                'joined_at': st.session_state.get('current_time', ''),
                                'status': 'active' # active, inactive, left
                            }
                            participants.append(participant)
                            st.success(f"{user['name']}を追加しました。")
                            st.rerun()
                        else:
                            st.error("既に参加者リストにいます。")
            else:
                st.info("登録されたユーザーがいません。")
            
            # ゲスト参加者追加
            st.write("**ゲスト参加者を追加**")
            with st.form("guest_add"):
                guest_name = st.text_input("ゲスト名（省略可）")
                guest_rating = st.slider("レーティング", 800, 1600, 1200, key="guest_rating")
                
                if st.form_submit_button("ゲスト追加"):
                    if not guest_name:
                        guest_name = f"ゲスト{len(participants) + 1}"
                    
                    participant = {
                        'name': guest_name,
                        'rating': guest_rating,
                        'active': True,
                        'number': len(participants) + 1,
                        'joined_at': st.session_state.get('current_time', ''),
                        'status': 'active'
                    }
                    participants.append(participant)
                    st.success(f"{guest_name}を追加しました。")
                    st.rerun()
            
            # 一括追加
            st.write("**一括追加**")
            with st.form("bulk_add"):
                bulk_count = st.number_input("追加人数", min_value=1, max_value=20, value=4)
                if st.form_submit_button("一括追加"):
                    for i in range(bulk_count):
                        guest_name = f"ゲスト{len(participants) + i + 1}"
                        participant = {
                            'name': guest_name,
                            'rating': 1200,
                            'active': True,
                            'number': len(participants) + i + 1,
                            'joined_at': st.session_state.get('current_time', ''),
                            'status': 'active'
                        }
                        participants.append(participant)
                    st.success(f"{bulk_count}人を一括追加しました。")
                    st.rerun()
        
        with col2:
            st.subheader("参加者一覧")
            if participants:
                # 参加者変更履歴の表示
                if 'participant_changes' not in st.session_state:
                    st.session_state.participant_changes = []
                
                # 参加者変更履歴
                if st.session_state.participant_changes:
                    with st.expander("📋 参加者変更履歴"):
                        for change in st.session_state.participant_changes[-5:]:  # 最新5件
                            st.write(f"**{change['timestamp']}**: {change['action']} - {change['participant']}")
                
                for i, participant in enumerate(participants):
                    # ステータスに応じたアイコン
                    if participant.get('status') == 'left':
                        status = "🔴"  # 退場
                        status_text = "退場"
                    elif participant.get('status') == 'inactive':
                        status = "🟡"  # 一時無効
                        status_text = "一時無効"
                    else:
                        status = "🟢"  # アクティブ
                        status_text = "アクティブ"
                    
                    col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                    
                    with col_a:
                        st.write(f"{status} **{participant['number']}.** {participant['name']} (レーティング: {participant['rating']})")
                        if participant.get('joined_at'):
                            st.caption(f"参加: {participant['joined_at']}")
                    
                    with col_b:
                        if st.button("編集", key=f"edit_{i}"):
                            st.session_state.editing = i
                    
                    with col_c:
                        # ステータス変更ボタン
                        if participant.get('status') == 'active':
                            if st.button("一時無効", key=f"inactive_{i}"):
                                participant['status'] = 'inactive'
                                st.session_state.participant_changes.append({
                                    'timestamp': st.session_state.get('current_time', ''),
                                    'action': '一時無効化',
                                    'participant': participant['name']
                                })
                                st.rerun()
                        elif participant.get('status') == 'inactive':
                            if st.button("復活", key=f"reactivate_{i}"):
                                participant['status'] = 'active'
                                st.session_state.participant_changes.append({
                                    'timestamp': st.session_state.get('current_time', ''),
                                    'action': '復活',
                                    'participant': participant['name']
                                })
                                st.rerun()
                        elif participant.get('status') == 'left':
                            st.write("退場済み")
                    
                    with col_d:
                        if st.button("退場", key=f"leave_{i}"):
                            participant['status'] = 'left'
                            st.session_state.participant_changes.append({
                                'timestamp': st.session_state.get('current_time', ''),
                                'action': '退場',
                                'participant': participant['name']
                            })
                            st.rerun()
                    
                    # 編集モード
                    if hasattr(st.session_state, 'editing') and st.session_state.editing == i:
                        with st.form(f"edit_form_{i}"):
                            new_name = st.text_input("名前", value=participant['name'], key=f"name_{i}")
                            new_rating = st.slider("レーティング", 800, 1600, participant['rating'], key=f"rating_{i}")
                            new_active = st.checkbox("アクティブ", value=participant['active'], key=f"active_{i}")
                            
                            if st.form_submit_button("更新"):
                                participant['name'] = new_name
                                participant['rating'] = new_rating
                                participant['active'] = new_active
                                if participant['active']:
                                    participant['status'] = 'active'
                                del st.session_state.editing
                                st.rerun()
            else:
                st.info("参加者がいません。")
        
        # 参加者変更時のラウンド再生成
        if st.session_state.rounds and st.session_state.participant_changes:
            st.markdown("---")
            st.subheader("🔄 参加者変更対応")
            
            active_count = sum(1 for p in participants if p.get('status') == 'active')
            st.write(f"**現在のアクティブ参加者**: {active_count}人")
            
            if st.button("🔄 参加者変更に基づいてラウンドを再生成", type="primary"):
                # ラウンド再生成ロジックを呼び出し
                st.session_state.regenerate_rounds = True
                st.rerun()
    
    @staticmethod
    def round_generation_form() -> tuple:
        """ラウンド生成フォーム"""
        with st.form("round_generation"):
            round_count = st.number_input("生成ラウンド数", min_value=1, max_value=10, value=1)
            court_count = st.number_input("コート数", min_value=1, max_value=10, value=2)
            consider_level = st.checkbox("レベル考慮モード", value=False)
            
            submitted = st.form_submit_button("ラウンド生成")
            return submitted, round_count, court_count, consider_level
    
    @staticmethod
    def match_table_display(rounds: List[Dict]):
        """試合テーブル表示"""
        if not rounds:
            st.info("ラウンドが生成されていません。")
            return
        
        # テーブルデータ作成
        table_data = []
        max_courts = max(len(round_data['matches']) for round_data in rounds)
        
        for court in range(1, max_courts + 1):
            row = [f"コート{court}"]
            for round_data in rounds:
                if court <= len(round_data['matches']):
                    match = round_data['matches'][court - 1]
                    team1_str = f"{match['team1'][0]}&{match['team1'][1]}"
                    team2_str = f"{match['team2'][0]}&{match['team2'][1]}"
                    score_str = f"{match['score1']}-{match['score2']}"
                    
                    if match['winner'] == 'team1':
                        display_str = f"🏆{team1_str} vs {team2_str}\n{score_str}"
                    elif match['winner'] == 'team2':
                        display_str = f"{team1_str} vs 🏆{team2_str}\n{score_str}"
                    else:
                        display_str = f"{team1_str} vs {team2_str}\n{score_str}"
                    
                    row.append(display_str)
                else:
                    row.append("")
            table_data.append(row)
        
        # ヘッダー行
        header = ["コート"] + [f"ラウンド{r['round']}" for r in rounds]
        table_data.insert(0, header)
        
        # テーブル表示
        df = pd.DataFrame(table_data[1:], columns=table_data[0])
        st.dataframe(df, use_container_width=True)
    
    @staticmethod
    def statistics_display(users: List[Dict], pair_history: Dict, bye_history: Dict):
        """統計表示"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ユーザー統計")
            if users:
                stats_data = []
                for user in users:
                    win_rate = user['wins'] / user['total_matches'] * 100 if user['total_matches'] > 0 else 0
                    stats_data.append({
                        '名前': user['name'],
                        'レーティング': user['rating'],
                        '勝利数': user['wins'],
                        '総試合数': user['total_matches'],
                        '勝率': f"{win_rate:.1f}%"
                    })
                
                df_stats = pd.DataFrame(stats_data)
                st.dataframe(df_stats, use_container_width=True)
                
                # レーティング分布
                ratings = [user['rating'] for user in users]
                if ratings:
                    fig = px.histogram(x=ratings, nbins=10, title="レーティング分布")
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("ペア履歴")
            if pair_history:
                pair_data = []
                for pair_key, count in pair_history.items():
                    players = pair_key.split('_')
                    pair_data.append({
                        'ペア': f"{players[0]} & {players[1]}",
                        '回数': count
                    })
                
                pair_df = pd.DataFrame(pair_data)
                pair_df = pair_df.sort_values('回数', ascending=False)
                st.dataframe(pair_df, use_container_width=True)
                
                # ペア履歴の統計
                if pair_data:
                    avg_pairs = sum(d['回数'] for d in pair_data) / len(pair_data)
                    max_pairs = max(d['回数'] for d in pair_data)
                    min_pairs = min(d['回数'] for d in pair_data)
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("平均ペア回数", f"{avg_pairs:.1f}")
                    with col_b:
                        st.metric("最多ペア回数", max_pairs)
                    with col_c:
                        st.metric("最少ペア回数", min_pairs)
            
            st.subheader("バイ履歴")
            if bye_history:
                bye_data = []
                for player, count in bye_history.items():
                    bye_data.append({
                        'プレイヤー': player,
                        'バイ回数': count
                    })
                
                bye_df = pd.DataFrame(bye_data)
                bye_df = bye_df.sort_values('バイ回数', ascending=False)
                st.dataframe(bye_df, use_container_width=True)
    
    @staticmethod
    def diversity_analysis_display(pair_history: Dict, match_history: Dict):
        st.subheader("🎯 組み合わせ多様性分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ペア組み合わせの公平性")
            if pair_history:
                # ペア回数の分布
                pair_counts = list(pair_history.values())
                if pair_counts:
                    avg_pairs = sum(pair_counts) / len(pair_counts)
                    variance = sum((x - avg_pairs) ** 2 for x in pair_counts) / len(pair_counts)
                    std_dev = variance ** 0.5
                    
                    st.metric("平均ペア回数", f"{avg_pairs:.1f}")
                    st.metric("標準偏差", f"{std_dev:.1f}")
                    
                    # 公平性スコア（標準偏差が小さいほど公平）
                    fairness_score = max(0,10- (std_dev * 10))
                    st.metric("公平性スコア", f"{fairness_score:.0f}%")
                    
                    # ペア回数分布のヒストグラム
                    fig = px.histogram(x=pair_counts, nbins=5, 
                                     title="ペア回数分布",
                                     labels={'x': 'ペア回数', 'y': 'ペア数'})
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 対戦組み合わせの多様性")
            if match_history:
                # 対戦回数の分布
                match_counts = list(match_history.values())
                if match_counts:
                    avg_matches = sum(match_counts) / len(match_counts)
                    variance = sum((x - avg_matches) ** 2 for x in match_counts) / len(match_counts)
                    std_dev = variance ** 0.5
                    
                    st.metric("平均対戦回数", f"{avg_matches:.1f}")
                    st.metric("標準偏差", f"{std_dev:.1f}")
                    
                    # 多様性スコア
                    diversity_score = max(0,10- (std_dev * 10))
                    st.metric("多様性スコア", f"{diversity_score:.0f}%")
                    
                    # 対戦回数分布のヒストグラム
                    fig = px.histogram(x=match_counts, nbins=5,
                                     title="対戦回数分布",
                                     labels={'x': '対戦回数', 'y': '対戦数'})
                    st.plotly_chart(fig, use_container_width=True)
        
        # 組み合わせ改善提案
        st.markdown("### 💡 組み合わせ改善提案")
        if pair_history and match_history:
            # 最もペア回数が多い組み合わせ
            max_pair_key = max(pair_history.keys(), key=lambda k: pair_history[k])
            max_pair_count = pair_history[max_pair_key]
            max_pair_players = max_pair_key.split('_')
            # 最も対戦回数が多い組み合わせ
            max_match_key = max(match_history.keys(), key=lambda k: match_history[k])
            max_match_count = match_history[max_match_key]
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"**最もペア回数が多い**: {max_pair_players[0]} & {max_pair_players[1]} ({max_pair_count}回)")
            with col_b:
                st.info(f"**最も対戦回数が多い**: {max_match_count}回")
            
            # 改善提案
            if max_pair_count > 3:
                st.warning("⚠️ 一部のペアが頻繁に組まれています。次回のラウンド生成で多様性を重視します。")
            elif max_pair_count <= 2:
                st.success("✅ ペア組み合わせは良好な多様性を保っています。") 