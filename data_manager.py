import streamlit as st
import json
import os
import hashlib
from typing import List
from dataclasses import asdict
from data_models import Goal, DiaryEntry

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