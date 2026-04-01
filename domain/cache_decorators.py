"""
缓存装饰器
为领域服务添加缓存功能，提升性能
"""
import asyncio
from typing import Optional, Any
from domain.services import ITerminologyDomainService, ITranslationDomainService
from domain.models import TermMatch, TranslationTask, TranslationResult


class CachedTerminologyService(ITerminologyDomainService):
    """带缓存的术语服务装饰器"""
    
    def __init__(self, 
                 service: ITerminologyDomainService,
                 cache_manager=None,
                 datasource: str = "terminology",
                 ttl: int = 3600):
        """
        初始化缓存装饰器
        
        Args:
            service: 被装饰的术语服务
            cache_manager: 缓存管理器（可选）
            datasource: 数据源名称
            ttl: 缓存过期时间（秒）
        """
        self.service = service
        self.cache_manager = cache_manager
        self.datasource = datasource
        self.ttl = ttl
        
        # 本地内存缓存作为后备
        self._local_cache = {}
    
    async def find_match(self, source_text: str, target_lang: str) -> Optional[TermMatch]:
        """查找术语匹配（带缓存）"""
        cache_key = f"{source_text}:{target_lang}"
        
        # 1. 尝试从缓存获取
        if self.cache_manager:
            try:
                cached = await self.cache_manager.get(self.datasource, cache_key)
                if cached:
                    return TermMatch.from_dict(cached)
            except Exception:
                pass
        
        # 2. 尝试本地缓存
        if cache_key in self._local_cache:
            cached_data, _ = self._local_cache[cache_key]
            return cached_data
        
        # 3. 查询服务
        result = await self.service.find_match(source_text, target_lang)
        
        # 4. 写入缓存
        if result:
            # 写入远程缓存
            if self.cache_manager:
                try:
                    await self.cache_manager.set(
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
                except Exception:
                    pass
            
            # 写入本地缓存
            self._local_cache[cache_key] = (result, asyncio.get_event_loop().time())
        
        return result
    
    async def save_term(self, source_text: str, target_lang: str, translation: str):
        """保存术语（同时使缓存失效）"""
        # 调用底层服务
        await self.service.save_term(source_text, target_lang, translation)
        
        # 使缓存失效
        cache_key = f"{source_text}:{target_lang}"
        
        if self.cache_manager:
            try:
                await self.cache_manager.delete(self.datasource, cache_key)
            except Exception:
                pass
        
        # 清除本地缓存
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
