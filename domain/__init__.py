"""
领域层 (Domain Layer)
核心业务逻辑，纯 Python 对象，无外部依赖
"""

from .services import ITerminologyDomainService, ITranslationDomainService
from .models import TranslationTask, TranslationResult, TranslationStatus, TermMatch
from .terminology_service_impl import TerminologyDomainService
from .translation_service_impl import TranslationDomainServiceImpl
from .cache_decorators import CachedTerminologyService

__all__ = [
    # 接口
    'ITerminologyDomainService',
    'ITranslationDomainService',
    
    # 模型
    'TranslationTask',
    'TranslationResult',
    'TranslationStatus',
    'TermMatch',
    
    # 实现
    'TerminologyDomainService',
    'TranslationDomainServiceImpl',
    
    # 缓存装饰器
    'CachedTerminologyService',
]
