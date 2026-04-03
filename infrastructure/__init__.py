"""
基础设施层 - 提供缓存、日志、数据库、配置、模型、DI容器等基础功能

重构后按职责划分为以下子模块：
- cache: 缓存相关
- logging: 日志相关
- database: 数据库相关
- utils: 工具类
- models: 数据模型
- di: DI容器
- config: 配置管理
"""

# 从各子模块导入常用功能
from .models import Config, TaskContext, StageResult, FinalResult
from .logging import setup_logger
from .utils import AdaptiveConcurrencyController

__all__ = [
    'Config', 'TaskContext', 'StageResult', 'FinalResult',
    'setup_logger', 'AdaptiveConcurrencyController'
]
