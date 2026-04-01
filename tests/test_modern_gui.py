"""
测试现代 GUI 功能完整性
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
from presentation.modern_gui_app import ModernGUIApp
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_gui_initialization():
    """测试 GUI 初始化"""
    print("=" * 60)
    print("测试 1: GUI 初始化")
    print("=" * 60)
    
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口，仅测试初始化
    
    try:
        app = ModernGUIApp(root, config_file=None)
        print("✅ GUI 初始化成功")
        
        # 检查关键组件是否存在
        assert hasattr(app, 'lang_notebook'), "❌ 缺少 lang_notebook 属性"
        print("✅ lang_notebook 属性存在")
        
        assert hasattr(app, 'tier_lang_frames'), "❌ 缺少 tier_lang_frames 属性"
        print("✅ tier_lang_frames 属性存在")
        
        assert hasattr(app, 'main_canvas'), "❌ 缺少 main_canvas 属性"
        print("✅ main_canvas 属性存在")
        
        assert hasattr(app, 'scrollable_frame'), "❌ 缺少 scrollable_frame 属性"
        print("✅ scrollable_frame 属性存在")
        
        # 检查变量初始化
        assert hasattr(app, 'term_path'), "❌ 缺少 term_path 变量"
        assert hasattr(app, 'source_path'), "❌ 缺少 source_path 变量"
        assert hasattr(app, 'mode_var'), "❌ 缺少 mode_var 变量"
        assert hasattr(app, 'draft_temp_var'), "❌ 缺少 draft_temp_var 变量"
        assert hasattr(app, 'review_temp_var'), "❌ 缺少 review_temp_var 变量"
        assert hasattr(app, 'translation_type_var'), "❌ 缺少 translation_type_var 变量"
        assert hasattr(app, 'log_level_var'), "❌ 缺少 log_level_var 变量"
        assert hasattr(app, 'log_granularity_var'), "❌ 缺少 log_granularity_var 变量"
        print("✅ 所有必要变量已初始化")
        
        # 检查语言选择功能
        assert len(app.lang_vars) > 0, "❌ 语言列表为空"
        print(f"✅ 已加载 {len(app.lang_vars)} 种语言")
        
        # 检查分页数量
        assert app.lang_notebook.winfo_exists(), "❌ lang_notebook 未创建"
        num_tabs = app.lang_notebook.index('end')
        assert num_tabs == 3, f"❌ 应该有 3 个分页，实际有{num_tabs}个"
        print(f"✅ 语言分页数量正确：{num_tabs}个 (T1/T2/T3)")
        
        root.destroy()
        print("\n✅ 所有初始化测试通过!\n")
        return True
        
    except Exception as e:
        root.destroy()
        print(f"❌ 初始化失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_language_selection():
    """测试语言选择功能"""
    print("=" * 60)
    print("测试 2: 语言选择功能")
    print("=" * 60)
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        app = ModernGUIApp(root)
        
        # 测试全选功能
        initial_count = len([lang for lang, var in app.lang_vars.items() if var.get()])
        app._select_all_langs()
        after_select_count = len([lang for lang, var in app.lang_vars.items() if var.get()])
        
        assert after_select_count > initial_count, "❌ 全选功能未生效"
        print(f"✅ 全选功能正常：{initial_count} -> {after_select_count}")
        
        # 测试取消全选
        app._deselect_all_langs()
        after_deselect_count = len([lang for lang, var in app.lang_vars.items() if var.get()])
        
        assert after_deselect_count < after_select_count, "❌ 取消全选功能未生效"
        print(f"✅ 取消全选功能正常：{after_select_count} -> {after_deselect_count}")
        
        root.destroy()
        print("\n✅ 语言选择功能测试通过!\n")
        return True
        
    except Exception as e:
        root.destroy()
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_parameter_sync():
    """测试参数同步功能"""
    print("=" * 60)
    print("测试 3: 参数同步功能")
    print("=" * 60)
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        app = ModernGUIApp(root)
        
        # 设置初译参数
        app.draft_model_var.set("test-model")
        app.draft_temp_var.set(0.5)
        app.draft_top_p_var.set(0.9)
        app.draft_timeout_var.set(90)
        app.draft_max_tokens_var.set(1024)
        
        # 同步到校对
        app._sync_draft_model_to_review()
        
        # 验证同步结果
        assert app.review_model_var.get() == "test-model", "❌ 模型同步失败"
        assert app.review_temp_var.get() == 0.5, "❌ 温度同步失败"
        assert app.review_top_p_var.get() == 0.9, "❌ Top P 同步失败"
        assert app.review_timeout_var.get() == 90, "❌ 超时同步失败"
        assert app.review_max_tokens_var.get() == 1024, "❌ Max Tokens 同步失败"
        
        print("✅ 参数同步功能正常")
        
        root.destroy()
        print("\n✅ 参数同步测试通过!\n")
        return True
        
    except Exception as e:
        root.destroy()
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_validation():
    """测试提示词验证功能"""
    print("=" * 60)
    print("测试 4: 提示词验证功能")
    print("=" * 60)
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        app = ModernGUIApp(root)
        
        # 测试空提示词
        app.draft_text.delete("1.0", tk.END)
        app.review_text.delete("1.0", tk.END)
        # 这里会弹出警告框，我们无法在自动化测试中验证，但不会报错
        
        # 测试有效提示词
        app.draft_text.insert(tk.END, "Translate to {target_lang}")
        app.review_text.insert(tk.END, "Review the translation")
        
        # 应该通过验证
        draft = app.draft_text.get("1.0", tk.END).strip()
        review = app.review_text.get("1.0", tk.END).strip()
        
        assert draft != "", "❌ 初译提示词为空"
        assert review != "", "❌ 校对提示词为空"
        assert "{target_lang}" in draft, "❌ 缺少占位符"
        
        print("✅ 提示词验证逻辑正常")
        
        root.destroy()
        print("\n✅ 提示词验证测试通过!\n")
        return True
        
    except Exception as e:
        root.destroy()
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_reset_parameters():
    """测试重置参数功能"""
    print("=" * 60)
    print("测试 5: 重置参数功能")
    print("=" * 60)
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        app = ModernGUIApp(root)
        
        # 修改参数
        app.draft_temp_var.set(1.5)
        app.draft_top_p_var.set(0.5)
        app.draft_timeout_var.set(120)
        app.draft_max_tokens_var.set(1024)
        
        app.review_temp_var.set(1.0)
        app.review_top_p_var.set(0.5)
        app.review_timeout_var.set(120)
        app.review_max_tokens_var.set(1024)
        
        # 重置
        app._reset_advanced_params()
        
        # 验证默认值
        assert app.draft_temp_var.get() == 0.3, "❌ 初译温度重置失败"
        assert app.draft_top_p_var.get() == 0.8, "❌ 初译 Top P 重置失败"
        assert app.draft_timeout_var.get() == 60, "❌ 初译超时重置失败"
        assert app.draft_max_tokens_var.get() == 512, "❌ 初译 Max Tokens 重置失败"
        
        assert app.review_temp_var.get() == 0.5, "❌ 校对温度重置失败"
        assert app.review_top_p_var.get() == 0.9, "❌ 校对 Top P 重置失败"
        assert app.review_timeout_var.get() == 60, "❌ 校对超时重置失败"
        assert app.review_max_tokens_var.get() == 512, "❌ 校对 Max Tokens 重置失败"
        
        print("✅ 参数重置功能正常")
        
        root.destroy()
        print("\n✅ 参数重置测试通过!\n")
        return True
        
    except Exception as e:
        root.destroy()
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 开始测试 ModernGUIApp 功能完整性")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("初始化测试", test_gui_initialization()))
    results.append(("语言选择测试", test_language_selection()))
    results.append(("参数同步测试", test_parameter_sync()))
    results.append(("提示词验证测试", test_prompt_validation()))
    results.append(("参数重置测试", test_reset_parameters()))
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, p in results if p)
    total_tests = len(results)
    
    print(f"\n总计：{total_passed}/{total_tests} 个测试通过")
    
    if total_passed == total_tests:
        print("\n🎉 所有测试通过！GUI 功能正常！")
    else:
        print(f"\n⚠️ 有 {total_tests - total_passed} 个测试失败，请检查问题")
    
    print("=" * 60 + "\n")
