"""
AI 智能翻译工作台 v3.0 - 主入口文件

本程序采用六层分层架构：
- presentation/     : 表示层 (GUI/CLI)
- application/      : 应用层 (流程编排/外观模式)
- domain/          : 领域层 (核心业务逻辑)
- service/         : 服务层 (API 集成)
- data_access/     : 数据访问层 (仓储/持久化)
- infrastructure/  : 基础设施层 (DI/日志/工具)
- config/          : 配置管理
"""
import multiprocessing
import tkinter as tk
from tkinter import ttk
import sys
import os

# 设置 UTF-8 编码模式（解决 Windows 控制台编码问题）
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gui_app import TranslationApp


def main():
    """应用程序入口点"""
    # 多进程支持
    multiprocessing.freeze_support()
    
    # 解析命令行参数
    config_file = None
    if len(sys.argv) > 1:
        # 检查是否是帮助参数
        if sys.argv[1] in ['--help', '-h', '-help', 'help']:
            print("AI 智能翻译工作台 v3.0.0")
            print("\n用法:")
            print("  python presentation/translation.py                    # 使用默认配置文件")
            print("  python presentation/translation.py [配置文件路径]      # 指定配置文件")
            print("\n示例:")
            print("  python presentation/translation.py config/config.json")
            print("\n配置说明:")
            print("  - 配置文件格式：JSON 或 YAML")
            print("  - 默认配置文件：config/config.json")
            print("  - API 密钥必须在配置文件中设置")
            return
        
        config_file = sys.argv[1]
        print(f"[INFO] 使用配置文件：{config_file}")
    
    # 创建主窗口
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')  # 使用更现代的主题
    
    # 启动应用（传入配置文件路径）
    app = TranslationApp(root, config_file=config_file)
    
    # 运行事件循环
    root.mainloop()


if __name__ == "__main__":
    main()
