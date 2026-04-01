"""
日志配置演示脚本
展示如何使用新的日志配置模块
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from infrastructure.log_config import (
    LogManager,
    LogConfig,
    LogLevel,
    LogGranularity,
    setup_logger,
    get_log_manager,
    set_log_granularity
)
import logging


def demo_basic_usage():
    """基础用法演示"""
    print("\n" + "="*60)
    print("📝 基础用法演示")
    print("="*60)
    
    # 1. 创建默认配置
    config = LogConfig()
    logger = setup_logger(config=config)
    
    # 2. 获取日志管理器
    log_manager = get_log_manager()
    
    # 3. 记录不同级别的日志
    logging.debug("🔍 DEBUG - 调试信息 (默认不显示)")
    logging.info("ℹ️ INFO - 常规信息")
    logging.warning("⚠️ WARNING - 警告信息")
    logging.error("❌ ERROR - 错误信息")
    

def demo_granularity_levels():
    """日志粒度级别演示"""
    print("\n" + "="*60)
    print("📊 日志粒度级别演示")
    print("="*60)
    
    log_manager = get_log_manager()
    
    # 测试不同粒度级别
    levels = [
        (LogGranularity.MINIMAL, "最小化 - 只显示错误"),
        (LogGranularity.BASIC, "基础 - 显示错误和警告"),
        (LogGranularity.NORMAL, "正常 - 显示 INFO 及以上"),
        (LogGranularity.DETAILED, "详细 - 显示所有 INFO+DEBUG"),
        (LogGranularity.VERBOSE, "最详细 - 显示所有细节"),
    ]
    
    for granularity, description in levels:
        print(f"\n👉 当前设置：{description}")
        log_manager.set_granularity(granularity)
        
        logging.debug("   [DEBUG] 这是调试信息")
        logging.info("   [INFO] 这是常规信息")
        logging.warning("   [WARNING] 这是警告信息")
        logging.error("   [ERROR] 这是错误信息")


def demo_custom_config():
    """自定义配置演示"""
    print("\n" + "="*60)
    print("⚙️ 自定义配置演示")
    print("="*60)
    
    # 创建自定义配置
    custom_config = LogConfig(
        level=LogLevel.DEBUG,           # 显示所有级别
        granularity=LogGranularity.VERBOSE,  # 最详细模式
        show_module=True,               # 显示模块名
        show_timestamp=True,            # 显示时间戳
        show_colors=True,               # 启用颜色
        max_lines=500,                  # GUI 最大显示 500 行
        enable_gui=False,               # 不启用 GUI(控制台程序)
        enable_console=True,            # 启用控制台
        enable_file=False,              # 不写入文件
    )
    
    logger = setup_logger(config=custom_config)
    
    logging.debug("🔧 自定义配置的调试信息")
    logging.info("✨ 自定义信息的常规信息")
    logging.warning("⚡ 自定义配置的警告信息")


def demo_dynamic_switching():
    """动态切换演示"""
    print("\n" + "="*60)
    print("🔄 动态切换演示")
    print("="*60)
    
    log_manager = get_log_manager()
    
    # 初始为正常模式
    print("\n📌 初始状态：正常模式")
    log_manager.set_granularity(LogGranularity.NORMAL)
    logging.info("这是一条 INFO 信息")
    logging.debug("这是一条 DEBUG 信息 (应该看不到)")
    
    # 切换到详细模式
    print("\n📌 切换到详细模式...")
    log_manager.set_granularity(LogGranularity.VERBOSE)
    logging.info("这是一条 INFO 信息")
    logging.debug("这是一条 DEBUG 信息 (现在应该能看到)")
    
    # 切换到最小化模式
    print("\n📌 切换到最小化模式...")
    log_manager.set_granularity(LogGranularity.MINIMAL)
    logging.info("这是一条 INFO 信息 (应该看不到)")
    logging.warning("这是一条 WARNING 信息 (应该看不到)")
    logging.error("这是一条 ERROR 信息")


def demo_level_constants():
    """日志级别常量演示"""
    print("\n" + "="*60)
    print("📏 日志级别常量演示")
    print("="*60)
    
    log_manager = get_log_manager()
    
    # 使用 LogLevel 枚举
    print("\n📌 使用 LogLevel.DEBUG")
    log_manager.set_level(LogLevel.DEBUG)
    logging.log(logging.DEBUG, "DEBUG 级别的日志")
    logging.log(logging.INFO, "INFO 级别的日志")
    
    print("\n📌 使用 LogLevel.ERROR")
    log_manager.set_level(LogLevel.ERROR)
    logging.log(logging.DEBUG, "DEBUG 级别的日志 (应该看不到)")
    logging.log(logging.INFO, "INFO 级别的日志 (应该看不到)")
    logging.log(logging.ERROR, "ERROR 级别的日志")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎯 日志配置模块功能演示")
    print("="*60)
    
    # 1. 基础用法
    demo_basic_usage()
    
    # 2. 粒度级别
    demo_granularity_levels()
    
    # 3. 自定义配置
    demo_custom_config()
    
    # 4. 动态切换
    demo_dynamic_switching()
    
    # 5. 级别常量
    demo_level_constants()
    
    print("\n" + "="*60)
    print("✅ 演示完成!")
    print("="*60)
    
    print("\n💡 使用提示:")
    print("1. 在 GUI 应用中，日志粒度可以通过下拉框实时切换")
    print("2. 快捷按钮可以快速切换到'详细调试'或'只看错误'模式")
    print("3. 可以通过 LogConfig 自定义日志输出格式和行为")
    print("4. 支持同时输出到控制台、GUI 和文件")
    print("5. 日志级别从低到高：DEBUG < INFO < WARNING < ERROR < CRITICAL")


if __name__ == "__main__":
    main()
