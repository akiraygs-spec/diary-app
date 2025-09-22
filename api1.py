# api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime
from typing import List
import hashlib

# 外部モジュールのインポート
# 以下のファイルが同じディレクトリに存在している必要があります
from data_models import DiaryEntry, Goal
from data_manager import DiaryManager, GoalManager
from bot_counselor import CounselingBot

app = FastAPI(
    title="習慣化ジャーナルAPI",
    description="ノーコードUIと連携するバックエンドロジック",
    version="0.1.0"
)

# Pydanticモデル: APIが受け取るデータの型を定義します
class DiaryEntryRequest(BaseModel):
    title: str
    content: str
    mood: str
    mood_intensity: int
    category: str
    user_email: str

# APIのインスタンスを初期化
bot = CounselingBot()

# --- 日記関連のエンドポイント ---
@app.post("/save_diary/")
def save_diary_entry(entry_request: DiaryEntryRequest):
    """
    日記のエントリーを保存し、ボットの応答を返します。
    """
    try:
        # ユーザー固有のファイルパスを生成
        diary_manager = DiaryManager(user_email=entry_request.user_email)

        # AIボットの応答を生成
        bot_response = bot.get_counseling_response(
            content=entry_request.content,
            mood=entry_request.mood,
            mood_intensity=entry_request.mood_intensity,
            category=entry_request.category
        )

        # 新しい日記エントリーを作成
        new_entry = DiaryEntry(
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            title=entry_request.title,
            content=entry_request.content,
            mood=entry_request.mood,
            mood_intensity=entry_request.mood_intensity,
            category=entry_request.category,
            user_email=entry_request.user_email,
            bot_response=bot_response
        )

        # 日記を保存
        diary_manager.add_entry(new_entry)

        return {"message": "日記が正常に保存されました。", "bot_response": bot_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部サーバーエラーが発生しました: {e}")


@app.get("/get_diary_history/{user_email}")
def get_diary_history(user_email: str):
    """
    ユーザーの全日記エントリーを取得します。
    """
    try:
        diary_manager = DiaryManager(user_email=user_email)
        entries = diary_manager.load_entries()
        # asdict()を使ってdataclassを辞書に変換し、JSONシリアライズ可能にする
        return {"entries": [entry for entry in entries]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部サーバーエラーが発生しました: {e}")

# --- 目標関連のエンドポイント ---
@app.get("/get_goals/{user_email}")
def get_user_goals(user_email: str):
    """
    ユーザーの全目標を取得します。
    """
    try:
        goal_manager = GoalManager(user_email=user_email)
        goals = goal_manager.load_goals()
        # asdict()を使ってdataclassを辞書に変換し、JSONシリアライズ可能にする
        return {"goals": [goal for goal in goals]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部サーバーエラーが発生しました: {e}")
