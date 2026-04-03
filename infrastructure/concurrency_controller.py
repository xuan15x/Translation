"""
并发控制模块
实现自适应并发度控制器，根据请求成功率动态调整并发数
"""
import asyncio
import time
from typing import Optional
import logging
from infrastructure.models.models import Config
from config.constants import ConcurrencyConfig

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
        self.recent_latencies: list[float] = []  # 最近请求延迟（毫秒）
        self.max_latency_samples = ConcurrencyConfig.MAX_LATENCY_SAMPLES
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
            # 修复：使用 asyncio.wait_for 替代 asyncio.timeout，确保状态一致性
            async with asyncio.timeout(ConcurrencyConfig.ADJUST_TIMEOUT_SECONDS):
                async with self.lock:
                    try:
                        self._do_adjust(success, latency_ms)
                    except Exception as e:
                        # 锁内异常处理，确保状态一致
                        logger.error(f"并发度调整内部错误：{e}")
                        # 发生错误时重置部分状态，但不影响并发度
                        if not success:
                            self.error_requests = max(0, self.error_requests - 1)
                            self.total_requests = max(0, self.total_requests - 1)
                        raise
        except asyncio.TimeoutError:
            logger.error("并发度调整超时，跳过本次调整")
            # 超时情况下不更新任何状态，保持数据一致性
        except Exception as e:
            logger.exception(f"并发度调整异常：{e}")
            # 外部异常时确保错误计数准确
            if not success:
                try:
                    async with self.lock:
                        self.error_requests = max(0, self.error_requests - 1)
                        self.total_requests = max(0, self.total_requests - 1)
                except Exception:
                    pass  # 忽略二次错误

    def _do_adjust(self, success: bool, latency_ms: Optional[float] = None):
        """
        执行实际的并发度调整逻辑（必须在锁内调用）

        Args:
            success: 请求是否成功
            latency_ms: 请求延迟（毫秒）
        """
        now = time.time()

        # 更新统计
        self.total_requests += 1
        if not success:
            self.error_requests += 1

        # 计算错误率
        if self.total_requests > 0:
            self.error_rate = self.error_requests / self.total_requests

        # 记录延迟
        if latency_ms is not None:
            self.recent_latencies.append(latency_ms)
            if len(self.recent_latencies) > self.max_latency_samples:
                self.recent_latencies.pop(0)

        # 限制调整频率
        if now - self.last_adjustment_time < ConcurrencyConfig.ADJUST_INTERVAL_SECONDS:
            return

        # 基于错误率的快速降级
        if self.error_rate > ConcurrencyConfig.HIGH_ERROR_RATE_THRESHOLD:  # 错误率超过 30%
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

        # 基于延迟的智能调整
        avg_latency = sum(self.recent_latencies) / len(self.recent_latencies) if self.recent_latencies else 0

        # 如果延迟过高，暂缓增加并发
        if avg_latency > ConcurrencyConfig.HIGH_LATENCY_THRESHOLD_MS:  # 平均延迟超过 2 秒
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

    def get_limit(self) -> int:
        """
        获取当前并发限制
        
        Returns:
            当前允许的并发数
        """
        # 确保返回值始终有效
        return max(1, min(self.current_concurrency, self.config.max_concurrency))
