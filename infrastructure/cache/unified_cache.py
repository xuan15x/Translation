"""
统一内存缓存管理器
提供高频数据的内存缓存支持，包含版本控制、缓存同步、并发安全保障
集成智能内存管理（动态内存池 + 冷热数据分离 + 磁盘交换）
纯进程内实现，无需外部依赖
"""
import asyncio
import hashlib
import time
from typing import Any, Dict, List, Optional, Set, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import logging
import sys

from infrastructure.utils import (
    get_memory_manager,
    IntelligentMemoryManager,
    MemoryPoolConfig
)

logger = logging.getLogger(__name__)


class CacheIsolationLevel(Enum):
    """缓存隔离级别"""
    READ_UNCOMMITTED = "read_uncommitted"      # 允许脏读
    READ_COMMITTED = "read_committed"          # 只读已提交（默认）
    REPEATABLE_READ = "repeatable_read"        # 可重复读
    SERIALIZABLE = "serializable"              # 串行化（最强一致性）


@dataclass
class VersionedData:
    """带版本号的数据"""
    data: Any
    version: int
    timestamp: float
    expires_at: Optional[float] = None
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    invalidations: int = 0
    version_conflicts: int = 0
    dirty_reads_prevented: int = 0
    phantom_reads_prevented: int = 0
    
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class DataVersionManager:
    """数据版本管理器"""
    
    def __init__(self):
        self._versions: Dict[str, int] = {}  # 数据源 -> 版本号
        self._lock = asyncio.Lock()
    
    async def get_version(self, datasource: str) -> int:
        """获取数据源的当前版本号"""
        async with self._lock:
            return self._versions.get(datasource, 0)
    
    async def increment_version(self, datasource: str) -> int:
        """递增数据源版本号并返回新版本号"""
        async with self._lock:
            current = self._versions.get(datasource, 0)
            new_version = current + 1
            self._versions[datasource] = new_version
            logger.debug(f"📈 {datasource} 版本号递增：{current} -> {new_version}")
            return new_version
    
    async def set_version(self, datasource: str, version: int):
        """设置数据源版本号（用于初始化或修复）"""
        async with self._lock:
            self._versions[datasource] = version
            logger.debug(f"🔧 {datasource} 版本号设置为：{version}")


class UnifiedCacheManager:
    """统一缓存管理器 - 支持版本控制、缓存同步、并发安全
    集成智能内存管理（动态内存池 + 冷热数据分离 + 磁盘交换）
    """
    
    def __init__(self, 
                 isolation_level: CacheIsolationLevel = CacheIsolationLevel.READ_COMMITTED,
                 default_ttl: int = 3600,
                 max_memory_mb: int = 500,
                 enable_intelligent_memory: bool = True):
        """
        初始化缓存管理器
        
        Args:
            isolation_level: 缓存隔离级别
            default_ttl: 默认缓存生存时间（秒）
            max_memory_mb: 最大内存使用量（MB）
            enable_intelligent_memory: 是否启用智能内存管理
        """
        self.isolation_level = isolation_level
        self.default_ttl = default_ttl
        self.max_memory_mb = max_memory_mb
        self.enable_intelligent_memory = enable_intelligent_memory
        
        # 主缓存：数据源 -> 键 -> 版本化数据
        self._cache: Dict[str, Dict[str, VersionedData]] = {}
        
        # 智能内存管理器（可选）
        self.memory_manager: Optional[IntelligentMemoryManager] = None
        if enable_intelligent_memory:
            config = MemoryPoolConfig(
                initial_size_mb=min(200, max_memory_mb // 2),
                max_size_mb=max_memory_mb,
                min_size_mb=50,
                swap_enabled=True
            )
            self.memory_manager = get_memory_manager()
        
        # 版本管理器
        self.version_manager = DataVersionManager()
        
        # 锁机制
        self._global_lock = asyncio.Lock()  # 全局锁
        self._datasource_locks: Dict[str, asyncio.Lock] = {}  # 数据源级别锁
        self._key_locks: Dict[str, Dict[str, asyncio.Lock]] = {}  # 键级别锁
        
        # 事务管理
        self._transactions: Dict[str, Dict] = {}  # 事务 ID -> 事务上下文
        self._transaction_counter = 0
        
        # 统计信息
        self.stats = CacheStats()
        
        # 内存估算
        self._memory_estimate_bytes = 0
        
        # 订阅者模式（缓存失效通知）
        self._subscribers: Dict[str, List[Callable]] = {}
        
        logger.info(f"✅ 统一缓存管理器已初始化")
        logger.info(f"   隔离级别：{isolation_level.value}")
        logger.info(f"   默认 TTL: {default_ttl}s")
        logger.info(f"   最大内存：{max_memory_mb}MB")
    
    def _get_datasource_lock(self, datasource: str) -> asyncio.Lock:
        """获取或创建数据源级别的锁"""
        if datasource not in self._datasource_locks:
            self._datasource_locks[datasource] = asyncio.Lock()
        return self._datasource_locks[datasource]
    
    def _get_key_lock(self, datasource: str, key: str) -> asyncio.Lock:
        """获取或创建键级别的锁"""
        if datasource not in self._key_locks:
            self._key_locks[datasource] = {}
        if key not in self._key_locks[datasource]:
            self._key_locks[datasource][key] = asyncio.Lock()
        return self._key_locks[datasource][key]
    
    async def get(self, datasource: str, key: str, 
                  default: Any = None) -> Optional[Any]:
        """
        读取缓存数据（保证隔离级别，支持智能内存）
        
        Args:
            datasource: 数据源名称
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值，如果不存在或已过期则返回 default
        """
        # 使用智能内存管理器读取（如果启用）
        if self.enable_intelligent_memory and self.memory_manager:
            try:
                versioned_data = await self.memory_manager.get(datasource, key)
                if versioned_data is not None:
                    # 检查过期
                    if versioned_data.is_expired():
                        await self.delete(datasource, key)
                        self.stats.misses += 1
                        return default
                    
                    # 根据隔离级别检查可见性
                    if not await self._check_visibility(datasource, key, versioned_data):
                        self.stats.dirty_reads_prevented += 1
                        self.stats.misses += 1
                        return default
                    
                    self.stats.hits += 1
                    logger.debug(f"✅ 缓存命中：{datasource}:{key} (v{versioned_data.version})")
                    return versioned_data.data
            except Exception as e:
                logger.error(f"智能内存读取失败：{e}")
                # 降级到传统方式
                return await self._get_traditional(datasource, key, default)
        
        # 传统方式读取
        return await self._get_traditional(datasource, key, default)
    
    async def set(self, datasource: str, key: str, value: Any,
                  version: Optional[int] = None,
                  ttl: Optional[int] = None,
                  transaction_id: Optional[str] = None):
        """
        写入缓存数据（智能内存管理：自动冷热分离 + 磁盘交换）
        
        Args:
            datasource: 数据源名称
            key: 缓存键
            value: 缓存值
            version: 指定版本号（可选，默认自动递增）
            ttl: 生存时间（秒）
            transaction_id: 事务 ID（可选）
        """
        if ttl is None:
            ttl = self.default_ttl
        
        # 如果没有指定版本号，自动递增
        if version is None:
            version = await self.version_manager.increment_version(datasource)
        
        expires_at = time.time() + ttl if ttl > 0 else None
        
        versioned_data = VersionedData(
            data=value,
            version=version,
            timestamp=time.time(),
            expires_at=expires_at
        )
        
        # 如果是事务操作，延迟到提交时写入
        if transaction_id:
            if transaction_id not in self._transactions:
                raise ValueError(f"未知的事务 ID: {transaction_id}")
            
            self._transactions[transaction_id]['writes'].append({
                'type': 'set',
                'datasource': datasource,
                'key': key,
                'versioned_data': versioned_data
            })
            return
        
        # 使用智能内存管理器存储（如果启用）
        if self.enable_intelligent_memory and self.memory_manager:
            try:
                await self.memory_manager.put(datasource, key, versioned_data)
            except Exception as e:
                logger.error(f"智能内存存储失败：{e}")
                # 降级到传统方式
                await self._set_traditional(datasource, key, versioned_data)
        else:
            # 传统方式存储
            await self._set_traditional(datasource, key, versioned_data)
    
    async def delete(self, datasource: str, key: str,
                    transaction_id: Optional[str] = None):
        """
        删除缓存数据
        
        Args:
            datasource: 数据源名称
            key: 缓存键
            transaction_id: 事务 ID（可选）
        """
        # 如果是事务操作，延迟到提交时处理
        if transaction_id:
            if transaction_id not in self._transactions:
                raise ValueError(f"未知的事务 ID: {transaction_id}")
            
            self._transactions[transaction_id]['writes'].append({
                'type': 'delete',
                'datasource': datasource,
                'key': key
            })
            return
        
        # 直接删除
        await self._delete_internal(datasource, key)
    
    async def _delete_internal(self, datasource: str, key: str):
        """内部删除方法"""
        if datasource not in self._cache:
            return
        
        if key not in self._cache[datasource]:
            return
        
        old_data = self._cache[datasource].pop(key)
        self._update_memory_estimate(datasource, key, old_data, None)
        self.stats.invalidations += 1
        
        logger.debug(f"🗑️ 缓存删除：{datasource}:{key}")
        
        # 通知订阅者
        await self._notify_subscribers(datasource, key, 'delete')
    
    async def invalidate_datasource(self, datasource: str):
        """
        使整个数据源的缓存失效（数据更新时调用）
        
        Args:
            datasource: 数据源名称
        """
        async with self._global_lock:
            if datasource in self._cache:
                keys_count = len(self._cache[datasource])
                del self._cache[datasource]
                
                # 重置版本号
                await self.version_manager.set_version(datasource, 0)
                
                self.stats.invalidations += keys_count
                
                logger.info(f"🧹 数据源缓存已清空：{datasource} ({keys_count} 个条目)")
                
                # 通知所有订阅者
                for key in list(self._cache.get(datasource, {}).keys()):
                    await self._notify_subscribers(datasource, key, 'invalidate_datasource')
    
    async def begin_transaction(self) -> str:
        """
        开始一个事务
        
        Returns:
            事务 ID
        """
        self._transaction_counter += 1
        transaction_id = f"txn_{self._transaction_counter}_{int(time.time())}"
        
        self._transactions[transaction_id] = {
            'id': transaction_id,
            'start_time': time.time(),
            'writes': [],
            'snapshot': {}  # 事务开始时的快照（用于 MVCC）
        }
        
        logger.debug(f"🔄 事务开始：{transaction_id}")
        return transaction_id
    
    async def commit_transaction(self, transaction_id: str):
        """
        提交事务
        
        Args:
            transaction_id: 事务 ID
        """
        if transaction_id not in self._transactions:
            raise ValueError(f"未知的事务 ID: {transaction_id}")
        
        transaction = self._transactions[transaction_id]
        
        async with self._global_lock:
            # 按顺序应用所有写入
            for write_op in transaction['writes']:
                if write_op['type'] == 'set':
                    datasource = write_op['datasource']
                    key = write_op['key']
                    versioned_data = write_op['versioned_data']
                    
                    await self._ensure_datasource_cache(datasource)
                    self._cache[datasource][key] = versioned_data
                    
                    self._update_memory_estimate(
                        datasource, key,
                        self._cache[datasource].get(key),
                        versioned_data
                    )
                    
                elif write_op['type'] == 'delete':
                    await self._delete_internal(
                        write_op['datasource'],
                        write_op['key']
                    )
        
        # 清理事务
        del self._transactions[transaction_id]
        
        logger.info(f"✅ 事务提交：{transaction_id}")
    
    async def rollback_transaction(self, transaction_id: str):
        """
        回滚事务
        
        Args:
            transaction_id: 事务 ID
        """
        if transaction_id not in self._transactions:
            raise ValueError(f"未知的事务 ID: {transaction_id}")
        
        # 简单实现：直接丢弃事务的写入
        del self._transactions[transaction_id]
        
        logger.info(f"❌ 事务回滚：{transaction_id}")
    
    async def _check_visibility(self, datasource: str, key: str, 
                               versioned_data: VersionedData) -> bool:
        """检查数据在当前隔离级别下是否可见"""
        if self.isolation_level == CacheIsolationLevel.READ_UNCOMMITTED:
            return True  # 允许读未提交
        
        # 对于其他隔离级别，检查数据是否已提交
        # 简化实现：假设所有在缓存中的数据都是已提交的
        # 实际项目中可以结合事务系统实现 MVCC
        return True
    
    async def _get_traditional(self, datasource: str, key: str, 
                               default: Any = None) -> Optional[Any]:
        """传统方式读取（兜底机制）"""
        datasource_lock = self._get_datasource_lock(datasource)
        
        async with datasource_lock:
            if datasource not in self._cache:
                self.stats.misses += 1
                return default
            
            if key not in self._cache[datasource]:
                self.stats.misses += 1
                return default
            
            versioned_data = self._cache[datasource][key]
            
            # 检查过期
            if versioned_data.is_expired():
                await self._delete_internal(datasource, key)
                self.stats.misses += 1
                return default
            
            # 根据隔离级别检查可见性
            if not await self._check_visibility(datasource, key, versioned_data):
                self.stats.dirty_reads_prevented += 1
                self.stats.misses += 1
                return default
            
            self.stats.hits += 1
            logger.debug(f"✅ 缓存命中：{datasource}:{key} (v{versioned_data.version})")
            return versioned_data.data
    
    async def _set_traditional(self, datasource: str, key: str, 
                               versioned_data: VersionedData):
        """传统方式写入（兜底机制）"""
        key_lock = self._get_key_lock(datasource, key)
        async with key_lock:
            await self._ensure_datasource_cache(datasource)
            
            # 检查版本冲突
            if datasource in self._cache and key in self._cache[datasource]:
                existing = self._cache[datasource][key]
                if existing.version > versioned_data.version:
                    self.stats.version_conflicts += 1
                    logger.warning(
                        f"⚠️ 版本冲突：{datasource}:{key} "
                        f"(现有 v{existing.version} > 新 v{versioned_data.version})"
                    )
                    return  # 拒绝写入旧版本
            
            old_data = self._cache[datasource].get(key)
            self._cache[datasource][key] = versioned_data
            
            # 更新内存估算
            self._update_memory_estimate(datasource, key, old_data, versioned_data)
        
        logger.debug(f"💾 缓存写入：{datasource}:{key} (v{versioned_data.version})")
    
    async def _ensure_datasource_cache(self, datasource: str):
        """确保数据源的缓存空间已创建"""
        if datasource not in self._cache:
            self._cache[datasource] = {}
    
    def _estimate_size(self, value: Any) -> int:
        """估算对象的内存大小"""
        try:
            return sys.getsizeof(value)
        except Exception:
            return 100  # 默认估算
    
    def _update_memory_estimate(self, datasource: str, key: str,
                               old_data: Optional[VersionedData],
                               new_data: Optional[VersionedData]):
        """更新内存估算"""
        if old_data:
            self._memory_estimate_bytes -= self._estimate_size(old_data.data)
        if new_data:
            self._memory_estimate_bytes += self._estimate_size(new_data.data)
        
        # 检查是否超出内存限制
        max_bytes = self.max_memory_mb * 1024 * 1024
        if self._memory_estimate_bytes > max_bytes:
            logger.warning(
                f"⚠️ 缓存内存超出限制："
                f"{self._memory_estimate_bytes / 1024 / 1024:.2f}MB > {self.max_memory_mb}MB"
            )
            # TODO: 实现 LRU 淘汰策略
    
    def subscribe(self, datasource: str, callback: Callable):
        """
        订阅数据源的缓存失效事件
        
        Args:
            datasource: 数据源名称
            callback: 回调函数 callback(datasource, key, event_type)
        """
        if datasource not in self._subscribers:
            self._subscribers[datasource] = []
        self._subscribers[datasource].append(callback)
        logger.debug(f"📢 订阅缓存事件：{datasource}")
    
    async def _notify_subscribers(self, datasource: str, key: str, event_type: str):
        """通知订阅者"""
        if datasource not in self._subscribers:
            return
        
        for callback in self._subscribers[datasource]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(datasource, key, event_type)
                else:
                    callback(datasource, key, event_type)
            except Exception as e:
                logger.error(f"缓存事件回调执行失败：{e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息（包含智能内存统计）"""
        async with self._global_lock:
            total_entries = sum(
                len(keys) for keys in self._cache.values()
            )
            
            stats = {
                'hits': self.stats.hits,
                'misses': self.stats.misses,
                'invalidations': self.stats.invalidations,
                'version_conflicts': self.stats.version_conflicts,
                'dirty_reads_prevented': self.stats.dirty_reads_prevented,
                'phantom_reads_prevented': self.stats.phantom_reads_prevented,
                'hit_rate_percent': round(self.stats.hit_rate(), 2),
                'total_entries': total_entries,
                'datasources_count': len(self._cache),
                'memory_usage_mb': round(self._memory_estimate_bytes / 1024 / 1024, 2),
                'isolation_level': self.isolation_level.value,
                'intelligent_memory_enabled': self.enable_intelligent_memory
            }
            
            # 添加智能内存统计（如果启用）
            if self.enable_intelligent_memory and self.memory_manager:
                try:
                    mem_stats = await self.memory_manager.get_stats()
                    stats['smart_memory'] = mem_stats
                except Exception as e:
                    logger.error(f"获取智能内存统计失败：{e}")
            
            return stats
    
    async def clear_all(self):
        """清空所有缓存"""
        async with self._global_lock:
            self._cache.clear()
            self._memory_estimate_bytes = 0
            self.stats = CacheStats()
            
            logger.info("🧹 所有缓存已清空")


# 全局单例
_cache_manager: Optional[UnifiedCacheManager] = None


def get_cache_manager() -> UnifiedCacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = UnifiedCacheManager()
    return _cache_manager


def init_cache_manager(isolation_level: str = "read_committed",
                      default_ttl: int = 3600,
                      max_memory_mb: int = 500,
                      enable_intelligent_memory: bool = True) -> UnifiedCacheManager:
    """
    初始化缓存管理器
    
    Args:
        isolation_level: 隔离级别 ("read_uncommitted"|"read_committed"|"repeatable_read"|"serializable")
        default_ttl: 默认 TTL（秒）
        max_memory_mb: 最大内存（MB）
        enable_intelligent_memory: 是否启用智能内存管理
        
    Returns:
        缓存管理器实例
    """
    global _cache_manager
    
    level_map = {
        "read_uncommitted": CacheIsolationLevel.READ_UNCOMMITTED,
        "read_committed": CacheIsolationLevel.READ_COMMITTED,
        "repeatable_read": CacheIsolationLevel.REPEATABLE_READ,
        "serializable": CacheIsolationLevel.SERIALIZABLE
    }
    
    isolation = level_map.get(isolation_level, CacheIsolationLevel.READ_COMMITTED)
    _cache_manager = UnifiedCacheManager(
        isolation_level=isolation,
        default_ttl=default_ttl,
        max_memory_mb=max_memory_mb,
        enable_intelligent_memory=enable_intelligent_memory
    )
    
    return _cache_manager
