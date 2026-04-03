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
    show_colors: bool = True            # 启用颜色
    show_tags: bool = True              # 显示标签
    max_lines: int = 1000               # GUI 最大显示行数
    enable_gui: bool = True             # 启用 GUI 日志
    enable_console: bool = True         # 启用控制台日志
    enable_file: bool = False           # 启用文件日志
    file_path: Optional[str] = None     # 日志文件路径
    file_level: LogLevel = LogLevel.DEBUG  # 文件日志级别
    tag_filter: Optional[List[LogTag]] = None  # 标签过滤器 (None=显示所有)


class ColorFormatter(logging.Formatter):
    """彩色日志格式化器"""
    grey = "\x1b[38;21m"
    blue = "\x1b[34;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;21m"
    cyan = "\x1b[36;21m"
    magenta = "\x1b[35;21m"
    orange = "\x1b[38;5;208m"
    reset = "\x1b[0m"
    
    # 标签颜色和图标映射
    TAG_ICONS = {
        LogTag.CRITICAL: "💀",
        LogTag.ERROR: "❌",
        LogTag.WARNING: "⚠️",
        LogTag.IMPORTANT: "⭐",
        LogTag.PROGRESS: "📊",
        LogTag.NORMAL: "ℹ️",
        LogTag.DEBUG: "🔍",
        LogTag.TRACE: "📝",
    }
    
    TAG_COLORS = {
        LogTag.CRITICAL: bold_red,
        LogTag.ERROR: red,
        LogTag.WARNING: yellow,
        LogTag.IMPORTANT: orange,
        LogTag.PROGRESS: cyan,
        LogTag.NORMAL: green,
        LogTag.DEBUG: blue,
        LogTag.TRACE: grey,
    }
    
    def __init__(self, config: LogConfig):
        super().__init__()
        self.config = config
        
        # 根据配置构建格式字符串
        format_parts = []
        if config.show_timestamp:
            format_parts.append("%(asctime)s")
        if config.show_module:
            format_parts.append("%(name)s")
        format_parts.append("%(levelname)s")
        if config.show_tags:
            format_parts.append("%(tag_icon)s")
        format_parts.append("%(message)s")
        
        format_str = " - ".join(format_parts)
        
        # 定义各级别颜色格式
        self.FORMATS = {
            logging.DEBUG: self.grey + format_str + self.reset,
            logging.INFO: self.green + format_str + self.reset,
            logging.WARNING: self.yellow + format_str + self.reset,
            logging.ERROR: self.red + format_str + self.reset,
            logging.CRITICAL: self.bold_red + format_str + self.reset
        }
    
    def format(self, record):
        # 获取或计算标签
        tag = getattr(record, 'tag', LogTag.NORMAL)
        record.tag_icon = self.TAG_ICONS.get(tag, "")
        
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


class PlainFormatter(logging.Formatter):
    """无格式日志格式化器 (用于文件输出)"""
    def __init__(self, config: LogConfig):
        super().__init__()
        self.config = config
        
        format_parts = []
        if config.show_timestamp:
            format_parts.append("%(asctime)s")
        if config.show_module:
            format_parts.append("%(name)s")
        format_parts.append("%(levelname)s")
        if config.show_tags:
            format_parts.append("%(tag_icon)s")
        format_parts.append("%(message)s")
        
        self.format_str = " - ".join(format_parts)
    
    def format(self, record):
        # 获取或计算标签
        tag = getattr(record, 'tag', LogTag.NORMAL)
        record.tag_icon = tag.name
        formatter = logging.Formatter(self.format_str, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class GUILogHandler(logging.Handler):
    """GUI 文本控件日志处理器"""
    def __init__(self, text_widget, config: LogConfig):
        super().__init__()
        self.text_widget = text_widget
        self.config = config
        self.line_count = 0
        
        # 添加标签过滤器
        self.addFilter(TagFilter(config))
    
    def emit(self, record):
        msg = self.format(record)
        
        def append():
            self.text_widget.configure(state='normal')
            
            # 检查是否超过最大行数
            if self.line_count >= self.config.max_lines:
                # 删除第一行
                self.text_widget.delete('1.0', '2.0')
                self.line_count -= 1
            
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
            self.line_count += 1
        
        self.text_widget.after(0, append)


class TagFilter(logging.Filter):
    """日志标签过滤器"""
    def __init__(self, config: LogConfig):
        super().__init__()
        self.config = config
    
    def filter(self, record):
        # 如果没有设置 tag，根据当前粒度的日志级别判断
        if not hasattr(record, 'tag'):
            # 获取处理器的级别
            handler_level = getattr(record, 'handler_level', logging.NOTSET)
            
            # 如果记录级别 >= 处理器级别，允许通过
            if record.levelno >= handler_level:
                return True
            return False
        
        tag = record.tag
        
        # 如果设置了标签过滤器，只允许指定的标签通过
        if self.config.tag_filter is not None:
            return tag in self.config.tag_filter
        
        # 否则根据最小标签级别过滤
        return tag.value >= self.config.min_tag.value


class LogManager:
    """日志管理器单例"""
    _instance = None
    _logger = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, config: Optional[LogConfig] = None):
        """初始化日志系统"""
        if config is None:
            config = LogConfig()
        
        self._config = config
        self._logger = logging.getLogger()
        
        # 设置日志级别
        self._logger.setLevel(config.level.value)
        
        # 清除现有处理器
        if self._logger.handlers:
            self._logger.handlers.clear()
        
        # 添加控制台处理器
        if config.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(config.level.value)
            
            if config.show_colors:
                console_handler.setFormatter(ColorFormatter(config))
            else:
                console_handler.setFormatter(PlainFormatter(config))
            
            self._logger.addHandler(console_handler)
        
        # 添加文件处理器 (如果启用)
        if config.enable_file and config.file_path:
            try:
                file_handler = logging.FileHandler(config.file_path, encoding='utf-8')
                file_handler.setLevel(config.file_level.value)
                file_handler.setFormatter(PlainFormatter(config))
                self._logger.addHandler(file_handler)
            except Exception as e:
                print(f"Failed to create file log handler: {e}")
        
        return self._logger
    
    def add_gui_handler(self, text_widget):
        """添加 GUI 日志处理器"""
        if not self._config or not self._config.enable_gui:
            return
        
        gui_handler = GUILogHandler(text_widget, self._config)
        gui_handler.setLevel(self._config.level.value)
        gui_handler.setFormatter(ColorFormatter(self._config))
        
        if self._logger:
            self._logger.addHandler(gui_handler)
    
    def set_granularity(self, granularity: LogGranularity):
        """动态设置日志粒度"""
        if not self._config or not self._logger:
            return
        
        self._config.granularity = granularity
        
        # 根据粒度调整日志级别
        if granularity == LogGranularity.MINIMAL:
            self._logger.setLevel(logging.ERROR)
            for handler in self._logger.handlers:
                handler.setLevel(logging.ERROR)
                # 清除旧的过滤器，添加新的
                handler.filters = [f for f in handler.filters if not isinstance(f, TagFilter)]
                handler.addFilter(TagFilter(self._config))
        elif granularity == LogGranularity.BASIC:
            self._logger.setLevel(logging.WARNING)
            for handler in self._logger.handlers:
                handler.setLevel(logging.WARNING)
                # 清除旧的过滤器，添加新的
                handler.filters = [f for f in handler.filters if not isinstance(f, TagFilter)]
                handler.addFilter(TagFilter(self._config))
        elif granularity == LogGranularity.NORMAL:
            self._logger.setLevel(logging.INFO)
            for handler in self._logger.handlers:
                handler.setLevel(logging.INFO)
                # 清除旧的过滤器，添加新的
                handler.filters = [f for f in handler.filters if not isinstance(f, TagFilter)]
                handler.addFilter(TagFilter(self._config))
        elif granularity in [LogGranularity.DETAILED, LogGranularity.VERBOSE]:
            self._logger.setLevel(logging.DEBUG)
            for handler in self._logger.handlers:
                handler.setLevel(logging.DEBUG)
                # 清除旧的过滤器，添加新的
                handler.filters = [f for f in handler.filters if not isinstance(f, TagFilter)]
                handler.addFilter(TagFilter(self._config))
    
    def set_level(self, level: LogLevel):
        """动态设置日志级别"""
        if not self._config or not self._logger:
            return
        
        self._config.level = level
        self._logger.setLevel(level.value)
        for handler in self._logger.handlers:
            handler.setLevel(level.value)
    
    def set_min_tag(self, tag: LogTag):
        """动态设置最小标签级别"""
        if not self._config:
            return
        
        self._config.min_tag = tag
        # 更新所有处理器的过滤器
        for handler in self._logger.handlers:
            handler.filters = [f for f in handler.filters if not isinstance(f, TagFilter)]
            handler.addFilter(TagFilter(self._config))
    
    def set_tag_filter(self, tags: List[LogTag]):
        """设置标签过滤器 (只允许指定的标签)"""
        if not self._config:
            return
        
        self._config.tag_filter = tags
        # 更新所有处理器的过滤器
        for handler in self._logger.handlers:
            handler.filters = [f for f in handler.filters if not isinstance(f, TagFilter)]
            handler.addFilter(TagFilter(self._config))
    
    def clear_tag_filter(self):
        """清除标签过滤器"""
        if not self._config:
            return
        
        self._config.tag_filter = None
        self._config.min_tag = LogTag.NORMAL
        # 更新所有处理器的过滤器
        for handler in self._logger.handlers:
            handler.filters = [f for f in handler.filters if not isinstance(f, TagFilter)]
            handler.addFilter(TagFilter(self._config))
    
    def get_config(self) -> Optional[LogConfig]:
        """获取当前日志配置"""
        return self._config
    
    def get_logger(self) -> Optional[logging.Logger]:
        """获取日志记录器"""
        return self._logger


# 便捷函数
def log_with_tag(message: str, level: LogLevel = LogLevel.INFO, tag: LogTag = LogTag.NORMAL, **kwargs):
    """
    带标签的日志记录函数
    
    Args:
        message: 日志消息
        level: 日志级别
        tag: 日志标签
        **kwargs: 其他参数传递给 logger
    """
    logger = get_logger()
    if logger is None:
        return
    
    # 创建自定义 record 并添加 tag 属性
    extra = kwargs.get('extra', {})
    extra['tag'] = tag
    kwargs['extra'] = extra
    
    logger.log(level.value, message, **kwargs)


def setup_logger(gui_handler=None, config: Optional[LogConfig] = None):
    """
    设置日志记录器 (兼容旧接口)
    
    Args:
        gui_handler: 可选的 GUI 日志处理器
        config: 可选的日志配置
        
    Returns:
        配置好的 logger 实例
    """
    manager = LogManager.get_instance()
    logger = manager.initialize(config)
    
    # 如果提供了 gui_handler,添加它
    if gui_handler and (not config or config.enable_gui):
        manager.add_gui_handler(gui_handler.text_widget if hasattr(gui_handler, 'text_widget') else gui_handler)
    
    return logger


def get_logger():
    """获取全局 logger 实例"""
    manager = LogManager.get_instance()
    logger = manager.get_logger()
    if logger is None:
        # 如果未初始化，使用默认配置初始化
        return setup_logger()
    return logger


def set_log_granularity(granularity: LogGranularity):
    """动态设置日志粒度"""
    manager = LogManager.get_instance()
    manager.set_granularity(granularity)


def set_log_level(level: LogLevel):
    """动态设置日志级别"""
    manager = LogManager.get_instance()
    manager.set_level(level)


def get_log_config() -> Optional[LogConfig]:
    """获取当前日志配置"""
    manager = LogManager.get_instance()
    return manager.get_config()


# 全局单例
_log_manager: Optional[LogManager] = None


def get_log_manager() -> LogManager:
    """获取日志管理器单例"""
    return LogManager.get_instance()
