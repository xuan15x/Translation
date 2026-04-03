"""
架构依赖检查器测试

验证 ArchDependencyChecker 的各项功能：
1. 检测 domain 导入 infrastructure
2. 检测 data_access 导入 service
3. 测试合规导入不被误报
4. 测试报告生成
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import TestCase

# 添加项目根目录和.qwen/skills到 sys.path
project_root = Path(__file__).parent.parent
skills_dir = project_root / '.qwen' / 'skills'
sys.path.insert(0, str(skills_dir))

from arch_dependency_checker import ArchDependencyChecker


class TestArchDependencyChecker(TestCase):
    """架构依赖检查器测试类"""

    def setUp(self):
        """设置测试环境"""
        # 创建临时项目目录
        self.test_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.test_dir.name)

        # 创建六层架构目录
        for layer in ['presentation', 'application', 'domain', 'service', 'data_access', 'infrastructure']:
            (self.project_root / layer).mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """清理测试环境"""
        self.test_dir.cleanup()

    def _create_python_file(self, relative_path: str, content: str):
        """创建 Python 测试文件"""
        file_path = self.project_root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')

    def test_domain_imports_infrastructure(self):
        """测试 1: 检测 domain 导入 infrastructure"""
        # 创建 domain 层文件，导入 infrastructure
        self._create_python_file(
            'domain/services.py',
            'from infrastructure.cache import CacheManager\n\nclass DomainService:\n    pass\n'
        )

        # 创建 infrastructure 层文件
        self._create_python_file(
            'infrastructure/cache.py',
            'class CacheManager:\n    pass\n'
        )

        # 执行检查
        violations = ArchDependencyChecker.check_file(
            str(self.project_root / 'domain/services.py'),
            project_root=str(self.project_root)
        )

        # 验证结果
        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation['source_layer'], 'domain')
        self.assertEqual(violation['target_layer'], 'infrastructure')
        self.assertEqual(violation['severity'], 'high')
        self.assertIn('infrastructure', violation['rule_violated'])

    def test_data_access_imports_service(self):
        """测试 2: 检测 data_access 导入 service"""
        # 创建 data_access 层文件，导入 service
        self._create_python_file(
            'data_access/repositories.py',
            'from service.api_provider import APIProviderManager\n\nclass Repository:\n    pass\n'
        )

        # 创建 service 层文件
        self._create_python_file(
            'service/api_provider.py',
            'class APIProviderManager:\n    pass\n'
        )

        # 执行检查
        violations = ArchDependencyChecker.check_file(
            str(self.project_root / 'data_access/repositories.py'),
            project_root=str(self.project_root)
        )

        # 验证结果
        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation['source_layer'], 'data_access')
        self.assertEqual(violation['target_layer'], 'service')
        self.assertEqual(violation['severity'], 'medium')
        self.assertIn('service', violation['rule_violated'])

    def test_compliant_imports_no_false_positives(self):
        """测试 3: 测试合规导入不被误报"""
        # 创建 domain 层文件，只导入 domain 内部
        self._create_python_file(
            'domain/models.py',
            'from domain.services import DomainService\n\nclass Model:\n    pass\n'
        )

        # 创建 domain.services 文件
        self._create_python_file(
            'domain/services.py',
            'class DomainService:\n    pass\n'
        )

        # 执行检查
        violations = ArchDependencyChecker.check_file(
            str(self.project_root / 'domain/models.py'),
            project_root=str(self.project_root)
        )

        # 验证没有违规
        self.assertEqual(len(violations), 0)

    def test_application_can_import_domain_and_service(self):
        """测试 4: application 层可以导入 domain 和 service 层"""
        # 创建 application 层文件
        self._create_python_file(
            'application/facade.py',
            'from domain.services import DomainService\nfrom service.api_provider import APIProvider\n\nclass Facade:\n    pass\n'
        )

        # 创建 domain 和 service 层文件
        self._create_python_file('domain/services.py', 'class DomainService:\n    pass\n')
        self._create_python_file('service/api_provider.py', 'class APIProvider:\n    pass\n')

        # 执行检查
        violations = ArchDependencyChecker.check_file(
            str(self.project_root / 'application/facade.py'),
            project_root=str(self.project_root)
        )

        # 验证没有违规（application 可以导入 domain 和 service）
        self.assertEqual(len(violations), 0)

    def test_presentation_should_not_import_low_layers(self):
        """测试 5: presentation 层不应直接导入低层"""
        # 创建 presentation 层文件，直接导入 service
        self._create_python_file(
            'presentation/gui.py',
            'from service.api_provider import APIProvider\n\nclass GUI:\n    pass\n'
        )

        # 创建 service 层文件
        self._create_python_file('service/api_provider.py', 'class APIProvider:\n    pass\n')

        # 执行检查
        violations = ArchDependencyChecker.check_file(
            str(self.project_root / 'presentation/gui.py'),
            project_root=str(self.project_root)
        )

        # 验证有违规
        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation['source_layer'], 'presentation')
        self.assertEqual(violation['target_layer'], 'service')
        self.assertEqual(violation['severity'], 'medium')

    def test_infrastructure_should_not_access_domain(self):
        """测试 6: infrastructure 层不应访问 domain"""
        # 创建 infrastructure 层文件，导入 domain
        self._create_python_file(
            'infrastructure/utils.py',
            'from domain.models import DomainModel\n\ndef utility_function():\n    pass\n'
        )

        # 创建 domain 层文件
        self._create_python_file('domain/models.py', 'class DomainModel:\n    pass\n')

        # 执行检查
        violations = ArchDependencyChecker.check_file(
            str(self.project_root / 'infrastructure/utils.py'),
            project_root=str(self.project_root)
        )

        # 验证有违规
        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation['source_layer'], 'infrastructure')
        self.assertEqual(violation['target_layer'], 'domain')
        self.assertEqual(violation['severity'], 'medium')

    def test_report_generation_text(self):
        """测试 7: 生成文本格式报告"""
        # 创建违规数据
        violations = [
            {
                'source_file': 'domain/services.py',
                'source_layer': 'domain',
                'target_file': 'infrastructure/cache.py',
                'target_layer': 'infrastructure',
                'import_statement': 'from infrastructure.cache import CacheManager',
                'line_number': 15,
                'rule_violated': 'domain 层不应导入 infrastructure 层',
                'severity': 'high',
                'suggestion': '考虑使用依赖注入或接口抽象'
            }
        ]

        # 生成报告
        report = ArchDependencyChecker.generate_report(violations, output_format='text')

        # 验证报告内容
        self.assertIn('架构依赖检查报告', report)
        self.assertIn('domain/services.py', report)
        self.assertIn('infrastructure', report)
        self.assertIn('严重', report)

    def test_report_generation_json(self):
        """测试 8: 生成 JSON 格式报告"""
        # 创建违规数据
        violations = [
            {
                'source_file': 'domain/services.py',
                'source_layer': 'domain',
                'target_file': 'infrastructure/cache.py',
                'target_layer': 'infrastructure',
                'import_statement': 'from infrastructure.cache import CacheManager',
                'line_number': 15,
                'rule_violated': 'domain 层不应导入 infrastructure 层',
                'severity': 'high',
                'suggestion': '考虑使用依赖注入或接口抽象'
            }
        ]

        # 生成报告
        report = ArchDependencyChecker.generate_report(violations, output_format='json')

        # 验证报告可以解析
        data = json.loads(report)
        self.assertIn('violations', data)
        self.assertIn('summary', data)
        self.assertIn('metadata', data)
        self.assertEqual(len(data['violations']), 1)

    def test_report_generation_markdown(self):
        """测试 9: 生成 Markdown 格式报告"""
        # 创建违规数据
        violations = [
            {
                'source_file': 'domain/services.py',
                'source_layer': 'domain',
                'target_file': 'infrastructure/cache.py',
                'target_layer': 'infrastructure',
                'import_statement': 'from infrastructure.cache import CacheManager',
                'line_number': 15,
                'rule_violated': 'domain 层不应导入 infrastructure 层',
                'severity': 'high',
                'suggestion': '考虑使用依赖注入或接口抽象'
            }
        ]

        # 生成报告
        report = ArchDependencyChecker.generate_report(violations, output_format='markdown')

        # 验证报告内容
        self.assertIn('# 架构依赖检查报告', report)
        self.assertIn('`domain/services.py`', report)
        self.assertIn('🔴 严重', report)

    def test_project_scan(self):
        """测试 10: 扫描整个项目"""
        # 创建多个违规文件
        self._create_python_file(
            'domain/services.py',
            'from infrastructure.cache import CacheManager\n\nclass DomainService:\n    pass\n'
        )
        self._create_python_file(
            'data_access/repositories.py',
            'from service.api_provider import APIProvider\n\nclass Repository:\n    pass\n'
        )
        self._create_python_file(
            'infrastructure/cache.py',
            'class CacheManager:\n    pass\n'
        )
        self._create_python_file(
            'service/api_provider.py',
            'class APIProvider:\n    pass\n'
        )

        # 执行检查
        result = ArchDependencyChecker.check_project(str(self.project_root))

        # 验证结果
        self.assertIn('violations', result)
        self.assertIn('summary', result)
        self.assertGreater(len(result['violations']), 0)
        self.assertEqual(result['summary']['total_violations'], len(result['violations']))

    def test_self_test(self):
        """测试 11: 自检测试"""
        # 执行自检
        result = ArchDependencyChecker.self_test()
        self.assertTrue(result)

    def test_custom_rules(self):
        """测试 12: 自定义规则"""
        # 创建 domain 层文件，导入 infrastructure.models
        self._create_python_file(
            'domain/services.py',
            'from infrastructure.models import BaseModel\n\nclass DomainService:\n    pass\n'
        )

        # 创建 infrastructure 层文件
        self._create_python_file('infrastructure/models.py', 'class BaseModel:\n    pass\n')

        # 使用默认规则检查（应该违规）
        violations_default = ArchDependencyChecker.check_file(
            str(self.project_root / 'domain/services.py'),
            project_root=str(self.project_root)
        )
        self.assertGreater(len(violations_default), 0)

        # 使用自定义规则检查（允许 domain 访问 infrastructure.models）
        custom_rules = {
            'domain': {
                'can_import': ['domain', 'infrastructure.models'],
                'cannot_import': ['infrastructure', 'service', 'data_access', 'presentation']
            }
        }

        violations_custom = ArchDependencyChecker.check_file(
            str(self.project_root / 'domain/services.py'),
            project_root=str(self.project_root),
            custom_rules=custom_rules
        )
        # 应该没有违规（因为允许访问 infrastructure.models）
        self.assertEqual(len(violations_custom), 0)

    def test_exclude_dirs(self):
        """测试 13: 排除目录"""
        # 创建 tests 目录（应该被排除）
        (self.project_root / 'tests').mkdir(exist_ok=True)

        # 在 tests 目录创建文件，导入 infrastructure
        self._create_python_file(
            'tests/test_services.py',
            'from infrastructure.cache import CacheManager\n\ndef test_service():\n    pass\n'
        )

        # 创建 infrastructure 层文件
        self._create_python_file('infrastructure/cache.py', 'class CacheManager:\n    pass\n')

        # 使用默认排除配置（包含 tests）
        result = ArchDependencyChecker.check_project(str(self.project_root))

        # tests 目录应该被排除，所以不应该有违规
        test_violations = [
            v for v in result['violations']
            if 'tests' in v['source_file']
        ]
        self.assertEqual(len(test_violations), 0)

    def test_strict_mode(self):
        """测试 14: 严格模式"""
        # 创建 presentation 层文件，导入 service（低严重程度）
        self._create_python_file(
            'presentation/gui.py',
            'from service.api_provider import APIProvider\n\nclass GUI:\n    pass\n'
        )

        # 创建 service 层文件
        self._create_python_file('service/api_provider.py', 'class APIProvider:\n    pass\n')

        # 非严格模式
        result_normal = ArchDependencyChecker.check_project(
            str(self.project_root),
            strict_mode=False
        )

        # 严格模式
        result_strict = ArchDependencyChecker.check_project(
            str(self.project_root),
            strict_mode=True
        )

        # 验证严格模式提升了严重程度
        normal_violation = result_normal['violations'][0]
        strict_violation = result_strict['violations'][0]

        self.assertEqual(normal_violation['severity'], 'medium')
        self.assertEqual(strict_violation['severity'], 'medium')  # 严格模式下 low 提升为 medium


if __name__ == '__main__':
    import unittest
    unittest.main()
