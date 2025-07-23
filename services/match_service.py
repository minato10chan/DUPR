from typing import List, Optional, Dict, Any
import math
from models.match import Match
from models.player import Player
from utils.data_manager import DataManager
from utils.match_generator import TournamentScheduler
from config.settings import ELO_K_FACTOR

class MatchService:
    def __init__(self):
        self.data_manager = DataManager()

    def get_all_matches(self) -> List[Match]:
        """すべての試合を取得"""
        data = self.data_manager.load_data()
        matches = []
        for match_data in data.get("matches", []):
            try:
                match = Match.from_dict(match_data)
                matches.append(match)
            except Exception as e:
                print(f"試合データの読み込みエラー: {e}")
                continue
        return matches

    def get_current_session_matches(self) -> List[Match]:
        """現在のセッションの試合を取得"""
        # 簡単のため、すべての試合を返す（実際の実装では日時で分ける）
        return self.get_all_matches()

    def save_match(self, match: Match) -> bool:
        """試合を保存"""
        data = self.data_manager.load_data()
        matches_data = data.get("matches", [])
        
        # 既存試合の更新 or 新規追加
        found = False
        for i, match_data in enumerate(matches_data):
            if match_data.get("id") == match.id:
                matches_data[i] = match.to_dict()
                found = True
                break
        
        if not found:
            matches_data.append(match.to_dict())
        
        data["matches"] = matches_data
        return self.data_manager.save_data(data)

    def save_matches(self, matches: List[Match]) -> bool:
        """複数の試合を保存"""
        data = self.data_manager.load_data()
        
        # 新しい試合を追加
        for match in matches:
            data["matches"].append(match.to_dict())
        
        return self.data_manager.save_data(data)

    def generate_matches(self, players: List[Player], num_matches: int, 
                        num_courts: int, skill_matching_enabled: bool) -> List[Match]:
        """試合を生成"""
        try:
            # 既存の試合履歴を取得
            existing_matches = self.get_all_matches()
            
            # TournamentSchedulerを初期化
            scheduler = TournamentScheduler(players, skill_matching_enabled)
            scheduler.update_pair_history(existing_matches)
            
            # 試合生成
            matches = scheduler.generate_matches(num_matches, num_courts)
            
            if not matches:
                # フォールバック処理
                print("通常の試合生成に失敗しました。ランダム生成を実行します。")
                matches = scheduler.generate_fallback_matches(num_matches, num_courts)
            
            return matches
            
        except Exception as e:
            print(f"試合生成エラー: {e}")
            return []

    def record_match_result(self, match_id: str, team1_score: int, team2_score: int, 
                           players: List[Player]) -> bool:
        """試合結果を記録し、スキルポイントを更新"""
        try:
            # 試合を取得
            matches = self.get_all_matches()
            target_match = None
            for match in matches:
                if match.id == match_id:
                    target_match = match
                    break
            
            if not target_match:
                return False
            
            # 試合を完了
            target_match.complete_match(team1_score, team2_score)
            
            # プレイヤーの統計を更新
            self._update_player_stats(target_match, players)
            
            # スキルポイントを更新
            self._update_skill_points(target_match, players)
            
            # 試合を保存
            return self.save_match(target_match)
            
        except Exception as e:
            print(f"試合結果記録エラー: {e}")
            return False

    def _update_player_stats(self, match: Match, players: List[Player]):
        """プレイヤーの統計を更新"""
        # 勝利チームを判定
        winner_team = match.winner_team
        
        # 各プレイヤーの統計を更新
        for player_id in match.team1_player_ids + match.team2_player_ids:
            player = next((p for p in players if p.id == player_id), None)
            if player:
                # 勝利数を更新
                if winner_team == 1 and player_id in match.team1_player_ids:
                    player.wins += 1
                elif winner_team == 2 and player_id in match.team2_player_ids:
                    player.wins += 1

    def _update_skill_points(self, match: Match, players: List[Player]):
        """Eloレーティングシステムでスキルポイントを更新"""
        # チーム1とチーム2のプレイヤーを取得
        team1_players = [p for p in players if p.id in match.team1_player_ids]
        team2_players = [p for p in players if p.id in match.team2_player_ids]
        
        # チーム平均スキルポイントを計算
        team1_avg_skill = sum(p.skill_points for p in team1_players) / len(team1_players)
        team2_avg_skill = sum(p.skill_points for p in team2_players) / len(team2_players)
        
        # 勝利期待値を計算
        expected_team1 = 1 / (1 + 10 ** ((team2_avg_skill - team1_avg_skill) / 400))
        expected_team2 = 1 - expected_team1
        
        # 実際の結果
        if match.winner_team == 1:
            actual_team1 = 1.0
            actual_team2 = 0.0
        elif match.winner_team == 2:
            actual_team1 = 0.0
            actual_team2 = 1.0
        else:
            # 引き分け
            actual_team1 = 0.5
            actual_team2 = 0.5
        
        # スキルポイントを更新
        for player in team1_players:
            delta = ELO_K_FACTOR * (actual_team1 - expected_team1)
            player.skill_points += delta
            player.skill_points = max(0, player.skill_points)  # 最小値0
        
        for player in team2_players:
            delta = ELO_K_FACTOR * (actual_team2 - expected_team2)
            player.skill_points += delta
            player.skill_points = max(0, player.skill_points)  # 最小値0

    def clear_session_matches(self) -> bool:
        """セッションの試合をクリア"""
        data = self.data_manager.load_data()
        data["matches"] = []
        return self.data_manager.save_data(data)

    def get_match_by_id(self, match_id: str) -> Optional[Match]:
        """IDで試合を取得"""
        matches = self.get_all_matches()
        for match in matches:
            if match.id == match_id:
                return match
        return None

    def get_incomplete_matches(self) -> List[Match]:
        """未完了の試合を取得"""
        matches = self.get_all_matches()
        return [m for m in matches if not m.is_completed]

    def get_completed_matches(self) -> List[Match]:
        """完了済みの試合を取得"""
        matches = self.get_all_matches()
        return [m for m in matches if m.is_completed]

    def delete_match(self, match_id: str) -> bool:
        """試合を完全に削除"""
        try:
            data = self.data_manager.load_data()
            matches_data = data.get("matches", [])
            
            # 指定されたIDの試合を削除
            original_length = len(matches_data)
            matches_data = [m for m in matches_data if m.get("id") != match_id]
            
            if len(matches_data) < original_length:
                data["matches"] = matches_data
                return self.data_manager.save_data(data)
            
            return False
            
        except Exception as e:
            print(f"試合削除エラー: {e}")
            return False

    def revert_match_result(self, match: Match, players: List[Player]) -> bool:
        """試合結果を元に戻す（スキルポイントと統計を逆算）"""
        try:
            if not match.is_completed:
                return True  # 未完了の試合は何もしない
            
            # チーム1とチーム2のプレイヤーを取得
            team1_players = [p for p in players if p.id in match.team1_player_ids]
            team2_players = [p for p in players if p.id in match.team2_player_ids]
            
            # チーム平均スキルポイントを計算
            team1_avg_skill = sum(p.skill_points for p in team1_players) / len(team1_players)
            team2_avg_skill = sum(p.skill_points for p in team2_players) / len(team2_players)
            
            # 勝利期待値を計算
            expected_team1 = 1 / (1 + 10 ** ((team2_avg_skill - team1_avg_skill) / 400))
            expected_team2 = 1 - expected_team1
            
            # 実際の結果（逆算）
            if match.winner_team == 1:
                actual_team1 = 1.0
                actual_team2 = 0.0
            elif match.winner_team == 2:
                actual_team1 = 0.0
                actual_team2 = 1.0
            else:
                # 引き分け
                actual_team1 = 0.5
                actual_team2 = 0.5
            
            # スキルポイントを逆算して元に戻す
            for player in team1_players:
                delta = ELO_K_FACTOR * (actual_team1 - expected_team1)
                player.skill_points -= delta
                player.skill_points = max(0, player.skill_points)  # 最小値0
            
            for player in team2_players:
                delta = ELO_K_FACTOR * (actual_team2 - expected_team2)
                player.skill_points -= delta
                player.skill_points = max(0, player.skill_points)  # 最小値0
            
            # 統計も元に戻す
            self._revert_player_stats(match, players)
            
            return True
            
        except Exception as e:
            print(f"試合結果の逆算エラー: {e}")
            return False

    def _revert_player_stats(self, match: Match, players: List[Player]):
        """プレイヤーの統計を元に戻す"""
        # 勝利チームを判定
        winner_team = match.winner_team
        
        # 各プレイヤーの統計を元に戻す
        for player_id in match.team1_player_ids + match.team2_player_ids:
            player = next((p for p in players if p.id == player_id), None)
            if player:
                # 勝利数を元に戻す
                if winner_team == 1 and player_id in match.team1_player_ids:
                    player.wins = max(0, player.wins - 1)
                elif winner_team == 2 and player_id in match.team2_player_ids:
                    player.wins = max(0, player.wins - 1) 