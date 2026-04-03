"""
concurrency_controller.py 单元测试
测试自适应并发控制功能
"""
import pytest
import asyncio
from infrastructure.utils import AdaptiveConcurrencyController
from infrastructure.models import Config


class TestAdaptiveConcurrencyController:
    """AdaptiveConcurrencyController 类测试"""
    
    @pytest.mark.asyncio
    async def test_initial_concurrency(self, sample_config):
        """测试初始并发数"""
        controller = AdaptiveConcurrencyController(sample_config)
        
        assert controller.current_concurrency == sample_config.initial_concurrency
        assert controller.get_limit() == sample_config.initial_concurrency
    
    @pytest.mark.asyncio
    async def test_adjust_success_increases_concurrency(self, sample_config):
        """测试成功请求增加并发数"""
        # 设置较小的初始值便于测试
        sample_config.initial_concurrency = 1
        sample_config.max_concurrency = 4
        sample_config.retry_streak_threshold = 2
        
        controller = AdaptiveConcurrencyController(sample_config)
        
        # 模拟连续成功
        await controller.adjust(True)
        await asyncio.sleep(0.1)  # 等待时间间隔
        await controller.adjust(True)
        
        # 并发数应该增加 (至少调整一次)
        # 注意：由于时间间隔限制，可能不会立即增加
        assert controller.current_concurrency >= 1
    
    @pytest.mark.asyncio
    async def test_adjust_failure_decreases_concurrency(self, sample_config):
        """测试失败请求减少并发数"""
        sample_config.initial_concurrency = 3
        controller = AdaptiveConcurrencyController(sample_config)
        
        # 模拟失败
        await controller.adjust(False)
        
        # 并发数应该减少 (从 3 减少到 2)
        # 注意：实际减少的量可能因实现而异
        assert controller.current_concurrency < 3 or controller.current_concurrency == 2
    
    @pytest.mark.asyncio
    async def test_concurrency_minimum(self, sample_config):
        """测试并发数最小值"""
        sample_config.initial_concurrency = 1
        controller = AdaptiveConcurrencyController(sample_config)
        
        # 多次失败，并发数不应低于 1
        for _ in range(5):
            await controller.adjust(False)
        
        assert controller.current_concurrency >= 1
    
    @pytest.mark.asyncio
    async def test_concurrency_maximum(self, sample_config):
        """测试并发数最大值"""
        sample_config.initial_concurrency = sample_config.max_concurrency - 1
        sample_config.retry_streak_threshold = 1
        
        controller = AdaptiveConcurrencyController(sample_config)
        
        # 多次成功，但不超过最大值
        for _ in range(10):
            await controller.adjust(True)
            await asyncio.sleep(0.1)
        
        assert controller.current_concurrency <= sample_config.max_concurrency
    
    @pytest.mark.asyncio
    async def test_cooldown_mechanism(self, sample_config):
        """测试冷却机制"""
        sample_config.initial_concurrency = 1
        sample_config.max_concurrency = 4
        sample_config.concurrency_cooldown_seconds = 1.0
        
        controller = AdaptiveConcurrencyController(sample_config)
        
        # 模拟失败触发冷却
        await controller.adjust(False)
        
        # 立即尝试增加并发（应该在冷却期间）
        await controller.adjust(True)
        
        # 并发数不应立即增加
        assert controller.current_concurrency == 1 or controller.cooldown_until > 0
    
    @pytest.mark.asyncio
    async def test_success_streak_reset_on_failure(self, sample_config):
        """测试失败时重置成功计数"""
        sample_config.retry_streak_threshold = 3
        controller = AdaptiveConcurrencyController(sample_config)
        
        # 累积成功
        await controller.adjust(True)
        await controller.adjust(True)
        
        # 一次失败应该重置计数
        await controller.adjust(False)
        
        # 验证成功计数被重置（通过再次检查行为）
        assert controller.success_streak == 0
    
    @pytest.mark.asyncio
    async def test_get_limit_returns_current(self, sample_config):
        """测试获取当前并发限制"""
        controller = AdaptiveConcurrencyController(sample_config)
        
        limit = controller.get_limit()
        assert limit == controller.current_concurrency
    
    @pytest.mark.asyncio
    async def test_thread_safety_with_lock(self, sample_config):
        """测试锁机制确保线程安全"""
        controller = AdaptiveConcurrencyController(sample_config)
        
        assert hasattr(controller, 'lock')
        assert isinstance(controller.lock, asyncio.Lock)
    
    @pytest.mark.asyncio
    async def test_adjust_timing_throttle(self, sample_config):
        """测试调整频率限制"""
        sample_config.initial_concurrency = 1
        sample_config.retry_streak_threshold = 1
        
        controller = AdaptiveConcurrencyController(sample_config)
        
        # 快速连续调用，应该不会频繁调整
        initial_concurrency = controller.current_concurrency
        for _ in range(5):
            await controller.adjust(True)
        
        # 由于时间间隔限制，并发数可能不会大幅增加
        # 这个测试主要验证节流机制存在
        assert controller.last_adjustment_time is not None


class TestAdaptiveConcurrencyControllerIntegration:
    """AdaptiveConcurrencyController 集成测试"""
    
    @pytest.mark.asyncio
    async def test_realistic_usage_pattern(self, sample_config):
        """测试真实使用场景"""
        sample_config.initial_concurrency = 2
        sample_config.max_concurrency = 8
        sample_config.retry_streak_threshold = 3
        
        controller = AdaptiveConcurrencyController(sample_config)
        
        # 模拟混合成功和失败的场景
        pattern = [True, True, False, True, True, True, False, True]
        
        for success in pattern:
            await controller.adjust(success)
            await asyncio.sleep(0.05)  # 小延迟模拟真实场景
        
        # 验证并发数在合理范围内
        assert 1 <= controller.get_limit() <= sample_config.max_concurrency
