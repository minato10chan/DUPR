from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class Match(BaseModel):
    id: str
    match_index: int
    court_number: int
    team1_player_ids: List[str]
    team2_player_ids: List[str]
    team1_score: int = 0
    team2_score: int = 0
    is_completed: bool = False
    completed_at: Optional[str] = None

    @classmethod
    def create_new(cls, match_index: int, court_number: int, 
                   team1_player_ids: List[str], team2_player_ids: List[str]) -> "Match":
        """新しい試合を作成"""
        return cls(
            id=str(uuid.uuid4()),
            match_index=match_index,
            court_number=court_number,
            team1_player_ids=team1_player_ids,
            team2_player_ids=team2_player_ids
        )

    def complete_match(self, team1_score: int, team2_score: int):
        """試合を完了する"""
        self.team1_score = team1_score
        self.team2_score = team2_score
        self.is_completed = True
        self.completed_at = datetime.now().isoformat()

    @property
    def winner_team(self) -> Optional[int]:
        """勝利チームを返す（1 or 2、引き分けの場合はNone）"""
        if not self.is_completed:
            return None
        if self.team1_score > self.team2_score:
            return 1
        elif self.team2_score > self.team1_score:
            return 2
        return None

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        """辞書から作成"""
        return cls(**data) 