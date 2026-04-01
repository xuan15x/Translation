"""
术语库历史记录模块
记录术语库的变更历史，支持时间线查看和版本对比
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from contextlib import contextmanager


class ChangeType(Enum):
    """变更类型"""
    ADDED = "added"  # 新增
    UPDATED = "updated"  # 更新
    DELETED = "deleted"  # 删除
    IMPORTED = "imported"  # 批量导入


@dataclass
class TermChange:
    """单条术语变更记录"""
    id: int  # 数据库自增 ID
    timestamp: str  # 时间戳
    change_type: str  # 变更类型
    source_text: str  # 源文本
    language: str  # 目标语言
    old_value: str = ""  # 旧值
    new_value: str = ""  # 新值
    batch_id: str = ""  # 批次 ID（用于批量操作）
    operator: str = ""  # 操作者（系统/用户）
    notes: str = ""  # 备注信息
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TermChange':
        """从字典创建"""
        return cls(**data)


@dataclass
class Snapshot:
    """术语库快照"""
    id: int
    timestamp: str
    total_entries: int
    total_translations: int
    languages_count: int
    snapshot_data: str  # JSON 格式的完整数据
    batch_id: str = ""
    notes: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Snapshot':
        return cls(**data)


class TerminologyHistoryManager:
    """术语库历史管理器"""
    
    DEFAULT_DB_PATH = "terminology_history.db"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化历史管理器
        
        Args:
            db_path: SQLite 数据库路径
        """
        self.db_path = db_path or self.DEFAULT_DB_PATH
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建变更记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS term_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    language TEXT NOT NULL,
                    old_value TEXT DEFAULT '',
                    new_value TEXT DEFAULT '',
                    batch_id TEXT DEFAULT '',
                    operator TEXT DEFAULT 'system',
                    notes TEXT DEFAULT ''
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON term_changes(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_source_text 
                ON term_changes(source_text)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_batch_id 
                ON term_changes(batch_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_change_type 
                ON term_changes(change_type)
            ''')
            
            # 创建快照表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_entries INTEGER NOT NULL,
                    total_translations INTEGER NOT NULL,
                    languages_count INTEGER NOT NULL,
                    snapshot_data TEXT NOT NULL,
                    batch_id TEXT DEFAULT '',
                    notes TEXT DEFAULT ''
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_snapshot_timestamp 
                ON snapshots(timestamp)
            ''')
    
    def record_change(self, change: TermChange) -> int:
        """
        记录术语变更
        
        Args:
            change: 变更记录对象
            
        Returns:
            插入的记录 ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO term_changes 
                (timestamp, change_type, source_text, language, 
                 old_value, new_value, batch_id, operator, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                change.timestamp,
                change.change_type,
                change.source_text,
                change.language,
                change.old_value,
                change.new_value,
                change.batch_id,
                change.operator,
                change.notes
            ))
            return cursor.lastrowid
    
    def record_add(self, source_text: str, language: str, new_value: str,
                  batch_id: str = "", operator: str = "system", 
                  notes: str = "") -> int:
        """记录添加操作"""
        change = TermChange(
            id=0,
            timestamp=datetime.now().isoformat(),
            change_type=ChangeType.ADDED.value,
            source_text=source_text,
            language=language,
            old_value="",
            new_value=new_value,
            batch_id=batch_id,
            operator=operator,
            notes=notes
        )
        return self.record_change(change)
    
    def record_update(self, source_text: str, language: str, 
                     old_value: str, new_value: str,
                     batch_id: str = "", operator: str = "system",
                     notes: str = "") -> int:
        """记录更新操作"""
        change = TermChange(
            id=0,
            timestamp=datetime.now().isoformat(),
            change_type=ChangeType.UPDATED.value,
            source_text=source_text,
            language=language,
            old_value=old_value,
            new_value=new_value,
            batch_id=batch_id,
            operator=operator,
            notes=notes
        )
        return self.record_change(change)
    
    def record_delete(self, source_text: str, language: str, old_value: str,
                     batch_id: str = "", operator: str = "system",
                     notes: str = "") -> int:
        """记录删除操作"""
        change = TermChange(
            id=0,
            timestamp=datetime.now().isoformat(),
            change_type=ChangeType.DELETED.value,
            source_text=source_text,
            language=language,
            old_value=old_value,
            new_value="",
            batch_id=batch_id,
            operator=operator,
            notes=notes
        )
        return self.record_change(change)
    
    def record_batch_import(self, source_text: str, language: str, 
                           new_value: str, batch_id: str,
                           operator: str = "system") -> int:
        """记录批量导入操作"""
        change = TermChange(
            id=0,
            timestamp=datetime.now().isoformat(),
            change_type=ChangeType.IMPORTED.value,
            source_text=source_text,
            language=language,
            old_value="",
            new_value=new_value,
            batch_id=batch_id,
            operator=operator
        )
        return self.record_change(change)
    
    def get_changes(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        change_type: Optional[str] = None,
        source_text: Optional[str] = None,
        language: Optional[str] = None,
        batch_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TermChange]:
        """
        获取变更记录
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            change_type: 变更类型过滤
            source_text: 源文本过滤
            language: 语言过滤
            batch_id: 批次 ID 过滤
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            变更记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date)
            
            if change_type:
                conditions.append("change_type = ?")
                params.append(change_type)
            
            if source_text:
                conditions.append("source_text = ?")
                params.append(source_text)
            
            if language:
                conditions.append("language = ?")
                params.append(language)
            
            if batch_id:
                conditions.append("batch_id = ?")
                params.append(batch_id)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f'''
                SELECT * FROM term_changes 
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            '''
            
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            changes = []
            for row in cursor.fetchall():
                changes.append(TermChange(**dict(row)))
            
            return changes
    
    def get_timeline(self, days: int = 7, limit: int = 200) -> List[Dict[str, Any]]:
        """
        获取时间线（按天分组）
        
        Args:
            days: 最近多少天
            limit: 返回记录数限制
            
        Returns:
            按天分组的变更记录
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 计算起始日期
            from datetime import timedelta
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    change_type,
                    COUNT(*) as count,
                    GROUP_CONCAT(DISTINCT source_text) as sources
                FROM term_changes
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp), change_type
                ORDER BY date DESC, count DESC
                LIMIT ?
            ''', (start_date, limit))
            
            timeline = []
            for row in cursor.fetchall():
                timeline.append({
                    'date': row['date'],
                    'change_type': row['change_type'],
                    'count': row['count'],
                    'sources': row['sources'].split(',')[:5]  # 只显示前 5 个源文本
                })
            
            return timeline
    
    def create_snapshot(self, db: Dict[str, Dict[str, str]], 
                       batch_id: str = "", notes: str = "") -> int:
        """
        创建术语库快照
        
        Args:
            db: 术语库字典
            batch_id: 批次 ID
            notes: 备注信息
            
        Returns:
            快照 ID
        """
        # 计算统计信息
        total_entries = len(db)
        total_translations = sum(len(t) for t in db.values())
        languages = set()
        for translations in db.values():
            languages.update(translations.keys())
        
        # 序列化数据
        snapshot_data = json.dumps(db, ensure_ascii=False)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO snapshots 
                (timestamp, total_entries, total_translations, 
                 languages_count, snapshot_data, batch_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                total_entries,
                total_translations,
                len(languages),
                snapshot_data,
                batch_id,
                notes
            ))
            return cursor.lastrowid
    
    def get_snapshot(self, snapshot_id: int) -> Optional[Snapshot]:
        """获取指定快照"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM snapshots WHERE id = ?
            ''', (snapshot_id,))
            
            row = cursor.fetchone()
            if row:
                return Snapshot(**dict(row))
            return None
    
    def get_latest_snapshot(self) -> Optional[Snapshot]:
        """获取最新快照"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM snapshots ORDER BY timestamp DESC LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                return Snapshot(**dict(row))
            return None
    
    def compare_snapshots(self, snapshot_id1: int, 
                         snapshot_id2: int) -> Dict[str, Any]:
        """
        对比两个快照
        
        Args:
            snapshot_id1: 第一个快照 ID
            snapshot_id2: 第二个快照 ID
            
        Returns:
            对比结果
        """
        snap1 = self.get_snapshot(snapshot_id1)
        snap2 = self.get_snapshot(snapshot_id2)
        
        if not snap1 or not snap2:
            return {'error': 'Snapshot not found'}
        
        # 解析快照数据
        db1 = json.loads(snap1.snapshot_data)
        db2 = json.loads(snap2.snapshot_data)
        
        # 找出差异
        added = {}
        updated = {}
        deleted = {}
        
        # 检查新增和更新
        for source_text, translations in db2.items():
            if source_text not in db1:
                added[source_text] = translations
            else:
                for language, translation in translations.items():
                    if language not in db1[source_text]:
                        if source_text not in updated:
                            updated[source_text] = {}
                        updated[source_text][language] = {
                            'old': '',
                            'new': translation
                        }
                    elif db1[source_text][language] != translation:
                        if source_text not in updated:
                            updated[source_text] = {}
                        updated[source_text][language] = {
                            'old': db1[source_text][language],
                            'new': translation
                        }
        
        # 检查删除
        for source_text, translations in db1.items():
            if source_text not in db2:
                deleted[source_text] = translations
            else:
                for language in translations:
                    if language not in db2[source_text]:
                        if source_text not in deleted:
                            deleted[source_text] = {}
                        deleted[source_text][language] = translations[language]
        
        return {
            'snapshot1': {
                'id': snap1.id,
                'timestamp': snap1.timestamp,
                'total_entries': snap1.total_entries
            },
            'snapshot2': {
                'id': snap2.id,
                'timestamp': snap2.timestamp,
                'total_entries': snap2.total_entries
            },
            'summary': {
                'added_count': len(added),
                'updated_count': len(updated),
                'deleted_count': len(deleted)
            },
            'changes': {
                'added': added,
                'updated': updated,
                'deleted': deleted
            }
        }
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            days: 统计最近多少天的数据
            
        Returns:
            统计信息字典
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            from datetime import timedelta
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 总变更数
            cursor.execute('''
                SELECT COUNT(*) as total FROM term_changes 
                WHERE timestamp >= ?
            ''', (start_date,))
            total = cursor.fetchone()['total']
            
            # 按类型统计
            cursor.execute('''
                SELECT change_type, COUNT(*) as count 
                FROM term_changes 
                WHERE timestamp >= ?
                GROUP BY change_type
            ''', (start_date,))
            by_type = {row['change_type']: row['count'] for row in cursor.fetchall()}
            
            # 按语言统计
            cursor.execute('''
                SELECT language, COUNT(*) as count 
                FROM term_changes 
                WHERE timestamp >= ?
                GROUP BY language
                ORDER BY count DESC
            ''', (start_date,))
            by_language = {row['language']: row['count'] for row in cursor.fetchall()}
            
            # 快照数量
            cursor.execute('SELECT COUNT(*) as count FROM snapshots')
            snapshot_count = cursor.fetchone()['count']
            
            return {
                'total_changes': total,
                'by_type': by_type,
                'by_language': by_language,
                'snapshot_count': snapshot_count,
                'period_days': days
            }
    
    def export_history(self, output_file: str, 
                      format: str = 'json') -> str:
        """
        导出历史记录
        
        Args:
            output_file: 输出文件路径
            format: 导出格式（json/csv）
            
        Returns:
            输出文件路径
        """
        changes = self.get_changes(limit=10000)
        
        if format == 'json':
            data = {
                'exported_at': datetime.now().isoformat(),
                'total_records': len(changes),
                'changes': [c.to_dict() for c in changes]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            import csv
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', '时间戳', '变更类型', '源文本', 
                               '语言', '旧值', '新值', '批次 ID', '操作者', '备注'])
                
                for change in changes:
                    writer.writerow([
                        change.id,
                        change.timestamp,
                        change.change_type,
                        change.source_text,
                        change.language,
                        change.old_value,
                        change.new_value,
                        change.batch_id,
                        change.operator,
                        change.notes
                    ])
        
        return output_file


# 全局单例
_history_manager: Optional[TerminologyHistoryManager] = None


def get_history_manager(db_path: Optional[str] = None) -> TerminologyHistoryManager:
    """获取全局历史管理器实例"""
    global _history_manager
    if _history_manager is None:
        _history_manager = TerminologyHistoryManager(db_path)
    return _history_manager


def record_term_change(change_type: str, source_text: str, language: str,
                      old_value: str = "", new_value: str = "",
                      batch_id: str = "", operator: str = "system",
                      notes: str = "") -> int:
    """
    记录术语变更的便捷函数
    
    Args:
        change_type: 变更类型
        source_text: 源文本
        language: 语言
        old_value: 旧值
        new_value: 新值
        batch_id: 批次 ID
        operator: 操作者
        notes: 备注
        
    Returns:
        插入的记录 ID
    """
    manager = get_history_manager()
    change = TermChange(
        id=0,
        timestamp=datetime.now().isoformat(),
        change_type=change_type,
        source_text=source_text,
        language=language,
        old_value=old_value,
        new_value=new_value,
        batch_id=batch_id,
        operator=operator,
        notes=notes
    )
    return manager.record_change(change)
