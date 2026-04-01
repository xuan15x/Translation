"""
测试历史记录功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.translation_history import get_history_manager, TranslationRecord
from datetime import datetime

def test_history_manager():
    """测试历史记录管理器"""
    print("=" * 60)
    print("测试历史记录功能")
    print("=" * 60)
    
    # 获取历史管理器
    manager = get_history_manager()
    print("✅ 历史记录管理器已初始化")
    
    # 添加测试记录
    print("\n添加测试记录...")
    test_records = [
        TranslationRecord(
            id=0,
            key='test_1',
            source_text='你好世界',
            target_lang='英语',
            original_trans='',
            draft_trans='Hello World',
            final_trans='Hello World',
            status='SUCCESS',
            diagnosis='Draft Only',
            reason='Direct translation',
            api_provider='deepseek',
            model_name='deepseek-chat',
            created_at=datetime.now().isoformat(),
            file_path='/test/file.xlsx',
            batch_id='batch_001'
        ),
        TranslationRecord(
            id=0,
            key='test_2',
            source_text='欢迎使用',
            target_lang='日语',
            original_trans='',
            draft_trans='ようこそ',
            final_trans='ようこそ',
            status='SUCCESS',
            diagnosis='Draft Only',
            reason='Direct translation',
            api_provider='deepseek',
            model_name='deepseek-chat',
            created_at=datetime.now().isoformat(),
            file_path='/test/file.xlsx',
            batch_id='batch_001'
        ),
        TranslationRecord(
            id=0,
            key='test_3',
            source_text='开始游戏',
            target_lang='法语',
            original_trans='',
            draft_trans='Commencer le jeu',
            final_trans='Commencer le jeu',
            status='SUCCESS',
            diagnosis='Draft Only',
            reason='Direct translation',
            api_provider='deepseek',
            model_name='deepseek-chat',
            created_at=datetime.now().isoformat(),
            file_path='/test/file.xlsx',
            batch_id='batch_002'
        )
    ]
    
    for record in test_records:
        record_id = manager.add_record(record)
        print(f"  ✓ 添加记录 ID: {record_id} - {record.source_text} -> {record.target_lang}")
    
    # 查询记录
    print("\n查询最近记录...")
    records = manager.get_recent_records(limit=10)
    print(f"找到 {len(records)} 条记录:")
    for record in records:
        status_icon = "✅" if record.status == "SUCCESS" else "❌"
        print(f"  {status_icon} [{record.created_at[:19]}] {record.source_text} -> {record.final_trans} ({record.target_lang})")
    
    # 获取统计信息
    print("\n统计信息:")
    stats = manager.get_statistics()
    print(f"  总记录数：{stats.get('total', 0)}")
    print(f"  成功数：{stats.get('success', 0)}")
    print(f"  失败数：{stats.get('failed', 0)}")
    print(f"  成功率：{stats.get('success_rate', 0):.1f}%")
    
    # 搜索记录
    print("\n搜索包含'世界'的记录...")
    search_results = manager.search_records(keyword='世界', limit=10)
    print(f"找到 {len(search_results)} 条记录:")
    for record in search_results:
        print(f"  ✓ {record.source_text} -> {record.final_trans}")
    
    print("\n" + "=" * 60)
    print("✅ 历史记录功能测试完成！")
    print("=" * 60)
    print("\n提示：现在可以在 GUI 中点击'📜 查看历史'按钮查看历史记录")

if __name__ == "__main__":
    test_history_manager()
