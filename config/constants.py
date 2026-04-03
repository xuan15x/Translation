"""
常量配置模块
集中管理所有魔法数字和常量配置
"""

# ========== API 调用配置 ==========
class APIConfig:
    """API 调用相关常量"""
    DEFAULT_MAX_TOKENS = 512
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_TOP_P = 0.8
    DEFAULT_TIMEOUT = 60
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 3.0
    RESPONSE_FORMAT_TYPE = "json_object"
    
    # 退避系数
    EXPONENTIAL_BACKOFF_FACTOR = 2
    
    # 错误率阈值
    HIGH_ERROR_RATE_THRESHOLD = 0.3  # 30%


# ========== 并发控制配置 ==========
class ConcurrencyConfig:
    """并发控制相关常量"""
    DEFAULT_INITIAL_CONCURRENCY = 8
    DEFAULT_MAX_CONCURRENCY = 10
    DEFAULT_COOLDOWN_SECONDS = 5.0
    DEFAULT_RETRY_STREAK_THRESHOLD = 3

    # 延迟阈值（毫秒）
    HIGH_LATENCY_THRESHOLD_MS = 2000

    # 调整频率限制（秒）
    ADJUST_INTERVAL_SECONDS = 2

    # 并发调整超时（秒）
    ADJUST_TIMEOUT_SECONDS = 2.0

    # 最大延迟样本数
    MAX_LATENCY_SAMPLES = 20

    # 错误率阈值（从 APIConfig 复制，避免循环引用）
    HIGH_ERROR_RATE_THRESHOLD = 0.3  # 30%


# ========== 缓存配置 ==========
class CacheConfig:
    """缓存相关常量"""
    DEFAULT_MAX_MEMORY_MB = 100
    DEFAULT_CACHE_CAPACITY = 2000
    DEFAULT_CACHE_TTL_SECONDS = 3600
    DEFAULT_POOL_SIZE = 5


# ========== 术语库配置 ==========
class TerminologyConfig:
    """术语库相关常量"""
    DEFAULT_SIMILARITY_LOW = 60  # 模糊匹配阈值
    DEFAULT_EXACT_MATCH_SCORE = 100  # 精确匹配置信度
    DEFAULT_MULTIPROCESS_THRESHOLD = 1000  # 多进程阈值


# ========== 工作流配置 ==========
class WorkflowConfig:
    """工作流相关常量"""
    DEFAULT_BATCH_SIZE = 1000
    DEFAULT_GC_INTERVAL = 2
    DEFAULT_ENABLE_TWO_PASS = True
    DEFAULT_SKIP_REVIEW_IF_LOCAL_HIT = True


# ========== 日志配置 ==========
class LogConfig:
    """日志相关常量"""
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_LOG_GRANULARITY = "normal"
    DEFAULT_LOG_MAX_LINES = 1000
    DEFAULT_LOG_MAX_SIZE_MB = 10


# ========== GUI 配置 ==========
class GUIConfig:
    """GUI 相关常量"""
    DEFAULT_WINDOW_TITLE = "AI 智能翻译工作台 v3.0"
    DEFAULT_WINDOW_WIDTH = 950
    DEFAULT_WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 400
    MIN_WINDOW_HEIGHT = 300


# ========== 性能监控配置 ==========
class PerformanceMonitorConfig:
    """性能监控相关常量"""
    DEFAULT_SAMPLE_INTERVAL = 1.0
    DEFAULT_HISTORY_SIZE = 300
    DEFAULT_ENABLE = False


# ========== 备份配置 ==========
class BackupConfig:
    """备份相关常量"""
    DEFAULT_BACKUP_DIR = ".terminology_backups"
    DEFAULT_BACKUP_STRATEGY = "daily"
    VALID_BACKUP_STRATEGIES = ['hourly', 'daily', 'weekly', 'per_batch']


# ========== 验证阈值 ==========
class ValidationThresholds:
    """参数验证阈值"""
    # Temperature 范围
    TEMPERATURE_MIN = 0.0
    TEMPERATURE_MAX = 2.0
    TEMPERATURE_RECOMMENDED_MIN = 0.3
    TEMPERATURE_RECOMMENDED_MAX = 0.7
    
    # Top P 范围
    TOP_P_MIN = 0.0
    TOP_P_MAX = 1.0
    TOP_P_RECOMMENDED_MIN = 0.8
    TOP_P_RECOMMENDED_MAX = 0.9
    
    # Timeout 范围
    TIMEOUT_MIN = 1
    TIMEOUT_RECOMMENDED = 60
    
    # 窗口尺寸
    WINDOW_WIDTH_MIN = 400
    WINDOW_WIDTH_RECOMMENDED = 950
    WINDOW_HEIGHT_MIN = 300
    WINDOW_HEIGHT_RECOMMENDED = 800
    
    # 批处理
    BATCH_SIZE_MIN = 1
    BATCH_SIZE_RECOMMENDED = 1000
    
    # 缓存
    CACHE_CAPACITY_MIN = 100
    CACHE_CAPACITY_RECOMMENDED = 2000
    
    # 相似度
    SIMILARITY_MIN = 0
    SIMILARITY_MAX = 100
    SIMILARITY_RECOMMENDED = 60


# ========== 文件路径配置 ==========
class PathConfig:
    """文件路径相关常量"""
    DEFAULT_CONFIG_FILES = [
        'config.yaml',
        'config.yml',
        'config.json',
        'config/config.yaml',
        'config/config.json',
    ]
    DEFAULT_DATABASE_DIR = 'data'
    DEFAULT_DATABASE_NAME = 'terminology.db'
    DEFAULT_EXCEL_FILENAME = "terminology.xlsx"


# ========== 语言配置 ==========
class LanguageConfig:
    """语言相关常量"""
    DEFAULT_SOURCE_LANG = "中文"
    DEFAULT_TARGET_LANGS = []
    DEFAULT_SUPPORTED_SOURCE_LANGS = ["中文", "英语", "日语", "韩语", "法语", "德语"]


# ========== 版本控制 ==========
class VersionConfig:
    """版本控制相关常量"""
    DEFAULT_ENABLE_VERSION_CONTROL = False
    DEFAULT_ENABLE_AUTO_BACKUP = False


# ========== 重试配置 ==========
class RetryConfig:
    """重试相关常量"""
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BASE_RETRY_DELAY = 3.0
    RATE_LIMIT_RETRY_AFTER_DEFAULT = 5.0


# ========== DeepSeek 模型配置 ==========
class DeepSeekConfig:
    """DeepSeek 模型特定配置常量"""
    # 支持的 DeepSeek 模型列表
    SUPPORTED_MODELS = [
        "deepseek-chat",      # DeepSeek Chat 模型
        "deepseek-coder",     # DeepSeek Coder 代码模型
        "deepseek-v2-chat",   # DeepSeek V2 Chat 模型
        "deepseek-v2-coder",  # DeepSeek V2 Coder 模型
    ]
    
    # 默认配置
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_BASE_URL = "https://api.deepseek.com"
    
    # 采样参数范围
    TEMPERATURE_MIN = 0.0
    TEMPERATURE_MAX = 2.0
    TEMPERATURE_DEFAULT = 0.7
    
    TOP_P_MIN = 0.0
    TOP_P_MAX = 1.0
    TOP_P_DEFAULT = 0.9
    
    # DeepSeek 特有参数
    PRESENCE_PENALTY_MIN = -2.0
    PRESENCE_PENALTY_MAX = 2.0
    PRESENCE_PENALTY_DEFAULT = 0.0
    
    FREQUENCY_PENALTY_MIN = -2.0
    FREQUENCY_PENALTY_MAX = 2.0
    FREQUENCY_PENALTY_DEFAULT = 0.0
    
    # 上下文窗口
    MAX_CONTEXT_WINDOW = 32768  # 32K tokens
    
    # 速率限制（每分钟请求数）
    RATE_LIMITS = {
        "deepseek-chat": 100,
        "deepseek-coder": 50,
        "deepseek-v2-chat": 100,
        "deepseek-v2-coder": 50,
    }
