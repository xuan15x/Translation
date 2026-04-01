"""
抽象日志切片层
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
    抽象日志切片基类
    为各个模块提供统一的日志记录切面
    """
    
    def __init__(self, category: LogCategory, logger: Optional[logging.Logger] = None):
        """
        初始化日志切片
        
        Args:
            category: 日志类别
            logger: 日志记录器，默认使用 root logger
        """
        self.category = category
        self.logger = logger or logging.getLogger()
        self._execution_times = []
    
    def log(self, level: LogLevel, message: str, context: Optional[LogContext] = None, **kwargs):
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
            context: 日志上下文
            **kwargs: 额外参数
        """
        if context:
            full_message = f"[{self.category.value}] {message}"
            if context.execution_time > 0:
                full_message += f" (耗时：{context.execution_time:.4f}s)"
        else:
            full_message = f"[{self.category.value}] {message}"
        
        # 添加额外上下文信息
        if kwargs:
            extra_parts = [f"{k}={v}" for k, v in kwargs.items()]
            full_message += f" | {', '.join(extra_parts)}"
        
        # 记录日志
        self.logger.log(level.value, full_message)
    
    def debug(self, message: str, **kwargs):
        """DEBUG 级别日志"""
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """INFO 级别日志"""
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """WARNING 级别日志"""
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """ERROR 级别日志"""
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """CRITICAL 级别日志"""
        self.log(LogLevel.CRITICAL, message, **kwargs)
    
    def create_context(self, func_name: str, params: Optional[Dict] = None) -> LogContext:
        """
        创建日志上下文
        
        Args:
            func_name: 函数名
            params: 函数参数
            
        Returns:
            LogContext 实例
        """
        return LogContext(
            module_name=self.__class__.__name__,
            function_name=func_name,
            category=self.category,
            parameters=params or {}
        )
    
    def log_entry(self, func_name: str, params: Dict[str, Any]):
        """记录函数入口日志"""
        params_str = ', '.join(f"{k}={v}" for k, v in params.items())
        self.debug(f">>> 进入 {func_name}({params_str})")
    
    def log_exit(self, func_name: str, result: Any, execution_time: float):
        """记录函数出口日志"""
        self.debug(f"<<< 离开 {func_name}, 结果={result}, 耗时={execution_time:.4f}s")
    
    def log_error(self, func_name: str, error: Exception):
        """记录错误日志"""
        self.error(f"!!! {func_name} 发生错误：{str(error)}", exc_info=True)
    
    def record_execution_time(self, execution_time: float):
        """记录执行时间"""
        self._execution_times.append(execution_time)
    
    def get_average_execution_time(self) -> float:
        """获取平均执行时间"""
        if not self._execution_times:
            return 0.0
        return sum(self._execution_times) / len(self._execution_times)
    
    def clear_execution_times(self):
        """清空执行时间记录"""
        self._execution_times.clear()


def log_slice(category: LogCategory, 
              entry_level: LogLevel = LogLevel.DEBUG,
              exit_level: LogLevel = LogLevel.DEBUG,
              error_level: LogLevel = LogLevel.ERROR,
              log_params: bool = True,
              log_result: bool = False,
              log_execution_time: bool = True):
    """
    日志切片装饰器
    
    Args:
        category: 日志类别
        entry_level: 入口日志级别
        exit_level: 出口日志级别
        error_level: 错误日志级别
        log_params: 是否记录参数
        log_result: 是否记录返回值
        log_execution_time: 是否记录执行时间
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取 logger slice
            logger_slice = LoggerSlice(category)
            
            # 获取函数信息
            func_name = func.__name__
            module_name = func.__module__
            
            # 准备参数信息
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 记录入口日志
            if log_params:
                params_dict = dict(bound_args.arguments)
                # 移除 self/cls 参数
                if 'self' in params_dict:
                    del params_dict['self']
                if 'cls' in params_dict:
                    del params_dict['cls']
                logger_slice.log_entry(func_name, params_dict)
            else:
                logger_slice.log_entry(func_name, {})
            
            # 记录开始时间
            start_time = time.time()
            
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                execution_time = time.time() - start_time
                
                # 记录出口日志
                if log_result:
                    logger_slice.log_exit(func_name, result, execution_time)
                elif log_execution_time:
                    logger_slice.debug(f"<<< 离开 {func_name}, 耗时={execution_time:.4f}s")
                else:
                    logger_slice.debug(f"<<< 离开 {func_name}")
                
                # 记录执行时间
                if log_execution_time:
                    logger_slice.record_execution_time(execution_time)
                
                return result
                
            except Exception as e:
                # 计算执行时间
                execution_time = time.time() - start_time
                
                # 记录错误日志
                logger_slice.log_error(func_name, e)
                
                # 重新抛出异常
                raise
        
        return wrapper
    return decorator


class ModuleLoggerMixin:
    """
    模块日志混合类
    为各个模块提供便捷的日志切片支持
    """
    
    LOG_CATEGORY: LogCategory = LogCategory.GENERAL
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger_slice = LoggerSlice(self.LOG_CATEGORY)
    
    @property
    def logger(self) -> LoggerSlice:
        """获取日志切片实例"""
        return self._logger_slice
    
    def log_debug(self, message: str, **kwargs):
        """记录 DEBUG 日志"""
        self._logger_slice.debug(message, **kwargs)
    
    def log_info(self, message: str, **kwargs):
        """记录 INFO 日志"""
        self._logger_slice.info(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """记录 WARNING 日志"""
        self._logger_slice.warning(message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """记录 ERROR 日志"""
        self._logger_slice.error(message, **kwargs)
    
    def log_critical(self, message: str, **kwargs):
        """记录 CRITICAL 日志"""
        self._logger_slice.critical(message, **kwargs)


# 便捷函数
def create_logger_slice(category: LogCategory, name: Optional[str] = None) -> LoggerSlice:
    """
    创建日志切片实例
    
    Args:
        category: 日志类别
        name: 日志器名称
        
    Returns:
        LoggerSlice 实例
    """
    logger = logging.getLogger(name) if name else None
    return LoggerSlice(category, logger)


def get_category_by_module(module_name: str) -> LogCategory:
    """
    根据模块名获取日志类别
    
    Args:
        module_name: 模块名称
        
    Returns:
        对应的 LogCategory
    """
    module_to_category = {
        'models': LogCategory.MODEL,
        'prompt_builder': LogCategory.PROMPT,
        'fuzzy_matcher': LogCategory.MATCHER,
        'concurrency_controller': LogCategory.CONCURRENCY,
        'terminology_manager': LogCategory.TERMINOLOGY,
        'api_stages': LogCategory.API,
        'workflow_orchestrator': LogCategory.WORKFLOW,
        'gui_app': LogCategory.GUI,
    }
    
    # 提取模块名（去除路径）
    base_name = module_name.split('.')[-1].split('/')[-1]
    
    return module_to_category.get(base_name, LogCategory.GENERAL)
