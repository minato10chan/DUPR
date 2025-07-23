import json
import os
import tempfile
import shutil
from typing import Dict, Any
from config.settings import DATA_FILE_PATH

class DataManager:
    @staticmethod
    def load_data() -> Dict[str, Any]:
        """データファイルを読み込む。ファイルが存在しない場合は空のデータ構造を返す"""
        try:
            # ディレクトリが存在しない場合は作成
            data_dir = os.path.dirname(DATA_FILE_PATH)
            if data_dir:  # パスにディレクトリが含まれている場合のみ
                os.makedirs(data_dir, exist_ok=True)
            
            if os.path.exists(DATA_FILE_PATH):
                with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # データ構造の検証
                    if not isinstance(data, dict):
                        raise ValueError("データファイルの形式が正しくありません")
                    return data
            else:
                print(f"データファイルが見つかりません。新しいファイルを作成します: {DATA_FILE_PATH}")
                # 初期データ構造を作成して保存
                initial_data = {
                    "players": [],
                    "matches": [],
                    "session_data": {
                        "current_match_index": 0,
                        "participating_players": []
                    }
                }
                DataManager.save_data(initial_data)
                return initial_data
                
        except (json.JSONDecodeError, FileNotFoundError, PermissionError, OSError) as e:
            print(f"データファイルの読み込みに失敗しました: {e}")
            print(f"ファイルパス: {DATA_FILE_PATH}")
            # エラーが発生した場合も初期データ構造を返す
            return {
                "players": [],
                "matches": [],
                "session_data": {
                    "current_match_index": 0,
                    "participating_players": []
                }
            }
        except Exception as e:
            print(f"予期しないエラーが発生しました: {e}")
            # 予期しないエラーでも初期データ構造を返す
            return {
                "players": [],
                "matches": [],
                "session_data": {
                    "current_match_index": 0,
                    "participating_players": []
                }
            }

    @staticmethod
    def save_data(data: Dict[str, Any]) -> bool:
        """データをJSONファイルに保存する。アトミックな書き込みを実行"""
        try:
            # ディレクトリが存在しない場合は作成
            data_dir = os.path.dirname(DATA_FILE_PATH)
            if data_dir:  # パスにディレクトリが含まれている場合のみ
                os.makedirs(data_dir, exist_ok=True)
            
            # 一時ファイルに書き込み
            temp_dir = data_dir if data_dir else '.'
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                           dir=temp_dir, 
                                           delete=False) as temp_file:
                json.dump(data, temp_file, ensure_ascii=False, indent=2)
                temp_filename = temp_file.name
            
            # バックアップを作成（既存ファイルがある場合）
            if os.path.exists(DATA_FILE_PATH):
                backup_file = DATA_FILE_PATH + ".backup"
                try:
                    shutil.copy2(DATA_FILE_PATH, backup_file)
                except Exception as backup_error:
                    print(f"バックアップ作成に失敗: {backup_error}")
            
            # 一時ファイルを本ファイルに移動（アトミック操作）
            shutil.move(temp_filename, DATA_FILE_PATH)
            print(f"データを正常に保存しました: {DATA_FILE_PATH}")
            return True
            
        except (PermissionError, OSError, IOError) as e:
            print(f"データの保存に失敗しました (ファイルシステムエラー): {e}")
            print(f"ファイルパス: {DATA_FILE_PATH}")
            # 一時ファイルを削除（もし存在すれば）
            try:
                if 'temp_filename' in locals() and os.path.exists(temp_filename):
                    os.unlink(temp_filename)
            except:
                pass
            return False
            
        except Exception as e:
            print(f"データの保存に失敗しました (予期しないエラー): {e}")
            print(f"ファイルパス: {DATA_FILE_PATH}")
            # 一時ファイルを削除（もし存在すれば）
            try:
                if 'temp_filename' in locals() and os.path.exists(temp_filename):
                    os.unlink(temp_filename)
            except:
                pass
            return False

    @staticmethod
    def backup_data() -> bool:
        """現在のデータファイルのバックアップを作成"""
        try:
            if os.path.exists(DATA_FILE_PATH):
                backup_file = DATA_FILE_PATH + ".backup"
                shutil.copy2(DATA_FILE_PATH, backup_file)
                return True
            return False
        except Exception as e:
            print(f"バックアップの作成に失敗しました: {e}")
            return False 