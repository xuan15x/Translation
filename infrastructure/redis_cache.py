"""
Redis 缓存模块
提供高性能的术语库 Redis 缓存支持，适用于高并发场景
"""
import json
import redis.asyncio as redis
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class RedisCacheConfig:
    """Redis 缓存配置"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    max_connections: int = 50
    retry_on_timeout: bool = True
    
    # 键前缀
    key_prefix: str = "translation:terminology:"
    
    # 过期时间（秒）
    default_ttl: int = 3600  # 默认 1 小时
    exact_match_ttl: int = 7200  # 精确匹配 2 小时
    fuzzy_match_ttl: int = 1800  # 模糊匹配 30 分钟


class RedisTerminologyCache:
    """术语库 Redis 缓存管理器"""
    
    def __init__(self, config: RedisCacheConfig):
        """
        初始化 Redis 缓存
        
        Args:
            config: Redis 配置对象
        """
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.connected = False
        self.stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0,
            'connections': 0
        }
    
    async def connect(self):
        """连接到 Redis 服务器"""
        if not self.connected:
            try:
                pool = redis.ConnectionPool(
                    host=self.config.host,
                    port=self.config.port,
                    db=self.config.db,
                    password=self.config.password,
                    decode_responses=self.config.decode_responses,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    max_connections=self.config.max_connections,
                    retry_on_timeout=self.config.retry_on_timeout
                )
                
                self.redis_client = redis.Redis(connection_pool=pool)
                
                # 测试连接
                await self.redis_client.ping()
                self.connected = True
                self.stats['connections'] += 1
                
                logger.info(f"✅ Redis 已连接：{self.config.host}:{self.config.port}")
                
            except Exception as e:
                logger.error(f"❌ Redis 连接失败：{e}")
                self.connected = False
                self.stats['errors'] += 1
                raise
    
    async def disconnect(self):
        """断开 Redis 连接"""
        if self.redis_client and self.connected:
            await self.redis_client.close()
            self.connected = False
            logger.info("🔒 Redis 连接已关闭")
    
    def _make_key(self, *parts: str) -> str:
        """生成 Redis 键"""
        return f"{self.config.key_prefix}{':'.join(parts)}"
    
    async def get_exact_match(self, src: str, lang: str) -> Optional[Dict]:
        """
        获取精确匹配结果
        
        Args:
            src: 源文本
            lang: 目标语言
            
        Returns:
            精确匹配结果，如果不存在则返回 None
        """
        if not self.connected:
            return None
        
        try:
            key = self._make_key("exact", src, lang)
            value = await self.redis_client.get(key)
            
            if value:
                self.stats['hits'] += 1
                return json.loads(value)
            else:
                self.stats['misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Redis 获取精确匹配失败：{e}")
            self.stats['errors'] += 1
            return None
    
    async def set_exact_match(self, src: str, lang: str, result: Dict):
        """
        设置精确匹配结果
        
        Args:
            src: 源文本
            lang: 目标语言
            result: 匹配结果
        """
        if not self.connected:
            return
        
        try:
            key = self._make_key("exact", src, lang)
            value = json.dumps(result, ensure_ascii=False)
            
            await self.redis_client.setex(
                key,
                self.config.exact_match_ttl,
                value
            )
            
        except Exception as e:
            logger.error(f"Redis 设置精确匹配失败：{e}")
            self.stats['errors'] += 1
    
    async def get_fuzzy_matches(self, src: str, lang: str) -> Optional[List[Dict]]:
        """
        获取模糊匹配结果列表
        
        Args:
            src: 源文本
            lang: 目标语言
            
        Returns:
            模糊匹配结果列表
        """
        if not self.connected:
            return None
        
        try:
            key = self._make_key("fuzzy", src, lang)
            value = await self.redis_client.get(key)
            
            if value:
                self.stats['hits'] += 1
                return json.loads(value)
            else:
                self.stats['misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Redis 获取模糊匹配失败：{e}")
            self.stats['errors'] += 1
            return None
    
    async def set_fuzzy_matches(self, src: str, lang: str, matches: List[Dict]):
        """
        设置模糊匹配结果列表
        
        Args:
            src: 源文本
            lang: 目标语言
            matches: 匹配结果列表
        """
        if not self.connected:
            return
        
        try:
            key = self._make_key("fuzzy", src, lang)
            value = json.dumps(matches, ensure_ascii=False)
            
            await self.redis_client.setex(
                key,
                self.config.fuzzy_match_ttl,
                value
            )
            
        except Exception as e:
            logger.error(f"Redis 设置模糊匹配失败：{e}")
            self.stats['errors'] += 1
    
    async def get_terminology_entry(self, src: str) -> Optional[Dict]:
        """
        获取完整术语条目
        
        Args:
            src: 源文本
            
        Returns:
            术语条目字典 {language: translation}
        """
        if not self.connected:
            return None
        
        try:
            key = self._make_key("term", src)
            value = await self.redis_client.hgetall(key)
            
            if value:
                self.stats['hits'] += 1
                return value
            else:
                self.stats['misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Redis 获取术语条目失败：{e}")
            self.stats['errors'] += 1
            return None
    
    async def set_terminology_entry(self, src: str, translations: Dict[str, str]):
        """
        设置完整术语条目
        
        Args:
            src: 源文本
            translations: 翻译字典 {language: translation}
        """
        if not self.connected:
            return
        
        try:
            key = self._make_key("term", src)
            
            # 使用 Hash 存储多个语言的翻译
            pipeline = self.redis_client.pipeline()
            await pipeline.hset(key, mapping=translations)
            await pipeline.expire(key, self.config.default_ttl)
            await pipeline.execute()
            
        except Exception as e:
            logger.error(f"Redis 设置术语条目失败：{e}")
            self.stats['errors'] += 1
    
    async def add_terminology_translation(self, src: str, lang: str, translation: str):
        """
        添加或更新单个翻译
        
        Args:
            src: 源文本
            lang: 目标语言
            translation: 翻译文本
        """
        if not self.connected:
            return
        
        try:
            key = self._make_key("term", src)
            await self.redis_client.hset(key, lang, translation)
            await self.redis_client.expire(key, self.config.default_ttl)
            
        except Exception as e:
            logger.error(f"Redis 添加翻译失败：{e}")
            self.stats['errors'] += 1
    
    async def delete_terminology(self, src: str):
        """
        删除术语条目
        
        Args:
            src: 源文本
        """
        if not self.connected:
            return
        
        try:
            key = self._make_key("term", src)
            await self.redis_client.delete(key)
            
            # 同时删除相关的精确/模糊匹配缓存
            pattern = self._make_key("*", src, "*")
            async for k in self.redis_client.scan_iter(match=pattern):
                await self.redis_client.delete(k)
            
        except Exception as e:
            logger.error(f"Redis 删除术语失败：{e}")
            self.stats['errors'] += 1
    
    async def invalidate_cache(self, src: str):
        """
        使某个术语的所有缓存失效
        
        Args:
            src: 源文本
        """
        await self.delete_terminology(src)
    
    async def clear_all(self):
        """清空所有缓存"""
        if not self.connected:
            return
        
        try:
            pattern = self._make_key("*")
            async for k in self.redis_client.scan_iter(match=pattern):
                await self.redis_client.delete(k)
            
            logger.info("🧹 Redis 缓存已清空")
            
        except Exception as e:
            logger.error(f"Redis 清空缓存失败：{e}")
            self.stats['errors'] += 1
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0.0
        
        stats = {
            **self.stats,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'connected': self.connected
        }
        
        # 如果已连接，获取 Redis 服务器信息
        if self.connected:
            try:
                info = await self.redis_client.info('stats')
                stats['redis_used_memory'] = info.get('used_memory', 'N/A')
                stats['redis_connected_clients'] = info.get('connected_clients', 'N/A')
            except:
                pass
        
        return stats
    
    async def health_check(self) -> bool:
        """健康检查"""
        if not self.connected:
            return False
        
        try:
            await self.redis_client.ping()
            return True
        except:
            return False


# 全局单例
_redis_cache: Optional[RedisTerminologyCache] = None


def get_redis_cache(config: Optional[RedisCacheConfig] = None) -> RedisTerminologyCache:
    """
    获取全局 Redis 缓存实例
    
    Args:
        config: Redis 配置，如果为 None 则使用默认配置
        
    Returns:
        Redis 缓存实例
    """
    global _redis_cache
    
    if _redis_cache is None:
        if config is None:
            config = RedisCacheConfig()
        _redis_cache = RedisTerminologyCache(config)
    
    return _redis_cache


async def init_redis_cache(host: str = "localhost", port: int = 6379, 
                          password: Optional[str] = None, **kwargs) -> RedisTerminologyCache:
    """
    初始化并连接 Redis 缓存
    
    Args:
        host: Redis 主机地址
        port: Redis 端口
        password: Redis 密码（可选）
        **kwargs: 其他配置参数
        
    Returns:
        已连接的 Redis 缓存实例
    """
    config = RedisCacheConfig(
        host=host,
        port=port,
        password=password,
        **kwargs
    )
    
    cache = get_redis_cache(config)
    await cache.connect()
    
    return cache
