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
    page_title="心の整理帳 - お悩み相談Bot + 日記",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 背景色テーマの定義（色分けで直感的に）
BACKGROUND_THEMES = {
    "青系": {
        "淡い青": {"bg_color": "#f8fbff", "sidebar_bg": "#f0f7ff", "card_bg": "rgba(240, 247, 255, 0.6)", "accent": "#e3f2fd", "preview": "#bbdefb"},
        "アイス青": {"bg_color": "#f1f8ff", "sidebar_bg": "#e8f4ff", "card_bg": "rgba(232, 244, 255, 0.6)", "accent": "#e1f5fe", "preview": "#b3e5fc"},
        "ソフト青": {"bg_color": "#f0f8ff", "sidebar_bg": "#e6f3ff", "card_bg": "rgba(230, 243, 255, 0.6)", "accent": "#e0f2f1", "preview": "#b2dfdb"}
    },
    "ピンク系": {
        "ソフトピンク": {"bg_color": "#fef9f9", "sidebar_bg": "#fdf2f2", "card_bg": "rgba(253, 242, 242, 0.6)", "accent": "#fce4ec", "preview": "#f8bbd9"},
        "ローズ": {"bg_color": "#fff8f8", "sidebar_bg": "#fef0f0", "card_bg": "rgba(254, 240, 240, 0.6)", "accent": "#fce4ec", "preview": "#f48fb1"},
        "チェリー": {"bg_color": "#fff5f5", "sidebar_bg": "#ffebeb", "card_bg": "rgba(255, 235, 235, 0.6)", "accent": "#ffebee", "preview": "#f06292"}
    },
    "緑系": {
        "やわらか緑": {"bg_color": "#f7fcf7", "sidebar_bg": "#f1f8f1", "card_bg": "rgba(241, 248, 241, 0.6)", "accent": "#e8f5e8", "preview": "#c8e6c9"},
        "ミント": {"bg_color": "#f7fffe", "sidebar_bg": "#f0fffe", "card_bg": "rgba(240, 255, 254, 0.6)", "accent": "#e0f2f1", "preview": "#b2dfdb"},
        "フォレスト": {"bg_color": "#f8fff8", "sidebar_bg": "#f0fef0", "card_bg": "rgba(240, 254, 240, 0.6)", "accent": "#e8f8e8", "preview": "#a5d6a7"}
    },
    "紫系": {
        "ラベンダー": {"bg_color": "#faf9fc", "sidebar_bg": "#f5f3f8", "card_bg": "rgba(245, 243, 248, 0.6)", "accent": "#f3e5f5", "preview": "#ce93d8"},
        "ライラック": {"bg_color": "#fdfbff", "sidebar_bg": "#f8f5ff", "card_bg": "rgba(248, 245, 255, 0.6)", "accent": "#f3e5f5", "preview": "#ba68c8"},
        "アメジスト": {"bg_color": "#fcf9ff", "sidebar_bg": "#f6f0ff", "card_bg": "rgba(246, 240, 255, 0.6)", "accent": "#ede7f6", "preview": "#9575cd"}
    },
    "オレンジ系": {
        "ピーチ": {"bg_color": "#fff9f7", "sidebar_bg": "#fff4f0", "card_bg": "rgba(255, 244, 240, 0.6)", "accent": "#ffe0d4", "preview": "#ffab91"},
        "アプリコット": {"bg_color": "#fffaf8", "sidebar_bg": "#fff6f2", "card_bg": "rgba(255, 246, 242, 0.6)", "accent": "#ffe0d4", "preview": "#ff8a65"},
        "コーラル": {"bg_color": "#fffbf9", "sidebar_bg": "#fff7f3", "card_bg": "rgba(255, 247, 243, 0.6)", "accent": "#ffe0d4", "preview": "#ff7043"}
    },
    "その他": {
        "クリーム": {"bg_color": "#fffef8", "sidebar_bg": "#fffcf0", "card_bg": "rgba(255, 252, 240, 0.6)", "accent": "#fff8e1", "preview": "#fff176"},
        "やさしいグレー": {"bg_color": "#fafafa", "sidebar_bg": "#f5f5f5", "card_bg": "rgba(245, 245, 245, 0.6)", "accent": "#f0f0f0", "preview": "#e0e0e0"}
    }
}

# 心模様の定義（20種類、色分け）
MOOD_OPTIONS = [
    {"name": "喜び", "color": "#ffeb3b", "intensity": 5},
    {"name": "幸福", "color": "#ffc107", "intensity": 5},
    {"name": "安らぎ", "color": "#81c784", "intensity": 4},
    {"name": "満足", "color": "#64b5f6", "intensity": 4},
    {"name": "穏やか", "color": "#a5d6a7", "intensity": 3},
    {"name": "平静", "color": "#b0bec5", "intensity": 3},
    {"name": "普通", "color": "#e0e0e0", "intensity": 2},
    {"name": "少し憂鬱", "color": "#90a4ae", "intensity": 2},
    {"name": "悲しみ", "color": "#64b5f6", "intensity": 1},
    {"name": "不安", "color": "#ffb74d", "intensity": 1},
    {"name": "心配", "color": "#ffcc02", "intensity": 1},
    {"name": "イライラ", "color": "#ff8a65", "intensity": 1},
    {"name": "怒り", "color": "#ef5350", "intensity": 0},
    {"name": "絶望", "color": "#424242", "intensity": 0},
    {"name": "疲労", "color": "#9e9e9e", "intensity": 1},
    {"name": "退屈", "color": "#bdbdbd", "intensity": 2},
    {"name": "混乱", "color": "#ba68c8", "intensity": 1},
    {"name": "孤独", "color": "#5c6bc0", "intensity": 1},
    {"name": "希望", "color": "#42a5f5", "intensity": 4},
    {"name": "感謝", "color": "#66bb6a", "intensity": 5}
]

# 瞑想音源の定義
MEDITATION_SOUNDS = {
    "自然音": {
        "雨音": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "波音": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "鳥のさえずり": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "風の音": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
    },
    "癒し音": {
        "チベット鈴": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "水滴": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "シンギングボウル": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "ホワイトノイズ": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
    }
}

# カスタムCSS（改良版）
def get_css(dark_mode=False, bg_theme_category="青系", bg_theme_name="淡い青"):
    theme = BACKGROUND_THEMES.get(bg_theme_category, {}).get(bg_theme_name, BACKGROUND_THEMES["青系"]["淡い青"])
    
    if dark_mode:
        return f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #f0f0f0;
    }}
    
    .stSidebar > div:first-child {{
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
    }}
    
    .main-header {{
        text-align: center;
        color: #a8c8ff;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(168, 200, 255, 0.3);
    }}
    
    .floating-write-btn {{
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        background: linear-gradient(135deg, #a8c8ff 0%, #8ab4ff 100%);
        border: none;
        border-radius: 50px;
        padding: 15px 25px;
        color: #1a1a2e;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(168, 200, 255, 0.4);
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 16px;
    }}
    
    .floating-write-btn:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(168, 200, 255, 0.6);
    }}
    
    .diary-entry {{
        background: linear-gradient(135deg, rgba(42, 42, 62, 0.8) 0%, rgba(30, 30, 46, 0.8) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 3px solid #a8c8ff;
        color: #f0f0f0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}
    
    .bot-response {{
        background: linear-gradient(135deg, rgba(62, 42, 30, 0.8) 0%, rgba(78, 52, 38, 0.8) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 3px solid #ffb366;
        color: #f0f0f0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}
    
    .mood-circle {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-block;
        margin: 5px;
        border: 2px solid #f0f0f0;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .mood-circle:hover {{
        transform: scale(1.1);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }}
    
    .mood-circle.selected {{
        border: 3px solid #a8c8ff;
        transform: scale(1.2);
    }}
    
    .theme-preview {{
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-block;
        margin: 3px;
        border: 2px solid #f0f0f0;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .theme-preview:hover {{
        transform: scale(1.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }}
    
    .meditation-controls {{
        background: linear-gradient(135deg, rgba(42, 42, 62, 0.7) 0%, rgba(30, 30, 46, 0.7) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        text-align: center;
    }}
    
    .stats-card {{
        background: linear-gradient(135deg, rgba(42, 42, 62, 0.7) 0%, rgba(30, 30, 46, 0.7) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        text-align: center;
        color: #f0f0f0;
        border: 1px solid rgba(168, 200, 255, 0.2);
        backdrop-filter: blur(5px);
    }}
</style>
"""
    else:
        return f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {theme['bg_color']} 0%, {theme['accent']} 30%, {theme['bg_color']} 100%);
        color: #4a4a4a;
        min-height: 100vh;
    }}
    
    .stSidebar > div:first-child {{
        background: linear-gradient(135deg, {theme['sidebar_bg']} 0%, {theme['accent']} 100%);
        border-right: 1px solid rgba(0, 0, 0, 0.05);
    }}
    
    .main-header {{
        text-align: center;
        color: #6b7280;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(107, 114, 128, 0.1);
        font-weight: 300;
    }}
    
    .floating-write-btn {{
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        background: linear-gradient(135deg, #6b7280 0%, #9ca3af 100%);
        border: none;
        border-radius: 50px;
        padding: 15px 25px;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 16px;
    }}
    
    .floating-write-btn:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(107, 114, 128, 0.4);
        background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%);
    }}
    
    .diary-entry {{
        background: {theme['card_bg']};
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 3px solid rgba(107, 114, 128, 0.3);
        color: #4a4a4a;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }}
    
    .diary-entry:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }}
    
    .bot-response {{
        background: rgba(255, 240, 230, 0.6);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 3px solid rgba(255, 179, 102, 0.5);
        color: #4a4a4a;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 8px rgba(255, 179, 102, 0.15);
        transition: all 0.3s ease;
    }}
    
    .mood-circle {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-block;
        margin: 5px;
        border: 2px solid #e0e0e0;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
    }}
    
    .mood-circle:hover {{
        transform: scale(1.1);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }}
    
    .mood-circle.selected {{
        border: 3px solid #6b7280;
        transform: scale(1.2);
        box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
    }}
    
    .theme-preview {{
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-block;
        margin: 3px;
        border: 2px solid #e0e0e0;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .theme-preview:hover {{
        transform: scale(1.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }}
    
    .theme-preview.selected {{
        border: 3px solid #6b7280;
        transform: scale(1.1);
    }}
    
    .meditation-controls {{
        background: {theme['card_bg']};
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        text-align: center;
        border: 1px solid rgba(107, 114, 128, 0.1);
    }}
    
    .stats-card {{
        background: {theme['card_bg']};
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        text-align: center;
        color: #4a4a4a;
        border: 1px solid rgba(107, 114, 128, 0.1);
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }}
    
    .stats-card:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }}
    
    .theme-category {{
        margin: 1rem 0;
        padding: 1rem;
        background: {theme['card_bg']};
        border-radius: 10px;
        border: 1px solid rgba(107, 114, 128, 0.1);
    }}
    
    .theme-category h4 {{
        margin: 0 0 0.5rem 0;
        color: #6b7280;
        font-size: 0.9rem;
    }}
</style>
"""

@dataclass
class User:
    email: str
    password_hash: str
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
                    return [User(**user) for user in data]
        except:
            pass
        return []
    
    def save_users(self, users: List[User]):
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(user) for user in users], f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"ユーザー情報の保存に失敗しました: {e}")
    
    def register_user(self, email: str, password: str) -> bool:
        if not self.validate_email(email):
            st.error("有効なメールアドレスを入力してください")
            return False
        
        if not self.validate_password(password):
            st.error("パスワードは8文字以上で、英字と数字の両方を含む必要があります")
            return False
        
        users = self.load_users()
        
        if any(user.email == email for user in users):
            st.error("このメールアドレスは既に登録されています")
            return False
        
        new_user = User(
            email=email,
            password_hash=self.hash_password(password),
            created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        users.append(new_user)
        self.save_users(users)
        return True
    
    def authenticate_user(self, email: str, password: str) -> bool:
        users = self.load_users()
        password_hash = self.hash_password(password)
        
        for user in users:
            if user.email == email and user.password_hash == password_hash:
                return True
        return False

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
                        # 新しいフィールドのデフォルト値を設定
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
    
    def get_entries_by_date(self, target_date: str) -> List[DiaryEntry]:
        entries = self.load_entries()
        return [entry for entry in entries if entry.date.split()[0] == target_date]
    
    def get_calendar_data(self, year: int, month: int) -> Dict[int, List[DiaryEntry]]:
        entries = self.load_entries()
        calendar_data = {}
        
        for entry in entries:
            try:
                entry_date = datetime.datetime.strptime(entry.date.split()[0], "%Y-%m-%d")
                if entry_date.year == year and entry_date.month == month:
                    day = entry_date.day
                    if day not in calendar_data:
                        calendar_data[day] = []
                    calendar_data[day].append(entry)
            except:
                continue
        
        return calendar_data

class CounselingBot:
    def __init__(self):
        try:
            self.api_key = st.secrets.get("OPENAI_API_KEY", "")
        except:
            self.api_key = ""
        
    def get_counseling_response(self, content: str, mood: str, mood_intensity: int, category: str) -> str:
        # 気分の強度に応じた応答
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
            "仕事・学業": "一歩ずつ、あなたのペースで進んでいけば大丈夫です。完璧でなくても、今日の努力は必ず明日につながります。",
            "人間関係": "人との関わりは複雑ですが、あなたの誠実さは必ず相手に伝わります。自分らしさを大切にしてください。",
            "恋愛": "心を開くことは勇気がいりますが、真っ直ぐな気持ちは美しいものです。時間をかけて育んでいきましょう。",
            "家族": "家族だからこそ難しい面もありますね。お互いを思いやる気持ちがあれば、きっと理解し合えます。",
            "健康": "心と体の声に耳を傾けることは大切です。無理をせず、自分に優しくしてあげてください。",
            "その他": "どんな気持ちも、あなたにとって大切な感情です。その気持ちを大切にしながら歩んでいきましょう。"
        }
        
        advice = category_advice.get(category, "あなたなりのペースで、ゆっくりと歩んでいけば大丈夫です。")
        
        return f"{base_response}\n\n{advice}\n\n今夜も一日お疲れ様でした。あなたの心が穏やかでありますように 🌸✨"

def floating_write_button():
    """フローティング日記作成ボタン"""
    if st.session_state.get('current_page') != "✍️ 今夜の心を綴る":
        if st.button("✍️ 日記を書く", key="floating_write", help="新しい日記を書く"):
            st.session_state.current_page = "✍️ 今夜の心を綴る"
            st.rerun()

def mood_selector():
    """心模様選択UI（20種類、色分け）"""
    st.subheader("今の心模様は？")
    
    selected_mood = st.session_state.get('selected_mood', MOOD_OPTIONS[0])
    
    # 5行4列で心模様を表示
    for row in range(4):
        cols = st.columns(5)
        for col in range(5):
            mood_idx = row * 5 + col
            if mood_idx < len(MOOD_OPTIONS):
                mood = MOOD_OPTIONS[mood_idx]
                with cols[col]:
                    # カスタムHTMLで色付きの円を作成
                    is_selected = selected_mood['name'] == mood['name']
                    circle_class = "mood-circle selected" if is_selected else "mood-circle"
                    
                    st.markdown(f"""
                    <div class="{circle_class}" 
                         style="background-color: {mood['color']};" 
                         onclick="selectMood('{mood['name']}', '{mood['color']}', {mood['intensity']})"
                         title="{mood['name']}">
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(mood['name'], key=f"mood_{mood['name']}", help=f"強度: {mood['intensity']}/5"):
                        st.session_state.selected_mood = mood
                        st.rerun()
    
    return selected_mood

def theme_selector():
    """背景テーマ選択UI（色分けで直感的）"""
    st.subheader("🎨 心地よい色合いを選ぶ")
    
    current_category = st.session_state.get('bg_theme_category', '青系')
    current_name = st.session_state.get('bg_theme_name', '淡い青')
    
    for category, themes in BACKGROUND_THEMES.items():
        st.markdown(f'<div class="theme-category">', unsafe_allow_html=True)
        st.markdown(f"<h4>{category}</h4>", unsafe_allow_html=True)
        
        cols = st.columns(len(themes))
        for i, (theme_name, theme_data) in enumerate(themes.items()):
            with cols[i]:
                is_selected = current_category == category and current_name == theme_name
                preview_class = "theme-preview selected" if is_selected else "theme-preview"
                
                st.markdown(f"""
                <div class="{preview_class}" 
                     style="background-color: {theme_data['preview']};" 
                     title="{theme_name}">
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(theme_name, key=f"theme_{category}_{theme_name}"):
                    st.session_state.bg_theme_category = category
                    st.session_state.bg_theme_name = theme_name
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def create_circular_chart(entries):
    """環状の折れ線グラフ作成"""
    if not entries:
        return None
    
    # 最近30日分のデータを取得
    recent_entries = entries[-30:] if len(entries) >= 30 else entries
    
    # 日付と気分強度のデータを作成
    dates = []
    intensities = []
    
    for entry in recent_entries:
        try:
            date = datetime.datetime.strptime(entry.date.split()[0], "%Y-%m-%d")
            dates.append(date)
            intensities.append(entry.mood_intensity)
        except:
            continue
    
    if not dates:
        return None
    
    # 角度の計算（0度から360度）
    angles = [i * 360 / len(dates) for i in range(len(dates))]
    
    # 極座標でのデータ作成
    chart_data = []
    for i, (angle, intensity) in enumerate(zip(angles, intensities)):
        # 角度をラジアンに変換
        angle_rad = math.radians(angle)
        # 半径は気分強度に応じて調整（中心から1-5の距離）
        radius = intensity + 1
        
        # 直交座標に変換
        x = radius * math.cos(angle_rad)
        y = radius * math.sin(angle_rad)
        
        chart_data.append({
            'x': x,
            'y': y,
            'intensity': intensity,
            'date': dates[i].strftime('%m/%d'),
            'angle': angle
        })
    
    # 円を閉じるために最初の点を最後に追加
    if chart_data:
        chart_data.append(chart_data[0])
    
    df = pd.DataFrame(chart_data)
    
    # Altairで環状グラフを作成
    line_chart = alt.Chart(df).mark_line(
        strokeWidth=3,
        point=alt.MarkConfig(size=100, filled=True)
    ).encode(
        x=alt.X('x:Q', scale=alt.Scale(domain=[-7, 7]), title=''),
        y=alt.Y('y:Q', scale=alt.Scale(domain=[-7, 7]), title=''),
        color=alt.Color('intensity:Q', 
                       scale=alt.Scale(range=['#ef5350', '#ffb74d', '#e0e0e0', '#81c784', '#66bb6a']),
                       legend=alt.Legend(title="気分強度")),
        tooltip=['date:N', 'intensity:Q']
    ).properties(
        width=400,
        height=400,
        title="心の軌跡 - 環状チャート"
    ).resolve_scale(
        color='independent'
    )
    
    # 同心円の背景を追加
    circles = []
    for r in range(1, 7):
        circle_points = []
        for angle in range(0, 361, 10):
            angle_rad = math.radians(angle)
            x = r * math.cos(angle_rad)
            y = r * math.sin(angle_rad)
            circle_points.append({'x': x, 'y': y, 'radius': r})
        circles.extend(circle_points)
    
    circle_df = pd.DataFrame(circles)
    circle_chart = alt.Chart(circle_df).mark_circle(
        opacity=0.1,
        size=1
    ).encode(
        x=alt.X('x:Q'),
        y=alt.Y('y:Q'),
        color=alt.value('#cccccc')
    )
    
    return line_chart + circle_chart

def meditation_page():
    """瞑想・リラクゼーションページ"""
    st.header("🧘‍♀️ 心を静める時間")
    
    st.markdown('<div class="meditation-controls">', unsafe_allow_html=True)
    
    # タイマー設定
    col1, col2 = st.columns(2)
    with col1:
        meditation_time = st.selectbox(
            "瞑想時間を選択",
            [1, 3, 5, 10, 15, 20, 30],
            index=2,
            help="瞑想する時間を分で選択してください"
        )
    
    with col2:
        breathing_pattern = st.selectbox(
            "呼吸パターン",
            ["4-7-8呼吸法", "ボックス呼吸", "自然呼吸"],
            help="お好みの呼吸法を選択してください"
        )
    
    # 音源選択
    st.subheader("🎵 リラックス音源")
    
    sound_category = st.selectbox(
        "音源カテゴリ",
        ["自然音", "癒し音", "無音"]
    )
    
    if sound_category != "無音":
        available_sounds = MEDITATION_SOUNDS.get(sound_category, {})
        selected_sound = st.selectbox(
            "音源を選択",
            list(available_sounds.keys()) if available_sounds else ["なし"]
        )
        
        if available_sounds and selected_sound in available_sounds:
            st.audio(available_sounds[selected_sound])
    
    # 瞑想開始ボタン
    if st.button("🧘‍♀️ 瞑想を始める", type="primary"):
        st.success(f"{meditation_time}分間の瞑想を開始します。")
        
        # 呼吸ガイド表示
        if breathing_pattern == "4-7-8呼吸法":
            st.info("4秒で息を吸い、7秒間息を止めて、8秒で息を吐きます。")
        elif breathing_pattern == "ボックス呼吸":
            st.info("4秒で息を吸い、4秒間息を止め、4秒で息を吐き、4秒間息を止めます。")
        else:
            st.info("自然な呼吸で、今この瞬間に意識を向けてください。")
        
        # 簡単なプログレスバー（実際のタイマーの代用）
        progress_bar = st.progress(0)
        for i in range(meditation_time * 60):
            progress_bar.progress((i + 1) / (meditation_time * 60))
        
        st.success("瞑想が完了しました。お疲れ様でした。🌸")
        
        # 瞑想後の感想を記録
        if st.button("今の気持ちを記録する"):
            st.session_state.current_page = "✍️ 今夜の心を綴る"
            st.rerun()
    
    # 瞑想のガイダンス
    st.markdown("---")
    st.subheader("🌸 瞑想のガイダンス")
    
    guidance_options = {
        "初心者向け": "背筋を伸ばして座り、目を閉じます。呼吸に意識を向けて、思考が浮かんでも判断せずに、また呼吸に戻ります。",
        "ストレス解消": "肩の力を抜いて、深くゆっくりとした呼吸を行います。息を吐くたびに、緊張が身体から流れ出ていくイメージを持ちます。",
        "感謝の瞑想": "今日感謝したいことを3つ思い浮かべます。その気持ちを心の中で味わいながら、静かに呼吸を続けます。",
        "慈悲の瞑想": "自分自身、そして大切な人々の幸せを願う気持ちを込めて、心を温かく保ちながら瞑想します。"
    }
    
    selected_guidance = st.selectbox("瞑想のテーマ", list(guidance_options.keys()))
    st.info(guidance_options[selected_guidance])
    
    st.markdown('</div>', unsafe_allow_html=True)

def login_page():
    """ログイン・新規登録ページ"""
    current_category = st.session_state.get('bg_theme_category', '青系')
    current_name = st.session_state.get('bg_theme_name', '淡い青')
    st.markdown(get_css(st.session_state.get('dark_mode', False), current_category, current_name), unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🌸 心の整理帳 🌸</h1>', unsafe_allow_html=True)
    st.markdown("**夜のひととき、心に寄り添うお悩み相談Bot + 日記アプリ**")
    
    # テーマ選択（ログイン前でも使用可能）
    with st.sidebar:
        theme_selector()
        
        st.markdown("---")
        # ダークモード切り替え
        if st.button("🌙 ダークモード" if not st.session_state.get('dark_mode', False) else "☀️ ライトモード"):
            st.session_state.dark_mode = not st.session_state.get('dark_mode', False)
            st.rerun()
    
    tab1, tab2 = st.tabs(["🔐 ログイン", "✨ 新規登録"])
    
    auth_manager = AuthManager()
    
    with tab1:
        st.subheader("ログイン")
        
        with st.form("login_form"):
            email = st.text_input("📧 メールアドレス", placeholder="example@email.com")
            password = st.text_input("🔒 パスワード", type="password")
            
            if st.form_submit_button("ログイン", type="primary"):
                if email and password:
                    if auth_manager.authenticate_user(email, password):
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
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
            reg_password = st.text_input("🔒 パスワード", type="password", key="reg_password",
                                       help="8文字以上、英字と数字の両方を含む")
            reg_password_confirm = st.text_input("🔒 パスワード確認", type="password", key="reg_password_confirm")
            
            if st.form_submit_button("新規登録", type="primary"):
                if reg_email and reg_password and reg_password_confirm:
                    if reg_password != reg_password_confirm:
                        st.error("パスワードが一致しません")
                    elif auth_manager.register_user(reg_email, reg_password):
                        st.success("登録完了！ログインしてください。")
                else:
                    st.error("すべてのフィールドを入力してください")

def write_diary_page(diary_manager: DiaryManager, bot: CounselingBot):
    st.header("✍️ 今夜の気持ちを静かに綴りましょう")
    
    # 日記保存後の状態管理
    if 'diary_saved' not in st.session_state:
        st.session_state.diary_saved = False
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        title = st.text_input("📌 タイトル", placeholder="今日感じたこと、心に残ったこと...")
        
        category = st.selectbox(
            "🏷️ どんなことについて",
            ["仕事・学業", "人間関係", "恋愛", "家族", "健康", "その他"]
        )
        
        content = st.text_area(
            "📝 心の中を静かに整理してみませんか",
            height=200,
            placeholder="今日の気持ち、心配事、嬉しかったこと、感謝していること... あなたのペースで、ゆっくりと。"
        )
    
    with col2:
        selected_mood = mood_selector()
    
    if st.button("💝 心の声を聞いてもらう", type="primary"):
        if title and content and selected_mood:
            with st.spinner("あなたの心に静かに寄り添っています..."):
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
            
            st.success("あなたの気持ち、しっかりと受け取りました。")
            
            st.markdown('<div class="bot-response">', unsafe_allow_html=True)
            st.markdown("### 🤖 心に寄り添うメッセージ")
            st.write(bot_response)
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.error("タイトル、内容、心模様を選択してください。")
    
    # 日記保存後のアクションボタン
    if st.session_state.diary_saved:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 もう少し書いてみる", type="secondary"):
                st.session_state.diary_saved = False
                st.rerun()
        
        with col2:
            if st.button("📚 今日の記録を見る"):
                st.session_state.diary_saved = False
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                st.session_state.selected_calendar_date = today
                st.session_state.current_page = "📚 心の記録を振り返る"
                st.rerun()
        
        with col3:
            if st.button("🧘‍♀️ 瞑想する"):
                st.session_state.diary_saved = False
                st.session_state.current_page = "🧘‍♀️ 心を静める"
                st.rerun()

def calendar_diary_page(diary_manager: DiaryManager):
    st.header("📅 時の流れと共に心を振り返る")
    
    # フローティングボタン
    floating_write_button()
    
    # 年月選択
    col1, col2 = st.columns(2)
    with col1:
        current_year = datetime.datetime.now().year
        year = st.selectbox("年", range(current_year-2, current_year+1), index=2)
    with col2:
        current_month = datetime.datetime.now().month
        month = st.selectbox("月", range(1, 13), index=current_month-1)
    
    # カレンダー表示（簡略化版）
    st.subheader(f"{year}年{month}月")
    
    entries = diary_manager.load_entries()
    month_entries = []
    
    for entry in entries:
        try:
            entry_date = datetime.datetime.strptime(entry.date.split()[0], "%Y-%m-%d")
            if entry_date.year == year and entry_date.month == month:
                month_entries.append(entry)
        except:
            continue
    
    if month_entries:
        for entry in reversed(month_entries):
            mood_color = next((m['color'] for m in MOOD_OPTIONS if m['name'] == entry.mood), '#e0e0e0')
            
            with st.expander(f"🔸 {entry.date.split()[0]} - {entry.title}"):
                st.markdown(f"""
                <div style="border-left: 4px solid {mood_color}; padding-left: 1rem; margin: 0.5rem 0;">
                    <strong>心模様:</strong> {entry.mood} (強度: {entry.mood_intensity}/5)<br>
                    <strong>テーマ:</strong> {entry.category}<br>
                    <strong>時刻:</strong> {entry.date.split()[1]}
                </div>
                """, unsafe_allow_html=True)
                
                st.write(entry.content)
                
                if entry.bot_response:
                    st.markdown("**🤖 その時のメッセージ:**")
                    st.info(entry.bot_response)
    else:
        st.info(f"{year}年{month}月の記録はまだありません。")

def read_diary_page(diary_manager: DiaryManager):
    st.header("📚 心の軌跡を辿る")
    
    # フローティングボタン
    floating_write_button()
    
    entries = diary_manager.load_entries()
    
    if not entries:
        st.info("まだ心の記録がありません。今夜から始めてみませんか？")
        return
    
    # 検索・フィルター
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 記憶を探す", placeholder="気になる言葉で検索...")
    with col2:
        filter_category = st.selectbox("テーマで絞る", ["すべて"] + ["仕事・学業", "人間関係", "恋愛", "家族", "健康", "その他"])
    with col3:
        mood_names = [mood['name'] for mood in MOOD_OPTIONS]
        filter_mood = st.selectbox("心模様で絞る", ["すべて"] + mood_names)
    
    # フィルタリング
    filtered_entries = entries
    if search_term:
        filtered_entries = [e for e in filtered_entries if search_term.lower() in e.content.lower() or search_term.lower() in e.title.lower()]
    if filter_category != "すべて":
        filtered_entries = [e for e in filtered_entries if e.category == filter_category]
    if filter_mood != "すべて":
        filtered_entries = [e for e in filtered_entries if e.mood == filter_mood]
    
    # エントリー表示
    for entry in reversed(filtered_entries):
        mood_color = next((m['color'] for m in MOOD_OPTIONS if m['name'] == entry.mood), '#e0e0e0')
        
        with st.expander(f"{entry.mood} {entry.title} - {entry.date}"):
            st.markdown(f"""
            <div style="border-left: 4px solid {mood_color}; padding-left: 1rem; margin: 0.5rem 0;">
                <strong>心模様:</strong> {entry.mood} (強度: {entry.mood_intensity}/5)<br>
                <strong>テーマ:</strong> {entry.category}<br>
                <strong>記録した時:</strong> {entry.date}
            </div>
            """, unsafe_allow_html=True)
            
            st.write(entry.content)
            
            if entry.bot_response:
                st.markdown("**🤖 その時受け取ったメッセージ:**")
                st.info(entry.bot_response)

def analytics_page(diary_manager: DiaryManager):
    st.header("📊 心の変化を静かに見つめる")
    
    # フローティングボタン
    floating_write_button()
    
    entries = diary_manager.load_entries()
    
    if not entries:
        st.info("まだデータが集まっていません。少しずつ記録を積み重ねていきましょう。")
        return
    
    # 統計カード
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("記録した日々", len(entries))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        moods = [entry.mood for entry in entries]
        most_common_mood = max(set(moods), key=moods.count)
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("よく現れる心模様", most_common_mood)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        intensities = [entry.mood_intensity for entry in entries]
        avg_intensity = sum(intensities) / len(intensities)
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("平均心境強度", f"{avg_intensity:.1f}/5")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        categories = [entry.category for entry in entries]
        most_common_category = max(set(categories), key=categories.count)
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("よく考えること", most_common_category)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # グラフ表示
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 心模様の分布")
        mood_counts = pd.Series(moods).value_counts()
        
        mood_df = pd.DataFrame({
            '心模様': mood_counts.index,
            '回数': mood_counts.values
        })
        
        # 心模様に対応する色を取得
        mood_df['色'] = mood_df['心模様'].apply(
            lambda x: next((m['color'] for m in MOOD_OPTIONS if m['name'] == x), '#e0e0e0')
        )
        
        chart = alt.Chart(mood_df).mark_bar(
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8,
            opacity=0.8
        ).encode(
            x=alt.X('心模様:N', title='心模様', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('回数:Q', title='回数'),
            color=alt.Color('色:N', scale=None, legend=None),
            tooltip=['心模様', '回数']
        ).properties(
            height=300,
            width='container'
        )
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("🌸 環状の心の軌跡")
        circular_chart = create_circular_chart(entries)
        if circular_chart:
            st.altair_chart(circular_chart, use_container_width=True)
        else:
            st.info("データが不足しています。もう少し記録を積み重ねてください。")
    
    # 時系列グラフ
    st.subheader("📅 時間経過と心の変化")
    
    # 日付ごとの平均強度を計算
    daily_data = {}
    for entry in entries:
        try:
            date = entry.date.split()[0]
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(entry.mood_intensity)
        except:
            continue
    
    if daily_data:
        time_series_data = []
        for date, intensities in daily_data.items():
            avg_intensity = sum(intensities) / len(intensities)
            time_series_data.append({
                'date': date,
                'intensity': avg_intensity,
                'count': len(intensities)
            })
        
        time_df = pd.DataFrame(time_series_data)
        time_df['date'] = pd.to_datetime(time_df['date'])
        
        time_chart = alt.Chart(time_df).mark_line(
            strokeWidth=3,
            point=alt.MarkConfig(size=100, filled=True)
        ).encode(
            x=alt.X('date:T', title='日付'),
            y=alt.Y('intensity:Q', title='平均心境強度', scale=alt.Scale(domain=[0, 5])),
            color=alt.value('#6b7280'),
            tooltip=['date:T', 'intensity:Q', 'count:Q']
        ).properties(
            height=200,
            width='container'
        )
        
        st.altair_chart(time_chart, use_container_width=True)
    
    # 最近の傾向分析
    st.subheader("🔍 最近の心の傾向")
    recent_entries = entries[-7:] if len(entries) >= 7 else entries
    
    if recent_entries:
        recent_intensities = [entry.mood_intensity for entry in recent_entries]
        avg_recent = sum(recent_intensities) / len(recent_intensities)
        
        if avg_recent >= 4:
            st.success("最近は心穏やかな日が多いようですね。その調子で、ゆっくりと歩んでいきましょう ✨")
        elif avg_recent >= 3:
            st.info("心に適度な波がありますね。それもまた、自然な心の動き。大丈夫ですよ 🌊")
        elif avg_recent >= 2:
            st.warning("少し重い気持ちの日が続いているようです。無理をせず、自分を労ってあげてくださいね 🌸")
        else:
            st.error("辛い時期が続いているようですね。一人で抱え込まず、専門家への相談も考えてみてください 💙")

def settings_page():
    st.header("🔧 アプリの設定")
    
    # フローティングボタン
    floating_write_button()
    
    # テーマ選択
    theme_selector()
    
    st.markdown("---")
    
    st.subheader("📱 心の整理帳について")
    st.markdown("""
    **心の整理帳** は、夜の静かな時間に、あなたの心に寄り添うアプリです。
    
    **✨ できること:**
    - 📝 20種類の心模様から選んで気持ちを記録
    - 🤖 気分の強度に応じた優しいAIカウンセラーのメッセージ  
    - 📊 環状グラフで心の軌跡を美しく可視化
    - 🧘‍♀️ 瞑想・リラクゼーション機能
    - 🎨 17種類の心地よい背景色テーマ
    - 🔍 過去の気持ちを検索・振り返り
    - 🔐 あなただけのプライベートな空間
    
    **💭 使い方のコツ:**
    - 完璧である必要はありません。思ったままを自由に
    - 毎晩少しずつでも、心の声に耳を傾けてみてください
    - 過去の記録を読み返すことで、成長している自分に気づけます
    - 辛い時こそ、一人で抱え込まずに心の声を聞いてもらいましょう
    - 瞑想機能を使って、心を静める時間を作りましょう
    
    **🌙 夜のひととき、あなたの心が安らぎますように**
    """)
    
    st.markdown("---")
    st.subheader("🌸 心の健康について")
    st.markdown("""
    - このアプリは心のサポートツールですが、専門的な治療の代替ではありません
    - 深刻な悩みや症状がある場合は、専門家にご相談ください
    - あなたの心の健康が何より大切です
    """)
    
    st.markdown("---")
    st.subheader("🎵 瞑想音源について")
    st.markdown("""
    瞑想ページでは、リラックス効果の高い音源を選択できます：
    - **自然音**: 雨音、波音、鳥のさえずり、風の音
    - **癒し音**: チベット鈴、水滴、シンギングボウル、ホワイトノイズ
    
    音源は心を落ち着かせ、瞑想の効果を高めるために選ばれています。
    """)

def main():
    # セッション状態の初期化
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'bg_theme_category' not in st.session_state:
        st.session_state.bg_theme_category = "青系"
    if 'bg_theme_name' not in st.session_state:
        st.session_state.bg_theme_name = "淡い青"
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "✍️ 今夜の心を綴る"
    if 'selected_mood' not in st.session_state:
        st.session_state.selected_mood = MOOD_OPTIONS[0]
    
    # ログインチェック
    if not st.session_state.logged_in:
        login_page()
        return
    
    # CSS適用
    current_category = st.session_state.get('bg_theme_category', '青系')
    current_name = st.session_state.get('bg_theme_name', '淡い青')
    st.markdown(get_css(st.session_state.dark_mode, current_category, current_name), unsafe_allow_html=True)
    
    # フローティング日記ボタンのHTML追加
    if st.session_state.get('current_page') != "✍️ 今夜の心を綴る":
        st.markdown("""
        <div class="floating-write-btn" onclick="location.reload();">
            ✍️ 日記を書く
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🌸 心の整理帳 🌸</h1>', unsafe_allow_html=True)
    st.markdown("**夜のひととき、あなたの心に静かに寄り添います**")
    
    # ヘッダーコントロール
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.write(f"こんばんは、{st.session_state.user_email} さん")
    with col2:
        # ダークモード切り替え
        if st.button("🌙" if not st.session_state.dark_mode else "☀️", help="モード切り替え"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    with col3:
        # クイックテーマ変更
        if st.button("🎨", help="テーマ変更"):
            all_themes = []
            for category, themes in BACKGROUND_THEMES.items():
                for theme_name in themes.keys():
                    all_themes.append((category, theme_name))
            
            current_theme = (st.session_state.bg_theme_category, st.session_state.bg_theme_name)
            try:
                current_idx = all_themes.index(current_theme)
                next_idx = (current_idx + 1) % len(all_themes)
                st.session_state.bg_theme_category, st.session_state.bg_theme_name = all_themes[next_idx]
            except:
                st.session_state.bg_theme_category, st.session_state.bg_theme_name = all_themes[0]
            st.rerun()
    with col4:
        if st.button("ログアウト"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.rerun()
    
    # サイドバー
    st.sidebar.title("📝 心のメニュー")
    
    # サイドバーにもテーマ選択
    with st.sidebar:
        st.markdown("---")
        st.subheader("🎨 今夜の色合い")
        current_category = st.session_state.get('bg_theme_category', '青系')
        current_name = st.session_state.get('bg_theme_name', '淡い青')
        
        # コンパクトなテーマ選択
        for category, themes in BACKGROUND_THEMES.items():
            st.markdown(f"**{category}**")
            cols = st.columns(len(themes))
            for i, (theme_name, theme_data) in enumerate(themes.items()):
                with cols[i]:
                    is_current = current_category == category and current_name == theme_name
                    button_text = f"{'🔸' if is_current else '◦'}"
                    if st.button(button_text, key=f"sidebar_{category}_{theme_name}", help=theme_name):
                        st.session_state.bg_theme_category = category
                        st.session_state.bg_theme_name = theme_name
                        st.rerun()
    
    # メインページ選択
    page = st.sidebar.selectbox(
        "今夜はどちらへ",
        ["✍️ 今夜の心を綴る", "📅 時の流れを辿る", "📚 心の記録を振り返る", "📊 心の変化を見つめる", "🧘‍♀️ 心を静める", "🔧 設定"],
        index=0
    )
    
    # ページが変更された場合はセッション状態を更新
    if page != st.session_state.current_page:
        st.session_state.current_page = page
    
    # インスタンス作成
    diary_manager = DiaryManager(st.session_state.user_email)
    bot = CounselingBot()
    
    # ページルーティング
    if page == "✍️ 今夜の心を綴る":
        write_diary_page(diary_manager, bot)
    elif page == "📅 時の流れを辿る":
        calendar_diary_page(diary_manager)
    elif page == "📚 心の記録を振り返る":
        read_diary_page(diary_manager)
    elif page == "📊 心の変化を見つめる":
        analytics_page(diary_manager)
    elif page == "🧘‍♀️ 心を静める":
        meditation_page()
    else:
        settings_page()

if __name__ == "__main__":
    main()