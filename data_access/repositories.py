"""
术语仓储实现
基于 SQLite 和 Excel 的持久化

安全修复：使用参数化查询防止 SQL 注入
"""
from typing import Optional, List, Dict, Any
import sqlite3
from domain.services import ITermRepository
from domain.models import TermMatch, MatchType


# 允许的目标语言列名白名单（防止 SQL 注入）
ALLOWED_LANGUAGE_COLUMNS = {
    '英语', '日语', '韩语', '法语', '德语', '西班牙语', '俄语',
    '葡萄牙语', '意大利语', '阿拉伯语', '泰语', '越南语',
    '印尼语', '马来语', '波兰语', '土耳其语', '瑞典语',
    '挪威语', '丹麦语', '芬兰语', '印地语', '乌尔都语',
    '孟加拉语', '菲律宾语', '缅甸语', '柬埔寨语', '老挝语',
    '波斯语', '希伯来语', '斯瓦希里语', '豪萨语', '哈萨克语',
    '乌兹别克语', '中文'
}


def _validate_column_name(column_name: str) -> bool:
    """
    验证列名是否安全（防止 SQL 注入）
    
    Args:
        column_name: 要验证的列名
        
    Returns:
        bool: 列名是否安全
        
    Raises:
        ValueError: 列名不安全时抛出异常
    """
    if column_name not in ALLOWED_LANGUAGE_COLUMNS:
        raise ValueError(f"不允许的列名：{column_name}。有效的列名：{list(ALLOWED_LANGUAGE_COLUMNS)}")
    return True


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
        """精确匹配优先 - 使用参数化查询"""
        try:
            cursor = self.db_conn.cursor()

            # 验证列名安全性
            _validate_column_name(target_lang)

            # 使用参数化查询（WHERE 子句的值使用参数，列名通过白名单验证）
            # 注意：使用英文逗号分隔列名
            cursor.execute(f'''
                SELECT "中文原文", "{target_lang}"
                FROM terminology
                WHERE "{target_lang}" IS NOT NULL AND "{target_lang}" != ''
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

        except ValueError:
            raise
        except Exception as e:
            # 术语查询失败时返回None而不是抛出异常，让翻译继续
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"术语查询失败（返回None继续翻译）: {e}")
            return None

    async def save(self, source_text: str, target_lang: str, translation: str) -> bool:
        """保存到术语库 - 使用参数化查询"""
        try:
            cursor = self.db_conn.cursor()

            # 验证列名安全性
            _validate_column_name(target_lang)

            # 检查是否已存在（使用参数化查询）
            cursor.execute('''
                SELECT Key FROM terminology WHERE "中文原文" = ?
            ''', (source_text,))

            existing = cursor.fetchone()

            if existing:
                # 更新现有记录（使用参数化查询）
                cursor.execute(f'''
                    UPDATE terminology
                    SET "{target_lang}" = ?
                    WHERE "中文原文" = ?
                ''', (translation, source_text))
            else:
                # 插入新记录（列名通过白名单验证，值使用参数）
                columns = ['中文原文', target_lang]
                values = [source_text, translation]

                placeholders = ', '.join(['?' for _ in columns])
                # 列名使用双引号包裹（SQLite 语法），列名已通过白名单验证
                column_names = ', '.join([f'"{col}"' for col in columns])

                cursor.execute(f'''
                    INSERT INTO terminology ({column_names})
                    VALUES ({placeholders})
                ''', values)

            self.db_conn.commit()

            # 同步到 Excel（可选，由持久化管理器负责）
            return True

        except ValueError:
            raise
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"保存术语失败：{e}")
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
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取术语列表失败：{e}")
            return []
