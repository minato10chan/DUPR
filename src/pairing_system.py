"""
ペアリングシステムモジュール
ペア作成と対戦カード生成を担当
"""

import streamlit as st
from typing import List, Dict, Tuple, Set


class PairingSystem:
    """ペアリングシステムクラス"""
    
    def __init__(self):
        pass
    
    def get_pair_key(self, player1: str, player2: str) -> str:
        """ペアのキーを生成"""
        return f"{min(player1, player2)}_{max(player1, player2)}"
    
    def get_match_key(self, player1: str, player2: str, player3: str, player4: str) -> str:
        """対戦のキーを生成"""
        team1 = f"{min(player1, player2)}_{max(player1, player2)}"
        team2 = f"{min(player3, player4)}_{max(player3, player4)}"
        return f"{min(team1, team2)}_{max(team1, team2)}"
    
    def create_pairs(self, participants: List[Dict], consider_level: bool = False) -> List[Tuple[str, str]]:
        """ペア作成"""
        if len(participants) < 4:
            return []
        
        # ステータスを考慮してアクティブな参加者のみを取得
        active_participants = [p for p in participants if p.get('status') == 'active' and p.get('active', True)]
        if len(active_participants) < 4:
            return []
        
        # レベル考慮モードの場合
        if consider_level:
            from src.rating_system import RatingSystem
            rating_system = RatingSystem()
            groups = rating_system.group_by_rating(active_participants)
            
            pairs = []
            for group in groups.values():
                if len(group) >= 4:
                    # グループ内でペア作成
                    group_pairs = self._create_pairs_for_group(group)
                    pairs.extend(group_pairs)
            
            return pairs
        
        # 通常モード
        return self._create_pairs_for_group(active_participants)
    
    def _create_pairs_for_group(self, participants: List[Dict]) -> List[Tuple[str, str]]:
        """グループ内でのペア作成（多様性を重視）"""
        if len(participants) < 4:
            return []
        
        # 各プレイヤーのペア履歴を取得
        player_pair_counts = {}
        for p in participants:
            player_pair_counts[p['name']] = {}
            for other in participants:
                if other['name'] != p['name']:
                    pair_key = self.get_pair_key(p['name'], other['name'])
                    count = st.session_state.pair_history.get(pair_key, 0)
                    player_pair_counts[p['name']][other['name']] = count
        
        # 最近のラウンドでのペア履歴を取得（直近3ラウンド）
        recent_pair_history = self._get_recent_pair_history(3)
        
        # バイ履歴を考慮
        bye_counts = {}
        for p in participants:
            bye_counts[p['name']] = st.session_state.bye_history.get(p['name'], 0)
        
        # 多様性を最大化するペア作成
        pairs = []
        used = set()
        
        # バイ履歴が多い人を優先
        sorted_by_bye = sorted(participants, key=lambda p: bye_counts[p['name']], reverse=True)
        
        for player in sorted_by_bye:
            if player['name'] in used:
                continue
            
            # 最適なパートナーを選択
            best_partner = self._find_best_partner(
                player, 
                [p for p in participants if p['name'] not in used and p['name'] != player['name']],
                player_pair_counts,
                recent_pair_history
            )
            
            if best_partner:
                pairs.append((player['name'], best_partner['name']))
                used.add(player['name'])
                used.add(best_partner['name'])
        
        return pairs
    
    def _find_best_partner(self, player: Dict, candidates: List[Dict], 
                          player_pair_counts: Dict, recent_pair_history: Set) -> Dict:
        """最適なパートナーを見つける"""
        if not candidates:
            return None
        
        best_partner = None
        best_score = float('inf')
        
        for candidate in candidates:
            score = self._calculate_pair_score(
                player, candidate, player_pair_counts, recent_pair_history
            )
            
            if score < best_score:
                best_score = score
                best_partner = candidate
        
        return best_partner
    
    def _calculate_pair_score(self, player1: Dict, player2: Dict, 
                            player_pair_counts: Dict, recent_pair_history: Set) -> float:
        """ペアのスコアを計算（低いほど良い）"""
        pair_key = self.get_pair_key(player1['name'], player2['name'])
        
        # 基本スコア：ペア回数
        base_score = player_pair_counts[player1['name']][player2['name']] * 10        
        # 最近のペア履歴ペナルティ
        recent_penalty = 0
        if pair_key in recent_pair_history:
            recent_penalty = 50  # 最近ペアを組んだ場合は大きなペナルティ
        
        # レーティング差ペナルティ（レベル考慮）
        rating_diff = abs(player1['rating'] - player2['rating'])
        rating_penalty = rating_diff * 0.1        
        # 総合スコア
        total_score = base_score + recent_penalty + rating_penalty
        
        return total_score
    
    def _get_recent_pair_history(self, rounds_back: int) -> Set[str]:
        """最近のラウンドでのペア履歴を取得"""
        recent_pairs = set()
        
        if not st.session_state.rounds:
            return recent_pairs
        
        # 最近のラウンドからペア履歴を取得
        recent_rounds = st.session_state.rounds[-rounds_back:] if len(st.session_state.rounds) >= rounds_back else st.session_state.rounds
        
        for round_data in recent_rounds:
            for match in round_data['matches']:
                # チーム1のペア
                pair_key1 = self.get_pair_key(match['team1'][0], match['team1'][1])
                recent_pairs.add(pair_key1)
                
                # チーム2のペア
                pair_key2 = self.get_pair_key(match['team2'][0], match['team2'][1])
                recent_pairs.add(pair_key2)
        
        return recent_pairs
    
    def create_matches(self, pairs: List[Tuple[str, str]], court_count: int) -> List[Dict]:
        """対戦カード作成（多様性を重視）"""
        if len(pairs) < 2:
            return []
        
        # 最近の対戦履歴を取得
        recent_match_history = self._get_recent_match_history(3)
        
        matches = []
        used_pairs = set()
        
        # 対戦履歴が少ないペアを優先して対戦を作成
        while len(pairs) >= 2:
            best_team1 = None
            best_team2 = None
            best_score = float('inf')
            
            # 最適な対戦組み合わせを見つける
            for i, team1 in enumerate(pairs):
                if team1 in used_pairs:
                    continue
                    
                for j, team2 in enumerate(pairs[i+1:], i+1):
                    if team2 in used_pairs:
                        continue
                    
                    score = self._calculate_match_score(team1, team2, recent_match_history)
                    
                    if score < best_score:
                        best_score = score
                        best_team1 = team1
                        best_team2 = team2
            
            if best_team1 and best_team2:
                # 対戦履歴をチェック
                match_key = self.get_match_key(best_team1[0], best_team1[1], best_team2[0], best_team2[1])
                match_count = st.session_state.match_history.get(match_key, 0)
                
                matches.append({
                    'team1': best_team1,
                    'team2': best_team2,
                    'score1': 0,
                    'score2': 0,
                    'winner': None,
                    'court': (len(matches) % court_count) + 1,
                    'match_count': match_count
                })
                
                used_pairs.add(best_team1)
                used_pairs.add(best_team2)
                
                # 使用済みペアをリストから削除
                pairs = [p for p in pairs if p not in [best_team1, best_team2]]
            else:
                break
        
        return matches
    
    def _calculate_match_score(self, team1: Tuple[str, str], team2: Tuple[str, str], 
                             recent_match_history: Set[str]) -> float:
        """対戦のスコアを計算（低いほど良い）"""
        match_key = self.get_match_key(team1[0], team1[1], team2[0], team2[1])
        
        # 基本スコア：対戦回数
        base_score = st.session_state.match_history.get(match_key, 0)
        # 最近の対戦履歴ペナルティ
        recent_penalty = 0
        if match_key in recent_match_history:
            recent_penalty = 100  # 最近対戦した場合は大きなペナルティ
        
        # 総合スコア
        total_score = base_score + recent_penalty
        
        return total_score
    
    def _get_recent_match_history(self, rounds_back: int) -> Set[str]:
        """最近のラウンドでの対戦履歴を取得"""
        recent_matches = set()
        
        if not st.session_state.rounds:
            return recent_matches
        
        # 最近のラウンドから対戦履歴を取得
        recent_rounds = st.session_state.rounds[-rounds_back:] if len(st.session_state.rounds) >= rounds_back else st.session_state.rounds
        
        for round_data in recent_rounds:
            for match in round_data['matches']:
                match_key = self.get_match_key(
                    match['team1'][0], match['team1'][1],
                    match['team2'][0], match['team2'][1]
                )
                recent_matches.add(match_key)
        
        return recent_matches
    
    def update_histories(self, matches: List[Dict]) -> None:
        """履歴を更新"""
        for match in matches:
            # ペア履歴を更新
            pair_key1 = self.get_pair_key(match['team1'][0], match['team1'][1])
            pair_key2 = self.get_pair_key(match['team2'][0], match['team2'][1])
            
            st.session_state.pair_history[pair_key1] = st.session_state.pair_history.get(pair_key1, 0) + 1
            st.session_state.pair_history[pair_key2] = st.session_state.pair_history.get(pair_key2, 0) + 1
            
            # 対戦履歴を更新
            match_key = self.get_match_key(match['team1'][0], match['team1'][1], match['team2'][0], match['team2'][1])
            st.session_state.match_history[match_key] = st.session_state.match_history.get(match_key, 0) + 1
    
    def update_bye_history(self, matches: List[Dict], participants: List[Dict]) -> None:
        """バイ履歴を更新"""
        active_names = set()
        for match in matches:
            active_names.update(match['team1'])
            active_names.update(match['team2'])
        
        for participant in participants:
            # ステータスを考慮してアクティブな参加者のみをチェック
            if (participant.get('status') == 'active' and 
                participant.get('active', True) and 
                participant['name'] not in active_names):
                st.session_state.bye_history[participant['name']] = st.session_state.bye_history.get(participant['name'], 0) + 1 