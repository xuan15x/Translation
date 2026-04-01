"""
仓储层/数据访问接口
定义数据访问的抽象接口，隔离业务逻辑与具体实现
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from domain.models import TermMatch


class ITermRepository(ABC):
    """术语仓储接口"""
    
    @abstractmethod
    async def find_by_source(self, source_text: str, target_lang: str) -> Optional[TermMatch]:
        """
        根据源文本查找术语
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            
        Returns:
            术语匹配结果
        """
        pass
    
    @abstractmethod
    async def save(self, source_text: str, target_lang: str, translation: str) -> bool:
        """
        保存术语
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            translation: 翻译结果
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    async def get_all_terms(self) -> List[Dict[str, Any]]:
        """
        获取所有术语
        
        Returns:
            术语列表
        """
        pass


class ITranslationHistoryRepo(ABC):
    """翻译历史仓储接口"""
    
    @abstractmethod
    async def save_record(self, record: Dict[str, Any]) -> bool:
        """
        保存历史记录
        
        Args:
            record: 记录数据
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    async def find_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        根据键查找历史记录
        
        Args:
            key: 唯一标识
            
        Returns:
            历史记录
        """
        pass


class IConfigRepo(ABC):
    """配置仓储接口"""
    
    @abstractmethod
    async def load(self) -> Dict[str, Any]:
        """加载配置"""
        pass
    
    @abstractmethod
    async def save(self, config: Dict[str, Any]) -> bool:
        """
        保存配置
        
        Args:
            config: 配置数据
            
        Returns:
            是否成功
        """
        pass
