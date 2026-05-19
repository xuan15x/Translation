"""
数据模型 - 配置模块
Config 数据类，存储所有系统配置参数
仅支持 DeepSeek 模型
"""
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from infrastructure.logging import ModuleLoggerMixin, LogCategory, LoggerSlice
from config.constants import (
    APIConfig, ConcurrencyConfig, CacheConfig, TerminologyConfig,
    WorkflowConfig, LogConfig, PerformanceMonitorConfig,
    BackupConfig, LanguageConfig, VersionConfig
)
from ..exceptions import AuthenticationError

# 默认提示词
DEFAULT_DRAFT_PROMPT = """Role: Professional Translator.
Task: Translate 'Src' to {target_lang}.
Constraints:
1. Output JSON ONLY: {"Trans": "string"}.
2. Strictly follow provided TM.
3. Accurate and direct."""

DEFAULT_REVIEW_PROMPT = """Role: Senior Language Editor.
Task: Polish 'Draft' into native {target_lang}.
Constraints:
1. Output JSON ONLY: {"Trans": "string", "Reason": "string"}.
2. 'Reason': Max 10 chars. If no change, Reason="".
3. Focus on flow and tone."""


@dataclass
class Config(ModuleLoggerMixin):
    """配置类，存储所有系统和 API 参数 - 仅支持 DeepSeek"""
    LOG_CATEGORY: LogCategory = LogCategory.MODEL

    # ========== API 基础配置（仅 DeepSeek） ==========
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    api_provider: str = "deepseek"

    # ========== DeepSeek 模型配置 ==========
    model_name: str = "deepseek-chat"
    temperature: float = APIConfig.DEFAULT_TEMPERATURE
    top_p: float = APIConfig.DEFAULT_TOP_P
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stop: Optional[List[str]] = None

    # 高级参数
    timeout: int = APIConfig.DEFAULT_TIMEOUT
    max_retries: int = APIConfig.DEFAULT_MAX_RETRIES
    retry_streak_threshold: int = ConcurrencyConfig.DEFAULT_RETRY_STREAK_THRESHOLD
    base_retry_delay: float = APIConfig.DEFAULT_RETRY_DELAY
    max_tokens: int = APIConfig.DEFAULT_MAX_TOKENS
    context_window_size: Optional[int] = None
    enable_cache_control: bool = True
    enable_stream: bool = False
    custom_headers: Dict[str, str] = field(default_factory=dict)
    extra_body: Dict[str, Any] = field(default_factory=dict)

    # ========== 双阶段翻译专用配置 ==========
    draft_model_name: Optional[str] = None
    draft_temperature: Optional[float] = None
    draft_top_p: Optional[float] = None
    draft_presence_penalty: Optional[float] = None
    draft_frequency_penalty: Optional[float] = None
    draft_timeout: Optional[int] = None
    draft_max_tokens: int = APIConfig.DEFAULT_MAX_TOKENS

    review_model_name: Optional[str] = None
    review_temperature: Optional[float] = None
    review_top_p: Optional[float] = None
    review_presence_penalty: Optional[float] = None
    review_frequency_penalty: Optional[float] = None
    review_timeout: Optional[int] = None
    review_max_tokens: int = APIConfig.DEFAULT_MAX_TOKENS

    # ========== 数据存储路径 ==========
    db_path: str = ""  # 术语库数据库路径，空字符串表示自动检测

    # ========== 并发控制 ==========
    initial_concurrency: int = ConcurrencyConfig.DEFAULT_INITIAL_CONCURRENCY
    max_concurrency: int = ConcurrencyConfig.DEFAULT_MAX_CONCURRENCY
    concurrency_cooldown_seconds: float = ConcurrencyConfig.DEFAULT_COOLDOWN_SECONDS

    # ========== 工作流配置 ==========
    enable_two_pass: bool = WorkflowConfig.DEFAULT_ENABLE_TWO_PASS
    skip_review_if_local_hit: bool = WorkflowConfig.DEFAULT_SKIP_REVIEW_IF_LOCAL_HIT
    batch_size: int = WorkflowConfig.DEFAULT_BATCH_SIZE
    gc_interval: int = WorkflowConfig.DEFAULT_GC_INTERVAL
    translation_mode: str = "full"
    enabled_translation_types: List[str] = field(default_factory=list)

    # ========== 术语库配置 ==========
    similarity_low: int = TerminologyConfig.DEFAULT_SIMILARITY_LOW
    exact_match_score: int = TerminologyConfig.DEFAULT_EXACT_MATCH_SCORE
    multiprocess_threshold: int = TerminologyConfig.DEFAULT_MULTIPROCESS_THRESHOLD
    prohibition_config: Dict[str, Any] = field(default_factory=dict)
    prohibition_type_map: Dict[str, Any] = field(default_factory=dict)

    # ========== 性能配置 ==========
    pool_size: int = CacheConfig.DEFAULT_POOL_SIZE
    cache_capacity: int = CacheConfig.DEFAULT_CACHE_CAPACITY
    cache_ttl_seconds: int = CacheConfig.DEFAULT_CACHE_TTL_SECONDS

    # ========== 日志配置 ==========
    log_level: str = LogConfig.DEFAULT_LOG_LEVEL
    log_granularity: str = LogConfig.DEFAULT_LOG_GRANULARITY
    log_max_lines: int = LogConfig.DEFAULT_LOG_MAX_LINES

    # ========== 提示词配置 ==========
    draft_prompt: str = DEFAULT_DRAFT_PROMPT
    review_prompt: str = DEFAULT_REVIEW_PROMPT
    prompt_templates: Dict[str, str] = field(default_factory=dict)

    # ========== 语言配置 ==========
    default_source_lang: str = LanguageConfig.DEFAULT_SOURCE_LANG
    supported_source_langs: List[str] = field(default_factory=lambda: LanguageConfig.DEFAULT_SUPPORTED_SOURCE_LANGS)
    favorite_languages: List[str] = field(default_factory=list)

    # ========== 版本控制和备份 ==========
    enable_version_control: bool = VersionConfig.DEFAULT_ENABLE_VERSION_CONTROL
    enable_auto_backup: bool = VersionConfig.DEFAULT_ENABLE_AUTO_BACKUP
    backup_dir: str = BackupConfig.DEFAULT_BACKUP_DIR
    backup_strategy: str = BackupConfig.DEFAULT_BACKUP_STRATEGY

    # ========== 性能监控 ==========
    enable_performance_monitor: bool = PerformanceMonitorConfig.DEFAULT_ENABLE
    perf_sample_interval: float = PerformanceMonitorConfig.DEFAULT_SAMPLE_INTERVAL
    perf_history_size: int = PerformanceMonitorConfig.DEFAULT_HISTORY_SIZE

    # ========== 思考模式（DeepSeek v4 专用） ==========
    enable_thinking_mode: bool = False
    thinking_effort: str = "high"

    def __post_init__(self):
        """初始化后验证"""
        from .config_validators import validate_config_post_init
        validate_config_post_init(self)

    # ========================================================================
    # Draft 阶段参数获取方法
    # ========================================================================

    def get_draft_model_name(self) -> str:
        return self.draft_model_name or self.model_name

    def get_draft_temperature(self) -> float:
        return self.draft_temperature if self.draft_temperature is not None else self.temperature

    def get_draft_top_p(self) -> float:
        return self.draft_top_p if self.draft_top_p is not None else self.top_p

    def get_draft_timeout(self) -> int:
        return self.draft_timeout if self.draft_timeout is not None else self.timeout

    def get_draft_max_tokens(self) -> int:
        return self.draft_max_tokens

    # ========================================================================
    # Review 阶段参数获取方法
    # ========================================================================

    def get_review_model_name(self) -> str:
        return self.review_model_name or self.model_name

    def get_review_temperature(self) -> float:
        return self.review_temperature if self.review_temperature is not None else self.temperature

    def get_review_top_p(self) -> float:
        return self.review_top_p if self.review_top_p is not None else self.top_p

    def get_review_timeout(self) -> int:
        return self.review_timeout if self.review_timeout is not None else self.timeout

    def get_review_max_tokens(self) -> int:
        return self.review_max_tokens

    # ========================================================================
    # API 配置方法（仅 DeepSeek）
    # ========================================================================

    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        if self.api_key and self.api_key.strip():
            return {
                "deepseek": {
                    'api_key': self.api_key,
                    'base_url': self.base_url,
                    'model_name': self.model_name,
                }
            }
        return {}

    def get_provider_models(self, provider_name: str = "deepseek") -> List[str]:
        if provider_name == "deepseek":
            return [self.model_name] if self.model_name else ["deepseek-chat"]
        return []

    def switch_provider(self, provider_name: str) -> bool:
        if provider_name != "deepseek":
            self.log_warning(f"仅支持 DeepSeek，忽略切换请求: {provider_name}")
            return False
        self.log_info("使用 DeepSeek API")
        return True
