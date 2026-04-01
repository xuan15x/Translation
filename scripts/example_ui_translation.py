"""
UI 文案翻译最佳实践示例
展示如何使用独立模式和术语扩展功能
"""
import asyncio
from service.advanced_translation import (
    get_context_translator,
    get_quality_evaluator
)


async def translate_ui_elements():
    """翻译 UI 元素（按钮、标签等）"""
    
    # 获取翻译器
    translator = get_context_translator(client=None, config=None)
    
    # 设置为独立模式（适合 UI 文案）
    translator.set_context_mode("isolated")
    
    # UI 按钮文案列表
    ui_buttons = [
        "提交",
        "取消", 
        "保存更改",
        "删除选中项",
        "导出为 Excel",
        "导入数据",
        "刷新",
        "搜索...",
        "设置",
        "帮助"
    ]
    
    # 术语库（从项目术语库加载）
    terminology_db = {
        "提交": {"英语": "Submit", "法语": "Soumettre", "德语": "Einreichen"},
        "取消": {"英语": "Cancel", "法语": "Annuler", "德语": "Abbrechen"},
        "保存": {"英语": "Save", "法语": "Enregistrer", "德语": "Speichern"},
        "删除": {"英语": "Delete", "法语": "Supprimer", "德语": "Löschen"},
        "导出": {"英语": "Export", "法语": "Exporter", "德语": "Exportieren"},
        "导入": {"英语": "Import", "法语": "Importer", "德语": "Importieren"},
        "刷新": {"英语": "Refresh", "法语": "Actualiser", "德语": "Aktualisieren"},
        "搜索": {"英语": "Search", "法语": "Rechercher", "德语": "Suchen"},
        "设置": {"英语": "Settings", "法语": "Paramètres", "德语": "Einstellungen"},
        "帮助": {"英语": "Help", "法语": "Aide", "德语": "Hilfe"},
        "Excel": {"英语": "Excel", "法语": "Excel", "德语": "Excel"}
    }
    
    target_language = "英语"
    
    print("=" * 80)
    print("UI 按钮文案翻译（独立模式 + 术语扩展）")
    print("=" * 80)
    
    results = []
    
    for i, button_text in enumerate(ui_buttons, 1):
        print(f"\n{i}. 按钮文案：'{button_text}'")
        
        # 分析并翻译（独立模式，自动扩展术语）
        suggestion = await translator.analyze_context(
            source_text=button_text,
            full_document=[],  # 空文档，不使用上下文
            current_index=0,
            target_lang=target_language,
            terminology_db=terminology_db
        )
        
        print(f"   翻译：{suggestion.translation_suggestion}")
        print(f"   置信度：{suggestion.confidence}%")
        print(f"   推理：{suggestion.reasoning}")
        
        results.append({
            'source': button_text,
            'translation': suggestion.translation_suggestion,
            'confidence': suggestion.confidence
        })
    
    print("\n" + "=" * 80)
    print("翻译结果汇总")
    print("=" * 80)
    
    for item in results:
        status = "✅" if item['confidence'] >= 90 else "⚠️"
        print(f"{status} {item['source']:15} → {item['translation']:20} ({item['confidence']}%)")


async def translate_with_custom_terms():
    """使用自定义术语库翻译"""
    
    translator = get_context_translator()
    translator.set_context_mode("isolated")
    
    # 待翻译的 UI 文案
    ui_texts = [
        "用户登录",
        "注册新账户",
        "忘记密码",
        "退出登录"
    ]
    
    # 自定义术语库
    custom_terminology = {
        "用户": {"英语": "User", "日语": "ユーザー"},
        "登录": {"英语": "Login", "日语": "ログイン"},
        "注册": {"英语": "Register", "日语": "登録"},
        "账户": {"英语": "Account", "日语": "アカウント"},
        "密码": {"英语": "Password", "日语": "パスワード"},
        "退出": {"英语": "Logout", "日语": "ログアウト"}
    }
    
    print("\n" + "=" * 80)
    print("使用自定义术语库翻译")
    print("=" * 80)
    
    for text in ui_texts:
        print(f"\n原文：{text}")
        
        suggestion = await translator.analyze_context(
            source_text=text,
            full_document=[],
            current_index=0,
            target_lang="英语",
            terminology_db=custom_terminology
        )
        
        print(f"译文：{suggestion.translation_suggestion}")
        print(f"说明：{suggestion.reasoning}")


async def main():
    """主函数"""
    try:
        # 示例 1: 标准 UI 按钮翻译
        await translate_ui_elements()
        
        # 示例 2: 使用自定义术语
        await translate_with_custom_terms()
        
        print("\n" + "=" * 80)
        print("✅ 所有示例完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
