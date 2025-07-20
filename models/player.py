from typing import Dict, Any
from config.settings import MIN_LEVEL, MAX_LEVEL, DEFAULT_LEVEL

class Player:
    def __init__(self, name: str, level: int = DEFAULT_LEVEL):
        self.name = name
        self.level = max(MIN_LEVEL, min(MAX_LEVEL, level))
        self.matches_played = 0
        self.wins = 0
        self.total_points_scored = 0
        self.total_points_conceded = 0
        self.is_resting = False
        self.last_match_index = -1  # 連続試合回避用
    
    @property
    def win_rate(self) -> float:
        """勝率を計算"""
        return self.wins / self.matches_played if self.matches_played > 0 else 0.0
    
    @property
    def point_ratio(self) -> float:
        """得失点比率を計算"""
        return self.total_points_scored / max(self.total_points_conceded, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'name': self.name,
            'level': self.level,
            'matches_played': self.matches_played,
            'wins': self.wins,
            'total_points_scored': self.total_points_scored,
            'total_points_conceded': self.total_points_conceded,
            'is_resting': self.is_resting,
            'last_match_index': self.last_match_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """辞書から復元"""
        player = cls(data['name'], data['level'])
        player.matches_played = data['matches_played']
        player.wins = data['wins']
        player.total_points_scored = data['total_points_scored']
        player.total_points_conceded = data['total_points_conceded']
        player.is_resting = data['is_resting']
        player.last_match_index = data['last_match_index']
        return player
    
    def update_level(self, new_level: int) -> None:
        """レベルを更新"""
        self.level = max(MIN_LEVEL, min(MAX_LEVEL, new_level))
    
    def add_match_result(self, points_scored: int, points_conceded: int, is_winner: bool) -> None:
        """試合結果を追加"""
        self.matches_played += 1
        self.total_points_scored += points_scored
        self.total_points_conceded += points_conceded
        if is_winner:
            self.wins += 1
    
    def toggle_rest_status(self) -> None:
        """休憩状態を切り替え"""
        self.is_resting = not self.is_resting 