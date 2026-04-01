"""
源语言选择功能演示
展示如何在表格翻译中使用源语言过滤来控制哪些行需要被翻译
"""
import asyncio


async def demo_source_language_filter_in_workflow():
    """
    演示在工作流中如何使用源语言过滤
    
    场景：
    - 表格中有中文和英文两列原文
    - 用户只想翻译中文原文 → 生成日语、韩语版本
    - 英文原文保持不变（不翻译）
    """
    
    print("=" * 80)
    print("源语言过滤功能演示（控制哪些原文需要被翻译）")
    print("=" * 80)
    
    # 模拟表格数据
    table_data = [
        {"key": "row_1", "中文原文": "提交", "英语原文": "Submit"},
        {"key": "row_2", "中文原文": "取消", "英语原文": "Cancel"},
        {"key": "row_3", "中文原文": "保存", "英语原文": "Save"},
        {"key": "row_4", "中文原文": "删除", "英语原文": "Delete"},
    ]
    
    # 用户选择：仅翻译中文原文
    selected_source_lang = "中文"
    target_languages = ["日语", "韩语"]
    
    print(f"\n📋 原始数据:")
    print(f"{'行号':<6} {'中文原文':<10} {'英语原文':<10}")
    print("-" * 40)
    for i, row in enumerate(table_data, 1):
        print(f"{i:<6} {row['中文原文']:<10} {row['英语原文']:<10}")
    
    print(f"\n⚙️  翻译设置:")
    print(f"   源语言：{selected_source_lang} (仅翻译中文原文)")
    print(f"   目标语言：{', '.join(target_languages)}")
    
    print(f"\n🔄 开始处理...\n")
    
    translation_results = []
    
    for i, row in enumerate(table_data, 1):
        print(f"行 {i}:")
        
        # 检查是否有指定源语言的原文
        source_text_key = f"{selected_source_lang}原文"
        
        if source_text_key in row and row[source_text_key]:
            source_text = row[source_text_key]
            print(f"   ✓ 检测到{selected_source_lang}原文：'{source_text}'")
            
            # 对每个目标语言进行翻译
            for target_lang in target_languages:
                # 这里调用实际的翻译 API
                # translated = await translate(source_text, target_lang)
                
                # 模拟翻译结果
                translated = f"[{target_lang}] of {source_text}"
                
                print(f"   → 翻译到{target_lang}: '{translated}'")
                
                translation_results.append({
                    'key': row['key'],
                    'source_text': source_text,
                    'source_lang': selected_source_lang,
                    'target_lang': target_lang,
                    'translation': translated
                })
        else:
            print(f"   ⚠️  无{selected_source_lang}原文，跳过翻译")
        
        print()
    
    print("=" * 80)
    print("翻译结果汇总")
    print("=" * 80)
    
    # 按行分组显示结果
    from collections import defaultdict
    grouped_results = defaultdict(dict)
    
    for result in translation_results:
        key = result['key']
        target_lang = result['target_lang']
        grouped_results[key][target_lang] = result['translation']
    
    print(f"\n{'行号':<6} {'原文':<10} {'日语':<15} {'韩语':<15}")
    print("-" * 60)
    
    for i, row in enumerate(table_data, 1):
        key = row['key']
        source = row[f'{selected_source_lang}原文']
        japanese = grouped_results[key].get('日语', '-')
        korean = grouped_results[key].get('韩语', '-')
        
        print(f"{i:<6} {source:<10} {japanese:<15} {korean:<15}")
    
    print("\n✅ 处理完成！")
    print(f"   总计：{len(table_data)} 行")
    print(f"   已翻译：{len(translation_results)} 条")
    skipped = len(table_data) - len([r for r in translation_results if r['source_lang'] == selected_source_lang]) // len(target_languages)
    print(f"   跳过：{skipped} 行")


async def demo_multi_source_language_selection():
    """演示多源语言选择"""
    
    print("\n" + "=" * 80)
    print("多源语言选择演示")
    print("=" * 80)
    
    # 模拟表格数据（包含多种语言的原文）
    table_data = [
        {
            "key": "row_1",
            "中文原文": "提交申请",
            "英语原文": "Submit Application",
            "日语原文": "申請を送信"
        },
        {
            "key": "row_2",
            "中文原文": "确认信息",
            "英语原文": "Confirm Information",
            "日语原文": "情報を確認"
        },
    ]
    
    print(f"\n📋 原始数据:")
    print(f"{'行号':<6} {'中文':<15} {'英语':<20} {'日语':<15}")
    print("-" * 70)
    for i, row in enumerate(table_data, 1):
        print(f"{i:<6} {row['中文原文']:<15} {row['英语原文']:<20} {row['日语原文']:<15}")
    
    print(f"\n⚙️  翻译选项:")
    print(f"   可选择的源语言：中文、英语、日语")
    print(f"   目标语言：德语、法语")
    
    # 模拟用户选择
    selected_sources = ["中文", "英语"]  # 用户选择了中文和英语
    target_langs = ["德语", "法语"]
    
    print(f"\n✅ 用户选择：翻译 {', '.join(selected_sources)} → {', '.join(target_langs)}")
    print(f"   （日语原文不会被翻译）")
    
    print(f"\n🔄 开始批量翻译...\n")
    
    total_translations = 0
    
    for i, row in enumerate(table_data, 1):
        print(f"行 {i}:")
        
        for source_lang in selected_sources:
            source_text_key = f"{source_lang}原文"
            
            if source_text_key in row and row[source_text_key]:
                source_text = row[source_text_key]
                
                for target_lang in target_langs:
                    # 模拟翻译
                    translated = f"[{target_lang}] of {source_text}"
                    print(f"   {source_text} ({source_lang}) → {translated} ({target_lang})")
                    total_translations += 1
        
        print()
    
    print(f"总计：{total_translations} 条翻译")
    print(f"   中文→德/法：{len(table_data) * 2} 条")
    print(f"   英语→德/法：{len(table_data) * 2} 条")
    print(f"   日语→德/法：0 条 (未选择)")


async def main():
    """主函数"""
    try:
        # 演示 1: 基本源语言过滤
        await demo_source_language_filter_in_workflow()
        
        # 演示 2: 多源语言选择
        await demo_multi_source_language_selection()
        
        print("\n" + "=" * 80)
        print("✅ 所有演示完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
