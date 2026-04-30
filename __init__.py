"""
AI 智能翻译系统 - 六层分层架构 v3.2
基于 DeepSeek 大模型的游戏本地化翻译工具

六层架构:
- presentation/      : 表示层 (GUI/CLI)
- application/       : 应用层 (流程编排/外观模式)
- domain/           : 领域层 (核心业务逻辑)
- service/          : 服务层 (DeepSeek API 集成)
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
from infrastructure.models.models import Config
from infrastructure.logging import setup_logger
from infrastructure.utils.concurrency_controller import AdaptiveConcurrencyController

# 应用层
from application import (
    TranslationServiceFacade,
    TranslationWorkflowCoordinator,
    BatchTaskProcessor
)

# 领域层
from domain import (
    TerminologyDomainService,
    TranslationDomainServiceImpl
)

# 服务层（DeepSeek）
from service import get_provider_manager, get_history_manager

# 数据访问
from data_access import ConfigPersistence

# 表示层
from presentation import TranslationApp

__version__ = '3.2.1'
__author__ = 'Translation Team'

__all__ = [
    # 配置
    'DEFAULT_DRAFT_PROMPT', 'DEFAULT_REVIEW_PROMPT',
    'TARGET_LANGUAGES', 'GUI_CONFIG',

    # 核心
    'Config', 'setup_logger',
    'AdaptiveConcurrencyController',

    # 应用层
    'TranslationServiceFacade',
    'TranslationWorkflowCoordinator',
    'BatchTaskProcessor',

    # 领域层
    'TerminologyDomainService',
    'TranslationDomainServiceImpl',

    # 服务层
    'get_provider_manager', 'get_history_manager',

    # 数据访问
    'ConfigPersistence',

    # GUI
    'TranslationApp'
]
