"""
术语缓存层
实现术语查询的缓存逻辑，支持多级缓存
"""
import asyncio
from typing import Optional, Dict, Any
from business_logic.terminology import ITerminologyCache
from infrastructure.cache import TerminologyCache
from infrastructure.unified_cache import UnifiedCacheManager


class TerminologyCacheAdapter(ITerminologyCache):
    """术语缓存适配器 - 整合 LRU 和统一缓存"""
    
    def __init__(self, 
                 lru_cache: TerminologyCache,
                 unified_cache: Optional[UnifiedCacheManager] = None,
                 datasource: str = "terminology"):
        self.lru_cache = lru_cache
        self.unified_cache = unified_cache
        self.datasource = datasource
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存（优先统一缓存）"""
        # 先查统一缓存
        if self.unified_cache:
            try:
                result = await self.unified_cache.get(self.datasource, key)
                if result:
                    return result
            except Exception:
                pass
        
        # 再查 LRU 缓存
        parts = key.split(':')
        if len(parts) == 2:
            src, lang = parts
            return await self.lru_cache.get_exact_match(src, lang)
        
        return None
    
    async def set(self, key: str, value: Any):
        """设置缓存（同时写入两级缓存）"""
        parts = key.split(':')
        if len(parts) == 2:
            src, lang = parts
            
            # 写入 LRU 缓存
            await self.lru_cache.set_exact_match(src, lang, value)
            
            # 写入统一缓存
            if self.unified_cache:
                try:
                    await self.unified_cache.set(self.datasource, key, value)
                except Exception:
                    pass
    
    async def invalidate(self, key: str):
        """使缓存失效"""
        parts = key.split(':')
        if len(parts) == 2:
            src, lang = parts
            
            # LRU 缓存失效
            await self.lru_cache.invalidate_source(src)
            
            # 统一缓存失效
            if self.unified_cache:
                try:
                    await self.unified_cache.delete(self.datasource, key)
                except Exception:
                    pass
