"""
撤销/重做和进度估计功能演示脚本
"""
import asyncio
import time
from infrastructure.undo_manager import (
    get_undo_manager, 
    OperationType, 
    record_operation,
    undo_last_operation,
    redo_last_operation
)
from infrastructure.progress_estimator import (
    get_progress_estimator,
    start_progress_tracking,
    update_progress,
    get_current_progress,
    format_progress_summary
)


async def demo_undo_redo():
    """演示撤销/重做功能"""
    print("=" * 60)
    print("🔄 撤销/重做功能演示")
    print("=" * 60)
    
    manager = get_undo_manager(max_history=10)
    
    # 记录一些操作
    print("\n📝 记录操作...")
    
    await record_operation(
        operation_type=OperationType.TERM_ADD,
        old_value=None,
        new_value={"中文": "你好", "英语": "Hello"},
        description="添加术语：你好 -> Hello"
    )
    
    await record_operation(
        operation_type=OperationType.TERM_UPDATE,
        old_value={"中文": "世界", "英语": "World"},
        new_value={"中文": "世界", "英语": "Globe"},
        description="更新术语：世界 -> Globe"
    )
    
    await record_operation(
        operation_type=OperationType.TERM_ADD,
        old_value=None,
        new_value={"中文": "测试", "法语": "Test"},
        description="添加术语：测试 -> Test"
    )
    
    # 显示统计
    stats = manager.get_stats()
    print(f"\n📊 当前状态:")
    print(f"  历史记录数：{stats['history_size']}")
    print(f"  总操作数：{stats['total_operations']}")
    print(f"  可撤销：{stats['can_undo']}")
    print(f"  可重做：{stats['can_redo']}")
    
    # 撤销操作
    print("\n↩️  执行撤销...")
    op = await undo_last_operation()
    if op:
        print(f"  已撤销：{op.description}")
    
    stats = manager.get_stats()
    print(f"  撤销后状态：可撤销={stats['can_undo']}, 可重做={stats['can_redo']}")
    
    # 重做操作
    print("\n↪️  执行重做...")
    op = await redo_last_operation()
    if op:
        print(f"  已重做：{op.description}")
    
    stats = manager.get_stats()
    print(f"  重做后状态：可撤销={stats['can_undo']}, 可重做={stats['can_redo']}")
    
    # 导出历史
    print("\n📄 导出操作历史:")
    history_json = await manager.export_history()
    print(history_json[:200] + "...")
    
    print("\n✅ 撤销/重做演示完成!")
    print("=" * 60)


def demo_progress_estimation():
    """演示进度估计功能"""
    print("\n" + "=" * 60)
    print("📊 进度估计功能演示")
    print("=" * 60)
    
    total_items = 100
    
    # 开始跟踪
    start_progress_tracking(total_items)
    print(f"\n🚀 开始跟踪进度，总任务数：{total_items}")
    
    # 模拟任务执行
    print("\n⏳ 模拟任务执行...")
    
    for i in range(0, total_items + 1, 5):
        update_progress(i)
        
        progress = get_current_progress()
        
        if i % 20 == 0 or i == total_items:
            print(f"\n进度更新点 {i}/{total_items}:")
            print(f"  百分比：{progress['progress_percent']:.1f}%")
            print(f"  预计剩余：{progress['eta_formatted']}")
            print(f"  速度：{progress['speed_per_second']:.1f} 项/秒")
            print(f"  已用时间：{progress['elapsed_formatted']}")
        
        # 模拟处理时间（带有一些随机性）
        time.sleep(0.05 + (i % 3) * 0.02)
    
    # 最终统计
    print("\n\n📈 最终统计:")
    estimator = get_progress_estimator()
    stats = estimator.get_detailed_stats()
    
    print(f"  总样本数：{stats['samples_collected']}")
    print(f"  平均速度：{stats.get('average_speed', 0):.2f} 项/秒")
    print(f"  最小速度：{stats.get('min_speed', 0):.2f} 项/秒")
    print(f"  最大速度：{stats.get('max_speed', 0):.2f} 项/秒")
    print(f"  中位速度：{stats.get('median_speed', 0):.2f} 项/秒")
    print(f"  是否完成：{stats['is_complete']}")
    
    # 格式化摘要
    print("\n📋 进度摘要:")
    summary = format_progress_summary()
    print(f"  {summary}")
    
    print("\n✅ 进度估计演示完成!")
    print("=" * 60)


async def main():
    """主函数"""
    print("\n🎯 撤销/重做与进度估计功能演示\n")
    
    try:
        # 演示 1: 撤销/重做
        await demo_undo_redo()
        
        # 演示 2: 进度估计
        demo_progress_estimation()
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
