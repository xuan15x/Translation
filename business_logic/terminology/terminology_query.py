"""
术语查询层
实现精确匹配和模糊匹配逻辑
"""
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from business_logic.terminology import ITerminologyQuery
from data_access.fuzzy_matcher import FuzzyMatcher


class TerminologyQueryService(ITerminologyQuery):
    """术语查询服务"""
    
    def __init__(self, db_conn, exact_match_score: int = 100, 
                 similarity_threshold: int = 60,
                 multiprocess_threshold: int = 1000):
        """
        初始化查询服务
        
        Args:
            db_conn: SQLite 数据库连接
            exact_match_score: 精确匹配置信度
            similarity_threshold: 相似度阈值
            multiprocess_threshold: 多进程处理阈值
        """
        self.db_conn = db_conn
        self.exact_match_score = exact_match_score
        self.similarity_threshold = similarity_threshold
        self.multiprocess_threshold = multiprocess_threshold
    
    async def exact_match(self, source_text: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """
        精确匹配（字符串完全相等）
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            
        Returns:
            匹配结果
        """
        try:
            cursor = self.db_conn.cursor()
            
            # 查询包含目标语言的记录
            cursor.execute(f'''
                SELECT 中文原文，{target_lang} 
                FROM terminology 
                WHERE {target_lang} IS NOT NULL AND {target_lang} != ''
            ''')
            
            rows = cursor.fetchall()
            items = [(row[0], row[1]) for row in rows]
            
            if not items:
                return None
            
            # 优先精确匹配检查（字符串完全相等）
            for source, trans in items:
                if source == source_text:  # 完全精确匹配
                    return {
                        'original': source,
                        'translation': trans,
                        'score': self.exact_match_score
                    }
            
            return None
            
        except Exception as e:
            raise RuntimeError(f"精确匹配失败：{e}")
    
    async def fuzzy_match(self, source_text: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """
        模糊匹配（使用 thefuzz 算法）
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            
        Returns:
            匹配结果
        """
        try:
            cursor = self.db_conn.cursor()
            
            # 查询包含目标语言的记录
            cursor.execute(f'''
                SELECT 中文原文，{target_lang} 
                FROM terminology 
                WHERE {target_lang} IS NOT NULL AND {target_lang} != ''
            ''')
            
            rows = cursor.fetchall()
            items = [(row[0], row[1]) for row in rows]
            
            if not items:
                return None
            
            # 模糊匹配
            if len(items) > self.multiprocess_threshold:
                # 大数据量时使用多进程
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    FuzzyMatcher.find_best_match,
                    source_text,
                    items,
                    self.similarity_threshold
                )
            else:
                # 小数据量直接计算
                result = FuzzyMatcher.find_best_match(
                    source_text,
                    items,
                    self.similarity_threshold
                )
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"模糊匹配失败：{e}")
