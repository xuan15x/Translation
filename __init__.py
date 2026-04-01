"""
AI 智能翻译系统 - 六层分层架构 v3.0

六层架构:
- presentation/      : 表示层 (GUI/CLI)
- application/       : 应用层 (流程编排/外观模式)
- domain/           : 领域层 (核心业务逻辑)
- service/          : 服务层 (API 集成)
- data_access/      : 数据访问层 (仓储/持久化)
- infrastructure/   : 基础设施层 (DI/日志/工具)
- config/           : 配置管理
"""

# 配置常量
from config import (
    DEFAULT_DRAFT_PROMPT,
    DEFAULT_REVIEW_PROMPT,
    TARGET_LANGUAGES,
    GUI_CONFIG
)

# 核心类
from infrastructure import (
    Config,
    setup_logger, AdaptiveConcurrencyController
)

# 日志配置
from infrastructure.log_config import (
    LogManager, get_log_manager, LogConfig,
    LogLevel, LogGranularity, LogTag, log_with_tag,
    get_logger
)

# 应用层（新架构）
from application import (
    TranslationServiceFacade,
    TranslationWorkflowCoordinator,
    BatchTaskProcessor
)

# 领域层（新架构）
from domain import (
    TerminologyDomainService,
    TranslationDomainServiceImpl
)

# 服务层
from service import (
    get_provider_manager, get_history_manager
)

# 数据访问
from data_access import ConfigPersistence

# 表示层
from presentation import TranslationApp

__version__ = '3.0'
__author__ = 'Translation Team'

__all__ = [
    # 配置
    'DEFAULT_DRAFT_PROMPT', 'DEFAULT_REVIEW_PROMPT',
    'TARGET_LANGUAGES', 'GUI_CONFIG',
    
    # 核心
    'Config',
    'setup_logger', 'get_logger',
    
    # 日志
    'LogManager', 'get_log_manager', 'LogConfig',
    'LogLevel', 'LogGranularity', 'LogTag', 'log_with_tag',
    
    # 应用层（新架构）
    'TranslationServiceFacade',
    'TranslationWorkflowCoordinator',
    'BatchTaskProcessor',
    
    # 领域层（新架构）
    'TerminologyDomainService',
    'TranslationDomainServiceImpl',
    
    # 服务层
    'get_provider_manager', 'get_history_manager',
    
    # 数据访问
    'ConfigPersistence',
    
    # GUI
    'TranslationApp'
]
