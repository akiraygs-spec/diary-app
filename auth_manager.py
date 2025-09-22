import streamlit as st
import datetime
import json
import os
import hashlib
import re
from typing import List
from dataclasses import asdict
from data_models import User

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
    
    def update_nickname(self, email: str, new_nickname: str) -> bool:
        if not new_nickname.strip():
            st.error("ニックネームを入力してください")
            return False
        
        users = self.load_users()
        for user in users:
            if user.email == email:
                user.nickname = new_nickname.strip()
                self.save_users(users)
                return True
        return False