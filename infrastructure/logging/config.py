"""
日志配置模块
提供可配置的日志粒度控制和格式化输出
"""
import logging
import sys
import tkinter as tk
from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = logging.DEBUG      # 10 - 最详细
    INFO = logging.INFO        # 20 - 常规信息
    WARNING = logging.WARNING  # 30 - 警告
    ERROR = logging.ERROR      # 40 - 错误
    CRITICAL = logging.CRITICAL  # 50 - 严重错误


class LogGranularity(Enum):
    """日志粒度级别"""
    MINIMAL = "minimal"        # 最小化 - 只显示错误
    BASIC = "basic"            # 基础 - 显示错误、警告、关键信息
    NORMAL = "normal"          # 正常 - 显示 INFO 及以上
    DETAILED = "detailed"      # 详细 - 显示所有 INFO + DEBUG
    VERBOSE = "verbose"        # 最详细 - 显示所有级别包括 DEBUG 细节


class LogTag(Enum):
    """日志标签 (按重要程度)"""
    CRITICAL = 5       # 严重错误 - 系统崩溃、数据丢失
    ERROR = 4          # 错误 - 操作失败、API 异常
    WARNING = 3        # 警告 - 潜在问题、降级处理
    IMPORTANT = 2      # 重要 - 关键业务节点、用户可见变更
    PROGRESS = 2       # 进度 - 任务执行进度、百分比
    NORMAL = 1         # 普通 - 常规业务流程
    DEBUG = 0          # 调试 - 技术细节、内部状态
    TRACE = -1         # 追踪 - 最详细的执行路径


@dataclass
class LogConfig:
    """日志配置数据类"""
    level: LogLevel = LogLevel.INFO
    granularity: LogGranularity = LogGranularity.NORMAL
    min_tag: LogTag = LogTag.NORMAL     # 最小显示的标签级别
    show_module: bool = True            # 显示模块名
    show_timestamp: bool = True         # 显示时间戳
    show_colors: bool = True            # 终端显示颜色
    gui_mode: bool = False              # GUI 模式
    text_widget: Optional[tk.Text] = None  # GUI 文本控件
    max_lines: int = 1000               # GUI 最大显示行数


def get_log_level_for_granularity(granularity: LogGranularity) -> LogLevel:
    """
    根据粒度获取对应的日志级别

    Args:
        granularity: 日志粒度

    Returns:
        对应的日志级别
    """
    mapping = {
        LogGranularity.MINIMAL: LogLevel.ERROR,
        LogGranularity.BASIC: LogLevel.WARNING,
        LogGranularity.NORMAL: LogLevel.INFO,
        LogGranularity.DETAILED: LogLevel.DEBUG,
        LogGranularity.VERBOSE: LogLevel.DEBUG,
    }
    return mapping.get(granularity, LogLevel.INFO)


def get_min_tag_for_granularity(granularity: LogGranularity) -> LogTag:
    """
    根据粒度获取最小显示的标签级别

    Args:
        granularity: 日志粒度

    Returns:
        最小标签级别
    """
    mapping = {
        LogGranularity.MINIMAL: LogTag.ERROR,
        LogGranularity.BASIC: LogTag.WARNING,
        LogGranularity.NORMAL: LogTag.NORMAL,
        LogGranularity.DETAILED: LogTag.DEBUG,
        LogGranularity.VERBOSE: LogTag.TRACE,
    }
    return mapping.get(granularity, LogTag.NORMAL)


def setup_logger(
    name: str,
    level: Optional[LogLevel] = None,
    granularity: LogGranularity = LogGranularity.NORMAL,
    gui_config: Optional[Dict] = None
) -> logging.Logger:
    """
    设置日志器

    Args:
        name: 日志器名称
        level: 日志级别
        granularity: 日志粒度
        gui_config: GUI 配置（包含 text_widget 等）

    Returns:
        配置好的日志器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 根级别设为 DEBUG，让 handler 控制过滤

    # 清除已有的 handler
    logger.handlers.clear()

    # 确定日志级别
    if level is None:
        level = get_log_level_for_granularity(granularity)

    # 创建控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level.value)

    # 设置格式化器
    if gui_config and gui_config.get('show_colors', True):
        from .formatter import ColorFormatter
        console_handler.setFormatter(ColorFormatter())
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # 如果是 GUI 模式，添加 GUI handler
    if gui_config and gui_config.get('gui_mode', False):
        text_widget = gui_config.get('text_widget')
        if text_widget:
            from .formatter import GUILogHandler
            gui_handler = GUILogHandler(text_widget)
            gui_handler.setLevel(level.value)
            logger.addHandler(gui_handler)

    return logger
