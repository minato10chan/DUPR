"""
データ管理モジュール
ユーザー、ペア履歴、バイ履歴、対戦履歴の保存・読み込みを担当
"""

import json
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any


class DataManager:
    """データ管理クラス"""
    
    def __init__(self):
        self.data_files = {
            'users': 'users.json',
            'pair_history': 'pair_history.json',
            'bye_history': 'bye_history.json',
            'match_history': 'match_history.json'
        }
    
    def load_data(self) -> None:
        """データの読み込み"""
        try:
            with open(self.data_files['users'], 'r', encoding='utf-8') as f:
                st.session_state.users = json.load(f)
        except FileNotFoundError:
            st.session_state.users = []
        
        try:
            with open(self.data_files['pair_history'], 'r', encoding='utf-8') as f:
                st.session_state.pair_history = json.load(f)
        except FileNotFoundError:
            st.session_state.pair_history = {}
        
        try:
            with open(self.data_files['bye_history'], 'r', encoding='utf-8') as f:
                st.session_state.bye_history = json.load(f)
        except FileNotFoundError:
            st.session_state.bye_history = {}
        
        try:
            with open(self.data_files['match_history'], 'r', encoding='utf-8') as f:
                st.session_state.match_history = json.load(f)
        except FileNotFoundError:
            st.session_state.match_history = {}
    
    def save_data(self) -> None:
        """データの保存"""
        with open(self.data_files['users'], 'w', encoding='utf-8') as f:
            json.dump(st.session_state.users, f, ensure_ascii=False, indent=2)
        
        with open(self.data_files['pair_history'], 'w', encoding='utf-8') as f:
            json.dump(st.session_state.pair_history, f, ensure_ascii=False, indent=2)
        
        with open(self.data_files['bye_history'], 'w', encoding='utf-8') as f:
            json.dump(st.session_state.bye_history, f, ensure_ascii=False, indent=2)
        
        with open(self.data_files['match_history'], 'w', encoding='utf-8') as f:
            json.dump(st.session_state.match_history, f, ensure_ascii=False, indent=2)
    
    def add_user(self, name: str, rating: int, memo: str) -> bool:
        """ユーザー追加"""
        if any(user['name'] == name for user in st.session_state.users):
            return False
        
        new_user = {
            'name': name,
            'rating': rating,
            'memo': memo,
            'wins': 0,
            'total_matches': 0,
            'created_at': datetime.now().isoformat()
        }
        st.session_state.users.append(new_user)
        self.save_data()
        return True
    
    def delete_user(self, user_index: int) -> None:
        """ユーザー削除"""
        if 0 <= user_index < len(st.session_state.users):
            st.session_state.users.pop(user_index)
            self.save_data()
    
    def update_user_ratings(self) -> None:
        """全ユーザーのレーティングを更新"""
        from src.rating_system import RatingSystem
        
        rating_system = RatingSystem()
        for user in st.session_state.users:
            user['rating'] = rating_system.calculate_rating(user['wins'], user['total_matches'])
        self.save_data() 