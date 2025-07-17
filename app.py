import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import plotly.express as px
from typing import List, Dict, Tuple, Optional
import random

# ページ設定
st.set_page_config(
    page_title="ピックルボール練習試合管理システム",
    page_icon="🏓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
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

def load_data():
    """データの読み込み"""
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            st.session_state.users = json.load(f)
    except FileNotFoundError:
        st.session_state.users = []
    
    try:
        with open('pair_history.json', 'r', encoding='utf-8') as f:
            st.session_state.pair_history = json.load(f)
    except FileNotFoundError:
        st.session_state.pair_history = {}
    
    try:
        with open('bye_history.json', 'r', encoding='utf-8') as f:
            st.session_state.bye_history = json.load(f)
    except FileNotFoundError:
        st.session_state.bye_history = {}
    
    try:
        with open('match_history.json', 'r', encoding='utf-8') as f:
            st.session_state.match_history = json.load(f)
    except FileNotFoundError:
        st.session_state.match_history = {}

def save_data():
    """データの保存"""
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.users, f, ensure_ascii=False, indent=2)
    
    with open('pair_history.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.pair_history, f, ensure_ascii=False, indent=2)
    
    with open('bye_history.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.bye_history, f, ensure_ascii=False, indent=2)
    
    with open('match_history.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.match_history, f, ensure_ascii=False, indent=2)

def calculate_rating(wins: int, total_matches: int) -> int:
    """レーティング計算"""
    if total_matches == 0:
        return 1200
    win_rate = wins / total_matches
    rating = 1200 + (win_rate - 0.5) * 800
    return max(800, min(1600, int(rating)))

def update_ratings():
    """全ユーザーのレーティングを更新"""
    for user in st.session_state.users:
        user['rating'] = calculate_rating(user['wins'], user['total_matches'])
    save_data()

def get_pair_key(player1: str, player2: str) -> str:
    """ペアのキーを生成"""
    return f"{min(player1, player2)}_{max(player1, player2)}"

def get_match_key(player1: str, player2: str, player3: str, player4: str) -> str:
    """対戦のキーを生成"""
    team1 = f"{min(player1, player2)}_{max(player1, player2)}"
    team2 = f"{min(player3, player4)}_{max(player3, player4)}"
    return f"{min(team1, team2)}_{max(team1, team2)}"

def create_pairs(participants: List[Dict], consider_level: bool = False) -> List[Tuple[str, str]]:
    """ペア作成"""
    if len(participants) < 4:
        return []
    
    active_participants = [p for p in participants if p['active']]
    if len(active_participants) < 4:
        return []
    
    # レベル考慮モードの場合
    if consider_level:
        # レーティングでグループ化
        groups = {}
        for p in active_participants:
            rating = p.get('rating', 1200)
            group_key = (rating // 200) * 200
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(p)
        
        pairs = []
        for group in groups.values():
            if len(group) >= 4:
                # グループ内でペア作成
                group_pairs = create_pairs_for_group(group)
                pairs.extend(group_pairs)
        
        return pairs
    
    # 通常モード
    return create_pairs_for_group(active_participants)

def create_pairs_for_group(participants: List[Dict]) -> List[Tuple[str, str]]:
    """グループ内でのペア作成"""
    if len(participants) < 4:
        return []
    
    # バイ履歴を考慮してペア作成
    participants_with_bye = []
    participants_without_bye = []
    
    for p in participants:
        bye_count = st.session_state.bye_history.get(p['name'], 0)
        if bye_count > 0:
            participants_with_bye.append((p, bye_count))
        else:
            participants_without_bye.append(p)
    
    # バイ履歴が多い順にソート
    participants_with_bye.sort(key=lambda x: x[1], reverse=True)
    
    # ペア作成
    pairs = []
    used = set()
    
    # まずバイ履歴がある人を優先
    for p, _ in participants_with_bye:
        if p['name'] in used:
            continue
        
        # 最もペア回数が少ない人とペアを作成
        best_partner = None
        min_pair_count = float('inf')
        
        for other in participants:
            if other['name'] == p['name'] or other['name'] in used:
                continue
            
            pair_key = get_pair_key(p['name'], other['name'])
            pair_count = st.session_state.pair_history.get(pair_key, 0)
            
            if pair_count < min_pair_count:
                min_pair_count = pair_count
                best_partner = other
        
        if best_partner:
            pairs.append((p['name'], best_partner['name']))
            used.add(p['name'])
            used.add(best_partner['name'])
    
    # 残りの人でペア作成
    remaining = [p for p in participants if p['name'] not in used]
    while len(remaining) >= 2:
        p1 = remaining.pop(0)
        p2 = remaining.pop(0)
        pairs.append((p1['name'], p2['name']))
    
    return pairs

def create_matches(pairs: List[Tuple[str, str]], court_count: int) -> List[Dict]:
    """対戦カード作成"""
    if len(pairs) < 2:
        return []
    
    matches = []
    used_pairs = set()
    
    for i in range(0, len(pairs), 2):
        if i + 1 < len(pairs):
            team1 = pairs[i]
            team2 = pairs[i + 1]
            
            # 対戦履歴をチェック
            match_key = get_match_key(team1[0], team1[1], team2[0], team2[1])
            match_count = st.session_state.match_history.get(match_key, 0)
            
            matches.append({
                'team1': team1,
                'team2': team2,
                'score1': 0,
                'score2': 0,
                'winner': None,
                'court': (len(matches) % court_count) + 1,
                'match_count': match_count
            })
    
    return matches

def generate_rounds(round_count: int, court_count: int, consider_level: bool = False):
    """ラウンド生成"""
    if not st.session_state.current_participants:
        st.error("参加者がいません。")
        return
    
    for round_num in range(1, round_count + 1):
        pairs = create_pairs(st.session_state.current_participants, consider_level)
        matches = create_matches(pairs, court_count)
        
        if matches:
            round_data = {
                'round': round_num,
                'matches': matches,
                'completed': False,
                'created_at': datetime.now().isoformat()
            }
            st.session_state.rounds.append(round_data)
            
            # ペア履歴を更新
            for match in matches:
                pair_key1 = get_pair_key(match['team1'][0], match['team1'][1])
                pair_key2 = get_pair_key(match['team2'][0], match['team2'][1])
                
                st.session_state.pair_history[pair_key1] = st.session_state.pair_history.get(pair_key1, 0) + 1
                st.session_state.pair_history[pair_key2] = st.session_state.pair_history.get(pair_key2, 0) + 1
                
                # 対戦履歴を更新
                match_key = get_match_key(match['team1'][0], match['team1'][1], match['team2'][0], match['team2'][1])
                st.session_state.match_history[match_key] = st.session_state.match_history.get(match_key, 0) + 1
            
            # バイプレイヤーを記録
            active_names = set()
            for match in matches:
                active_names.update(match['team1'])
                active_names.update(match['team2'])
            
            for participant in st.session_state.current_participants:
                if participant['active'] and participant['name'] not in active_names:
                    st.session_state.bye_history[participant['name']] = st.session_state.bye_history.get(participant['name'], 0) + 1
    
    save_data()
    st.success(f"{round_count}ラウンドを生成しました。")

def record_match_result(round_idx: int, match_idx: int, score1: int, score2: int):
    """試合結果記録"""
    if round_idx < len(st.session_state.rounds):
        match = st.session_state.rounds[round_idx]['matches'][match_idx]
        match['score1'] = score1
        match['score2'] = score2
        
        # 勝敗判定
        if score1 > score2:
            match['winner'] = 'team1'
        elif score2 > score1:
            match['winner'] = 'team2'
        else:
            match['winner'] = 'draw'
        
        # ユーザーの戦績を更新
        team1_players = [match['team1'][0], match['team1'][1]]
        team2_players = [match['team2'][0], match['team2'][1]]
        
        if match['winner'] == 'team1':
            for player_name in team1_players:
                for user in st.session_state.users:
                    if user['name'] == player_name:
                        user['wins'] += 1
                        user['total_matches'] += 1
                        break
            for player_name in team2_players:
                for user in st.session_state.users:
                    if user['name'] == player_name:
                        user['total_matches'] += 1
                        break
        elif match['winner'] == 'team2':
            for player_name in team2_players:
                for user in st.session_state.users:
                    if user['name'] == player_name:
                        user['wins'] += 1
                        user['total_matches'] += 1
                        break
            for player_name in team1_players:
                for user in st.session_state.users:
                    if user['name'] == player_name:
                        user['total_matches'] += 1
                        break
        
        save_data()

# データ読み込み
load_data()

# メインアプリケーション
st.title("🏓 ピックルボール練習試合管理システム")

# サイドバー
st.sidebar.title("メニュー")
page = st.sidebar.selectbox(
    "ページ選択",
    ["ユーザー管理", "参加者管理", "ラウンド生成", "試合結果", "統計・履歴"]
)

if page == "ユーザー管理":
    st.header("👥 ユーザー管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("新規ユーザー登録")
        with st.form("user_registration"):
            name = st.text_input("名前")
            rating = st.slider("初期レーティング", 800, 1600, 1200)
            memo = st.text_area("メモ")
            
            if st.form_submit_button("登録"):
                if name:
                    # 重複チェック
                    if any(user['name'] == name for user in st.session_state.users):
                        st.error("この名前は既に登録されています。")
                    else:
                        new_user = {
                            'name': name,
                            'rating': rating,
                            'memo': memo,
                            'wins': 0,
                            'total_matches': 0,
                            'created_at': datetime.now().isoformat()
                        }
                        st.session_state.users.append(new_user)
                        save_data()
                        st.success(f"{name}を登録しました。")
                else:
                    st.error("名前を入力してください。")
    
    with col2:
        st.subheader("ユーザー一覧")
        if st.session_state.users:
            for i, user in enumerate(st.session_state.users):
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
                            st.session_state.users.pop(i)
                            save_data()
                            st.rerun()
        else:
            st.info("登録されたユーザーがいません。")
    
    # レーティング更新
    if st.button("レーティングを更新"):
        update_ratings()
        st.success("レーティングを更新しました。")

elif page == "参加者管理":
    st.header("👤 参加者管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("参加者追加")
        
        # 登録ユーザーからの選択
        st.write("**登録ユーザーから追加**")
        if st.session_state.users:
            search = st.text_input("ユーザー検索")
            filtered_users = [user for user in st.session_state.users 
                            if search.lower() in user['name'].lower()]
            
            for user in filtered_users:
                if st.button(f"➕ {user['name']} (レーティング: {user['rating']})", 
                           key=f"add_user_{user['name']}"):
                    if not any(p['name'] == user['name'] for p in st.session_state.current_participants):
                        participant = {
                            'name': user['name'],
                            'rating': user['rating'],
                            'active': True,
                            'number': len(st.session_state.current_participants) + 1
                        }
                        st.session_state.current_participants.append(participant)
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
                    guest_name = f"ゲスト{len(st.session_state.current_participants) + 1}"
                
                participant = {
                    'name': guest_name,
                    'rating': guest_rating,
                    'active': True,
                    'number': len(st.session_state.current_participants) + 1
                }
                st.session_state.current_participants.append(participant)
                st.success(f"{guest_name}を追加しました。")
                st.rerun()
        
        # 一括追加
        st.write("**一括追加**")
        with st.form("bulk_add"):
            bulk_count = st.number_input("追加人数", min_value=1, max_value=20, value=4)
            if st.form_submit_button("一括追加"):
                for i in range(bulk_count):
                    guest_name = f"ゲスト{len(st.session_state.current_participants) + i + 1}"
                    participant = {
                        'name': guest_name,
                        'rating': 1200,
                        'active': True,
                        'number': len(st.session_state.current_participants) + i + 1
                    }
                    st.session_state.current_participants.append(participant)
                st.success(f"{bulk_count}人を一括追加しました。")
                st.rerun()
    
    with col2:
        st.subheader("参加者一覧")
        if st.session_state.current_participants:
            for i, participant in enumerate(st.session_state.current_participants):
                status = "🟢" if participant['active'] else "🔴"
                col_a, col_b, col_c = st.columns([3, 1, 1])
                
                with col_a:
                    st.write(f"{status} **{participant['number']}.** {participant['name']} (レーティング: {participant['rating']})")
                
                with col_b:
                    if st.button("編集", key=f"edit_{i}"):
                        st.session_state.editing = i
                
                with col_c:
                    if st.button("削除", key=f"delete_participant_{i}"):
                        st.session_state.current_participants.pop(i)
                        # 番号を再割り当て
                        for j, p in enumerate(st.session_state.current_participants):
                            p['number'] = j + 1
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
                            del st.session_state.editing
                            st.rerun()
        else:
            st.info("参加者がいません。")

elif page == "ラウンド生成":
    st.header("🎯 ラウンド生成")
    
    if not st.session_state.current_participants:
        st.error("参加者がいません。参加者管理で参加者を追加してください。")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ラウンド生成設定")
            with st.form("round_generation"):
                round_count = st.number_input("生成ラウンド数", min_value=1, max_value=10, value=1)
                court_count = st.number_input("コート数", min_value=1, max_value=10, value=2)
                consider_level = st.checkbox("レベル考慮モード", value=False)
                
                if st.form_submit_button("ラウンド生成"):
                    generate_rounds(round_count, court_count, consider_level)
                    st.rerun()
        
        with col2:
            st.subheader("現在の参加者")
            active_count = sum(1 for p in st.session_state.current_participants if p['active'])
            st.write(f"**アクティブ参加者**: {active_count}人")
            
            for participant in st.session_state.current_participants:
                if participant['active']:
                    st.write(f"• {participant['name']} (レーティング: {participant['rating']})")
        
        # ラウンド一覧
        if st.session_state.rounds:
            st.subheader("生成されたラウンド")
            for i, round_data in enumerate(st.session_state.rounds):
                with st.expander(f"ラウンド {round_data['round']} {'✅' if round_data['completed'] else '⏳'}"):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        for j, match in enumerate(round_data['matches']):
                            team1_str = f"{match['team1'][0]} & {match['team1'][1]}"
                            team2_str = f"{match['team2'][0]} & {match['team2'][1]}"
                            score_str = f"{match['score1']} - {match['score2']}"
                            
                            if match['winner'] == 'team1':
                                st.write(f"**コート{match['court']}**: 🏆 **{team1_str}** vs {team2_str} ({score_str})")
                            elif match['winner'] == 'team2':
                                st.write(f"**コート{match['court']}**: {team1_str} vs 🏆 **{team2_str}** ({score_str})")
                            else:
                                st.write(f"**コート{match['court']}**: {team1_str} vs {team2_str} ({score_str})")
                    
                    with col_b:
                        if not round_data['completed']:
                            if st.button("完了", key=f"complete_{i}"):
                                round_data['completed'] = True
                                save_data()
                                st.rerun()
                        
                        if st.button("削除", key=f"delete_round_{i}"):
                            st.session_state.rounds.pop(i)
                            save_data()
                            st.rerun()

elif page == "試合結果":
    st.header("📊 試合結果")
    
    if not st.session_state.rounds:
        st.info("ラウンドが生成されていません。")
    else:
        # テーブル表示
        st.subheader("全ラウンド一覧")
        
        # テーブルデータ作成
        table_data = []
        max_courts = max(len(round_data['matches']) for round_data in st.session_state.rounds)
        
        for court in range(1, max_courts + 1):
            row = [f"コート{court}"]
            for round_data in st.session_state.rounds:
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
        header = ["コート"] + [f"ラウンド{r['round']}" for r in st.session_state.rounds]
        table_data.insert(0, header)
        
        # テーブル表示
        df = pd.DataFrame(table_data[1:], columns=table_data[0])
        st.dataframe(df, use_container_width=True)
        
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
                                    record_match_result(i, j, score1, score2)
                                    st.rerun()
                        else:
                            st.write(f"**スコア**: {match['score1']} - {match['score2']}")

elif page == "統計・履歴":
    st.header("📈 統計・履歴")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ユーザー統計")
        if st.session_state.users:
            stats_data = []
            for user in st.session_state.users:
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
            ratings = [user['rating'] for user in st.session_state.users]
            if ratings:
                fig = px.histogram(x=ratings, nbins=10, title="レーティング分布")
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("ペア履歴")
        if st.session_state.pair_history:
            pair_data = []
            for pair_key, count in st.session_state.pair_history.items():
                players = pair_key.split('_')
                pair_data.append({
                    'ペア': f"{players[0]} & {players[1]}",
                    '回数': count
                })
            
            pair_df = pd.DataFrame(pair_data)
            pair_df = pair_df.sort_values('回数', ascending=False)
            st.dataframe(pair_df, use_container_width=True)
        
        st.subheader("バイ履歴")
        if st.session_state.bye_history:
            bye_data = []
            for player, count in st.session_state.bye_history.items():
                bye_data.append({
                    'プレイヤー': player,
                    'バイ回数': count
                })
            
            bye_df = pd.DataFrame(bye_data)
            bye_df = bye_df.sort_values('バイ回数', ascending=False)
            st.dataframe(bye_df, use_container_width=True)

# フッター
st.markdown("---")
st.markdown("ピックルボール練習試合管理システム v1.0") 