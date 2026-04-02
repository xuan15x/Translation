"""
数据模型模块
定义所有数据结构和使用到的类型
"""
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging

from .log_slice import ModuleLoggerMixin, LogCategory, LoggerSlice
from .exceptions import ValidationError, AuthenticationError

# 导入默认提示词
DEFAULT_DRAFT_PROMPT = """Role: Professional Translator.
Task: Translate 'Src' to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Strictly follow provided TM.
3. Accurate and direct."""

DEFAULT_REVIEW_PROMPT = """Role: Senior Language Editor.
Task: Polish 'Draft' into native {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars. If no change, Reason="".
3. Focus on flow and tone."""

# 导入常量配置
from config.constants import (
    APIConfig, ConcurrencyConfig, CacheConfig, TerminologyConfig,
    WorkflowConfig, LogConfig, GUIConfig, PerformanceMonitorConfig,
    BackupConfig, LanguageConfig, VersionConfig
)


@dataclass
class Config(ModuleLoggerMixin):
    """配置类，存储所有系统和 API 参数 - 支持 DeepSeek 完整配置"""
    LOG_CATEGORY: LogCategory = LogCategory.MODEL

    # ========== API 基础配置 ==========
    api_key: str = ""  # 必须在配置文件中设置
    base_url: str = "https://api.deepseek.com"
    api_provider: str = "deepseek"

    # 多 API 提供商配置（支持配置文件管理）
    api_providers: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # ========== 全局模型配置 ==========
    model_name: str = "deepseek-chat"
    
    # OpenAI 兼容采样参数（支持 DeepSeek）
    temperature: float = APIConfig.DEFAULT_TEMPERATURE
    top_p: float = APIConfig.DEFAULT_TOP_P
    presence_penalty: float = 0.0  # DeepSeek 支持的存在惩罚
    frequency_penalty: float = 0.0  # DeepSeek 支持的频率惩罚
    stop: Optional[List[str]] = None  # 停止序列
    
    # 高级参数
    timeout: int = APIConfig.DEFAULT_TIMEOUT
    max_retries: int = APIConfig.DEFAULT_MAX_RETRIES
    retry_streak_threshold: int = ConcurrencyConfig.DEFAULT_RETRY_STREAK_THRESHOLD
    base_retry_delay: float = APIConfig.DEFAULT_RETRY_DELAY
    max_tokens: int = APIConfig.DEFAULT_MAX_TOKENS
    
    # 上下文窗口控制
    context_window_size: Optional[int] = None  # 上下文窗口大小（None=自动）
    enable_cache_control: bool = True  # 启用缓存控制
    enable_stream: bool = False  # 启用流式输出
    
    # 自定义请求头（高级用户）
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # 额外请求体参数（OpenAI 兼容）
    extra_body: Dict[str, Any] = field(default_factory=dict)

    # ========== 双阶段翻译专用配置 ==========
    # 初译阶段（Draft）
    draft_model_name: Optional[str] = None
    draft_temperature: Optional[float] = None
    draft_top_p: Optional[float] = None
    draft_presence_penalty: Optional[float] = None
    draft_frequency_penalty: Optional[float] = None
    draft_timeout: Optional[int] = None
    draft_max_tokens: int = APIConfig.DEFAULT_MAX_TOKENS

    # 校对阶段（Review）
    review_model_name: Optional[str] = None
    review_temperature: Optional[float] = None
    review_top_p: Optional[float] = None
    review_presence_penalty: Optional[float] = None
    review_frequency_penalty: Optional[float] = None
    review_timeout: Optional[int] = None
    review_max_tokens: int = APIConfig.DEFAULT_MAX_TOKENS

    # ========== 并发控制 ==========
    initial_concurrency: int = ConcurrencyConfig.DEFAULT_INITIAL_CONCURRENCY
    max_concurrency: int = ConcurrencyConfig.DEFAULT_MAX_CONCURRENCY
    concurrency_cooldown_seconds: float = ConcurrencyConfig.DEFAULT_COOLDOWN_SECONDS

    # ========== 工作流配置 ==========
    enable_two_pass: bool = WorkflowConfig.DEFAULT_ENABLE_TWO_PASS
    skip_review_if_local_hit: bool = WorkflowConfig.DEFAULT_SKIP_REVIEW_IF_LOCAL_HIT
    batch_size: int = WorkflowConfig.DEFAULT_BATCH_SIZE
    gc_interval: int = WorkflowConfig.DEFAULT_GC_INTERVAL

    # ========== 术语库配置 ==========
    similarity_low: int = TerminologyConfig.DEFAULT_SIMILARITY_LOW
    exact_match_score: int = TerminologyConfig.DEFAULT_EXACT_MATCH_SCORE
    multiprocess_threshold: int = TerminologyConfig.DEFAULT_MULTIPROCESS_THRESHOLD

    # ========== 性能配置 ==========
    pool_size: int = CacheConfig.DEFAULT_POOL_SIZE
    cache_capacity: int = CacheConfig.DEFAULT_CACHE_CAPACITY
    cache_ttl_seconds: int = CacheConfig.DEFAULT_CACHE_TTL_SECONDS

    # ========== 日志配置 ==========
    log_level: str = LogConfig.DEFAULT_LOG_LEVEL
    log_granularity: str = LogConfig.DEFAULT_LOG_GRANULARITY
    log_max_lines: int = LogConfig.DEFAULT_LOG_MAX_LINES

    # ========== GUI 配置 ==========
    gui_window_title: str = GUIConfig.DEFAULT_WINDOW_TITLE
    gui_window_width: int = GUIConfig.DEFAULT_WINDOW_WIDTH
    gui_window_height: int = GUIConfig.DEFAULT_WINDOW_HEIGHT

    # ========== 提示词配置 ==========
    draft_prompt: str = DEFAULT_DRAFT_PROMPT
    review_prompt: str = DEFAULT_REVIEW_PROMPT

    # ========== 语言配置 ==========
    default_source_lang: str = LanguageConfig.DEFAULT_SOURCE_LANG
    supported_source_langs: List[str] = field(default_factory=lambda: LanguageConfig.DEFAULT_SUPPORTED_SOURCE_LANGS)

    # ========== 版本控制和备份 ==========
    enable_version_control: bool = VersionConfig.DEFAULT_ENABLE_VERSION_CONTROL
    enable_auto_backup: bool = VersionConfig.DEFAULT_ENABLE_AUTO_BACKUP
    backup_dir: str = BackupConfig.DEFAULT_BACKUP_DIR
    backup_strategy: str = BackupConfig.DEFAULT_BACKUP_STRATEGY

    # ========== 性能监控 ==========
    enable_performance_monitor: bool = PerformanceMonitorConfig.DEFAULT_ENABLE
    perf_sample_interval: float = PerformanceMonitorConfig.DEFAULT_SAMPLE_INTERVAL
    perf_history_size: int = PerformanceMonitorConfig.DEFAULT_HISTORY_SIZE
    
    def __post_init__(self):
        """初始化后验证 - 增强安全模式"""
        # 确保 ModuleLoggerMixin 已初始化
        if not hasattr(self, '_logger_slice'):
            self._logger_slice = LoggerSlice(self.LOG_CATEGORY)

        self.log_info("Config 初始化", api_key_set=bool(self.api_key), provider=self.api_provider)

        # 安全修复：TEST_MODE 环境变量不再绕过 API key 验证
        # 仅在显式设置 TEST_MODE=skip_all 时跳过验证（仅用于测试）
        test_mode = os.getenv('TEST_MODE', '').lower()
        skip_all_checks = test_mode == 'skip_all'
        
        if skip_all_checks:
            # 仅在明确指定 TEST_MODE=skip_all 时跳过所有验证
            self.log_warning("测试模式：跳过所有配置验证（仅限测试环境）")
        else:
            # 正常模式下必须验证 API key
            if not self.api_key or not self.api_key.strip():
                error_msg = f"❌ 致命错误：API 密钥不能为空，请在配置文件或 GUI 界面中设置 api_key。"
                self.log_error(error_msg)
                raise AuthenticationError(error_msg, details={'env_var': 'api_key'})
            
            # 记录配置使用情况
            self._track_config_usage()
            # 验证配置参数的有效性
            self._validate_config()

        self.log_debug(f"Config 参数：base_url={self.base_url}, model={self.model_name}, provider={self.api_provider}")
        self.log_debug(f"Draft 模型：{self.get_draft_model_name()}, temperature={self.get_draft_temperature()}")
        self.log_debug(f"Review 模型：{self.get_review_model_name()}, temperature={self.get_review_temperature()}")
    
    def _validate_config(self):
        """验证配置参数的有效性 - 增强版，暴露具体出错点"""
        errors = []
        
        # ========== API 基础配置验证 ==========
        if not self.api_key or not self.api_key.strip():
            errors.append({
                'field': 'api_key',
                'error': 'API 密钥不能为空',
                'check_point': 'API 认证配置',
                'current_value': '(空)' if not self.api_key else '***',
                'requirement': '必须设置有效的 API 密钥',
                'solution': '请通过以下方式设置：\n'
                           '1. 配置文件：config.json 中设置 "api_key": "your-key"\n'
                           '2. GUI 界面：在翻译平台界面中配置 API 密钥'
            })
        
        # ========== API 提供商配置验证 ==========
        valid_providers = ['deepseek', 'openai', 'anthropic', 'moonshot', 'zhipu', 'baidu', 'alibaba', 'custom']
        if self.api_provider not in valid_providers:
            errors.append({
                'field': 'api_provider',
                'error': f'api_provider 值 "{self.api_provider}" 无效',
                'check_point': 'API 提供商选择',
                'current_value': self.api_provider,
                'requirement': f'必须是以下之一：{valid_providers}',
                'solution': f'建议使用 "deepseek" 或 "openai"，当前值：" {self.api_provider}"'
            })
        
        if not self.base_url or not self.base_url.strip():
            errors.append({
                'field': 'base_url',
                'error': 'API Base URL 不能为空',
                'check_point': 'API 端点配置',
                'current_value': repr(self.base_url),
                'requirement': '必须设置有效的 API 端点 URL',
                'solution': '示例："base_url": "https://api.deepseek.com"'
            })
        elif not self.base_url.startswith(('http://', 'https://')):
            errors.append({
                'field': 'base_url',
                'error': 'API Base URL 格式错误',
                'check_point': 'URL 格式验证',
                'current_value': self.base_url,
                'requirement': 'URL 必须以 http:// 或 https:// 开头',
                'solution': '修正为："https://api.deepseek.com" 或 "http://localhost:8000"'
            })
        
        # ========== 全局模型参数验证 ==========
        if not isinstance(self.model_name, str) or not self.model_name.strip():
            errors.append({
                'field': 'model_name',
                'error': '模型名称不能为空字符串',
                'check_point': '模型标识配置',
                'current_value': repr(self.model_name),
                'requirement': '必须指定有效的模型名称',
                'solution': '示例："model_name": "deepseek-chat" 或 "gpt-4"'
            })
        
        if not (0 <= self.temperature <= 2):
            errors.append({
                'field': 'temperature',
                'error': f'temperature 值 {self.temperature} 超出有效范围',
                'check_point': '模型温度参数',
                'current_value': self.temperature,
                'requirement': '必须在 0 到 2 之间（推荐值：0.3-0.5）',
                'solution': f'建议设置为 0.3（保守翻译）或 0.5（平衡翻译），当前值：{self.temperature}'
            })
        
        if not (0 <= self.top_p <= 1):
            errors.append({
                'field': 'top_p',
                'error': f'top_p 值 {self.top_p} 超出有效范围',
                'check_point': '核采样参数',
                'current_value': self.top_p,
                'requirement': '必须在 0 到 1 之间（推荐值：0.8-0.9）',
                'solution': f'建议设置为 0.8（稳定）或 0.9（灵活），当前值：{self.top_p}'
            })
        
        if self.timeout < 1:
            errors.append({
                'field': 'timeout',
                'error': f'timeout 值 {self.timeout} 秒太短',
                'check_point': '超时时间配置',
                'current_value': f'{self.timeout}秒',
                'requirement': '必须 >= 1 秒（推荐值：30-120 秒）',
                'solution': f'建议设置为 60 秒（中等文本）或 90 秒（长文本），当前值：{self.timeout}秒'
            })
        
        if self.max_retries < 0:
            errors.append({
                'field': 'max_retries',
                'error': f'max_retries 值 {self.max_retries} 无效',
                'check_point': '重试次数配置',
                'current_value': self.max_retries,
                'requirement': '必须 >= 0（推荐值：2-5 次）',
                'solution': f'建议设置为 3 次，当前值：{self.max_retries}'
            })
        
        # ========== Draft 阶段参数验证 ==========
        if self.draft_temperature is not None and not (0 <= self.draft_temperature <= 2):
            errors.append({
                'field': 'draft_temperature',
                'error': f'draft_temperature 值 {self.draft_temperature} 超出范围',
                'check_point': '初译阶段温度参数',
                'current_value': self.draft_temperature,
                'requirement': '必须在 0 到 2 之间（推荐值：0.3-0.4）',
                'solution': f'初译建议使用较低温度（如 0.3）以保证准确性，当前值：{self.draft_temperature}'
            })
        
        if self.draft_top_p is not None and not (0 <= self.draft_top_p <= 1):
            errors.append({
                'field': 'draft_top_p',
                'error': f'draft_top_p 值 {self.draft_top_p} 超出范围',
                'check_point': '初译阶段核采样参数',
                'current_value': self.draft_top_p,
                'requirement': '必须在 0 到 1 之间（推荐值：0.8）',
                'solution': f'初译建议使用较保守的 top_p（如 0.8），当前值：{self.draft_top_p}'
            })
        
        if self.draft_max_tokens < 100:
            errors.append({
                'field': 'draft_max_tokens',
                'error': f'draft_max_tokens 值 {self.draft_max_tokens} 过小',
                'check_point': '初译输出长度限制',
                'current_value': self.draft_max_tokens,
                'requirement': '必须 >= 100（推荐值：512-1024）',
                'solution': f'建议设置为 512 以支持较长句子的翻译，当前值：{self.draft_max_tokens}'
            })
        
        # ========== Review 阶段参数验证 ==========
        if self.review_temperature is not None and not (0 <= self.review_temperature <= 2):
            errors.append({
                'field': 'review_temperature',
                'error': f'review_temperature 值 {self.review_temperature} 超出范围',
                'check_point': '校对阶段温度参数',
                'current_value': self.review_temperature,
                'requirement': '必须在 0 到 2 之间（推荐值：0.5-0.7）',
                'solution': f'校对建议使用较高温度（如 0.5-0.7）以优化表达，当前值：{self.review_temperature}'
            })
        
        if self.review_top_p is not None and not (0 <= self.review_top_p <= 1):
            errors.append({
                'field': 'review_top_p',
                'error': f'review_top_p 值 {self.review_top_p} 超出范围',
                'check_point': '校对阶段核采样参数',
                'current_value': self.review_top_p,
                'requirement': '必须在 0 到 1 之间（推荐值：0.9）',
                'solution': f'校对建议使用较灵活的 top_p（如 0.9），当前值：{self.review_top_p}'
            })
        
        if self.review_max_tokens < 100:
            errors.append({
                'field': 'review_max_tokens',
                'error': f'review_max_tokens 值 {self.review_max_tokens} 过小',
                'check_point': '校对输出长度限制',
                'current_value': self.review_max_tokens,
                'requirement': '必须 >= 100（推荐值：512-1024）',
                'solution': f'建议设置为 512 以支持较长的润色说明，当前值：{self.review_max_tokens}'
            })
        
        # ========== 并发控制配置验证 ==========
        if self.initial_concurrency < 1:
            errors.append({
                'field': 'initial_concurrency',
                'error': f'initial_concurrency 值 {self.initial_concurrency} 无效',
                'check_point': '初始并发数配置',
                'current_value': self.initial_concurrency,
                'requirement': '必须 >= 1（推荐值：2-10）',
                'solution': f'建议根据 API 限流情况设置，新手从 2 开始，当前值：{self.initial_concurrency}'
            })
        
        if self.max_concurrency < self.initial_concurrency:
            errors.append({
                'field': 'max_concurrency',
                'error': f'max_concurrency ({self.max_concurrency}) < initial_concurrency ({self.initial_concurrency})',
                'check_point': '并发上限逻辑校验',
                'current_value': f'max={self.max_concurrency}, initial={self.initial_concurrency}',
                'requirement': 'max_concurrency 必须 >= initial_concurrency',
                'solution': f'请将 max_concurrency 设置为 >= {self.initial_concurrency} 的值'
            })
        
        if self.concurrency_cooldown_seconds < 0:
            errors.append({
                'field': 'concurrency_cooldown_seconds',
                'error': f'concurrency_cooldown_seconds 值 {self.concurrency_cooldown_seconds} 无效',
                'check_point': '并发冷却时间配置',
                'current_value': f'{self.concurrency_cooldown_seconds}秒',
                'requirement': '必须 >= 0（推荐值：3.0-10.0 秒）',
                'solution': f'建议设置为 5.0 秒，API 限流严重时增加到 10.0 秒，当前值：{self.concurrency_cooldown_seconds}秒'
            })
        
        # ========== 工作流配置验证 ==========
        if self.batch_size < 1:
            errors.append({
                'field': 'batch_size',
                'error': f'batch_size 值 {self.batch_size} 无效',
                'check_point': '批处理大小配置',
                'current_value': self.batch_size,
                'requirement': '必须 >= 1（推荐值：500-2000）',
                'solution': f'建议设置为 1000，内存充足可设为 2000，当前值：{self.batch_size}'
            })
        
        if self.gc_interval < 0:
            errors.append({
                'field': 'gc_interval',
                'error': f'gc_interval 值 {self.gc_interval} 无效',
                'check_point': '垃圾回收间隔配置',
                'current_value': self.gc_interval,
                'requirement': '必须 >= 0（推荐值：2-5）',
                'solution': f'建议每 2 个任务执行一次 GC，当前值：{self.gc_interval}'
            })
        
        # ========== 术语库配置验证 ==========
        if not (0 <= self.similarity_low <= 100):
            errors.append({
                'field': 'similarity_low',
                'error': f'similarity_low 值 {self.similarity_low} 超出范围',
                'check_point': '模糊匹配阈值配置',
                'current_value': self.similarity_low,
                'requirement': '必须在 0 到 100 之间（推荐值：60-70）',
                'solution': f'建议设置为 60（平衡）或 70（严格），当前值：{self.similarity_low}'
            })
        
        if self.exact_match_score != 100:
            errors.append({
                'field': 'exact_match_score',
                'error': f'exact_match_score 值 {self.exact_match_score} 不推荐',
                'check_point': '精确匹配置信度',
                'current_value': self.exact_match_score,
                'requirement': '强烈建议设置为 100',
                'solution': '精确匹配应该使用满分 100 分，不建议修改'
            })
        
        if self.multiprocess_threshold < 100:
            errors.append({
                'field': 'multiprocess_threshold',
                'error': f'multiprocess_threshold 值 {self.multiprocess_threshold} 过小',
                'check_point': '多进程处理阈值',
                'current_value': self.multiprocess_threshold,
                'requirement': '必须 >= 100（推荐值：1000-2000）',
                'solution': f'术语库少于 1000 条时使用单进程，超过使用多进程，当前阈值：{self.multiprocess_threshold}'
            })
        
        # ========== 性能配置验证 ==========
        if self.pool_size < 1:
            errors.append({
                'field': 'pool_size',
                'error': f'pool_size 值 {self.pool_size} 无效',
                'check_point': '数据库连接池大小',
                'current_value': self.pool_size,
                'requirement': '必须 >= 1（推荐值：5-10）',
                'solution': f'建议设置为 5，高并发场景可设为 10，当前值：{self.pool_size}'
            })
        
        if self.cache_capacity < 100:
            errors.append({
                'field': 'cache_capacity',
                'error': f'cache_capacity 值 {self.cache_capacity} 过小',
                'check_point': '缓存容量配置',
                'current_value': self.cache_capacity,
                'requirement': '必须 >= 100（推荐值：2000-5000）',
                'solution': f'建议根据术语库大小设置，至少 2000，当前值：{self.cache_capacity}'
            })
        
        if self.cache_ttl_seconds < 0:
            errors.append({
                'field': 'cache_ttl_seconds',
                'error': f'cache_ttl_seconds 值 {self.cache_ttl_seconds} 无效',
                'check_point': '缓存过期时间配置',
                'current_value': f'{self.cache_ttl_seconds}秒',
                'requirement': '必须 >= 0（0 表示永不过期，推荐值：3600）',
                'solution': f'建议设置为 3600 秒（1 小时）或 0（永不过期），当前值：{self.cache_ttl_seconds}秒'
            })
        
        # ========== 日志配置验证 ==========
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_log_levels:
            errors.append({
                'field': 'log_level',
                'error': f'log_level 值 "{self.log_level}" 无效',
                'check_point': '日志级别配置',
                'current_value': self.log_level,
                'requirement': f'必须是以下之一：{valid_log_levels}',
                'solution': f'建议设置为 "INFO"（常规）或 "DEBUG"（调试），当前值："{self.log_level}"'
            })
        
        valid_log_granularities = ['minimal', 'basic', 'normal', 'detailed', 'verbose']
        if self.log_granularity not in valid_log_granularities:
            errors.append({
                'field': 'log_granularity',
                'error': f'log_granularity 值 "{self.log_granularity}" 无效',
                'check_point': '日志粒度配置',
                'current_value': self.log_granularity,
                'requirement': f'必须是以下之一：{valid_log_granularities}',
                'solution': f'建议设置为 "normal"（常规）或 "detailed"（详细），当前值："{self.log_granularity}"'
            })
        
        if self.log_max_lines < 100:
            errors.append({
                'field': 'log_max_lines',
                'error': f'log_max_lines 值 {self.log_max_lines} 过小',
                'check_point': 'GUI 日志行数限制',
                'current_value': self.log_max_lines,
                'requirement': '必须 >= 100（推荐值：1000-5000）',
                'solution': f'建议设置为 1000 行，需要完整日志可设为 5000，当前值：{self.log_max_lines}'
            })
        
        # ========== GUI 配置验证 ==========
        if self.gui_window_width < 400:
            errors.append({
                'field': 'gui_window_width',
                'error': f'gui_window_width 值 {self.gui_window_width} 过小',
                'check_point': 'GUI 窗口宽度',
                'current_value': f'{self.gui_window_width}px',
                'requirement': '必须 >= 400（推荐值：950-1200）',
                'solution': f'建议设置为 950px 以获得良好体验，当前值：{self.gui_window_width}px'
            })
        
        if self.gui_window_height < 300:
            errors.append({
                'field': 'gui_window_height',
                'error': f'gui_window_height 值 {self.gui_window_height} 过小',
                'check_point': 'GUI 窗口高度',
                'current_value': f'{self.gui_window_height}px',
                'requirement': '必须 >= 300（推荐值：800-1000）',
                'solution': f'建议设置为 800px 以获得良好体验，当前值：{self.gui_window_height}px'
            })
        
        # ========== 语言配置验证 ==========
        if not self.default_source_lang or not self.default_source_lang.strip():
            errors.append({
                'field': 'default_source_lang',
                'error': '默认源语言不能为空',
                'check_point': '默认源语言配置',
                'current_value': repr(self.default_source_lang),
                'requirement': '必须设置有效的语言名称',
                'solution': '示例："中文"、"English"、"日本語"'
            })
        
        if not isinstance(self.supported_source_langs, list) or len(self.supported_source_langs) == 0:
            errors.append({
                'field': 'supported_source_langs',
                'error': '支持的语言列表不能为空',
                'check_point': '支持语言列表配置',
                'current_value': self.supported_source_langs,
                'requirement': '必须包含至少一种语言',
                'solution': '示例：["中文", "英语", "日语"]'
            })
        
        # ========== 版本控制和备份配置验证 ==========
        if self.enable_auto_backup and not self.backup_dir:
            errors.append({
                'field': 'backup_dir',
                'error': '启用自动备份时必须指定 backup_dir',
                'check_point': '备份目录配置',
                'current_value': repr(self.backup_dir),
                'requirement': 'enable_auto_backup=true 时必须有有效的 backup_dir',
                'solution': '示例：".terminology_backups" 或 "/path/to/backups"'
            })
        
        valid_backup_strategies = ['hourly', 'daily', 'weekly', 'per_batch']
        if self.enable_auto_backup and self.backup_strategy not in valid_backup_strategies:
            errors.append({
                'field': 'backup_strategy',
                'error': f'backup_strategy 值 "{self.backup_strategy}" 无效',
                'check_point': '备份策略配置',
                'current_value': self.backup_strategy,
                'requirement': f'必须是以下之一：{valid_backup_strategies}',
                'solution': f'建议使用 "daily"（每日备份）或 "per_batch"（每批次备份），当前值："{self.backup_strategy}"'
            })
        
        # ========== 性能监控配置验证 ==========
        if self.enable_performance_monitor:
            if self.perf_sample_interval <= 0:
                errors.append({
                    'field': 'perf_sample_interval',
                    'error': f'perf_sample_interval 值 {self.perf_sample_interval} 无效',
                    'check_point': '性能采样间隔',
                    'current_value': f'{self.perf_sample_interval}秒',
                    'requirement': '必须 > 0（推荐值：1.0-5.0 秒）',
                    'solution': f'建议设置为 1.0 秒，当前值：{self.perf_sample_interval}秒'
                })
            
            if self.perf_history_size < 10:
                errors.append({
                    'field': 'perf_history_size',
                    'error': f'perf_history_size 值 {self.perf_history_size} 过小',
                    'check_point': '性能历史记录大小',
                    'current_value': self.perf_history_size,
                    'requirement': '必须 >= 10（推荐值：300-500）',
                    'solution': f'建议设置为 300 以保留足够历史数据，当前值：{self.perf_history_size}'
                })
        
        # ========== 提示词配置验证 ==========
        if not self.draft_prompt or not self.draft_prompt.strip():
            errors.append({
                'field': 'draft_prompt',
                'error': '初译提示词不能为空',
                'check_point': 'Draft Prompt 配置',
                'current_value': '(空)',
                'requirement': '必须包含有效的提示词模板',
                'solution': '必须包含 {target_lang} 占位符和 JSON 输出格式要求'
            })
        elif '{target_lang}' not in self.draft_prompt:
            errors.append({
                'field': 'draft_prompt',
                'error': '初译提示词缺少必需的 {target_lang} 占位符',
                'check_point': 'Prompt 变量占位符检查',
                'current_value': self.draft_prompt[:100] + '...',
                'requirement': '提示词必须包含 {target_lang} 占位符',
                'solution': '在提示词中添加 "Translate to {target_lang}"'
            })
        
        if not self.review_prompt or not self.review_prompt.strip():
            errors.append({
                'field': 'review_prompt',
                'error': '校对提示词不能为空',
                'check_point': 'Review Prompt 配置',
                'current_value': '(空)',
                'requirement': '必须包含有效的提示词模板',
                'solution': '必须包含 {target_lang} 占位符和 Reason 字段要求'
            })
        elif '{target_lang}' not in self.review_prompt:
            errors.append({
                'field': 'review_prompt',
                'error': '校对提示词缺少必需的 {target_lang} 占位符',
                'check_point': 'Prompt 变量占位符检查',
                'current_value': self.review_prompt[:100] + '...',
                'requirement': '提示词必须包含 {target_lang} 占位符',
                'solution': '在提示词中添加 "Polish into {target_lang}"'
            })
        
        # ========== 抛出所有验证错误 ==========
        if errors:
            error_message = self._format_validation_errors(errors)
            raise ValidationError(
                message=f"配置验证失败：共发现 {len(errors)} 个错误",
                field_name='config_validation',
                details={
                    'total_errors': len(errors),
                    'errors': errors,
                    'error_summary': error_message
                }
            )
    
    def _format_validation_errors(self, errors: List[Dict]) -> str:
        """格式化验证错误为易读的文本"""
        if not errors:
            return ""
        
        lines = [f"❌ 配置验证失败：共发现 {len(errors)} 个错误\n"]
        
        # 按检查点分组
        checkpoints = {}
        for error in errors:
            checkpoint = error.get('check_point', '其他配置')
            if checkpoint not in checkpoints:
                checkpoints[checkpoint] = []
            checkpoints[checkpoint].append(error)
        
        # 格式化输出
        for i, (checkpoint, checkpoint_errors) in enumerate(checkpoints.items(), 1):
            lines.append(f"\n【检查点 {i}】{checkpoint}")
            lines.append("─" * 60)
            
            for error in checkpoint_errors:
                lines.append(f"\n  ❌ 字段：{error['field']}")
                lines.append(f"     错误：{error['error']}")
                lines.append(f"     当前值：{error['current_value']}")
                lines.append(f"     要求：{error['requirement']}")
                lines.append(f"\n  💡 解决方案:")
                for solution_line in error['solution'].split('\n'):
                    lines.append(f"     {solution_line}")
        
        lines.append("\n" + "═" * 60)
        lines.append(f"总计：{len(errors)} 个配置错误需要修正")
        
        return "\n".join(lines)

    def _track_config_usage(self):
        """
        跟踪配置使用情况（用于分析和监控）
        记录哪些配置项被使用，帮助优化默认配置
        """
        # 简单实现：记录配置使用日志
        self.log_debug(
            "配置使用跟踪",
            provider=self.api_provider,
            model=self.model_name,
            concurrency=self.initial_concurrency,
            batch_size=self.batch_size
        )

    def _validate_config(self):
        """验证配置参数的有效性 - 增强版，暴露具体出错点"""
        errors = []
        
        # ========== API 基础配置验证 ==========
        if not self.api_key or not self.api_key.strip():
            errors.append({
                'field': 'api_key',
                'error': 'API 密钥不能为空',
                'check_point': 'API 认证配置',
                'current_value': '(空)' if not self.api_key else '***',
                'requirement': '必须设置有效的 API 密钥',
                'solution': '请通过以下方式设置：\n'
                           '1. 配置文件：config.json 中设置 "api_key": "your-key"\n'
                           '2. GUI 界面：在翻译平台界面中配置 API 密钥'
            })
        
        # ========== API 提供商配置验证 ==========
        valid_providers = ['deepseek', 'openai', 'anthropic', 'moonshot', 'zhipu', 'baidu', 'alibaba', 'custom']
        if self.api_provider not in valid_providers:
            errors.append({
                'field': 'api_provider',
                'error': f'api_provider 值 "{self.api_provider}" 无效',
                'check_point': 'API 提供商选择',
                'current_value': self.api_provider,
                'requirement': f'必须是以下之一：{valid_providers}',
                'solution': f'建议使用 "deepseek" 或 "openai"，当前值：" {self.api_provider}"'
            })
        
        if not self.base_url or not self.base_url.strip():
            errors.append({
                'field': 'base_url',
                'error': 'API Base URL 不能为空',
                'check_point': 'API 端点配置',
                'current_value': repr(self.base_url),
                'requirement': '必须设置有效的 API 端点 URL',
                'solution': '示例："base_url": "https://api.deepseek.com"'
            })
        elif not self.base_url.startswith(('http://', 'https://')):
            errors.append({
                'field': 'base_url',
                'error': 'API Base URL 格式错误',
                'check_point': 'URL 格式验证',
                'current_value': self.base_url,
                'requirement': 'URL 必须以 http:// 或 https:// 开头',
                'solution': '修正为："https://api.deepseek.com" 或 "http://localhost:8000"'
            })
        
        # ========== 全局模型参数验证 ==========
        if not isinstance(self.model_name, str) or not self.model_name.strip():
            errors.append({
                'field': 'model_name',
                'error': '模型名称不能为空字符串',
                'check_point': '模型标识配置',
                'current_value': repr(self.model_name),
                'requirement': '必须指定有效的模型名称',
                'solution': '示例："model_name": "deepseek-chat" 或 "gpt-4"'
            })
        
        if not (0 <= self.temperature <= 2):
            errors.append({
                'field': 'temperature',
                'error': f'temperature 值 {self.temperature} 超出有效范围',
                'check_point': '模型温度参数',
                'current_value': self.temperature,
                'requirement': '必须在 0 到 2 之间（推荐值：0.3-0.5）',
                'solution': f'建议设置为 0.3（保守翻译）或 0.5（平衡翻译），当前值：{self.temperature}'
            })
        
        if not (0 <= self.top_p <= 1):
            errors.append({
                'field': 'top_p',
                'error': f'top_p 值 {self.top_p} 超出有效范围',
                'check_point': '核采样参数',
                'current_value': self.top_p,
                'requirement': '必须在 0 到 1 之间（推荐值：0.8-0.9）',
                'solution': f'建议设置为 0.8（稳定）或 0.9（灵活），当前值：{self.top_p}'
            })
        
        if self.timeout < 1:
            errors.append({
                'field': 'timeout',
                'error': f'timeout 值 {self.timeout} 秒太短',
                'check_point': '超时时间配置',
                'current_value': f'{self.timeout}秒',
                'requirement': '必须 >= 1 秒（推荐值：30-120 秒）',
                'solution': f'建议设置为 60 秒（中等文本）或 90 秒（长文本），当前值：{self.timeout}秒'
            })
        
        if self.max_retries < 0:
            errors.append({
                'field': 'max_retries',
                'error': f'max_retries 值 {self.max_retries} 无效',
                'check_point': '重试次数配置',
                'current_value': self.max_retries,
                'requirement': '必须 >= 0（推荐值：2-5 次）',
                'solution': f'建议设置为 3 次，当前值：{self.max_retries}'
            })
        
        # ========== Draft 阶段参数验证 ==========
        if self.draft_temperature is not None and not (0 <= self.draft_temperature <= 2):
            errors.append({
                'field': 'draft_temperature',
                'error': f'draft_temperature 值 {self.draft_temperature} 超出范围',
                'check_point': '初译阶段温度参数',
                'current_value': self.draft_temperature,
                'requirement': '必须在 0 到 2 之间（推荐值：0.3-0.4）',
                'solution': f'初译建议使用较低温度（如 0.3）以保证准确性，当前值：{self.draft_temperature}'
            })
        
        if self.draft_top_p is not None and not (0 <= self.draft_top_p <= 1):
            errors.append({
                'field': 'draft_top_p',
                'error': f'draft_top_p 值 {self.draft_top_p} 超出范围',
                'check_point': '初译阶段核采样参数',
                'current_value': self.draft_top_p,
                'requirement': '必须在 0 到 1 之间（推荐值：0.8）',
                'solution': f'初译建议使用较保守的 top_p（如 0.8），当前值：{self.draft_top_p}'
            })
        
        if self.draft_max_tokens < 100:
            errors.append({
                'field': 'draft_max_tokens',
                'error': f'draft_max_tokens 值 {self.draft_max_tokens} 过小',
                'check_point': '初译输出长度限制',
                'current_value': self.draft_max_tokens,
                'requirement': '必须 >= 100（推荐值：512-1024）',
                'solution': f'建议设置为 512 以支持较长句子的翻译，当前值：{self.draft_max_tokens}'
            })
        
        # ========== Review 阶段参数验证 ==========
        if self.review_temperature is not None and not (0 <= self.review_temperature <= 2):
            errors.append({
                'field': 'review_temperature',
                'error': f'review_temperature 值 {self.review_temperature} 超出范围',
                'check_point': '校对阶段温度参数',
                'current_value': self.review_temperature,
                'requirement': '必须在 0 到 2 之间（推荐值：0.5-0.7）',
                'solution': f'校对建议使用较高温度（如 0.5-0.7）以优化表达，当前值：{self.review_temperature}'
            })
        
        if self.review_top_p is not None and not (0 <= self.review_top_p <= 1):
            errors.append({
                'field': 'review_top_p',
                'error': f'review_top_p 值 {self.review_top_p} 超出范围',
                'check_point': '校对阶段核采样参数',
                'current_value': self.review_top_p,
                'requirement': '必须在 0 到 1 之间（推荐值：0.9）',
                'solution': f'校对建议使用较灵活的 top_p（如 0.9），当前值：{self.review_top_p}'
            })
        
        if self.review_max_tokens < 100:
            errors.append({
                'field': 'review_max_tokens',
                'error': f'review_max_tokens 值 {self.review_max_tokens} 过小',
                'check_point': '校对输出长度限制',
                'current_value': self.review_max_tokens,
                'requirement': '必须 >= 100（推荐值：512-1024）',
                'solution': f'建议设置为 512 以支持较长的润色说明，当前值：{self.review_max_tokens}'
            })
        
        # ========== 并发控制配置验证 ==========
        if self.initial_concurrency < 1:
            errors.append({
                'field': 'initial_concurrency',
                'error': f'initial_concurrency 值 {self.initial_concurrency} 无效',
                'check_point': '初始并发数配置',
                'current_value': self.initial_concurrency,
                'requirement': '必须 >= 1（推荐值：2-10）',
                'solution': f'建议根据 API 限流情况设置，新手从 2 开始，当前值：{self.initial_concurrency}'
            })
        
        if self.max_concurrency < self.initial_concurrency:
            errors.append({
                'field': 'max_concurrency',
                'error': f'max_concurrency ({self.max_concurrency}) < initial_concurrency ({self.initial_concurrency})',
                'check_point': '并发上限逻辑校验',
                'current_value': f'max={self.max_concurrency}, initial={self.initial_concurrency}',
                'requirement': 'max_concurrency 必须 >= initial_concurrency',
                'solution': f'请将 max_concurrency 设置为 >= {self.initial_concurrency} 的值'
            })
        
        if self.concurrency_cooldown_seconds < 0:
            errors.append({
                'field': 'concurrency_cooldown_seconds',
                'error': f'concurrency_cooldown_seconds 值 {self.concurrency_cooldown_seconds} 无效',
                'check_point': '并发冷却时间配置',
                'current_value': f'{self.concurrency_cooldown_seconds}秒',
                'requirement': '必须 >= 0（推荐值：3.0-10.0 秒）',
                'solution': f'建议设置为 5.0 秒，API 限流严重时增加到 10.0 秒，当前值：{self.concurrency_cooldown_seconds}秒'
            })
        
        # ========== 工作流配置验证 ==========
        if self.batch_size < 1:
            errors.append({
                'field': 'batch_size',
                'error': f'batch_size 值 {self.batch_size} 无效',
                'check_point': '批处理大小配置',
                'current_value': self.batch_size,
                'requirement': '必须 >= 1（推荐值：500-2000）',
                'solution': f'建议设置为 1000，内存充足可设为 2000，当前值：{self.batch_size}'
            })
        
        if self.gc_interval < 0:
            errors.append({
                'field': 'gc_interval',
                'error': f'gc_interval 值 {self.gc_interval} 无效',
                'check_point': '垃圾回收间隔配置',
                'current_value': self.gc_interval,
                'requirement': '必须 >= 0（推荐值：2-5）',
                'solution': f'建议每 2 个任务执行一次 GC，当前值：{self.gc_interval}'
            })
        
        # ========== 术语库配置验证 ==========
        if not (0 <= self.similarity_low <= 100):
            errors.append({
                'field': 'similarity_low',
                'error': f'similarity_low 值 {self.similarity_low} 超出范围',
                'check_point': '模糊匹配阈值配置',
                'current_value': self.similarity_low,
                'requirement': '必须在 0 到 100 之间（推荐值：60-70）',
                'solution': f'建议设置为 60（平衡）或 70（严格），当前值：{self.similarity_low}'
            })
        
        if self.exact_match_score != 100:
            errors.append({
                'field': 'exact_match_score',
                'error': f'exact_match_score 值 {self.exact_match_score} 不推荐',
                'check_point': '精确匹配置信度',
                'current_value': self.exact_match_score,
                'requirement': '强烈建议设置为 100',
                'solution': '精确匹配应该使用满分 100 分，不建议修改'
            })
        
        if self.multiprocess_threshold < 100:
            errors.append({
                'field': 'multiprocess_threshold',
                'error': f'multiprocess_threshold 值 {self.multiprocess_threshold} 过小',
                'check_point': '多进程处理阈值',
                'current_value': self.multiprocess_threshold,
                'requirement': '必须 >= 100（推荐值：1000-2000）',
                'solution': f'术语库少于 1000 条时使用单进程，超过使用多进程，当前阈值：{self.multiprocess_threshold}'
            })
        
        # ========== 性能配置验证 ==========
        if self.pool_size < 1:
            errors.append({
                'field': 'pool_size',
                'error': f'pool_size 值 {self.pool_size} 无效',
                'check_point': '数据库连接池大小',
                'current_value': self.pool_size,
                'requirement': '必须 >= 1（推荐值：5-10）',
                'solution': f'建议设置为 5，高并发场景可设为 10，当前值：{self.pool_size}'
            })
        
        if self.cache_capacity < 100:
            errors.append({
                'field': 'cache_capacity',
                'error': f'cache_capacity 值 {self.cache_capacity} 过小',
                'check_point': '缓存容量配置',
                'current_value': self.cache_capacity,
                'requirement': '必须 >= 100（推荐值：2000-5000）',
                'solution': f'建议根据术语库大小设置，至少 2000，当前值：{self.cache_capacity}'
            })
        
        if self.cache_ttl_seconds < 0:
            errors.append({
                'field': 'cache_ttl_seconds',
                'error': f'cache_ttl_seconds 值 {self.cache_ttl_seconds} 无效',
                'check_point': '缓存过期时间配置',
                'current_value': f'{self.cache_ttl_seconds}秒',
                'requirement': '必须 >= 0（0 表示永不过期，推荐值：3600）',
                'solution': f'建议设置为 3600 秒（1 小时）或 0（永不过期），当前值：{self.cache_ttl_seconds}秒'
            })
        
        # ========== 日志配置验证 ==========
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_log_levels:
            errors.append({
                'field': 'log_level',
                'error': f'log_level 值 "{self.log_level}" 无效',
                'check_point': '日志级别配置',
                'current_value': self.log_level,
                'requirement': f'必须是以下之一：{valid_log_levels}',
                'solution': f'建议设置为 "INFO"（常规）或 "DEBUG"（调试），当前值："{self.log_level}"'
            })
        
        valid_log_granularities = ['minimal', 'basic', 'normal', 'detailed', 'verbose']
        if self.log_granularity not in valid_log_granularities:
            errors.append({
                'field': 'log_granularity',
                'error': f'log_granularity 值 "{self.log_granularity}" 无效',
                'check_point': '日志粒度配置',
                'current_value': self.log_granularity,
                'requirement': f'必须是以下之一：{valid_log_granularities}',
                'solution': f'建议设置为 "normal"（常规）或 "detailed"（详细），当前值："{self.log_granularity}"'
            })
        
        if self.log_max_lines < 100:
            errors.append({
                'field': 'log_max_lines',
                'error': f'log_max_lines 值 {self.log_max_lines} 过小',
                'check_point': 'GUI 日志行数限制',
                'current_value': self.log_max_lines,
                'requirement': '必须 >= 100（推荐值：1000-5000）',
                'solution': f'建议设置为 1000 行，需要完整日志可设为 5000，当前值：{self.log_max_lines}'
            })
        
        # ========== GUI 配置验证 ==========
        if self.gui_window_width < 400:
            errors.append({
                'field': 'gui_window_width',
                'error': f'gui_window_width 值 {self.gui_window_width} 过小',
                'check_point': 'GUI 窗口宽度',
                'current_value': f'{self.gui_window_width}px',
                'requirement': '必须 >= 400（推荐值：950-1200）',
                'solution': f'建议设置为 950px 以获得良好体验，当前值：{self.gui_window_width}px'
            })
        
        if self.gui_window_height < 300:
            errors.append({
                'field': 'gui_window_height',
                'error': f'gui_window_height 值 {self.gui_window_height} 过小',
                'check_point': 'GUI 窗口高度',
                'current_value': f'{self.gui_window_height}px',
                'requirement': '必须 >= 300（推荐值：800-1000）',
                'solution': f'建议设置为 800px 以获得良好体验，当前值：{self.gui_window_height}px'
            })
        
        # ========== 语言配置验证 ==========
        if not self.default_source_lang or not self.default_source_lang.strip():
            errors.append({
                'field': 'default_source_lang',
                'error': '默认源语言不能为空',
                'check_point': '默认源语言配置',
                'current_value': repr(self.default_source_lang),
                'requirement': '必须设置有效的语言名称',
                'solution': '示例："中文"、"English"、"日本語"'
            })
        
        if not isinstance(self.supported_source_langs, list) or len(self.supported_source_langs) == 0:
            errors.append({
                'field': 'supported_source_langs',
                'error': '支持的语言列表不能为空',
                'check_point': '支持语言列表配置',
                'current_value': self.supported_source_langs,
                'requirement': '必须包含至少一种语言',
                'solution': '示例：["中文", "英语", "日语"]'
            })
        
        # ========== 版本控制和备份配置验证 ==========
        if self.enable_auto_backup and not self.backup_dir:
            errors.append({
                'field': 'backup_dir',
                'error': '启用自动备份时必须指定 backup_dir',
                'check_point': '备份目录配置',
                'current_value': repr(self.backup_dir),
                'requirement': 'enable_auto_backup=true 时必须有有效的 backup_dir',
                'solution': '示例：".terminology_backups" 或 "/path/to/backups"'
            })
        
        valid_backup_strategies = ['hourly', 'daily', 'weekly', 'per_batch']
        if self.enable_auto_backup and self.backup_strategy not in valid_backup_strategies:
            errors.append({
                'field': 'backup_strategy',
                'error': f'backup_strategy 值 "{self.backup_strategy}" 无效',
                'check_point': '备份策略配置',
                'current_value': self.backup_strategy,
                'requirement': f'必须是以下之一：{valid_backup_strategies}',
                'solution': f'建议使用 "daily"（每日备份）或 "per_batch"（每批次备份），当前值："{self.backup_strategy}"'
            })
        
        # ========== 性能监控配置验证 ==========
        if self.enable_performance_monitor:
            if self.perf_sample_interval <= 0:
                errors.append({
                    'field': 'perf_sample_interval',
                    'error': f'perf_sample_interval 值 {self.perf_sample_interval} 无效',
                    'check_point': '性能采样间隔',
                    'current_value': f'{self.perf_sample_interval}秒',
                    'requirement': '必须 > 0（推荐值：1.0-5.0 秒）',
                    'solution': f'建议设置为 1.0 秒，当前值：{self.perf_sample_interval}秒'
                })
            
            if self.perf_history_size < 10:
                errors.append({
                    'field': 'perf_history_size',
                    'error': f'perf_history_size 值 {self.perf_history_size} 过小',
                    'check_point': '性能历史记录大小',
                    'current_value': self.perf_history_size,
                    'requirement': '必须 >= 10（推荐值：300-500）',
                    'solution': f'建议设置为 300 以保留足够历史数据，当前值：{self.perf_history_size}'
                })
        
        # ========== 提示词配置验证 ==========
        if not self.draft_prompt or not self.draft_prompt.strip():
            errors.append({
                'field': 'draft_prompt',
                'error': '初译提示词不能为空',
                'check_point': 'Draft Prompt 配置',
                'current_value': '(空)',
                'requirement': '必须包含有效的提示词模板',
                'solution': '必须包含 {target_lang} 占位符和 JSON 输出格式要求'
            })
        elif '{target_lang}' not in self.draft_prompt:
            errors.append({
                'field': 'draft_prompt',
                'error': '初译提示词缺少必需的 {target_lang} 占位符',
                'check_point': 'Prompt 变量占位符检查',
                'current_value': self.draft_prompt[:100] + '...',
                'requirement': '提示词必须包含 {target_lang} 占位符',
                'solution': '在提示词中添加 "Translate to {target_lang}"'
            })
        
        if not self.review_prompt or not self.review_prompt.strip():
            errors.append({
                'field': 'review_prompt',
                'error': '校对提示词不能为空',
                'check_point': 'Review Prompt 配置',
                'current_value': '(空)',
                'requirement': '必须包含有效的提示词模板',
                'solution': '必须包含 {target_lang} 占位符和 Reason 字段要求'
            })
        elif '{target_lang}' not in self.review_prompt:
            errors.append({
                'field': 'review_prompt',
                'error': '校对提示词缺少必需的 {target_lang} 占位符',
                'check_point': 'Prompt 变量占位符检查',
                'current_value': self.review_prompt[:100] + '...',
                'requirement': '提示词必须包含 {target_lang} 占位符',
                'solution': '在提示词中添加 "Polish into {target_lang}"'
            })
        
        # ========== 抛出所有验证错误 ==========
        if errors:
            error_message = self._format_validation_errors(errors)
            raise ValidationError(
                message=f"配置验证失败：共发现 {len(errors)} 个错误",
                field_name='config_validation',
                details={
                    'total_errors': len(errors),
                    'errors': errors,
                    'error_summary': error_message
                }
            )
    
    # ========== 模型配置获取方法 ==========
    
    def get_draft_model_name(self) -> str:
        """获取翻译阶段使用的模型名称"""
        return self.draft_model_name or self.model_name
    
    def get_draft_temperature(self) -> float:
        """获取翻译阶段的 temperature"""
        return self.draft_temperature if self.draft_temperature is not None else self.temperature
    
    def get_draft_top_p(self) -> float:
        """获取翻译阶段的 top_p"""
        return self.draft_top_p if self.draft_top_p is not None else self.top_p
    
    def get_draft_timeout(self) -> int:
        """获取翻译阶段的 timeout"""
        return self.draft_timeout if self.draft_timeout is not None else self.timeout
    
    def get_draft_max_tokens(self) -> int:
        """获取翻译阶段的 max_tokens"""
        return self.draft_max_tokens
    
    def get_review_model_name(self) -> str:
        """获取校对阶段使用的模型名称"""
        return self.review_model_name or self.model_name
    
    def get_review_temperature(self) -> float:
        """获取校对阶段的 temperature"""
        return self.review_temperature if self.review_temperature is not None else self.temperature
    
    def get_review_top_p(self) -> float:
        """获取校对阶段的 top_p"""
        return self.review_top_p if self.review_top_p is not None else self.top_p
    
    def get_review_timeout(self) -> int:
        """获取校对阶段的 timeout"""
        return self.review_timeout if self.review_timeout is not None else self.timeout
    
    def get_review_max_tokens(self) -> int:
        """获取校对阶段的 max_tokens"""
        return self.review_max_tokens
    
    # ========================================================================
    # 多 API 提供商支持方法（新增）
    # ========================================================================
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        获取已配置的 API 提供商（只显示配置了 api_key 的）
        
        Returns:
            包含所有已配置提供商的字典，键为提供商名称，值为配置信息
        """
        if not self.api_providers:
            # 如果没有配置多提供商，返回当前单个提供商
            if self.api_key and self.api_key.strip():
                return {
                    self.api_provider: {
                        'api_key': self.api_key,
                        'base_url': self.base_url,
                        'model_name': self.model_name,
                        'models': [self.model_name]
                    }
                }
            return {}
        
        # 过滤出配置了 api_key 的提供商
        available = {}
        for provider_name, provider_config in self.api_providers.items():
            api_key = provider_config.get('api_key', '')
            if api_key and api_key.strip():
                available[provider_name] = provider_config
        
        return available
    
    def get_provider_models(self, provider_name: str) -> List[str]:
        """
        获取指定提供商的所有可用模型
        
        Args:
            provider_name: 提供商名称
            
        Returns:
            模型名称列表
        """
        providers = self.get_available_providers()
        if provider_name not in providers:
            return []
        
        provider_config = providers[provider_name]
        models = provider_config.get('models', [])
        
        if models:
            return models
        
        # 如果没有配置 models 列表，使用 model_name
        model_name = provider_config.get('model_name', '')
        if model_name:
            return [model_name]
        
        return []
    
    def switch_provider(self, provider_name: str) -> bool:
        """
        切换到指定的 API 提供商
        
        Args:
            provider_name: 提供商名称
            
        Returns:
            是否切换成功
        """
        providers = self.get_available_providers()
        if provider_name not in providers:
            return False
        
        provider_config = providers[provider_name]
        self.api_provider = provider_name
        self.api_key = provider_config.get('api_key', '')
        self.base_url = provider_config.get('base_url', '')
        self.model_name = provider_config.get('model_name', '')
        
        self.log_info(f"切换到 API 提供商：{provider_name}", model=self.model_name)
        return True


@dataclass
class TaskContext:
    """任务上下文，存储单个翻译任务的所有信息"""
    idx: int
    key: str
    source_text: str
    source_lang: str = "中文"  # 新增：源语言
    original_trans: str = ""
    target_lang: str = "英语"
    tm_suggestion: Optional[Dict[str, Any]] = None
    is_exact_hit: bool = False
    
    def __post_init__(self):
        """验证任务上下文的有效性"""
        if not self.key:
            raise ValidationError(
                "TaskContext 的 key 不能为空",
                field_name='key'
            )
        if not self.source_text:
            raise ValidationError(
                "TaskContext 的 source_text 不能为空",
                field_name='source_text'
            )


@dataclass
class StageResult:
    """阶段执行结果 - 支持双阶段翻译"""
    success: bool
    translation: str
    error_msg: Optional[str] = None
    reason: str = ""  # 校对原因（如果有修改）
    source: str = ""  # 源文本
    diagnosis: str = ""  # 诊断信息

    def __post_init__(self):
        """验证阶段结果的有效性"""
        if self.success and not self.translation:
            raise ValidationError(
                "成功时 translation 不能为空字符串",
                field_name='translation'
            )


@dataclass
class FinalResult:
    """最终翻译结果 - 精简版"""
    key: str
    target_lang: str
    source_text: str
    final_trans: str
    status: str
    error_detail: Optional[str] = None
