"""
模型模块 - 定义基础设施层的数据模型
"""
from .config import Config
from .context import TaskContext, StageResult, FinalResult

__all__ = [
    'Config',
    'TaskContext',
    'StageResult',
    'FinalResult',
]
