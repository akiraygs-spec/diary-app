import streamlit as st
import json
import datetime
import hashlib
import re
import pandas as pd
import altair as alt
from typing import List, Dict
import os
from dataclasses import dataclass, asdict
import calendar
import numpy as np
import math

# ページ設定
st.set_page_config(
    page_title="習慣化ジャーナル - 目標達成と心の成長",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 淡色テーマカラー定義（6種類、より淡く優しい色合い）
THEME_PALETTES = {
    "ソフトブルー": {
        "primary": "#87ceeb",
        "secondary": "#add8e6", 
        "accent": "#e0f6ff",
        "background": "#f8fcff",
        "surface": "#f5faff",
        "card": "rgba(245, 250, 255, 0.9)",
        "text_primary": "#4682b4",
        "text_secondary": "#6495ed",
        "border": "rgba(135, 206, 235, 0.3)",
        "shadow": "rgba(135, 206, 235, 0.2)",
        "gradient": "linear-gradient(135deg, #f8fcff 0%, #e0f6ff 100%)"
    },
    "パステルピンク": {
        "primary": "#ffc0cb",
        "secondary": "#ffb6c1",
        "accent": "#ffe4e6",
        "background": "#fffafc",
        "surface": "#fff5f8",
        "card": "rgba(255, 245, 248, 0.9)",
        "text_primary": "#cd919e",
        "text_secondary": "#db7093",
        "border": "rgba(255, 192, 203, 0.3)",
        "shadow": "rgba(255, 192, 203, 0.2)",
        "gradient": "linear-gradient(135deg, #fffafc 0%, #ffe4e6 100%)"
    },
    "ミントグリーン": {
        "primary": "#98fb98",
        "secondary": "#90ee90",
        "accent": "#f0fff0",
        "background": "#f8fff8",
        "surface": "#f5fff5",
        "card": "rgba(245, 255, 245, 0.9)",
        "text_primary": "#228b22",
        "text_secondary": "#32cd32",
        "border": "rgba(152, 251, 152, 0.3)",
        "shadow": "rgba(152, 251, 152, 0.2)",
        "gradient": "linear-gradient(135deg, #f8fff8 0%, #f0fff0 100%)"
    },
    "ラベンダーミスト": {
        "primary": "#e6e6fa",
        "secondary": "#dda0dd",
        "accent": "#f8f8ff",
        "background": "#fefcff",
        "surface": "#faf8ff",
        "card": "rgba(250, 248, 255, 0.9)",
        "text_primary": "#9370db",
        "text_secondary": "#ba55d3",
        "border": "rgba(230, 230, 250, 0.4)",
        "shadow": "rgba(230, 230, 250, 0.2)",
        "gradient": "linear-gradient(135deg, #fefcff 0%, #f8f8ff 100%)"
    },
    "ピーチクリーム": {
        "primary": "#ffdab9",
        "secondary": "#ffe4b5",
        "accent": "#fff8dc",
        "background": "#fffefa",
        "surface": "#fffcf5",
        "card": "rgba(255, 252, 245, 0.9)",
        "text_primary": "#cd853f",
        "text_secondary": "#daa520",
        "border": "rgba(255, 218, 185, 0.3)",
        "shadow": "rgba(255, 218, 185, 0.2)",
        "gradient": "linear-gradient(135deg, #fffefa 0%, #fff8dc 100%)"
    },
    "クラウドグレー": {
        "primary": "#d3d3d3",
        "secondary": "#dcdcdc",
        "accent": "#f8f8ff",
        "background": "#fafafa",
        "surface": "#f7f7f7",
        "card": "rgba(247, 247, 247, 0.9)",
        "text_primary": "#696969",
        "text_secondary": "#808080",
        "border": "rgba(211, 211, 211, 0.4)",
        "shadow": "rgba(211, 211, 211, 0.2)",
        "gradient": "linear-gradient(135deg, #fafafa 0%, #f8f8ff 100%)"
    }
}

# 心模様の定義（5色×4種類 = 20種類、感情別に整理）
MOOD_OPTIONS = {
    "ポジティブ": [
        {"name": "喜び", "color": "#87ceeb", "intensity": 5},
        {"name": "幸福", "color": "#87ceeb", "intensity": 5},
        {"name": "満足", "color": "#87ceeb", "intensity": 4},
        {"name": "希望", "color": "#87ceeb", "intensity": 4}
    ],
    "穏やか": [
        {"name": "安らぎ", "color": "#98fb98", "intensity": 4},
        {"name": "穏やか", "color": "#98fb98", "intensity": 3},
        {"name": "平静", "color": "#98fb98", "intensity": 3},
        {"name": "感謝", "color": "#98fb98", "intensity": 4}
    ],
    "ニュートラル": [
        {"name": "普通", "color": "#d3d3d3", "intensity": 2},
        {"name": "退屈", "color": "#d3d3d3", "intensity": 2},
        {"name": "疲労", "color": "#d3d3d3", "intensity": 1},
        {"name": "混乱", "color": "#d3d3d3", "intensity": 1}
    ],
    "不安・心配": [
        {"name": "不安", "color": "#ffdab9", "intensity": 1},
        {"name": "心配", "color": "#ffdab9", "intensity": 1},
        {"name": "少し憂鬱", "color": "#ffdab9", "intensity": 2},
        {"name": "孤独", "color": "#ffdab9", "intensity": 1}
    ],
    "ネガティブ": [
        {"name": "悲しみ", "color": "#ffc0cb", "intensity": 1},
        {"name": "イライラ", "color": "#ffc0cb", "intensity": 1},
        {"name": "怒り", "color": "#ffc0cb", "intensity": 0},
        {"name": "絶望", "color": "#ffc0cb", "intensity": 0}
    ]
}

# カスタムCSS（改良版）
def get_css(theme_name="ソフトブルー"):
    theme = THEME_PALETTES.get(theme_name, THEME_PALETTES["ソフトブルー"])
    
    return f"""
<style>
    .stApp {{
        background: {theme['gradient']};
        color: {theme['text_primary']};
        min-height: 100vh;
    }}
    
    .stSidebar > div:first-child {{
        background: linear-gradient(180deg, {theme['surface']} 0%, {theme['card']} 100%);
        border-right: 1px solid {theme['border']};
    }}
    
    .main-header {{
        text-align: center;
        color: {theme['primary']};
        font-size: 2.8rem;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px {theme['shadow']};
        font-weight: 300;
        letter-spacing: -0.5px;
    }}
    
    .subtitle {{
        text-align: center;
        color: {theme['text_secondary']};
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }}
    
    /* 目標表示カード */
    .goals-overview {{
        background: {theme['card']};
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid {theme['border']};
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px {theme['shadow']};
        position: sticky;
        top: 20px;
        z-index: 100;
    }}
    
    .goal-item {{
        margin: 0.8rem 0;
        padding: 0.8rem;
        background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.4) 100%);
        border-radius: 8px;
        border-left: 4px solid {theme['primary']};
    }}
    
    .floating-write-btn {{
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        background: linear-gradient(135deg, {theme['primary']} 0%, {theme['secondary']} 100%);
        border: none;
        border-radius: 50px;
        padding: 15px 25px;
        color: {theme['text_primary']};
        font-weight: bold;
        box-shadow: 0 6px 25px {theme['shadow']};
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 16px;
    }}
    
    .floating-write-btn:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 35px {theme['shadow']};
        background: linear-gradient(135deg, {theme['secondary']} 0%, {theme['accent']} 100%);
    }}
    
    .diary-entry {{
        background: {theme['card']};
        padding: 1.8rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid {theme['border']};
        color: {theme['text_primary']};
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px {theme['shadow']};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .diary-entry:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 30px {theme['shadow']};
    }}
    
    .bot-response {{
        background: linear-gradient(135deg, rgba(255, 248, 220, 0.9) 0%, rgba(255, 250, 235, 0.7) 100%);
        padding: 1.8rem;
        border-radius: 16px;
        margin: 1rem 0;
        border-left: 4px solid #daa520;
        color: #8b7355;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(218, 165, 32, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .mood-section {{
        margin: 1rem 0;
        padding: 1rem;
        background: {theme['card']};
        border-radius: 12px;
        border: 1px solid {theme['border']};
    }}
    
    .mood-section h4 {{
        margin: 0 0 0.5rem 0;
        color: {theme['text_primary']};
        font-size: 0.95rem;
    }}
    
    .mood-circle {{
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: inline-block;
        margin: 6px;
        border: 2px solid rgba(255,255,255,0.7);
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    .mood-circle:hover {{
        transform: scale(1.15);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border-color: {theme['primary']};
    }}
    
    .mood-circle.selected {{
        border: 3px solid {theme['primary']};
        transform: scale(1.2);
        box-shadow: 0 4px 20px {theme['shadow']};
    }}

    .selected-mood-display {{
        background: {theme['card']};
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid {theme['primary']};
        text-align: center;
    }}
    
    .action-plan {{
        background: {theme['card']};
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid {theme['border']};
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px {theme['shadow']};
    }}
    
    .action-item {{
        background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.4) 100%);
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid {theme['secondary']};
    }}
    
    .goal-period {{
        display: inline-block;
        background: {theme['primary']};
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }}
    
    .stats-card {{
        background: {theme['card']};
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px {theme['shadow']};
        text-align: center;
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        backdrop-filter: blur(5px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .stats-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 30px {theme['shadow']};
    }}

    /* ボトムナビゲーション */
    .bottom-nav {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: {theme['card']};
        border-top: 1px solid {theme['border']};
        padding: 0.8rem 1rem;
        z-index: 1000;
        backdrop-filter: blur(10px);
        box-shadow: 0 -2px 20px {theme['shadow']};
    }}
    
    .nav-container {{
        display: flex;
        justify-content: space-around;
        align-items: center;
        max-width: 600px;
        margin: 0 auto;
    }}
    
    .nav-item {{
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 8px;
        transition: all 0.2s ease;
        color: {theme['text_secondary']};
        text-decoration: none;
        min-width: 60px;
    }}
    
    .nav-item:hover {{
        background: rgba(255, 255, 255, 0.1);
        color: {theme['primary']};
    }}
    
    .nav-item.active {{
        color: {theme['primary']};
        background: rgba(255, 255, 255, 0.15);
    }}
    
    .nav-icon {{
        font-size: 1.4rem;
        margin-bottom: 0.2rem;
    }}
    
    .nav-text {{
        font-size: 0.7rem;
        font-weight: 500;
        text-align: center;
    }}
    
    /* メインコンテンツの下部余白を追加 */
    .main-content {{
        padding-bottom: 100px;
    }}
    
    /* サイドバーを非表示 */
    .stSidebar {{
        display: none !important;
    }}
    
    /* メインコンテンツ幅を調整 */
    .stAppViewContainer > .main > div {{
        max-width: none !important;
        padding: 1rem 2rem;
    }}
    
    /* 改良されたボタンスタイル */
    .stButton > button {{
        background: linear-gradient(135deg, {theme['primary']} 0%, {theme['secondary']} 100%);
        border: none;
        border-radius: 25px;
        color: {theme['text_primary']};
        padding: 12px 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px {theme['shadow']};
        font-weight: 500;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, {theme['secondary']} 0%, {theme['accent']} 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px {theme['shadow']};
    }}
    
    /* セレクトボックスのスタイル改善 */
    .stSelectbox > div > div {{
        background: {theme['card']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        backdrop-filter: blur(5px);
    }}
    
    /* テキスト入力のスタイル改善 */
    .stTextInput > div > div > input {{
        background: {theme['card']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        backdrop-filter: blur(5px);
        color: {theme['text_primary']};
    }}
    
    .stTextArea > div > div > textarea {{
        background: {theme['card']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        backdrop-filter: blur(5px);
        color: {theme['text_primary']};
    }}
</style>
"""

@dataclass
class Goal:
    id: str
    title: str
    description: str
    category: str  # "short", "medium", "long"
    deadline: str
    created_date: str
    user_email: str = ""

@dataclass
class User:
    email: str
    password_hash: str
    nickname: str
    created_date: str

@dataclass
class DiaryEntry:
    date: str
    title: str
    content: str
    mood: str
    mood_intensity: int
    category: str
    user_email: str = ""
    bot_response: str = ""

class GoalManager:
    def __init__(self, user_email: str = ""):
        self.user_email = user_email
        self.goals_file = f"goals_{hashlib.md5(user_email.encode()).hexdigest()}.json" if user_email else "goals.json"
    
    def load_goals(self) -> List[Goal]:
        try:
            if os.path.exists(self.goals_file):
                with open(self.goals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    goals = []
                    for goal_data in data:
                        # 古いデータとの互換性のため進捗フィールドを除去
                        if 'progress' in goal_data:
                            del goal_data['progress']
                        goals.append(Goal(**goal_data))
                    return goals
        except:
            pass
        return []
    
    def save_goals(self, goals: List[Goal]):
        try:
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(goal) for goal in goals], f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"目標の保存に失敗しました: {e}")
    
    def add_goal(self, goal: Goal):
        goal.user_email = self.user_email
        goals = self.load_goals()
        goals.append(goal)
        self.save_goals(goals)
    
    def delete_goal(self, goal_id: str):
        goals = self.load_goals()
        goals = [goal for goal in goals if goal.id != goal_id]
        self.save_goals(goals)

class AuthManager:
    def __init__(self):
        self.users_file = "users.json"
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> bool:
        if len(password) < 8:
            return False
        has_letter = re.search(r'[a-zA-Z]', password)
        has_number = re.search(r'[0-9]', password)
        return has_letter is not None and has_number is not None
    
    def load_users(self) -> List[User]:
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    users = []
                    for user_data in data:
                        # 古いデータとの互換性のためニックネームフィールドを追加
                        if 'nickname' not in user_data:
                            user_data['nickname'] = user_data['email'].split('@')[0]
                        users.append(User(**user_data))
                    return users
        except:
            pass
        return []
    
    def save_users(self, users: List[User]):
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(user) for user in users], f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"ユーザー情報の保存に失敗しました: {e}")
    
    def register_user(self, email: str, password: str, nickname: str) -> bool:
        if not self.validate_email(email):
            st.error("有効なメールアドレスを入力してください")
            return False
        
        if not self.validate_password(password):
            st.error("パスワードは8文字以上で、英字と数字の両方を含む必要があります")
            return False
        
        if not nickname.strip():
            st.error("ニックネームを入力してください")
            return False
        
        users = self.load_users()
        
        if any(user.email == email for user in users):
            st.error("このメールアドレスは既に登録されています")
            return False
        
        new_user = User(
            email=email,
            password_hash=self.hash_password(password),
            nickname=nickname.strip(),
            created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        users.append(new_user)
        self.save_users(users)
        return True
    
    def authenticate_user(self, email: str, password: str) -> tuple[bool, str]:
        users = self.load_users()
        password_hash = self.hash_password(password)
        
        for user in users:
            if user.email == email and user.password_hash == password_hash:
                return True, user.nickname
        return False, ""

class DiaryManager:
    def __init__(self, user_email: str = ""):
        self.user_email = user_email
        self.entries_file = f"diary_entries_{hashlib.md5(user_email.encode()).hexdigest()}.json" if user_email else "diary_entries.json"
        
    def load_entries(self) -> List[DiaryEntry]:
        try:
            if os.path.exists(self.entries_file):
                with open(self.entries_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entries = []
                    for entry_data in data:
                        if 'mood_intensity' not in entry_data:
                            entry_data['mood_intensity'] = 3
                        entries.append(DiaryEntry(**entry_data))
                    return entries
        except:
            pass
        return []
    
    def save_entries(self, entries: List[DiaryEntry]):
        try:
            with open(self.entries_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(entry) for entry in entries], f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"保存に失敗しました: {e}")
    
    def add_entry(self, entry: DiaryEntry):
        entry.user_email = self.user_email
        entries = self.load_entries()
        entries.append(entry)
        self.save_entries(entries)

class CounselingBot:
    def __init__(self):
        try:
            self.api_key = st.secrets.get("OPENAI_API_KEY", "")
        except:
            self.api_key = ""
        
    def get_counseling_response(self, content: str, mood: str, mood_intensity: int, category: str) -> str:
        intensity_responses = {
            0: "今はとても辛い時期ですね。あなたの痛みを心から受け止めています。一人ではありません。",
            1: "大変な気持ちですね。そんな日もあります。無理をせず、自分を労ってあげてください。",
            2: "少し重い気持ちなのですね。ゆっくりと深呼吸をして、今この瞬間を大切にしましょう。",
            3: "穏やかな心持ちですね。この平静さを大切に、今日を過ごしてください。",
            4: "良い気分のようですね。その明るい気持ちが、周りにも温かさを届けています。",
            5: "素晴らしい気持ちが伝わってきます！この喜びを心に刻んで、明日への力にしてください。"
        }
        
        base_response = intensity_responses.get(mood_intensity, "あなたの気持ちに、静かに寄り添っています。")
        
        category_advice = {
            "仕事・学業": "一歩ずつ、あなたのペースで進んでいけば大丈夫です。目標に向かって着実に歩んでいきましょう。",
            "人間関係": "人との関わりは複雑ですが、あなたの誠実さは必ず相手に伝わります。自分らしさを大切にしてください。",
            "恋愛": "心を開くことは勇気がいりますが、真っ直ぐな気持ちは美しいものです。時間をかけて育んでいきましょう。",
            "家族": "家族だからこそ難しい面もありますね。お互いを思いやる気持ちがあれば、きっと理解し合えます。",
            "健康": "心と体の声に耳を傾けることは大切です。無理をせず、自分に優しくしてあげてください。",
            "その他": "どんな気持ちも、あなたにとって大切な感情です。その気持ちを大切にしながら歩んでいきましょう。"
        }
        
        advice = category_advice.get(category, "あなたなりのペースで、ゆっくりと歩んでいけば大丈夫です。")
        
        return f"{base_response}\n\n{advice}\n\n今日も一日お疲れ様でした。あなたの成長を応援しています 🌟"

def goals_overview_widget(goal_manager: GoalManager):
    """目標概要ウィジェット（常時表示、進捗バー削除）"""
    goals = goal_manager.load_goals()
    
    if not goals:
        st.markdown("""
        <div class="goals-overview">
            <h3 style="margin-bottom: 1rem; color: var(--primary-color);">🎯 まずは目標を設定しましょう</h3>
            <p style="color: var(--text-secondary); margin: 0;">目標設定ページで短期・中期・長期の目標を設定してください</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    short_goals = [g for g in goals if g.category == "short"]
    medium_goals = [g for g in goals if g.category == "medium"]
    long_goals = [g for g in goals if g.category == "long"]
    
    goals_html = f"""
    <div class="goals-overview">
        <h3 style="margin-bottom: 1rem;">🎯 現在の目標</h3>
    """
    
    # 短期目標
    if short_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'>🔥 短期目標</h4>"
        for goal in short_goals[:2]:  # 最大2つ表示
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
            </div>
            """
    
    # 中期目標
    if medium_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'>📈 中期目標</h4>"
        for goal in medium_goals[:2]:
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
            </div>
            """
    
    # 長期目標
    if long_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'>🌟 長期目標</h4>"
        for goal in long_goals[:1]:  # 1つだけ表示
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
            </div>
            """
    
    goals_html += "</div>"
    st.markdown(goals_html, unsafe_allow_html=True)

def mood_selector():
    """心模様選択UI（5つのカテゴリ別に整理）"""
    st.subheader("今の心模様は？")
    
    selected_mood = st.session_state.get('selected_mood', MOOD_OPTIONS["ポジティブ"][0])
    
    for category, moods in MOOD_OPTIONS.items():
        st.markdown(f'<div class="mood-section">', unsafe_allow_html=True)
        st.markdown(f"<h4>{category}</h4>", unsafe_allow_html=True)
        
        cols = st.columns(4)
        for i, mood in enumerate(moods):
            with cols[i]:
                is_selected = selected_mood['name'] == mood['name']
                circle_class = "mood-circle selected" if is_selected else "mood-circle"
                
                st.markdown(f"""
                <div class="{circle_class}" 
                     style="background-color: {mood['color']};" 
                     title="{mood['name']}">
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(mood['name'], key=f"mood_{mood['name']}", help=f"強度: {mood['intensity']}/5"):
                    st.session_state.selected_mood = mood
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return selected_mood

def login_page():
    """ログイン・新規登録ページ"""
    theme_name = st.session_state.get('theme_name', 'ソフトブルー')
    st.markdown(get_css(theme_name), unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🎯 習慣化ジャーナル</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">目標達成と心の成長をサポート</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 ログイン", "✨ 新規登録"])
    
    auth_manager = AuthManager()
    
    with tab1:
        st.subheader("ログイン")
        
        with st.form("login_form"):
            email = st.text_input("📧 メールアドレス", placeholder="example@email.com")
            password = st.text_input("🔒 パスワード", type="password")
            
            if st.form_submit_button("ログイン", type="primary"):
                if email and password:
                    success, nickname = auth_manager.authenticate_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.user_nickname = nickname
                        st.success("ログインしました！")
                        st.rerun()
                    else:
                        st.error("メールアドレスまたはパスワードが間違っています")
                else:
                    st.error("メールアドレスとパスワードを入力してください")
    
    with tab2:
        st.subheader("新規登録")
        
        with st.form("register_form"):
            reg_email = st.text_input("📧 メールアドレス", placeholder="example@email.com", key="reg_email")
            reg_nickname = st.text_input("👤 ニックネーム", placeholder="例: 太郎", key="reg_nickname")
            reg_password = st.text_input("🔒 パスワード", type="password", key="reg_password",
                                       help="8文字以上、英字と数字の両方を含む")
            reg_password_confirm = st.text_input("🔒 パスワード確認", type="password", key="reg_password_confirm")
            
            if st.form_submit_button("新規登録", type="primary"):
                if reg_email and reg_nickname and reg_password and reg_password_confirm:
                    if reg_password != reg_password_confirm:
                        st.error("パスワードが一致しません")
                    elif auth_manager.register_user(reg_email, reg_password, reg_nickname):
                        st.success("登録完了！ログインしてください。")
                else:
                    st.error("すべてのフィールドを入力してください")

def goals_page(goal_manager: GoalManager):
    """目標設定・管理ページ（進捗機能削除）"""
    st.header("🎯 目標設定・管理")
    
    goals = goal_manager.load_goals()
    
    # 新しい目標追加
    with st.expander("➕ 新しい目標を追加", expanded=not goals):
        with st.form("add_goal_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                goal_title = st.text_input("目標タイトル", placeholder="例：英語の勉強を習慣化する")
                goal_category = st.selectbox("期間", ["today", "week", "month","year"], 
                                           format_func=lambda x: {"today": "今日の目標", 
                                                                 "week": "今週の目標", 
                                                                 "month": "今月の目標",
                                                                 "year":"今年の目標"}[x])
            
            with col2:
                goal_deadline = st.date_input("期限", min_value=datetime.date.today())
            
            goal_description = st.text_area("詳細説明（任意）", placeholder="具体的な目標内容、達成方法など")
            
            if st.form_submit_button("目標を追加", type="primary"):
                if goal_title:
                    new_goal = Goal(
                        id=hashlib.md5(f"{goal_title}{datetime.datetime.now()}".encode()).hexdigest(),
                        title=goal_title,
                        description=goal_description or "",
                        category=goal_category,
                        deadline=goal_deadline.strftime("%Y-%m-%d"),
                        action_plans=[],
                        created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    goal_manager.add_goal(new_goal)
                    st.success("目標が追加されました！")
                    st.rerun()
                else:
                    st.error("タイトルを入力してください")
    
    # 既存の目標表示・編集
    if goals:
        st.subheader("📋 現在の目標")
        
        # カテゴリ別に分けて表示
        categories = {
            "today": {"name": "今日の目標", "goals": []},
            "week": {"name": "今週の目標", "goals": []},
            "month": {"name": "今月の目標", "goals": []},
            "year":{"name":"今年の目標","goals":[]}
        }
        
        for goal in goals:
            categories[goal.category]["goals"].append(goal)
        
        for category, data in categories.items():
            if data["goals"]:
                st.markdown(f"### {data['name']}")
                
                for goal in data["goals"]:
                    with st.expander(f"{goal.title}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            if goal.description:
                                st.write(f"**説明:** {goal.description}")
                            st.write(f"**期限:** {goal.deadline}")
                            st.write(f"**作成日:** {goal.created_date}")
                        
                        with col2:
                            if st.button("削除", key=f"delete_{goal.id}"):
                                goal_manager.delete_goal(goal.id)
                                st.success("目標を削除しました！")
                                st.rerun()

                        st.markdown("---")
                        
                        # アクションプラン追加
                        with st.form(f"add_action_{goal.id}"):
                            st.markdown("**📋 アクションプランを追加**")
                            col_a, col_b = st.columns([2, 1])
                            
                            with col_a:
                                action_text = st.text_input("具体的な行動", placeholder="例：朝7時に起きて読書を30分する", key=f"action_{goal.id}")
                            with col_b:
                                action_deadline = st.date_input("実行期限", min_value=datetime.date.today(), key=f"deadline_{goal.id}")
                            
                            if st.form_submit_button("アクションプラン追加", key=f"add_action_btn_{goal.id}"):
                                if action_text:
                                    new_action = ActionPlan(
                                        id=hashlib.md5(f"{action_text}{datetime.datetime.now()}".encode()).hexdigest(),
                                        goal_id=goal.id,
                                        action=action_text,
                                        deadline=action_deadline.strftime("%Y-%m-%d"),
                                        completed=False,
                                        created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    )
                                    goal_manager.add_action_plan(new_action)
                                    st.success("アクションプランを追加しました！")
                                    st.rerun()
                        
                        # 既存のアクションプラン表示
                        if actions:
                            st.markdown("**📝 アクションプラン一覧**")
                            for action in actions:
                                col_x, col_y = st.columns([4, 1])
                                
                                with col_x:
                                    status_icon = "✅" if action.completed else "⏳"
                                    status_style = "text-decoration: line-through; opacity: 0.6;" if action.completed else ""
                                    
                                    st.markdown(f"""
                                    <div class="action-item" style="{status_style}">
                                        {status_icon} <strong>{action.action}</strong><br>
                                        <small>期限: {action.deadline}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_y:
                                    button_text = "完了取消" if action.completed else "完了"
                                    if st.button(button_text, key=f"toggle_{action.id}"):
                                        goal_manager.toggle_action_completion(action.id)
                                        st.rerun()
                        else:
                            st.info("まだアクションプランがありません。上記のフォームから追加してください。")
    else:
        st.info("まだ目標が設定されていません。上記のフォームから目標を追加してください。")

def write_diary_page(diary_manager: DiaryManager, bot: CounselingBot, goal_manager: GoalManager):
    st.header("✍️ 今日の振り返り")
    
    # 目標概要を常時表示
    goals_overview_widget(goal_manager)
    
    if 'diary_saved' not in st.session_state:
        st.session_state.diary_saved = False
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        title = st.text_input("📌 タイトル", placeholder="今日の出来事や気持ち...")
        
        category = st.selectbox(
            "🏷️ カテゴリ",
            ["仕事・学業", "人間関係", "恋愛", "家族", "健康", "その他"]
        )
        
        content = st.text_area(
            "📝 今日の振り返り",
            height=200,
            placeholder="今日の出来事、感じたこと、学んだこと、目標への進捗など... 自由に書いてください。"
        )
    
    with col2:
        selected_mood = mood_selector()
    
    if st.button("💝 記録して相談する", type="primary"):
        if title and content and selected_mood:
            with st.spinner("あなたの気持ちに寄り添っています..."):
                bot_response = bot.get_counseling_response(
                    content, 
                    selected_mood['name'], 
                    selected_mood['intensity'], 
                    category
                )
            
            entry = DiaryEntry(
                date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                title=title,
                content=content,
                mood=selected_mood['name'],
                mood_intensity=selected_mood['intensity'],
                category=category,
                bot_response=bot_response
            )
            
            diary_manager.add_entry(entry)
            st.session_state.diary_saved = True
            
            st.success("記録が保存されました！")
            
            st.markdown('<div class="bot-response">', unsafe_allow_html=True)
            st.markdown("### 🤖 今日のメッセージ")
            st.write(bot_response)
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.error("タイトル、内容、心模様を選択してください。")
    
    if st.session_state.diary_saved:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 続けて記録", type="secondary"):
                st.session_state.diary_saved = False
                st.rerun()
        
        with col2:
            if st.button("🎯 目標を確認"):
                st.session_state.current_page = "🎯 目標設定・管理"
                st.rerun()
        
        with col3:
            if st.button("📚 過去の記録"):
                st.session_state.current_page = "📚 記録を振り返る"
                st.rerun()

def history_page(diary_manager: DiaryManager, goal_manager: GoalManager):
    """記録振り返りページ（グラフ削除、シンプルに）"""
    st.header("📚 記録を振り返る")
    
    # 目標概要を表示
    goals_overview_widget(goal_manager)
    
    entries = diary_manager.load_entries()
    
    if not entries:
        st.info("まだ記録がありません。今日から始めてみましょう。")
        return
    
    # 統計カード（シンプル化）
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("記録日数", len(entries))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if entries:
            avg_mood = sum(entry.mood_intensity for entry in entries) / len(entries)
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("平均気分", f"{avg_mood:.1f}/5")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        goals = goal_manager.load_goals()
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("設定目標数", len(goals))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 検索・フィルター
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 記録を検索", placeholder="キーワードで検索...")
    with col2:
        filter_category = st.selectbox("カテゴリで絞る", ["すべて"] + ["仕事・学業", "人間関係", "恋愛", "家族", "健康", "その他"])
    with col3:
        # 感情カテゴリでフィルター
        mood_categories = list(MOOD_OPTIONS.keys())
        filter_mood_cat = st.selectbox("気持ちで絞る", ["すべて"] + mood_categories)
    
    # フィルタリング
    filtered_entries = entries
    if search_term:
        filtered_entries = [e for e in filtered_entries if search_term.lower() in e.content.lower() or search_term.lower() in e.title.lower()]
    if filter_category != "すべて":
        filtered_entries = [e for e in filtered_entries if e.category == filter_category]
    if filter_mood_cat != "すべて":
        # 選択された感情カテゴリの心模様名リストを取得
        category_moods = [mood['name'] for mood in MOOD_OPTIONS[filter_mood_cat]]
        filtered_entries = [e for e in filtered_entries if e.mood in category_moods]
    
    # エントリー表示
    st.subheader(f"📖 記録一覧 ({len(filtered_entries)}件)")
    
    for entry in reversed(filtered_entries):
        # 心模様の色を取得
        mood_color = "#d3d3d3"  # デフォルト色
        for category, moods in MOOD_OPTIONS.items():
            for mood in moods:
                if mood['name'] == entry.mood:
                    mood_color = mood['color']
                    break
        
        with st.expander(f"{entry.mood} {entry.title} - {entry.date.split()[0]}"):
            st.markdown(f"""
            <div style="border-left: 4px solid {mood_color}; padding-left: 1rem; margin: 0.5rem 0;">
                <strong>心模様:</strong> {entry.mood} (強度: {entry.mood_intensity}/5)<br>
                <strong>カテゴリ:</strong> {entry.category}<br>
                <strong>記録時刻:</strong> {entry.date}
            </div>
            """, unsafe_allow_html=True)
            
            st.write(entry.content)
            
            if entry.bot_response:
                st.markdown("**🤖 その時のメッセージ:**")
                st.info(entry.bot_response)

def main():
    # セッション状態の初期化
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    if 'user_nickname' not in st.session_state:
        st.session_state.user_nickname = ""
    if 'theme_name' not in st.session_state:
        st.session_state.theme_name = "ソフトブルー"
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "✍️ 今日の振り返り"
    if 'selected_mood' not in st.session_state:
        st.session_state.selected_mood = MOOD_OPTIONS["ポジティブ"][0]
    
    # ログインチェック
    if not st.session_state.logged_in:
        login_page()
        return
    
    # CSS適用
    st.markdown(get_css(st.session_state.theme_name), unsafe_allow_html=True)
    
    # フローティング日記ボタン
    if st.session_state.get('current_page') != "✍️ 今日の振り返り":
        st.markdown("""
        <div class="floating-write-btn" onclick="location.reload();">
            ✍️ 振り返り
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🎯 習慣化ジャーナル</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">目標達成と心の成長をサポート</div>', unsafe_allow_html=True)
    
    # ヘッダーコントロール（リフレッシュボタン削除）
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.write(f"こんにちは、{st.session_state.user_nickname}さん")
    with col2:
        # テーマ変更（ワンボタン）
        if st.button("🎨", help="テーマ変更"):
            themes = list(THEME_PALETTES.keys())
            current_idx = themes.index(st.session_state.theme_name) if st.session_state.theme_name in themes else 0
            next_idx = (current_idx + 1) % len(themes)
            st.session_state.theme_name = themes[next_idx]
            st.rerun()
    with col3:
        if st.button("ログアウト"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_nickname = ""
            st.rerun()
    
    # サイドバー（シンプルに）
    st.sidebar.title("📝 メニュー")
    
    page = st.sidebar.selectbox(
        "ページを選択",
        ["✍️ 今日の振り返り", "🎯 目標設定・管理", "📚 記録を振り返る", "🔧 設定"],
        index=0
    )
    
    if page != st.session_state.current_page:
        st.session_state.current_page = page
    
    # インスタンス作成
    diary_manager = DiaryManager(st.session_state.user_email)
    goal_manager = GoalManager(st.session_state.user_email)
    bot = CounselingBot()
    
    # ページルーティング
    if page == "✍️ 今日の振り返り":
        write_diary_page(diary_manager, bot, goal_manager)
    elif page == "🎯 目標設定・管理":
        goals_page(goal_manager)
    elif page == "📚 記録を振り返る":
        history_page(diary_manager, goal_manager)
    else:
        st.header("🔧 設定")
        st.markdown(f"""
        **現在のテーマ:** {st.session_state.theme_name}
        
        **ニックネーム:** {st.session_state.user_nickname}
        
        **利用可能なテーマ:**
        {', '.join(THEME_PALETTES.keys())}
        
        テーマは画面上部の🎨ボタンで切り替えできます。
        """)

if __name__ == "__main__":
    main()