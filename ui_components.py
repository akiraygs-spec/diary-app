import streamlit as st
from data_models import THEME_PALETTES, MOOD_OPTIONS
from data_manager import GoalManager

def get_css(theme_name: str = "ソフトブルー"):
    theme = THEME_PALETTES.get(theme_name, THEME_PALETTES["ソフトブルー"])
    
    return f"""
<style>
    .stApp {{ background: {theme['gradient']}; color: {theme['text_primary']}; min-height: 100vh; }}
    .stSidebar > div:first-child {{ background: linear-gradient(180deg, {theme['surface']} 0%, {theme['card']} 100%); border-right: 1px solid {theme['border']}; }}
    .main-header {{ text-align: center; color: {theme['primary']}; font-size: 2.8rem; margin-bottom: 1rem; text-shadow: 0 2px 4px {theme['shadow']}; font-weight: 300; letter-spacing: -0.5px; }}
    .subtitle {{ text-align: center; color: {theme['text_secondary']}; font-size: 1.1rem; margin-bottom: 2rem; font-weight: 400; }}
    .goals-overview {{ background: {theme['card']}; padding: 1.5rem; border-radius: 16px; margin: 1rem 0; border: 1px solid {theme['border']}; backdrop-filter: blur(10px); box-shadow: 0 4px 20px {theme['shadow']}; position: sticky; top: 20px; z-index: 100; }}
    .goal-item {{ margin: 0.8rem 0; padding: 0.8rem; background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.4) 100%); border-radius: 8px; border-left: 4px solid {theme['primary']}; }}
    .tip-card {{ background: {theme['card']}; padding: 1.5rem; border-radius: 16px; margin: 1rem 0; border: 1px solid {theme['border']}; backdrop-filter: blur(10px); box-shadow: 0 4px 20px {theme['shadow']}; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
    .tip-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 30px {theme['shadow']}; }}
    .tip-icon {{ font-size: 2rem; margin-bottom: 0.5rem; display: block; }}
    .tip-title {{ font-size: 1.2rem; font-weight: 600; color: {theme['text_primary']}; margin-bottom: 0.8rem; }}
    .tip-content {{ color: {theme['text_secondary']}; line-height: 1.6; }}
    .plan-card {{ background: {theme['card']}; padding: 2rem; border-radius: 16px; margin: 1rem 0; border: 1px solid {theme['border']}; backdrop-filter: blur(10px); box-shadow: 0 4px 20px {theme['shadow']}; text-align: center; }}
    .plan-price {{ font-size: 2.5rem; font-weight: 700; color: {theme['primary']}; margin: 1rem 0; }}
    .plan-feature {{ margin: 0.5rem 0; padding: 0.5rem; background: rgba(255,255,255,0.5); border-radius: 8px; }}
    .floating-write-btn {{ position: fixed; bottom: 30px; right: 30px; z-index: 1000; background: linear-gradient(135deg, {theme['primary']} 0%, {theme['secondary']} 100%); border: none; border-radius: 50px; padding: 15px 25px; color: {theme['text_primary']}; font-weight: bold; box-shadow: 0 6px 25px {theme['shadow']}; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); font-size: 16px; }}
    .floating-write-btn:hover {{ transform: translateY(-3px); box-shadow: 0 8px 35px {theme['shadow']}; background: linear-gradient(135deg, {theme['secondary']} 0%, {theme['accent']} 100%); }}
    .diary-entry {{ background: {theme['card']}; padding: 1.8rem; border-radius: 16px; margin: 1rem 0; border: 1px solid {theme['border']}; color: {theme['text_primary']}; backdrop-filter: blur(10px); box-shadow: 0 4px 20px {theme['shadow']}; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
    .diary-entry:hover {{ transform: translateY(-2px); box-shadow: 0 8px 30px {theme['shadow']}; }}
    .bot-response {{ background: linear-gradient(135deg, rgba(255, 248, 220, 0.9) 0%, rgba(255, 250, 235, 0.7) 100%); padding: 1.8rem; border-radius: 16px; margin: 1rem 0; border-left: 4px solid #daa520; color: #8b7355; backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(218, 165, 32, 0.15); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
    .mood-section {{ margin: 1rem 0; padding: 1rem; background: {theme['card']}; border-radius: 12px; border: 1px solid {theme['border']}; }}
    .mood-section h4 {{ margin: 0 0 0.5rem 0; color: {theme['text_primary']}; font-size: 0.95rem; }}
    .mood-circle {{ width: 45px; height: 45px; border-radius: 50%; display: inline-block; margin: 6px; border: 2px solid rgba(255,255,255,0.7); cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .mood-circle:hover {{ transform: scale(1.15); box-shadow: 0 4px 15px rgba(0,0,0,0.2); border-color: {theme['primary']}; }}
    .mood-circle.selected {{ border: 3px solid {theme['primary']}; transform: scale(1.2); box-shadow: 0 4px 20px {theme['shadow']}; }}
    .stats-card {{ background: {theme['card']}; padding: 1.8rem; border-radius: 16px; box-shadow: 0 4px 20px {theme['shadow']}; text-align: center; color: {theme['text_primary']}; border: 1px solid {theme['border']}; backdrop-filter: blur(5px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
    .stats-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 30px {theme['shadow']}; }}
    .stButton > button {{ background: linear-gradient(135deg, {theme['primary']} 0%, {theme['secondary']} 100%); border: none; border-radius: 25px; color: {theme['text_primary']}; padding: 12px 24px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); backdrop-filter: blur(5px); box-shadow: 0 4px 15px {theme['shadow']}; font-weight: 500; }}
    .stButton > button:hover {{ background: linear-gradient(135deg, {theme['secondary']} 0%, {theme['accent']} 100%); transform: translateY(-1px); box-shadow: 0 6px 20px {theme['shadow']}; }}
    .stSelectbox > div > div {{ background: {theme['card']}; border: 1px solid {theme['border']}; border-radius: 12px; backdrop-filter: blur(5px); }}
    .stTextInput > div > div > input {{ background: {theme['card']}; border: 1px solid {theme['border']}; border-radius: 12px; backdrop-filter: blur(5px); color: {theme['text_primary']}; }}
    .stTextArea > div > div > textarea {{ background: {theme['card']}; border: 1px solid {theme['border']}; border-radius: 12px; backdrop-filter: blur(5px); color: {theme['text_primary']}; }}
</style>
"""

def goals_overview_widget(goal_manager: GoalManager):
    goals = goal_manager.load_goals()
    
    if not goals:
        st.markdown("""
        <div class="goals-overview">
            <h3 style="margin-bottom: 1rem; color: var(--primary-color);"> まずは目標を設定しましょう</h3>
            <p style="color: var(--text-secondary); margin: 0;">目標設定ページで今日の目標を設定してください</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    day_goals = [g for g in goals if g.category == "day"]
    week_goals = [g for g in goals if g.category == "week"]
    month_goals = [g for g in goals if g.category == "month"]
    year_goals = [g for g in goals if g.category == "year"]
    
    goals_html = f"""
    <div class="goals-overview">
        <h3 style="margin-bottom: 1rem;"> 現在の目標</h3>
    """
    
    if day_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'> 今日の目標</h4>"
        for goal in day_goals[:2]:
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
            </div>
            """
    
    if week_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'> 今週の目標</h4>"
        for goal in week_goals[:2]:
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
            </div>
            """
    
    if month_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'> 今月の目標</h4>"
        for goal in month_goals[:1]:
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
            </div>
            """

    if year_goals:
        goals_html += "<h4 style='margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.8;'> 今年の目標</h4>"
        for goal in year_goals[:1]:
            goals_html += f"""
            <div class="goal-item">
                <div style="font-weight: 500; font-size: 0.9rem;">{goal.title}</div>
            </div>
            """
    
    goals_html += "</div>"
    st.markdown(goals_html, unsafe_allow_html=True)

def mood_selector():
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