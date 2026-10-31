# ccc-system-python
A mini CCC OS developed in Python

**lang zh 4 ~ 23**
**lang en 24 ~ 42**
## 功能

- 用户登录/注册
- 虚拟文件系统（ls, cd, mkdir, touch, cat, write, rm）
- 路径安全校验，防止越界访问

## 快速开始

*准备工作：进入仓库上级仓库，如：C:/CCC-OS/。而非C:/CCC-OS/仓库名*

```bash
python -m 命令行版本.main
```
## 可用命令

| 命令 | 说明 |
|------|------|
| `ls` | 列出文件 |
| `cd <目录>` | 切换目录 |
| `mkdir <目录>` | 创建文件夹 |
| `touch <文件>` | 创建文件 |
| `cat <文件>` | 查看内容 |
| `write <文件> <内容>` | 写入文件 |
| `rm <文件/目录>` | 删除 |
| `add_user <用户名> <密码>` | 添加用户 |
| `logout` | 返回登录界面 |
| `clear` | 清屏 |
| `exit` | 退出程序 |

## Features

- User login/registration
- Virtual file system (ls, cd, mkdir, touch, cat, write, rm)
- Path validation to prevent out-of-bounds access

## Quick Start

*Preparatory work: enter the parent warehouse, such as: C:/CCC-OS/. Do not enter C:/CCC-OS/warehouse name*

```bash
python -m 命令行版本.main
```

## Available Commands

| Command | Description |
|---------|-------------|
| `ls` | List files |
| `cd <dir>` | Change directory |
| `mkdir <dir>` | Create a directory |
| `touch <file>` | Create a file |
| `cat <file>` | Display file contents |
| `write <file> <content>` | Write content to a file |
| `rm <file/dir>` | Delete a file or directory |
| `add_user <username> <password>` | Add a new user |
| `logout` | Return to the login screen |
| `clear` | Clear screen |
| `exit` | Exit the program |

