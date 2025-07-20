import random
from typing import List, Set, Tuple, Dict
from models.player import Player
from models.match import Match
from config.settings import (
    MIN_PLAYERS_FOR_MATCH, 
    MAX_COMBINATION_ATTEMPTS,
    MIN_MATCHES_FOR_LEVEL_UPDATE
)

def get_historical_combinations(matches: List[Match]) -> Set[Tuple]:
    """過去の組み合わせを取得（完了した試合のみ）"""
    combinations = set()
    for match in matches:
        if match.is_completed:  # 完了した試合のみを考慮
            # チーム1の組み合わせ
            team1_players = tuple(sorted(match.team1))
            combinations.add(team1_players)
            # チーム2の組み合わせ
            team2_players = tuple(sorted(match.team2))
            combinations.add(team2_players)
            # 対戦組み合わせ
            match_combination = tuple(sorted([team1_players, team2_players]))
            combinations.add(match_combination)
    return combinations

def is_combination_used(team1: List[str], team2: List[str], historical_combinations: Set[Tuple]) -> bool:
    """組み合わせが過去に使用されているかチェック"""
    team1_sorted = tuple(sorted(team1))
    team2_sorted = tuple(sorted(team2))
    match_combination = tuple(sorted([team1_sorted, team2_sorted]))
    
    # チーム内の組み合わせチェック
    if team1_sorted in historical_combinations or team2_sorted in historical_combinations:
        return True
    
    # 対戦組み合わせチェック
    if match_combination in historical_combinations:
        return True
    
    return False

def generate_matches(
    players: Dict[str, Player], 
    matches: List[Match], 
    court_count: int, 
    match_count: int, 
    skill_matching: bool
) -> List[Match]:
    """試合組み合わせを生成"""
    available_players = [name for name, player in players.items() 
                        if not player.is_resting]
    
    if len(available_players) < MIN_PLAYERS_FOR_MATCH:
        return []
    
    # 過去の組み合わせを取得（完了した試合のみ）
    historical_combinations = get_historical_combinations(matches)
    
    new_matches = []
    current_match_index = len(matches)
    
    # 各プレイヤーの試合数を取得
    player_match_counts = {}
    for name in available_players:
        player_match_counts[name] = players[name].matches_played
    
    # 前回の試合に出たプレイヤーを取得
    last_match_players = set()
    if matches:
        last_match = matches[-1]
        if not last_match.is_completed:  # 前回の試合が未完了の場合
            last_match_players = set(last_match.team1 + last_match.team2)
    
    # 指定された試合数分の組み合わせを生成
    for match_num in range(match_count):
        if len(available_players) < MIN_PLAYERS_FOR_MATCH:
            break
            
        # 組み合わせ生成を試行
        match_found = False
        for attempt in range(MAX_COMBINATION_ATTEMPTS):
            # プレイヤーを優先度でソート
            # 1. 前回の試合に出ていない人を優先
            # 2. 試合数の少ない人を優先
            # 3. スキルレベルマッチングがONの場合はレベルでソート
            temp_players = available_players.copy()
            
            # 優先度スコアを計算
            def get_priority_score(player_name):
                score = 0
                # 前回の試合に出ていない場合は+1000点
                if player_name not in last_match_players:
                    score += 1000
                # 試合数の少ない人を優先（試合数が少ないほど高スコア）
                score += (max(player_match_counts.values()) - player_match_counts[player_name]) * 100
                # スキルレベルマッチングがONの場合はレベルでソート
                if skill_matching:
                    score += players[player_name].level
                return score
            
            temp_players.sort(key=get_priority_score, reverse=True)
            
            # チーム1を選択（試合数の少ない人を優先）
            team1_players = []
            for player in temp_players:
                if len(team1_players) >= 2:
                    break
                # 前回の試合に出ていない人を優先
                if player not in last_match_players or len(team1_players) == 0:
                    team1_players.append(player)
            
            if len(team1_players) != 2:
                continue
                
            # チーム1のプレイヤーを一時的に削除
            remaining_players = [p for p in temp_players if p not in team1_players]
            
            # チーム2を選択（試合数の少ない人を優先）
            team2_players = []
            for player in remaining_players:
                if len(team2_players) >= 2:
                    break
                # 前回の試合に出ていない人を優先
                if player not in last_match_players or len(team2_players) == 0:
                    team2_players.append(player)
            
            if len(team2_players) != 2:
                continue
            
            # 過去の組み合わせをチェック（完了した試合 + 今回生成した試合）
            if is_combination_used(team1_players, team2_players, historical_combinations):
                continue
            
            # 新しい組み合わせが見つかった
            match = Match(
                team1_players, 
                team2_players, 
                (match_num % court_count) + 1, 
                current_match_index
            )
            new_matches.append(match)
            current_match_index += 1
            
            # 新しく生成した組み合わせを履歴に追加（重複回避のため）
            team1_sorted = tuple(sorted(team1_players))
            team2_sorted = tuple(sorted(team2_players))
            match_combination = tuple(sorted([team1_sorted, team2_sorted]))
            historical_combinations.add(team1_sorted)
            historical_combinations.add(team2_sorted)
            historical_combinations.add(match_combination)
            
            # プレイヤーの試合数を更新
            for player in team1_players + team2_players:
                player_match_counts[player] += 1
            
            # 前回の試合プレイヤーを更新
            last_match_players = set(team1_players + team2_players)
            
            match_found = True
            break
        
        # 組み合わせが見つからない場合は制約を緩める
        if not match_found and len(available_players) >= MIN_PLAYERS_FOR_MATCH:
            # 試合数の少ない人を優先して選択
            temp_players = sorted(available_players, key=lambda x: player_match_counts[x])
            
            team1_players = temp_players[:2]
            team2_players = temp_players[2:4] if len(temp_players) >= 4 else temp_players[:2]
            
            # 過去の組み合わせをチェック
            if is_combination_used(team1_players, team2_players, historical_combinations):
                continue
            
            match = Match(
                team1_players, 
                team2_players, 
                (match_num % court_count) + 1, 
                current_match_index
            )
            new_matches.append(match)
            current_match_index += 1
            
            # 新しく生成した組み合わせを履歴に追加
            team1_sorted = tuple(sorted(team1_players))
            team2_sorted = tuple(sorted(team2_players))
            match_combination = tuple(sorted([team1_sorted, team2_sorted]))
            historical_combinations.add(team1_sorted)
            historical_combinations.add(team2_sorted)
            historical_combinations.add(match_combination)
            
            # プレイヤーの試合数を更新
            for player in team1_players + team2_players:
                player_match_counts[player] += 1
            
            # 前回の試合プレイヤーを更新
            last_match_players = set(team1_players + team2_players)
    
    return new_matches 