"""
レーティングシステムモジュール
レーティング計算と更新を担当
"""

from typing import Dict, List


class RatingSystem:
    """レーティングシステムクラス"""
    
    def __init__(self):
        self.min_rating = 800
        self.max_rating = 1600
        self.base_rating = 1200
        self.rating_range = 800
    
    def calculate_rating(self, wins: int, total_matches: int) -> int:
        """レーティング計算"""
        if total_matches == 0:
            return self.base_rating
        
        win_rate = wins / total_matches
        rating = self.base_rating + (win_rate - 0.5) * self.rating_range
        return max(self.min_rating, min(self.max_rating, int(rating)))
    
    def get_rating_group(self, rating: int) -> int:
        """レーティンググループを取得（200単位でグループ化）"""
        return (rating // 200) * 200
    
    def is_same_level(self, rating1: int, rating2: int, max_diff: int = 200) -> bool:
        """同じレベルかどうかを判定"""
        return abs(rating1 - rating2) <= max_diff
    
    def group_by_rating(self, participants: List[Dict]) -> Dict[int, List[Dict]]:
        """レーティングでグループ化"""
        groups = {}
        for participant in participants:
            rating = participant.get('rating', self.base_rating)
            group_key = self.get_rating_group(rating)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(participant)
        return groups 