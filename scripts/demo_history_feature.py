"""
历史记录功能演示脚本
展示完整的翻译历史记录功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.translation_history import get_history_manager, TranslationRecord
from datetime import datetime

def print_separator(title=""):
    """打印分隔线"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)

def demo_history_features():
    """演示历史记录功能"""
    print_separator("📜 历史记录功能演示")
    
    # 1. 初始化历史管理器
    print("\n1️⃣  初始化历史记录管理器...")
    manager = get_history_manager()
    print("   ✅ 历史管理器已初始化")
    print(f"   📍 数据库位置：{manager.db_path}")
    
    # 2. 添加示例记录
    print_separator("2️⃣  添加示例翻译记录")
    
    examples = [
        {
            'source': '游戏开始',
            'target': '英语',
            'translation': 'Game Start',
            'batch': 'demo_batch_001'
        },
        {
            'source': '加载中...',
            'target': '日语',
            'translation': '読み込み中...',
            'batch': 'demo_batch_001'
        },
        {
            'source': '恭喜通关！',
            'target': '韩语',
            'translation': '축하합니다!',
            'batch': 'demo_batch_002'
        },
        {
            'source': '设置',
            'target': '法语',
            'translation': 'Paramètres',
            'batch': 'demo_batch_002'
        },
        {
            'source': '返回',
            'target': '德语',
            'translation': 'Zurück',
            'batch': 'demo_batch_002'
        }
    ]
    
    for ex in examples:
        record = TranslationRecord(
            id=0,
            key=f'demo_{ex["source"]}',
            source_text=ex['source'],
            target_lang=ex['target'],
            original_trans='',
            draft_trans=ex['translation'],
            final_trans=ex['translation'],
            status='SUCCESS',
            diagnosis='Draft Only',
            reason='Demo translation',
            api_provider='deepseek',
            model_name='deepseek-chat',
            created_at=datetime.now().isoformat(),
            file_path='/demo/file.xlsx',
            batch_id=ex['batch']
        )
        
        record_id = manager.add_record(record)
        print(f"   ✓ ID:{record_id} | {ex['source']} -> {ex['translation']} ({ex['target']})")
    
    # 3. 查看最近记录
    print_separator("3️⃣  查看最近翻译记录")
    records = manager.get_recent_records(limit=5)
    print(f"   📊 最近 {len(records)} 条记录:\n")
    
    for i, record in enumerate(records, 1):
        status_icon = "✅" if record.status == "SUCCESS" else "❌"
        print(f"   {i}. {status_icon} [{record.created_at[11:19]}] {record.source_text}")
        print(f"      → {record.final_trans} ({record.target_lang})")
        print(f"      批次：{record.batch_id}")
        print()
    
    # 4. 统计信息
    print_separator("4️⃣  翻译统计信息")
    stats = manager.get_statistics()
    
    print(f"\n   📈 总体统计:")
    print(f"      总记录数：{stats['total']}")
    print(f"      成功数：{stats['success']}")
    print(f"      失败数：{stats['failed']}")
    print(f"      成功率：{stats['success_rate']:.1f}%")
    
    print(f"\n   🌍 按语言分布:")
    for lang, count in stats.get('by_language', {}).items():
        print(f"      {lang}: {count} 条")
    
    print(f"\n   🔌 按 API 提供商:")
    for provider, count in stats.get('by_provider', {}).items():
        print(f"      {provider}: {count} 条")
    
    # 5. 搜索功能演示
    print_separator("5️⃣  搜索功能演示")
    
    keywords = ['游戏', '加载', '设置']
    for keyword in keywords:
        results = manager.search_records(keyword=keyword, limit=5)
        if results:
            print(f"\n   🔍 搜索 '{keyword}': 找到 {len(results)} 条记录")
            for r in results:
                print(f"      ✓ {r.source_text} → {r.final_trans}")
        else:
            print(f"\n   🔍 搜索 '{keyword}': 无匹配记录")
    
    # 6. 导出功能说明
    print_separator("6️⃣  导出功能")
    print("\n   💡 在 GUI 中点击 '📤 导出 Excel' 按钮")
    print("      - 选择保存位置")
    print("      - 自动命名：translation_history_YYYYMMDD_HHMMSS.xlsx")
    print("      - 包含所有翻译记录详情")
    
    # 7. GUI 使用说明
    print_separator("📋 GUI 使用说明")
    print("""
    启动翻译应用:
      python presentation/translation.py
    
    查看历史记录:
      1. 点击主界面的 "📜 查看历史" 按钮
      2. 查看翻译记录列表
      3. 使用搜索框搜索特定内容
      4. 双击记录查看详细信息
      5. 点击 "📤 导出 Excel" 导出数据
    
    功能特性:
      ✅ 实时查看翻译历史
      ✅ 关键词搜索
      ✅ 统计信息展示
      ✅ 详情查看
      ✅ Excel 导出
    """)
    
    print_separator("✨ 演示完成")
    print("\n🎉 历史记录功能已完全实现并可用！")
    print("\n💡 提示：")
    print("   - 所有翻译操作会自动记录到历史")
    print("   - 历史记录保存在 translation_history.db")
    print("   - 支持搜索、筛选、导出等多种操作")
    print("   - 查看 docs/guides/历史记录功能使用指南.md 获取详细文档")
    print()

if __name__ == "__main__":
    demo_history_features()
