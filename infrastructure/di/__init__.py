"""
DI容器模块 - 提供依赖注入功能
"""
from .di_container import DependencyContainer, initialize_container

__all__ = [
    'DependencyContainer',
    'initialize_container'
]
