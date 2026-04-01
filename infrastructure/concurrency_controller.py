"""
并发控制模块
实现自适应并发度控制器，根据请求成功率动态调整并发数
"""
import asyncio
import time
from typing import Optional
import logging
from .models import Config

logger = logging.getLogger(__name__)


class AdaptiveConcurrencyController:
    """自适应并发度控制器 - 优化版"""
    
    def __init__(self, config: Config):
        """
        初始化并发控制器
        
        Args:
            config: 系统配置对象
        """
        self.config = config
        self.current_concurrency = config.initial_concurrency
        self.success_streak = 0
        self.last_adjustment_time = time.time()
        self.lock = asyncio.Lock()
        self.cooldown_until = 0.0
        # 优化 1: 添加性能指标追踪
        self.recent_latencies = []  # 最近请求延迟（毫秒）
        self.max_latency_samples = 20
        self.error_rate = 0.0
        self.total_requests = 0
        self.error_requests = 0

    async def adjust(self, success: bool, latency_ms: Optional[float] = None):
        """
        根据请求结果和延迟调整并发度
        
        Args:
            success: 请求是否成功
            latency_ms: 请求延迟（毫秒），用于性能感知调整
        """
        try:
            # 使用超时防止死锁
            async with asyncio.timeout(5.0):
                async with self.lock:
                    now = time.time()
                    
                    # 更新统计
                    self.total_requests += 1
                    if not success:
                        self.error_requests += 1
                    
                    # 计算错误率
                    if self.total_requests > 0:
                        self.error_rate = self.error_requests / self.total_requests
                    
                    # 优化 2: 记录延迟
                    if latency_ms is not None:
                        self.recent_latencies.append(latency_ms)
                        if len(self.recent_latencies) > self.max_latency_samples:
                            self.recent_latencies.pop(0)
                    
                    # 限制调整频率
                    if now - self.last_adjustment_time < 2:
                        return
                    
                    # 优化 3: 基于错误率的快速降级
                    if self.error_rate > 0.3:  # 错误率超过 30%
                        if self.current_concurrency > 1:
                            old_concurrency = self.current_concurrency
                            self.current_concurrency = max(1, int(self.current_concurrency * 0.5))
                            self.cooldown_until = now + self.config.concurrency_cooldown_seconds * 2
                            self.success_streak = 0
                            self.last_adjustment_time = now
                            logger.warning(
                                f"⚠️ 高错误率触发快速降级：{old_concurrency} -> {self.current_concurrency} "
                                f"(错误率：{self.error_rate:.1%})"
                            )
                        return
                    
                    if not success:
                        # 失败时降低并发度
                        if self.current_concurrency > 1:
                            old_concurrency = self.current_concurrency
                            self.current_concurrency = max(1, self.current_concurrency - 1)
                            self.cooldown_until = now + self.config.concurrency_cooldown_seconds
                            self.success_streak = 0
                            self.last_adjustment_time = now
                            logger.warning(
                                f"并发度降低：{old_concurrency} -> {self.current_concurrency} "
                                f"(冷却至 {self.cooldown_until:.2f})"
                            )
                        return
                    
                    # 冷却期间不增加并发
                    if now < self.cooldown_until:
                        remaining = self.cooldown_until - now
                        logger.debug(f"仍在冷却期，剩余 {remaining:.2f}s")
                        return
                    
                    # 优化 4: 基于延迟的智能调整
                    avg_latency = sum(self.recent_latencies) / len(self.recent_latencies) if self.recent_latencies else 0
                    
                    # 如果延迟过高，暂缓增加并发
                    if avg_latency > 2000:  # 平均延迟超过 2 秒
                        logger.debug(f"延迟较高 ({avg_latency:.0f}ms)，暂缓提升并发度")
                        return
                    
                    # 成功累积，增加并发度
                    self.success_streak += 1
                    if (self.success_streak >= self.config.retry_streak_threshold and 
                        self.current_concurrency < self.config.max_concurrency):
                        old_concurrency = self.current_concurrency
                        self.current_concurrency += 1
                        self.success_streak = 0
                        self.last_adjustment_time = now
                        logger.info(
                            f"并发度提升：{old_concurrency} -> {self.current_concurrency} "
                            f"(连续成功 {self.config.retry_streak_threshold} 次，平均延迟:{avg_latency:.0f}ms)"
                        )
        except asyncio.TimeoutError:
            logger.error("并发度调整超时，跳过本次调整")
        except Exception as e:
            logger.exception(f"并发度调整异常：{e}")

    def get_limit(self) -> int:
        """
        获取当前并发限制
        
        Returns:
            当前允许的并发数
        """
        # 确保返回值始终有效
        return max(1, min(self.current_concurrency, self.config.max_concurrency))
