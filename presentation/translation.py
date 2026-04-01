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

# 使用 gui_app 中的 TranslationApp（功能完整版）
from presentation.gui_app import run_gui_app


def main():
    """应用程序入口点"""
    import logging
    logger = logging.getLogger(__name__)
    
    # 多进程支持
    multiprocessing.freeze_support()
    
    # 解析命令行参数
    config_file = None
    logger.info(f"📋 translation.py 启动 - sys.argv: {sys.argv}")
    logger.info(f"📋 参数数量：{len(sys.argv)}")
    
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
        logger.info(f"📂 从命令行获取配置文件：{config_file}")
        print(f"[INFO] 使用配置文件：{config_file}")
    else:
        logger.warning("⚠️ 未提供命令行参数")
    
    # 启动应用（使用功能完整的 TranslationApp）
    logger.info(f"📦 启动 TranslationApp - config_file={config_file}")
    run_gui_app(config_file)
    
    # 运行事件循环
    # root.mainloop() 已经在 run_gui_app 中调用


if __name__ == "__main__":
    main()
