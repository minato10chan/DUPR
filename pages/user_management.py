import streamlit as st
import pandas as pd
from models.player import Player
from services.player_service import PlayerService
from services.match_service import MatchService
from utils.data_manager import load_data, save_data
from config.settings import APP_TITLE

# ページ設定
st.set_page_config(
    page_title="ユーザー管理 - " + APP_TITLE,
    page_icon="👥",
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

def main():
    st.title("👥 ユーザー管理")
    st.markdown("参加者の登録、編集、削除を行います。")
    
    # メインページへのリンク
    if st.button("🏠 メインページに戻る", type="secondary", use_container_width=True):
        st.switch_page("app.py")
    
    st.divider()
    
    # ユーザー追加セクション
    st.header("➕ 新しいユーザー追加")
    
    # タブで個別追加と一括追加を分ける
    tab1, tab2 = st.tabs(["個別追加", "JSON一括追加"])
    
    with tab1:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            new_user_name = st.text_input("ユーザー名", placeholder="新しいユーザー名を入力", key="single_name")
        with col2:
            new_user_level = st.selectbox("レベル", options=[1, 2, 3, 4, 5], index=2, key="single_level")
        with col3:
            if st.button("追加", type="primary", use_container_width=True, key="single_add") and new_user_name.strip():
                if player_service.add_player(new_user_name.strip(), new_user_level):
                    st.success(f"✅ {new_user_name}を追加しました")
                    st.rerun()
                else:
                    st.error("❌ ユーザー名が既に存在します")
    
    with tab2:
        st.markdown("**JSON形式でユーザーを一括追加**")
        st.markdown("例: `{\"Name\":[\"田井木の実/60代\",\"鈴木郁子/60代\"]}`")
        
        # ファイルアップロード
        uploaded_file = st.file_uploader(
            "JSONファイルをアップロード",
            type=['json'],
            help="JSONファイルを選択してください"
        )
        
        if uploaded_file is not None:
            try:
                json_data = uploaded_file.read().decode('utf-8')
                st.text_area("アップロードされたJSON", json_data, height=100, disabled=True)
                json_input = json_data
            except Exception as e:
                st.error(f"❌ ファイル読み込みエラー: {str(e)}")
                json_input = ""
        else:
            json_input = st.text_area(
                "JSONデータを入力",
                placeholder='{"Name":["ユーザー名1","ユーザー名2","ユーザー名3"]}',
                height=150
            )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            default_level = st.selectbox("デフォルトレベル", options=[1, 2, 3, 4, 5], index=2, key="json_level")
        with col2:
            if st.button("JSONから追加", type="primary", use_container_width=True, key="json_add") and json_input.strip():
                try:
                    import json
                    data = json.loads(json_input)
                    
                    if "Name" in data and isinstance(data["Name"], list):
                        added_count = 0
                        skipped_count = 0
                        
                        for user_name in data["Name"]:
                            if isinstance(user_name, str) and user_name.strip():
                                if player_service.add_player(user_name.strip(), default_level):
                                    added_count += 1
                                else:
                                    skipped_count += 1
                        
                        if added_count > 0:
                            st.success(f"✅ {added_count}人のユーザーを追加しました")
                            if skipped_count > 0:
                                st.warning(f"⚠️ {skipped_count}人は既に存在するためスキップしました")
                            st.rerun()
                        else:
                            st.error("❌ 追加されたユーザーがありません")
                    else:
                        st.error("❌ JSONの形式が正しくありません。'Name'キーと配列が必要です。")
                        
                except json.JSONDecodeError:
                    st.error("❌ JSONの形式が正しくありません")
                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")
    
    st.divider()
    
    # ユーザー一覧セクション
    st.header("📋 ユーザー一覧")
    
    if st.session_state.players:
        # 検索機能
        search_term = st.text_input("🔍 ユーザー検索", placeholder="ユーザー名で検索...")
        
        # 統計情報
        summary_stats = player_service.get_summary_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("総ユーザー数", summary_stats['total_players'])
        with col2:
            st.metric("参加可能", summary_stats['active_players'])
        with col3:
            st.metric("休憩中", summary_stats['total_players'] - summary_stats['active_players'])
        with col4:
            st.metric("完了試合", summary_stats['completed_matches'])
        
        # ユーザー一覧テーブル（検索フィルター適用）
        users_data = []
        filtered_count = 0
        
        for name, player in st.session_state.players.items():
            # 検索フィルター
            if search_term and search_term.lower() not in name.lower():
                continue
                
            filtered_count += 1
            users_data.append({
                "ユーザー名": name,
                "レベル": player.level,
                "試合数": player.matches_played,
                "勝数": player.wins,
                "勝率": f"{player.win_rate:.1%}",
                "得失点比": f"{player.point_ratio:.2f}",
                "ステータス": "🟢 参加中" if not player.is_resting else "🔴 休憩中"
            })
        
        # 検索結果の表示
        if search_term:
            st.info(f"🔍 検索結果: {filtered_count}人 / 総ユーザー数: {summary_stats['total_players']}人")
        
        df_users = pd.DataFrame(users_data)
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        
        # ユーザー編集セクション
        st.subheader("✏️ ユーザー編集")
        
        # ユーザー選択（検索フィルター適用）
        if search_term:
            # 検索結果からユーザー名を取得
            filtered_user_names = [name for name in st.session_state.players.keys() 
                                 if search_term.lower() in name.lower()]
            if filtered_user_names:
                user_names = filtered_user_names
                st.info(f"🔍 検索結果から{len(user_names)}人を選択可能")
            else:
                user_names = list(st.session_state.players.keys())
                st.warning("🔍 検索結果がありません。全ユーザーを表示します。")
        else:
            user_names = list(st.session_state.players.keys())
        
        selected_user = st.selectbox("編集するユーザーを選択", user_names)
        
        if selected_user:
            player = st.session_state.players[selected_user]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**選択中:** {selected_user}")
            
            with col2:
                new_level = st.selectbox(
                    "レベル",
                    options=[1, 2, 3, 4, 5],
                    index=player.level - 1,
                    key="edit_level"
                )
                if new_level != player.level:
                    player_service.update_player_level(selected_user, new_level)
                    st.success(f"レベルを{new_level}に更新しました")
            
            with col3:
                status = "参加中" if not player.is_resting else "休憩中"
                st.write(f"**現在のステータス:** {status}")
                
                if st.button(
                    "参加" if player.is_resting else "休憩",
                    key="edit_status",
                    type="primary" if not player.is_resting else "secondary"
                ):
                    player_service.toggle_rest_status(selected_user)
                    st.rerun()
            
            with col4:
                if st.button("🗑️ 削除", key="delete_user", type="secondary"):
                    player_service.remove_player(selected_user)
                    st.success(f"✅ {selected_user}を削除しました")
                    st.rerun()
    
    else:
        st.info("ユーザーが登録されていません。上記でユーザーを追加してください。")

if __name__ == "__main__":
    main() 