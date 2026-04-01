"""
翻译历史记录模块
提供翻译历史的存储、查询和管理功能
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


@dataclass
class TranslationRecord:
    """单条翻译记录"""
    id: int  # 数据库自增 ID
    key: str  # 原文键
    source_text: str  # 原文
    target_lang: str  # 目标语言
    original_trans: str  # 原译文（如果有）
    draft_trans: str  # 初译
    final_trans: str  # 最终译文
    status: str  # 状态：SUCCESS/FAILED
    diagnosis: str  # 诊断信息
    reason: str  # 原因说明
    api_provider: str  # API 提供商
    model_name: str  # 使用的模型
    created_at: str  # 创建时间
    file_path: str = ""  # 源文件路径
    batch_id: str = ""  # 批次 ID
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TranslationRecord':
        """从字典创建"""
        return cls(**data)


class TranslationHistoryManager:
    """翻译历史管理器"""
    
    DEFAULT_DB_PATH = "translation_history.db"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化历史管理器
        
        Args:
            db_path: SQLite 数据库路径，默认当前目录
        """
        self.db_path = db_path or self.DEFAULT_DB_PATH
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 返回字典式行
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败：{e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建翻译历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS translation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    original_trans TEXT DEFAULT '',
                    draft_trans TEXT NOT NULL,
                    final_trans TEXT NOT NULL,
                    status TEXT NOT NULL,
                    diagnosis TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    api_provider TEXT NOT NULL DEFAULT 'deepseek',
                    model_name TEXT NOT NULL DEFAULT 'deepseek-chat',
                    created_at TEXT NOT NULL,
                    file_path TEXT DEFAULT '',
                    batch_id TEXT DEFAULT ''
                )
            ''')
            
            # 创建索引以加速查询
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_key 
                ON translation_history(key)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_source_text 
                ON translation_history(source_text)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_target_lang 
                ON translation_history(target_lang)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON translation_history(created_at)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_status 
                ON translation_history(status)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_batch_id 
                ON translation_history(batch_id)
            ''')
    
    def add_record(self, record: TranslationRecord) -> int:
        """
        添加翻译记录
        
        Args:
            record: 翻译记录对象
            
        Returns:
            插入的记录 ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO translation_history 
                (key, source_text, target_lang, original_trans, draft_trans, 
                 final_trans, status, diagnosis, reason, api_provider, 
                 model_name, created_at, file_path, batch_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.key,
                record.source_text,
                record.target_lang,
                record.original_trans,
                record.draft_trans,
                record.final_trans,
                record.status,
                record.diagnosis,
                record.reason,
                record.api_provider,
                record.model_name,
                record.created_at,
                record.file_path,
                record.batch_id
            ))
            return cursor.lastrowid
    
    def add_from_result(self, result: Any, api_provider: str = "", 
                       model_name: str = "", file_path: str = "", 
                       batch_id: str = "") -> int:
        """
        从 FinalResult 添加记录
        
        Args:
            result: FinalResult 对象
            api_provider: API 提供商
            model_name: 模型名称
            file_path: 源文件路径
            batch_id: 批次 ID
            
        Returns:
            插入的记录 ID
        """
        record = TranslationRecord(
            id=0,  # 由数据库自动生成
            key=result.key,
            source_text=result.source_text,
            target_lang=result.target_lang,
            original_trans=result.original_trans,
            draft_trans=result.draft_trans,
            final_trans=result.final_trans,
            status=result.status,
            diagnosis=result.diagnosis,
            reason=result.reason,
            api_provider=api_provider or "deepseek",
            model_name=model_name or "deepseek-chat",
            created_at=datetime.now().isoformat(),
            file_path=file_path,
            batch_id=batch_id
        )
        
        return self.add_record(record)
    
    def get_record_by_id(self, record_id: int) -> Optional[TranslationRecord]:
        """根据 ID 获取记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM translation_history WHERE id = ?
            ''', (record_id,))
            
            row = cursor.fetchone()
            if row:
                return TranslationRecord(**dict(row))
            return None
    
    def search_records(
        self,
        keyword: Optional[str] = None,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        batch_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TranslationRecord]:
        """
        搜索翻译记录
        
        Args:
            keyword: 关键词（搜索 source_text 或 key）
            source_lang: 源语言过滤
            target_lang: 目标语言过滤
            status: 状态过滤（SUCCESS/FAILED）
            start_date: 开始日期（ISO 格式）
            end_date: 结束日期（ISO 格式）
            batch_id: 批次 ID 过滤
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            翻译记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 构建 WHERE 子句
            conditions = []
            params = []
            
            if keyword:
                conditions.append("(source_text LIKE ? OR key LIKE ?)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            if source_lang:
                conditions.append("target_lang = ?")
                params.append(source_lang)
            
            if target_lang:
                conditions.append("target_lang = ?")
                params.append(target_lang)
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if start_date:
                conditions.append("created_at >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("created_at <= ?")
                params.append(end_date)
            
            if batch_id:
                conditions.append("batch_id = ?")
                params.append(batch_id)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f'''
                SELECT * FROM translation_history 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            '''
            
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            records = []
            for row in cursor.fetchall():
                records.append(TranslationRecord(**dict(row)))
            
            return records
    
    def get_statistics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            batch_id: 批次 ID
            
        Returns:
            统计信息字典
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 构建 WHERE 子句
            conditions = []
            params = []
            
            if start_date:
                conditions.append("created_at >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("created_at <= ?")
                params.append(end_date)
            
            if batch_id:
                conditions.append("batch_id = ?")
                params.append(batch_id)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # 总记录数
            cursor.execute(f'''
                SELECT COUNT(*) as total FROM translation_history WHERE {where_clause}
            ''', params)
            total = cursor.fetchone()['total']
            
            # 成功数
            cursor.execute(f'''
                SELECT COUNT(*) as success FROM translation_history 
                WHERE {where_clause} AND status = 'SUCCESS'
            ''', params)
            success = cursor.fetchone()['success']
            
            # 失败数
            cursor.execute(f'''
                SELECT COUNT(*) as failed FROM translation_history 
                WHERE {where_clause} AND status = 'FAILED'
            ''', params)
            failed = cursor.fetchone()['failed']
            
            # 成功率
            success_rate = (success / total * 100) if total > 0 else 0
            
            # 按目标语言分组统计
            cursor.execute(f'''
                SELECT target_lang, COUNT(*) as count 
                FROM translation_history 
                WHERE {where_clause}
                GROUP BY target_lang
                ORDER BY count DESC
            ''', params)
            by_language = {row['target_lang']: row['count'] for row in cursor.fetchall()}
            
            # 按 API 提供商分组统计
            cursor.execute(f'''
                SELECT api_provider, COUNT(*) as count 
                FROM translation_history 
                WHERE {where_clause}
                GROUP BY api_provider
                ORDER BY count DESC
            ''', params)
            by_provider = {row['api_provider']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total': total,
                'success': success,
                'failed': failed,
                'success_rate': round(success_rate, 2),
                'by_language': by_language,
                'by_provider': by_provider
            }
    
    def get_recent_records(self, limit: int = 50) -> List[TranslationRecord]:
        """
        获取最近的翻译记录
        
        Args:
            limit: 返回数量
            
        Returns:
            翻译记录列表，按时间倒序
        """
        return self.search_records(limit=limit)
    
    def delete_record(self, record_id: int) -> bool:
        """
        删除翻译记录
        
        Args:
            record_id: 记录 ID
            
        Returns:
            是否删除成功
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM translation_history WHERE id = ?
            ''', (record_id,))
            return cursor.rowcount > 0
    
    def clear_history(self, before_date: Optional[str] = None) -> int:
        """
        清空历史记录
        
        Args:
            before_date: 如果提供，只删除此日期之前的记录
            
        Returns:
            删除的记录数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if before_date:
                cursor.execute('''
                    DELETE FROM translation_history WHERE created_at < ?
                ''', (before_date,))
            else:
                cursor.execute('DELETE FROM translation_history')
            
            return cursor.rowcount
    
    def export_to_json(self, output_file: str, 
                      records: Optional[List[TranslationRecord]] = None) -> str:
        """
        导出历史记录到 JSON 文件
        
        Args:
            output_file: 输出文件路径
            records: 要导出的记录，如果为 None 则导出所有记录
            
        Returns:
            输出文件路径
        """
        if records is None:
            records = self.search_records(limit=10000)
        
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_records': len(records),
            'records': [r.to_dict() for r in records]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_file
    
    def import_from_json(self, input_file: str) -> int:
        """
        从 JSON 文件导入历史记录
        
        Args:
            input_file: 输入文件路径
            
        Returns:
            导入的记录数
        """
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = 0
        for record_data in data.get('records', []):
            try:
                record = TranslationRecord.from_dict(record_data)
                record.id = 0  # 重置 ID，让数据库重新生成
                self.add_record(record)
                count += 1
            except Exception as e:
                print(f"导入记录失败：{e}")
        
        return count
    
    def get_history_file_path(self) -> str:
        """获取历史数据库文件路径"""
        return self.db_path


# 全局单例
_history_manager: Optional[TranslationHistoryManager] = None


def get_history_manager(db_path: Optional[str] = None) -> TranslationHistoryManager:
    """
    获取全局历史管理器实例
    
    Args:
        db_path: 数据库路径
        
    Returns:
        历史管理器实例
    """
    global _history_manager
    if _history_manager is None:
        _history_manager = TranslationHistoryManager(db_path)
    return _history_manager


def record_translation(result: Any, api_provider: str = "", 
                      model_name: str = "", file_path: str = "", 
                      batch_id: str = "") -> int:
    """
    记录翻译结果的便捷函数
    
    Args:
        result: FinalResult 对象
        api_provider: API 提供商
        model_name: 模型名称
        file_path: 源文件路径
        batch_id: 批次 ID
        
    Returns:
        插入的记录 ID
    """
    manager = get_history_manager()
    return manager.add_from_result(result, api_provider, model_name, file_path, batch_id)
