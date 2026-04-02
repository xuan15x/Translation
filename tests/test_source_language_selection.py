"""
源语言选择功能测试
测试 GUI 中新增的源语言选择功能
"""
import pandas as pd
import tempfile
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_source_language_detection():
    """测试源语言自动检测功能"""
    
    # 创建测试 Excel 文件
    test_data = {
        'Key': ['row_1', 'row_2', 'row_3'],
        '中文原文': ['提交', '取消', '保存'],
        '英语原文': ['Submit', 'Cancel', 'Save'],
        '日语原文': ['送信', 'キャンセル', '保存'],
        '备注': ['按钮', '按钮', '按钮']  # 这列应该被排除
    }
    
    df = pd.DataFrame(test_data)
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        temp_path = f.name
        df.to_excel(temp_path, index=False, engine='openpyxl')
    
    try:
        # 模拟 GUI 中的检测逻辑
        df = pd.read_excel(temp_path, engine='openpyxl')
        columns = df.columns.tolist()
        
        # 排除常见的非源语言列名
        exclude_patterns = ['key', 'id', '序号', '编号', 'status', '备注', 'note']
        
        # 过滤出可能的源语言列
        available_langs = []
        for col in columns:
            col_lower = str(col).lower()
            # 检查是否包含排除关键词
            is_excluded = any(pattern in col_lower for pattern in exclude_patterns)
            
            if not is_excluded:
                # 进一步检查：该列是否有非空数据
                if df[col].notna().any():
                    available_langs.append(str(col))
        
        print("=" * 80)
        print("源语言检测结果")
        print("=" * 80)
        print(f"📋 Excel 文件所有列：{columns}")
        print(f"✅ 检测到的可用源语言：{available_langs}")
        print(f"📊 检测到 {len(available_langs)} 个源语言")
        
        # 验证结果
        assert len(available_langs) == 3, f"应该检测到 3 个源语言，但检测到 {len(available_langs)} 个"
        assert '中文原文' in available_langs, "应该包含'中文原文'"
        assert '英语原文' in available_langs, "应该包含'英语原文'"
        assert '日语原文' in available_langs, "应该包含'日语原文'"
        assert '备注' not in available_langs, "'备注' 应该被排除"
        assert 'Key' not in available_langs, "'Key' 应该被排除"
        
        print("\n✅ 所有测试通过！")
        print("\n💡 用户可以在 GUI 中选择以下源语言之一进行翻译:")
        for i, lang in enumerate(available_langs, 1):
            print(f"   {i}. {lang}")
        
    finally:
        os.remove(temp_path)


def test_task_creation_with_source_language():
    """测试使用指定源语言创建任务"""
    from application.result_builder import TaskFactory
    
    # 创建测试 Excel 文件（多语言混合）
    # 注意：需要包含目标语言列，否则不会创建任务
    test_data = {
        'Key': ['row_1', 'row_2', 'row_3'],
        '中文原文': ['提交', '取消', '保存'],
        '英语原文': ['Submit', 'Cancel', 'Save'],
        '日语原文': ['送信', 'キャンセル', '保存'],
        '韩语': ['', '', ''],  # 目标语言列（空的需要被填充）
        '法语': ['', '', '']   # 目标语言列
    }
    
    df = pd.DataFrame(test_data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        temp_path = f.name
        df.to_excel(temp_path, index=False, engine='openpyxl')
    
    try:
        print("\n" + "=" * 80)
        print("测试任务创建（使用不同源语言）")
        print("=" * 80)
        
        target_langs = ['韩语', '法语']
        
        # 场景 1: 使用中文原文作为源语言
        print("\n📌 场景 1: 使用'中文原文'作为源语言")
        tasks_zh = TaskFactory.from_excel_file(temp_path, target_langs, source_lang='中文原文')
        print(f"   创建任务数：{len(tasks_zh)}")
        print(f"   示例原文：{tasks_zh[0].source_text if tasks_zh else 'N/A'}")
        assert len(tasks_zh) == 6, f"应该创建 6 个任务（3 行 x 2 个目标语言），但创建了 {len(tasks_zh)} 个"
        assert tasks_zh[0].source_text == '提交', f"原文应该是'提交'，但是 {tasks_zh[0].source_text}"
        
        # 场景 2: 使用英语原文作为源语言
        print("\n📌 场景 2: 使用'英语原文'作为源语言")
        tasks_en = TaskFactory.from_excel_file(temp_path, target_langs, source_lang='英语原文')
        print(f"   创建任务数：{len(tasks_en)}")
        print(f"   示例原文：{tasks_en[0].source_text if tasks_en else 'N/A'}")
        assert len(tasks_en) == 6, f"应该创建 6 个任务，但创建了 {len(tasks_en)} 个"
        assert tasks_en[0].source_text == 'Submit', f"原文应该是'Submit'，但是 {tasks_en[0].source_text}"
        
        # 场景 3: 使用日语原文作为源语言
        print("\n📌 场景 3: 使用'日语原文'作为源语言")
        tasks_ja = TaskFactory.from_excel_file(temp_path, target_langs, source_lang='日语原文')
        print(f"   创建任务数：{len(tasks_ja)}")
        print(f"   示例原文：{tasks_ja[0].source_text if tasks_ja else 'N/A'}")
        assert len(tasks_ja) == 6, f"应该创建 6 个任务，但创建了 {len(tasks_ja)} 个"
        assert tasks_ja[0].source_text == '送信', f"原文应该是'送信'，但是 {tasks_ja[0].source_text}"
        
        # 场景 4: 不指定源语言（默认使用'中文原文'）
        print("\n📌 场景 4: 不指定源语言（默认行为）")
        tasks_default = TaskFactory.from_excel_file(temp_path, target_langs, source_lang=None)
        print(f"   创建任务数：{len(tasks_default)}")
        print(f"   示例原文：{tasks_default[0].source_text if tasks_default else 'N/A'}")
        assert len(tasks_default) == 6, f"应该创建 6 个任务，但创建了 {len(tasks_default)} 个"
        assert tasks_default[0].source_text == '提交', f"原文应该是'提交'，但是 {tasks_default[0].source_text}"
        
        print("\n✅ 所有任务创建测试通过！")
        
    finally:
        os.remove(temp_path)


if __name__ == '__main__':
    print("开始测试源语言选择功能...\n")
    
    # 测试 1: 源语言检测
    test_source_language_detection()
    
    # 测试 2: 任务创建
    test_task_creation_with_source_language()
    
    print("\n" + "=" * 80)
    print("🎉 所有测试完成！")
    print("=" * 80)
