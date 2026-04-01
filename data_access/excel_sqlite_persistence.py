"""
数据持久化管理器
负责 Excel 文件与 SQLite 内存数据库之间的数据同步
"""
import os
import json
import pandas as pd
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExcelSQLiteManager:
    """Excel 文件与 SQLite 内存数据库管理器"""
    
    def __init__(self, excel_path: str, db_path: str = ":memory:"):
        """
        初始化
        
        Args:
            excel_path: Excel 文件路径
            db_path: SQLite 数据库路径，默认使用内存数据库
        """
        self.excel_path = excel_path
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化内存数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"✅ 内存数据库已初始化：{self.db_path}")
        except Exception as e:
            logger.error(f"数据库初始化失败：{e}")
            raise
    
    def load_from_excel(self, table_name: str = "data", 
                       key_columns: List[str] = None) -> int:
        """
        从 Excel 加载数据到 SQLite
        
        Args:
            table_name: 表名
            key_columns: 键列名列表，用于生成 WHERE 条件
            
        Returns:
            加载的行数
        """
        if not os.path.exists(self.excel_path):
            logger.info(f"Excel 文件不存在，将自动创建：{self.excel_path}")
            return 0
        
        try:
            # 读取 Excel
            df = pd.read_excel(self.excel_path, engine='openpyxl')
            df.fillna('', inplace=True)
            
            # 写入 SQLite
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            
            # 创建索引
            if key_columns:
                cursor = self.conn.cursor()
                for col in key_columns:
                    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{col} ON {table_name}({col})')
                self.conn.commit()
            
            logger.info(f"📊 已加载 {len(df)} 行数据到内存数据库：{table_name}")
            return len(df)
            
        except Exception as e:
            logger.error(f"从 Excel 加载失败：{e}")
            raise
    
    def save_to_excel(self, table_name: str = "data", 
                     output_path: Optional[str] = None) -> str:
        """
        保存 SQLite 数据到 Excel
        
        Args:
            table_name: 表名
            output_path: 输出路径，如果为 None 则保存到原 Excel 文件
            
        Returns:
            保存的文件路径
        """
        if output_path is None:
            output_path = self.excel_path
        
        try:
            # 从 SQLite 读取数据
            cursor = self.conn.cursor()
            cursor.execute(f'SELECT * FROM {table_name}')
            rows = cursor.fetchall()
            
            if not rows:
                logger.info(f"{table_name} 表为空")
                return output_path
            
            # 转换为 DataFrame
            columns = [description[0] for description in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            
            # 保存到 Excel
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.info(f"💾 已保存 {len(df)} 行数据到 Excel: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"保存到 Excel 失败：{e}")
            raise
    
    def execute_query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """
        执行 SQL 查询
        
        Args:
            sql: SQL 查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # 转换为字典列表
            result = []
            for row in rows:
                result.append(dict(row))
            
            return result
            
        except Exception as e:
            logger.error(f"查询执行失败：{e}")
            raise
    
    def execute_update(self, sql: str, params: tuple = ()) -> int:
        """
        执行 SQL 更新（INSERT/UPDATE/DELETE）
        
        Args:
            sql: SQL 更新语句
            params: 参数
            
        Returns:
            受影响的行数
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            self.conn.commit()
            return cursor.rowcount
            
        except Exception as e:
            logger.error(f"更新失败：{e}")
            self.conn.rollback()
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("🔒 数据库连接已关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class TerminologyPersistence:
    """术语库持久化管理器"""
    
    def __init__(self, excel_path: str, db_path: str = ":memory:"):
        """
        初始化
        
        Args:
            excel_path: 术语库 Excel 文件路径
            db_path: SQLite 数据库路径
        """
        self.manager = ExcelSQLiteManager(excel_path, db_path)
        self.excel_path = excel_path
        
        # 加载数据到内存
        self._load_to_memory()
    
    def _load_to_memory(self):
        """加载术语库到内存"""
        try:
            count = self.manager.load_from_excel(
                table_name="terminology",
                key_columns=["中文原文", "Key"]
            )
            logger.info(f"✅ 术语库已加载到内存：{count} 条")
        except Exception as e:
            logger.warning(f"术语库加载失败（可能是新文件）: {e}")
    
    def save_to_excel(self, output_path: Optional[str] = None) -> str:
        """
        保存术语库到 Excel
        
        Args:
            output_path: 输出路径
            
        Returns:
            保存的文件路径
        """
        return self.manager.save_to_excel(
            table_name="terminology",
            output_path=output_path
        )
    
    def get_terminology(self, source_text: str) -> Optional[Dict]:
        """
        获取术语
        
        Args:
            source_text: 源文本
            
        Returns:
            术语字典
        """
        sql = "SELECT * FROM terminology WHERE 中文原文 = ?"
        results = self.manager.execute_query(sql, (source_text,))
        return results[0] if results else None
    
    def add_terminology(self, source_text: str, lang: str, trans: str):
        """
        添加术语
        
        Args:
            source_text: 源文本
            lang: 目标语言
            trans: 翻译
        """
        # 检查是否存在
        existing = self.get_terminology(source_text)
        
        if existing:
            # 更新现有记录
            sql = f"UPDATE terminology SET {lang} = ? WHERE 中文原文 = ?"
            self.manager.execute_update(sql, (trans, source_text))
        else:
            # 插入新记录
            sql = """
                INSERT INTO terminology (Key, 中文原文, {lang}) 
                VALUES (?, ?, ?)
            """.format(lang=lang)
            key = f"TM_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            self.manager.execute_update(sql, (key, source_text, trans))
    
    def get_all_terminology(self) -> List[Dict]:
        """获取所有术语"""
        return self.manager.execute_query("SELECT * FROM terminology")
    
    def close(self):
        """关闭并保存数据"""
        self.save_to_excel()
        self.manager.close()


class HistoryPersistence:
    """翻译历史持久化管理器"""
    
    def __init__(self, excel_path: str, db_path: str = ":memory:"):
        """
        初始化
        
        Args:
            excel_path: 历史库 Excel 文件路径
            db_path: SQLite 数据库路径
        """
        self.manager = ExcelSQLiteManager(excel_path, db_path)
        self.excel_path = excel_path
        
        # 加载数据到内存
        self._load_to_memory()
    
    def _load_to_memory(self):
        """加载历史数据到内存"""
        try:
            count = self.manager.load_from_excel(
                table_name="history",
                key_columns=["key", "source_text", "batch_id", "created_at"]
            )
            logger.info(f"✅ 历史库已加载到内存：{count} 条")
        except Exception as e:
            logger.warning(f"历史库加载失败（可能是新文件）: {e}")
    
    def save_to_excel(self, output_path: Optional[str] = None) -> str:
        """
        保存历史数据到 Excel
        
        Args:
            output_path: 输出路径
        """
        return self.manager.save_to_excel(
            table_name="history",
            output_path=output_path
        )
    
    def add_record(self, record_data: Dict):
        """
        添加历史记录
        
        Args:
            record_data: 记录字典
        """
        columns = ', '.join(record_data.keys())
        placeholders = ', '.join(['?' for _ in record_data])
        
        sql = f"""
            INSERT INTO history ({columns}) 
            VALUES ({placeholders})
        """
        self.manager.execute_update(sql, tuple(record_data.values()))
    
    def get_records(self, batch_id: Optional[str] = None, 
                   limit: int = 100) -> List[Dict]:
        """
        获取历史记录
        
        Args:
            batch_id: 批次 ID
            limit: 返回记录数限制
            
        Returns:
            历史记录列表
        """
        if batch_id:
            sql = "SELECT * FROM history WHERE batch_id = ? ORDER BY created_at DESC LIMIT ?"
            return self.manager.execute_query(sql, (batch_id, limit))
        else:
            sql = "SELECT * FROM history ORDER BY created_at DESC LIMIT ?"
            return self.manager.execute_query(sql, (limit,))
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取统计信息"""
        # 实现统计查询逻辑
        return {
            'total_records': len(self.get_records(limit=10000)),
            'days': days
        }
    
    def close(self):
        """关闭并保存数据"""
        self.save_to_excel()
        self.manager.close()
