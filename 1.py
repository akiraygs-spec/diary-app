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

# 淡色テーマカラー定義
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
    }
}

# 心模様の定義（5色×5種類 = 25種類、感情別に整理）
MOOD_OPTIONS = {
    "とても良い": {
        "color": "#87ceeb",  # ソフトブルー
        "moods": [
            {"name": "最高", "intensity": 5},
            {"name": "幸せ", "intensity": 5},
            {"name": "大満足", "intensity": 5},
            {"name": "感激", "intensity": 5},
            {"name": "やる気満々", "intensity": 5}
        ]
    },
    "良い": {
        "color": "#98fb98",  # ミントグリーン
        "moods": [
            {"name": "嬉しい", "intensity": 4},
            {"name": "楽しい", "intensity": 4},
            {"name": "満足", "intensity": 4},
            {"name": "前向き", "intensity": 4},
            {"name": "充実", "intensity": 4}
        ]
    },
    "普通": {
        "color": "#d3d3d3",  # グレー
        "moods": [
            {"name": "普通", "intensity": 3},
            {"name": "平静", "intensity": 3},
            {"name": "落ち着き", "intensity": 3},
            {"name": "まあまあ", "intensity": 3},
            {"name": "いつも通り", "intensity": 3}
        ]
    },
    "少し落ち込み": {
        "color": "#ffdab9",  # ピーチクリーム
        "moods": [
            {"name": "少し疲れ", "intensity": 2},
            {"name": "モヤモヤ", "intensity": 2},
            {"name": "不安", "intensity": 2},
            {"name": "心配", "intensity": 2},
            {"name": "退屈", "intensity": 2}
        ]
    },
    "落ち込み": {
        "color": "#ffc0cb",  # パステルピンク
        "moods": [
            {"name": "悲しい", "intensity": 1},
            {"name": "辛い", "intensity": 1},
            {"name": "イライラ", "intensity": 1},
            {"name": "落ち込み", "intensity": 1},
            {"name": "憂鬱", "intensity": 1}
        ]
    }
}

# カスタムCSS
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
    
    .goal-progress {{
        font-size: 0.75rem;
        opacity: 0.8;
        margin-top: 4px;
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
    
    /* 心模様選択セクション */
    .mood-section {{
        margin: 1.5rem 0;
        padding: 1.2rem;
        background: {theme['card']};
        border-radius: 12px;
        border: 1px solid {theme['border']};
    }}
    
    .mood-section h4 {{
        margin: 0 0 0.8rem 0;
        color: {theme['text_primary']};
        font-size: 1rem;
        font-weight: 600;
    }}
    
    .mood-circle {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: inline-block;
        margin: 8px;
        border: 3px solid rgba(255,255,255,0.7);
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 3px 10px rgba(0,0,0,0.15);
        position: relative;
    }}
    
    .mood-circle:hover {{
        transform: scale(1.2);
        box-shadow: 0 5px 20px rgba(0,0,0,0.25);
        border-color: {theme['primary']};
    }}
    
    .mood-circle.selected {{
        border: 4px solid {theme['primary']};
        transform: scale(1.3);
        box-shadow: 0 6px 25px {theme['shadow']};
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1.3); }}
        50% {{ transform: scale(1.35); }}
        100% {{ transform: scale(1.3); }}
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
    
    /* 行動プランカード */
    .action-plan-card {{
        background: {theme['card']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }}
    
    .action-plan-card:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 15px {theme['shadow']};
    }}
    
    .action-plan-completed {{
        background: linear-gradient(135deg, rgba(152, 251, 152, 0.2) 0%, rgba(144, 238, 144, 0.1) 100%);
        border-color: #90ee90;
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
    
    /* 目標達成度表示 */
    .goal-achievement {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 8px;
    }}
    
    .achievement-bar {{
        flex: 1;
        height: 6px;
        background: rgba(255,255,255,0.3);
        border-radius: 3px;
        overflow: hidden;
    }}
    
    .achievement-fill {{
        height: 100%;
        background: linear-gradient(90deg, #90ee90 0%, #32cd32 100%);
        transition: width 0.3s ease;
    }}
</style>
"""

@dataclass
class Goal:
    id: str
    title: str
    description: str
    category: str  # "daily", "weekly", "monthly", "yearly"
    created_date: str
    user_email: str = ""

@dataclass
class ActionPlan:
    id: str
    goal_id: str
    title: str
    description: str
    completed: bool = False
    created_date: str = ""
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

def get_period_end_date(category: str) -> str:
    """カテゴリに応じて自動的に期限を計算"""
    today = datetime.date.today()
    
    if category == "daily":
        return today.strftime("%Y-%m-%d")
    elif category == "weekly":
        # 今週の日曜日まで
        days_until_sunday = (6 - today.weekday()) % 7
        end_date = today + datetime.timedelta(days=days_until_sunday)
        return end_date.strftime("%Y-%m-%d")
    elif category == "monthly":
        # 今月の最終日まで
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        end_date = next_month - datetime.timedelta(days=1)
        return end_date.strftime("%Y-%m-%d")
    else:  # yearly
        # 今年の12月31日まで
        end_date = today.replace(month=12, day=31)
        return end_date.strftime("%Y-%m-%d")

class ActionPlanManager:
    def __init__(self, user_email: str = ""):
        self.user_email = user_email
        self.plans_file = f"action_plans_{hashlib.md5(user_email.encode()).hexdigest()}.json" if user_email else "action_plans.json"
    
    def load_plans(self) -> List[ActionPlan]:
        try:
            if os.path.exists(self.plans_file):
                with open(self.plans_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    plans = []
                    for plan_data in data:
                        plans.append(ActionPlan(**plan_data))
                    return plans
        except:
            pass
        return []
    
    def save_plans(self, plans: List[ActionPlan]):
        try:
            with open(self.plans_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(plan) for plan in plans], f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"行動プランの保存に失敗しました: {e}")
    
    def add_plan(self, plan: ActionPlan):
        plan.user_email = self.user_email
        plans = self.load_plans()
        plans.append(plan)
        self.save_plans(plans)
    
    def update_plan_status(self, plan_id: str, completed: bool):
        plans = self.load_plans()
        for plan in plans:
            if plan.id == plan_id:
                plan.completed = completed
                break
        self.save_plans(plans)
    
    def delete_plan(self, plan_id: str):
        plans = self.load_plans()
        plans = [plan for plan in plans if plan.id != plan_id]
        self.save_plans(plans)

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
                        # 古いデータとの互換性のため
                        if 'deadline' in goal_data:
                            del goal_data['deadline']
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
        pass
        
    def get_counseling_response(self, content: str, mood: str, mood_intensity: int, category: str) -> str:
        intensity_responses = {
            1: "辛い気持ちを抱えているのですね。でも、その気持ちを振り返って記録する勇気があることは素晴らしいです。一歩ずつ進んでいきましょう。",
            2: "少し重い気持ちの時もありますね。そんな日もあって当然です。自分を責めず、優しく受け止めてあげてください。",
            3: "穏やかな心持ちですね。この平静さを保ちながら、目標に向かって歩んでいきましょう。",
            4: "前向きな気持ちが伝わってきます。この調子で目標達成に向けて進んでいけそうですね。",
            5: "素晴らしい気持ちですね！この前向きなエネルギーを目標達成に活かしていきましょう。"
        }
        
        base_response = intensity_responses.get(mood_intensity, "今日もお疲れ様です。")
        
        goal_advice = "毎日の小さな積み重ねが、大きな目標達成につながります。今日も一歩前進できましたね。明日も自分のペースで続けていきましょう。"
        
        return f"{base_response}\n\n{goal_advice}\n\nあなたの成長を心から応援しています 🌟"

def goals_overview_widget(goal_manager: GoalManager, action_plan_manager: ActionPlanManager):
    """目標概要ウィジェット（習慣化フォーカス）"""
    goals = goal_manager.load_goals()
    action_plans = action_plan_manager.load_plans()
    
    if not goals:
        st.markdown("""
        <div class="goals-overview">
            <h3 style="margin-bottom: 1rem; color: var(--primary-color);">🎯 目標を設定して習慣化を始めましょう</h3>
            <p style="color: var(--text-secondary); margin: 0;">まずは目標設定ページで今日・今週・今月・今年の目標を設定してください</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # カテゴリ別に分類
    daily_goals = [g for g in goals if g.category == "daily"]
    weekly_goals = [g for g in goals if g.category == "weekly"]
    monthly_goals = [g for g in goals if g.category == "monthly"]
    yearly_goals = [g for g in goals if g.category == "yearly"]
    
    goals_html = f"""
    <div class="goals-overview">
        <h3 style="margin-bottom: 1rem;">🎯 習慣化目標の進捗</h3>
    """
    
    # 今日の目標
    if daily_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'>📅 今日の目標</h4>"
        for goal in daily_goals[:2]:
            goal_plans = [p for p in action_plans if p.goal_id == goal.id]
            completed_plans = [p for p in goal_plans if p.completed]
            
            # 期限チェック
            deadline = get_period_end_date(goal.category)
            today = datetime.date.today().strftime("%Y-%m-%d")
            is_deadline = deadline == today
            
            deadline_indicator = "🔔 今日が期限！振り返りを忘れずに" if is_deadline else ""
            
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
                <div class="goal-progress">行動プラン: {len(completed_plans)}/{len(goal_plans)} 実行済み</div>
                {f'<div style="color: #ff6b6b; font-size: 0.8rem; font-weight: 600; margin-top: 4px;">{deadline_indicator}</div>' if is_deadline else ''}
            </div>
            """
    
    # 今週の目標
    if weekly_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'>📊 今週の目標</h4>"
        for goal in weekly_goals[:2]:
            goal_plans = [p for p in action_plans if p.goal_id == goal.id]
            completed_plans = [p for p in goal_plans if p.completed]
            
            deadline = get_period_end_date(goal.category)
            today = datetime.date.today().strftime("%Y-%m-%d")
            is_deadline = deadline == today
            
            deadline_indicator = "🔔 今日が期限！振り返りを忘れずに" if is_deadline else ""
            
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
                <div class="goal-progress">行動プラン: {len(completed_plans)}/{len(goal_plans)} 実行済み</div>
                {f'<div style="color: #ff6b6b; font-size: 0.8rem; font-weight: 600; margin-top: 4px;">{deadline_indicator}</div>' if is_deadline else ''}
            </div>
            """
    
    # 今月の目標
    if monthly_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'>🗓️ 今月の目標</h4>"
        for goal in monthly_goals[:2]:
            goal_plans = [p for p in action_plans if p.goal_id == goal.id]
            completed_plans = [p for p in goal_plans if p.completed]
            
            deadline = get_period_end_date(goal.category)
            today = datetime.date.today().strftime("%Y-%m-%d")
            is_deadline = deadline == today
            
            deadline_indicator = "🔔 今日が期限！振り返りを忘れずに" if is_deadline else ""
            
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
                <div class="goal-progress">行動プラン: {len(completed_plans)}/{len(goal_plans)} 実行済み</div>
                {f'<div style="color: #ff6b6b; font-size: 0.8rem; font-weight: 600; margin-top: 4px;">{deadline_indicator}</div>' if is_deadline else ''}
            </div>
            """
    
    # 今年の目標
    if yearly_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'>🌟 今年の目標</h4>"
        for goal in yearly_goals[:1]:
            goal_plans = [p for p in action_plans if p.goal_id == goal.id]
            completed_plans = [p for p in goal_plans if p.completed]
            
            deadline = get_period_end_date(goal.category)
            today = datetime.date.today().strftime("%Y-%m-%d")
            is_deadline = deadline == today
            
            deadline_indicator = "🔔 今日が期限！振り返りを忘れずに" if is_deadline else ""
            
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
                <div class="goal-progress">行動プラン: {len(completed_plans)}/{len(goal_plans)} 実行済み</div>
                {f'<div style="color: #ff6b6b; font-size: 0.8rem; font-weight: 600; margin-top: 4px;">{deadline_indicator}</div>' if is_deadline else ''}
            </div>
            """
    
    goals_html += "</div>"
    st.markdown(goals_html, unsafe_allow_html=True)

def mood_selector():
    """改良された心模様選択UI（5色分類版・直感的選択）"""
    st.subheader("今の心模様は？")
    
    selected_mood = st.session_state.get('selected_mood')
    if not selected_mood:
        st.session_state.selected_mood = {"name": "普通", "intensity": 3, "category": "普通"}
        selected_mood = st.session_state.selected_mood
    
    for category, data in MOOD_OPTIONS.items():
        st.markdown(f'<div class="mood-section">', unsafe_allow_html=True)
        st.markdown(f"<h4>{category}</h4>", unsafe_allow_html=True)
        
        # 各心模様の選択ボタン
        cols = st.columns(len(data["moods"]))
        for i, mood in enumerate(data["moods"]):
            with cols[i]:
                is_selected = selected_mood.get('name') == mood['name']
                
                # ボタンとして表示（見た目は円）
                if st.button(
                    mood['name'], 
                    key=f"mood_{category}_{mood['name']}", 
                    help=f"{mood['name']} (強度: {mood['intensity']}/5)",
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.selected_mood = {
                        "name": mood['name'],
                        "intensity": mood['intensity'],
                        "category": category
                    }
                    st.rerun()
                
                # 視覚的な円を表示（選択状態を示す）
                selected_class = "selected" if is_selected else ""
                st.markdown(f"""
                <div class="mood-circle {selected_class}" 
                     style="background-color: {data['color']}; margin: 4px auto; display: block;" 
                     title="{mood['name']}">
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return st.session_state.selected_mood

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

def goals_page(goal_manager: GoalManager, action_plan_manager: ActionPlanManager):
    """目標設定・管理ページ（習慣化フォーカス、期限自動計算）"""
    st.header("🎯 習慣化目標の設定・管理")
    
    tab1, tab2 = st.tabs(["🎯 目標設定", "📋 行動習慣プラン"])
    
    with tab1:
        goals = goal_manager.load_goals()
        
        st.info("💡 **習慣化のコツ**: 小さく始めて継続することが重要です。無理のない目標から始めましょう。")
        
        # 新しい目標追加
        with st.expander("➕ 新しい習慣化目標を追加", expanded=not goals):
            with st.form("add_goal_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    goal_title = st.text_input("習慣化したい目標", placeholder="例：毎日30分読書する")
                    goal_category = st.selectbox("達成期間", ["daily", "weekly", "monthly", "yearly"], 
                                               format_func=lambda x: {
                                                   "daily": "📅 毎日の習慣 (今日中に実行)",
                                                   "weekly": "📊 週間目標 (今週中に達成)", 
                                                   "monthly": "🗓️ 月間目標 (今月中に達成)", 
                                                   "yearly": "🌟 年間目標 (今年中に達成)"
                                               }[x])
                
                with col2:
                    # 期間の説明のみ表示（期限は表示しない）
                    period_description = {
                        "daily": "毎日継続する習慣として設定されます",
                        "weekly": "今週中に達成する目標として設定されます",
                        "monthly": "今月中に達成する目標として設定されます",
                        "yearly": "今年中に達成する目標として設定されます"
                    }[goal_category]
                    
                    st.write("**設定内容:**")
                    st.info(period_description)
                
                goal_description = st.text_area("詳細・なぜこの目標を達成したいか", 
                                              placeholder="この目標を達成する理由、期待する効果、具体的な方法など...")
                
                if st.form_submit_button("習慣化目標を追加", type="primary"):
                    if goal_title:
                        new_goal = Goal(
                            id=hashlib.md5(f"{goal_title}{datetime.datetime.now()}".encode()).hexdigest(),
                            title=goal_title,
                            description=goal_description or "",
                            category=goal_category,
                            created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        goal_manager.add_goal(new_goal)
                        st.success("目標が追加されました！次に行動プランを作成しましょう。")
                        st.rerun()
                    else:
                        st.error("目標タイトルを入力してください")
        
        # 既存の目標表示・編集
        if goals:
            st.subheader("📋 現在の習慣化目標")
            
            # カテゴリ別に分けて表示
            categories = {
                "daily": {"name": "📅 毎日の習慣", "goals": []},
                "weekly": {"name": "📊 週間目標", "goals": []},
                "monthly": {"name": "🗓️ 月間目標", "goals": []},
                "yearly": {"name": "🌟 年間目標", "goals": []}
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
                                    st.write(f"**詳細:** {goal.description}")
                                
                                # 自動期限を表示（削除）
                                auto_deadline = get_period_end_date(goal.category)
                                st.write(f"**期限:** {auto_deadline}")
                                st.write(f"**作成日:** {goal.created_date}")
                                
                                # 行動プラン数を表示（%削除）
                                goal_plans = [p for p in action_plan_manager.load_plans() if p.goal_id == goal.id]
                                completed_plans = [p for p in goal_plans if p.completed]
                                
                                st.write(f"**行動プラン:** {len(completed_plans)}/{len(goal_plans)} 実行済み")
                            
                            with col2:
                                if st.button("削除", key=f"delete_{goal.id}"):
                                    goal_manager.delete_goal(goal.id)
                                    # 関連する行動プランも削除
                                    plans = action_plan_manager.load_plans()
                                    remaining_plans = [p for p in plans if p.goal_id != goal.id]
                                    action_plan_manager.save_plans(remaining_plans)
                                    st.success("目標を削除しました！")
                                    st.rerun()
        else:
            st.info("まだ目標が設定されていません。上記のフォームから最初の習慣化目標を追加してください。")
    
    with tab2:
        # 行動プラン管理
        goals = goal_manager.load_goals()
        action_plans = action_plan_manager.load_plans()
        
        if not goals:
            st.info("まず目標を設定してから行動習慣プランを作成してください。")
            return
        
        st.info("💡 **行動習慣プランのコツ**: 具体的で実行しやすい小さな行動に分解することが成功の鍵です。")
        
        # 新しい行動プラン追加
        with st.expander("➕ 新しい行動習慣プランを追加", expanded=not action_plans):
            with st.form("add_action_plan_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_goal = st.selectbox(
                        "どの目標の行動プランですか？",
                        goals,
                        format_func=lambda x: f"{x.title} ({{'daily': '毎日', 'weekly': '週間', 'monthly': '月間', 'yearly': '年間'}}[x.category])"
                    )
                    plan_title = st.text_input("行動習慣プランのタイトル", placeholder="例：朝食後に15分読書")
                
                with col2:
                    plan_description = st.text_area("具体的な実行方法", 
                                                  placeholder="いつ、どこで、どのように実行するかを具体的に...")
                
                if st.form_submit_button("行動習慣プランを追加", type="primary"):
                    if selected_goal and plan_title:
                        new_plan = ActionPlan(
                            id=hashlib.md5(f"{plan_title}{datetime.datetime.now()}".encode()).hexdigest(),
                            goal_id=selected_goal.id,
                            title=plan_title,
                            description=plan_description or "",
                            completed=False,
                            created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        action_plan_manager.add_plan(new_plan)
                        st.success("行動習慣プランが追加されました！")
                        st.rerun()
                    else:
                        st.error("目標とタイトルを入力してください")
        
        # 既存の行動プラン表示
        if action_plans:
            st.subheader("📋 行動習慣プラン一覧")
            
            # 目標別に行動プランをグループ化
            for goal in goals:
                goal_plans = [p for p in action_plans if p.goal_id == goal.id]
                if goal_plans:
                    completion_rate = len([p for p in goal_plans if p.completed]) / len(goal_plans) * 100
                    
                    st.markdown(f"### {goal.title} (達成率: {completion_rate:.0f}%)")
                    
                    for plan in goal_plans:
                        plan_class = "action-plan-completed" if plan.completed else ""
                        
                        st.markdown(f'<div class="action-plan-card {plan_class}">', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([4, 1, 1])
                        
                        with col1:
                            st.write(f"**{plan.title}**")
                            if plan.description:
                                st.write(f"*{plan.description}*")
                        
                        with col2:
                            current_status = plan.completed
                            new_status = st.checkbox("完了", value=current_status, key=f"plan_status_{plan.id}")
                            if new_status != current_status:
                                action_plan_manager.update_plan_status(plan.id, new_status)
                                st.rerun()
                        
                        with col3:
                            if st.button("削除", key=f"delete_plan_{plan.id}"):
                                action_plan_manager.delete_plan(plan.id)
                                st.success("行動習慣プランを削除しました！")
                                st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("まだ行動習慣プランが作成されていません。上記のフォームから行動習慣プランを追加してください。")

def write_diary_page(diary_manager: DiaryManager, bot: CounselingBot, goal_manager: GoalManager, action_plan_manager: ActionPlanManager):
    st.header("✍️ 今日の振り返り")
    
    # 目標概要を常時表示
    goals_overview_widget(goal_manager, action_plan_manager)
    
    if 'diary_saved' not in st.session_state:
        st.session_state.diary_saved = False
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        title = st.text_input("📌 タイトル", placeholder="今日の出来事や気持ち...")
        
        category = st.selectbox(
            "🏷️ カテゴリ",
            ["目標達成・習慣化", "仕事・学業", "人間関係", "恋愛", "家族", "健康", "その他"]
        )
        
        content = st.text_area(
            "📝 今日の振り返り",
            height=200,
            placeholder="""今日の出来事、感じたこと、学んだことを自由に書いてください。

特に以下について振り返ってみましょう：
• 設定した目標に向けてどんな行動ができましたか？
• 習慣化したい行動は実行できましたか？
• 今日の気持ちや体調はいかがでしたか？
• 明日はどんなことを意識したいですか？"""
        )
    
    with col2:
        selected_mood = mood_selector()
    
    if st.button("💝 記録して振り返りのアドバイスをもらう", type="primary"):
        if title and content and selected_mood:
            with st.spinner("あなたの振り返りを分析しています..."):
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
            st.markdown("### 🤖 今日の振り返りアドバイス")
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

def history_page(diary_manager: DiaryManager, goal_manager: GoalManager, action_plan_manager: ActionPlanManager):
    """記録振り返りページ（習慣化フォーカス）"""
    st.header("📚 習慣化の記録を振り返る")
    
    # 目標概要を表示
    goals_overview_widget(goal_manager, action_plan_manager)
    
    entries = diary_manager.load_entries()
    
    if not entries:
        st.info("まだ記録がありません。今日から習慣化ジャーナルを始めてみましょう。")
        return
    
    # 習慣化統計カード
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("継続日数", len(entries))
        st.caption("ジャーナル記録")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if entries:
            avg_mood = sum(entry.mood_intensity for entry in entries) / len(entries)
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("平均気分", f"{avg_mood:.1f}/5")
            st.caption("心の健康度")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        goals = goal_manager.load_goals()
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("設定目標数", len(goals))
        st.caption("習慣化目標")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        action_plans = action_plan_manager.load_plans()
        completed_plans = [p for p in action_plans if p.completed]
        completion_rate = len(completed_plans) / len(action_plans) * 100 if action_plans else 0
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("習慣達成率", f"{completion_rate:.1f}%")
        st.caption(f"{len(completed_plans)}/{len(action_plans)} 完了")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 検索・フィルター
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 記録を検索", placeholder="キーワードで検索...")
    with col2:
        filter_category = st.selectbox("カテゴリで絞る", 
                                     ["すべて"] + ["目標達成・習慣化", "仕事・学業", "人間関係", "恋愛", "家族", "健康", "その他"])
    with col3:
        # 気分の範囲でフィルター
        mood_categories = list(MOOD_OPTIONS.keys())
        mood_filter = st.selectbox("気分で絞る", ["すべて"] + mood_categories)
    
    # フィルタリング
    filtered_entries = entries
    if search_term:
        filtered_entries = [e for e in filtered_entries if search_term.lower() in e.content.lower() or search_term.lower() in e.title.lower()]
    if filter_category != "すべて":
        filtered_entries = [e for e in filtered_entries if e.category == filter_category]
    if mood_filter != "すべて":
        # 選択された感情カテゴリの心模様名リストを取得
        category_moods = [mood['name'] for mood in MOOD_OPTIONS[mood_filter]["moods"]]
        filtered_entries = [e for e in filtered_entries if e.mood in category_moods]
    
    # エントリー表示
    st.subheader(f"📖 記録一覧 ({len(filtered_entries)}件)")
    
    for entry in reversed(filtered_entries):
        # 心模様の色を取得
        mood_color = "#d3d3d3"  # デフォルト色
        for category, data in MOOD_OPTIONS.items():
            for mood in data["moods"]:
                if mood['name'] == entry.mood:
                    mood_color = data['color']
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
                st.markdown("**🤖 その時の振り返りアドバイス:**")
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
        st.session_state.selected_mood = {"name": "普通", "intensity": 3, "category": "普通"}
    
    # ログインチェック
    if not st.session_state.logged_in:
        login_page()
        return
    
    # CSS適用
    st.markdown(get_css(st.session_state.theme_name), unsafe_allow_html=True)
    
    # フローティング日記ボタン（修正版）
    if st.session_state.get('current_page') != "✍️ 今日の振り返り":
        # JavaScriptを使って確実にページ遷移させる
        st.markdown("""
        <div class="floating-write-btn" onclick="changeToWritePage();">
            ✍️ 振り返り
        </div>
        <script>
        function changeToWritePage() {
            // Streamlitの内部で使えるrerunを呼び出す
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: {
                    key: 'change_page',
                    value: 'write_diary'
                }
            }, '*');
        }
        </script>
        """, unsafe_allow_html=True)
        
        # 隠しボタンでページ遷移を処理
        if st.button("", key="hidden_write_button", help="振り返りページへ"):
            st.session_state.current_page = "✍️ 今日の振り返り"
            st.rerun()
    
    st.markdown('<h1 class="main-header">🎯 習慣化ジャーナル</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">目標達成と心の成長をサポート</div>', unsafe_allow_html=True)
    
    # ヘッダーコントロール
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.write(f"こんにちは、{st.session_state.user_nickname}さん")
    with col2:
        # テーマ変更
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
    
    # サイドバー
    st.sidebar.title("📝 メニュー")
    
    # selectboxを無効化するCSS（より確実な方法）
    st.markdown("""
    <style>
    .stSelectbox label {
        pointer-events: none !important;
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
    }
    .stSelectbox label p {
        pointer-events: none !important;
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
    }
    .stSelectbox [data-testid="stMarkdownContainer"] {
        pointer-events: none !important;
        user-select: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 固定ラベルでselectboxを表示
    page = st.sidebar.selectbox(
        ".", # 最小限のラベル
        ["✍️ 今日の振り返り", "🎯 目標設定・管理", "📚 記録を振り返る", "🔧 設定"],
        index=0,
        label_visibility="collapsed"  # ラベルを非表示
    )
    
    # サイドバーにページ選択説明を追加
    st.sidebar.markdown("**ページを選択:**")
    
    if page != st.session_state.current_page:
        st.session_state.current_page = page
    
    # インスタンス作成
    diary_manager = DiaryManager(st.session_state.user_email)
    goal_manager = GoalManager(st.session_state.user_email)
    action_plan_manager = ActionPlanManager(st.session_state.user_email)
    bot = CounselingBot()
    
    # ページルーティング
    if page == "✍️ 今日の振り返り":
        write_diary_page(diary_manager, bot, goal_manager, action_plan_manager)
    elif page == "🎯 目標設定・管理":
        goals_page(goal_manager, action_plan_manager)
    elif page == "📚 記録を振り返る":
        history_page(diary_manager, goal_manager, action_plan_manager)
    else:
        st.header("🔧 設定")
        st.markdown(f"""
        **現在のテーマ:** {st.session_state.theme_name}
        
        **ニックネーム:** {st.session_state.user_nickname}
        
        **利用可能なテーマ:**
        {', '.join(THEME_PALETTES.keys())}
        
        テーマは画面上部の🎨ボタンで切り替えできます。
        
        **📊 あなたの習慣化統計:**
        """)
        
        # 習慣化統計表示
        entries = diary_manager.load_entries()
        goals = goal_manager.load_goals()
        action_plans = action_plan_manager.load_plans()
        
        if entries or goals or action_plans:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("総記録日数", len(entries))
                if entries:
                    avg_mood = sum(entry.mood_intensity for entry in entries) / len(entries)
                    st.metric("平均気分スコア", f"{avg_mood:.1f}/5")
                
                # 継続率計算（過去7日）
                recent_entries = [e for e in entries if (datetime.datetime.now() - datetime.datetime.strptime(e.date.split()[0], "%Y-%m-%d")).days <= 7]
                continuation_rate = len(recent_entries) / 7 * 100
                st.metric("週間継続率", f"{continuation_rate:.1f}%")
            
            with col2:
                st.metric("設定目標数", len(goals))
                daily_goals = [g for g in goals if g.category == "daily"]
                weekly_goals = [g for g in goals if g.category == "weekly"]
                monthly_goals = [g for g in goals if g.category == "monthly"]
                yearly_goals = [g for g in goals if g.category == "yearly"]
                
                st.write(f"📅 毎日の習慣: {len(daily_goals)}個")
                st.write(f"📊 週間目標: {len(weekly_goals)}個")
                st.write(f"🗓️ 月間目標: {len(monthly_goals)}個")
                st.write(f"🌟 年間目標: {len(yearly_goals)}個")
            
            with col3:
                st.metric("行動プラン数", len(action_plans))
                completed_plans = [p for p in action_plans if p.completed]
                completion_rate = len(completed_plans) / len(action_plans) * 100 if action_plans else 0
                st.metric("全体達成率", f"{completion_rate:.1f}%")
                
                # カテゴリ別達成率
                if daily_goals:
                    daily_plans = [p for p in action_plans for g in daily_goals if p.goal_id == g.id]
                    daily_completed = [p for p in daily_plans if p.completed]
                    daily_rate = len(daily_completed) / len(daily_plans) * 100 if daily_plans else 0
                    st.write(f"📅 毎日の習慣達成率: {daily_rate:.1f}%")
        else:
            st.info("まだデータがありません。習慣化ジャーナルを始めましょう！")

if __name__ == "__main__":
    main()