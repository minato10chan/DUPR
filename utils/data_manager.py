import json
import os
import streamlit as st
from datetime import datetime
from typing import Dict, List, Tuple
from models.player import Player
from models.match import Match
from config.settings import DATA_FILE

def load_data() -> Tuple[Dict[str, Player], List[Match]]:
    """データをファイルから読み込み"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # プレイヤーデータの復元
            players = {}
            for name, player_data in data.get('players', {}).items():
                players[name] = Player.from_dict(player_data)
            
            # マッチデータの復元
            matches = []
            for match_data in data.get('matches', []):
                matches.append(Match.from_dict(match_data))
            
            return players, matches
        except Exception as e:
            st.error(f"データ読み込みエラー: {e}")
            return {}, []
    return {}, []

def save_data(players: Dict[str, Player], matches: List[Match]) -> None:
    """データをファイルに保存"""
    try:
        # プレイヤーデータを辞書形式に変換
        players_data = {}
        for name, player in players.items():
            players_data[name] = player.to_dict()
        
        # マッチデータを辞書形式に変換
        matches_data = []
        for match in matches:
            matches_data.append(match.to_dict())
        
        # データを保存
        data = {
            'players': players_data,
            'matches': matches_data,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        st.error(f"データ保存エラー: {e}")



def get_data_file_info() -> Dict[str, any]:
    """データファイルの情報を取得"""
    if os.path.exists(DATA_FILE):
        return {
            'exists': True,
            'size': os.path.getsize(DATA_FILE),
            'modified': datetime.fromtimestamp(os.path.getmtime(DATA_FILE))
        }
    return {
        'exists': False,
        'size': 0,
        'modified': None
    } 