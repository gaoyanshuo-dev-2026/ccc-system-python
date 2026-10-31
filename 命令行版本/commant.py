import os
import shutil
import json

# 假设你有一个 state.py 或者 config.py 存放全局变量
# 如果没有，请将下面的导入改为你实际存放 _current_dir, _ROOT_ABS 等变量的地方
# 例如：如果变量还在 main.py 里且无法移动，这里会再次面临循环导入问题。
# 强烈建议按照之前的建议，将全局变量提取到 state.py
try:
    from .state import (
        _current_dir, 
        _ROOT_ABS, 
        SYSTEM_DIR, 
        USER_FILE, 
        load_users, 
        save_users
    )
except ImportError:
    # 兼容旧结构：如果还没有提取 state.py，这里暂时从 main 导入（不推荐，仅作为过渡）
    # 注意：这仍然可能导致循环导入，除非 main.py 中使用了延迟导入或 TYPE_CHECKING
    from .main import (
        _current_dir, 
        _ROOT_ABS, 
        SYSTEM_DIR, 
        USER_FILE, 
        load_users, 
        save_users
    )

def _get_current_path():
    """获取当前虚拟目录对应的物理绝对路径"""
    if _current_dir:
        return os.path.join(_ROOT_ABS, *_current_dir.split("/"))
    return _ROOT_ABS

def _resolve_path(name):
    """
    解析相对路径为绝对路径，并进行沙箱安全检查。
    禁止访问 _ROOT_ABS 之外的任何路径。
    """
    current_phys = _get_current_path()
    target_phys = os.path.join(current_phys, name)
    
    # 规范化路径（处理 .. 和 .）
    real_path = os.path.normpath(target_phys)
    real_abs = os.path.abspath(real_path)
    
    # 安全检查：确保解析后的路径仍在根目录内
    # 注意：Windows下要注意盘符大小写和分隔符，startswith 需严谨
    if not (real_abs.startswith(_ROOT_ABS + os.sep) or real_abs == _ROOT_ABS):
        return None
        
    return real_abs

def cmd_ls():
    """列出当前目录下的文件和文件夹"""
    path = _get_current_path()
    try:
        items = os.listdir(path)
    except PermissionError:
        print("❌ 权限不足，无法列出此目录")
        return
    except FileNotFoundError:
        print("❌ 当前目录不存在")
        return

    if not items:
        print("（空文件夹）")
        return

    # 排序：文件夹在前，文件在后，按名称字母序
    dirs = []
    files = []
    for item in sorted(items):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            dirs.append(f"📁 {item}/")
        else:
            files.append(f"📄 {item}")
    
    for d in dirs:
        print(d)
    for f in files:
        print(f)

def cmd_touch(filename):
    """创建空文件"""
    path = _resolve_path(filename)
    if path is None:
        print("❌ 非法路径：不能访问系统外部或路径无效")
        return
    
    if os.path.exists(path):
        print(f"⚠️ 文件 '{filename}' 已存在")
    else:
        try:
            with open(path, "w", encoding="utf-8") as f:
                pass
            print(f"✅ 已创建文件: {filename}")
        except Exception as e:
            print(f"❌ 创建文件失败: {e}")

def cmd_cat(filename):
    """查看文件内容"""
    path = _resolve_path(filename)
    if path is None:
        print("❌ 非法路径：不能访问系统外部或路径无效")
        return
    
    if not os.path.exists(path):
        print(f"❌ 文件 '{filename}' 不存在")
        return
    
    if os.path.isdir(path):
        print(f"❌ '{filename}' 是一个文件夹，无法使用 cat 查看")
        return
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if content:
                print(content)
            else:
                print("（空文件）")
    except UnicodeDecodeError:
        print("❌ 无法解码文件内容（可能是二进制文件）")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

def cmd_write(filename, text):
    """写入内容到文件（覆盖模式）"""
    path = _resolve_path(filename)
    if path is None:
        print("❌ 非法路径：不能访问系统外部或路径无效")
        return
    
    try:
        # 如果文件所在目录不存在，mkdir不会自动创建父目录，这里只负责写文件
        # 如果需要自动创建父目录，可以使用 os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ 已写入 {len(text)} 个字符到 '{filename}'")
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")

def cmd_rm(filename):
    """删除文件或文件夹"""
    path = _resolve_path(filename)
    if path is None:
        print("❌ 非法路径：不能访问系统外部或路径无效")
        return
    
    if not os.path.exists(path):
        print(f"❌ '{filename}' 不存在")
        return
    
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"✅ 已删除文件夹: {filename}")
        else:
            os.remove(path)
            print(f"✅ 已删除文件: {filename}")
    except Exception as e:
        print(f"❌ 删除失败: {e}")

def cmd_mkdir(dirname):
    """创建文件夹"""
    path = _resolve_path(dirname)
    if path is None:
        print("❌ 非法路径：不能访问系统外部或路径无效")
        return
    
    if os.path.exists(path):
        print(f"⚠️ '{dirname}' 已存在")
        return
    
    try:
        os.makedirs(path, exist_ok=True)
        print(f"✅ 已创建文件夹: {dirname}")
    except Exception as e:
        print(f"❌ 创建文件夹失败: {e}")

def cmd_cd(dirname):
    """切换目录"""
    global _current_dir  # 需要修改全局状态
    
    if dirname == "..":
        if not _current_dir:
            print("⚠️ 已经在根目录了")
            return
        
        parts = _current_dir.split("/")
        if len(parts) == 1:
            _current_dir = ""
        else:
            _current_dir = "/".join(parts[:-1])
        
        print(f"✅ 已切换到: /{_current_dir if _current_dir else ''}")
        return

    # 处理绝对路径或相对路径
    resolved_path = _resolve_path(dirname)
    
    if resolved_path is None:
        print("❌ 无法切换到该目录：非法路径或超出沙箱范围")
        return
    
    if not os.path.isdir(resolved_path):
        print(f"❌ 文件夹 '{dirname}' 不存在")
        return
    
    # 计算相对于 ROOT 的新虚拟路径
    rel_path = os.path.relpath(resolved_path, _ROOT_ABS)
    if rel_path == ".":
        _current_dir = ""
    else:
        # 统一使用正斜杠作为虚拟路径分隔符
        _current_dir = rel_path.replace(os.sep, "/")
        
    print(f"✅ 已切换到: /{_current_dir if _current_dir else ''}")

def cmd_add_user(username, password):
    """添加新用户"""
    # 保留命令列表，防止用户创建与命令同名的用户导致冲突
    reserved_commands = {
        "exit", "help", "ls", "cd", "touch", "cat", 
        "write", "mkdir", "rm", "add_user", "logout", "pwd", "clear"
    }
    
    if username in reserved_commands:
        print(f"❌ 用户名 '{username}' 是系统保留命令，无法使用")
        return

    users = load_users()
    if username in users:
        print(f"❌ 用户 '{username}' 已存在")
        return
    
    users[username] = password
    save_users(users)
    
    # 为新用户创建个人目录
    user_folder = os.path.join(SYSTEM_DIR, "Users", username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder, exist_ok=True)
        
    print(f"✅ 已添加新用户: {username}")

def cmd_help():
    """显示帮助信息"""
    print("\n📋 ccc 系统可用命令：")
    print("-" * 30)
    print(f"  {'ls':<15} - 列出当前目录文件")
    print(f"  {'cd <dir>':<15} - 切换目录 (支持 cd ..)")
    print(f"  {'pwd':<15} - 显示当前路径")
    print(f"  {'mkdir <dir>':<15} - 创建文件夹")
    print(f"  {'touch <file>':<15} - 创建空文件")
    print(f"  {'cat <file>':<15} - 查看文件内容")
    print(f"  {'write <f> <txt>':<15} - 写入内容到文件")
    print(f"  {'rm <name>':<15} - 删除文件或文件夹")
    print(f"  {'add_user <u> <p>':<15} - 添加新用户")
    print(f"  {'clear':<15} - 清屏")
    print(f"  {'logout':<15} - 退出登录")
    print(f"  {'exit':<15} - 关闭程序")
    print(f"  {'help':<15} - 显示此帮助信息")
    print("-" * 30)
    print("⚠️ 提示：所有文件操作仅限于 ccc_system 目录内")

def cmd_clear():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def cmd_pwd():
    """打印当前工作目录"""
    print(f"/{_current_dir if _current_dir else ''}")
