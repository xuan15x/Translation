"""
缓存装饰器
为领域服务添加缓存功能，提升性能
"""
import asyncio
import logging
from typing import Optional, Any
from domain.services import ITerminologyDomainService, ITranslationDomainService
from domain.models import TermMatch, TranslationTask, TranslationResult

logger = logging.getLogger(__name__)


class CachedTerminologyService(ITerminologyDomainService):
    """带缓存的术语服务装饰器 - 优化版"""
    
    def __init__(self, 
                 service: ITerminologyDomainService,
                 cache_manager=None,
                 datasource: str = "terminology",
                 ttl: int = 3600,
                 local_cache_size: int = 1000):
        """
        初始化缓存装饰器
        
        Args:
            service: 被装饰的术语服务
            cache_manager: 缓存管理器（可选）
            datasource: 数据源名称
            ttl: 缓存过期时间（秒）
            local_cache_size: 本地缓存大小限制
        """
        self.service = service
        self.cache_manager = cache_manager
        self.datasource = datasource
        self.ttl = ttl
        
        # 优化的本地缓存 - 使用 OrderedDict 实现 LRU
        from collections import OrderedDict
        self._local_cache = OrderedDict()
        self._local_cache_size = local_cache_size
    
    def _get_from_local_cache(self, key: str) -> Optional[TermMatch]:
        """从本地缓存获取（LRU 优化）"""
        if key in self._local_cache:
            # 移动到末尾（最近使用）
            self._local_cache.move_to_end(key)
            return self._local_cache[key]
        return None
    
    def _add_to_local_cache(self, key: str, value: TermMatch):
        """添加到本地缓存（LRU 淘汰）"""
        if key in self._local_cache:
            self._local_cache.move_to_end(key)
        else:
            if len(self._local_cache) >= self._local_cache_size:
                # 淘汰最旧的
                self._local_cache.popitem(last=False)
        self._local_cache[key] = value
    
    async def find_match(self, source_text: str, target_lang: str) -> Optional[TermMatch]:
        """查找术语匹配（带三级缓存）"""
        cache_key = f"{source_text}:{target_lang}"
        
        # 1. 尝试本地缓存（最快）
        cached = self._get_from_local_cache(cache_key)
        if cached:
            return cached
        
        # 2. 尝试远程缓存
        if self.cache_manager:
            try:
                cached = await self.cache_manager.get(self.datasource, cache_key)
                if cached:
                    result = TermMatch.from_dict(cached)
                    # 写入本地缓存
                    self._add_to_local_cache(cache_key, result)
                    return result
            except Exception as e:
                logger.debug(f"缓存查询失败，回退到服务调用: {e}")
        
        # 3. 查询服务
        result = await self.service.find_match(source_text, target_lang)
        
        # 4. 写入缓存
        if result:
            # 写入远程缓存（不等待）
            if self.cache_manager:
                asyncio.create_task(
                    self.cache_manager.set(
                        self.datasource,
                        cache_key,
                        result.to_dict() if hasattr(result, 'to_dict') else {
                            'original': result.original,
                            'translation': result.translation,
                            'score': result.score,
                            'match_type': result.match_type.value,
                            'target_lang': result.target_lang
                        },
                        ttl=self.ttl
                    )
                )
            
            # 写入本地缓存
            self._add_to_local_cache(cache_key, result)
        
        return result
    
    async def find_matches_batch(self, queries: List[tuple]) -> List[Optional[TermMatch]]:
        """批量查找（优化：先查缓存，再批量查询）"""
        results = []
        uncached_queries = []
        uncached_indices = []
        
        # 1. 先检查本地缓存
        for i, (source_text, target_lang) in enumerate(queries):
            cache_key = f"{source_text}:{target_lang}"
            cached = self._get_from_local_cache(cache_key)
            
            if cached:
                results.append(cached)
            else:
                results.append(None)
                uncached_queries.append((source_text, target_lang))
                uncached_indices.append(i)
        
        # 2. 批量查询未命中的
        if uncached_queries and hasattr(self.service, 'find_matches_batch'):
            batch_results = await self.service.find_matches_batch(uncached_queries)
            
            # 填充结果并缓存
            for idx, result in zip(uncached_indices, batch_results):
                results[idx] = result
                if result:
                    source_text, target_lang = uncached_queries[idx - len(results)]
                    cache_key = f"{source_text}:{target_lang}"
                    self._add_to_local_cache(cache_key, result)
        else:
            # 降级为单次查询
            for i, (source_text, target_lang) in zip(uncached_indices, uncached_queries):
                result = await self.service.find_match(source_text, target_lang)
                results[i] = result
                if result:
                    self._add_to_local_cache(f"{source_text}:{target_lang}", result)
        
        return results
    
    async def save_term(self, source_text: str, target_lang: str, translation: str):
        """保存术语（同时使缓存失效）"""
        # 调用底层服务
        await self.service.save_term(source_text, target_lang, translation)
        
        # 使缓存失效
        cache_key = f"{source_text}:{target_lang}"
        
        # 清除本地缓存
        if cache_key in self._local_cache:
            del self._local_cache[cache_key]
        
        # 清除远程缓存
        if self.cache_manager:
            asyncio.create_task(self.cache_manager.delete(self.datasource, cache_key))
    
    async def save_terms_batch(self, terms: List[tuple]):
        """批量保存术语（优化：批量操作）"""
        # 调用底层服务
        if hasattr(self.service, 'save_terms_batch'):
            await self.service.save_terms_batch(terms)
        else:
            # 降级为逐个保存
            for source_text, target_lang, translation in terms:
                await self.service.save_term(source_text, target_lang, translation)
        
        # 批量清除缓存
        for source_text, target_lang, _ in terms:
            cache_key = f"{source_text}:{target_lang}"
            if cache_key in self._local_cache:
                del self._local_cache[cache_key]


class CachedTranslationService(ITranslationDomainService):
    """带缓存的翻译服务装饰器（可选功能）"""
    
    def __init__(self, 
                 service: ITranslationDomainService,
                 cache_manager=None,
                 datasource: str = "translation",
                 ttl: int = 7200):
        """
        初始化缓存装饰器
        
        Args:
            service: 被装饰的翻译服务
            cache_manager: 缓存管理器
            datasource: 数据源名称
            ttl: 缓存过期时间（秒）
        """
        self.service = service
        self.cache_manager = cache_manager
        self.datasource = datasource
        self.ttl = ttl
        self._local_cache = {}
    
    async def translate(self, task: TranslationTask) -> TranslationResult:
        """翻译（带缓存）"""
        cache_key = f"translate:{task.source_text}:{task.target_lang}"
        
        # 尝试缓存
        if cache_key in self._local_cache:
            cached_time = self._local_cache[cache_key][1]
            # 检查是否过期（简单实现）
            if asyncio.get_event_loop().time() - cached_time < self.ttl:
                return self._local_cache[cache_key][0]
        
        # 执行翻译
        result = await self.service.translate(task)
        
        # 写入缓存
        if result.success:
            self._local_cache[cache_key] = (result, asyncio.get_event_loop().time())
        
        return result
    
    async def proofread(self, task: TranslationTask, draft: str) -> TranslationResult:
        """校对（通常不缓存）"""
        return await self.service.proofread(task, draft)
