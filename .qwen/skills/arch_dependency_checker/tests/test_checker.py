"""架构依赖检查器测试"""
import unittest
from pathlib import Path
from ..checker import ArchDependencyChecker


class TestArchDependencyChecker(unittest.TestCase):
    """测试架构依赖检查器"""
    
    def test_check_project(self):
        """测试项目架构检查"""
        project_root = str(Path(__file__).parent.parent.parent.parent.parent)
        result = ArchDependencyChecker.check_project(project_root)
        
        # 验证返回类型
        self.assertIsInstance(result, dict)
        self.assertIn('violations', result)
        self.assertIn('summary', result)
    
    def test_check_file(self):
        """测试单文件架构检查"""
        # 使用项目中的任意Python文件
        test_file = str(Path(__file__).parent.parent / 'checker.py')
        project_root = str(Path(__file__).parent.parent.parent.parent.parent)
        
        violations = ArchDependencyChecker.check_file(test_file, project_root)
        
        # 验证返回类型
        self.assertIsInstance(violations, list)
    
    def test_generate_report_text(self):
        """测试文本报告生成"""
        report = ArchDependencyChecker.generate_report([], output_format='text')
        self.assertIsInstance(report, str)
    
    def test_generate_report_json(self):
        """测试JSON报告生成"""
        report = ArchDependencyChecker.generate_report([], output_format='json')
        import json
        data = json.loads(report)
        self.assertIsInstance(data, dict)
    
    def test_generate_report_markdown(self):
        """测试Markdown报告生成"""
        report = ArchDependencyChecker.generate_report([], output_format='markdown')
        self.assertIsInstance(report, str)
    
    def test_self_test(self):
        """测试自检功能"""
        result = ArchDependencyChecker.self_test()
        self.assertTrue(result)
    
    def test_check_invalid_project(self):
        """测试无效项目路径"""
        with self.assertRaises(ValueError):
            ArchDependencyChecker.check_project('/nonexistent/path')
    
    def test_check_invalid_file(self):
        """测试无效文件路径"""
        project_root = str(Path(__file__).parent.parent.parent.parent.parent)
        with self.assertRaises(ValueError):
            ArchDependencyChecker.check_file('/nonexistent/file.py', project_root)
    
    def test_merge_rules(self):
        """测试规则合并"""
        # 测试无自定义规则
        rules = ArchDependencyChecker._merge_rules(None)
        self.assertIn('domain', rules)
        
        # 测试自定义规则
        custom_rules = {
            'domain': {
                'can_import': ['domain', 'infrastructure'],
                'cannot_import': ['service'],
                'description': '自定义领域层规则'
            }
        }
        rules = ArchDependencyChecker._merge_rules(custom_rules)
        self.assertIn('infrastructure', rules['domain']['can_import'])
    
    def test_assess_severity(self):
        """测试严重程度评估"""
        # domain层违规应该是high
        severity = ArchDependencyChecker._assess_severity('domain', 'infrastructure')
        self.assertEqual(severity, 'high')
        
        # data_access访问service应该是medium
        severity = ArchDependencyChecker._assess_severity('data_access', 'service')
        self.assertEqual(severity, 'medium')
    
    def test_generate_suggestion(self):
        """测试修复建议生成"""
        suggestion = ArchDependencyChecker._generate_suggestion('domain', 'infrastructure')
        self.assertIsInstance(suggestion, str)
        self.assertGreater(len(suggestion), 0)


if __name__ == '__main__':
    unittest.main()
