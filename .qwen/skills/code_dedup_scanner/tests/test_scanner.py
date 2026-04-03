"""代码重复扫描器测试"""
import unittest
from pathlib import Path
from ..scanner import CodeDedupScanner


class TestCodeDedupScanner(unittest.TestCase):
    """测试代码重复扫描器"""
    
    def test_scan_duplicate_classes(self):
        """测试重复类扫描"""
        # 使用当前项目路径
        project_root = str(Path(__file__).parent.parent.parent.parent.parent)
        duplicates = CodeDedupScanner.scan_duplicate_classes(project_root)
        
        # 验证返回类型
        self.assertIsInstance(duplicates, list)
        
        # 如果有重复类，验证结构
        if duplicates:
            for dup in duplicates:
                self.assertIn('class_name', dup)
                self.assertIn('locations', dup)
    
    def test_scan_duplicate_files(self):
        """测试相似文件扫描"""
        project_root = str(Path(__file__).parent.parent.parent.parent.parent)
        similar = CodeDedupScanner.scan_duplicate_files(project_root, similarity_threshold=0.8)
        
        # 验证返回类型
        self.assertIsInstance(similar, list)
        
        # 如果有相似文件，验证结构
        if similar:
            for pair in similar:
                self.assertIn('file1', pair)
                self.assertIn('file2', pair)
                self.assertIn('similarity', pair)
    
    def test_generate_report_text(self):
        """测试文本报告生成"""
        report = CodeDedupScanner.generate_report([], [], output_format='text')
        self.assertIsInstance(report, str)
        self.assertIn('重复类', report)
    
    def test_generate_report_json(self):
        """测试JSON报告生成"""
        report = CodeDedupScanner.generate_report([], [], output_format='json')
        import json
        data = json.loads(report)
        self.assertIn('metadata', data)
    
    def test_generate_report_markdown(self):
        """测试Markdown报告生成"""
        report = CodeDedupScanner.generate_report([], [], output_format='markdown')
        self.assertIsInstance(report, str)
        self.assertIn('#', report)
    
    def test_self_test(self):
        """测试自检功能"""
        result = CodeDedupScanner.self_test()
        self.assertTrue(result)
    
    def test_normalize_line_with_keywords(self):
        """测试关键字行标准化"""
        # 测试类定义
        result = CodeDedupScanner._normalize_line('class MyClass:')
        self.assertIn('class', result)
        
        # 测试函数定义
        result = CodeDedupScanner._normalize_line('def my_function():')
        self.assertIn('def', result)
        
        # 测试if语句
        result = CodeDedupScanner._normalize_line('if x > 0:')
        self.assertIn('if', result)
    
    def test_normalize_line_with_assignment(self):
        """测试赋值语句标准化"""
        result = CodeDedupScanner._normalize_line('x = 10')
        self.assertEqual(result, 'VAR = VAR')
    
    def test_normalize_line_with_string(self):
        """测试字符串替换"""
        result = CodeDedupScanner._normalize_line('name = "test"')
        # 应该被标准化为 VAR = VAR
        self.assertEqual(result, 'VAR = VAR')
    
    def test_scan_with_invalid_project(self):
        """测试无效项目路径"""
        with self.assertRaises(ValueError):
            CodeDedupScanner.scan_duplicate_classes('/nonexistent/path')
    
    def test_scan_duplicate_files_invalid_threshold(self):
        """测试无效相似度阈值"""
        project_root = str(Path(__file__).parent.parent.parent.parent.parent)
        with self.assertRaises(ValueError):
            CodeDedupScanner.scan_duplicate_files(project_root, similarity_threshold=1.5)


if __name__ == '__main__':
    unittest.main()
