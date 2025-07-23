import streamlit as st
from services.player_service import PlayerService
from services.match_service import MatchService
from pages.user_management import show_user_management
from pages.match_history import show_match_history
from config.settings import DEFAULT_COURT_COUNT, MAX_COURTS, MIN_MATCHES_PER_GENERATION, MAX_MATCHES_PER_GENERATION

# ページの設定（スマートフォン最適化）
st.set_page_config(
    page_title="PicklePair - ピックルボール試合運営",
    page_icon="🏓",
    layout="centered",  # モバイル向けセンタードレイアウト
    initial_sidebar_state="collapsed"  # サイドバーを非表示
)

# カスタムCSS（スマートフォン最適化 - 大きなフォント）
st.markdown("""
<style>
    /* メインエリアのパディング調整 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    
    /* 基本フォントサイズを大きく */
    .stMarkdown, .stText {
        font-size: 18px;
    }
    
    /* ボタンを大きく、タップしやすく */
    .stButton > button {
        font-size: 20px;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        min-height: 60px;
        font-weight: bold;
        border: 2px solid transparent;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* プライマリーボタンのスタイル */
    .stButton > button[kind="primary"] {
        font-size: 22px;
        min-height: 70px;
        background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
        border: none;
    }
    
    /* セカンダリボタンのスタイル */
    .stButton > button[kind="secondary"] {
        font-size: 18px;
        background-color: #f8f9fa;
        color: #6c757d;
        border: 2px solid #dee2e6;
    }
    
    /* タブのスタイル - 大きく */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #f0f2f6;
        border-radius: 12px;
        padding: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        flex: 1;
        text-align: center;
        padding: 16px 12px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 18px;
        min-height: 60px;
    }
    
    /* 入力フィールドを大きく */
    .stTextInput > div > div > input {
        font-size: 20px;
        padding: 12px;
        border-radius: 8px;
        min-height: 50px;
    }
    
    .stNumberInput > div > div > input {
        font-size: 20px;
        padding: 12px;
        border-radius: 8px;
        min-height: 50px;
    }
    
    .stSelectbox > div > div > div {
        font-size: 18px;
        min-height: 50px;
    }
    
    /* マルチセレクトを大きく */
    .stMultiSelect > div > div {
        font-size: 18px;
        min-height: 50px;
    }
    
    /* チェックボックスを大きく */
    .stCheckbox > label {
        font-size: 18px;
        font-weight: 500;
    }
    
    .stCheckbox > label > span {
        min-width: 24px;
        min-height: 24px;
    }
    
    /* エラー・成功メッセージを大きく */
    .stAlert {
        font-size: 18px;
        padding: 1rem;
    }
    
    /* キャプションも見やすく */
    .caption {
        font-size: 16px;
        color: #666;
    }
    
    /* メトリクス風の大きな数字表示 */
    .big-number {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #ff6b6b;
    }
    
    /* ポップオーバーも大きく */
    [data-testid="stPopover"] {
        min-width: 90vw;
    }
    
    /* スマホ画面での余白調整 */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }
        
        .stButton > button {
            font-size: 18px;
            min-height: 55px;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            padding: 12px 8px;
        }
    }
</style>
""", unsafe_allow_html=True)

# カスタムCSS
custom_css = """
<style>
    /* メインコンテナのスタイル */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* ボタンのスタイル調整 */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    /* メトリックのスタイル */
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    /* タブのスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        font-weight: 500;
    }
    
    /* エラー・成功メッセージを大きく */
    .stAlert {
        font-size: 16px;
        font-weight: 500;
    }
</style>
"""

def show_score_input_section(match, player_service):
    """スコア入力セクション（同じ画面内）"""
    # プレイヤー情報の取得
    all_players = player_service.get_all_players()
    
    # 2列でスコア入力のみを表示
    col1, col2 = st.columns(2)
    
    with col1:
        team1_score = st.text_input("チーム1スコア", value=str(match.team1_score), key=f"team1_{match.id}", placeholder="スコア", label_visibility="collapsed")
    
    with col2:
        team2_score = st.text_input("チーム2スコア", value=str(match.team2_score), key=f"team2_{match.id}", placeholder="スコア", label_visibility="collapsed")
    
    # 記録ボタン
    if st.button("🏆", key=f"save_{match.id}", use_container_width=True, type="primary", help="結果を記録"):
        # 入力値の検証
        try:
            team1_score_int = int(team1_score) if team1_score else 0
            team2_score_int = int(team2_score) if team2_score else 0
            
            if team1_score_int < 0 or team2_score_int < 0:
                st.error("❌ スコアは0以上の数値を入力してください")
                return
            
            match_service = MatchService()
            success = match_service.record_match_result(
                match.id, team1_score_int, team2_score_int, all_players
            )
            
            if success:
                # プレイヤー情報も更新
                for player in all_players:
                    player_service.update_player(player)
                st.success("🎉 試合結果を記録しました！")
                st.rerun()
            else:
                st.error("❌ 記録に失敗しました")
        except ValueError:
            st.error("❌ スコアは数値で入力してください")

def show_incomplete_match_delete_confirmation(match, player_service):
    """未完了試合の削除確認"""
    st.divider()
    st.warning("⚠️ **未完了試合の削除**")
    st.write(f"第{match.match_index}試合を削除しますか？")
    
    col_delete, col_cancel = st.columns(2)
    
    # 削除確認ボタン
    with col_delete:
        if st.button("🗑️", key=f"confirm_delete_incomplete_{match.id}", use_container_width=True, type="primary", help="削除する"):
            match_service = MatchService()
            
            # 試合を削除（データから完全に除去）
            if match_service.delete_match(match.id):
                # セッション状態をクリア
                st.session_state[f"deleting_incomplete_{match.id}"] = False
                st.success("✅ 試合を削除しました！")
                st.rerun()
            else:
                st.error("❌ 削除に失敗しました")
    
    # キャンセルボタン
    with col_cancel:
        if st.button("❌", key=f"cancel_delete_incomplete_{match.id}", use_container_width=True, help="キャンセル"):
            # セッション状態をクリア
            st.session_state[f"deleting_incomplete_{match.id}"] = False
            st.rerun()

def show_match_edit_form(match, player_service):
    """試合編集フォームを表示"""
    st.divider()
    
    # プレイヤー名の取得
    all_players = player_service.get_all_players()
    
    # 2列でスコア入力のみを表示
    col1, col2 = st.columns(2)
    
    with col1:
        team1_score = st.text_input("チーム1スコア編集", value=str(match.team1_score), key=f"edit_team1_{match.id}", placeholder="スコア", label_visibility="collapsed")
    
    with col2:
        team2_score = st.text_input("チーム2スコア編集", value=str(match.team2_score), key=f"edit_team2_{match.id}", placeholder="スコア", label_visibility="collapsed")
    
    # 保存・キャンセルボタン
    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("💾", key=f"save_edit_{match.id}", use_container_width=True, type="primary", help="保存"):
            # 入力値の検証
            try:
                team1_score_int = int(team1_score) if team1_score else 0
                team2_score_int = int(team2_score) if team2_score else 0
                
                if team1_score_int < 0 or team2_score_int < 0:
                    st.error("スコアは0以上の数値を入力してください")
                    return
                
                # 既存の結果を削除（スキルポイントを元に戻す）
                match_service = MatchService()
                match_service.revert_match_result(match, all_players)
                
                # 新しい結果を記録
                success = match_service.record_match_result(
                    match.id, team1_score_int, team2_score_int, all_players
                )
                
                if success:
                    # プレイヤー情報も更新
                    for player in all_players:
                        player_service.update_player(player)
                    
                    # 編集モードを終了
                    st.session_state[f"editing_match_{match.id}"] = False
                    st.success("試合結果を更新しました！")
                    st.rerun()
                else:
                    st.error("更新に失敗しました")
            except ValueError:
                st.error("スコアは数値で入力してください")
    
    with col_cancel:
        if st.button("❌", key=f"cancel_edit_{match.id}", use_container_width=True, help="キャンセル"):
            # 編集モードを終了
            st.session_state[f"editing_match_{match.id}"] = False
            st.rerun()

def show_delete_confirmation(match, player_service):
    """削除確認ダイアログを表示"""
    st.divider()
    st.warning("⚠️ **試合結果の削除**")
    st.write(f"第{match.match_index}試合の結果を削除しますか？")
    
    col_delete, col_cancel = st.columns(2)
    
    # 削除確認ボタン
    with col_delete:
        if st.button("🗑️", key=f"confirm_delete_{match.id}", use_container_width=True, type="primary", help="削除する"):
            # 試合結果を削除
            match_service = MatchService()
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
                
                st.success("試合結果を削除しました！")
                st.rerun()
            else:
                st.error("削除に失敗しました")
    
    # キャンセルボタン
    with col_cancel:
        if st.button("❌", key=f"cancel_delete_{match.id}", use_container_width=True, help="キャンセル"):
            st.rerun()

def main():
    """メインアプリケーション"""
    try:
        # ヘッダー（大きく）
        st.markdown("# 🏓 PicklePair")
        st.markdown("### 🎾 スマートダブルス試合管理システム")
        
        # カスタムCSS
        st.markdown(custom_css, unsafe_allow_html=True)
        
        # サービス初期化
        player_service = PlayerService()
        match_service = MatchService()
        
        # タブ設定（アイコン付き）
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏆 試合進行", 
            "👥 参加者", 
            "📊 ランキング", 
            "⚙️ 管理"
        ])
        
        with tab1:
            show_match_progress_tab(player_service, match_service)
        
        with tab2:
            show_participants_tab(player_service)
        
        with tab3:
            show_ranking_tab(player_service)
        
        with tab4:
            show_management_tab()
            
    except Exception as e:
        st.error("🚨 アプリケーションの初期化中にエラーが発生しました")
        st.error(f"エラーの詳細: {str(e)}")
        st.info("💡 解決方法:")
        st.write("1. ページを再読み込みしてください")
        st.write("2. データファイルの権限を確認してください")
        st.write("3. 問題が続く場合は、管理者にお問い合わせください")
        
        # デバッグ情報
        with st.expander("🔧 デバッグ情報"):
            import traceback
            st.code(traceback.format_exc())

def show_match_progress_tab(player_service, match_service):
    """試合進行タブ"""
    st.markdown("# 🏆 試合進行")
    
    # プレイヤー状況を大きく表示
    active_players = player_service.get_active_players()
    participating_players = player_service.get_participating_players()
    resting_count = len(participating_players) - len(active_players)
    
    # 状況メトリクス（大きなフォント）
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("## 👥 参加者")
        st.markdown(f"### {len(participating_players)}人")
    with col2:
        st.markdown("## ⚡ 待機中")
        st.markdown(f"### {len(active_players)}人")
    with col3:
        st.markdown("## 💤 休憩中")
        st.markdown(f"### {resting_count}人")
    
    # 参加者一覧（テーブル形式）
    if participating_players:
        st.markdown("## 📋 参加者一覧")
        
        # 参加者を番号順で表示（テーブル形式）
        sorted_participants = sorted(participating_players, key=lambda p: p.player_number or 999)
        
        # テーブルヘッダー
        st.markdown("""
        <div style="
            background-color: #f0f2f6; 
            padding: 8px; 
            border-radius: 8px 8px 0 0; 
            border: 1px solid #ddd;
            font-weight: bold;
            display: grid;
            grid-template-columns: 60px 1fr 80px 80px 80px 80px 80px 80px;
            gap: 8px;
            align-items: center;
        ">
            <div style="text-align: center;">番号</div>
            <div>プレイヤー名</div>
            <div style="text-align: center;">レベル</div>
            <div style="text-align: center;">試合数</div>
            <div style="text-align: center;">勝数</div>
            <div style="text-align: center;">勝率</div>
            <div style="text-align: center;">状態</div>
            <div style="text-align: center;">休憩</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 各参加者の行
        for i, player in enumerate(sorted_participants):
            number_display = str(player.player_number) if player.player_number else "未"
            level_emoji = ["🔸", "🔹", "🟡", "🟠", "🔴"][player.level - 1]
            
            # 行の背景色（交互）
            bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
            
            # 休憩状態の表示
            status_icon = "💤" if player.is_resting else "⚡"
            status_text = "休憩中" if player.is_resting else "待機中"
            status_color = "#ff9800" if player.is_resting else "#4caf50"
            
            # 勝率の計算
            win_rate = (player.wins / player.matches_played * 100) if player.matches_played > 0 else 0
            
            # テーブル行
            st.markdown(f"""
            <div style="
                background-color: {bg_color}; 
                padding: 8px; 
                border-left: 1px solid #ddd;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
                display: grid;
                grid-template-columns: 60px 1fr 80px 80px 80px 80px 80px 80px;
                gap: 8px;
                align-items: center;
                min-height: 40px;
            ">
                <div style="
                    text-align: center; 
                    background-color: #4285f4; 
                    color: white; 
                    border-radius: 50%; 
                    width: 30px; 
                    height: 30px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-weight: bold; 
                    margin: 0 auto;
                ">
                    {number_display}
                </div>
                <div style="font-weight: bold; padding-left: 8px;">
                    {player.name}
                </div>
                <div style="text-align: center;">
                    {level_emoji}
                </div>
                <div style="text-align: center; font-weight: bold;">
                    {player.matches_played}
                </div>
                <div style="text-align: center; font-weight: bold;">
                    {player.wins}
                </div>
                <div style="text-align: center; font-weight: bold;">
                    {win_rate:.0f}%
                </div>
                <div style="text-align: center;">
                    <span style="color: {status_color}; font-weight: bold;">
                        {status_icon} {status_text}
                    </span>
                </div>
                <div style="text-align: center;" id="rest_btn_progress_{player.id}">
                    <!-- 休憩ボタンプレースホルダー -->
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ボタン用の列を作成
            cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
            
            with cols[7]:  # 休憩ボタン列
                rest_button_text = "復帰" if player.is_resting else "休憩"
                rest_button_icon = "⚡" if player.is_resting else "💤"
                rest_button_help = f"{player.name}を{'待機中に復帰' if player.is_resting else '休憩中に設定'}"
                
                if st.button(
                    f"{rest_button_icon}",
                    key=f"rest_progress_{player.id}",
                    help=rest_button_help,
                    use_container_width=True
                ):
                    new_resting = not player.is_resting
                    player_service.set_resting_status(player.id, new_resting)
                    action_text = "復帰" if not new_resting else "休憩"
                    st.success(f"✅ {player.name}を{action_text}させました")
                    st.rerun()
        
        # テーブルの下線
        st.markdown("""
        <div style="
            border-bottom: 1px solid #ddd;
            border-radius: 0 0 8px 8px;
            height: 1px;
        "></div>
        """, unsafe_allow_html=True)
        
        st.markdown("")  # 余白
        
        # 詳細統計
        st.markdown("### 📊 詳細統計")
        
        # 統計データの計算
        total_matches = sum(p.matches_played for p in participating_players)
        total_wins = sum(p.wins for p in participating_players)
        avg_matches = total_matches / len(participating_players) if participating_players else 0
        avg_wins = total_wins / len(participating_players) if participating_players else 0
        
        # レベル別統計
        level_counts = {}
        for player in participating_players:
            level_counts[player.level] = level_counts.get(player.level, 0) + 1
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("👥 総参加者", f"{len(participating_players)}人")
        with col_stat2:
            st.metric("⚡ 待機中", f"{len(active_players)}人")
        with col_stat3:
            st.metric("💤 休憩中", f"{resting_count}人")
        with col_stat4:
            st.metric("🎯 総試合数", f"{total_matches}試合")
        
        # 追加統計
        col_stat5, col_stat6, col_stat7, col_stat8 = st.columns(4)
        with col_stat5:
            st.metric("📊 平均試合数", f"{avg_matches:.1f}試合/人")
        with col_stat6:
            st.metric("🏆 平均勝数", f"{avg_wins:.1f}勝/人")
        with col_stat7:
            highest_level = max(level_counts.keys()) if level_counts else 0
            st.metric("⭐ 最高レベル", f"Lv.{highest_level}")
        with col_stat8:
            most_active = max(participating_players, key=lambda p: p.matches_played) if participating_players else None
            if most_active:
                st.metric("🔥 最多試合", f"{most_active.matches_played}試合")
            else:
                st.metric("🔥 最多試合", "0試合")
        
        # レベル分布
        if level_counts:
            st.markdown("#### 🎯 レベル分布")
            level_cols = st.columns(5)
            level_emojis = ["🔸", "🔹", "🟡", "🟠", "🔴"]
            
            for level in range(1, 6):
                with level_cols[level - 1]:
                    count = level_counts.get(level, 0)
                    emoji = level_emojis[level - 1]
                    st.metric(f"{emoji} Lv.{level}", f"{count}人")
    
    st.divider()
    
    # 設定セクション（簡素化）
    st.markdown("## ⚙️ 試合設定")
    
    col_courts, col_matches, col_skill = st.columns(3)
    with col_courts:
        num_courts = st.number_input(
            "🏓 コート数", 
            min_value=1, 
            max_value=MAX_COURTS, 
            value=DEFAULT_COURT_COUNT,
            key="num_courts"
        )
    
    with col_matches:
        num_matches = st.number_input(
            "🎾 試合数", 
            min_value=MIN_MATCHES_PER_GENERATION, 
            max_value=MAX_MATCHES_PER_GENERATION, 
            value=3,
            key="num_matches"
        )
    
    with col_skill:
        skill_matching = st.checkbox(
            "⚖️ スキルマッチング", 
            value=True,
            help="スキルバランスを考慮"
        )
    
    st.divider()
    
    # 試合生成ボタン（大きく）
    if st.button("🎯 試合を生成する", use_container_width=True, type="primary"):
        if len(active_players) < 4:
            st.error("⚠️ 試合を生成するには、待機中のプレイヤーが4人以上必要です。")
        else:
            # 前回の試合をクリア（新しいセッション開始）
            if st.session_state.get("clear_previous_matches", True):
                match_service.clear_session_matches()
                player_service.reset_session_stats()
                st.session_state["clear_previous_matches"] = False
            
            # 試合生成前にプレイヤー番号を確実に割り振り
            player_service.assign_player_numbers()
            
            # 最新のプレイヤーデータを取得
            updated_active_players = player_service.get_active_players()
            
            matches = match_service.generate_matches(
                updated_active_players, num_matches, num_courts, skill_matching
            )
            
            if matches:
                match_service.save_matches(matches)
                st.success(f"🎉 {len(matches)}試合を生成しました！")
                st.rerun()
            else:
                st.error("❌ 試合の生成に失敗しました。")
    
    # 新規試合のクリアボタン
    if st.button("🗑️ すべての試合をクリア", use_container_width=True, type="secondary"):
        if match_service.clear_session_matches():
            player_service.reset_session_stats()
            st.success("🗑️ すべての試合をクリアしました")
            st.rerun()
    
    st.divider()
    
    # デバッグ用番号再割り振りボタン
    if st.button("🔄 プレイヤー番号を再割り振り", help="試合に番号が正しく表示されない場合にクリック"):
        player_service.assign_player_numbers()
        st.success("プレイヤー番号を再割り振りしました！")
        st.rerun()
    
    # 現在の試合を表示
    current_matches = match_service.get_current_session_matches()
    
    if current_matches:        
        # 未完了試合
        incomplete_matches = [m for m in current_matches if not m.is_completed]
        completed_matches = [m for m in current_matches if m.is_completed]
        
        if incomplete_matches:
            st.markdown("## ⏳ 進行中の試合")
            for match in incomplete_matches:
                show_match_card(match, player_service, is_completed=False)
        
        # 完了済み試合を表示
        if completed_matches:
            st.markdown("## ✅ 完了済み試合")
            
            # リスト形式で表示
            for match in completed_matches:
                with st.container():
                    # プレイヤー番号の取得
                    all_players = player_service.get_all_players()
                    player_number_map = {p.id: p.player_number for p in all_players}
                    
                    def get_player_number_display(player_id):
                        number = player_number_map.get(player_id)
                        return str(number) if number is not None else "未"
                    
                    team1_numbers = [get_player_number_display(pid) for pid in match.team1_player_ids]
                    team2_numbers = [get_player_number_display(pid) for pid in match.team2_player_ids]
                    
                    # 勝者アイコン
                    winner_icon = "🏆" if match.winner_team == 1 else ("🏆" if match.winner_team == 2 else "🤝")
                    team1_style = "font-weight: bold; color: #4285f4;" if match.winner_team == 1 else "color: #666;"
                    team2_style = "font-weight: bold; color: #ea4335;" if match.winner_team == 2 else "color: #666;"
                    
                    # コンパクトな1行表示
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #ddd; 
                        border-radius: 8px; 
                        padding: 12px; 
                        margin: 4px 0;
                        background-color: #f8f9fa;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                    ">
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <div style="font-weight: bold; min-width: 80px;">
                                第{match.match_index}試合
                            </div>
                            <div style="min-width: 60px;">
                                コート{match.court_number}
                            </div>
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <span style="{team1_style}">
                                    {' & '.join([f'{n}番' for n in team1_numbers])}
                                </span>
                                <span style="font-size: 18px; font-weight: bold;">
                                    {match.team1_score} - {match.team2_score}
                                </span>
                                <span style="{team2_style}">
                                    {' & '.join([f'{n}番' for n in team2_numbers])}
                                </span>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 20px;">{winner_icon}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 編集・削除ボタン（小さく）
                    col_edit, col_delete, col_spacer = st.columns([1, 1, 8])
                    with col_edit:
                        if st.button("✏️", key=f"edit_completed_{match.id}", help="編集"):
                            st.session_state[f"editing_match_{match.id}"] = True
                            st.rerun()
                    with col_delete:
                        if st.button("🗑️", key=f"delete_completed_{match.id}", help="削除"):
                            show_delete_confirmation(match, player_service)
                    
                    # 編集モードの表示
                    if st.session_state.get(f"editing_match_{match.id}", False):
                        show_match_edit_form(match, player_service)
    else:
        st.info("📋 まだ試合が生成されていません。上のボタンから試合を生成してください。")

def show_match_card(match, player_service, is_completed=False):
    """試合カードを表示"""
    with st.container():
        # プレイヤー情報の取得
        all_players = player_service.get_all_players()
        player_number_map = {p.id: p.player_number for p in all_players}
        
        # 番号がNoneの場合は"未"と表示
        def get_player_number_display(player_id):
            number = player_number_map.get(player_id)
            return str(number) if number is not None else "未"
        
        team1_numbers = [get_player_number_display(pid) for pid in match.team1_player_ids]
        team2_numbers = [get_player_number_display(pid) for pid in match.team2_player_ids]
        
        # ヘッダー（試合番号とコート）
        col_header1, col_header2 = st.columns(2)
        with col_header1:
            st.markdown(f"### 🏓 第{match.match_index}試合")
        with col_header2:
            st.markdown(f"### 📍 コート{match.court_number}")
        
        st.divider()
        
        # チーム表示（番号のみ、枠付き）
        col_team1, col_vs, col_team2 = st.columns([2, 1, 2])
        
        with col_team1:
            st.markdown("#### 🔵 チーム1")
            for number in team1_numbers:
                st.markdown(f"""
                <div style="
                    border: 3px solid #4285f4; 
                    border-radius: 15px; 
                    padding: 15px; 
                    text-align: center; 
                    margin: 8px 0;
                    background-color: #e3f2fd;
                    display: inline-block;
                    min-width: 80px;
                ">
                    <div style="font-size: 28px; font-weight: bold; color: #1565c0;">
                        {number}番
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_vs:
            st.markdown("<div style='text-align: center; font-size: 24px; margin-top: 40px;'>⚡ VS ⚡</div>", unsafe_allow_html=True)
        
        with col_team2:
            st.markdown("#### 🔴 チーム2")
            for number in team2_numbers:
                st.markdown(f"""
                <div style="
                    border: 3px solid #ea4335; 
                    border-radius: 15px; 
                    padding: 15px; 
                    text-align: center; 
                    margin: 8px 0;
                    background-color: #ffebee;
                    display: inline-block;
                    min-width: 80px;
                ">
                    <div style="font-size: 28px; font-weight: bold; color: #c62828;">
                        {number}番
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # スコア表示（完了済みの場合のみ）
        if is_completed:
            st.divider()
            col_score1, col_score_vs, col_score2 = st.columns([2, 1, 2])
            
            with col_score1:
                st.markdown(f"<div style='text-align: center; font-size: 36px; font-weight: bold; color: #4285f4;'>{match.team1_score}</div>", unsafe_allow_html=True)
            
            with col_score_vs:
                st.markdown("<div style='text-align: center; font-size: 24px; margin-top: 8px;'>-</div>", unsafe_allow_html=True)
            
            with col_score2:
                st.markdown(f"<div style='text-align: center; font-size: 36px; font-weight: bold; color: #ea4335;'>{match.team2_score}</div>", unsafe_allow_html=True)
            
            # 勝者表示
            if match.winner_team == 1:
                st.success("🏆 チーム1の勝利！")
            elif match.winner_team == 2:
                st.success("🏆 チーム2の勝利！")
            else:
                st.info("🤝 引き分け")
        
        st.divider()
        
        # 操作ボタン
        if not is_completed:
            # 未完了試合の操作
            
            # スコア入力セクション
            show_score_input_section(match, player_service)
            
            # 編集・削除ボタン（縦に配置）
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{match.id}", use_container_width=True, help="編集"):
                    st.session_state[f"editing_match_{match.id}"] = True
                    st.rerun()
            with col_delete:
                if st.button("🗑️", key=f"delete_incomplete_{match.id}", use_container_width=True, type="secondary", help="削除"):
                    st.session_state[f"deleting_incomplete_{match.id}"] = True
                    st.rerun()
        else:
            # 完了済み試合の操作
            
            # 編集・削除ボタン（縦に配置）
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{match.id}", use_container_width=True, help="編集"):
                    st.session_state[f"editing_match_{match.id}"] = True
                    st.rerun()
            with col_delete:
                if st.button("🗑️", key=f"delete_{match.id}", use_container_width=True, help="削除"):
                    show_delete_confirmation(match, player_service)
        
        # 削除確認ダイアログ
        if st.session_state.get(f"deleting_incomplete_{match.id}", False):
            show_incomplete_match_delete_confirmation(match, player_service)
        
        # 編集モードの表示
        if st.session_state.get(f"editing_match_{match.id}", False):
            show_match_edit_form(match, player_service)

def show_participants_tab(player_service):
    """参加者タブ"""
    st.markdown("# 👥 参加者選択")
    
    players = player_service.get_all_players()
    
    if not players:
        st.info("まだプレイヤーが登録されていません。「⚙️管理」タブからプレイヤーを追加してください。")
        return
    
    # 参加者選択セクション
    st.markdown("## 🔍 参加者を追加")
    
    # 検索機能
    search_key = "participants_search_query"
    search_query = st.text_input("🔎 プレイヤーを検索して追加", placeholder="名前を入力してください...", key=search_key)
    
    # 検索候補を表示
    if search_query:
        # 検索にマッチするプレイヤー（参加者ではないもののみ）
        search_results = [p for p in players if search_query.lower() in p.name.lower() and not p.is_participating_today]
        # あいうえお順でソート
        search_results.sort(key=lambda p: p.name)
        
        if search_results:
            st.markdown("### 📋 検索結果（タップして追加）")
            for player in search_results[:5]:  # 上位5件まで表示
                level_emoji = ["🔸", "🔹", "🟡", "🟠", "🔴"][player.level - 1]
                if st.button(
                    f"{level_emoji} {player.name} (Lv.{player.level})",
                    key=f"add_search_{player.id}",
                    use_container_width=True,
                    help="タップして参加者に追加"
                ):
                    # プレイヤーを参加者に追加
                    player_service.set_participation_status(player.id, True)
                    # 番号を自動割り振り
                    player_service.assign_player_numbers()
                    st.success(f"✅ {player.name}を参加者に追加しました！")
                    # 検索クエリをクリア
                    st.session_state[search_key] = ""
                    st.rerun()
        else:
            if len(search_query) >= 1:
                st.info("🤷‍♂️ 該当するプレイヤーが見つからないか、既に参加者に追加済みです")
    
    # 検索クリアボタン
    if search_query:
        if st.button("🧹 検索をクリア", help="検索結果をクリアします", key="clear_participants_search"):
            st.session_state[search_key] = ""
            st.rerun()
    
    # 便利ボタン
    col_all, col_clear = st.columns(2)
    with col_all:
        if st.button("👥 全員を参加者に追加", use_container_width=True, key="add_all_participants_tab"):
            for player in players:
                player_service.set_participation_status(player.id, True)
            player_service.assign_player_numbers()
            st.success(f"✅ {len(players)}人全員を参加者に追加しました！")
            st.rerun()
    
    with col_clear:
        if st.button("🧹 全参加者をクリア", use_container_width=True, key="clear_all_participants_tab"):
            for player in players:
                player_service.set_participation_status(player.id, False)
            st.success("🧹 全参加者をクリアしました")
            st.rerun()
    
    # プレイヤー一覧からの選択
    non_participating_players = [p for p in players if not p.is_participating_today]
    # あいうえお順でソート
    non_participating_players.sort(key=lambda p: p.name)
    
    if non_participating_players:
        st.markdown(f"### 📋 全プレイヤー一覧から選択 ({len(non_participating_players)}人)")
        st.write("参加者になっていないプレイヤー一覧（複数選択可能）：")
        
        # 最近追加されたプレイヤーの成功メッセージ
        if "recently_added_player_tab" in st.session_state:
            st.success(f"✅ {st.session_state.recently_added_player_tab}を参加者に追加しました！")
            # メッセージを一度表示したら削除
            del st.session_state["recently_added_player_tab"]
        
        # 3列でプレイヤーボタンを表示
        cols = st.columns(3)
        for i, player in enumerate(non_participating_players):
            level_emoji = ["🔸", "🔹", "🟡", "🟠", "🔴"][player.level - 1]
            col_index = i % 3
            
            with cols[col_index]:
                if st.button(
                    f"{level_emoji} {player.name}",
                    key=f"add_list_tab_{player.id}",
                    use_container_width=True,
                    help=f"Lv.{player.level} | SP:{player.skill_points:.0f}"
                ):
                    player_service.set_participation_status(player.id, True)
                    player_service.assign_player_numbers()
                    # 成功メッセージをセッション状態に保存
                    st.session_state["recently_added_player_tab"] = player.name
                    st.rerun()
    else:
        st.info("👏 すべてのプレイヤーが参加者に追加されています！")
    
    st.divider()
    
    # 現在の参加者リスト（テーブル形式）
    participating_players = player_service.get_participating_players()
    
    if participating_players:
        st.markdown(f"## 👥 参加者一覧 ({len(participating_players)}人)")
        
        # 参加者を番号順で表示（テーブル形式）
        sorted_participants = sorted(participating_players, key=lambda p: p.player_number or 999)
        
        # テーブルヘッダー
        st.markdown("""
        <div style="
            background-color: #f0f2f6; 
            padding: 8px; 
            border-radius: 8px 8px 0 0; 
            border: 1px solid #ddd;
            font-weight: bold;
            display: grid;
            grid-template-columns: 80px 1fr 80px;
            gap: 8px;
            align-items: center;
        ">
            <div style="text-align: center;">番号</div>
            <div>プレイヤー名</div>
            <div style="text-align: center;">除外</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 各参加者の行
        for i, player in enumerate(sorted_participants):
            number_display = str(player.player_number) if player.player_number else "未"
            
            # 行の背景色（交互）
            bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
            
            # テーブル行
            st.markdown(f"""
            <div style="
                background-color: {bg_color}; 
                padding: 8px; 
                border-left: 1px solid #ddd;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
                display: grid;
                grid-template-columns: 80px 1fr 80px;
                gap: 8px;
                align-items: center;
                min-height: 40px;
            ">
                <div style="
                    text-align: center; 
                    background-color: #4285f4; 
                    color: white; 
                    border-radius: 50%; 
                    width: 30px; 
                    height: 30px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-weight: bold; 
                    margin: 0 auto;
                ">
                    {number_display}
                </div>
                <div style="font-weight: bold; padding-left: 8px;">
                    {player.name}
                </div>
                <div style="text-align: center;" id="remove_btn_tab_{player.id}">
                    <!-- 除外ボタンプレースホルダー -->
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ボタン用の列を作成
            cols = st.columns([1, 1, 1])
            
            with cols[2]:  # 除外ボタン列
                if st.button(
                    "❌",
                    key=f"remove_tab_{player.id}",
                    help=f"{player.name}を参加者から除外",
                    use_container_width=True
                ):
                    player_service.set_participation_status(player.id, False)
                    # 番号を再割り振り
                    player_service.assign_player_numbers()
                    st.success(f"🚪 {player.name}を参加者から除外しました")
                    st.rerun()
        
        # テーブルの下線
        st.markdown("""
        <div style="
            border-bottom: 1px solid #ddd;
            border-radius: 0 0 8px 8px;
            height: 1px;
        "></div>
        """, unsafe_allow_html=True)
        
        st.markdown("")  # 余白
        
        # 参加者統計
        st.markdown("### 📊 参加者統計")
        active_count = len([p for p in participating_players if not p.is_resting])
        resting_count = len([p for p in participating_players if p.is_resting])
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("👥 総参加者", f"{len(participating_players)}人")
        with col_stat2:
            st.metric("⚡ 待機中", f"{active_count}人")
        with col_stat3:
            st.metric("💤 休憩中", f"{resting_count}人")
    else:
        st.info("参加者が選択されていません。上記から参加者を選択してください。")

def show_ranking_tab(player_service):
    """ランキングタブ"""
    st.markdown("# 📊 ランキング")
    
    participating_players = player_service.get_participating_players()
    
    if not participating_players:
        st.info("🤷‍♂️ 参加者がいません。「👥参加者」タブでプレイヤーを選択してください。")
        return
    
    # ランキング種類の選択（大きく）
    st.markdown("## 📈 ランキング基準を選択")
    ranking_type = st.selectbox(
        "ランキング基準",
        ["🏆 勝率ランキング", "⭐ スキルポイントランキング"],
        key="ranking_type",
        label_visibility="collapsed"
    )
    
    if "勝率" in ranking_type:
        ranked_players = player_service.get_ranking_by_winrate()
        main_metric = "勝率"
        main_icon = "🏆"
    else:
        ranked_players = player_service.get_ranking_by_skill()
        main_metric = "スキルポイント"
        main_icon = "⭐"
    
    st.divider()
    
    # ランキング表示（大きなフォント）
    st.markdown(f"## {main_icon} {main_metric}ランキング")
    
    for i, player in enumerate(ranked_players, 1):
        # 順位のメダル・アイコン表示
        if i == 1:
            rank_display = "🥇 1位"
            card_color = "#FFD700"
        elif i == 2:
            rank_display = "🥈 2位"  
            card_color = "#C0C0C0"
        elif i == 3:
            rank_display = "🥉 3位"
            card_color = "#CD7F32"
        else:
            rank_display = f"🔸 {i}位"
            card_color = "#f8f9fa"
        
        # プレイヤーカード
        with st.container():
            st.markdown(f"""
            <div style="
                background: {card_color}; 
                border: 2px solid #dee2e6; 
                border-radius: 12px; 
                padding: 16px; 
                margin: 12px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
            </div>
            """, unsafe_allow_html=True)
            
            # プレイヤー情報（大きなフォント）
            level_emoji = ["🔸", "🔹", "🟡", "🟠", "🔴"][player.level - 1]
            status_icon = "💤" if player.is_resting else "⚡"
            
            st.markdown(f"## {rank_display} {player.player_number}番 {level_emoji} {player.name} {status_icon}")
            
            # 統計情報を2列で表示
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                ### 🎯 試合成績
                - **試合数**: {player.matches_played}試合
                - **勝数**: {player.wins}勝
                - **勝率**: {player.win_rate:.1%}
                """)
            
            with col2:
                st.markdown(f"""
                ### ⭐ スキル情報
                - **レベル**: Lv.{player.level}
                - **ポイント**: {player.skill_points:.0f}pt
                - **状態**: {"休憩中" if player.is_resting else "待機中"}
                """)
            
            st.divider()

def show_management_tab():
    """管理タブ"""
    st.subheader("⚙️ システム管理")
    
    # サブページの選択
    management_option = st.selectbox(
        "管理項目",
        ["プレイヤー管理", "試合履歴", "データ管理"],
        key="management_option"
    )
    
    if management_option == "プレイヤー管理":
        show_user_management()
    elif management_option == "試合履歴":
        show_match_history()
    elif management_option == "データ管理":
        show_data_management()

def show_data_management():
    """データ管理セクション"""
    st.subheader("💾 データ管理")
    
    player_service = PlayerService()
    match_service = MatchService()
    
    # 統計情報
    players = player_service.get_all_players()
    matches = match_service.get_all_matches()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総プレイヤー数", len(players))
    with col2:
        st.metric("総試合数", len(matches))
    with col3:
        completed_matches = len([m for m in matches if m.is_completed])
        st.metric("完了試合数", completed_matches)
    
    st.divider()
    
    # データリセット
    st.subheader("🗑️ データリセット")
    st.warning("⚠️ 以下の操作は取り消しできません。慎重に実行してください。")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 セッションリセット", use_container_width=True):
            match_service.clear_session_matches()
            player_service.reset_session_stats()
            st.success("セッションデータをリセットしました")
            st.rerun()
    
    with col2:
        if st.button("⚠️ 全データリセット", use_container_width=True):
            st.session_state["confirm_reset_all_data"] = True
            st.rerun()
    
    # データリセット確認
    if st.session_state.get("confirm_reset_all_data", False):
        st.divider()
        st.error("🚨 **全データリセット確認**")
        st.write("この操作により以下のデータがすべて削除されます：")
        st.write("- すべてのプレイヤー情報")
        st.write("- すべての試合履歴")
        st.write("- すべてのスキルポイント・統計")
        st.write("**この操作は取り消すことができません！**")
        
        col_confirm, col_cancel = st.columns(2)
        
        with col_confirm:
            if st.button("🗑️ 完全にリセットする", key="final_reset_confirm", use_container_width=True):
                # データマネージャーを使用してデータをリセット
                from utils.data_manager import DataManager
                data_manager = DataManager()
                
                # 空のデータ構造で初期化
                empty_data = {
                    "players": [],
                    "matches": [],
                    "session_data": {
                        "current_match_index": 0,
                        "participating_players": []
                    }
                }
                
                if data_manager.save_data(empty_data):
                    st.session_state["confirm_reset_all_data"] = False
                    st.success("🎉 全データをリセットしました！アプリを再読み込みしてください。")
                    # セッション状態もクリア
                    for key in list(st.session_state.keys()):
                        if key.startswith(("editing_", "deleting_", "clear_")):
                            del st.session_state[key]
                    st.rerun()
                else:
                    st.error("❌ リセットに失敗しました")
        
        with col_cancel:
            if st.button("❌ キャンセル", key="cancel_reset_confirm", use_container_width=True):
                st.session_state["confirm_reset_all_data"] = False
                st.rerun()

if __name__ == "__main__":
    main() 