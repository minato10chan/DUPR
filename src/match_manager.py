"""
試合管理モジュール
試合結果記録とラウンド管理を担当
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
from src.data_manager import DataManager


class MatchManager:
    """試合管理クラス"""
    
    def __init__(self):
        self.data_manager = DataManager()
    
    def generate_rounds(self, round_count: int, court_count: int, consider_level: bool = False) -> bool:
        """ラウンド生成"""
        if not st.session_state.current_participants:
            return False
        
        from src.pairing_system import PairingSystem
        pairing_system = PairingSystem()
        
        for round_num in range(1, round_count + 1):
            pairs = pairing_system.create_pairs(st.session_state.current_participants, consider_level)
            matches = pairing_system.create_matches(pairs, court_count)
            
            if matches:
                round_data = {
                    'round': round_num,
                    'matches': matches,
                    'completed': False,
                    'created_at': datetime.now().isoformat()
                }
                st.session_state.rounds.append(round_data)
                
                # 履歴を更新
                pairing_system.update_histories(matches)
                pairing_system.update_bye_history(matches, st.session_state.current_participants)
        
        self.data_manager.save_data()
        return True
    
    def record_match_result(self, round_idx: int, match_idx: int, score1: int, score2: int) -> None:
        """試合結果記録"""
        if round_idx >= len(st.session_state.rounds):
            return
        
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
        self._update_user_stats(match)
        
        self.data_manager.save_data()
    
    def _update_user_stats(self, match: Dict) -> None:
        """ユーザーの戦績を更新"""
        team1_players = [match['team1'][0], match['team1'][1]]
        team2_players = [match['team2'][0], match['team2'][1]]
        
        if match['winner'] == 'team1':
            for player_name in team1_players:
                self._update_user_win(player_name)
            for player_name in team2_players:
                self._update_user_loss(player_name)
        elif match['winner'] == 'team2':
            for player_name in team2_players:
                self._update_user_win(player_name)
            for player_name in team1_players:
                self._update_user_loss(player_name)
        else:
            # 引き分けの場合
            for player_name in team1_players + team2_players:
                self._update_user_loss(player_name)
    
    def _update_user_win(self, player_name: str) -> None:
        """ユーザーの勝利を記録"""
        for user in st.session_state.users:
            if user['name'] == player_name:
                user['wins'] += 1
                user['total_matches'] += 1
                break
    
    def _update_user_loss(self, player_name: str) -> None:
        """ユーザーの敗北を記録"""
        for user in st.session_state.users:
            if user['name'] == player_name:
                user['total_matches'] += 1
                break
    
    def complete_round(self, round_idx: int) -> None:
        """ラウンドを完了にする"""
        if 0 <= round_idx < len(st.session_state.rounds):
            st.session_state.rounds[round_idx]['completed'] = True
            self.data_manager.save_data()
    
    def delete_round(self, round_idx: int) -> None:
        """ラウンドを削除"""
        if 0 <= round_idx < len(st.session_state.rounds):
            st.session_state.rounds.pop(round_idx)
            self.data_manager.save_data()
    
    def get_round_summary(self) -> Dict:
        """ラウンド概要を取得"""
        total_rounds = len(st.session_state.rounds)
        completed_rounds = sum(1 for r in st.session_state.rounds if r['completed'])
        total_matches = sum(len(r['matches']) for r in st.session_state.rounds)
        completed_matches = sum(
            sum(1 for m in r['matches'] if m['winner'] is not None)
            for r in st.session_state.rounds
        )
        
        return {
            'total_rounds': total_rounds,
            'completed_rounds': completed_rounds,
            'total_matches': total_matches,
            'completed_matches': completed_matches
        } 
    
    def regenerate_rounds_for_participant_changes(self, court_count: int, consider_level: bool = False) -> bool:
        """参加者変更時のラウンド再生成"""
        if not st.session_state.current_participants:
            return False
        
        # アクティブな参加者数を確認
        active_participants = [p for p in st.session_state.current_participants 
                             if p.get('status') == 'active' and p.get('active', True)]
        
        if len(active_participants) < 4:
            st.error("アクティブな参加者が4人未満です。ラウンドを生成できません。")
            return False
        
        # 完了していないラウンドを削除
        incomplete_rounds = [r for r in st.session_state.rounds if not r['completed']]
        for round_data in incomplete_rounds:
            st.session_state.rounds.remove(round_data)
        
        # 新しいラウンドを生成
        from src.pairing_system import PairingSystem
        pairing_system = PairingSystem()
        
        # 残りのラウンド数を計算（完了済みラウンドを除く）
        remaining_rounds = 3 - len([r for r in st.session_state.rounds if r['completed']])
        
        for round_num in range(1, remaining_rounds + 1):
            pairs = pairing_system.create_pairs(st.session_state.current_participants, consider_level)
            matches = pairing_system.create_matches(pairs, court_count)
            
            if matches:
                round_data = {
                    'round': len(st.session_state.rounds) + 1,
                    'matches': matches,
                    'completed': False,
                    'created_at': datetime.now().isoformat(),
                    'regenerated': True  # 再生成フラグ
                }
                st.session_state.rounds.append(round_data)
                
                # 履歴を更新
                pairing_system.update_histories(matches)
                pairing_system.update_bye_history(matches, st.session_state.current_participants)
        
        self.data_manager.save_data()
        return True
    
    def get_active_participants_count(self) -> int:
        """アクティブな参加者数を取得"""
        return len([p for p in st.session_state.current_participants 
                   if p.get('status') == 'active' and p.get('active', True)])
    
    def get_participant_status_summary(self) -> Dict:
        """参加者ステータス概要を取得"""
        total = len(st.session_state.current_participants)
        active = len([p for p in st.session_state.current_participants 
                     if p.get('status') == 'active'])
        inactive = len([p for p in st.session_state.current_participants 
                       if p.get('status') == 'inactive'])
        left = len([p for p in st.session_state.current_participants 
                   if p.get('status') == 'left'])
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'left': left
        } 