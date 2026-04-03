"""
测试脚本：验证术语库和翻译测试表的功能
"""
import pandas as pd
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from application.result_builder import TaskFactory

def test_files():
    """测试两个Excel文件"""
    term_file = "D:/文案翻译/dify/统一术语.xlsx"
    test_file = "D:/文案翻译/dify/翻译测试表.xlsx"
    
    print("="*60)
    print("测试文件结构")
    print("="*60)
    
    # 测试术语库
    print("\n📄 术语库文件:", term_file)
    df_term = pd.read_excel(term_file)
    print(f"  列名: {df_term.columns.tolist()}")
    print(f"  行数: {len(df_term)}")
    print(f"  前3行:")
    print(df_term.head(3).to_string(index=False))
    
    # 测试翻译测试表
    print("\n📄 翻译测试表:", test_file)
    df_test = pd.read_excel(test_file)
    print(f"  列名: {df_test.columns.tolist()}")
    print(f"  行数: {len(df_test)}")
    print(f"  前3行:")
    print(df_test.head(3).to_string(index=False))
    
    print("\n" + "="*60)
    print("测试任务创建")
    print("="*60)
    
    # 测试术语库任务创建
    print("\n📝 从术语库创建任务（目标语言：日语）...")
    term_tasks = TaskFactory.from_excel_file(term_file, ['日语'])
    print(f"  ✅ 创建了 {len(term_tasks)} 个任务")
    if term_tasks:
        print(f"  示例任务:")
        task = term_tasks[0]
        print(f"    - Key: {task.key}")
        print(f"    - 原文: {task.source_text}")
        print(f"    - 目标语言: {task.target_lang}")
    
    # 测试翻译测试表任务创建
    print("\n📝 从翻译测试表创建任务（目标语言：日语）...")
    test_tasks = TaskFactory.from_excel_file(test_file, ['日语'])
    print(f"  ✅ 创建了 {len(test_tasks)} 个任务")
    if test_tasks:
        print(f"  示例任务:")
        for i, task in enumerate(test_tasks[:3], 1):
            print(f"    {i}. Key: {task.key}")
            print(f"       原文: {task.source_text[:50]}...")
            print(f"       目标语言: {task.target_lang}")
    
    # 测试多语言
    print("\n📝 从翻译测试表创建任务（目标语言：日语、英语、韩语）...")
    multi_tasks = TaskFactory.from_excel_file(test_file, ['日语', '英语', '韩语'])
    print(f"  ✅ 创建了 {len(multi_tasks)} 个任务")
    print(f"  每个语言的平均任务数: {len(multi_tasks) / 3:.0f}")
    
    print("\n" + "="*60)
    print("测试结论")
    print("="*60)
    if len(term_tasks) > 0 and len(test_tasks) > 0:
        print("✅ 所有测试通过！文件结构正确，任务创建成功。")
        print("✅ 可以在GUI中使用这两个文件进行翻译。")
        return True
    else:
        print("❌ 测试失败：任务创建数量为0")
        return False

if __name__ == "__main__":
    success = test_files()
    sys.exit(0 if success else 1)
