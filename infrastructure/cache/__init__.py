"""
缓存模块 - 提供术语缓存和统一缓存功能
"""
from .cache import TerminologyCache, LRUCache, CacheEntry
from .unified_cache import UnifiedCacheManager
# 缓存装饰器已移至 domain 层
from domain.cache_decorators import CachedTerminologyService, CachedTranslationService

__all__ = [
    'TerminologyCache',
    'LRUCache',
    'CacheEntry',
    'UnifiedCacheManager',
    'CachedTerminologyService',
    'CachedTranslationService'
]
