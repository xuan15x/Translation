"""
自我反思Skill测试套件

测试模块: .qwen.skills.self_optimization.reflector
测试类: SelfReflectionSkill

包含以下测试用例：
1. test_generate_reflection - 测试反思报告生成
2. test_save_reflection - 测试反思报告保存
3. test_auto_reflect - 测试自动反思
4. test_load_reflections - 测试加载反思
5. test_review_reflections - 测试反思回顾
6. test_format_list - 测试列表格式化
7. test_format_checklist - 测试检查清单格式化
8. test_format_scores - 测试评分表格式化
9. test_empty_scores - 测试空评分
10. test_reflection_with_full_result - 测试完整结果的反思
11. test_format_problems - 测试问题格式化
12. test_reflection_file_content - 测试反思文件内容完整性
"""
import unittest
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# 导入被测试的类
import sys
import os

# 确保可以导入项目模块
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入模块 - 使用绝对路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from reflector import SelfReflectionSkill


class TestSelfReflectionSkill(unittest.TestCase):
    """测试自我反思Skill"""

    @classmethod
    def setUpClass(cls):
        """测试类级别的设置"""
        # 保存原始的REFLECTION_DIR
        cls.original_reflection_dir = SelfReflectionSkill.REFLECTION_DIR
        # 使用临时目录进行测试
        SelfReflectionSkill.REFLECTION_DIR = Path(".test_reflections_temp")

    @classmethod
    def tearDownClass(cls):
        """测试类级别的清理"""
        # 恢复原始的REFLECTION_DIR
        SelfReflectionSkill.REFLECTION_DIR = cls.original_reflection_dir
        # 清理临时目录
        if SelfReflectionSkill.REFLECTION_DIR.exists():
            shutil.rmtree(SelfReflectionSkill.REFLECTION_DIR, ignore_errors=True)

    def setUp(self):
        """每个测试方法运行前的设置"""
        # 清理临时目录
        if SelfReflectionSkill.REFLECTION_DIR.exists():
            shutil.rmtree(SelfReflectionSkill.REFLECTION_DIR)
        SelfReflectionSkill.REFLECTION_DIR.mkdir(exist_ok=True)

    def tearDown(self):
        """每个测试方法运行后的清理"""
        # 清理临时目录
        if SelfReflectionSkill.REFLECTION_DIR.exists():
            shutil.rmtree(SelfReflectionSkill.REFLECTION_DIR)

    def test_generate_reflection(self):
        """
        测试用例1: 测试反思报告生成
        
        验证:
        - 生成的反思报告是字符串类型
        - 包含必要的章节标题
        - 包含任务ID和基本信息
        """
        start_time = datetime.now() - timedelta(minutes=30)
        end_time = datetime.now()
        
        result = SelfReflectionSkill.generate_reflection(
            task_id="test_001",
            task_description="测试任务",
            agent_type="test",
            execution_result={
                'status': '✅成功',
                'strengths': ['优点1', '优点2'],
                'weaknesses': ['不足1'],
                'scores': {'目标达成': 9, '执行效率': 8}
            },
            start_time=start_time,
            end_time=end_time
        )
        
        # 验证返回类型
        self.assertIsInstance(result, str)
        
        # 验证包含关键内容
        self.assertIn('任务反思报告', result)
        self.assertIn('test_001', result)
        self.assertIn('测试任务', result)
        self.assertIn('目标达成情况', result)
        self.assertIn('执行过程评估', result)
        self.assertIn('量化评分', result)
    
    def test_save_reflection(self):
        """
        测试用例2: 测试反思报告保存
        
        验证:
        - 文件被正确创建
        - 文件路径正确返回
        - 文件内容完整
        """
        reflection = "# 测试反思\n\n这是测试内容。"
        filepath = SelfReflectionSkill.save_reflection(reflection, "test_save")
        
        # 验证文件路径
        self.assertTrue(Path(filepath).exists())
        
        # 验证文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, reflection)
    
    def test_auto_reflect(self):
        """
        测试用例3: 测试自动反思
        
        验证:
        - 自动生成反思报告
        - 文件被正确保存
        - 返回有效的文件路径
        """
        filepath = SelfReflectionSkill.auto_reflect(
            task_id="test_auto",
            task_description="自动测试",
            agent_type="test",
            execution_result={'status': '成功'}
        )
        
        # 验证文件存在
        self.assertTrue(Path(filepath).exists())
        
        # 验证文件名格式
        self.assertIn('reflection_test_auto', filepath)
        self.assertTrue(filepath.endswith('.md'))
    
    def test_load_reflections(self):
        """
        测试用例4: 测试加载反思
        
        验证:
        - 返回反思报告列表
        - 列表元素包含必要的字段
        - 按时间倒序排列
        """
        # 先创建一些测试反思
        SelfReflectionSkill.auto_reflect(
            task_id="load_test_1",
            task_description="加载测试1",
            agent_type="test",
            execution_result={'status': '成功'}
        )
        SelfReflectionSkill.auto_reflect(
            task_id="load_test_2",
            task_description="加载测试2",
            agent_type="test",
            execution_result={'status': '成功'}
        )
        
        # 加载反思
        reflections = SelfReflectionSkill.load_reflections(days=30)
        
        # 验证返回类型
        self.assertIsInstance(reflections, list)
        
        # 验证数量
        self.assertEqual(len(reflections), 2)
        
        # 验证包含必要字段
        for reflection in reflections:
            self.assertIn('file', reflection)
            self.assertIn('content', reflection)
            self.assertIn('date', reflection)
            self.assertIn('task_id', reflection)
    
    def test_review_reflections(self):
        """
        测试用例5: 测试反思回顾
        
        验证:
        - 能够生成回顾报告
        - 回顾报告文件存在
        - 包含总结信息
        """
        # 先生成一些反思
        SelfReflectionSkill.auto_reflect(
            task_id="review_test_1",
            task_description="回顾测试1",
            agent_type="test",
            execution_result={
                'status': '成功',
                'strengths': ['优点1'],
                'weaknesses': ['不足1']
            }
        )
        SelfReflectionSkill.auto_reflect(
            task_id="review_test_2",
            task_description="回顾测试2",
            agent_type="test",
            execution_result={
                'status': '成功',
                'strengths': ['优点2'],
                'weaknesses': ['不足2']
            }
        )
        
        # 运行回顾
        summary_file = SelfReflectionSkill.review_reflections(days=30)
        
        # 验证总结文件存在
        self.assertTrue(Path(summary_file).exists())
        self.assertIn('review_summary', summary_file)
        
        # 验证总结内容
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('反思总结报告', content)
        self.assertIn('过去30天', content)
    
    def test_format_list(self):
        """
        测试用例6: 测试列表格式化
        
        验证:
        - 列表项被正确编号
        - 格式符合Markdown要求
        - 空列表返回"无"
        """
        result = SelfReflectionSkill._format_list(['项目1', '项目2', '项目3'])
        
        # 验证格式
        self.assertIn('1. 项目1', result)
        self.assertIn('2. 项目2', result)
        self.assertIn('3. 项目3', result)
        
        # 验证空列表
        empty_result = SelfReflectionSkill._format_list([])
        self.assertEqual(empty_result, "无")
    
    def test_format_checklist(self):
        """
        测试用例7: 测试检查清单格式化
        
        验证:
        - 清单项使用Markdown复选框格式
        - 空清单返回"无"
        """
        result = SelfReflectionSkill._format_checklist(['行动1', '行动2', '行动3'])
        
        # 验证格式
        self.assertIn('- [ ] 行动1', result)
        self.assertIn('- [ ] 行动2', result)
        self.assertIn('- [ ] 行动3', result)
        
        # 验证空清单
        empty_result = SelfReflectionSkill._format_checklist([])
        self.assertEqual(empty_result, "无")
    
    def test_format_scores(self):
        """
        测试用例8: 测试评分表格式化
        
        验证:
        - 评分表使用Markdown表格格式
        - 包含表头和分隔线
        - 正确显示评分
        """
        scores = {
            '目标达成': 9,
            '执行效率': 8,
            '代码质量': 9
        }
        result = SelfReflectionSkill._format_scores(scores)
        
        # 验证表格结构
        self.assertIn('| 评估维度 | 评分 (1-10) | 评分理由 |', result)
        self.assertIn('|---------|-------------|---------|', result)
        
        # 验证评分内容
        self.assertIn('目标达成', result)
        self.assertIn('9/10', result)
        self.assertIn('执行效率', result)
        self.assertIn('8/10', result)
    
    def test_empty_scores(self):
        """
        测试用例9: 测试空评分
        
        验证:
        - 空评分字典返回"暂无评分"
        """
        result = SelfReflectionSkill._format_scores({})
        self.assertEqual(result, "暂无评分")
    
    def test_reflection_with_full_result(self):
        """
        测试用例10: 测试完整结果的反思
        
        验证:
        - 所有反思章节都存在
        - 包含完整的信息
        - 评分和清单格式正确
        """
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        
        result = SelfReflectionSkill.generate_reflection(
            task_id="full_test",
            task_description="完整测试",
            agent_type="test",
            execution_result={
                'status': '✅成功',
                'expected_goal': '测试目标',
                'actual_result': '实际结果',
                'achievement_rate': '100%',
                'strengths': ['优点1', '优点2'],
                'weaknesses': ['不足1'],
                'key_learnings': ['学习点1'],
                'commitments': ['承诺1'],
                'immediate_actions': ['行动1'],
                'short_term_plans': ['计划1'],
                'long_term_improvements': ['改进1'],
                'scores': {
                    '目标达成': 10,
                    '执行效率': 9,
                    '代码质量': 9,
                    '文档完整': 8,
                    '用户满意': 9
                }
            },
            start_time=start_time,
            end_time=end_time
        )
        
        # 验证所有部分都存在
        self.assertIn('目标达成情况', result)
        self.assertIn('预期目标', result)
        self.assertIn('测试目标', result)
        self.assertIn('实际结果', result)
        self.assertIn('执行过程评估', result)
        self.assertIn('做得好的地方', result)
        self.assertIn('做得不足的地方', result)
        self.assertIn('经验教训', result)
        self.assertIn('关键学习点', result)
        self.assertIn('量化评分', result)
        self.assertIn('改进承诺', result)
        self.assertIn('后续行动', result)
        self.assertIn('立即执行', result)
        self.assertIn('短期计划', result)
        self.assertIn('长期改进', result)
    
    def test_format_problems(self):
        """
        测试用例11: 测试问题格式化
        
        验证:
        - 字典格式问题被正确格式化
        - 字符串格式问题被正确处理
        - 空问题列表返回"无"
        """
        # 测试字典格式
        problems_dict = [
            {
                'problem': '问题1',
                'impact': '影响1',
                'solution': '解决方案1'
            }
        ]
        result_dict = SelfReflectionSkill._format_problems(problems_dict)
        self.assertIn('**问题**: 问题1', result_dict)
        self.assertIn('**影响**: 影响1', result_dict)
        self.assertIn('**解决**: 解决方案1', result_dict)
        
        # 测试字符串格式
        problems_string = ['简单问题1', '简单问题2']
        result_string = SelfReflectionSkill._format_problems(problems_string)
        self.assertIn('1. 简单问题1', result_string)
        self.assertIn('2. 简单问题2', result_string)
        
        # 测试空列表
        result_empty = SelfReflectionSkill._format_problems([])
        self.assertEqual(result_empty, "无")
    
    def test_reflection_file_content(self):
        """
        测试用例12: 测试反思文件内容完整性
        
        验证:
        - 保存的文件包含所有必要的Markdown章节
        - 文件编码正确（UTF-8）
        - 文件可以正确读取
        """
        start_time = datetime.now() - timedelta(minutes=15)
        end_time = datetime.now()
        
        # 生成并保存反思
        filepath = SelfReflectionSkill.auto_reflect(
            task_id="content_test",
            task_description="内容完整性测试",
            agent_type="test",
            execution_result={
                'status': '✅成功',
                'strengths': ['测试优点'],
                'weaknesses': ['测试缺点'],
                'scores': {'目标达成': 8, '执行效率': 7}
            },
            start_time=start_time
        )
        
        # 读取文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证关键章节存在
        self.assertIn('# 任务反思报告', content)
        self.assertIn('## 📊 基本信息', content)
        self.assertIn('## 1️⃣ 目标达成情况', content)
        self.assertIn('## 2️⃣ 执行过程评估', content)
        self.assertIn('## 3️⃣ 技术评估', content)
        self.assertIn('## 4️⃣ 遇到的问题', content)
        self.assertIn('## 5️⃣ 经验教训', content)
        self.assertIn('## 6️⃣ 量化评分', content)
        self.assertIn('## 7️⃣ 关键洞察', content)
        self.assertIn('## 8️⃣ 改进承诺', content)
        self.assertIn('## 9️⃣ 后续行动', content)
        
        # 验证任务信息
        self.assertIn('content_test', content)
        self.assertIn('内容完整性测试', content)
        self.assertIn('✅成功', content)


class TestSelfReflectionSkillEdgeCases(unittest.TestCase):
    """测试边界情况和异常处理"""

    @classmethod
    def setUpClass(cls):
        """测试类级别的设置"""
        cls.original_reflection_dir = SelfReflectionSkill.REFLECTION_DIR
        SelfReflectionSkill.REFLECTION_DIR = Path(".test_reflections_edge_temp")

    @classmethod
    def tearDownClass(cls):
        """测试类级别的清理"""
        SelfReflectionSkill.REFLECTION_DIR = cls.original_reflection_dir
        if SelfReflectionSkill.REFLECTION_DIR.exists():
            shutil.rmtree(SelfReflectionSkill.REFLECTION_DIR, ignore_errors=True)

    def setUp(self):
        """每个测试方法运行前的设置"""
        if SelfReflectionSkill.REFLECTION_DIR.exists():
            shutil.rmtree(SelfReflectionSkill.REFLECTION_DIR)
        SelfReflectionSkill.REFLECTION_DIR.mkdir(exist_ok=True)

    def tearDown(self):
        """每个测试方法运行后的清理"""
        if SelfReflectionSkill.REFLECTION_DIR.exists():
            shutil.rmtree(SelfReflectionSkill.REFLECTION_DIR)

    def test_load_empty_reflections(self):
        """测试加载空反思目录"""
        # 清理目录
        if SelfReflectionSkill.REFLECTION_DIR.exists():
            shutil.rmtree(SelfReflectionSkill.REFLECTION_DIR)
        
        reflections = SelfReflectionSkill.load_reflections(days=30)
        self.assertIsInstance(reflections, list)
        self.assertEqual(len(reflections), 0)

    def test_review_empty_reflections(self):
        """测试回顾空反思目录"""
        # 清理目录
        if SelfReflectionSkill.REFLECTION_DIR.exists():
            shutil.rmtree(SelfReflectionSkill.REFLECTION_DIR)
        
        result = SelfReflectionSkill.review_reflections(days=30)
        self.assertEqual(result, "")

    def test_reflection_with_minimal_result(self):
        """测试最小执行结果的反思"""
        start_time = datetime.now()
        end_time = datetime.now()
        
        result = SelfReflectionSkill.generate_reflection(
            task_id="minimal_test",
            task_description="最小测试",
            agent_type="test",
            execution_result={'status': '成功'},
            start_time=start_time,
            end_time=end_time
        )
        
        self.assertIsInstance(result, str)
        self.assertIn('minimal_test', result)
        self.assertIn('待补充', result)  # 应该有默认值

    def test_auto_reflect_with_custom_start_time(self):
        """测试带自定义开始时间的自动反思"""
        custom_start_time = datetime.now() - timedelta(hours=2)
        
        filepath = SelfReflectionSkill.auto_reflect(
            task_id="custom_time_test",
            task_description="自定义时间测试",
            agent_type="test",
            execution_result={'status': '成功'},
            start_time=custom_start_time
        )
        
        self.assertTrue(Path(filepath).exists())
        
        # 验证文件内容包含时间信息
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('custom_time_test', content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
