"""
AI 智能翻译工作台 v2.0 - 主入口文件

本程序采用模块化设计，各功能模块已解耦：
- models.py: 数据模型定义
- logging_config.py: 日志系统配置
- config.py: 配置管理和常量
- prompt_builder.py: 提示词构建器
- fuzzy_matcher.py: 模糊匹配引擎
- concurrency_controller.py: 自适应并发控制
- terminology_manager.py: 术语库管理
- api_stages.py: API 处理阶段（初译/校对）
- workflow_orchestrator.py: 工作流编排
- gui_app.py: 图形用户界面
- config_persistence.py: 配置持久化（JSON/YAML）
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
