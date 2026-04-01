"""
术语服务接口
定义术语管理的抽象接口，降低模块耦合
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class ITerminologyService(ABC):
    """术语服务接口"""
    
    @abstractmethod
    async def find_term(self, source_text: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """
        查找术语翻译
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            
        Returns:
            术语翻译结果，包含 original, translation, score
        """
        pass
    
    @abstractmethod
    async def add_term(self, source_text: str, target_lang: str, translation: str):
        """
        添加术语
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            translation: 翻译结果
        """
        pass
    
    @abstractmethod
    async def shutdown(self):
        """关闭服务"""
        pass


class ITerminologyCache(ABC):
    """术语缓存接口"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any):
        """设置缓存"""
        pass
    
    @abstractmethod
    async def invalidate(self, key: str):
        """使缓存失效"""
        pass


class ITerminologyQuery(ABC):
    """术语查询接口"""
    
    @abstractmethod
    async def exact_match(self, source_text: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """
        精确匹配
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            
        Returns:
            匹配结果
        """
        pass
    
    @abstractmethod
    async def fuzzy_match(self, source_text: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """
        模糊匹配
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            
        Returns:
            匹配结果
        """
        pass
