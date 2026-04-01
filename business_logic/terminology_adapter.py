"""
术语管理器适配器
将旧的 TerminologyManager 适配到新的领域服务接口
便于逐步迁移，不破坏现有功能
"""
from typing import Optional, Dict, Any
from domain.services import ITerminologyDomainService
from domain.models import TermMatch, MatchType


class TerminologyManagerAdapter(ITerminologyDomainService):
    """适配器模式 - 包装旧的 TerminologyManager"""
    
    def __init__(self, terminology_manager):
        """
        初始化适配器
        
        Args:
            terminology_manager: 旧的 TerminologyManager 实例
        """
        self.tm = terminology_manager
    
    async def find_match(self, source_text: str, target_lang: str) -> Optional[TermMatch]:
        """查找术语匹配（精确优先）"""
        # 调用旧的方法
        result = await self.tm.find_similar(source_text, target_lang)
        
        if not result:
            return None
        
        # 转换为领域模型
        score = result.get('score', 0)
        match_type = MatchType.EXACT if score == 100 else (
            MatchType.FUZZY if score >= 60 else MatchType.NO_MATCH
        )
        
        return TermMatch(
            original=result.get('original', ''),
            translation=result.get('translation', ''),
            score=score,
            match_type=match_type,
            target_lang=target_lang
        )
    
    async def save_term(self, source_text: str, target_lang: str, translation: str):
        """保存术语"""
        await self.tm.add_entry(source_text, target_lang, translation)
