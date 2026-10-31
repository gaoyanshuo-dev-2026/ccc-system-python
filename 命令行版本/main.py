import os
import sys
import time
import json
import shutil

# ===== 内测版本标记 =====
VERSION = "1.0.7-alpha"
SYSTEM_DIR = "ccc_system"
USER_FILE = os.path.join(SYSTEM_DIR, "System", "users.json")

# 初始化系统目录
if not os.path.exists(SYSTEM_DIR):
    os.mkdir(SYSTEM_DIR)
    os.mkdir(os.path.join(SYSTEM_DIR, "Users"))
    os.mkdir(os.path.join(SYSTEM_DIR, "System"))
    print(f"✅ 已创建专属系统文件夹: {SYSTEM_DIR}")

USER_FILE = os.path.abspath(os.path.join(SYSTEM_DIR, "System", "users.json"))
# 固定全局根：整个文件系统都在 SYSTEM_DIR 里面
_ROOT_ABS = os.path.abspath(SYSTEM_DIR)
_current_dir = ""


def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        default_users = {"Admin": "ccc"}
        save_users(default_users)
        user_folder = os.path.join(SYSTEM_DIR, "Users", "Admin")
        if not os.path.exists(user_folder):
            os.mkdir(user_folder)
        return default_users


def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def cmd_add_user(username, password):
    users = load_users()
    if username in users or username in ("exit", "help", "ls", "cd", "touch", "cat", "write", "mkdir", "rm", "add_user", "logout"):
        print(f"❌ 用户 '{username}' 已存在，或者是保留命令，无法添加")
        return
    users[username] = password
    save_users(users)
    user_folder = os.path.join(SYSTEM_DIR, "Users", username)
    if not os.path.exists(user_folder):
        os.mkdir(user_folder)
    print(f"✅ 已添加新用户: {username}")


def _current_path():
    """返回当前虚拟目录对应的物理绝对路径，根是 ccc_system"""
    if _current_dir:
        return os.path.join(_ROOT_ABS, *_current_dir.split("/"))
    return _ROOT_ABS


def _resolve_path(name):
    """解析路径，只禁止跳出 _ROOT_ABS（ccc_system），内部随便走"""
    target = os.path.join(_current_path(), name)
    real = os.path.normpath(target)
    # 关键：不能跑到 ccc_system 外面
    if not real.startswith(_ROOT_ABS):
        return None
    return real


def cmd_ls():
    path = _current_path()
    try:
        files = os.listdir(path)
    except PermissionError:
        print("❌ 权限不足，无法列出此目录")
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
        print("❌ 非法路径（不能访问系统外部）")
        return
    if os.path.exists(path):
        print(f"⚠️ 文件 '{filename}' 已存在")
    else:
        with open(path, "w", encoding="utf-8") as f:
            pass
        print(f"✅ 已创建文件: {filename}")


def cmd_cat(filename):
    path = _resolve_path(filename)
    if path is None:
        print("❌ 非法路径（不能访问系统外部）")
        return
    if not os.path.exists(path):
        print(f"❌ 文件 '{filename}' 不存在")
    elif os.path.isdir(path):
        print(f"❌ '{filename}' 是一个文件夹")
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
        print("❌ 非法路径（不能访问系统外部）")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✅ 已写入 {len(text)} 个字符到 '{filename}'")


def cmd_rm(filename):
    path = _resolve_path(filename)
    if path is None:
        print("❌ 非法路径（不能访问系统外部）")
        return
    if not os.path.exists(path):
        print(f"❌ '{filename}' 不存在")
    else:
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"✅ 已删除文件夹: {filename}")
        else:
            os.remove(path)
            print(f"✅ 已删除文件: {filename}")


def cmd_mkdir(filename):
    path = _resolve_path(filename)
    if path is None:
        print("❌ 非法路径（不能访问系统外部）")
        return
    if os.path.exists(path):
        print(f"⚠️ 文件夹 '{filename}' 已存在")
    else:
        os.makedirs(path, exist_ok=True)
        print(f"✅ 已创建文件夹: {filename}")


def cmd_cd(dirname):
    global _current_dir
    if dirname == "..":
        parts = _current_dir.rstrip("/").split("/")
        if not _current_dir or len(parts) <= 1:
            print("⚠️ 已经在根目录了")
            return
        _current_dir = "/".join(parts[:-1])
        print(f"✅ 已切换到: /{_current_dir}")
        return

    resolved = _resolve_path(dirname)
    if resolved is None:
        print("❌ 无法切换到该目录（非法路径）")
        return
    if not os.path.isdir(resolved):
        print(f"❌ 文件夹 '{dirname}' 不存在")
        return
    # 转成相对于根的虚拟路径
    rel = os.path.relpath(resolved, _ROOT_ABS)
    if rel == ".":
        _current_dir = ""
    else:
        _current_dir = rel
    print(f"✅ 已切换到文件夹: {dirname}/")


def cmd_help():
    print("📋 可用命令：")
    print(f"  {'ls':<15}\t- 列出文件")
    print(f"  {'touch':<15}\t- 创建文件")
    print(f"  {'cat':<15}\t- 查看文件内容")
    print(f"  {'write':<15}\t- 写入文件")
    print(f"  {'rm':<15}\t- 删除文件/文件夹")
    print(f"  {'mkdir':<15}\t- 创建文件夹")
    print(f"  {'cd':<15}\t- 切换目录（支持 cd ..）")
    print(f"  {'add_user':<15}\t- 添加用户【内测：所有用户可用】")
    print(f"  {'logout':<15}\t- 退出回到登录界面")
    print(f"  {'exit':<15}\t- 完全关闭程序")
    print(f"  {'help':<15}\t- 显示帮助")
    print("\n⚠️ 提示：当前为内部测试版，无目录隔离，所有用户共享文件树，功能可能存在BUG！")


# ========== 主程序 ==========
def main():
    global _current_dir
    running = True
    user_list = load_users()

    while running:
        print("\n===== ccc 系统登录 =====")
        print(f"版本：{VERSION} | 【内部测试 0.x.x 开发版】")
        print("⚠️ 内测版：全局共享文件系统，无用户目录隔离\n")
        user_name = input("请输入您的用户名: ").strip()
        user_password = input("请输入您的密码: ").strip()

        if user_name in user_list and user_list[user_name] == user_password:
            print("✅ 登录成功！")
            spinner = ['|', '/', '-', '\\']
            for i in range(15):
                sys.stdout.write(f'\r正在进入系统 {spinner[i % 4]}')
                sys.stdout.flush()
                time.sleep(0.3)
            print(f'\r🎉 欢迎进入 ccc 系统 | v{VERSION}            ')

            # 登录之后：固定根，当前路径重置到 /
            _current_dir = ""
            print(f"Welcome, {user_name}! 系统根目录: {_ROOT_ABS}")
            print("输入 'logout' 返回登录页，'exit' 关闭程序，'help' 查看命令\n")

            shell_loop = True
            while shell_loop:
                prompt_path = f"/{_current_dir}" if _current_dir else "/"
                command = input(f"{user_name}@ccc:{prompt_path}> ").strip()

                if command == "exit":
                    print("👋 Shutting down the program...")
                    running = False
                    shell_loop = False

                elif command == "logout":
                    print("📤 登出，返回登录页面...")
                    _current_dir = ""
                    shell_loop = False

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
                elif command == "":
                    continue
                else:
                    print(f"❌ 未知命令: {command}")

        else:
            print("❌ 用户名或密码错误，请重新输入！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 程序被手动中断，退出")
    except Exception as e:
        print(f"\n💥 全局异常: {e}")
        print(f"版本 {VERSION} 捕获异常：", e)
        input("按回车关闭窗口")
