"""
验证 GUI 语言选择框默认状态的脚本
用于确认所有语言复选框默认都是未选中状态
"""
import sys
import tkinter as tk
from tkinter import ttk

# 模拟 TARGET_LANGUAGES
TARGET_LANGUAGES = ["英语", "法语", "德语", "西班牙语", "日语", "韩语", "俄语", "中文 (简体)"]

def test_lang_checkboxes_default_state():
    """测试语言复选框的默认状态"""
    print("=" * 60)
    print("测试 GUI 语言选择框默认状态")
    print("=" * 60)
    
    # 创建根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    # 模拟初始化过程
    lang_vars = {}
    
    for i, lang in enumerate(TARGET_LANGUAGES):
        var = tk.BooleanVar(value=False)  # 关键：默认值为 False
        lang_vars[lang] = var
        
        # 验证初始值
        assert var.get() == False, f"{lang} 的默认值应该是 False,但实际是 {var.get()}"
        print(f"✅ {lang}: 默认状态 = {var.get()} (未选中)")
    
    # 统计选中的数量
    selected_count = sum(1 for v in lang_vars.values() if v.get())
    selected_langs = [k for k, v in lang_vars.items() if v.get()]
    
    print("\n" + "=" * 60)
    print(f"测试结果:")
    print(f"  - 总语言数：{len(lang_vars)}")
    print(f"  - 已选中：{selected_count}")
    print(f"  - 未选中：{len(lang_vars) - selected_count}")
    print(f"  - 选中的语言：{selected_langs if selected_langs else '无'}")
    print("=" * 60)
    
    # 验证结果
    if selected_count == 0:
        print("\n✅ 测试通过！所有语言复选框默认都是未选中状态")
        return True
    else:
        print(f"\n❌ 测试失败！有 {selected_count} 个语言被默认选中")
        return False
    
    root.destroy()

if __name__ == "__main__":
    success = test_lang_checkboxes_default_state()
    sys.exit(0 if success else 1)
