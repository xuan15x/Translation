"""
配置打点上报使用示例

演示如何使用配置指标收集器来跟踪配置使用情况、验证错误和性能指标。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.config_metrics import (
    ConfigMetrics,
    record_config_validation_error,
    record_config_usage,
    record_performance_metric,
    export_metrics_report,
    flush_metrics,
    get_metrics_collector
)


def demo_validation_error_tracking():
    """演示验证错误跟踪"""
    print("=" * 70)
    print("演示 1: 验证错误跟踪")
    print("=" * 70)
    
    # 模拟记录不同的验证错误
    record_config_validation_error(
        field='api_key',
        error_type='API 密钥不能为空',
        check_point='API 认证配置',
        value='(空)'
    )
    
    record_config_validation_error(
        field='temperature',
        error_type='temperature 值超出范围',
        check_point='模型温度参数',
        value=3.5
    )
    
    record_config_validation_error(
        field='initial_concurrency',
        error_type='initial_concurrency 值无效',
        check_point='初始并发数配置',
        value=0
    )
    
    # 再次记录相同的错误（测试统计）
    record_config_validation_error(
        field='temperature',
        error_type='temperature 值超出范围',
        check_point='模型温度参数',
        value=2.8
    )
    
    print("✅ 已记录 4 个验证错误")
    print()


def demo_config_usage_tracking():
    """演示配置使用情况跟踪"""
    print("=" * 70)
    print("演示 2: 配置使用情况跟踪")
    print("=" * 70)
    
    # 模拟不同用户的配置使用
    config_samples = [
        {
            '_version': 'v3.0.0',
            'api_provider': 'deepseek',
            'model_name': 'deepseek-chat',
            'temperature': 0.3,
            'top_p': 0.8,
            'initial_concurrency': 8,
            'cache_capacity': 2000,
            'enable_two_pass': True,
            'log_level': 'INFO',
        },
        {
            '_version': 'v3.0.0',
            'api_provider': 'openai',
            'model_name': 'gpt-4',
            'temperature': 0.5,
            'top_p': 0.9,
            'initial_concurrency': 10,
            'cache_capacity': 3000,
            'enable_two_pass': True,
            'log_level': 'DEBUG',
        },
        {
            '_version': 'v2.2.0',
            'api_provider': 'deepseek',
            'model_name': 'deepseek-coder',
            'temperature': 0.2,
            'top_p': 0.7,
            'initial_concurrency': 5,
            'cache_capacity': 1000,
            'enable_two_pass': False,
            'log_level': 'INFO',
        },
    ]
    
    for i, config in enumerate(config_samples, 1):
        record_config_usage(config)
        print(f"✅ 样本 {i}: {config['api_provider']} - {config['model_name']}")
    
    print()


def demo_performance_tracking():
    """演示性能指标跟踪"""
    print("=" * 70)
    print("演示 3: 性能指标跟踪")
    print("=" * 70)
    
    # 模拟记录翻译性能指标
    performance_data = [
        ('translation_speed', 150.5, 'tokens/s', {'batch_size': 50}),
        ('translation_speed', 180.2, 'tokens/s', {'batch_size': 100}),
        ('translation_speed', 120.8, 'tokens/s', {'batch_size': 30}),
        ('cache_hit_rate', 85.3, '%', {'cache_size': 2000}),
        ('cache_hit_rate', 92.1, '%', {'cache_size': 3000}),
        ('error_rate', 2.5, '%', {'concurrency': 8}),
        ('error_rate', 5.8, '%', {'concurrency': 15}),
        ('memory_usage', 256.5, 'MB', {'operation': 'terminology_query'}),
        ('memory_usage', 512.3, 'MB', {'operation': 'batch_translation'}),
    ]
    
    for metric_name, value, unit, tags in performance_data:
        record_performance_metric(metric_name, value, unit, tags)
        print(f"✅ 指标：{metric_name} = {value} {unit}")
    
    print()


def demo_error_hotspot_analysis():
    """演示错误热力图分析"""
    print("=" * 70)
    print("演示 4: 错误热力图分析")
    print("=" * 70)
    
    metrics = get_metrics_collector()
    
    # 获取错误热力图 Top 5
    hotspots = metrics.get_error_hotspots(5)
    
    print("\n🔥 Top 5 错误检查点:")
    for checkpoint, count in hotspots:
        percentage = count / sum(h[1] for h in hotspots) * 100
        bar = "█" * int(percentage / 5)
        print(f"  {checkpoint:20s} {bar} {count}次 ({percentage:.1f}%)")
    
    print()


def demo_export_report():
    """演示导出报告"""
    print("=" * 70)
    print("演示 5: 导出配置指标报告")
    print("=" * 70)
    
    # 导出文本报告
    report = export_metrics_report(output_file="config_metrics_report.txt")
    print("\n📊 报告预览:")
    print(report[:500] + "..." if len(report) > 500 else report)
    print(f"\n✅ 完整报告已保存至：config_metrics_report.txt")
    
    # 刷写所有指标到文件
    flush_metrics()
    print("\n✅ 所有指标已刷写到文件")
    print()


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "配置打点上报功能演示" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    try:
        # 执行所有演示
        demo_validation_error_tracking()
        demo_config_usage_tracking()
        demo_performance_tracking()
        demo_error_hotspot_analysis()
        demo_export_report()
        
        print("=" * 70)
        print("✅ 所有演示完成！")
        print("=" * 70)
        print("\n💡 提示:")
        print("  - 查看 .config_metrics/ 目录查看详细指标文件")
        print("  - 运行此脚本多次以积累更多数据")
        print("  - 使用 export_metrics_report() 导出分析报告")
        print()
        
    except Exception as e:
        print(f"\n❌ 演示失败：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
