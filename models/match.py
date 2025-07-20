from typing import List, Dict, Any, Optional

class Match:
    def __init__(self, team1: List[str], team2: List[str], court: int, match_index: Optional[int] = None):
        self.team1 = team1
        self.team2 = team2
        self.court = court
        self.team1_score = 0
        self.team2_score = 0
        self.is_completed = False
        self.match_index = match_index if match_index is not None else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'team1': self.team1,
            'team2': self.team2,
            'court': self.court,
            'team1_score': self.team1_score,
            'team2_score': self.team2_score,
            'is_completed': self.is_completed,
            'match_index': self.match_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Match':
        """辞書から復元"""
        match = cls(data['team1'], data['team2'], data['court'])
        match.team1_score = data['team1_score']
        match.team2_score = data['team2_score']
        match.is_completed = data['is_completed']
        match.match_index = data['match_index']
        return match
    
    def complete(self, team1_score: int, team2_score: int) -> None:
        """試合を完了"""
        self.team1_score = team1_score
        self.team2_score = team2_score
        self.is_completed = True
    
    @property
    def winner(self) -> List[str]:
        """勝者チームを取得"""
        return self.team1 if self.team1_score > self.team2_score else self.team2
    
    @property
    def loser(self) -> List[str]:
        """敗者チームを取得"""
        return self.team2 if self.team1_score > self.team2_score else self.team1
    
    def get_team_score(self, team: List[str]) -> int:
        """指定チームのスコアを取得"""
        if team == self.team1:
            return self.team1_score
        elif team == self.team2:
            return self.team2_score
        return 0 