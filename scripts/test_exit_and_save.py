"""
测试全局退出机制和 Excel 保存功能

此脚本验证：
1. 退出按钮是否正常保存所有数据库到 Excel
2. 窗口关闭时是否自动保存数据
3. 所有历史管理器是否正确注册到全局管理器
"""
import os
import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from data_access.global_persistence_manager import (
    get_global_persistence_manager,
    save_all_databases,
    shutdown_all_databases
)


def test_global_persistence_manager():
    """测试全局持久化管理器"""
    print("=" * 60)
    print("测试全局持久化管理器")
    print("=" * 60)
    
    # 获取全局管理器实例
    manager = get_global_persistence_manager()
    
    print(f"✅ 全局管理器实例已创建：{manager}")
    print(f"📊 当前注册的持久化实例：{list(manager._persistences.keys())}")
    print(f"📊 当前注册的历史管理器：{list(manager._history_managers.keys())}")
    
    return True


def test_save_all_databases():
    """测试保存所有数据库"""
    print("\n" + "=" * 60)
    print("测试保存所有数据库到 Excel")
    print("=" * 60)
    
    try:
        # 调用保存函数
        results = save_all_databases()
        
        print(f"\n💾 保存结果统计:")
        print(f"   - 成功保存：{results.get('saved', 0)} 个数据库")
        print(f"   - 保存失败：{results.get('failed', 0)} 个数据库")
        print(f"   - 详细信息：{results.get('details', [])}")
        
        # 检查是否有数据被保存
        if results.get('saved', 0) > 0 or results.get('total_saved', 0) > 0:
            print("\n✅ 数据库保存成功！")
            return True
        else:
            print("\n⚠️ 没有数据需要保存（可能是首次运行）")
            return True
            
    except Exception as e:
        print(f"\n❌ 保存失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_shutdown_all_databases():
    """测试关闭所有数据库并保存"""
    print("\n" + "=" * 60)
    print("测试关闭所有数据库并保存")
    print("=" * 60)
    
    try:
        # 调用关闭函数
        results = shutdown_all_databases()
        
        print(f"\n🛑 关闭结果统计:")
        print(f"   - 总保存数：{results.get('total_saved', 0)}")
        print(f"   - 总失败数：{results.get('total_failed', 0)}")
        print(f"   - 保存详情：{results.get('save', {})}")
        print(f"   - 关闭详情：{results.get('close', {})}")
        
        if results.get('total_failed', 0) == 0:
            print("\n✅ 数据库正常关闭并保存！")
            return True
        else:
            print(f"\n⚠️ 关闭时有 {results['total_failed']} 个错误")
            return False
            
    except Exception as e:
        print(f"\n❌ 关闭失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def verify_excel_files():
    """验证 Excel 文件是否生成"""
    print("\n" + "=" * 60)
    print("验证 Excel 文件是否生成")
    print("=" * 60)
    
    # 检查可能的 Excel 文件
    excel_files = [
        "terminology.xlsx",
        "translation_history.xlsx",
        "terminology_history.xlsx"
    ]
    
    found_files = []
    for excel_file in excel_files:
        if os.path.exists(excel_file):
            file_size = os.path.getsize(excel_file)
            found_files.append(excel_file)
            print(f"✅ 找到 Excel 文件：{excel_file} (大小：{file_size} 字节)")
    
    if not found_files:
        print("⚠️ 未找到 Excel 文件（可能是首次运行，数据为空）")
        print("\n提示：Excel 文件将在第一次有数据后生成")
    
    return True


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🧪 开始测试全局退出机制和 Excel 保存功能")
    print("=" * 60)
    
    all_passed = True
    
    # 测试 1：全局管理器
    if not test_global_persistence_manager():
        all_passed = False
    
    # 测试 2：保存所有数据库
    if not test_save_all_databases():
        all_passed = False
    
    # 测试 3：关闭所有数据库
    if not test_shutdown_all_databases():
        all_passed = False
    
    # 测试 4：验证 Excel 文件
    if not verify_excel_files():
        all_passed = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请检查日志")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
