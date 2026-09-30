import os
import sys
import time
import json

# 专属文件夹路径（固定，不会被 cd 改变）
SYSTEM_DIR = "ccc_system"
USER_FILE = os.path.join(SYSTEM_DIR, "users.json")

# 程序启动时自动创建专属文件夹
if not os.path.exists(SYSTEM_DIR):
    os.mkdir(SYSTEM_DIR)
    print(f"已创建专属系统文件夹: {SYSTEM_DIR}")


def get_path(filename):
    """把文件名拼接成专属文件夹内的完整路径"""
    return os.path.join(SYSTEM_DIR, filename)

def load_users():
    """从文件加载用户数据，如果文件不存在则返回默认用户"""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        default_users = {"gao": "123"}
        save_users(default_users)
        return default_users

def save_users(users):
    """将用户数据保存到文件"""
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)

def cmd_add_user(username, password):
    """添加新用户"""
    users = load_users()
    if username in users:
        print(f"用户 '{username}' 已存在")
    else:
        users[username] = password
        save_users(users)
        print(f"已添加新用户: {username}")

def cmd_ls():
    """列出专属文件夹内的所有文件"""
    files = os.listdir(SYSTEM_DIR)
    if not files:
        print("（空文件夹）")
    else:
        for f in files:
            full_path = get_path(f)
            if os.path.isdir(full_path):
                print(f"📁 {f}/")
            else:
                print(f"📄 {f}")

def cmd_touch(filename):
    """创建一个空文件"""
    path = get_path(filename)
    if os.path.exists(path):
        print(f"文件 '{filename}' 已存在")
    else:
        with open(path, "w") as f:
            pass
        print(f"已创建文件: {filename}")

def cmd_cat(filename):
    """查看文件内容"""
    path = get_path(filename)
    if not os.path.exists(path):
        print(f"文件 '{filename}' 不存在")
    elif os.path.isdir(path):
        print(f"'{filename}' 是一个文件夹")
    else:
        with open(path, "r") as f:
            content = f.read()
        if content:
            print(content)
        else:
            print("（空文件）")

def cmd_write(filename, text):
    """向文件写入内容"""
    path = get_path(filename)
    with open(path, "w") as f:
        f.write(text)
    print(f"已写入 {len(text)} 个字符到 '{filename}'")

def cmd_rm(filename):
    """删除文件"""
    path = get_path(filename)
    if not os.path.exists(path):
        print(f"文件 '{filename}' 不存在")
    else:
        if os.path.isdir(path):
            os.rmdir(path)
            print(f"已删除文件夹: {filename}")
        else:
            os.remove(path)
            print(f"已删除文件: {filename}")

def cmd_mkdir(filename):
    """创建一个文件夹"""
    path = get_path(filename)
    if os.path.exists(path):
        print(f"文件夹 '{filename}' 已存在")
    else:
        os.mkdir(path)
        print(f"已创建文件夹: {filename}")

def cmd_help():
    """显示帮助信息"""
    print("📋 可用命令：")
    print(f"  {'ls':<15}\t- 列出文件")
    print(f"  {'touch':<15}\t- 创建文件")
    print(f"  {'cat':<15}\t- 查看文件内容")
    print(f"  {'write':<15}\t- 写入文件")
    print(f"  {'rm':<15}\t- 删除文件/文件夹")
    print(f"  {'mkdir':<15}\t- 创建文件夹")
    print(f"  {'add_user':<15}\t- 添加用户")
    print(f"  {'exit':<15}\t- 退出程序")
    print(f"  {'help':<15}\t- 显示帮助")

# ========== 主程序 ==========
running = True

user_list = load_users()

while running:
    print("\nHello, I am ccc.")
    user_name = input("Enter your username: ")
    user_password = input("Enter your password: ")

    if user_name in user_list and user_list[user_name] == user_password:
        print("Login successful!")

        # 加载动画
        spinner = ['|', '/', '-', '\\']
        for i in range(15):
            sys.stdout.write(f'\r正在进入系统 {spinner[i % 4]}')
            sys.stdout.flush()
            time.sleep(0.3)
        print('\r欢迎进入 ccc 系统！          ')

        print(f"Welcome, {user_name}! 你的专属文件夹: {SYSTEM_DIR}/")
        print("Type 'exit' to shut down. Type 'help' for help.")

        while True:
            command = input("ccc> ").strip()

            if command == "exit":
                print("Shutting down the program...")
                running = False
                break

            elif command == "help":
                cmd_help()

            elif command.startswith("ls"):
                cmd_ls()

            elif command.startswith("touch "):
                filename = command[6:].strip()
                if filename:
                    cmd_touch(filename)
                else:
                    print("用法: touch <文件名>")

            elif command.startswith("cat "):
                filename = command[4:].strip()
                if filename:
                    cmd_cat(filename)
                else:
                    print("用法: cat <文件名>")

            elif command.startswith("write "):
                parts = command[6:].strip().split(" ", 1)
                if len(parts) == 2:
                    cmd_write(parts[0], parts[1])
                else:
                    print("用法: write <文件名> <内容>")

            elif command.startswith("rm "):
                filename = command[3:].strip()
                if filename:
                    cmd_rm(filename)
                else:
                    print("用法: rm <文件名>")

            elif command.startswith("mkdir "):
                filename = command[6:].strip()
                if filename:
                    cmd_mkdir(filename)
                else:
                    print("用法: mkdir <文件夹名>")

            elif command.startswith("add_user "):
                parts = command[9:].strip().split(" ", 1)
                if len(parts) == 2:
                    cmd_add_user(parts[0], parts[1])
                    user_list = load_users()  # 刷新用户列表
                else:
                    print("用法: add_user <用户名> <密码>")

            else:
                print(f"未知命令: {command}")

    else:
        print("Invalid username or password. (Press any key to shut down.)")
        input()
        running = False