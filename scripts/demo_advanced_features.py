"""
高级翻译功能演示脚本
展示上下文感知翻译、质量评估、风格一致性检查和术语推荐
"""
import asyncio
from service.advanced_translation import (
    get_context_translator,
    get_quality_evaluator,
    get_style_checker,
    get_term_recommender,
    QualityLevel,
    StyleConsistency
)


async def demo_context_aware_translation():
    """演示上下文感知翻译（针对 UI 文案优化）"""
    print("=" * 70)
    print("🔍 上下文感知翻译演示（UI 文案优化版）")
    print("=" * 70)
    
    # 获取翻译器
    translator = get_context_translator()
    
    # 场景 1: UI 文案模式（独立分析）
    print("\n📱 场景 1: UI 按钮文案翻译（独立模式）")
    print("-" * 70)
    
    # 设置为独立模式
    translator.set_context_mode("isolated")
    
    # 模拟 UI 按钮文案表格
    ui_elements = [
        "提交",
        "取消",
        "保存更改",
        "删除选中项",
        "导出为 Excel"
    ]
    
    # 模拟术语库
    terminology_db = {
        "提交": {"英语": "Submit", "法语": "Soumettre"},
        "取消": {"英语": "Cancel", "法语": "Annuler"},
        "保存": {"英语": "Save", "法语": "Enregistrer"},
        "删除": {"英语": "Delete", "法语": "Supprimer"},
        "导出": {"英语": "Export", "法语": "Exporter"},
        "Excel": {"英语": "Excel", "法语": "Excel"}
    }
    
    target_lang = "英语"
    
    for i, text in enumerate(ui_elements, 1):
        print(f"\n按钮 {i}: {text}")
        
        # 使用独立模式分析（不使用上下文）
        suggestion = await translator.analyze_context(
            source_text=text,
            full_document=ui_elements,
            current_index=i-1,
            target_lang=target_lang,
            terminology_db=terminology_db
        )
        
        print(f"   翻译：{suggestion.translation_suggestion}")
        print(f"   置信度：{suggestion.confidence}%")
        print(f"   推理：{suggestion.reasoning}")
    
    # 场景 2: 文档模式（带上下文）
    print("\n\n📄 场景 2: 文档段落翻译（上下文模式）")
    print("-" * 70)
    
    # 切换回上下文模式
    translator.set_context_mode("contextual")
    
    # 模拟文档段落
    document = [
        "今天天气很好。",
        "我们决定去公园散步。",
        "他带着相机。",  # 当前待翻译句子
        "路上遇到了很多游客。",
        "大家都玩得很开心。"
    ]
    
    current_index = 2  # "他带着相机。"
    
    print(f"\n完整文档:")
    for i, sentence in enumerate(document):
        marker = "→ " if i == current_index else "  "
        print(f"{marker}{i+1}. {sentence}")
    
    print(f"\n分析第 {current_index + 1} 句的上下文...")
    
    # 分析上下文
    suggestion = await translator.analyze_context(
        source_text=document[current_index],
        full_document=document,
        current_index=current_index,
        target_lang=target_lang,
        terminology_db=None
    )
    
    print(f"\n💡 上下文分析结果:")
    print(f"   上下文类型：{suggestion.context_type}")
    print(f"   前文：{suggestion.surrounding_context[0] if suggestion.surrounding_context else '无'}")
    print(f"   后文：{suggestion.surrounding_context[1] if len(suggestion.surrounding_context) > 1 else '无'}")
    print(f"\n✨ 翻译建议:")
    print(f"   最佳翻译：{suggestion.translation_suggestion}")
    print(f"   置信度：{suggestion.confidence}%")
    print(f"   推理：{suggestion.reasoning}")
    
    if suggestion.alternative_translations:
        print(f"\n🔄 备选翻译:")
        for alt in suggestion.alternative_translations:
            print(f"   - {alt}")
    
    print("\n✅ 上下文感知翻译演示完成!")
    print("=" * 70)


async def demo_quality_evaluation():
    """演示翻译质量自动评估"""
    print("\n" + "=" * 70)
    print("⭐ 翻译质量自动评估演示")
    print("=" * 70)
    
    # 获取评估器
    evaluator = get_quality_evaluator()
    
    # 测试用例
    test_cases = [
        {
            'source': "你好，世界！",
            'translation': "Hello, World!",
            'target_lang': "英语",
            'description': "经典问候语"
        },
        {
            'source': "这个项目的技术架构非常复杂。",
            'translation': "The technical architecture of this project is very complex.",
            'target_lang': "英语",
            'description': "技术文档"
        },
        {
            'source': "快速 brown fox 跳过 lazy dog。",
            'translation': "The quick brown fox jumps over the lazy dog.",
            'target_lang': "英语",
            'description': "有语法问题的翻译"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {case['description']}")
        print(f"   原文：{case['source']}")
        print(f"   译文：{case['translation']}")
        
        # 评估质量
        metrics = await evaluator.evaluate_quality(
            source_text=case['source'],
            translation=case['translation'],
            target_lang=case['target_lang']
        )
        
        print(f"\n📊 质量评估结果:")
        print(f"   总体得分：{metrics.overall_score}/100")
        print(f"   质量等级：{metrics.quality_level.value.upper()}")
        print(f"   ── 细分指标 ──")
        print(f"   • 准确性：{metrics.accuracy_score}/100")
        print(f"   • 流畅性：{metrics.fluency_score}/100")
        print(f"   • 一致性：{metrics.consistency_score}/100")
        print(f"   • 术语使用：{metrics.terminology_score}/100")
        
        if metrics.issues:
            print(f"\n⚠️  发现问题:")
            for issue in metrics.issues:
                print(f"   - {issue}")
        
        if metrics.suggestions:
            print(f"\n💡 改进建议:")
            for sug in metrics.suggestions:
                print(f"   • {sug}")
    
    print("\n✅ 翻译质量评估演示完成!")
    print("=" * 70)


async def demo_style_consistency():
    """演示风格一致性检查"""
    print("\n" + "=" * 70)
    print("🎨 风格一致性检查演示")
    print("=" * 70)
    
    # 获取检查器
    checker = get_style_checker()
    
    # 模拟翻译数据
    translations = [
        {'source': '用户', 'translation': 'User'},
        {'source': '用户', 'translation': 'Customer'},  # 不一致！
        {'source': '系统', 'translation': 'System'},
        {'source': '系统', 'translation': 'System'},  # 一致
        {'source': '设置', 'translation': 'Settings'},
        {'source': '设置', 'translation': 'Configuration'},  # 不一致！
        {'source': '帮助', 'translation': 'Help'},
        {'source': '帮助', 'translation': 'Help'},  # 一致
    ]
    
    print(f"\n📋 检查 {len(translations)} 条翻译的风格一致性...")
    print(f"\n原始数据:")
    for i, item in enumerate(translations, 1):
        print(f"   {i}. {item['source']} → {item['translation']}")
    
    # 执行检查
    report = await checker.check_consistency(translations)
    
    print(f"\n📊 一致性检查结果:")
    print(f"   一致性级别：{report.consistency_level.value.upper()}")
    print(f"   一致性得分：{report.consistency_score}/100")
    
    if report.inconsistencies:
        print(f"\n❌ 发现不一致:")
        for inc in report.inconsistencies:
            print(f"   术语：'{inc['term']}'")
            print(f"   不同译法：{', '.join(inc['translations'])}")
            print(f"   出现次数：{inc['occurrences']}")
    
    if report.style_violations:
        print(f"\n⚠️  风格违规:")
        for viol in report.style_violations:
            print(f"   - {viol}")
    
    if report.recommendations:
        print(f"\n💡 建议:")
        for rec in report.recommendations:
            print(f"   • {rec}")
    
    print("\n✅ 风格一致性检查演示完成!")
    print("=" * 70)


async def demo_term_recommendation():
    """演示术语推荐"""
    print("\n" + "=" * 70)
    print("📚 机器学习术语推荐演示")
    print("=" * 70)
    
    # 模拟训练数据（平行语料）
    training_data = [
        {'source': '人工智能改变世界', 'translation': 'Artificial Intelligence changes the world'},
        {'source': '机器学习是人工智能的分支', 'translation': 'Machine learning is a branch of artificial intelligence'},
        {'source': '深度学习用于图像识别', 'translation': 'Deep learning is used for image recognition'},
        {'source': '神经网络模拟人脑', 'translation': 'Neural networks simulate the human brain'},
        {'source': '算法优化提高效率', 'translation': 'Algorithm optimization improves efficiency'},
    ] * 10  # 重复以增加频率
    
    # 初始化推荐器
    recommender = get_term_recommender(training_data)
    
    print(f"\n📖 使用 {len(training_data)} 条平行语料训练...")
    print(f"\n已构建术语数据库，包含 {len(recommender.term_database)} 个术语")
    
    # 测试推荐
    test_terms = ['人工智能', '机器学习', '深度学习', '算法']
    target_lang = "英语"
    
    print(f"\n🔍 为以下术语推荐翻译（目标语言：{target_lang}）:")
    for term in test_terms:
        print(f"\n   术语：{term}")
        
        rec = await recommender.recommend_translation(term, target_lang)
        
        if rec:
            print(f"   ✅ 推荐译法：{rec.recommended_translation}")
            print(f"   📊 置信度：{rec.confidence:.2%}")
            print(f"   🎯 领域相关性：{rec.domain_relevance:.2f}")
            
            if rec.alternatives:
                print(f"   🔄 备选方案:")
                for alt_trans, alt_conf in rec.alternatives[:3]:
                    print(f"      - {alt_trans} ({alt_conf:.2%})")
        else:
            print(f"   ⚠️  未找到推荐（术语库中无此术语）")
    
    print("\n✅ 术语推荐演示完成!")
    print("=" * 70)


async def demo_integrated_workflow():
    """演示集成工作流"""
    print("\n" + "=" * 70)
    print("🚀 高级翻译功能集成工作流演示")
    print("=" * 70)
    
    # 初始化所有服务
    translator = get_context_translator()
    evaluator = get_quality_evaluator()
    checker = get_style_checker()
    recommender = get_term_recommender()
    
    # 模拟翻译任务
    document = [
        "欢迎使用 AI 翻译系统。",
        "本系统采用先进技术。",
        "提供高质量翻译服务。"
    ]
    
    translations = []
    
    print(f"\n📝 待翻译文档 ({len(document)} 句):")
    for i, sentence in enumerate(document, 1):
        print(f"   {i}. {sentence}")
    
    print(f"\n🔄 开始处理...\n")
    
    for i, source in enumerate(document):
        print(f"处理第 {i+1} 句：{source}")
        
        # 1. 上下文感知翻译
        context_suggestion = await translator.analyze_context(
            source_text=source,
            full_document=document,
            current_index=i,
            target_lang="英语"
        )
        translation = context_suggestion.translation_suggestion
        
        print(f"   → 翻译：{translation}")
        
        # 2. 质量评估
        quality_metrics = await evaluator.evaluate_quality(
            source_text=source,
            translation=translation,
            target_lang="英语"
        )
        
        print(f"   → 质量：{quality_metrics.overall_score}/100 ({quality_metrics.quality_level.value})")
        
        # 3. 记录翻译
        translations.append({
            'source': source,
            'translation': translation
        })
        
        print()
    
    # 4. 风格一致性检查
    print("🎨 进行风格一致性检查...")
    style_report = await checker.check_consistency(translations)
    
    print(f"   一致性：{style_report.consistency_score}/100 ({style_report.consistency_level.value})")
    
    if style_report.recommendations:
        print(f"   建议：{'; '.join(style_report.recommendations)}")
    
    print("\n📊 最终报告:")
    print(f"   总句数：{len(document)}")
    print(f"   平均质量得分：{sum((await evaluator.evaluate_quality(t['source'], t['translation'], '英语')).overall_score for t in translations) / len(document):.2f}")
    print(f"   风格一致性：{style_report.consistency_level.value}")
    
    print("\n✅ 集成工作流演示完成!")
    print("=" * 70)


async def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("          高级翻译功能演示")
    print("=" * 70)
    
    try:
        # 单独功能演示
        await demo_context_aware_translation()
        await demo_quality_evaluation()
        await demo_style_consistency()
        await demo_term_recommendation()
        
        # 集成工作流演示
        await demo_integrated_workflow()
        
        print("\n" + "=" * 70)
        print("🎉 所有演示完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
