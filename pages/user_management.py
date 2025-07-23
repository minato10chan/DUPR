import streamlit as st
from services.player_service import PlayerService

def show_user_management():
    """ユーザー管理ページを表示"""
    st.title("👥 プレイヤー管理")
    
    player_service = PlayerService()
    
    # プレイヤー追加タブ
    add_tab1, add_tab2 = st.tabs(["👤 個別追加", "📋 一括追加"])
    
    with add_tab1:
        # 新しいプレイヤーの追加（個別）
        st.subheader("新しいプレイヤーを追加")
        with st.form("add_player_form"):
            new_player_name = st.text_input(
                "プレイヤー名", 
                placeholder="プレイヤー名を入力してください",
                key="new_player_name"
            )
            submit_add = st.form_submit_button("➕ プレイヤーを追加", use_container_width=True)
            
            if submit_add and new_player_name.strip():
                try:
                    player_service.create_player(new_player_name.strip())
                    st.success(f"プレイヤー「{new_player_name}」を追加しました！")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
            elif submit_add:
                st.error("プレイヤー名を入力してください")
    
    with add_tab2:
        # JSON一括登録
        st.subheader("📋 JSON一括登録")
        st.write("複数のプレイヤーを一度に登録できます。")
        
        # 使用例の表示
        with st.expander("📝 JSONフォーマット例", expanded=False):
            st.code('''
{
  "Name": [
    "委員長代理/40代",
    "高橋理事長/40代", 
    "今本あけみ/50代",
    "うちだなおき/30代",
    "内田美由紀/30代",
    "森田亜希子/50代",
    "タケウチカツミ/50代"
  ]
}
            ''', language='json')
        
        # JSON入力
        json_input = st.text_area(
            "JSONデータを入力してください",
            placeholder='{"Name": ["プレイヤー1", "プレイヤー2", "プレイヤー3"]}',
            height=200,
            key="json_input"
        )
        
        # 自動参加オプション
        auto_participate = st.checkbox(
            "✅ 追加時に自動で参加者にする", 
            value=True,
            help="ONにすると、追加されたプレイヤーが自動で参加者に設定されます"
        )
        
        # 一括登録ボタン
        if st.button("📋 一括登録", use_container_width=True, type="primary"):
            if json_input.strip():
                try:
                    import json
                    
                    # JSONパース
                    data = json.loads(json_input)
                    
                    # "Name"キーの存在確認
                    if "Name" not in data:
                        st.error("❌ JSONに'Name'キーが見つかりません")
                    elif not isinstance(data["Name"], list):
                        st.error("❌ 'Name'の値はリスト形式である必要があります")
                    else:
                        names = data["Name"]
                        
                        if not names:
                            st.error("❌ プレイヤー名のリストが空です")
                        else:
                            # プレイヤー追加処理
                            success_count = 0
                            error_count = 0
                            duplicate_count = 0
                            errors = []
                            added_players = []
                            
                            for name in names:
                                name = str(name).strip()
                                if name:
                                    try:
                                        new_player = player_service.create_player(name)
                                        added_players.append(new_player)
                                        success_count += 1
                                    except ValueError as e:
                                        if "既に存在" in str(e):
                                            duplicate_count += 1
                                            # 既存プレイヤーも自動参加に含める場合
                                            if auto_participate:
                                                existing_player = next((p for p in player_service.get_all_players() if p.name == name), None)
                                                if existing_player and not existing_player.is_participating_today:
                                                    added_players.append(existing_player)
                                        else:
                                            error_count += 1
                                            errors.append(f"{name}: {str(e)}")
                            
                            # 自動参加機能
                            if auto_participate and added_players:
                                for player in added_players:
                                    player_service.set_participation_status(player.id, True)
                                # 番号を自動割り振り
                                player_service.assign_player_numbers()
                            
                            # 結果表示
                            if success_count > 0:
                                if auto_participate:
                                    st.success(f"✅ {success_count}人のプレイヤーを追加し、参加者に設定しました！")
                                else:
                                    st.success(f"✅ {success_count}人のプレイヤーを追加しました！")
                            if duplicate_count > 0:
                                if auto_participate:
                                    st.warning(f"⚠️ {duplicate_count}人は既に登録済みでしたが、参加者に設定しました")
                                else:
                                    st.warning(f"⚠️ {duplicate_count}人は既に登録済みでした")
                            if error_count > 0:
                                st.error(f"❌ {error_count}人の登録に失敗しました")
                                for error in errors:
                                    st.error(f"  • {error}")
                            
                            if success_count > 0 or (auto_participate and duplicate_count > 0):
                                st.rerun()
                
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON形式が正しくありません: {str(e)}")
                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")
            else:
                st.error("❌ JSONデータを入力してください")
    
    st.divider()
    
    # 既存プレイヤーの管理
    st.subheader("登録プレイヤー一覧")
    players = player_service.get_all_players()
    
    if not players:
        st.info("まだプレイヤーが登録されていません。上記のフォームから追加してください。")
        return
    
    # プレイヤー一覧をカード形式で表示
    for player in players:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{player.name}**")
                st.caption(f"スキルレベル: {player.level} | スキルポイント: {player.skill_points:.1f}")
            
            with col2:
                if player.is_participating_today:
                    st.success("参加中")
                else:
                    st.info("不参加")
            
            with col3:
                if st.button("🗑️ 削除", key=f"delete_{player.id}"):
                    if player_service.delete_player(player.id):
                        st.success(f"プレイヤー「{player.name}」を削除しました")
                        st.rerun()
                    else:
                        st.error("削除に失敗しました")
        
        st.divider()
    
    # 便利機能
    st.subheader("🛠️ 便利機能")
    col_export, col_clear = st.columns(2)
    
    with col_export:
        if st.button("📤 JSON形式でエクスポート", use_container_width=True):
            if players:
                export_data = {
                    "Name": [p.name for p in players]
                }
                import json
                json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
                st.text_area("エクスポートされたJSON", json_str, height=200)
                st.success("✅ プレイヤー情報をJSONでエクスポートしました")
            else:
                st.info("エクスポートするプレイヤーがいません")
    
    with col_clear:
        if st.button("🗑️ 全プレイヤー削除", use_container_width=True):
            st.session_state["confirm_delete_all_players"] = True
            st.rerun()
    
    # 全削除確認ダイアログ
    if st.session_state.get("confirm_delete_all_players", False):
        st.warning("⚠️ **全プレイヤー削除確認**")
        st.write("すべてのプレイヤーを削除しますか？この操作は取り消せません。")
        
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("🗑️ 全削除実行", key="confirm_delete_all", use_container_width=True):
                try:
                    for player in players:
                        player_service.delete_player(player.id)
                    st.session_state["confirm_delete_all_players"] = False
                    st.success("✅ 全プレイヤーを削除しました")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 削除に失敗しました: {e}")
        
        with col_cancel:
            if st.button("❌ キャンセル", key="cancel_delete_all", use_container_width=True):
                st.session_state["confirm_delete_all_players"] = False
                st.rerun()
    
    st.divider()
    
    # 統計情報
    st.subheader("📊 統計情報")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("登録プレイヤー数", len(players))
    
    with col2:
        participating_count = len([p for p in players if p.is_participating_today])
        st.metric("本日参加予定", participating_count)
    
    with col3:
        avg_skill = sum(p.skill_points for p in players) / len(players) if players else 0
        st.metric("平均スキルポイント", f"{avg_skill:.1f}")

if __name__ == "__main__":
    show_user_management() 