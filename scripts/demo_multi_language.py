"""
多语言翻译和源语言选择演示
展示如何支持多种源语言和目标语言的翻译
"""
import asyncio
from service.advanced_translation import (
    get_context_translator,
    get_quality_evaluator
)


async def demo_multi_language_translation():
    """演示多语言翻译功能"""
    
    print("=" * 80)
    print("多语言翻译演示（支持源语言选择）")
    print("=" * 80)
    
    # 获取翻译器
    translator = get_context_translator()
    translator.set_context_mode("isolated")  # 独立模式
    
    # 测试数据：不同源语言的 UI 文案
    test_cases = [
        {
            'source_text': '提交',
            'source_lang': '中文',
            'target_lang': '英语'
        },
        {
            'source_text': 'Submit',
            'source_lang': '英语',
            'target_lang': '中文'
        },
        {
            'source_text': '送信',
            'source_lang': '日语',
            'target_lang': '英语'
        },
        {
            'source_text': '제출',
            'source_lang': '韩语',
            'target_lang': '中文'
        },
        {
            'source_text': 'Soumettre',
            'source_lang': '法语',
            'target_lang': '英语'
        },
        {
            'source_text': 'Einreichen',
            'source_lang': '德语',
            'target_lang': '中文'
        }
    ]
    
    # 术语库（多语言版本）
    terminology_db = {
        "提交": {"英语": "Submit", "法语": "Soumettre", "德语": "Einreichen"},
        "Submit": {"中文": "提交", "日语": "送信", "韩语": "제출"},
        "送信": {"英语": "Submit", "中文": "提交"},
        "제출": {"英语": "Submit", "中文": "提交"},
        "Soumettre": {"英语": "Submit", "中文": "提交"},
        "Einreichen": {"英语": "Submit", "中文": "提交"}
    }
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. 翻译任务:")
        print(f"   原文：{case['source_text']} ({case['source_lang']})")
        print(f"   目标：{case['target_lang']}")
        
        # 执行翻译
        suggestion = await translator.analyze_context(
            source_text=case['source_text'],
            full_document=[],
            current_index=0,
            target_lang=case['target_lang'],
            terminology_db=terminology_db,
            source_lang=case['source_lang']  # 传入源语言
        )
        
        print(f"   译文：{suggestion.translation_suggestion}")
        print(f"   置信度：{suggestion.confidence}%")
        print(f"   推理：{suggestion.reasoning[:100]}...")
        
        results.append({
            'source': case['source_text'],
            'source_lang': case['source_lang'],
            'target_lang': case['target_lang'],
            'translation': suggestion.translation_suggestion,
            'confidence': suggestion.confidence
        })
    
    print("\n" + "=" * 80)
    print("翻译结果汇总")
    print("=" * 80)
    
    for item in results:
        status = "✅" if item['confidence'] >= 90 else "⚠️"
        print(f"{status} [{item['source_lang']:4}] {item['source']:15} → [{item['target_lang']:4}] {item['translation']:20} ({item['confidence']}%)")


async def demo_source_language_filtering():
    """演示源语言过滤功能（核心功能）"""
    
    print("\n" + "=" * 80)
    print("源语言过滤功能演示（仅使用指定语言的术语）")
    print("=" * 80)
    
    translator = get_context_translator()
    translator.set_context_mode("isolated")
    
    # 多语言术语库
    terminology_db = {
        # 中文术语
        "提交": {"英语": "Submit", "日语": "送信", "韩语": "제출"},
        "取消": {"英语": "Cancel", "日语": "キャンセル", "韩语": "취소"},
        # 英文术语
        "Submit": {"中文": "提交", "日语": "送信"},
        "Cancel": {"中文": "取消", "日语": "キャンセル"},
        # 日文术语
        "送信": {"英语": "Submit", "中文": "提交"},
        "確認": {"英语": "Confirm", "中文": "确认"},
    }
    
    # 场景 1: 只使用中文术语翻译到英语
    print("\n📌 场景 1: 仅使用中文术语 → 英语")
    print("-" * 80)
    chinese_texts = ["提交", "取消"]
    
    for text in chinese_texts:
        result = await translator.analyze_context(
            source_text=text,
            full_document=[],
            current_index=0,
            target_lang="英语",
            terminology_db=terminology_db,
            source_lang="中文"  # ← 关键：只匹配中文术语
        )
        
        print(f"{text} (中文) → {result.translation_suggestion} (英语)")
        print(f"   置信度：{result.confidence}%")
    
    # 场景 2: 只使用英文术语翻译到日语
    print("\n📌 场景 2: 仅使用英文术语 → 日语")
    print("-" * 80)
    english_texts = ["Submit", "Cancel"]
    
    for text in english_texts:
        result = await translator.analyze_context(
            source_text=text,
            full_document=[],
            current_index=0,
            target_lang="日语",
            terminology_db=terminology_db,
            source_lang="英语"  # ← 关键：只匹配英文术语
        )
        
        print(f"{text} (英语) → {result.translation_suggestion} (日语)")
        print(f"   置信度：{result.confidence}%")
    
    # 场景 3: 只使用日文术语翻译到中文
    print("\n📌 场景 3: 仅使用日文术语 → 中文")
    print("-" * 80)
    japanese_texts = ["送信", "確認"]
    
    for text in japanese_texts:
        result = await translator.analyze_context(
            source_text=text,
            full_document=[],
            current_index=0,
            target_lang="中文",
            terminology_db=terminology_db,
            source_lang="日语"  # ← 关键：只匹配日文术语
        )
        
        print(f"{text} (日语) → {result.translation_suggestion} (中文)")
        print(f"   置信度：{result.confidence}%")


async def demo_batch_multi_language():
    """演示批量多语言翻译"""
    
    print("\n" + "=" * 80)
    print("批量多语言翻译演示")
    print("=" * 80)
    
    translator = get_context_translator()
    translator.set_context_mode("isolated")
    
    # UI 按钮列表
    ui_buttons = ["提交", "取消", "保存", "删除"]
    
    # 目标语言列表
    target_languages = ["英语", "日语", "韩语", "法语", "德语"]
    
    # 术语库
    terminology_db = {
        "提交": {"英语": "Submit", "日语": "送信", "韩语": "제출", "法语": "Soumettre", "德语": "Einreichen"},
        "取消": {"英语": "Cancel", "日语": "キャンセル", "韩语": "취소", "法语": "Annuler", "德语": "Abbrechen"},
        "保存": {"英语": "Save", "日语": "保存", "韩语": "저장", "法语": "Enregistrer", "德语": "Speichern"},
        "删除": {"英语": "Delete", "日语": "削除", "韩语": "삭제", "法语": "Supprimer", "德语": "Löschen"}
    }
    
    print(f"\n待翻译按钮：{ui_buttons}")
    print(f"目标语言：{target_languages}\n")
    
    # 为每个按钮翻译到所有目标语言
    for button in ui_buttons:
        print(f"\n{'='*60}")
        print(f"按钮：{button}")
        print(f"{'='*60}")
        
        translations = {}
        
        for target_lang in target_languages:
            result = await translator.analyze_context(
                source_text=button,
                full_document=[],
                current_index=0,
                target_lang=target_lang,
                terminology_db=terminology_db,
                source_lang="中文"
            )
            
            translations[target_lang] = result.translation_suggestion
            status = "✅" if result.confidence >= 90 else "⚠️"
            print(f"{status} {target_lang:6} → {result.translation_suggestion:20} ({result.confidence}%)")
        
        print(f"\n汇总：{button}")
        for lang, trans in translations.items():
            print(f"  {lang:6}: {trans}")


async def main():
    """主函数"""
    try:
        # 演示 1: 多语言翻译
        await demo_multi_language_translation()
        
        # 演示 2: 源语言过滤
        await demo_source_language_filtering()
        
        # 演示 3: 批量多语言翻译
        await demo_batch_multi_language()
        
        print("\n" + "=" * 80)
        print("✅ 所有演示完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
