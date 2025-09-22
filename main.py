import streamlit as st
import datetime
from data_models import THEME_PALETTES, MOOD_OPTIONS
from auth_manager import AuthManager
from data_manager import DiaryManager, GoalManager
from bot_counselor import CounselingBot
from ui_components import get_css
from pages import login_page, goals_page, write_diary_page, history_page, tips_page, settings_page

# ページ設定
st.set_page_config(
    page_title="習慣化ジャーナル - 目標達成と心の成長",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        st.session_state.current_page = " 今日の振り返り"
    if 'selected_mood' not in st.session_state:
        st.session_state.selected_mood = MOOD_OPTIONS["ポジティブ"][0]
    
    # ログインチェック
    if not st.session_state.logged_in:
        login_page()
        return
    
    # CSS適用
    st.markdown(get_css(st.session_state.theme_name), unsafe_allow_html=True)
    
    # フローティング日記ボタン
    if st.session_state.get('current_page') != "📝 今日の振り返り":
        st.markdown("""
        <div class="floating-write-btn" onclick="location.reload();">
             振り返り
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header"> 習慣化ジャーナル</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">目標達成と心の成長をサポート</div>', unsafe_allow_html=True)
    
    # ヘッダーコントロール
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.write(f"こんにちは、{st.session_state.user_nickname} さん")
    with col2:
        if st.button("🎨", help="テーマ変更"):
            themes = list(THEME_PALETTES.keys())
            current_idx = themes.index(st.session_state.theme_name) if st.session_state.theme_name in themes else 0
            next_idx = (current_idx + 1) % len(themes)
            st.session_state.theme_name = themes[next_idx]
            st.rerun()
    with col3:
        if st.button(" ログアウト"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_nickname = ""
            st.rerun()
    
    # サイドバー
    st.sidebar.title(" メニュー")
    page = st.sidebar.selectbox(
        "ページを選択",
        [" 今日の振り返り", " 目標設定・管理", " 記録を振り返る", " 目標達成Tips", " 設定"],
        index=0
    )
    
    if page != st.session_state.current_page:
        st.session_state.current_page = page
    
    # インスタンス作成
    diary_manager = DiaryManager(st.session_state.user_email)
    goal_manager = GoalManager(st.session_state.user_email)
    bot = CounselingBot()
    auth_manager = AuthManager()
    
    # ページルーティング
    if st.session_state.current_page == " 今日の振り返り":
        write_diary_page(diary_manager, bot, goal_manager)
    elif st.session_state.current_page == " 目標設定・管理":
        goals_page(goal_manager)
    elif st.session_state.current_page == " 記録を振り返る":
        history_page(diary_manager, goal_manager)
    elif st.session_state.current_page == " 目標達成Tips":
        tips_page()
    elif st.session_state.current_page == " 設定":
        settings_page(auth_manager)

if __name__ == "__main__":
    main()