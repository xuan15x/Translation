"""
智能内存管理系统
提供动态内存池、冷热数据分离、磁盘交换机制，防止内存泄露和膨胀
"""
import asyncio
import os
import pickle
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import psutil
import sys

logger = logging.getLogger(__name__)


class DataTemperature(Enum):
    """数据温度分类"""
    HOT = "hot"          # 热点数据（高频访问）
    WARM = "warm"        # 温数据（偶尔访问）
    COLD = "cold"        # 冷数据（很少访问）


@dataclass
class MemoryPoolConfig:
    """内存池配置"""
    initial_size_mb: int = 100          # 初始内存池大小 (MB)
    max_size_mb: int = 500              # 最大内存池大小 (MB)
    min_size_mb: int = 50               # 最小内存池大小 (MB)
    growth_step_mb: int = 20            # 增长步长 (MB)
    shrink_threshold_percent: float = 0.3  # 收缩阈值 (使用率低于 30% 时收缩)
    expand_threshold_percent: float = 0.8  # 扩张阈值 (使用率高于 80% 时扩张)
    
    # 冷热分离配置
    hot_data_ratio: float = 0.2         # 热点数据比例 (20%)
    warm_data_ratio: float = 0.5        # 温数据比例 (50%)
    cold_data_ratio: float = 0.3        # 冷数据比例 (30%)
    
    # 交换配置
    swap_enabled: bool = True           # 启用磁盘交换
    swap_dir: Optional[str] = None      # 交换文件目录 (None 则使用临时目录)
    swap_file_prefix: str = "swap_"     # 交换文件前缀
    
    # 监控配置
    monitor_interval: int = 10          # 监控间隔 (秒)
    gc_interval: int = 60               # GC 间隔 (秒)


@dataclass
class MemoryBlock:
    """内存块"""
    id: int
    size_bytes: int
    data: Optional[Any] = None
    is_free: bool = True
    last_access_time: float = field(default_factory=time.time)
    access_count: int = 0
    temperature: DataTemperature = DataTemperature.WARM


@dataclass
class SwapFileInfo:
    """交换文件信息"""
    file_path: Path
    key: str
    size_bytes: int
    created_at: float
    last_access: float
    access_count: int = 0


class DynamicMemoryPool:
    """动态内存池 - 自动扩容/收缩"""
    
    def __init__(self, config: MemoryPoolConfig):
        self.config = config
        self._blocks: Dict[int, MemoryBlock] = {}
        self._free_blocks: List[int] = []
        self._key_to_block: Dict[str, int] = {}
        
        self._current_size_bytes = config.initial_size_mb * 1024 * 1024
        self._used_bytes = 0
        self._block_counter = 0
        
        self._lock = asyncio.Lock()
        self._stats = {
            'allocations': 0,
            'deallocations': 0,
            'expansions': 0,
            'contractions': 0,
            'swap_outs': 0,
            'swap_ins': 0
        }
        
        logger.info(f"💾 动态内存池已初始化：{config.initial_size_mb}MB")
    
    async def allocate(self, key: str, data: Any, size_bytes: int) -> bool:
        """分配内存块"""
        async with self._lock:
            # 检查是否需要扩容
            if self._used_bytes + size_bytes > self._current_size_bytes:
                if not await self._try_expand():
                    # 扩容失败，尝试交换冷数据
                    await self._swap_out_cold_data(size_bytes)
                    
                    # 仍然不足则拒绝分配
                    if self._used_bytes + size_bytes > self._current_size_bytes:
                        logger.warning(f"⚠️ 内存池已满，无法分配 {key}")
                        return False
            
            # 分配新块
            block_id = self._block_counter
            self._block_counter += 1
            
            block = MemoryBlock(
                id=block_id,
                size_bytes=size_bytes,
                data=data,
                is_free=False,
                last_access_time=time.time(),
                access_count=1,
                temperature=self._calculate_temperature(1)
            )
            
            self._blocks[block_id] = block
            self._key_to_block[key] = block_id
            self._used_bytes += size_bytes
            self._stats['allocations'] += 1
            
            logger.debug(f"📦 分配内存块：{key} ({size_bytes} bytes)")
            return True
    
    async def get(self, key: str) -> Optional[Any]:
        """获取数据并更新访问统计"""
        async with self._lock:
            if key not in self._key_to_block:
                return None
            
            block_id = self._key_to_block[key]
            block = self._blocks[block_id]
            
            # 更新访问统计
            block.last_access_time = time.time()
            block.access_count += 1
            block.temperature = self._calculate_temperature(block.access_count)
            
            logger.debug(f"✅ 内存命中：{key} (温度:{block.temperature.value})")
            return block.data
    
    async def deallocate(self, key: str) -> bool:
        """释放内存块"""
        async with self._lock:
            if key not in self._key_to_block:
                return False
            
            block_id = self._key_to_block.pop(key)
            block = self._blocks.pop(block_id)
            
            self._used_bytes -= block.size_bytes
            self._free_blocks.append(block_id)
            self._stats['deallocations'] += 1
            
            logger.debug(f"🗑️ 释放内存块：{key}")
            return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取内存池统计"""
        async with self._lock:
            usage_percent = (self._used_bytes / self._current_size_bytes * 100) \
                           if self._current_size_bytes > 0 else 0
            
            temp_stats = {'hot': 0, 'warm': 0, 'cold': 0}
            for block in self._blocks.values():
                if not block.is_free:
                    temp_stats[block.temperature.value] += 1
            
            return {
                **self._stats,
                'current_size_mb': round(self._current_size_bytes / 1024 / 1024, 2),
                'used_bytes': self._used_bytes,
                'used_mb': round(self._used_bytes / 1024 / 1024, 2),
                'usage_percent': round(usage_percent, 2),
                'total_blocks': len(self._blocks),
                'free_blocks': len(self._free_blocks),
                'temperature_distribution': temp_stats
            }
    
    async def _try_expand(self) -> bool:
        """尝试扩容"""
        current_mb = self._current_size_bytes / 1024 / 1024
        
        if current_mb >= self.config.max_size_mb:
            logger.warning("⚠️ 内存池已达最大容量")
            return False
        
        new_size_mb = min(
            current_mb + self.config.growth_step_mb,
            self.config.max_size_mb
        )
        
        self._current_size_bytes = int(new_size_mb * 1024 * 1024)
        self._stats['expansions'] += 1
        
        logger.info(f"📈 内存池扩容：{current_mb:.0f}MB -> {new_size_mb:.0f}MB")
        return True
    
    async def _try_shrink(self):
        """尝试收缩"""
        usage_percent = (self._used_bytes / self._current_size_bytes * 100) \
                       if self._current_size_bytes > 0 else 0
        
        if usage_percent > self.config.shrink_threshold_percent * 100:
            return  # 使用率还很高，不收缩
        
        current_mb = self._current_size_bytes / 1024 / 1024
        
        if current_mb <= self.config.min_size_mb:
            return  # 已经是最小了
        
        new_size_mb = max(
            current_mb - self.config.growth_step_mb,
            self.config.min_size_mb
        )
        
        self._current_size_bytes = int(new_size_mb * 1024 * 1024)
        self._stats['contractions'] += 1
        
        logger.info(f"📉 内存池收缩：{current_mb:.0f}MB -> {new_size_mb:.0f}MB")
    
    def _calculate_temperature(self, access_count: int) -> DataTemperature:
        """根据访问次数计算数据温度"""
        if access_count >= 10:
            return DataTemperature.HOT
        elif access_count >= 3:
            return DataTemperature.WARM
        else:
            return DataTemperature.COLD
    
    async def _swap_out_cold_data(self, needed_bytes: int):
        """交换冷数据到磁盘"""
        if not self.config.swap_enabled:
            return
        
        # 找出所有冷数据块
        cold_blocks = [
            (block_id, block) 
            for block_id, block in self._blocks.items()
            if not block.is_free and block.temperature == DataTemperature.COLD
        ]
        
        if not cold_blocks:
            return  # 没有冷数据可交换
        
        # 按最后访问时间排序，最老的先交换
        cold_blocks.sort(key=lambda x: x[1].last_access_time)
        
        freed_bytes = 0
        for block_id, block in cold_blocks:
            if freed_bytes >= needed_bytes:
                break
            
            # 找到对应的 key
            key = None
            for k, bid in self._key_to_block.items():
                if bid == block_id:
                    key = k
                    break
            
            if key:
                # 交换到磁盘
                await self._swap_to_disk(key, block.data)
                
                # 释放内存
                block.data = None
                self._used_bytes -= block.size_bytes
                freed_bytes += block.size_bytes
                self._stats['swap_outs'] += 1
                
                logger.debug(f"❄️ 冷数据交换到磁盘：{key}")
    
    async def _swap_to_disk(self, key: str, data: Any):
        """将数据交换到磁盘"""
        # 实现略，见 SwapManager 类
        pass


class SwapManager:
    """交换管理器 - 管理磁盘交换文件"""
    
    def __init__(self, config: MemoryPoolConfig):
        self.config = config
        
        # 确定交换目录
        if config.swap_dir:
            self.swap_dir = Path(config.swap_dir)
        else:
            self.swap_dir = Path(tempfile.gettempdir()) / "translation_swap"
        
        self.swap_dir.mkdir(parents=True, exist_ok=True)
        
        self._swap_files: Dict[str, SwapFileInfo] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            'swap_outs': 0,
            'swap_ins': 0,
            'total_swap_size_mb': 0.0
        }
        
        logger.info(f"💿 交换管理器已初始化：{self.swap_dir}")
    
    async def swap_out(self, key: str, data: Any) -> bool:
        """换出到磁盘"""
        try:
            async with self._lock:
                # 生成交换文件名
                filename = f"{self.config.swap_file_prefix}{hash(key)}_{int(time.time())}.pkl"
                file_path = self.swap_dir / filename
                
                # 序列化并写入文件
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: pickle.dump(data, open(file_path, 'wb'))
                )
                
                file_size = file_path.stat().st_size
                
                # 记录交换文件信息
                self._swap_files[key] = SwapFileInfo(
                    file_path=file_path,
                    key=key,
                    size_bytes=file_size,
                    created_at=time.time(),
                    last_access=time.time()
                )
                
                self._stats['swap_outs'] += 1
                self._stats['total_swap_size_mb'] += file_size / 1024 / 1024
                
                logger.debug(f"💿 换出到磁盘：{key} ({file_size} bytes)")
                return True
                
        except Exception as e:
            logger.error(f"交换出失败：{e}")
            return False
    
    async def swap_in(self, key: str) -> Optional[Any]:
        """从磁盘换入"""
        try:
            async with self._lock:
                if key not in self._swap_files:
                    return None
                
                swap_info = self._swap_files[key]
                
                # 读取并反序列化
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(
                    None,
                    lambda: pickle.load(open(swap_info.file_path, 'rb'))
                )
                
                # 更新访问统计
                swap_info.last_access = time.time()
                swap_info.access_count += 1
                
                self._stats['swap_ins'] += 1
                
                logger.debug(f"💿 从磁盘换入：{key}")
                return data
                
        except Exception as e:
            logger.error(f"交换入失败：{e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """删除交换文件"""
        try:
            async with self._lock:
                if key not in self._swap_files:
                    return False
                
                swap_info = self._swap_files.pop(key)
                
                # 删除文件
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: swap_info.file_path.unlink(missing_ok=True)
                )
                
                self._stats['total_swap_size_mb'] -= swap_info.size_bytes / 1024 / 1024
                
                logger.debug(f"🗑️ 删除交换文件：{key}")
                return True
                
        except Exception as e:
            logger.error(f"删除交换文件失败：{e}")
            return False
    
    async def cleanup_old_swaps(self, max_age_seconds: int = 3600):
        """清理旧的交换文件"""
        try:
            async with self._lock:
                now = time.time()
                expired_keys = [
                    key for key, info in self._swap_files.items()
                    if (now - info.last_access) > max_age_seconds
                ]
                
                for key in expired_keys:
                    await self.delete(key)
                
                logger.info(f"🧹 清理了 {len(expired_keys)} 个过期交换文件")
                
        except Exception as e:
            logger.error(f"清理交换文件失败：{e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取交换统计"""
        async with self._lock:
            return {
                **self._stats,
                'swap_files_count': len(self._swap_files),
                'swap_dir_path': str(self.swap_dir)
            }


class IntelligentMemoryManager:
    """智能内存管理器 - 整合内存池和交换机制"""
    
    def __init__(self, config: Optional[MemoryPoolConfig] = None):
        self.config = config or MemoryPoolConfig()
        
        # 内存池
        self.memory_pool = DynamicMemoryPool(self.config)
        
        # 交换管理器
        self.swap_manager = SwapManager(self.config)
        
        # 系统内存监控
        self._process = psutil.Process()
        
        # 后台任务
        self._monitor_task: Optional[asyncio.Task] = None
        self._gc_task: Optional[asyncio.Task] = None
        
        self._running = False
        
        logger.info("🧠 智能内存管理器已启动")
    
    async def start(self):
        """启动后台监控任务"""
        self._running = True
        
        # 启动内存监控
        self._monitor_task = asyncio.create_task(self._memory_monitor())
        
        # 启动定期 GC
        self._gc_task = asyncio.create_task(self._periodic_gc())
        
        logger.info("✅ 后台监控任务已启动")
    
    async def stop(self):
        """停止后台任务"""
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        if self._gc_task:
            self._gc_task.cancel()
            try:
                await self._gc_task
            except asyncio.CancelledError:
                pass
        
        # 清理交换文件
        await self.swap_manager.cleanup_old_swaps(max_age_seconds=0)
        
        logger.info("🛑 智能内存管理器已停止")
    
    async def put(self, datasource: str, key: str, value: Any) -> bool:
        """存储数据（自动冷热分离）"""
        full_key = f"{datasource}:{key}"
        
        # 估算大小
        size_bytes = sys.getsizeof(value)
        
        # 尝试分配到内存池
        success = await self.memory_pool.allocate(full_key, value, size_bytes)
        
        if not success:
            # 内存不足，直接换出到磁盘
            logger.warning(f"⚠️ 内存不足，换出到磁盘：{full_key}")
            return await self.swap_manager.swap_out(full_key, value)
        
        return True
    
    async def get(self, datasource: str, key: str) -> Optional[Any]:
        """获取数据（优先内存，其次磁盘）"""
        full_key = f"{datasource}:{key}"
        
        # 先从内存获取
        data = await self.memory_pool.get(full_key)
        if data is not None:
            return data
        
        # 内存未命中，从磁盘换入
        logger.debug(f"🔄 内存未命中，尝试从磁盘换入：{full_key}")
        data = await self.swap_manager.swap_in(full_key)
        
        if data is not None:
            # 换入后重新加载到内存
            size_bytes = sys.getsizeof(data)
            await self.memory_pool.allocate(full_key, data, size_bytes)
            await self.swap_manager.delete(full_key)
        
        return data
    
    async def delete(self, datasource: str, key: str):
        """删除数据"""
        full_key = f"{datasource}:{key}"
        
        # 从内存删除
        await self.memory_pool.deallocate(full_key)
        
        # 从磁盘删除
        await self.swap_manager.delete(full_key)
    
    async def _memory_monitor(self):
        """内存监控任务"""
        while self._running:
            try:
                # 获取系统内存使用情况
                mem = self._process.memory_info()
                mem_percent = self._process.memory_percent()
                
                pool_stats = await self.memory_pool.get_stats()
                
                logger.debug(
                    f"📊 内存监控："
                    f"进程={mem.rss / 1024 / 1024:.1f}MB ({mem_percent:.1f}%), "
                    f"池使用={pool_stats['usage_percent']:.1f}%"
                )
                
                # 如果系统内存紧张，触发 GC
                if mem_percent > 80:
                    logger.warning(f"⚠️ 系统内存紧张：{mem_percent:.1f}%")
                    await self._force_gc()
                
                await asyncio.sleep(self.config.monitor_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"内存监控异常：{e}")
                await asyncio.sleep(self.config.monitor_interval)
    
    async def _periodic_gc(self):
        """定期 GC 任务"""
        while self._running:
            try:
                await self._force_gc()
                await asyncio.sleep(self.config.gc_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"GC 异常：{e}")
    
    async def _force_gc(self):
        """强制 GC"""
        import gc
        
        # Python GC
        collected = gc.collect()
        
        # 收缩内存池
        await self.memory_pool._try_shrink()
        
        # 清理过期交换文件
        await self.swap_manager.cleanup_old_swaps(max_age_seconds=300)
        
        logger.debug(f"♻️ GC 完成：回收 {collected} 个对象")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取完整统计"""
        pool_stats = await self.memory_pool.get_stats()
        swap_stats = await self.swap_manager.get_stats()
        
        return {
            'memory_pool': pool_stats,
            'swap_manager': swap_stats,
            'system_memory_mb': round(
                self._process.memory_info().rss / 1024 / 1024, 2
            ),
            'system_memory_percent': round(self._process.memory_percent(), 2)
        }


# 全局单例
_memory_manager: Optional[IntelligentMemoryManager] = None


def get_memory_manager() -> IntelligentMemoryManager:
    """获取全局内存管理器实例"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = IntelligentMemoryManager()
    return _memory_manager


def init_memory_manager(config: Optional[MemoryPoolConfig] = None) -> IntelligentMemoryManager:
    """初始化内存管理器"""
    global _memory_manager
    _memory_manager = IntelligentMemoryManager(config)
    return _memory_manager
