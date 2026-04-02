"""
源语言选择功能演示
展示如何在 GUI 中使用新增的源语言选择功能
"""
import pandas as pd
import tempfile
import os


def demo_source_language_selection():
    """演示源语言选择功能的使用场景"""
    
    print("=" * 80)
    print("📚 源语言选择功能演示")
    print("=" * 80)
    
    # 创建示例 Excel 文件（模拟真实的多语言项目）
    print("\n📋 创建示例多语言表格...")
    
    example_data = {
        'Key': [
            'btn_submit', 'btn_cancel', 'btn_save', 
            'msg_welcome', 'msg_confirm'
        ],
        '中文原文': [
            '提交', '取消', '保存',
            '欢迎使用本系统', '请确认您的操作'
        ],
        '英语原文': [
            'Submit', 'Cancel', 'Save',
            'Welcome to the system', 'Please confirm your action'
        ],
        '日语原文': [
            '送信', 'キャンセル', '保存',
            'システムへようこそ', '操作を確認してください'
        ],
    }
    
    df = pd.DataFrame(example_data)
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False, prefix='demo_') as f:
        temp_path = f.name
        df.to_excel(temp_path, index=False, engine='openpyxl')
    
    try:
        print(f"✅ 示例文件已创建：{temp_path}")
        
        # 模拟 GUI 中的检测逻辑
        print("\n🔍 自动检测可用源语言...")
        df = pd.read_excel(temp_path, engine='openpyxl')
        columns = df.columns.tolist()
        
        exclude_patterns = ['key', 'id', '序号', '编号', 'status', '备注', 'note']
        
        available_langs = []
        for col in columns:
            col_lower = str(col).lower()
            is_excluded = any(pattern in col_lower for pattern in exclude_patterns)
            
            if not is_excluded and df[col].notna().any():
                available_langs.append(str(col))
        
        print(f"\n📊 检测到以下可用的源语言列:")
        for i, lang in enumerate(available_langs, 1):
            print(f"   {i}. {lang}")
        
        # 演示不同场景
        print("\n" + "=" * 80)
        print("🎯 使用场景演示")
        print("=" * 80)
        
        # 场景 1: 中译英/法/德
        print("\n📌 场景 1: 将中文 UI 翻译到多种语言")
        print("   源语言：中文原文")
        print("   目标语言：英语、法语、德语")
        print("   适用场景：中国开发的游戏，需要本地化到欧美市场")
        print(f"   待翻译条数：{len(df)} 条")
        
        # 场景 2: 英译中/日/韩
        print("\n📌 场景 2: 将英文 UI 翻译到亚洲语言")
        print("   源语言：英语原文")
        print("   目标语言：中文、日语、韩语")
        print("   适用场景：国际化游戏，需要从英文版本本地化到亚洲市场")
        print(f"   待翻译条数：{len(df)} 条")
        
        # 场景 3: 日译中/英
        print("\n📌 场景 3: 将日文游戏翻译到其他语言")
        print("   源语言：日语原文")
        print("   目标语言：中文、英语")
        print("   适用场景：日本引进游戏的本地化")
        print(f"   待翻译条数：{len(df)} 条")
        
        print("\n" + "=" * 80)
        print("💡 GUI 操作流程")
        print("=" * 80)
        print("""
1. 点击「选择待翻译文件」按钮，选择包含多语言原文的 Excel 文件
2. 系统自动检测并弹出提示框，显示检测到的源语言列表
3. 在「源语言选择」下拉框中选择要翻译的源语言列:
   - 选择「自动检测」：使用默认的「中文原文」列
   - 选择具体语言列：如「英语原文」「日语原文」等
4. 在下方「目标语言」区域选择要翻译到的目标语言
5. 点击「开始翻译」执行翻译任务
        
注意：
- 如果 Excel 只有一列原文（如只有「中文原文」），系统会自动选中该列
- 如果有多列原文，系统会提示用户手动选择
- 「Key」「ID」「备注」等列会被自动排除
        """)
        
        print("\n" + "=" * 80)
        print("✅ 功能特点")
        print("=" * 80)
        print("""
✓ 自动检测：读取 Excel 后自动识别所有可能的源语言列
✓ 智能过滤：自动排除 Key、ID、备注等非源语言列
✓ 灵活选择：支持在下拉框中手动选择源语言
✓ 默认行为：未选择时默认使用「中文原文」列
✓ 多语言支持：支持中文、英语、日语、韩语等多种源语言
✓ 一键刷新：提供「刷新源语言列表」按钮重新检测
        """)
        
    finally:
        os.remove(temp_path)


if __name__ == '__main__':
    demo_source_language_selection()
    
    print("\n" + "=" * 80)
    print("🎉 演示完成！")
    print("=" * 80)
    print("\n💡 提示：在 GUI 中使用时，选择文件后会自动弹出源语言检测结果")
    print("   您可以根据需要选择要翻译的源语言列\n")
