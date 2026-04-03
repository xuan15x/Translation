"""
性能基准测试和压力测试
"""
import pytest
import asyncio
import time
import os
import tempfile
from datetime import datetime
import statistics
import pandas as pd

from infrastructure.models import Config, TaskContext
# 旧的测试已废弃
# from business_logic.terminology_manager import TerminologyManager
# from business_logic.workflow_orchestrator import WorkflowOrchestrator
from infrastructure.cache import TerminologyCache, LRUCache
from infrastructure.utils import PerformanceMonitor


class TestPerformance:
    """性能基准测试"""
    
    @pytest.fixture
    def performance_config(self):
        """性能测试配置"""
        config = Config()
        config.batch_size = 10
        config.max_concurrency = 5
        return config
    
    def test_cache_performance(self):
        """测试缓存性能"""
        cache = LRUCache(capacity=1000)
        
        # 预热缓存
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 写入缓存
            for i in range(500):
                loop.run_until_complete(cache.set(f"key_{i}", f"value_{i}"))
            
            # 测试读取性能
            iterations = 1000
            start_time = time.time()
            
            for _ in range(iterations):
                key_idx = _ % 500  # 在已缓存的范围内
                loop.run_until_complete(cache.get(f"key_{key_idx}"))
            
            elapsed = time.time() - start_time
            avg_time = (elapsed / iterations) * 1000  # 转换为毫秒
            
            print(f"\n缓存读取性能:")
            print(f"  总耗时：{elapsed:.3f}s")
            print(f"  平均耗时：{avg_time:.3f}ms/次")
            print(f"  QPS: {iterations / elapsed:.0f}")
            
            # 断言：平均响应时间应小于 1ms
            assert avg_time < 1.0, f"缓存响应时间过长：{avg_time}ms"
            
        finally:
            loop.close()
    
    @pytest.mark.asyncio
    async def test_terminology_lookup_performance(self, performance_config):
        """测试术语查询性能"""
        # 创建大型术语库
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            term_file = f.name
        
        try:
            # 生成 1000 条术语
            data = {
                '中文原文': [f'术语_{i}' for i in range(1000)],
                '英语': [f'Term_{i}' for i in range(1000)],
                '法语': [f'Terme_{i}' for i in range(1000)],
            }
            df = pd.DataFrame(data)
            df.to_excel(term_file, index=False, engine='openpyxl')
            
            tm = TerminologyManager(term_file, performance_config)
            
            # 性能测试
            test_queries = [f'术语_{i}' for i in range(100)]
            
            start_time = time.time()
            
            for query in test_queries:
                await tm.find_similar(query, "英语")
            
            elapsed = time.time() - start_time
            avg_time = (elapsed / len(test_queries)) * 1000
            
            print(f"\n术语查询性能:")
            print(f"  查询数量：{len(test_queries)}")
            print(f"  总耗时：{elapsed:.3f}s")
            print(f"  平均耗时：{avg_time:.3f}ms/次")
            
            # 验证性能指标
            assert avg_time < 50, f"术语查询过慢：{avg_time}ms/次"
            
            await tm.shutdown()
            
        finally:
            if os.path.exists(term_file):
                os.remove(term_file)
    
    def test_memory_usage(self, performance_config):
        """测试内存使用"""
        import tracemalloc
        
        # 创建术语库管理器
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            term_file = f.name
        
        try:
            # 生成 5000 条术语
            data = {
                '中文原文': [f'术语_{i}' for i in range(5000)],
                '英语': [f'Term_{i}' for i in range(5000)],
            }
            pd.DataFrame(data).to_excel(term_file, index=False)
            
            # 开始内存跟踪
            tracemalloc.start()
            
            tm = TerminologyManager(term_file, performance_config)
            
            # 执行一些操作
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                for i in range(100):
                    loop.run_until_complete(
                        tm.find_similar(f'术语_{i}', '英语')
                    )
            finally:
                loop.close()
            
            # 获取内存统计
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            current_mb = current / (1024 * 1024)
            peak_mb = peak / (1024 * 1024)
            
            print(f"\n内存使用:")
            print(f"  当前内存：{current_mb:.2f}MB")
            print(f"  峰值内存：{peak_mb:.2f}MB")
            
            # 断言：峰值内存不应超过 100MB
            assert peak_mb < 100, f"内存使用过高：{peak_mb}MB"
            
        finally:
            if os.path.exists(term_file):
                os.remove(term_file)


class TestStress:
    """压力测试"""
    
    @pytest.fixture
    def stress_config(self):
        """压力测试配置"""
        config = Config()
        config.batch_size = 50
        config.max_concurrency = 10
        config.timeout = 30
        return config
    
    @pytest.mark.asyncio
    async def test_high_concurrency(self, stress_config):
        """高并发压力测试"""
        # 创建临时术语库
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            term_file = f.name
        
        try:
            # 初始化术语库
            pd.DataFrame({
                '中文原文': [f'术语_{i}' for i in range(100)],
                '英语': [f'Term_{i}' for i in range(100)],
            }).to_excel(term_file, index=False)
            
            tm = TerminologyManager(term_file, stress_config)
            
            # 模拟高并发查询
            async def concurrent_query(query_id):
                return await tm.find_similar(f'术语_{query_id % 100}', '英语')
            
            # 启动 100 个并发任务
            tasks = [concurrent_query(i) for i in range(100)]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - start_time
            
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = sum(1 for r in results if isinstance(r, Exception))
            
            print(f"\n高并发测试:")
            print(f"  并发任务数：100")
            print(f"  总耗时：{elapsed:.2f}s")
            print(f"  成功：{successful}")
            print(f"  失败：{failed}")
            print(f"  吞吐量：{100 / elapsed:.1f} 任务/秒")
            
            # 验证：成功率应大于 90%
            success_rate = successful / len(results) * 100
            assert success_rate > 90, f"成功率过低：{success_rate}%"
            
            await tm.shutdown()
            
        finally:
            if os.path.exists(term_file):
                os.remove(term_file)
    
    @pytest.mark.asyncio
    async def test_long_running(self, stress_config):
        """长时间运行稳定性测试"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            term_file = f.name
        
        try:
            # 小型术语库
            pd.DataFrame({
                '中文原文': ['术语 1', '术语 2'],
                '英语': ['Term 1', 'Term 2'],
            }).to_excel(term_file, index=False)
            
            tm = TerminologyManager(term_file, stress_config)
            
            # 持续运行 60 秒
            duration_seconds = 60
            total_queries = 0
            errors = []
            
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                try:
                    await tm.find_similar("术语 1", "英语")
                    await tm.add_entry(f"新术语_{total_queries}", "英语", f"Term_{total_queries}")
                    total_queries += 1
                    
                    # 每 100 次查询后短暂休息
                    if total_queries % 100 == 0:
                        await asyncio.sleep(0.1)
                
                except Exception as e:
                    errors.append(str(e))
            
            elapsed = time.time() - start_time
            
            print(f"\n长时间运行测试:")
            print(f"  运行时长：{elapsed:.1f}s")
            print(f"  总查询数：{total_queries}")
            print(f"  错误数：{len(errors)}")
            print(f"  平均速度：{total_queries / elapsed:.1f} 查询/秒")
            
            # 验证：错误率应小于 1%
            error_rate = len(errors) / total_queries * 100 if total_queries > 0 else 0
            assert error_rate < 1, f"错误率过高：{error_rate}%"
            
            await tm.shutdown()
            
        finally:
            if os.path.exists(term_file):
                os.remove(term_file)


class TestLoadBalancing:
    """负载均衡测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_writes(self):
        """测试并发写入性能"""
        cache = TerminologyCache(capacity=1000)
        
        async def writer(writer_id, count):
            for i in range(count):
                await cache.set_exact_match(
                    f"key_{writer_id}_{i}",
                    "英语",
                    {"translation": f"Value_{i}"}
                )
        
        # 10 个并发写入者，每个写入 100 条
        writers = [writer(i, 100) for i in range(10)]
        
        start_time = time.time()
        await asyncio.gather(*writers)
        elapsed = time.time() - start_time
        
        total_writes = 10 * 100
        
        print(f"\n并发写入测试:")
        print(f"  总写入数：{total_writes}")
        print(f"  总耗时：{elapsed:.2f}s")
        print(f"  写入速度：{total_writes / elapsed:.1f} 条/秒")
        
        # 验证所有数据都已写入
        stats = await cache.get_stats()
        assert stats['exact_matches'] == total_writes, \
            f"写入数量不匹配：期望{total_writes}, 实际{stats['exact_matches']}"


# 辅助函数
def run_performance_tests():
    """运行所有性能测试并生成报告"""
    import subprocess
    
    print("=" * 60)
    print("性能测试报告")
    print("=" * 60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 运行 pytest 性能测试
    result = subprocess.run([
        'pytest', 
        'tests/test_performance.py',
        '-v',
        '--tb=short'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    run_performance_tests()
