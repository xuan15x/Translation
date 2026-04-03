"""
缓存模块
实现 LRU 缓存机制，提升术语查询性能
"""
import asyncio
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    timestamp: float
    hit_count: int = 0


class LRUCache:
    """LRU 缓存实现 - 优化版"""
    
    def __init__(self, capacity: int = 1000):
        """
        初始化 LRU 缓存
        
        Args:
            capacity: 缓存容量（最大条目数）
        """
        self.capacity = capacity
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = asyncio.Lock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        # 优化 1: 添加内存限制
        self.max_memory_mb = 100  # 默认 100MB
        self._current_memory_estimate = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值 - 优化版"""
        async with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            # 移动到末尾（最近使用）
            entry = self.cache.pop(key)
            entry.hit_count += 1
            self.cache[key] = entry
            
            self.stats['hits'] += 1
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值 - 优化版"""
        async with self.lock:
            # 如果已存在，先删除
            if key in self.cache:
                old_entry = self.cache.pop(key)
                self._update_memory_estimate(-self._estimate_size(old_entry))
            
            # 创建新条目
            new_entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                hit_count=0
            )
            
            # 优化 2: 内存检查，超出则清理
            estimated_size = self._estimate_size(new_entry)
            while (len(self.cache) >= self.capacity or 
                   self._current_memory_estimate + estimated_size > self.max_memory_mb * 1024 * 1024):
                if not self.cache:
                    break
                # 淘汰最旧的条目
                _, oldest = self.cache.popitem(last=False)
                self._update_memory_estimate(-self._estimate_size(oldest))
                self.stats['evictions'] += 1
            
            # 添加新条目
            self.cache[key] = new_entry
            self._update_memory_estimate(estimated_size)
    
    def _estimate_size(self, entry: CacheEntry) -> int:
        """估算缓存条目的内存占用（字节）"""
        import sys
        base_size = sys.getsizeof(entry)
        value_size = sys.getsizeof(entry.value) if hasattr(entry.value, '__sizeof__') else 100
        return base_size + value_size
    
    def _update_memory_estimate(self, delta: int):
        """更新内存估算"""
        self._current_memory_estimate += delta
        if self._current_memory_estimate < 0:
            self._current_memory_estimate = 0
    
    async def delete(self, key: str):
        """删除缓存条目"""
        async with self.lock:
            if key in self.cache:
                self.cache.pop(key)
    
    async def clear(self):
        """清空缓存"""
        async with self.lock:
            self.cache.clear()
            self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    async def get_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        async with self.lock:
            total = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total * 100) if total > 0 else 0.0
            
            return {
                **self.stats,
                'total_requests': total,
                'hit_rate_percent': round(hit_rate, 2),
                'current_size': len(self.cache),
                'capacity': self.capacity
            }
    
    async def cleanup_expired(self, max_age_seconds: int = 3600):
        """
        清理过期的缓存条目
        
        Args:
            max_age_seconds: 最大存活时间（秒）
        """
        async with self.lock:
            now = time.time()
            expired_keys = [
                key for key, entry in self.cache.items()
                if (now - entry.timestamp) > max_age_seconds
            ]
            
            for key in expired_keys:
                self.cache.pop(key)
                self.stats['evictions'] += 1


class TerminologyCache:
    """术语查询专用缓存"""
    
    def __init__(self, capacity: int = 2000):
        """
        初始化术语缓存
        
        Args:
            capacity: 缓存容量
        """
        self.cache = LRUCache(capacity)
        self.exact_hit_cache: Dict[str, Dict] = {}  # 精确命中缓存
        self.fuzzy_hit_cache: Dict[str, Tuple[Dict, int]] = {}  # 模糊匹配缓存
        self.lock = asyncio.Lock()
    
    def _make_key(self, src: str, lang: str) -> str:
        """生成缓存键"""
        return f"{src}:{lang}"
    
    async def get_exact_match(self, src: str, lang: str) -> Optional[Dict]:
        """
        获取精确匹配结果
        
        Args:
            src: 源文本
            lang: 目标语言
            
        Returns:
            精确匹配结果
        """
        key = self._make_key(src, lang)
        async with self.lock:
            return self.exact_hit_cache.get(key)
    
    async def set_exact_match(self, src: str, lang: str, result: Dict):
        """
        设置精确匹配结果
        
        Args:
            src: 源文本
            lang: 目标语言
            result: 匹配结果
        """
        key = self._make_key(src, lang)
        async with self.lock:
            self.exact_hit_cache[key] = result
    
    async def get_fuzzy_match(self, src: str, lang: str) -> Optional[Tuple[Dict, int]]:
        """
        获取模糊匹配结果
        
        Args:
            src: 源文本
            lang: 目标语言
            
        Returns:
            (匹配结果，分数) 元组
        """
        key = self._make_key(src, lang)
        async with self.lock:
            return self.fuzzy_hit_cache.get(key)
    
    async def set_fuzzy_match(self, src: str, lang: str, result: Dict, score: int):
        """
        设置模糊匹配结果
        
        Args:
            src: 源文本
            lang: 目标语言
            result: 匹配结果
            score: 匹配分数
        """
        key = self._make_key(src, lang)
        async with self.lock:
            self.fuzzy_hit_cache[key] = (result, score)
    
    async def invalidate_source(self, src: str):
        """
        使特定源文本的所有缓存失效
        
        Args:
            src: 源文本
        """
        async with self.lock:
            # 清除所有包含该源文本的缓存键
            keys_to_delete = [
                key for key in self.exact_hit_cache.keys()
                if key.startswith(f"{src}:")
            ]
            for key in keys_to_delete:
                del self.exact_hit_cache[key]
            
            keys_to_delete = [
                key for key in self.fuzzy_hit_cache.keys()
                if key.startswith(f"{src}:")
            ]
            for key in keys_to_delete:
                del self.fuzzy_hit_cache[key]
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        exact_stats = await self.cache.get_stats()
        
        async with self.lock:
            return {
                'exact_matches': len(self.exact_hit_cache),
                'fuzzy_matches': len(self.fuzzy_hit_cache),
                'lru_cache': exact_stats
            }
    
    async def clear_all(self):
        """清空所有缓存"""
        async with self.lock:
            self.exact_hit_cache.clear()
            self.fuzzy_hit_cache.clear()
        await self.cache.clear()
