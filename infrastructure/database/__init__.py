"""
数据库模块 - 提供数据库连接池和数据访问功能
"""
from .db_pool import ConnectionPool, DatabaseManager

# 延迟导入以避免循环导入
def __getattr__(name):
    if name == 'ITermRepository':
        # 从领域层导入接口（避免循环依赖）
        from domain.services import ITermRepository
        return ITermRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'ConnectionPool',
    'DatabaseManager',
    'ITermRepository'
]
