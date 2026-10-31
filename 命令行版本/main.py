import os
import sys
import time
import json

# 尝试以包模式导入，如果失败则尝试直接导入（兼容直接运行 python main.py 的情况）
try:
    from .state import (
        SYSTEM_DIR, 
        USER_FILE, 
        _ROOT_ABS, 
        load_users, 
        save_users,
        _current_dir
    )
    from . import commant
except ImportError:
    import state
    from state import (
        SYSTEM_DIR, 
        USER_FILE, 
        _ROOT_ABS, 
        load_users, 
        save_users,
        _current_dir
    )
    import commant

def init_system():
    """
    初始化系统目录结构。
    如果 ccc_system 文件夹不存在，则创建基础结构。
    """
    if not os.path.exists(SYSTEM_DIR):
        os.mkdir(SYSTEM_DIR)
        os.mkdir(os.path.join(SYSTEM_DIR, "Users"))
        os.mkdir(os.path.join(SYSTEM_DIR, "System"))
        print(f"✅ 已创建专属系统文件夹: {SYSTEM_DIR}")
    
    # 确保全局根路径是绝对路径且最新
    global _ROOT_ABS
    _ROOT_ABS = os.path.abspath(SYSTEM_DIR)

def show_loading_animation(duration=1.5):
    """显示简单的加载动画"""
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    while time.time() < end_time:
        for char in spinner:
            sys.stdout.write(f'\r正在进入系统 {char}')
            sys.stdout.flush()
            time.sleep(0.1)
    print('\r🎉 欢迎进入 ccc system!             ')

def handle_login():
    """
    处理用户登录逻辑。
    返回: 成功登录的用户名 (str)，如果用户选择退出则返回 None
    """
    while True:
        print("\n===== ccc 系统登录 =====")
        user_name = input("请输入您的用户名: ").strip()
        user_password = input("请输入您的密码: ").strip()

        if not user_name or not user_password:
            print("❌ 用户名和密码不能为空")
            continue

        # 每次登录时重新加载用户列表，确保数据最新
        user_list = load_users()
        
        if user_name in user_list and user_list[user_name] == user_password:
            print("✅ 登录成功！")
            show_loading_animation()
            return user_name
        else:
            print("❌ 用户名或密码错误，请重新输入！")

def start_shell(user_name):
    """
    启动 Shell 交互界面。
    参数:
        user_name: 当前登录的用户名
    返回:
        bool: True 表示用户请求登出（返回登录页），False 表示用户请求退出程序
    """
    # 登录成功后，重置当前目录为根目录
    # 注意：这里修改的是 state 模块中的全局变量
    state._current_dir = ""
    
    running = True
    while running:
        try:
            # 构建命令提示符
            prompt_path = f"/{state._current_dir}" if state._current_dir else "/"
            raw_input = input(f"{user_name}@ccc:{prompt_path}> ")
            
            if not raw_input:
                continue
            
            # 解析命令和参数
            parts = raw_input.strip().split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            # --- 命令分发逻辑 ---
            
            if cmd == "exit":
                print("👋 Shutting down the program...")
                return False  # 退出程序

            elif cmd == "logout":
                print("📤 登出，返回登录页面...")
                return True   # 返回登录页

            elif cmd == "help":
                commant.cmd_help()

            elif cmd == "ls":
                commant.cmd_ls()

            elif cmd == "pwd":
                commant.cmd_pwd()

            elif cmd == "clear":
                commant.cmd_clear()

            elif cmd == "touch":
                if args:
                    commant.cmd_touch(args.strip())
                else:
                    print("用法: touch <文件名>")

            elif cmd == "cat":
                if args:
                    commant.cmd_cat(args.strip())
                else:
                    print("用法: cat <文件名>")

            elif cmd == "write":
                # write 命令格式: write <filename> <content>
                if args:
                    write_parts = args.strip().split(maxsplit=1)
                    if len(write_parts) == 2:
                        commant.cmd_write(write_parts[0], write_parts[1])
                    else:
                        print("用法: write <文件名> <内容>")
                else:
                    print("用法: write <文件名> <内容>")

            elif cmd == "rm":
                if args:
                    commant.cmd_rm(args.strip())
                else:
                    print("用法: rm <文件名/文件夹名>")

            elif cmd == "mkdir":
                if args:
                    commant.cmd_mkdir(args.strip())
                else:
                    print("用法: mkdir <文件夹名>")

            elif cmd == "cd":
                if args:
                    commant.cmd_cd(args.strip())
                else:
                    # cd 无参数默认回到根目录
                    state._current_dir = ""
                    print("✅ 已切换到根目录: /")

            elif cmd == "add_user":
                if args:
                    user_parts = args.strip().split(maxsplit=1)
                    if len(user_parts) == 2:
                        commant.cmd_add_user(user_parts[0], user_parts[1])
                    else:
                        print("用法: add_user <用户名> <密码>")
                else:
                    print("用法: add_user <用户名> <密码>")

            else:
                print(f"❌ 未知命令: '{cmd}'。输入 'help' 查看可用命令。")

        except KeyboardInterrupt:
            print("\n⚠️ 检测到中断信号 (Ctrl+C)")
            confirm = input("确定要退出程序吗? (y/n): ").strip().lower()
            if confirm == 'y':
                return False
            else:
                continue
        except Exception as e:
            print(f"\n💥 发生未知错误: {e}")
            # 调试时可取消下面注释查看堆栈
            # import traceback; traceback.print_exc()

def main():
    """程序主入口"""
    try:
        # 1. 初始化系统环境
        init_system()
        
        # 2. 主循环：处理登录 -> Shell -> 登出/退出
        while True:
            user_name = handle_login()
            if user_name is None:
                break
            
            # 进入 Shell，根据返回值决定是重新登录还是彻底退出
            should_logout = start_shell(user_name)
            if not should_logout:
                break
                
    except Exception as e:
        print(f"\n💥 全局异常: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
