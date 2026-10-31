# state.py
import os
import json

SYSTEM_DIR = "ccc_system"
USER_FILE = os.path.join(SYSTEM_DIR, "System", "users.json")
_ROOT_ABS = os.path.abspath(SYSTEM_DIR)
_current_dir = ""  # 初始当前目录

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        default_users = {"Admin": "ccc"}
        save_users(default_users)
        user_folder = os.path.join(SYSTEM_DIR, "Users", "Admin")
        if not os.path.exists(user_folder):
            os.makedirs(user_folder, exist_ok=True)
        return default_users

def save_users(users):
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
