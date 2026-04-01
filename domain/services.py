"""
领域服务层
定义核心业务逻辑和服务接口
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models import TranslationTask, TranslationResult, TermMatch, BatchResult


class ITerminologyDomainService(ABC):
    """术语领域服务接口"""
    
    @abstractmethod
    async def find_match(self, source_text: str, target_lang: str) -> Optional[TermMatch]:
        """
        查找术语匹配
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            
        Returns:
            术语匹配结果
        """
        pass
    
    @abstractmethod
    async def save_term(self, source_text: str, target_lang: str, translation: str):
        """
        保存术语
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            translation: 翻译结果
        """
        pass


class ITranslationDomainService(ABC):
    """翻译领域服务接口"""
    
    @abstractmethod
    async def translate(self, task: TranslationTask) -> TranslationResult:
        """
        执行翻译
        
        Args:
            task: 翻译任务
            
        Returns:
            翻译结果
        """
        pass
    
    @abstractmethod
    async def proofread(self, task: TranslationTask, draft: str) -> TranslationResult:
        """
        校对翻译
        
        Args:
            task: 翻译任务
            draft: 初译结果
            
        Returns:
            校对结果
        """
        pass


class IBatchProcessor(ABC):
    """批量处理器接口"""
    
    @abstractmethod
    async def process_batch(self, tasks: List[TranslationTask]) -> BatchResult:
        """
        批量处理任务
        
        Args:
            tasks: 任务列表
            
        Returns:
            批量结果
        """
        pass
