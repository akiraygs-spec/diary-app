import streamlit as st
import datetime
import hashlib
from data_models import Goal, DiaryEntry, MOOD_OPTIONS, ACHIEVEMENT_TIPS, THEME_PALETTES
from auth_manager import AuthManager
from data_manager import GoalManager, DiaryManager
from bot_counselor import CounselingBot
from ui_components import get_css, goals_overview_widget, mood_selector

def login_page():
    theme_name = st.session_state.get('theme_name', 'ソフトブルー')
    st.markdown(get_css(theme_name), unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header"> 習慣化ジャーナル</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">目標達成と心の成長をサポート</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([" ログイン", " 新規登録"])
    
    auth_manager = AuthManager()
    
    with tab1:
        st.subheader("ログイン")
        with st.form("login_form"):
            email = st.text_input(" メールアドレス", placeholder="example@email.com")
            password = st.text_input(" パスワード", type="password")
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
            reg_email = st.text_input(" メールアドレス", placeholder="example@email.com", key="reg_email")
            reg_nickname = st.text_input(" ニックネーム", placeholder="例: 太郎", key="reg_nickname")
            reg_password = st.text_input(" パスワード", type="password", key="reg_password", help="8文字以上、英字と数字の両方を含む")
            reg_password_confirm = st.text_input(" パスワード確認", type="password", key="reg_password_confirm")
            if st.form_submit_button("新規登録", type="primary"):
                if reg_password != reg_password_confirm:
                    st.error("パスワードが一致しません")
                elif auth_manager.register_user(reg_email, reg_password, reg_nickname):
                    st.success("登録完了！ログインしてください。")

def goals_page(goal_manager: GoalManager):
    st.header(" 目標設定・管理")
    goals = goal_manager.load_goals()
    
    with st.expander("➕ 新しい目標を追加", expanded=not goals):
        with st.form("add_goal_form"):
            col1, col2 = st.columns(2)
            with col1:
                goal_title = st.text_input("目標タイトル", placeholder="例：英語の勉強を習慣化する")
                goal_category = st.selectbox("期間", ["day", "week", "month","year"], format_func=lambda x: {"day": " 今日の目標 ", "week": " 今週の目標 ", "month": " 今月の目標 ", "year": " 今年の目標" }[x])
            with col2:
                goal_deadline = st.date_input("目標期限", min_value=datetime.date.today())
            goal_description = st.text_area("詳細説明（任意）", placeholder="具体的な目標内容、達成方法など")
            if st.form_submit_button("目標を追加", type="primary"):
                if goal_title:
                    new_goal = Goal(id=hashlib.md5(f"{goal_title}{datetime.datetime.now()}".encode()).hexdigest(), title=goal_title, description=goal_description or "", category=goal_category, deadline=goal_deadline.strftime("%Y-%m-%d"), created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    goal_manager.add_goal(new_goal)
                    st.success("目標が追加されました！")
                    st.rerun()
                else:
                    st.error("タイトルを入力してください")
    
    if goals:
        st.subheader(" 現在の目標")
        categories = {"day": {"name": " 今日の目標", "goals": []}, "week": {"name": " 今週の目標", "goals": []}, "month": {"name": " 今月の目標", "goals": []}, "year": {"name": " 今年の目標", "goals": []}}
        for goal in goals:
            if goal.category in categories:
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
    else:
        st.info("まだ目標が設定されていません。上記のフォームから目標を追加してください。")

def write_diary_page(diary_manager: DiaryManager, bot: CounselingBot, goal_manager: GoalManager):
    st.header(" 今日の振り返り")
    goals_overview_widget(goal_manager)
    if 'diary_saved' not in st.session_state:
        st.session_state.diary_saved = False
    
    col1, col2 = st.columns([2, 1])
    with col1:
        title = st.text_input(" タイトル", placeholder="今日の出来事や気持ち...")
        category = st.selectbox(" カテゴリ", ["仕事・学業", "人間関係", "恋愛", "家族", "健康", "その他"])
        content = st.text_area(" 今日の振り返り", height=200, placeholder="今日の出来事、感じたこと、学んだこと、目標への進捗など... 自由に書いてください。")
    with col2:
        selected_mood = mood_selector()
    
    if st.button(" 記録して相談する", type="primary"):
        if title and content and selected_mood:
            with st.spinner("あなたの気持ちに寄り添っています..."):
                bot_response = bot.get_counseling_response(content, selected_mood['name'], selected_mood['intensity'], category)
            entry = DiaryEntry(date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title=title, content=content, mood=selected_mood['name'], mood_intensity=selected_mood['intensity'], category=category, bot_response=bot_response)
            diary_manager.add_entry(entry)
            st.session_state.diary_saved = True
            st.success("記録が保存されました！")
            st.markdown('<div class="bot-response">', unsafe_allow_html=True)
            st.markdown("###  今日のメッセージ")
            st.write(bot_response)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("タイトル、内容、心模様を選択してください。")
    
    if st.session_state.diary_saved:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ 続けて記録", type="secondary"):
                st.session_state.diary_saved = False
                st.rerun()
        with col2:
            if st.button(" 目標を確認"):
                st.session_state.current_page = " 目標設定・管理"
                st.rerun()
        with col3:
            if st.button(" 過去の記録"):
                st.session_state.current_page = " 記録を振り返る"
                st.rerun()

def history_page(diary_manager: DiaryManager, goal_manager: GoalManager):
    st.header(" 記録を振り返る")
    goals_overview_widget(goal_manager)
    entries = diary_manager.load_entries()
    if not entries:
        st.info("まだ記録がありません。今日から始めてみましょう。")
        return
    
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
    
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input(" 記録を検索", placeholder="キーワードで検索...")
    with col2:
        filter_category = st.selectbox("カテゴリで絞る", ["すべて"] + ["仕事・学業", "人間関係", "恋愛", "家族", "健康", "その他"])
    with col3:
        mood_categories = list(MOOD_OPTIONS.keys())
        filter_mood_cat = st.selectbox("気持ちで絞る", ["すべて"] + mood_categories)
    
    filtered_entries = entries
    if search_term:
        filtered_entries = [e for e in filtered_entries if search_term.lower() in e.content.lower() or search_term.lower() in e.title.lower()]
    if filter_category != "すべて":
        filtered_entries = [e for e in filtered_entries if e.category == filter_category]
    if filter_mood_cat != "すべて":
        category_moods = [mood['name'] for mood in MOOD_OPTIONS[filter_mood_cat]]
        filtered_entries = [e for e in filtered_entries if e.mood in category_moods]
    
    st.subheader(f" 記録一覧 ({len(filtered_entries)}件)")
    for entry in reversed(filtered_entries):
        mood_color = "#d3d3d3"
        for category, moods in MOOD_OPTIONS.items():
            for mood in moods:
                if mood['name'] == entry.mood:
                    mood_color = mood['color']
                    break
        with st.expander(f"{entry.mood} {entry.title} - {entry.date.split()[0]}"):
            st.markdown(f"""<div style="border-left: 4px solid {mood_color}; padding-left: 1rem; margin: 0.5rem 0;"><strong>心模様:</strong> {entry.mood} (強度: {entry.mood_intensity}/5)<br><strong>カテゴリ:</strong> {entry.category}<br><strong>記録時刻:</strong> {entry.date}</div>""", unsafe_allow_html=True)
            st.write(entry.content)
            if entry.bot_response:
                st.markdown("** その時のメッセージ:**")
                st.info(entry.bot_response)

def tips_page():
    st.header(" 目標達成のためのTips")
    st.markdown("""<div style="background: var(--card); padding: 1rem; border-radius: 12px; margin-bottom: 2rem; border: 1px solid var(--border);"><p style="margin: 0; text-align: center; color: var(--text-secondary);">目標達成と習慣化のための実践的なアドバイスをまとめました。<br>あなたの成長を応援する、科学に基づいたヒントを参考にしてください。</p></div>""", unsafe_allow_html=True)
    for category, tips in ACHIEVEMENT_TIPS.items():
        st.subheader(f" {category}")
        cols = st.columns(2)
        for i, tip in enumerate(tips):
            with cols[i % 2]:
                st.markdown(f"""<div class="tip-card"><div class="tip-title">{tip['title']}</div><div class="tip-content">{tip['content']}</div></div>""", unsafe_allow_html=True)

def settings_page(auth_manager: AuthManager):
    if 'settings_section' not in st.session_state:
        st.session_state.settings_section = "menu"
    
    if st.session_state.settings_section == "menu":
        st.header(" 設定")
        st.markdown("""<div style="background: var(--card); padding: 1rem; border-radius: 12px; margin-bottom: 2rem; border: 1px solid var(--border);"><p style="margin: 0; text-align: center; color: var(--text-secondary);">設定したい項目を選択してください</p></div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(" アカウント情報", use_container_width=True):
                st.session_state.settings_section = "account"
                st.rerun()
            if st.button("🎨 テーマ設定", use_container_width=True):
                st.session_state.settings_section = "theme"
                st.rerun()
        with col2:
            if st.button(" ニックネーム変更", use_container_width=True):
                st.session_state.settings_section = "nickname"
                st.rerun()
            if st.button(" プラン・課金", use_container_width=True):
                st.session_state.settings_section = "billing"
                st.rerun()
    else:
        if st.button("← 設定メニューに戻る", type="secondary"):
            st.session_state.settings_section = "menu"
            st.rerun()
        if st.session_state.settings_section == "account":
            st.header(" アカウント情報")
            current_email = st.session_state.user_email
            current_nickname = st.session_state.user_nickname
            st.markdown("""<div style="background: var(--card); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 1px solid var(--border);"><h3 style="margin-bottom: 1rem;">基本情報</h3></div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"** メールアドレス**\n{current_email}")
            with col2:
                st.info(f"** ニックネーム**\n{current_nickname}")
            auth_users = auth_manager.load_users()
            for user in auth_users:
                if user.email == current_email:
                    st.markdown(f"** アカウント作成日:** {user.created_date}")
                    break
        elif st.session_state.settings_section == "nickname":
            st.header(" ニックネーム変更")
            current_nickname = st.session_state.user_nickname
            st.markdown(f"**現在のニックネーム:** {current_nickname}")
            with st.form("nickname_form"):
                new_nickname = st.text_input("新しいニックネーム", placeholder="新しいニックネームを入力")
                if st.form_submit_button("ニックネームを変更", type="primary"):
                    if new_nickname and new_nickname != current_nickname:
                        if auth_manager.update_nickname(st.session_state.user_email, new_nickname):
                            st.session_state.user_nickname = new_nickname
                            st.success("ニックネームを変更しました！")
                            st.rerun()
                        else:
                            st.error("ニックネームの変更に失敗しました")
                    elif not new_nickname:
                        st.error("ニックネームを入力してください")
                    else:
                        st.info("ニックネームに変更はありません")
        elif st.session_state.settings_section == "theme":
            st.header("🎨 テーマ設定")
            st.markdown(f"**現在のテーマ:** {st.session_state.theme_name}")
            st.markdown("### テーマプレビュー")
            cols = st.columns(3)
            for i, (theme_name, theme_data) in enumerate(THEME_PALETTES.items()):
                with cols[i % 3]:
                    is_current = theme_name == st.session_state.theme_name
                    st.markdown(f"""<div style="background: {theme_data['gradient']}; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; border: {'3px solid ' + theme_data['primary'] if is_current else '1px solid ' + theme_data['border']}; text-align: center;"><h4 style="color: {theme_data['text_primary']: margin: 0.5rem 0;">{theme_name}</h4>}<div style="background: {theme_data['card']}; padding: 0.5rem; border-radius: 8px; margin: 0.5rem 0;"><small style="color: {theme_data['text_secondary']};">サンプルテキスト</small></div>{"<p style='color: #28a745; font-weight: bold; margin: 0;'>適用中</p>" if is_current else ""}</div>""", unsafe_allow_html=True)
                    if not is_current and st.button(f"{theme_name}を適用", key=f"theme_{theme_name}"):
                        st.session_state.theme_name = theme_name
                        st.success(f"{theme_name}を適用しました！")
                        st.rerun()
            st.markdown("### テーマ変更の方法")
            st.info(" 画面上部の🎨ボタンでも素早くテーマを切り替えできます")
        elif st.session_state.settings_section == "billing":
            st.header(" プラン・課金")
            st.markdown("""<div class="plan-card"><h3> フリープラン</h3><div class="plan-price">無料</div><div class="plan-feature"> 基本的な日記機能</div><div class="plan-feature"> 目標設定機能</div><div class="plan-feature"> 心模様記録</div><div class="plan-feature"> 基本的な振り返り機能</div><p style="margin-top: 1rem; color: #28a745; font-weight: bold;">現在のプラン</p></div>""", unsafe_allow_html=True)
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""<div class="plan-card"><h3> プレミアムプラン</h3><div class="plan-price">¥480/月</div><div class="plan-feature"> フリープランの全機能</div><div class="plan-feature"> AI個別アドバイス</div><div class="plan-feature"> 詳細な分析レポート</div><div class="plan-feature"> カスタムテーマ</div><div class="plan-feature"> データエクスポート</div><div class="plan-feature"> 優先サポート</div></div>""", unsafe_allow_html=True)
            with col2:
                st.markdown("""<div class="plan-card"><h3> プロプラン</h3><div class="plan-price">¥980/月</div><div class="plan-feature"> プレミアムの全機能</div><div class="plan-feature"> チーム機能</div><div class="plan-feature"> コーチング機能</div><div class="plan-feature"> 無制限ストレージ</div><div class="plan-feature"> API連携</div><div class="plan-feature"> 24時間サポート</div></div>""", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("""<div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); padding: 2rem; border-radius: 16px; text-align: center; margin: 1rem 0; border: 1px solid #ffeaa7;"><h3 style="color: #856404; margin-bottom: 1rem;"> 現在準備中です</h3><p style="color: #856404; margin: 0;">プレミアムプラン・プロプランは現在開発中です。<br>より良いサービスを提供するため、鋭意準備中です。<br>リリース時期については、近日中にお知らせいたします。</p></div>""", unsafe_allow_html=True)
            st.markdown("###  お問い合わせ")
            st.markdown("""プランに関するご質問やご要望がございましたら、お気軽にお問い合わせください。**Email:** akira.ygs@gmail.com **受付時間:** 平日 10:00-18:00""")