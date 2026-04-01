"""
术语库版本控制和备份功能演示脚本
"""
import asyncio
import os
from terminology_manager import TerminologyManager
from models import Config
from service.auto_backup import BackupStrategy


async def demo_version_control():
    """演示版本控制功能"""
    print("=" * 60)
    print("📦 术语库版本控制演示")
    print("=" * 60)
    
    config = Config()
    tm = TerminologyManager("tests/data/test_terms.xlsx", config)
    
    # 启用版本控制
    print("\n🔧 启用版本控制...")
    tm.enable_version_control(repo_path=os.getcwd())
    
    # 添加一些术语
    print("\n📝 添加测试术语...")
    await tm.add_entry("版本控制", "英语", "Version Control")
    await tm.add_entry("备份策略", "英语", "Backup Strategy")
    await tm.add_entry("Git 仓库", "英语", "Git Repository")
    
    # 提交更改
    print("\n💾 提交更改...")
    await tm.commit_changes("添加新术语：版本控制相关")
    
    # 查看历史
    print("\n📜 查看版本历史:")
    history = tm.get_version_history(limit=5)
    
    for i, entry in enumerate(history, 1):
        print(f"\n{i}. {entry['commit']}")
        print(f"   信息：{entry['message']}")
        print(f"   作者：{entry['author']}")
        print(f"   时间：{entry['time']}")
    
    # 创建手动备份
    print("\n💾 创建手动备份...")
    backup_path = await tm.create_backup(reason="演示备份")
    print(f"备份路径：{backup_path}")
    
    print("\n✅ 版本控制演示完成!")
    print("=" * 60)


async def demo_auto_backup():
    """演示自动备份功能"""
    print("\n" + "=" * 60)
    print("🔄 自动备份功能演示")
    print("=" * 60)
    
    config = Config()
    tm = TerminologyManager("tests/data/test_terms.xlsx", config)
    
    # 启用自动备份（每小时备份，保留 24 个）
    print("\n🔧 启用自动备份...")
    tm.enable_auto_backup(
        backup_dir=".terminology_backups",
        strategy=BackupStrategy.HOURLY
    )
    
    # 启动自动备份
    print("\n🚀 启动自动备份循环...")
    await tm.start_auto_backup()
    
    # 等待一会儿
    await asyncio.sleep(2)
    
    # 创建手动备份
    print("\n💾 创建手动备份...")
    backup_path = await tm.create_backup(reason="演示开始")
    print(f"备份路径：{backup_path}")
    
    # 添加术语并再次备份
    print("\n📝 添加更多术语...")
    await tm.add_entry("自动备份", "法语", "Sauvegarde automatique")
    await tm.add_entry("定时任务", "德语", "Geplante Aufgabe")
    
    # 再次创建备份
    print("\n💾 再次创建备份...")
    backup_path2 = await tm.create_backup(reason="添加术语后")
    print(f"备份路径：{backup_path2}")
    
    # 列出所有备份
    print("\n📋 列出所有备份:")
    backups = tm.list_backups(limit=10)
    
    for i, backup in enumerate(backups, 1):
        print(f"\n{i}. {backup['filename']}")
        print(f"   时间：{backup.get('time', '未知')}")
        print(f"   策略：{backup.get('strategy', 'unknown')}")
        print(f"   原因：{backup.get('reason', '')}")
        print(f"   大小：{backup.get('size', 0)} bytes")
    
    # 获取统计信息
    print("\n📊 备份统计:")
    if tm.backup_manager:
        stats = tm.backup_manager.get_stats()
        print(f"  总备份数：{stats['total_backups']}")
        print(f"  失败次数：{stats['failed_backups']}")
        print(f"  最后备份：{stats.get('last_backup_time', '无')}")
        print(f"  最后大小：{stats.get('last_backup_size', 0)} bytes")
        print(f"  运行中：{stats['running']}")
    
    # 停止自动备份
    print("\n⏹️ 停止自动备份...")
    await tm.stop_auto_backup()
    
    print("\n✅ 自动备份演示完成!")
    print("=" * 60)


async def demo_backup_restore():
    """演示备份恢复功能"""
    print("\n" + "=" * 60)
    print("💾 备份恢复演示")
    print("=" * 60)
    
    config = Config()
    tm = TerminologyManager("tests/data/test_terms.xlsx", config)
    
    # 先创建一些术语
    print("\n📝 创建初始数据...")
    await tm.add_entry("原始术语 1", "英语", "Original Term 1")
    await tm.add_entry("原始术语 2", "英语", "Original Term 2")
    
    # 创建备份
    print("\n💾 创建备份...")
    backup_path = await tm.create_backup(reason="恢复测试点")
    print(f"备份路径：{backup_path}")
    
    # 修改术语库
    print("\n✏️  修改术语库...")
    await tm.add_entry("新术语", "英语", "New Term")
    await tm.add_entry("原始术语 1", "英语", "Modified Term 1")  # 更新
    
    # 显示当前状态
    print("\n📊 当前术语库状态:")
    stats = await tm.get_performance_stats()
    print(f"  总条目数：{stats['database']['total_entries']}")
    
    # 恢复备份
    print(f"\n🔄 恢复到备份点：{backup_path}")
    success = await tm.restore_from_backup(backup_path)
    
    if success:
        print("✅ 恢复成功!")
        
        # 重新加载术语库
        print("\n🔄 重新加载术语库...")
        tm.db.clear()
        tm._load_sync()
        
        # 显示恢复后状态
        print("\n📊 恢复后术语库状态:")
        stats = await tm.get_performance_stats()
        print(f"  总条目数：{stats['database']['total_entries']}")
    else:
        print("❌ 恢复失败")
    
    print("\n✅ 备份恢复演示完成!")
    print("=" * 60)


async def main():
    """主函数"""
    print("\n🎯 术语库版本控制与备份功能演示\n")
    
    try:
        # 演示 1: 版本控制
        await demo_version_control()
        
        # 演示 2: 自动备份
        await demo_auto_backup()
        
        # 演示 3: 备份恢复
        await demo_backup_restore()
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
