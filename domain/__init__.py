"""
领域层 (Domain Layer)
核心业务逻辑，纯 Python 对象，无外部依赖

注意：为了避免循环导入，使用延迟加载机制。
"""
from typing import TYPE_CHECKING

# 基础模型导入（无依赖）
from .models import TranslationTask, TranslationResult, TranslationStatus, TermMatch

# 延迟导入服务（避免在初始化时触发循环）
def __getattr__(name):
    if name == 'ITerminologyDomainService':
        from .services import ITerminologyDomainService
        return ITerminologyDomainService
    elif name == 'ITranslationDomainService':
        from .services import ITranslationDomainService
        return ITranslationDomainService
    elif name == 'ITermRepository':
        from .services import ITermRepository
        return ITermRepository
    elif name == 'TerminologyDomainService':
        from .terminology_service_impl import TerminologyDomainService
        return TerminologyDomainService
    elif name == 'TranslationDomainServiceImpl':
        from .translation_service_impl import TranslationDomainServiceImpl
        return TranslationDomainServiceImpl
    elif name == 'CachedTerminologyService':
        from .cache_decorators import CachedTerminologyService
        return CachedTerminologyService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # 接口（延迟导入）
    'ITerminologyDomainService',
    'ITranslationDomainService',
    'ITermRepository',

    # 模型
    'TranslationTask',
    'TranslationResult',
    'TranslationStatus',
    'TermMatch',

    # 实现（延迟导入）
    'TerminologyDomainService',
    'TranslationDomainServiceImpl',

    # 缓存装饰器（延迟导入）
    'CachedTerminologyService',
]
