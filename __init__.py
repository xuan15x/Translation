"""
AI 智能翻译系统 — 黑盒 CLI 模式 v3.3
基于 DeepSeek 大模型的游戏本地化翻译工具

五层架构:
- application/       : 应用层 (流程编排/外观模式)
- domain/           : 领域层 (核心业务逻辑)
- service/          : 服务层 (DeepSeek API 集成)
- data_access/      : 数据访问层 (仓储/持久化)
- infrastructure/   : 基础设施层 (DI/日志/工具)
- config/           : 配置管理

启动方式: python run.py
"""

# 配置常量
from config import (
    DEFAULT_DRAFT_PROMPT,
    DEFAULT_REVIEW_PROMPT,
    TARGET_LANGUAGES
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
from service import get_history_manager

# 数据访问
from data_access import ConfigPersistence

__version__ = '3.3.0'
__author__ = 'Translation Team'

__all__ = [
    # 配置
    'DEFAULT_DRAFT_PROMPT', 'DEFAULT_REVIEW_PROMPT',
    'TARGET_LANGUAGES',

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
    'get_history_manager',

    # 数据访问
    'ConfigPersistence',
]
