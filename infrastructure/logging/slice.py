"""
日志切片模块
为各个功能模块提供统一的日志切面编程支持
基于 AOP (Aspect-Oriented Programming) 思想实现
"""
import logging
import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar
from dataclasses import dataclass, field
from enum import Enum
import inspect


class LogCategory(Enum):
    """日志类别枚举"""
    MODEL = "MODEL"
    PROMPT = "PROMPT"
    MATCHER = "MATCHER"
    CONCURRENCY = "CONCURRENCY"
    TERMINOLOGY = "TERMINOLOGY"
    API = "API"
    WORKFLOW = "WORKFLOW"
    GUI = "GUI"
    GENERAL = "GENERAL"


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogContext:
    """日志上下文信息"""
    module_name: str
    function_name: str
    category: LogCategory
    level: LogLevel = LogLevel.INFO
    execution_time: float = 0.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: Optional[Exception] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)


class LoggerSlice:
    """
    日志切片类
    为模块提供统一的日志记录功能
    """
    
    def __init__(self, category: LogCategory = LogCategory.GENERAL):
        """
        初始化日志切片

        Args:
            category: 日志类别
        """
        self.category = category
        self.logger = logging.getLogger(f"slice.{category.value}")
    
    def log(self, level: LogLevel, message: str, **kwargs):
        """
        记录日志

        Args:
            level: 日志级别
            message: 日志消息
            **kwargs: 额外数据
        """
        log_method = getattr(self.logger, level.name.lower(), self.logger.info)
        log_method(f"{message} | {kwargs}")
    
    def log_debug(self, message: str, **kwargs):
        """记录 DEBUG 日志"""
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def log_info(self, message: str, **kwargs):
        """记录 INFO 日志"""
        self.log(LogLevel.INFO, message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """记录 WARNING 日志"""
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """记录 ERROR 日志"""
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def log_critical(self, message: str, **kwargs):
        """记录 CRITICAL 日志"""
        self.log(LogLevel.CRITICAL, message, **kwargs)
    
    def log_exception(self, message: str, exc: Exception, **kwargs):
        """
        记录异常日志

        Args:
            message: 日志消息
            exc: 异常对象
            **kwargs: 额外数据
        """
        self.logger.exception(f"{message} | {kwargs} | Exception: {exc}")
    
    def create_context(self, func_name: str) -> LogContext:
        """
        创建日志上下文

        Args:
            func_name: 函数名

        Returns:
            日志上下文对象
        """
        return LogContext(
            module_name=self.logger.name,
            function_name=func_name,
            category=self.category
        )


# 类型变量
F = TypeVar('F', bound=Callable)


def log_with_tag(tag: str = "NORMAL"):
    """
    带标签的日志装饰器

    Args:
        tag: 日志标签

    Returns:
        装饰器函数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"tag.{tag}")
            logger.info(f"Executing {func.__name__}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"Completed {func.__name__} in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.exception(f"Failed {func.__name__} after {elapsed:.3f}s: {e}")
                raise
        
        return wrapper  # type: ignore
    return decorator


def log_exception(logger: logging.Logger):
    """
    异常日志装饰器

    Args:
        logger: 日志器对象

    Returns:
        装饰器函数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Exception in {func.__name__}: {e}")
                raise
        
        return wrapper  # type: ignore
    return decorator


class ModuleLoggerMixin:
    """
    模块日志混入类
    为类提供统一的日志功能
    """
    
    LOG_CATEGORY: LogCategory = LogCategory.GENERAL
    _logger_slice: Optional[LoggerSlice] = None
    
    @property
    def logger(self) -> LoggerSlice:
        """获取日志切片对象"""
        if self._logger_slice is None:
            self._logger_slice = LoggerSlice(self.LOG_CATEGORY)
        return self._logger_slice
    
    def log_debug(self, message: str, **kwargs):
        """记录 DEBUG 日志"""
        self.logger.log_debug(message, **kwargs)
    
    def log_info(self, message: str, **kwargs):
        """记录 INFO 日志"""
        self.logger.log_info(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """记录 WARNING 日志"""
        self.logger.log_warning(message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """记录 ERROR 日志"""
        self.logger.log_error(message, **kwargs)
    
    def log_critical(self, message: str, **kwargs):
        """记录 CRITICAL 日志"""
        self.logger.log_critical(message, **kwargs)
    
    def log_exception(self, message: str, exc: Exception, **kwargs):
        """记录异常日志"""
        self.logger.log_exception(message, exc, **kwargs)
