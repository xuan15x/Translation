"""
术语领域服务实现
整合仓储层和缓存层
"""
from typing import Optional
from domain.services import ITerminologyDomainService
from domain.models import TermMatch
from infrastructure.repositories import ITermRepository


class TerminologyDomainService(ITerminologyDomainService):
    """术语领域服务 - 使用仓储接口"""
    
    def __init__(self, repo: ITermRepository):
        """
        初始化术语领域服务
        
        Args:
            repo: 术语仓储
        """
        self.repo = repo
    
    async def find_match(self, source_text: str, target_lang: str) -> Optional[TermMatch]:
        """查找术语匹配（精确优先）"""
        return await self.repo.find_by_source(source_text, target_lang)
    
    async def save_term(self, source_text: str, target_lang: str, translation: str):
        """保存术语"""
        success = await self.repo.save(source_text, target_lang, translation)
        if not success:
            raise RuntimeError("保存术语失败")
