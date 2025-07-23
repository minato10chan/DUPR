from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class Player(BaseModel):
    id: str
    name: str
    skill_points: float = 50.0
    created_at: str
    
    # セッション固有の属性（計算される）
    player_number: Optional[int] = None
    matches_played: int = 0
    wins: int = 0
    is_participating_today: bool = False
    is_resting: bool = False

    @classmethod
    def create_new(cls, name: str) -> "Player":
        """新しいプレイヤーを作成"""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            skill_points=50.0,
            created_at=datetime.now().isoformat()
        )

    @property
    def level(self) -> int:
        """スキルポイントを1から5のレベルに変換する"""
        return min(5, max(1, int(self.skill_points / 20)))

    @property
    def win_rate(self) -> float:
        """勝率を計算"""
        if self.matches_played == 0:
            return 0.0
        return self.wins / self.matches_played

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """辞書から作成"""
        return cls(**data) 