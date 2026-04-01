"""
术语仓储实现
基于 SQLite 和 Excel 的持久化
"""
from typing import Optional, List, Dict, Any
import sqlite3
from infrastructure.repositories import ITermRepository
from domain.models import TermMatch, MatchType


class TerminologyRepository(ITermRepository):
    """术语仓储实现 - 基于 SQLite + Excel"""
    
    def __init__(self, db_conn: sqlite3.Connection, excel_path: str):
        """
        初始化术语仓储
        
        Args:
            db_conn: SQLite 数据库连接
            excel_path: Excel 文件路径
        """
        self.db_conn = db_conn
        self.excel_path = excel_path
    
    async def find_by_source(self, source_text: str, target_lang: str) -> Optional[TermMatch]:
        """精确匹配优先"""
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
                    return TermMatch(
                        original=source,
                        translation=trans,
                        score=100,
                        match_type=MatchType.EXACT,
                        target_lang=target_lang
                    )
            
            # 模糊匹配
            from data_access.fuzzy_matcher import FuzzyMatcher
            result = FuzzyMatcher.find_best_match(source_text, items, 60)
            
            if result:
                return TermMatch.from_dict({
                    **result,
                    'target_lang': target_lang
                })
            
            return None
            
        except Exception as e:
            raise RuntimeError(f"术语查询失败：{e}")
    
    async def save(self, source_text: str, target_lang: str, translation: str) -> bool:
        """保存到术语库"""
        try:
            cursor = self.db_conn.cursor()
            
            # 检查是否已存在
            cursor.execute('''
                SELECT Key FROM terminology WHERE 中文原文 = ?
            ''', (source_text,))
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute(f'''
                    UPDATE terminology 
                    SET {target_lang} = ?
                    WHERE 中文原文 = ?
                ''', (translation, source_text))
            else:
                # 插入新记录
                columns = ['中文原文', target_lang]
                values = [source_text, translation]
                
                placeholders = ', '.join(['?' for _ in columns])
                column_names = ', '.join(columns)
                
                cursor.execute(f'''
                    INSERT INTO terminology ({column_names})
                    VALUES ({placeholders})
                ''', values)
            
            self.db_conn.commit()
            
            # 同步到 Excel（可选，由持久化管理器负责）
            return True
            
        except Exception as e:
            print(f"保存术语失败：{e}")
            return False
    
    async def get_all_terms(self) -> List[Dict[str, Any]]:
        """获取所有术语"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT * FROM terminology')
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            print(f"获取术语列表失败：{e}")
            return []
