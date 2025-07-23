import random
import itertools
from typing import List, Tuple, Dict, Any
from models.player import Player
from models.match import Match

class TournamentScheduler:
    def __init__(self, players: List[Player], skill_matching_enabled: bool = True):
        self.players = players
        self.skill_matching_enabled = skill_matching_enabled
        # 過去のペア対戦記録（プレイヤーIDの組み合わせ -> 対戦回数）
        self.pair_history: Dict[Tuple[str, str], int] = {}

    def update_pair_history(self, matches: List[Match]):
        """過去の試合からペア対戦履歴を更新"""
        self.pair_history.clear()
        for match in matches:
            if match.is_completed:
                # チーム1のペア
                team1_pair = tuple(sorted(match.team1_player_ids))
                # チーム2のペア
                team2_pair = tuple(sorted(match.team2_player_ids))
                
                # ペア対戦回数を記録
                self.pair_history[team1_pair] = self.pair_history.get(team1_pair, 0) + 1
                self.pair_history[team2_pair] = self.pair_history.get(team2_pair, 0) + 1

    def generate_matches(self, num_matches: int, num_courts: int) -> List[Match]:
        """指定された数の試合を生成"""
        # 参加可能なプレイヤーをフィルタリング
        available_players = [p for p in self.players 
                           if p.is_participating_today and not p.is_resting]
        
        if len(available_players) < 4:
            return []  # プレイヤー不足

        # 試合数でソート（少ない順）
        available_players.sort(key=lambda p: p.matches_played)
        
        matches = []
        current_match_index = 1
        
        for match_num in range(num_matches):
            court_number = (match_num % num_courts) + 1
            
            # プレイヤー選定（試合数が少ない順に4人）
            selected_players = self._select_players_for_match(available_players)
            
            if len(selected_players) < 4:
                break  # プレイヤー不足で終了
            
            # チーム分割の最適化
            team_split = self._optimize_team_split(selected_players)
            
            if team_split:
                team1_ids = [p.id for p in team_split[0]]
                team2_ids = [p.id for p in team_split[1]]
                
                match = Match.create_new(
                    match_index=current_match_index,
                    court_number=court_number,
                    team1_player_ids=team1_ids,
                    team2_player_ids=team2_ids
                )
                matches.append(match)
                current_match_index += 1
                
                # 選ばれたプレイヤーの試合数を更新
                for player in selected_players:
                    player.matches_played += 1
        
        return matches

    def _select_players_for_match(self, available_players: List[Player]) -> List[Player]:
        """試合用のプレイヤーを選択"""
        # 試合数が最も少ないプレイヤーから4人を選択
        min_matches = min(p.matches_played for p in available_players)
        candidates = [p for p in available_players if p.matches_played == min_matches]
        
        if len(candidates) >= 4:
            # 同じ試合数の中からランダムに4人選択
            return random.sample(candidates, 4)
        else:
            # 足りない分は次の試合数レベルから選択
            selected = candidates.copy()
            remaining_players = [p for p in available_players if p not in selected]
            needed = 4 - len(selected)
            
            if len(remaining_players) >= needed:
                selected.extend(remaining_players[:needed])
            
            return selected

    def _optimize_team_split(self, players: List[Player]) -> Tuple[List[Player], List[Player]]:
        """4人のプレイヤーを最適にチーム分割"""
        if len(players) != 4:
            return None
        
        p1, p2, p3, p4 = players
        
        # 3つのパターンを生成
        patterns = [
            ([p1, p2], [p3, p4]),  # パターンA
            ([p1, p3], [p2, p4]),  # パターンB  
            ([p1, p4], [p2, p3]),  # パターンC
        ]
        
        best_pattern = None
        best_score = float('inf')
        
        for pattern in patterns:
            score = self._evaluate_team_split(pattern[0], pattern[1])
            if score < best_score:
                best_score = score
                best_pattern = pattern
        
        return best_pattern

    def _evaluate_team_split(self, team1: List[Player], team2: List[Player]) -> float:
        """チーム分割の評価スコアを計算"""
        if self.skill_matching_enabled:
            # スキルバランスを重視
            team1_skill = sum(p.skill_points for p in team1) / len(team1)
            team2_skill = sum(p.skill_points for p in team2) / len(team2)
            skill_diff = abs(team1_skill - team2_skill)
            
            # ペア重複も考慮（副次的）
            team1_pair = tuple(sorted([p.id for p in team1]))
            team2_pair = tuple(sorted([p.id for p in team2]))
            pair_count = self.pair_history.get(team1_pair, 0) + self.pair_history.get(team2_pair, 0)
            
            return skill_diff + pair_count * 0.1  # スキル差を主、ペア重複を副とする
        else:
            # ペア重複回避を重視
            team1_pair = tuple(sorted([p.id for p in team1]))
            team2_pair = tuple(sorted([p.id for p in team2]))
            return self.pair_history.get(team1_pair, 0) + self.pair_history.get(team2_pair, 0)

    def generate_fallback_matches(self, num_matches: int, num_courts: int) -> List[Match]:
        """フォールバック用のランダム試合生成"""
        available_players = [p for p in self.players 
                           if p.is_participating_today and not p.is_resting]
        
        if len(available_players) < 4:
            return []
        
        matches = []
        current_match_index = 1
        
        for match_num in range(num_matches):
            court_number = (match_num % num_courts) + 1
            
            # ランダムに4人選択
            selected = random.sample(available_players, 4)
            random.shuffle(selected)
            
            team1_ids = [selected[0].id, selected[1].id]
            team2_ids = [selected[2].id, selected[3].id]
            
            match = Match.create_new(
                match_index=current_match_index,
                court_number=court_number,
                team1_player_ids=team1_ids,
                team2_player_ids=team2_ids
            )
            matches.append(match)
            current_match_index += 1
        
        return matches 