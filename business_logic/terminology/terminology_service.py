"""
术语服务实现
整合缓存层和查询层，提供完整的术语管理功能
"""
import asyncio
from typing import Optional, Dict, Any
from business_logic.terminology import (
    ITerminologyService,
    ITerminologyCache,
    ITerminologyQuery
)


class TerminologyService(ITerminologyService):
    """术语服务实现 - 组合模式"""
    
    def __init__(self, 
                 cache: ITerminologyCache,
                 query: ITerminologyQuery):
        """
        初始化术语服务
        
        Args:
            cache: 缓存层
            query: 查询层
        """
        self.cache = cache
        self.query = query
    
    async def find_term(self, source_text: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """查找术语翻译（优先精确匹配）"""
        cache_key = f"{source_text}:{target_lang}"
        
        # 1. 查缓存
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # 2. 优先精确匹配
        result = await self.query.exact_match(source_text, target_lang)
        if result:
            # 精确命中，写入缓存
            await self.cache.set(cache_key, result)
            return result
        
        # 3. 模糊匹配
        result = await self.query.fuzzy_match(source_text, target_lang)
        if result:
            # 模糊命中，写入缓存（TTL 较短）
            await self.cache.set(cache_key, result)
            return result
        
        return None
    
    async def add_term(self, source_text: str, target_lang: str, translation: str):
        """添加术语"""
        # 由数据访问层负责实际写入
        # 这里只负责缓存失效
        cache_key = f"{source_text}:{target_lang}"
        await self.cache.invalidate(cache_key)
    
    async def shutdown(self):
        """关闭服务"""
        # 清理资源
        pass
