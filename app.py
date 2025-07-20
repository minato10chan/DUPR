import streamlit as st
import pandas as pd
from typing import Dict, List

# 設定とインポート
from config.settings import (
    APP_TITLE, 
    APP_ICON, 
    DEFAULT_COURT_COUNT, 
    DEFAULT_MATCH_COUNT, 
    DEFAULT_SKILL_MATCHING,
    MAX_COURTS,
    MAX_MATCHES
)
from models.player import Player
from models.match import Match
from utils.data_manager import load_data, get_data_file_info
from services.player_service import PlayerService
from services.match_service import MatchService

# ページ設定
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# モバイルフレンドリーなCSS
st.markdown("""
<style>
    /* モバイル対応のボタンサイズ */
    .stButton > button {
        min-height: 44px;
        font-size: 16px;
    }
    
    /* サイドバーの幅調整 */
    .css-1d391kg {
        min-width: 300px;
    }
    
    /* データフレームのレスポンシブ対応 */
    .dataframe {
        font-size: 14px;
    }
    
    /* メトリクスの表示改善 */
    .metric-container {
        padding: 10px;
    }
    
    /* モバイルでのテキストサイズ調整 */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .stButton > button {
            width: 100%;
        }
        
        .stNumberInput > div > div > input {
            font-size: 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'players' not in st.session_state:
    st.session_state.players = {}
if 'matches' not in st.session_state:
    st.session_state.matches = []
if 'current_matches' not in st.session_state:
    st.session_state.current_matches = []
if 'court_count' not in st.session_state:
    st.session_state.court_count = DEFAULT_COURT_COUNT
if 'match_count' not in st.session_state:
    st.session_state.match_count = DEFAULT_MATCH_COUNT
if 'skill_matching' not in st.session_state:
    st.session_state.skill_matching = DEFAULT_SKILL_MATCHING

# データ読み込み（セッション状態初期化後）
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
    st.title(APP_TITLE)
    
    # サイドバー - 設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 設定セクション
        with st.expander("🏟️ 試合設定", expanded=True):
            # コート数設定
            st.session_state.court_count = st.number_input(
                "コート数", 
                min_value=1, 
                max_value=MAX_COURTS, 
                value=st.session_state.court_count,
                help="使用可能なコート数を設定"
            )
            
            # 試合数設定
            st.session_state.match_count = st.number_input(
                "生成試合数", 
                min_value=1, 
                max_value=MAX_MATCHES, 
                value=st.session_state.match_count,
                help="一度に生成する試合数を設定"
            )
            
            # スキルレベルマッチング
            st.session_state.skill_matching = st.checkbox(
                "スキルレベルマッチング", 
                value=st.session_state.skill_matching,
                help="レベルを考慮した組み合わせ生成"
            )
            
            # 組み合わせ設定
            st.info("過去の組み合わせを避けて新しい組み合わせを生成します")
        
        # データ保存状況表示
        file_info = get_data_file_info()
        if file_info['exists']:
            st.success(f"💾 データ保存中 ({file_info['size']} bytes)")
        
        st.divider()
        
        # 参加者管理
        st.header("👥 参加者管理")
        
        # ユーザー管理ページへのリンク
        if st.button("👥 ユーザー管理ページ", type="secondary", use_container_width=True):
            st.switch_page("pages/user_management.py")
        
        # 参加者追加
        new_player = st.text_input("新しい参加者名", placeholder="参加者名を入力")
        if st.button("➕ 参加者追加", type="primary", use_container_width=True) and new_player.strip():
            if player_service.add_player(new_player.strip()):
                st.rerun()
        

        
        st.divider()
        
        # 参加者一覧と管理
        if st.session_state.players:
            st.subheader("📋 参加者一覧")
            
            # 参加者数と参加可能人数の表示
            summary_stats = player_service.get_summary_stats()
            st.info(f"👥 登録者: {summary_stats['total_players']}人 | ✅ 参加可能: {summary_stats['active_players']}人")
            
            # 参加者管理テーブル
            for name, player in st.session_state.players.items():
                with st.container():
                    # 参加者名、レベル、ステータスを同じ行に表示
                    col1, col2, col3 = st.columns([3, 1, 2])
                    with col1:
                        st.write(f"**{name}** (Lv.{player.level})")
                    with col2:
                        status = "参加中" if not player.is_resting else "休憩中"
                        status_color = "🟢" if not player.is_resting else "🔴"
                        st.write(f"{status_color} {status}")
                    with col3:
                        if st.button(
                            "参加" if player.is_resting else "休憩",
                            key=f"toggle_{name}",
                            type="primary" if not player.is_resting else "secondary",
                            use_container_width=True
                        ):
                            player_service.toggle_rest_status(name)
                            st.rerun()
        else:
            st.info("参加者が登録されていません。上記で参加者を追加してください。")
    
    # 参加者状況サマリー
    if st.session_state.players:
        summary_stats = player_service.get_summary_stats()
        
        # モバイル対応のメトリクス表示
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👥 登録者数", summary_stats['total_players'])
            st.metric("✅ 参加可能", summary_stats['active_players'])
        with col2:
            st.metric("🏆 完了試合", summary_stats['completed_matches'])
            if summary_stats['can_play']:
                st.metric("🎾 試合可能", "準備完了", delta="✅")
            else:
                st.metric("🎾 試合可能", "人数不足", delta=f"❌ あと{4 - summary_stats['active_players']}人")
    
    st.divider()
    
    # 現在の試合
    st.subheader("🏓 現在の試合")
    
    if not st.session_state.current_matches:
        st.info(f"📋 生成試合数: {st.session_state.match_count}試合 | 🏟️ コート数: {st.session_state.court_count}コート")
        if st.button("🎯 新しい試合を生成", type="primary", use_container_width=True):
            new_matches = match_service.create_new_matches(
                st.session_state.court_count,
                st.session_state.match_count,
                st.session_state.skill_matching
            )
            if new_matches:
                st.session_state.current_matches = new_matches
                if len(new_matches) < st.session_state.match_count:
                    st.warning(f"要求された{st.session_state.match_count}試合のうち、{len(new_matches)}試合のみ生成されました。参加者数が少ない場合、同じプレイヤーが複数試合に参加します。")
                else:
                    st.success(f"✅ {len(new_matches)}試合を生成しました")
                st.rerun()
            else:
                st.warning("試合を生成するには4人以上の参加者が必要です")
    else:
        st.success(f"🎉 現在 {len(st.session_state.current_matches)}試合が進行中です")
        for i, match in enumerate(st.session_state.current_matches):
            with st.container():
                st.markdown(f"### 🏟️ コート{match.court}")
                
                # チーム情報
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**🔵 チーム1:** {', '.join(match.team1)}")
                with col2:
                    st.write(f"**🔴 チーム2:** {', '.join(match.team2)}")
                
                # スコア入力
                col1, col2 = st.columns(2)
                with col1:
                    team1_score = st.number_input("チーム1得点", min_value=0, key=f"score1_{i}")
                with col2:
                    team2_score = st.number_input("チーム2得点", min_value=0, key=f"score2_{i}")
                
                # 試合完了ボタン
                if st.button("🏁 試合完了", key=f"complete_{i}", type="primary", use_container_width=True):
                    match_service.complete_match(match, team1_score, team2_score)
                    # レベルを自動更新
                    player_service.update_player_levels()
                    # 現在の試合から削除
                    st.session_state.current_matches.remove(match)
                    st.rerun()
                
                st.divider()
    
    # 統計表示
    display_player_stats()
    
    # 試合履歴
    if st.session_state.matches:
        st.subheader("📜 試合履歴")
        
        # 試合履歴管理ページへのリンク
        if st.button("📜 試合履歴管理", type="secondary", use_container_width=True):
            st.switch_page("pages/match_history.py")
        
        history_data = match_service.get_match_history()
        
        if history_data:
            df_history = pd.DataFrame(history_data)
            st.dataframe(df_history, use_container_width=True, hide_index=True)

def display_player_stats():
    """プレイヤーの統計を表示"""
    if not st.session_state.players:
        st.info("参加者が登録されていません")
        return
    
    # 統計データを取得
    stats_data = player_service.get_player_stats()
    df = pd.DataFrame(stats_data)
    
    # 勝率順でソート
    df_sorted = df.sort_values('勝率', ascending=False)
    
    st.subheader("📊 参加者統計")
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)
    
    st.subheader("📈 今日の試合数")
    completed_matches = match_service.get_completed_matches_count()
    st.metric("🏆 完了試合数", completed_matches)

if __name__ == "__main__":
    main() 