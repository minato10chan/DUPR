import streamlit as st
import pandas as pd
from models.player import Player
from models.match import Match
from services.player_service import PlayerService
from services.match_service import MatchService
from utils.data_manager import load_data, save_data
from config.settings import APP_TITLE

# ページ設定
st.set_page_config(
    page_title="試合履歴管理 - " + APP_TITLE,
    page_icon="📜",
    layout="wide"
)

# セッション状態の初期化
if 'players' not in st.session_state:
    st.session_state.players = {}
if 'matches' not in st.session_state:
    st.session_state.matches = []

# データ読み込み
if not st.session_state.players and not st.session_state.matches:
    loaded_players, loaded_matches = load_data()
    if loaded_players:
        st.session_state.players = loaded_players
    if loaded_matches:
        st.session_state.matches = loaded_matches

# サービスインスタンスの初期化
player_service = PlayerService(st.session_state.players, st.session_state.matches)
match_service = MatchService(st.session_state.players, st.session_state.matches)

def main():
    st.title("📜 試合履歴管理")
    st.markdown("完了した試合の履歴を確認、編集、削除できます。")
    
    # メインページへのリンク
    if st.button("🏠 メインページに戻る", type="secondary", use_container_width=True):
        st.switch_page("app.py")
    
    st.divider()
    
    # 試合履歴セクション
    st.header("📋 試合履歴一覧")
    
    # 完了した試合のみを取得
    completed_matches = [match for match in st.session_state.matches if match.is_completed]
    
    if completed_matches:
        # 統計情報
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("総試合数", len(completed_matches))
        with col2:
            total_players = len(st.session_state.players)
            st.metric("登録ユーザー数", total_players)
        with col3:
            avg_matches = sum(player.matches_played for player in st.session_state.players.values()) / max(total_players, 1)
            st.metric("平均試合数", f"{avg_matches:.1}")
        with col4:
            total_points = sum(match.team1_score + match.team2_score for match in completed_matches)
            st.metric("総得点数", total_points)
        
        # 検索機能
        search_term = st.text_input("🔍 試合検索", placeholder="プレイヤー名で検索...")
        
        # 試合履歴テーブル
        history_data = []
        filtered_count = 0
        
        for i, match in enumerate(completed_matches):
            # 検索フィルター
            all_players = match.team1 + match.team2
            if search_term and not any(search_term.lower() in player.lower() for player in all_players):
                continue
                
            filtered_count += 1
            history_data.append({
                "試合ID": i,
                "コート": match.court,
                "チーム1": ', '.join(match.team1),
                "チーム2": ', '.join(match.team2),
                "スコア": f"{match.team1_score} - {match.team2_score}",
                "勝者": ', '.join(match.winner),
                "試合日時": match.completed_at.strftime("%Y-%m-%d %H:%M") if hasattr(match, 'completed_at') and match.completed_at else "不明"
            })
        
        # 検索結果の表示
        if search_term:
            st.info(f"🔍 検索結果: {filtered_count}試合 / 総試合数: {len(completed_matches)}試合")
        
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        
        # 試合編集セクション
        st.subheader("✏️ 試合編集")
        
        # 試合選択（検索フィルター適用）
        if search_term:
            filtered_match_indices = [i for i, match in enumerate(completed_matches) 
                                    if any(search_term.lower() in player.lower() 
                                          for player in match.team1 + match.team2)]
            if filtered_match_indices:
                match_indices = filtered_match_indices
                st.info(f"🔍 検索結果から{len(match_indices)}試合を選択可能")
            else:
                match_indices = list(range(len(completed_matches)))
                st.warning("🔍 検索結果がありません。全試合を表示します。")
        else:
            match_indices = list(range(len(completed_matches)))
        
        if match_indices:
            selected_match_index = st.selectbox(
                "編集する試合を選択", 
                match_indices,
                format_func=lambda x: f"試合{x+1}: {completed_matches[x].team1_score}-{completed_matches[x].team2_score} ({', '.join(completed_matches[x].team1)} vs {', '.join(completed_matches[x].team2)})"
            )
            
            if selected_match_index is not None:
                selected_match = completed_matches[selected_match_index]
                
                st.markdown(f"**選択中の試合:** コート{selected_match.court}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**チーム1:** {', '.join(selected_match.team1)}")
                    new_team1_score = st.number_input(
                        "チーム1得点", 
                        min_value=0, 
                        value=selected_match.team1_score,
                        key="edit_team1_score"
                    )
                
                with col2:
                    st.write(f"**チーム2:** {', '.join(selected_match.team2)}")
                    new_team2_score = st.number_input(
                        "チーム2得点", 
                        min_value=0, 
                        value=selected_match.team2_score,
                        key="edit_team2_score"
                    )
                
                # 編集・削除ボタン
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 更新", type="primary", use_container_width=True):
                        # 古い結果を元に戻す
                        old_team1_score = selected_match.team1_score
                        old_team2_score = selected_match.team2_score
                        old_winner = selected_match.winner
                        
                        # プレイヤーの統計を元に戻す
                        for player_name in selected_match.team1:
                            player = st.session_state.players[player_name]
                            player.matches_played -= 1
                            player.total_points_scored -= old_team1_score
                            player.total_points_conceded -= old_team2_score
                            if player_name in old_winner:
                                player.wins -= 1
                        
                        for player_name in selected_match.team2:
                            player = st.session_state.players[player_name]
                            player.matches_played -= 1
                            player.total_points_scored -= old_team2_score
                            player.total_points_conceded -= old_team1_score
                            if player_name in old_winner:
                                player.wins -= 1
                        
                        # 新しい結果を適用
                        selected_match.team1_score = new_team1_score
                        selected_match.team2_score = new_team2_score
                        selected_match.winner = selected_match.team1 if new_team1_score > new_team2_score else selected_match.team2
                        
                        # プレイヤーの統計を更新
                        for player_name in selected_match.team1:
                            player = st.session_state.players[player_name]
                            player.matches_played += 1
                            player.total_points_scored += new_team1_score
                            player.total_points_conceded += new_team2_score
                            if player_name in selected_match.winner:
                                player.wins += 1
                        
                        for player_name in selected_match.team2:
                            player = st.session_state.players[player_name]
                            player.matches_played += 1
                            player.total_points_scored += new_team2_score
                            player.total_points_conceded += new_team1_score
                            if player_name in selected_match.winner:
                                player.wins += 1
                        
                        # データを保存
                        save_data(st.session_state.players, st.session_state.matches)
                        st.success("✅ 試合結果を更新しました")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ 削除", type="secondary", use_container_width=True):
                        # プレイヤーの統計を元に戻す
                        for player_name in selected_match.team1:
                            player = st.session_state.players[player_name]
                            player.matches_played -= 1
                            player.total_points_scored -= selected_match.team1_score
                            player.total_points_conceded -= selected_match.team2_score
                            if player_name in selected_match.winner:
                                player.wins -= 1
                        
                        for player_name in selected_match.team2:
                            player = st.session_state.players[player_name]
                            player.matches_played -= 1
                            player.total_points_scored -= selected_match.team2_score
                            player.total_points_conceded -= selected_match.team1_score
                            if player_name in selected_match.winner:
                                player.wins -= 1
                        
                        # 試合を削除
                        st.session_state.matches.remove(selected_match)
                        
                        # データを保存
                        save_data(st.session_state.players, st.session_state.matches)
                        st.success("✅ 試合を削除しました")
                        st.rerun()
    
    else:
        st.info("完了した試合がありません。")
        
        # 現在進行中の試合があるかチェック
        current_matches = [match for match in st.session_state.matches if not match.is_completed]
        if current_matches:
            st.warning(f"⚠️ 現在{len(current_matches)}試合が進行中です。試合を完了させると履歴に表示されます。")

if __name__ == "__main__":
    main() 