from typing import List, Optional, Dict, Any
from models.player import Player
from utils.data_manager import DataManager

class PlayerService:
    def __init__(self):
        self.data_manager = DataManager()

    def get_all_players(self) -> List[Player]:
        """すべてのプレイヤーを取得"""
        data = self.data_manager.load_data()
        players = []
        for player_data in data.get("players", []):
            try:
                player = Player.from_dict(player_data)
                players.append(player)
            except Exception as e:
                print(f"プレイヤーデータの読み込みエラー: {e}")
                continue
        return players

    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """IDでプレイヤーを取得"""
        players = self.get_all_players()
        for player in players:
            if player.id == player_id:
                return player
        return None

    def create_player(self, name: str) -> Player:
        """新しいプレイヤーを作成"""
        # 名前の重複チェック
        existing_players = self.get_all_players()
        if any(p.name == name for p in existing_players):
            raise ValueError(f"プレイヤー名 '{name}' は既に存在します")
        
        player = Player.create_new(name)
        self.save_player(player)
        return player

    def update_player(self, player: Player) -> bool:
        """プレイヤー情報を更新"""
        data = self.data_manager.load_data()
        players_data = data.get("players", [])
        
        for i, player_data in enumerate(players_data):
            if player_data.get("id") == player.id:
                players_data[i] = player.to_dict()
                data["players"] = players_data
                return self.data_manager.save_data(data)
        
        return False

    def save_player(self, player: Player) -> bool:
        """プレイヤーを保存"""
        data = self.data_manager.load_data()
        players_data = data.get("players", [])
        
        # 既存プレイヤーの更新 or 新規追加
        found = False
        for i, player_data in enumerate(players_data):
            if player_data.get("id") == player.id:
                players_data[i] = player.to_dict()
                found = True
                break
        
        if not found:
            players_data.append(player.to_dict())
        
        data["players"] = players_data
        return self.data_manager.save_data(data)

    def delete_player(self, player_id: str) -> bool:
        """プレイヤーを削除"""
        data = self.data_manager.load_data()
        players_data = data.get("players", [])
        
        original_length = len(players_data)
        players_data = [p for p in players_data if p.get("id") != player_id]
        
        if len(players_data) < original_length:
            data["players"] = players_data
            return self.data_manager.save_data(data)
        
        return False

    def set_participation_status(self, player_id: str, is_participating: bool) -> bool:
        """参加状態を設定"""
        player = self.get_player_by_id(player_id)
        if player:
            player.is_participating_today = is_participating
            if not is_participating:
                player.is_resting = False  # 不参加の場合は休憩も解除
            return self.update_player(player)
        return False

    def set_resting_status(self, player_id: str, is_resting: bool) -> bool:
        """休憩状態を設定"""
        player = self.get_player_by_id(player_id)
        if player and player.is_participating_today:
            player.is_resting = is_resting
            return self.update_player(player)
        return False

    def get_participating_players(self) -> List[Player]:
        """本日参加中のプレイヤーを取得"""
        players = self.get_all_players()
        return [p for p in players if p.is_participating_today]

    def get_active_players(self) -> List[Player]:
        """現在アクティブなプレイヤー（参加中かつ非休憩）を取得"""
        players = self.get_all_players()
        return [p for p in players if p.is_participating_today and not p.is_resting]

    def reset_session_stats(self) -> bool:
        """セッション用統計をリセット"""
        players = self.get_all_players()
        for player in players:
            player.matches_played = 0
            player.wins = 0
            player.player_number = None
            self.update_player(player)
        return True

    def assign_player_numbers(self) -> bool:
        """参加者に番号を振る"""
        participating_players = self.get_participating_players()
        
        # 名前順でソートして番号を振る（一貫性を保つため）
        participating_players.sort(key=lambda p: p.name)
        
        for i, player in enumerate(participating_players, 1):
            player.player_number = i
            self.update_player(player)
        return True

    def get_ranking_by_winrate(self) -> List[Player]:
        """勝率でランキングを取得"""
        players = self.get_participating_players()
        # 勝率順でソート（勝率同じ場合は試合数が多い順）
        players.sort(key=lambda p: (p.win_rate, p.matches_played), reverse=True)
        return players

    def get_ranking_by_skill(self) -> List[Player]:
        """スキルポイントでランキングを取得"""
        players = self.get_participating_players()
        players.sort(key=lambda p: p.skill_points, reverse=True)
        return players 