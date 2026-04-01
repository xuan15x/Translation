"""
异常处理模块
定义全项目统一的异常体系和错误处理标准
"""
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorCategory(Enum):
    """错误分类"""
    # API 相关错误
    API_ERROR = "api_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    
    # 配置相关错误
    CONFIG_ERROR = "config_error"
    VALIDATION_ERROR = "validation_error"
    
    # 文件操作错误
    FILE_ERROR = "file_error"
    FILE_NOT_FOUND_ERROR = "file_not_found_error"
    IO_ERROR = "io_error"
    
    # 数据处理错误
    DATA_ERROR = "data_error"
    PARSING_ERROR = "parsing_error"
    
    # 业务逻辑错误
    TRANSLATION_ERROR = "translation_error"
    TERMINOLOGY_ERROR = "terminology_error"
    WORKFLOW_ERROR = "workflow_error"
    
    # 系统错误
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"


class TranslationBaseError(Exception):
    """翻译系统基础异常类 - 所有自定义异常的基类"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        初始化异常
        
        Args:
            message: 错误消息
            category: 错误分类
            error_code: 错误代码（可选）
            details: 详细错误信息（可选）
            original_exception: 原始异常（用于包装其他异常）
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.error_code = error_code or f"{category.value.upper()}_001"
        self.details = details or {}
        self.original_exception = original_exception
        
        # 生成完整的错误报告
        self.error_report = self._generate_error_report()
    
    def _generate_error_report(self) -> Dict[str, Any]:
        """生成错误报告"""
        report = {
            'error_code': self.error_code,
            'category': self.category.value,
            'message': self.message,
            'details': self.details,
        }
        
        if self.original_exception:
            report['original_exception'] = {
                'type': type(self.original_exception).__name__,
                'message': str(self.original_exception)
            }
        
        return report
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.error_report
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"[{self.error_code}] {self.message}"
    
    def __repr__(self) -> str:
        """详细信息"""
        return f"{self.__class__.__name__}(code={self.error_code}, category={self.category.value})"


# ========== API 相关异常 ==========

class APIError(TranslationBaseError):
    """API 调用失败"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.API_ERROR, **kwargs)
        self.error_code = kwargs.get('error_code', 'API_001')


class RateLimitError(APIError):
    """API 速率限制"""
    
    def __init__(self, message: str = "API 请求频率超限", **kwargs):
        super().__init__(message, error_code='API_002', **kwargs)
        self.category = ErrorCategory.RATE_LIMIT_ERROR


class APITimeoutError(APIError):
    """API 超时"""
    
    def __init__(self, message: str = "API 请求超时", **kwargs):
        super().__init__(message, error_code='API_003', **kwargs)
        self.category = ErrorCategory.TIMEOUT_ERROR


class AuthenticationError(APIError):
    """认证失败"""
    
    def __init__(self, message: str = "API 认证失败", **kwargs):
        super().__init__(message, error_code='API_004', **kwargs)
        self.category = ErrorCategory.AUTHENTICATION_ERROR


# ========== 配置相关异常 ==========

class ConfigError(TranslationBaseError):
    """配置错误"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.CONFIG_ERROR, **kwargs)
        self.error_code = kwargs.get('error_code', 'CFG_001')


class ValidationError(ConfigError):
    """验证失败"""
    
    def __init__(self, message: str, field_name: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if field_name:
            details['field'] = field_name
        
        super().__init__(message, details=details, error_code='CFG_002', **kwargs)
        self.category = ErrorCategory.VALIDATION_ERROR


# ========== 文件操作异常 ==========

class FileError(TranslationBaseError):
    """文件操作失败"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if file_path:
            details['file_path'] = file_path
        
        super().__init__(message, details=details, category=ErrorCategory.FILE_ERROR, **kwargs)
        self.error_code = kwargs.get('error_code', 'FILE_001')


class FileNotFoundError(FileError):
    """文件未找到"""
    
    def __init__(self, message: str = "文件不存在", file_path: Optional[str] = None, **kwargs):
        super().__init__(message, file_path=file_path, error_code='FILE_002', **kwargs)
        self.category = ErrorCategory.FILE_NOT_FOUND_ERROR


class IOError(FileError):
    """IO 操作失败"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(message, file_path=file_path, error_code='FILE_003', **kwargs)
        self.category = ErrorCategory.IO_ERROR


# ========== 数据处理异常 ==========

class DataError(TranslationBaseError):
    """数据处理失败"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.DATA_ERROR, **kwargs)
        self.error_code = kwargs.get('error_code', 'DATA_001')


class ParsingError(DataError):
    """数据解析失败"""
    
    def __init__(self, message: str, data_format: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if data_format:
            details['format'] = data_format
        
        super().__init__(message, details=details, error_code='DATA_002', **kwargs)
        self.category = ErrorCategory.PARSING_ERROR


# ========== 业务逻辑异常 ==========

class TranslationError(TranslationBaseError):
    """翻译过程错误"""
    
    def __init__(self, message: str, task_id: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if task_id:
            details['task_id'] = task_id
        
        super().__init__(message, details=details, category=ErrorCategory.TRANSLATION_ERROR, **kwargs)
        self.error_code = kwargs.get('error_code', 'TRANS_001')


class TerminologyError(TranslationBaseError):
    """术语库操作失败"""
    
    def __init__(self, message: str, term_path: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if term_path:
            details['term_path'] = term_path
        
        super().__init__(message, details=details, category=ErrorCategory.TERMINOLOGY_ERROR, **kwargs)
        self.error_code = kwargs.get('error_code', 'TERM_001')


class WorkflowError(TranslationBaseError):
    """工作流执行失败"""
    
    def __init__(self, message: str, stage: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if stage:
            details['stage'] = stage
        
        super().__init__(message, details=details, category=ErrorCategory.WORKFLOW_ERROR, **kwargs)
        self.error_code = kwargs.get('error_code', 'FLOW_001')


# ========== 系统异常 ==========

class SystemError(TranslationBaseError):
    """系统级错误"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.SYSTEM_ERROR, **kwargs)
        self.error_code = kwargs.get('error_code', 'SYS_001')


class NetworkError(TranslationBaseError):
    """网络错误"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.NETWORK_ERROR, **kwargs)
        self.error_code = kwargs.get('error_code', 'NET_001')


# ========== 错误处理器 ==========

class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> TranslationBaseError:
        """
        处理异常，转换为统一的异常类型
        
        Args:
            error: 原始异常
            context: 上下文信息
            
        Returns:
            标准化后的异常对象
        """
        # 如果已经是标准异常，直接返回
        if isinstance(error, TranslationBaseError):
            if context:
                error.details.update(context)
            return error
        
        # 映射常见异常到标准异常
        error_mapping = {
            FileNotFoundError: lambda e: FileNotFoundError(str(e)),
            IOError: lambda e: IOError(str(e)),
            ValueError: lambda e: ValidationError(str(e)),
            KeyError: lambda e: DataError(f"键错误：{e}"),
            TypeError: lambda e: DataError(f"类型错误：{e}"),
            TimeoutError: lambda e: APITimeoutError(str(e)),
        }
        
        error_type = type(error)
        handler = error_mapping.get(error_type)
        
        if handler:
            standardized = handler(error)
            standardized.original_exception = error
            if context:
                standardized.details.update(context)
            return standardized
        
        # 未知异常包装为 SystemError
        system_error = SystemError(
            message=f"未知错误：{str(error)}",
            original_exception=error,
            details={'exception_type': error_type.__name__, **(context or {})}
        )
        return system_error
    
    @staticmethod
    def log_error(error: TranslationBaseError, logger: Any) -> None:
        """
        记录错误日志
        
        Args:
            error: 异常对象
            logger: 日志记录器
        """
        log_message = (
            f"❌ 错误 [{error.error_code}] | "
            f"分类：{error.category.value} | "
            f"消息：{error.message}"
        )
        
        if error.details:
            log_message += f" | 详情：{error.details}"
        
        if error.original_exception:
            log_message += f" | 原始异常：{type(error.original_exception).__name__}: {error.original_exception}"
        
        # 根据错误级别选择日志级别
        if error.category in [ErrorCategory.SYSTEM_ERROR, ErrorCategory.UNKNOWN_ERROR]:
            logger.error(log_message, exc_info=True)
        elif error.category in [ErrorCategory.API_ERROR, ErrorCategory.NETWORK_ERROR]:
            logger.warning(log_message)
        else:
            logger.error(log_message)
    
    @staticmethod
    def get_user_friendly_message(error: TranslationBaseError) -> str:
        """
        获取用户友好的错误消息
        
        Args:
            error: 异常对象
            
        Returns:
            用户友好的消息文本
        """
        user_messages = {
            ErrorCategory.API_ERROR: "API 调用失败，请检查网络连接或稍后重试",
            ErrorCategory.RATE_LIMIT_ERROR: "请求过于频繁，请稍后再试",
            ErrorCategory.TIMEOUT_ERROR: "请求超时，请检查网络或重试",
            ErrorCategory.AUTHENTICATION_ERROR: "认证失败，请检查 API 密钥配置",
            ErrorCategory.CONFIG_ERROR: "配置错误，请检查配置文件",
            ErrorCategory.VALIDATION_ERROR: "参数验证失败，请检查输入",
            ErrorCategory.FILE_ERROR: "文件操作失败",
            ErrorCategory.FILE_NOT_FOUND_ERROR: "文件不存在，请检查路径",
            ErrorCategory.IO_ERROR: "读写文件失败",
            ErrorCategory.DATA_ERROR: "数据处理失败",
            ErrorCategory.PARSING_ERROR: "数据格式解析失败",
            ErrorCategory.TRANSLATION_ERROR: "翻译过程出错",
            ErrorCategory.TERMINOLOGY_ERROR: "术语库操作失败",
            ErrorCategory.WORKFLOW_ERROR: "工作流执行失败",
            ErrorCategory.SYSTEM_ERROR: "系统错误，请联系管理员",
            ErrorCategory.NETWORK_ERROR: "网络错误，请检查连接",
            ErrorCategory.UNKNOWN_ERROR: "未知错误，请稍后重试",
        }
        
        base_message = user_messages.get(error.category, "发生错误")
        
        # 添加具体错误信息
        if error.message:
            return f"{base_message}：{error.message}"
        
        return base_message


# ========== 便捷函数 ==========

def raise_error(
    message: str,
    category: ErrorCategory,
    error_code: str,
    **kwargs
) -> None:
    """
    抛出指定类型的异常
    
    Args:
        message: 错误消息
        category: 错误分类
        error_code: 错误代码
        **kwargs: 其他参数
    """
    error_class_map = {
        ErrorCategory.API_ERROR: APIError,
        ErrorCategory.RATE_LIMIT_ERROR: RateLimitError,
        ErrorCategory.TIMEOUT_ERROR: APITimeoutError,
        ErrorCategory.AUTHENTICATION_ERROR: AuthenticationError,
        ErrorCategory.CONFIG_ERROR: ConfigError,
        ErrorCategory.VALIDATION_ERROR: ValidationError,
        ErrorCategory.FILE_ERROR: FileError,
        ErrorCategory.FILE_NOT_FOUND_ERROR: FileNotFoundError,
        ErrorCategory.IO_ERROR: IOError,
        ErrorCategory.DATA_ERROR: DataError,
        ErrorCategory.PARSING_ERROR: ParsingError,
        ErrorCategory.TRANSLATION_ERROR: TranslationError,
        ErrorCategory.TERMINOLOGY_ERROR: TerminologyError,
        ErrorCategory.WORKFLOW_ERROR: WorkflowError,
        ErrorCategory.SYSTEM_ERROR: SystemError,
        ErrorCategory.NETWORK_ERROR: NetworkError,
        ErrorCategory.UNKNOWN_ERROR: TranslationBaseError,
    }
    
    error_class = error_class_map.get(category, TranslationBaseError)
    raise error_class(message, category=category, error_code=error_code, **kwargs)


def safe_execute(func, *args, default=None, **kwargs):
    """
    安全执行函数，捕获并处理所有异常
    
    Args:
        func: 要执行的函数
        *args: 位置参数
        default: 默认返回值（发生异常时）
        **kwargs: 关键字参数
        
    Returns:
        函数执行结果或默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error = ErrorHandler.handle_error(e)
        # 这里可以添加日志记录
        return default


__all__ = [
    # 枚举
    'ErrorCategory',
    
    # 基础异常
    'TranslationBaseError',
    
    # API 异常
    'APIError',
    'RateLimitError',
    'APITimeoutError',
    'AuthenticationError',
    
    # 配置异常
    'ConfigError',
    'ValidationError',
    
    # 文件异常
    'FileError',
    'FileNotFoundError',
    'IOError',
    
    # 数据异常
    'DataError',
    'ParsingError',
    
    # 业务异常
    'TranslationError',
    'TerminologyError',
    'WorkflowError',
    
    # 系统异常
    'SystemError',
    'NetworkError',
    
    # 处理器
    'ErrorHandler',
    
    # 便捷函数
    'raise_error',
    'safe_execute',
]
