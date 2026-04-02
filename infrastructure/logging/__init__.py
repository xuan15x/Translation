"""
统一日志模块
整合 log_config, logging_config, log_slice 的功能
提供统一的日志配置、格式化和处理器
"""

from .config import (
    LogLevel,
    LogGranularity,
    LogTag,
    LogConfig,
    setup_logger,
    get_log_level_for_granularity,
    get_min_tag_for_granularity
)

from .formatter import (
    ColorFormatter,
    GUILogHandler,
    GUILogController
)

from .slice import (
    LogCategory,
    LogContext,
    LoggerSlice,
    ModuleLoggerMixin,
    log_with_tag,
    log_exception
)

__all__ = [
    # 配置相关
    'LogLevel',
    'LogGranularity',
    'LogTag',
    'LogConfig',
    'setup_logger',
    'get_log_level_for_granularity',
    'get_min_tag_for_granularity',
    
    # 格式化相关
    'ColorFormatter',
    'GUILogHandler',
    'GUILogController',
    
    # 切片相关
    'LogCategory',
    'LogContext',
    'LoggerSlice',
    'ModuleLoggerMixin',
    'log_with_tag',
    'log_exception',
]
