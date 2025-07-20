from typing import Dict, List
from models.player import Player
from models.match import Match
from utils.data_manager import save_data
from utils.match_generator import generate_matches

class MatchService:
    def __init__(self, players: Dict[str, Player], matches: List[Match]):
        self.players = players
        self.matches = matches
    
    def create_new_matches(self, court_count: int, match_count: int, skill_matching: bool) -> List[Match]:
        """新しい試合を生成"""
        return generate_matches(self.players, self.matches, court_count, match_count, skill_matching)
    
    def complete_match(self, match: Match, team1_score: int, team2_score: int) -> None:
        """試合を完了し、結果を記録"""
        match.complete(team1_score, team2_score)
        
        # プレイヤーの統計を更新
        for player_name in match.team1:
            player = self.players[player_name]
            player.add_match_result(team1_score, team2_score, team1_score > team2_score)
            player.last_match_index = match.match_index
        
        for player_name in match.team2:
            player = self.players[player_name]
            player.add_match_result(team2_score, team1_score, team2_score > team1_score)
            player.last_match_index = match.match_index
        
        # 完了した試合を履歴に追加
        self.matches.append(match)
        
        # データを保存
        self._save_data()
    
    def get_match_history(self) -> List[Dict]:
        """試合履歴を取得"""
        history_data = []
        for match in self.matches:
            if match.is_completed:
                history_data.append({
                    'コート': match.court,
                    'チーム1': ', '.join(match.team1),
                    'チーム2': ', '.join(match.team2),
                    'スコア': f"{match.team1_score} - {match.team2_score}",
                    '勝者': ', '.join(match.winner)
                })
        return history_data
    
    def get_completed_matches_count(self) -> int:
        """完了した試合数を取得"""
        return len([m for m in self.matches if m.is_completed])
    
    def _save_data(self) -> None:
        """データを保存"""
        save_data(self.players, self.matches) 