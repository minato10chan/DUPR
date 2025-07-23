import streamlit as st
from services.match_service import MatchService
from services.player_service import PlayerService
import pandas as pd

def show_match_history():
    """試合履歴ページを表示"""
    st.title("📋 試合履歴")
    
    match_service = MatchService()
    player_service = PlayerService()
    
    # 試合履歴を取得
    matches = match_service.get_all_matches()
    players = player_service.get_all_players()
    
    if not matches:
        st.info("まだ試合履歴がありません。")
        return
    
    # プレイヤー名のマッピングを作成
    player_name_map = {p.id: p.name for p in players}
    
    # 完了済み試合のみを表示
    completed_matches = [m for m in matches if m.is_completed]
    
    if not completed_matches:
        st.info("完了した試合がまだありません。")
        return
    
    # 試合履歴をテーブル形式で表示
    st.subheader("完了済み試合")
    
    # データフレーム用のデータを準備
    history_data = []
    for match in completed_matches:
        team1_names = [player_name_map.get(pid, "不明") for pid in match.team1_player_ids]
        team2_names = [player_name_map.get(pid, "不明") for pid in match.team2_player_ids]
        
        history_data.append({
            "試合": f"第{match.match_index}試合",
            "コート": f"コート{match.court_number}",
            "チーム1": " & ".join(team1_names),
            "スコア": f"{match.team1_score} - {match.team2_score}",
            "チーム2": " & ".join(team2_names),
            "勝者": "チーム1" if match.winner_team == 1 else "チーム2" if match.winner_team == 2 else "引き分け",
            "完了日時": match.completed_at[:16] if match.completed_at else "不明"
        })
    
    # データフレームを作成して表示
    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 試合詳細と編集機能
    st.subheader("📝 試合詳細・編集")
    
    # 試合選択
    if completed_matches:
        selected_match_index = st.selectbox(
            "編集する試合を選択",
            options=[m.match_index for m in completed_matches],
            format_func=lambda x: f"第{x}試合"
        )
        
        selected_match = next(m for m in completed_matches if m.match_index == selected_match_index)
        
        if selected_match:
            # 試合詳細表示
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**試合情報**")
                st.write(f"試合番号: 第{selected_match.match_index}試合")
                st.write(f"コート: コート{selected_match.court_number}")
                st.write(f"完了日時: {selected_match.completed_at[:16] if selected_match.completed_at else '不明'}")
                
                winner = "チーム1" if selected_match.winner_team == 1 else "チーム2" if selected_match.winner_team == 2 else "引き分け"
                st.write(f"勝者: {winner}")
            
            with col2:
                st.write("**チーム構成**")
                team1_names = [player_name_map.get(pid, "不明") for pid in selected_match.team1_player_ids]
                team2_names = [player_name_map.get(pid, "不明") for pid in selected_match.team2_player_ids]
                
                st.write("🔵 **チーム1**")
                for name in team1_names:
                    st.write(f"  • {name}")
                
                st.write("🔴 **チーム2**")
                for name in team2_names:
                    st.write(f"  • {name}")
            
            st.divider()
            
            # 編集・削除ボタン
            col_edit, col_delete, col_view = st.columns(3)
            
            with col_edit:
                if st.button("✏️ スコアを編集", use_container_width=True, type="primary"):
                    st.session_state["editing_match_history"] = selected_match.id
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️ 試合を削除", use_container_width=True, type="secondary"):
                    st.session_state["deleting_match_history"] = selected_match.id
                    st.rerun()
            
            with col_view:
                if st.button("👁️ 詳細表示", use_container_width=True):
                    st.session_state["viewing_match_details"] = selected_match.id
                    st.rerun()
            
            # 編集モード
            if st.session_state.get("editing_match_history") == selected_match.id:
                show_match_history_edit_form(selected_match, player_service, match_service)
            
            # 削除確認
            if st.session_state.get("deleting_match_history") == selected_match.id:
                show_match_history_delete_confirmation(selected_match, player_service, match_service)
            
            # 詳細表示
            if st.session_state.get("viewing_match_details") == selected_match.id:
                show_match_history_details(selected_match, player_service)
    
    # 統計情報
    st.subheader("📊 試合統計")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("総試合数", len(completed_matches))
    
    with col2:
        total_points = sum(m.team1_score + m.team2_score for m in completed_matches)
        avg_points = total_points / len(completed_matches) if completed_matches else 0
        st.metric("平均総得点", f"{avg_points:.1f}")
    
    with col3:
        # 各コートの使用回数
        court_usage = {}
        for match in completed_matches:
            court_usage[match.court_number] = court_usage.get(match.court_number, 0) + 1
        most_used_court = max(court_usage.keys()) if court_usage else 1
        st.metric("最多使用コート", f"コート{most_used_court}")

    # 詳細な個人成績は別のセクションで表示
    st.subheader("👤 個人成績サマリー")
    
    # 参加プレイヤーの成績を計算
    player_stats = {}
    for match in completed_matches:
        for player_id in match.team1_player_ids + match.team2_player_ids:
            if player_id not in player_stats:
                player_stats[player_id] = {
                    "name": player_name_map.get(player_id, "不明"),
                    "matches": 0,
                    "wins": 0,
                    "points_scored": 0,
                    "points_conceded": 0
                }
            
            player_stats[player_id]["matches"] += 1
            
            # 勝敗の記録
            if match.winner_team == 1 and player_id in match.team1_player_ids:
                player_stats[player_id]["wins"] += 1
                player_stats[player_id]["points_scored"] += match.team1_score
                player_stats[player_id]["points_conceded"] += match.team2_score
            elif match.winner_team == 2 and player_id in match.team2_player_ids:
                player_stats[player_id]["wins"] += 1
                player_stats[player_id]["points_scored"] += match.team2_score
                player_stats[player_id]["points_conceded"] += match.team1_score
            else:
                # 負けた場合
                if player_id in match.team1_player_ids:
                    player_stats[player_id]["points_scored"] += match.team1_score
                    player_stats[player_id]["points_conceded"] += match.team2_score
                else:
                    player_stats[player_id]["points_scored"] += match.team2_score
                    player_stats[player_id]["points_conceded"] += match.team1_score
    
    # 成績データフレームを作成
    if player_stats:
        stats_data = []
        for player_id, stats in player_stats.items():
            win_rate = (stats["wins"] / stats["matches"]) * 100 if stats["matches"] > 0 else 0
            avg_scored = stats["points_scored"] / stats["matches"] if stats["matches"] > 0 else 0
            avg_conceded = stats["points_conceded"] / stats["matches"] if stats["matches"] > 0 else 0
            
            stats_data.append({
                "プレイヤー": stats["name"],
                "試合数": stats["matches"],
                "勝数": stats["wins"],
                "勝率": f"{win_rate:.1f}%",
                "平均得点": f"{avg_scored:.1f}",
                "平均失点": f"{avg_conceded:.1f}"
            })
        
        stats_df = pd.DataFrame(stats_data)
        # 勝率でソート
        stats_df = stats_df.sort_values("勝率", ascending=False)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

def show_match_history_edit_form(match, player_service, match_service):
    """試合履歴の編集フォーム"""
    st.divider()
    st.markdown("### ✏️ 試合結果を編集")
    
    # プレイヤー名の取得
    all_players = player_service.get_all_players()
    player_name_map = {p.id: p.name for p in all_players}
    
    team1_names = [player_name_map.get(pid, "不明") for pid in match.team1_player_ids]
    team2_names = [player_name_map.get(pid, "不明") for pid in match.team2_player_ids]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔵 チーム1")
        st.write(" & ".join(team1_names))
        team1_score = st.number_input("スコア編集用", min_value=0, max_value=50, value=match.team1_score, key=f"history_team1_{match.id}", label_visibility="collapsed")
    
    with col2:
        st.markdown("#### 🔴 チーム2")
        st.write(" & ".join(team2_names))
        team2_score = st.number_input("スコア編集用", min_value=0, max_value=50, value=match.team2_score, key=f"history_team2_{match.id}", label_visibility="collapsed")
    
    # 操作ボタン
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("💾 保存", key=f"history_save_{match.id}", use_container_width=True, type="primary"):
            # 既存の結果を削除（スキルポイントを元に戻す）
            match_service.revert_match_result(match, all_players)
            
            # 新しい結果を記録
            success = match_service.record_match_result(
                match.id, team1_score, team2_score, all_players
            )
            
            if success:
                # プレイヤー情報も更新
                for player in all_players:
                    player_service.update_player(player)
                
                # 編集モードを終了
                st.session_state["editing_match_history"] = None
                st.success("試合結果を更新しました！")
                st.rerun()
            else:
                st.error("更新に失敗しました")
    
    with col_cancel:
        if st.button("❌ キャンセル", key=f"history_cancel_{match.id}", use_container_width=True):
            st.session_state["editing_match_history"] = None
            st.rerun()

def show_match_history_delete_confirmation(match, player_service, match_service):
    """試合履歴の削除確認"""
    st.divider()
    st.warning("⚠️ **試合結果の削除**")
    st.write(f"第{match.match_index}試合の結果を削除しますか？")
    st.write(f"**スコア**: {match.team1_score} - {match.team2_score}")
    
    col_confirm, col_cancel = st.columns(2)
    
    with col_confirm:
        if st.button("🗑️ 削除する", key=f"history_confirm_delete_{match.id}", use_container_width=True, type="primary"):
            all_players = player_service.get_all_players()
            
            # スキルポイントを元に戻す
            match_service.revert_match_result(match, all_players)
            
            # 試合を未完了状態に戻す
            match.team1_score = 0
            match.team2_score = 0
            match.is_completed = False
            match.completed_at = None
            
            # 保存
            if match_service.save_match(match):
                # プレイヤー情報も更新
                for player in all_players:
                    player_service.update_player(player)
                
                st.session_state["deleting_match_history"] = None
                st.success("試合結果を削除しました！")
                st.rerun()
            else:
                st.error("削除に失敗しました")
    
    with col_cancel:
        if st.button("❌ キャンセル", key=f"history_cancel_delete_{match.id}", use_container_width=True):
            st.session_state["deleting_match_history"] = None
            st.rerun()

def show_match_history_details(match, player_service):
    """試合履歴の詳細表示"""
    st.divider()
    st.write("**👁️ 試合詳細**")
    
    all_players = player_service.get_all_players()
    player_name_map = {p.id: p.name for p in all_players}
    
    # チーム1の詳細
    st.write("🔵 **チーム1**")
    team1_players = [p for p in all_players if p.id in match.team1_player_ids]
    for player in team1_players:
        st.write(f"  • {player.name} (Lv.{player.level}, SP: {player.skill_points:.0f})")
    
    st.write("🔴 **チーム2**")
    team2_players = [p for p in all_players if p.id in match.team2_player_ids]
    for player in team2_players:
        st.write(f"  • {player.name} (Lv.{player.level}, SP: {player.skill_points:.0f})")
    
    # スコア詳細
    st.write(f"**スコア**: {match.team1_score} - {match.team2_score}")
    
    if st.button("❌ 閉じる", key=f"close_details_{match.id}"):
        st.session_state["viewing_match_details"] = None
        st.rerun()

if __name__ == "__main__":
    show_match_history() 