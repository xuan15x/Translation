"""
性能优化演示脚本
展示如何使用新的缓存、连接池和性能监控功能
"""
import asyncio
import time
from terminology_manager import TerminologyManager
from models import Config
from infrastructure.cache import TerminologyCache
from infrastructure.performance_monitor import (
    start_performance_monitoring,
    get_performance_stats,
    stop_performance_monitoring
)


async def demo_cache_performance():
    """演示缓存性能提升"""
    print("=" * 60)
    print("📊 术语库缓存性能演示")
    print("=" * 60)
    
    # 创建配置和术语管理器
    config = Config()
    tm = TerminologyManager("tests/data/test_terms.xlsx", config)
    
    # 启用内存跟踪
    tm.enable_memory_tracking()
    
    # 启动性能监控
    await start_performance_monitoring(sample_interval=0.5)
    
    test_queries = [
        ("你好", "英语"),
        ("世界", "英语"),
        ("测试", "法语"),
        ("欢迎", "日语"),
    ]
    
    print("\n🔍 第一轮查询（无缓存）...")
    start_time = time.time()
    
    for src, lang in test_queries * 10:
        result = await tm.find_similar(src, lang)
    
    first_round_time = time.time() - start_time
    print(f"⏱️  第一轮耗时：{first_round_time:.3f}s")
    
    print("\n🔍 第二轮查询（使用缓存）...")
    start_time = time.time()
    
    for src, lang in test_queries * 10:
        result = await tm.find_similar(src, lang)
    
    second_round_time = time.time() - start_time
    print(f"⏱️  第二轮耗时：{second_round_time:.3f}s")
    
    speedup = first_round_time / second_round_time if second_round_time > 0 else float('inf')
    print(f"\n🚀 性能提升：{speedup:.2f}x")
    
    # 获取缓存统计
    cache_stats = await tm.cache.get_stats()
    print(f"\n📈 缓存统计:")
    print(f"  精确命中：{cache_stats.get('exact_matches', 0)}")
    print(f"  模糊匹配：{cache_stats.get('fuzzy_matches', 0)}")
    print(f"  LRU 缓存命中率：{cache_stats.get('lru_cache', {}).get('hit_rate_percent', 0)}%")
    
    # 获取性能统计
    perf_stats = get_performance_stats()
    print(f"\n💻 系统性能:")
    print(f"  当前 CPU: {perf_stats['current']['cpu_percent']:.1f}%")
    print(f"  平均 CPU: {perf_stats['averages'].get('avg_cpu_percent', 0):.1f}%")
    print(f"  峰值 CPU: {perf_stats['peak_cpu']:.1f}%")
    print(f"  当前内存：{perf_stats['current']['memory_mb']:.1f}MB")
    print(f"  峰值内存：{perf_stats['peak_memory_mb']:.1f}MB")
    
    # 获取内存使用情况
    memory_usage = tm.get_memory_usage()
    print(f"\n🧠 内存使用:")
    print(f"  数据库大小：{memory_usage['db_size_mb']:.2f}MB")
    print(f"  当前内存：{memory_usage.get('current_memory_mb', 0):.2f}MB")
    print(f"  峰值内存：{memory_usage.get('peak_memory_mb', 0):.2f}MB")
    
    # 优化内存
    print("\n🧹 执行内存优化...")
    await tm.optimize_memory()
    
    # 停止监控
    await stop_performance_monitoring()
    
    print("\n✅ 演示完成!")
    print("=" * 60)


async def demo_batch_processing():
    """演示批量处理优化"""
    print("\n" + "=" * 60)
    print("📦 批量添加术语性能演示")
    print("=" * 60)
    
    config = Config()
    tm = TerminologyManager("tests/data/test_terms.xlsx", config)
    
    # 生成测试数据
    test_entries = [
        (f"测试术语{i}", "英语", f"Test Term {i}")
        for i in range(500)
    ]
    
    print(f"\n📝 准备添加 {len(test_entries)} 条术语...")
    
    start_time = time.time()
    
    # 使用优化的批量添加
    stats = await tm.batch_add_entries_optimized(
        test_entries,
        batch_size=50
    )
    
    elapsed = time.time() - start_time
    
    print(f"\n⏱️  总耗时：{elapsed:.2f}s")
    print(f"📊 处理速度：{len(test_entries) / elapsed:.1f} 条/秒")
    print(f"📈 结果:")
    print(f"  新增：{stats['added']} 条")
    print(f"  更新：{stats['updated']} 条")
    print(f"  跳过：{stats['skipped']} 条")
    
    # 获取性能统计
    perf_stats = await tm.get_performance_stats()
    print(f"\n💻 性能统计:")
    print(f"  数据库条目：{perf_stats['database']['total_entries']}")
    print(f"  总翻译数：{perf_stats['database']['total_translations']}")
    print(f"  内存使用：{perf_stats['memory']['db_size_mb']:.2f}MB")
    
    print("\n✅ 批量处理完成!")
    print("=" * 60)


async def main():
    """主函数"""
    print("\n🚀 性能优化功能演示\n")
    
    try:
        # 演示 1: 缓存性能
        await demo_cache_performance()
        
        # 演示 2: 批量处理
        await demo_batch_processing()
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
