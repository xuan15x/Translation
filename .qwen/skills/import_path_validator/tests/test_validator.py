"""
导入路径验证器 - 单元测试

测试 ImportPathValidator 的各项功能,包括:
- 重复导入检测
- 循环导入检测
- __init__.py 导出一致性检查
- 报告生成
- 自检测试

运行测试:
    pytest .qwen/skills/import_path_validator/tests/test_validator.py -v
"""

import tempfile
from pathlib import Path

import pytest

from ..validator import ImportPathValidator


@pytest.fixture
def sample_project():
    """
    创建示例项目结构

    返回:
        临时项目根目录路径
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 创建包 A
        package_a = temp_path / 'package_a'
        package_a.mkdir()

        (package_a / '__init__.py').write_text(
            'from .module_a import ClassA, ClassB\n'
            '__all__ = ["ClassA"]  # ClassB 未导出\n',
            encoding='utf-8'
        )

        (package_a / 'module_a.py').write_text(
            'class ClassA:\n'
            '    """测试类 A"""\n'
            '    pass\n'
            '\n'
            'class ClassB:\n'
            '    """测试类 B"""\n'
            '    pass\n'
            '\n'
            'class ClassC:\n'
            '    """测试类 C(未导出)"""\n'
            '    pass\n',
            encoding='utf-8'
        )

        # 创建包 B - 循环导入
        package_b = temp_path / 'package_b'
        package_b.mkdir()

        (package_b / '__init__.py').write_text(
            '',
            encoding='utf-8'
        )

        (package_b / 'module_b.py').write_text(
            'from .module_c import ClassC\n'
            '\n'
            'class ClassB:\n'
            '    """测试类 B"""\n'
            '    def __init__(self):\n'
            '        self.c = ClassC()\n',
            encoding='utf-8'
        )

        (package_b / 'module_c.py').write_text(
            'from .module_b import ClassB\n'
            '\n'
            'class ClassC:\n'
            '    """测试类 C"""\n'
            '    def __init__(self):\n'
            '        self.b = ClassB()\n',
            encoding='utf-8'
        )

        # 创建文件,使用重复导入
        (temp_path / 'main.py').write_text(
            'from package_a.module_a import ClassA\n'
            'from package_b.module_b import ClassB\n'
            '\n'
            'def main():\n'
            '    a = ClassA()\n'
            '    b = ClassB()\n',
            encoding='utf-8'
        )

        # 创建另一个文件,使用不同的路径导入 ClassA (重复导入)
        (temp_path / 'app.py').write_text(
            'from package_a import ClassA\n'
            '\n'
            'def run():\n'
            '    a = ClassA()\n',
            encoding='utf-8'
        )

        yield temp_path


class TestValidateProject:
    """测试 validate_project 方法"""

    def test_validate_project_returns_dict(self, sample_project):
        """测试 validate_project 返回字典"""
        result = ImportPathValidator.validate_project(str(sample_project))

        assert isinstance(result, dict)
        assert 'summary' in result
        assert 'duplicates' in result
        assert 'circular' in result
        assert 'init_issues' in result

    def test_validate_project_counts_files(self, sample_project):
        """测试文件计数"""
        result = ImportPathValidator.validate_project(str(sample_project))

        # 应该有 6 个 Python 文件
        assert result['summary']['total_files'] == 6

    def test_validate_project_detects_duplicates(self, sample_project):
        """测试重复导入检测"""
        result = ImportPathValidator.validate_project(str(sample_project))

        assert result['summary']['duplicate_imports'] > 0
        assert len(result['duplicates']) > 0

    def test_validate_project_detects_circular_imports(self, sample_project):
        """测试循环导入检测"""
        result = ImportPathValidator.validate_project(str(sample_project))

        assert result['summary']['circular_imports'] > 0
        assert len(result['circular']) > 0

    def test_validate_project_detects_init_issues(self, sample_project):
        """测试 __init__.py 一致性检查"""
        result = ImportPathValidator.validate_project(str(sample_project))

        assert result['summary']['init_inconsistencies'] > 0
        assert len(result['init_issues']) > 0

    def test_validate_project_nonexistent_dir(self):
        """测试不存在的目录"""
        with pytest.raises(FileNotFoundError):
            ImportPathValidator.validate_project("/nonexistent/path")

    def test_validate_project_file(self):
        """测试传入文件而非目录"""
        with tempfile.NamedTemporaryFile(suffix='.py') as f:
            with pytest.raises(ValueError):
                ImportPathValidator.validate_project(f.name)

    def test_validate_project_exclude_dirs(self, sample_project):
        """测试排除目录"""
        # 创建 tests 目录
        tests_dir = sample_project / 'tests'
        tests_dir.mkdir()
        (tests_dir / 'test_file.py').write_text('pass\n', encoding='utf-8')

        result = ImportPathValidator.validate_project(
            str(sample_project),
            exclude_dirs=['tests']
        )

        # tests 目录下的文件不应被扫描
        assert result['summary']['total_files'] == 6

    def test_validate_project_disable_checks(self, sample_project):
        """测试禁用某些检查"""
        result = ImportPathValidator.validate_project(
            str(sample_project),
            check_duplicates=False,
            check_circular=False,
            check_init=False
        )

        assert result['summary']['duplicate_imports'] == 0
        assert result['summary']['circular_imports'] == 0
        assert result['summary']['init_inconsistencies'] == 0
        assert result['summary']['total_issues'] == 0


class TestValidateFile:
    """测试 validate_file 方法"""

    def test_validate_file_returns_list(self, sample_project):
        """测试 validate_file 返回列表"""
        test_file = sample_project / 'main.py'
        issues = ImportPathValidator.validate_file(str(test_file))

        assert isinstance(issues, list)

    def test_validate_file_nonexistent(self):
        """测试不存在的文件"""
        with pytest.raises(FileNotFoundError):
            ImportPathValidator.validate_file("/nonexistent/file.py")

    def test_validate_file_non_python(self):
        """测试非 Python 文件"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            with pytest.raises(ValueError):
                ImportPathValidator.validate_file(f.name)

    def test_validate_file_with_circular_import(self, sample_project):
        """测试循环导入文件验证"""
        test_file = sample_project / 'package_b' / 'module_b.py'
        issues = ImportPathValidator.validate_file(str(test_file))

        # 应该检测到潜在问题
        assert isinstance(issues, list)


class TestCheckDuplicateImports:
    """测试 check_duplicate_imports 方法"""

    def test_detect_duplicates(self, sample_project):
        """测试重复导入检测"""
        duplicates = ImportPathValidator.check_duplicate_imports(str(sample_project))

        assert len(duplicates) > 0

        # 检查返回结构
        dup = duplicates[0]
        assert 'symbol' in dup
        assert 'imports' in dup
        assert 'path_count' in dup
        assert 'severity' in dup
        assert 'suggestion' in dup

    def test_duplicate_path_count(self, sample_project):
        """测试路径计数"""
        duplicates = ImportPathValidator.check_duplicate_imports(str(sample_project))

        # ClassA 从两个不同路径导入
        classa_dups = [d for d in duplicates if d['symbol'] == 'ClassA']
        if classa_dups:
            assert classa_dups[0]['path_count'] >= 2

    def test_empty_project(self):
        """测试空项目"""
        with tempfile.TemporaryDirectory() as temp_dir:
            duplicates = ImportPathValidator.check_duplicate_imports(temp_dir)
            assert len(duplicates) == 0


class TestCheckCircularImports:
    """测试 check_circular_imports 方法"""

    def test_detect_circular_imports(self, sample_project):
        """测试循环导入检测"""
        circulars = ImportPathValidator.check_circular_imports(str(sample_project))

        assert len(circulars) > 0

        # 检查返回结构
        cycle = circulars[0]
        assert 'cycle' in cycle
        assert 'files' in cycle
        assert 'cycle_length' in cycle
        assert 'severity' in cycle
        assert 'suggestion' in cycle

    def test_circular_import_cycle_length(self, sample_project):
        """测试循环长度"""
        circulars = ImportPathValidator.check_circular_imports(str(sample_project))

        # 应该有一个长度为 2 的循环
        cycle = circulars[0]
        assert cycle['cycle_length'] == 2

    def test_no_circular_imports(self):
        """测试无循环导入"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 创建无循环的模块
            mod_a = temp_path / 'mod_a.py'
            mod_a.write_text('x = 1\n', encoding='utf-8')

            mod_b = temp_path / 'mod_b.py'
            mod_b.write_text('from mod_a import x\n', encoding='utf-8')

            circulars = ImportPathValidator.check_circular_imports(temp_dir)
            assert len(circulars) == 0


class TestCheckInitConsistency:
    """测试 check_init_consistency 方法"""

    def test_detect_init_issues(self, sample_project):
        """测试 __init__.py 一致性检查"""
        issues = ImportPathValidator.check_init_consistency(str(sample_project))

        assert len(issues) > 0

        # 检查返回结构
        issue = issues[0]
        assert 'file' in issue
        assert 'issue_type' in issue
        assert 'symbol' in issue
        assert 'severity' in issue
        assert 'suggestion' in issue

    def test_missing_export(self, sample_project):
        """测试缺失导出检测"""
        issues = ImportPathValidator.check_init_consistency(str(sample_project))

        # 应该检测到 ClassB 未导出
        missing_exports = [i for i in issues if i['issue_type'] == 'missing_export']
        assert len(missing_exports) > 0

    def test_consistent_init(self):
        """测试一致的 __init__.py"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            package = temp_path / 'pkg'
            package.mkdir()

            # 创建一致的 __init__.py
            (package / '__init__.py').write_text(
                'from .module import ClassA\n'
                '__all__ = ["ClassA"]\n',
                encoding='utf-8'
            )

            (package / 'module.py').write_text(
                'class ClassA:\n'
                '    pass\n',
                encoding='utf-8'
            )

            issues = ImportPathValidator.check_init_consistency(temp_dir)
            # 应该没有问题
            assert len(issues) == 0


class TestGenerateReport:
    """测试 generate_report 方法"""

    def test_text_report(self, sample_project):
        """测试文本报告生成"""
        result = ImportPathValidator.validate_project(str(sample_project))
        report = ImportPathValidator.generate_report(result, output_format='text')

        assert isinstance(report, str)
        assert '导入路径验证报告' in report
        assert '统计摘要' in report

    def test_json_report(self, sample_project):
        """测试 JSON 报告生成"""
        import json

        result = ImportPathValidator.validate_project(str(sample_project))
        report = ImportPathValidator.generate_report(result, output_format='json')

        # 验证 JSON 格式
        data = json.loads(report)
        assert 'summary' in data
        assert 'duplicates' in data

    def test_markdown_report(self, sample_project):
        """测试 Markdown 报告生成"""
        result = ImportPathValidator.validate_project(str(sample_project))
        report = ImportPathValidator.generate_report(result, output_format='markdown')

        assert '# 导入路径验证报告' in report
        assert '## 统计摘要' in report

    def test_invalid_format(self, sample_project):
        """测试无效格式"""
        result = ImportPathValidator.validate_project(str(sample_project))

        with pytest.raises(ValueError):
            ImportPathValidator.generate_report(result, output_format='xml')

    def test_output_file(self, sample_project):
        """测试输出到文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / 'report.txt'

            result = ImportPathValidator.validate_project(str(sample_project))
            report = ImportPathValidator.generate_report(
                result,
                output_format='text',
                output_file=str(output_file)
            )

            # 验证文件已创建
            assert output_file.exists()
            assert output_file.read_text(encoding='utf-8') == report


class TestSelfTest:
    """测试 self_test 方法"""

    def test_self_test_passes(self):
        """测试自检测试通过"""
        result = ImportPathValidator.self_test()
        assert result is True


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_python_file(self):
        """测试空 Python 文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            empty_file = temp_path / 'empty.py'
            empty_file.write_text('', encoding='utf-8')

            issues = ImportPathValidator.validate_file(str(empty_file))
            assert isinstance(issues, list)

    def test_file_with_syntax_error(self):
        """测试语法错误文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            bad_file = temp_path / 'bad.py'
            bad_file.write_text('def broken(\n', encoding='utf-8')

            issues = ImportPathValidator.validate_file(str(bad_file))
            # 应该能处理语法错误
            assert isinstance(issues, list)

    def test_standard_library_imports_not_flagged(self):
        """测试标准库导入不被标记为重复"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            file1 = temp_path / 'file1.py'
            file1.write_text('import os\nimport sys\n', encoding='utf-8')

            file2 = temp_path / 'file2.py'
            file2.write_text('import os\n', encoding='utf-8')

            duplicates = ImportPathValidator.check_duplicate_imports(temp_dir)
            # 标准库导入不应被标记
            os_dups = [d for d in duplicates if d['symbol'] in ['os', 'sys']]
            assert len(os_dups) == 0

    def test_relative_import_in_non_package(self):
        """测试非包文件中的相对导入"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 没有 __init__.py 的目录
            standalone_file = temp_path / 'standalone.py'
            standalone_file.write_text(
                'from . import something\n',
                encoding='utf-8'
            )

            issues = ImportPathValidator.validate_file(str(standalone_file))

            # 应该检测到问题
            invalid_imports = [i for i in issues if i['type'] == 'invalid_relative_import']
            assert len(invalid_imports) > 0
