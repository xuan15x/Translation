"""
AI 智能翻译系统 - 模块化架构

五层架构:
- presentation/      : 表示层 (GUI)
- business_logic/    : 业务逻辑层 (流程编排)
- service/          : 服务层 (API/历史)
- data_access/      : 数据访问层 (持久化)
- infrastructure/   : 基础设施层 (模型/工具)
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
    Config, TaskContext, StageResult, FinalResult,
    setup_logger, AdaptiveConcurrencyController
)

# 日志配置
from infrastructure.log_config import (
    LogManager, get_log_manager, LogConfig,
    LogLevel, LogGranularity, LogTag, log_with_tag,
    get_logger
)

# 业务层
from business_logic import (
    WorkflowOrchestrator, TerminologyManager
)

# 服务层
from service import (
    get_provider_manager, get_history_manager
)

# 数据访问
from data_access import ConfigPersistence

# 表示层
from presentation import TranslationApp

__version__ = '2.0'
__author__ = 'Translation Team'

__all__ = [
    # 配置
    'DEFAULT_DRAFT_PROMPT', 'DEFAULT_REVIEW_PROMPT',
    'TARGET_LANGUAGES', 'GUI_CONFIG',
    
    # 核心
    'Config', 'TaskContext', 'StageResult', 'FinalResult',
    'setup_logger', 'get_logger',
    
    # 日志
    'LogManager', 'get_log_manager', 'LogConfig',
    'LogLevel', 'LogGranularity', 'LogTag', 'log_with_tag',
    
    # 业务
    'WorkflowOrchestrator', 'TerminologyManager',
    
    # 服务
    'get_provider_manager', 'get_history_manager',
    
    # 数据
    'ConfigPersistence',
    
    # GUI
    'TranslationApp'
]
