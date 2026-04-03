"""
数据库模块 - 提供数据库连接池和数据访问功能
"""
from .db_pool import ConnectionPool, DatabaseManager
from .repositories import ITermRepository

__all__ = [
    'ConnectionPool',
    'DatabaseManager',
    'ITermRepository'
]
