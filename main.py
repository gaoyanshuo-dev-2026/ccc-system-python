import os
import sys
import time
import json
import shutil

SYSTEM_DIR = "ccc_system"
USER_FILE = os.path.join(SYSTEM_DIR, "users.json")

if not os.path.exists(SYSTEM_DIR):
    os.mkdir(SYSTEM_DIR)
    print(f"已创建专属系统文件夹: {SYSTEM_DIR}")


def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        default_users = {"gao": "123"}
        save_users(default_users)
        return default_users


def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)


def cmd_add_user(username, password):
    users = load_users()
    if username in users or username in ("exit", "help"):
        print(f"用户 '{username}' 已存在, 或者是保留命令，无法添加")
    else:
        users[username] = password
        save_users(users)
        print(f"已添加新用户: {username}")


def _current_path():
    """返回当前虚拟目录对应的物理绝对路径"""
    if _current_dir:
        return os.path.join(_ROOT_ABS, *_current_dir.split("/"))
    return _ROOT_ABS


def _resolve_path(name):
    """把文件名/相对路径解析成物理绝对路径，并校验不越界"""
    target = os.path.join(_current_path(), name)
    real = os.path.normpath(target)
    if not real.startswith(_ROOT_ABS):
        return None
    return real


def cmd_ls():
    path = _current_path()
    try:
        files = os.listdir(path)
    except PermissionError:
        print("权限不足，无法列出此目录")
        return
    if not files:
        print("（空文件夹）")
    else:
        for f in sorted(files):
            full = os.path.join(path, f)
            if os.path.isdir(full):
                print(f"📁 {f}/")
            else:
                print(f"📄 {f}")


def cmd_touch(filename):
    path = _resolve_path(filename)
    if path is None:
        print("非法路径")
        return
    if os.path.exists(path):
        print(f"文件 '{filename}' 已存在")
    else:
        with open(path, "w") as f:
            pass
        print(f"已创建文件: {filename}")


def cmd_cat(filename):
    path = _resolve_path(filename)
    if path is None:
        print("非法路径")
        return
    if not os.path.exists(path):
        print(f"文件 '{filename}' 不存在")
    elif os.path.isdir(path):
        print(f"'{filename}' 是一个文件夹")
    else:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if content:
            print(content)
        else:
            print("（空文件）")


def cmd_write(filename, text):
    path = _resolve_path(filename)
    if path is None:
        print("非法路径")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"已写入 {len(text)} 个字符到 '{filename}'")


def cmd_rm(filename):
    path = _resolve_path(filename)
    if path is None:
        print("非法路径")
        return
    if not os.path.exists(path):
        print(f"'{filename}' 不存在")
    else:
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"已删除文件夹: {filename}")
        else:
            os.remove(path)
            print(f"已删除文件: {filename}")


def cmd_mkdir(filename):
    path = _resolve_path(filename)
    if path is None:
        print("非法路径")
        return
    if os.path.exists(path):
        print(f"文件夹 '{filename}' 已存在")
    else:
        os.makedirs(path, exist_ok=True)
        print(f"已创建文件夹: {filename}")


def _resolve(path):
    if path == "..":
        parts = _current_dir.rstrip("/").split("/")
        if len(parts) <= 1:
            return None
        return "/".join(parts[:-1])
    target = _current_dir + "/" + path if _current_dir else path
    parts = [p for p in target.split("/") if p and p != "."]
    normalized = "/".join(parts)
    real = os.path.normpath(os.path.join(_ROOT_ABS, normalized))
    if not real.startswith(_ROOT_ABS):
        return None
    return normalized


def cmd_cd(dirname):
    global _current_dir
    if dirname == "..":
        parts = _current_dir.rstrip("/").split("/")
        if len(parts) <= 1 and _current_dir:
            _current_dir = ""
        elif not _current_dir:
            print("已经在根目录了")
            return
        else:
            _current_dir = "/".join(parts[:-1])
        print(f"已切换到: {_current_dir or '根目录'}/")
    else:
        resolved = _resolve(dirname)
        if resolved is None:
            print("无法切换到该目录")
        elif not os.path.isdir(os.path.join(_ROOT_ABS, resolved)):
            print(f"文件夹 '{dirname}' 不存在")
        else:
            _current_dir = resolved
            print(f"已切换到文件夹: {dirname}/")


def cmd_help():
    print("📋 可用命令：")
    print(f"  {'ls':<15}\t- 列出文件")
    print(f"  {'touch':<15}\t- 创建文件")
    print(f"  {'cat':<15}\t- 查看文件内容")
    print(f"  {'write':<15}\t- 写入文件")
    print(f"  {'rm':<15}\t- 删除文件/文件夹")
    print(f"  {'mkdir':<15}\t- 创建文件夹")
    print(f"  {'cd':<15}\t- 切换目录（支持 cd ..）")
    print(f"  {'add_user':<15}\t- 添加用户")
    print(f"  {'exit':<15}\t- 退出程序")
    print(f"  {'help':<15}\t- 显示帮助")


# ========== 主程序 ==========
running = True
user_list = load_users()

while running:
    try:
        print("\nHello, I am ccc.")
        user_name = input("Enter your username: ")
        user_password = input("Enter your password: ")

        if user_name in user_list and user_list[user_name] == user_password:
            print("Login successful!")

            spinner = ['|', '/', '-', '\\']
            for i in range(15):
                sys.stdout.write(f'\r正在进入系统 {spinner[i % 4]}')
                sys.stdout.flush()
                time.sleep(0.3)
            print('\r欢迎进入 ccc 系统！          ')

            os.chdir(SYSTEM_DIR)
            _ROOT_ABS = os.path.abspath(".")
            _current_dir = ""
            print(f"Welcome, {user_name}! 当前目录: {os.getcwd()}")
            print("Type 'exit' to shut down. Type 'help' for help.")

            while True:
                command = input("ccc> ").strip()

                if command == "exit":
                    print("Shutting down the program...")
                    running = False
                    break
                elif command == "help":
                    cmd_help()
                elif command == "ls":
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
                elif command.startswith("cd "):
                    dirname = command[3:].strip()
                    if dirname:
                        cmd_cd(dirname)
                    else:
                        print("用法: cd <文件夹名>")
                elif command.startswith("add_user "):
                    parts = command[9:].strip().split(" ", 1)
                    if len(parts) == 2:
                        cmd_add_user(parts[0], parts[1])
                        user_list = load_users()
                    else:
                        print("用法: add_user <用户名> <密码>")
                else:
                    print(f"未知命令: {command}")

        elif user_name in ("exit", "help") or user_password in ("exit", "help"):
            print("Invalid username or password. (Press any key to shut down.)")
            input()
            running = False
        else:
            print("Invalid username or password. (Press any key to shut down.)")
            input()
            running = False

    except KeyboardInterrupt:
        input("\n程序已中断，正在退出...")
        running = False
    except Exception as e:
        print(f"发生错误: {e}")
        input("按任意键继续...")
        running = False