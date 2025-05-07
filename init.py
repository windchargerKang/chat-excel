#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化脚本：帮助用户快速开始使用Chat-Excel工具

这个脚本会检查环境，安装依赖，并提供简单的使用说明。
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 6):
        print(f"错误: 需要Python 3.6或更高版本，当前版本为{major}.{minor}")
        return False
    print(f"Python版本检查通过: {major}.{minor}")
    return True

def install_dependencies():
    """安装依赖"""
    print("\n安装依赖...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print(f"错误: 找不到依赖文件 {requirements_file}")
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], check=True)
        print("依赖安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"安装依赖时出错: {e}")
        return False

def setup_env():
    """设置环境变量"""
    print("\n设置环境变量...")
    env_example = Path(__file__).parent / ".env.example"
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists() and env_example.exists():
        # 复制示例环境变量文件
        with open(env_example, "r", encoding="utf-8") as src:
            with open(env_file, "w", encoding="utf-8") as dst:
                dst.write(src.read())
        print(f"已创建环境变量文件: {env_file}")
    elif env_file.exists():
        print(f"环境变量文件已存在: {env_file}")
    else:
        print("警告: 找不到环境变量示例文件，跳过环境变量设置")

def create_output_dir():
    """创建输出目录"""
    output_dir = Path(__file__).parent / "output"
    if not output_dir.exists():
        output_dir.mkdir()
        print(f"\n已创建输出目录: {output_dir}")

def show_usage():
    """显示使用说明"""
    print("\n" + "=" * 50)
    print("Chat-Excel 工具已准备就绪！")
    print("=" * 50)
    print("\n基本用法:")
    print("python chat_excel.py 你的文件.xlsx")
    print("\n更多选项:")
    print("python chat_excel.py --help")
    print("\n示例:")
    print("python examples/example.py")
    print("\n" + "=" * 50)

def main():
    """主函数"""
    print("初始化 Chat-Excel 工具...\n")
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_dependencies():
        return
    
    # 设置环境变量
    setup_env()
    
    # 创建输出目录
    create_output_dir()
    
    # 显示使用说明
    show_usage()

if __name__ == "__main__":
    main()