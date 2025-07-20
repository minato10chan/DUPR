from typing import Dict, List
from models.player import Player
from utils.data_manager import save_data
from config.settings import MIN_MATCHES_FOR_LEVEL_UPDATE

class PlayerService:
    def __init__(self, players: Dict[str, Player], matches: List):
        self.players = players
        self.matches = matches
    
    def add_player(self, name: str, level: int = 3) -> bool:
        """参加者を追加"""
        if name.strip() and name not in self.players:
            self.players[name] = Player(name, level)
            self._save_data()
            return True
        return False
    
    def remove_player(self, name: str) -> bool:
        """参加者を削除"""
        if name in self.players:
            del self.players[name]
            self._save_data()
            return True
        return False
    
    def toggle_rest_status(self, name: str) -> bool:
        """参加者の休憩状態を切り替え"""
        if name in self.players:
            self.players[name].toggle_rest_status()
            self._save_data()
            return True
        return False
    
    def update_player_level(self, name: str, new_level: int) -> bool:
        """プレイヤーのレベルを更新"""
        if name in self.players:
            self.players[name].update_level(new_level)
            self._save_data()
            return True
        return False
    

    
    def update_player_levels(self) -> None:
        """プレイヤーのレベルを自動更新"""
        for player in self.players.values():
            if player.matches_played >= MIN_MATCHES_FOR_LEVEL_UPDATE:
                # 勝率と得失点比率を考慮
                win_rate_factor = (player.win_rate - 0.5) * 2  # -1 to 1
                point_ratio_factor = (player.point_ratio - 1.0) * 0.5  # -0.5 to 0.5
                
                level_change = int(win_rate_factor + point_ratio_factor)
                new_level = player.level + level_change
                
                if new_level != player.level:
                    player.update_level(new_level)
    
    def get_active_players(self) -> List[str]:
        """参加可能なプレイヤーのリストを取得"""
        return [name for name, player in self.players.items() if not player.is_resting]
    
    def get_player_stats(self) -> List[Dict]:
        """プレイヤーの統計データを取得"""
        stats_data = []
        for name, player in self.players.items():
            stats_data.append({
                '名前': name,
                'レベル': player.level,
                '試合数': player.matches_played,
                '勝数': player.wins,
                '勝率': f"{player.win_rate:.1%}",
                '総得点': player.total_points_scored,
                '総失点': player.total_points_conceded,
                '得失点比': f"{player.point_ratio:.2f}",
                '休憩中': "✓" if player.is_resting else ""
            })
        return stats_data
    
    def get_summary_stats(self) -> Dict:
        """サマリー統計を取得"""
        total_players = len(self.players)
        active_players = len(self.get_active_players())
        completed_matches = len([m for m in self.matches if m.is_completed])
        
        return {
            'total_players': total_players,
            'active_players': active_players,
            'completed_matches': completed_matches,
            'can_play': active_players >= 4
        }
    
    def _save_data(self) -> None:
        """データを保存"""
        save_data(self.players, self.matches) 