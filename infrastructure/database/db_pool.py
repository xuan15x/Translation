"""
数据库连接池模块
实现 SQLite 连接池，提升高并发写入性能
"""
import sqlite3
import asyncio
from typing import Optional, Dict
from contextlib import asynccontextmanager
import logging
import time

logger = logging.getLogger(__name__)


class ConnectionPool:
    """SQLite 连接池"""
    
    def __init__(self, db_path: str, pool_size: int = 5, 
                 max_overflow: int = 2, timeout: int = 30):
        """
        初始化连接池
        
        Args:
            db_path: 数据库文件路径
            pool_size: 基础连接池大小
            max_overflow: 最大溢出连接数
            timeout: 获取连接超时（秒）
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.timeout = timeout
        
        # 连接池队列
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=pool_size)
        self._overflow_connections: set = set()  # 跟踪溢出连接的ID
        self._overflow_count = 0
        self._created_count = 0
        self._stats = {
            'connections_created': 0,
            'connections_closed': 0,
            'queries_executed': 0,
            'wait_time_total': 0.0
        }
        
        # 初始化连接池
        self._initialized = False
    
    async def _initialize(self):
        """初始化连接池"""
        if self._initialized:
            return
        
        logger.info(f"初始化连接池：pool_size={self.pool_size}, max_overflow={self.max_overflow}")
        
        # 创建基础连接池
        for i in range(self.pool_size):
            conn = await self._create_connection()
            await self._pool.put(conn)
        
        self._initialized = True
        logger.info(f"连接池初始化完成，已创建 {self.pool_size} 个连接")
    
    async def _create_connection(self) -> sqlite3.Connection:
        """创建新的数据库连接"""
        loop = asyncio.get_event_loop()
        
        # 在线程池中创建连接（避免阻塞）
        conn = await loop.run_in_executor(
            None,
            lambda: sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None  # 自动提交模式
            )
        )
        
        # 配置连接
        await loop.run_in_executor(
            None,
            lambda: conn.execute("PRAGMA journal_mode=WAL")  # WAL 模式提升并发
        )
        
        await loop.run_in_executor(
            None,
            lambda: conn.execute("PRAGMA synchronous=NORMAL")  # 平衡性能和安全性
        )
        
        await loop.run_in_executor(
            None,
            lambda: conn.execute("PRAGMA cache_size=-64000")  # 64MB 缓存
        )
        
        self._created_count += 1
        self._stats['connections_created'] += 1
        
        logger.debug(f"创建新数据库连接 (总创建数：{self._created_count})")
        
        return conn
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接的上下文管理器"""
        if not self._initialized:
            await self._initialize()
        
        conn = None
        start_time = time.time()
        
        try:
            # 尝试从池中获取连接
            try:
                conn = await asyncio.wait_for(
                    self._pool.get(),
                    timeout=self.timeout
                )
                wait_time = time.time() - start_time
                self._stats['wait_time_total'] += wait_time
                
                if wait_time > 0.1:
                    logger.warning(f"等待数据库连接耗时：{wait_time:.2f}s")
                
            except asyncio.TimeoutError:
                # 池中没有可用连接，创建溢出连接
                if self._overflow_count < self.max_overflow:
                    self._overflow_count += 1
                    conn = await self._create_connection()
                    self._overflow_connections.add(id(conn))
                    logger.debug(
                        f"创建溢出连接 (当前溢出数：{self._overflow_count}/{self.max_overflow})"
                    )
                else:
                    logger.error(
                        f"连接池耗尽：pool_size={self.pool_size}, "
                        f"overflow={self._overflow_count}"
                    )
                    raise RuntimeError("数据库连接池耗尽")
            
            self._stats['queries_executed'] += 1
            yield conn
            
        finally:
            # 归还连接到池
            if conn:
                if self._overflow_count > 0 and id(conn) in self._overflow_connections:
                    # 如果是溢出连接，直接关闭
                    self._overflow_connections.discard(id(conn))
                    await self._close_connection(conn)
                    self._overflow_count -= 1
                else:
                    # 普通连接归还到池
                    try:
                        self._pool.put_nowait(conn)
                    except asyncio.QueueFull:
                        # 池已满，关闭连接
                        await self._close_connection(conn)
    
    async def _close_connection(self, conn: sqlite3.Connection):
        """关闭数据库连接"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conn.close)
        self._stats['connections_closed'] += 1
        logger.debug(f"关闭数据库连接 (总关闭数：{self._stats['connections_closed']})")
    
    async def close_all(self):
        """关闭所有连接"""
        logger.info("关闭所有数据库连接")

        # 关闭池中所有连接
        while not self._pool.empty():
            conn = self._pool.get_nowait()
            await self._close_connection(conn)

        logger.info(
            f"连接池关闭完成："
            f"创建={self._stats['connections_created']}, "
            f"关闭={self._stats['connections_closed']}, "
            f"溢出={self._overflow_count}, "
            f"查询={self._stats['queries_executed']}"
        )
    
    async def get_stats(self) -> Dict:
        """获取连接池统计信息"""
        return {
            **self._stats,
            'pool_size': self.pool_size,
            'current_pool_size': self._pool.qsize(),
            'overflow_count': self._overflow_count,
            'total_connections_created': self._created_count,
            'avg_wait_time': (
                self._stats['wait_time_total'] / self._stats['queries_executed']
                if self._stats['queries_executed'] > 0 else 0.0
            )
        }


class DatabaseManager:
    """数据库管理器（带连接池）"""
    
    _instances: Dict[str, 'DatabaseManager'] = {}
    
    def __new__(cls, db_path: str, pool_size: int = 5):
        """单例模式，每个数据库路径一个实例"""
        if db_path not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[db_path] = instance
        return cls._instances[db_path]
    
    def __init__(self, db_path: str, pool_size: int = 5):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库路径
            pool_size: 连接池大小
        """
        # 防止重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.db_path = db_path
        self.pool = ConnectionPool(db_path, pool_size=pool_size)
        self._initialized = True
        
        logger.info(f"数据库管理器初始化：{db_path} (pool_size={pool_size})")
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接"""
        async with self.pool.get_connection() as conn:
            yield conn
    
    async def execute(self, query: str, params: tuple = None):
        """
        执行 SQL 查询
        
        Args:
            query: SQL 查询语句
            params: 查询参数
            
        Returns:
            查询结果
        """
        async with self.pool.get_connection() as conn:
            loop = asyncio.get_event_loop()
            
            if params:
                result = await loop.run_in_executor(
                    None,
                    lambda: conn.execute(query, params)
                )
            else:
                result = await loop.run_in_executor(
                    None,
                    lambda: conn.execute(query)
                )
            
            return result
    
    async def executemany(self, query: str, params_list: list):
        """
        批量执行 SQL
        
        Args:
            query: SQL 查询语句
            params_list: 参数列表
        """
        async with self.pool.get_connection() as conn:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: conn.executemany(query, params_list)
            )
    
    async def close(self):
        """关闭数据库连接池"""
        await self.pool.close_all()
    
    async def get_stats(self) -> Dict:
        """获取统计信息"""
        return await self.pool.get_stats()
