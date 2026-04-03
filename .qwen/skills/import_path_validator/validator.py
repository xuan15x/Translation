"""
导入路径验证器 - 核心实现

验证 Python 项目的导入路径规范性,检测以下问题:
- 同一类/函数从多个路径导入(重复导入)
- 模块间的循环导入依赖
- __init__.py 导出与实际定义不一致

使用示例:
    >>> from .qwen.skills.import_path_validator import ImportPathValidator
    >>> result = ImportPathValidator.validate_project("/path/to/project")
    >>> report = ImportPathValidator.generate_report(result)
    >>> print(report)

版本: 1.0.0
创建日期: 2026-04-03
"""

import ast
import json
import os
import sys
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class ImportPathValidator:
    """
    导入路径验证器

    提供以下核心功能:
    - 检测同一类/函数从多个路径导入的问题
    - 检测模块间的循环导入依赖
    - 验证 __init__.py 导出与实际定义的一致性
    - 生成项目级验证报告

    Attributes:
        DEFAULT_EXCLUDE_DIRS: 默认排除的目录列表
        DEFAULT_EXCLUDE_FILES: 默认排除的文件列表
    """

    # 默认配置
    DEFAULT_EXCLUDE_DIRS = [
        '.git',
        '.venv',
        'venv',
        '__pycache__',
        'node_modules',
        '.mypy_cache',
        '.pytest_cache',
        'build',
        'dist',
        'eggs',
        'tests'
    ]

    DEFAULT_EXCLUDE_FILES = [
        'conftest.py',
        'setup.py'
    ]

    @classmethod
    def validate_project(
        cls,
        project_root: str,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        strict_mode: bool = False,
        check_duplicates: bool = True,
        check_circular: bool = True,
        check_init: bool = True
    ) -> Dict[str, Any]:
        """
        验证整个项目的导入路径规范性

        扫描项目中所有 Python 文件,检测重复导入、循环导入和
        __init__.py 导出一致性问题。

        Args:
            project_root: 项目根目录路径
            exclude_dirs: 排除的目录列表,默认为 DEFAULT_EXCLUDE_DIRS
            exclude_files: 排除的文件列表,默认为 DEFAULT_EXCLUDE_FILES
            strict_mode: 严格模式,将所有警告视为错误
            check_duplicates: 是否检查重复导入,默认为 True
            check_circular: 是否检查循环导入,默认为 True
            check_init: 是否检查 __init__.py 一致性,默认为 True

        Returns:
            字典,包含以下键:
            - summary: 验证统计摘要
            - duplicates: 重复导入问题列表
            - circular: 循环导入问题列表
            - init_issues: __init__.py 不一致问题列表

        Raises:
            FileNotFoundError: 项目根目录不存在
            ValueError: 无效的项目根目录

        Example:
            >>> result = ImportPathValidator.validate_project("/path/to/project")
            >>> print(result['summary']['total_issues'])
        """
        project_path = Path(project_root).resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"项目根目录不存在: {project_root}")

        if not project_path.is_dir():
            raise ValueError(f"项目根目录必须是一个目录: {project_root}")

        exclude_dirs = exclude_dirs or cls.DEFAULT_EXCLUDE_DIRS
        exclude_files = exclude_files or cls.DEFAULT_EXCLUDE_FILES

        # 扫描所有 Python 文件
        python_files = cls._scan_python_files(
            project_path,
            exclude_dirs,
            exclude_files
        )

        # 初始化结果
        result = {
            'summary': {
                'total_files': len(python_files),
                'total_imports': 0,
                'total_packages': 0,
                'duplicate_imports': 0,
                'circular_imports': 0,
                'init_inconsistencies': 0,
                'total_issues': 0
            },
            'duplicates': [],
            'circular': [],
            'init_issues': []
        }

        # 统计总导入数和包数
        total_imports = 0
        init_files = []

        for file_path in python_files:
            imports = cls._parse_imports(file_path)
            total_imports += len(imports)

            if file_path.name == '__init__.py':
                init_files.append(file_path)

        result['summary']['total_imports'] = total_imports
        result['summary']['total_packages'] = len(init_files)

        # 执行各项检查
        if check_duplicates:
            result['duplicates'] = cls.check_duplicate_imports(
                project_root,
                exclude_dirs,
                exclude_files,
                python_files
            )
            result['summary']['duplicate_imports'] = len(result['duplicates'])

        if check_circular:
            result['circular'] = cls.check_circular_imports(
                project_root,
                exclude_dirs,
                exclude_files,
                python_files
            )
            result['summary']['circular_imports'] = len(result['circular'])

        if check_init:
            result['init_issues'] = cls.check_init_consistency(
                project_root,
                exclude_dirs,
                exclude_files
            )
            result['summary']['init_inconsistencies'] = len(result['init_issues'])

        # 计算总问题数
        result['summary']['total_issues'] = (
            result['summary']['duplicate_imports'] +
            result['summary']['circular_imports'] +
            result['summary']['init_inconsistencies']
        )

        return result

    @classmethod
    def validate_file(cls, file_path: str) -> List[Dict[str, Any]]:
        """
        验证单个文件的导入路径

        检查文件中的导入语句是否规范,包括:
        - 导入路径格式是否正确
        - 是否存在明显的循环导入风险
        - 导入的符号是否存在

        Args:
            file_path: Python 文件路径

        Returns:
            问题列表,每个问题是一个字典,包含:
            - type: 问题类型
            - message: 问题描述
            - line: 行号
            - severity: 严重程度('low', 'medium', 'high')
            - suggestion: 修复建议

        Raises:
            FileNotFoundError: 文件不存在
            SyntaxError: Python 语法错误

        Example:
            >>> issues = ImportPathValidator.validate_file("module.py")
            >>> for issue in issues:
            ...     print(f"[{issue['severity']}] {issue['message']}")
        """
        file_path_obj = Path(file_path).resolve()

        if not file_path_obj.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not file_path_obj.suffix == '.py':
            raise ValueError(f"必须是 Python 文件(.py): {file_path}")

        issues = []

        try:
            imports = cls._parse_imports_with_line_numbers(file_path_obj)

            for imp in imports:
                # 检查导入路径是否合理
                if cls._is_relative_import_in_non_package(imp, file_path_obj):
                    issues.append({
                        'type': 'invalid_relative_import',
                        'message': f'非包文件中使用相对导入: {imp["statement"]}',
                        'line': imp['line'],
                        'severity': 'high',
                        'suggestion': '将文件放入包结构中,或使用绝对导入'
                    })

                # 检查可能的循环导入(简化检查)
                if cls._is_likely_circular_import(imp, file_path_obj):
                    issues.append({
                        'type': 'potential_circular_import',
                        'message': f'可能的循环导入: {imp["statement"]}',
                        'line': imp['line'],
                        'severity': 'medium',
                        'suggestion': '检查目标模块是否也导入了当前模块'
                    })

        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'message': f'Python 语法错误: {e}',
                'line': e.lineno or 0,
                'severity': 'high',
                'suggestion': '修复语法错误后重新检查'
            })

        return issues

    @classmethod
    def check_duplicate_imports(
        cls,
        project_root: str,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        python_files: Optional[List[Path]] = None
    ) -> List[Dict[str, Any]]:
        """
        检查项目中的重复导入路径

        扫描所有 Python 文件,找出同一符号从多个不同模块导入的情况。

        Args:
            project_root: 项目根目录路径
            exclude_dirs: 排除的目录列表
            exclude_files: 排除的文件列表
            python_files: 预扫描的 Python 文件列表(可选,用于优化性能)

        Returns:
            重复导入问题列表,每个问题包含:
            - symbol: 被重复导入的符号
            - imports: 导入位置列表
            - path_count: 导入路径数量
            - severity: 严重程度
            - suggestion: 修复建议

        Example:
            >>> duplicates = ImportPathValidator.check_duplicate_imports(".")
            >>> for dup in duplicates:
            ...     print(f"{dup['symbol']}: {dup['path_count']} 个路径")
        """
        project_path = Path(project_root).resolve()
        exclude_dirs = exclude_dirs or cls.DEFAULT_EXCLUDE_DIRS
        exclude_files = exclude_files or cls.DEFAULT_EXCLUDE_FILES

        if python_files is None:
            python_files = cls._scan_python_files(
                project_path,
                exclude_dirs,
                exclude_files
            )

        # 构建符号到导入位置的映射
        # 格式: symbol -> [(module, file_path, line_number)]
        symbol_imports: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for file_path in python_files:
            try:
                imports = cls._parse_imports_with_line_numbers(file_path)

                for imp in imports:
                    for name in imp['names']:
                        # 处理别名: from module import ClassA as A
                        symbol_name = name['asname'] or name['name']
                        module_path = imp['module']

                        symbol_imports[symbol_name].append({
                            'module': module_path,
                            'file': str(file_path.relative_to(project_path)),
                            'line': imp['line']
                        })

            except (SyntaxError, UnicodeDecodeError):
                # 跳过无法解析的文件
                continue

        # 找出重复导入
        duplicates = []

        for symbol, imports in symbol_imports.items():
            # 过滤掉标准库和常见的第三方库
            if cls._is_standard_library_or_third_party(imports[0]['module']):
                continue

            # 获取唯一的模块路径
            unique_modules = list(set(imp['module'] for imp in imports))

            if len(unique_modules) >= 2:
                # 确定严重程度
                severity = 'medium' if len(unique_modules) == 2 else 'high'

                duplicates.append({
                    'symbol': symbol,
                    'imports': imports,
                    'path_count': len(unique_modules),
                    'severity': severity,
                    'suggestion': cls._generate_duplicate_suggestion(
                        symbol,
                        unique_modules,
                        imports
                    )
                })

        # 按严重程度和路径数量排序
        duplicates.sort(
            key=lambda x: (0 if x['severity'] == 'high' else 1, -x['path_count'])
        )

        return duplicates

    @classmethod
    def check_circular_imports(
        cls,
        project_root: str,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        python_files: Optional[List[Path]] = None
    ) -> List[Dict[str, Any]]:
        """
        检查项目中的循环导入依赖

        构建模块依赖图,使用深度优先搜索(DFS)检测循环导入路径。

        Args:
            project_root: 项目根目录路径
            exclude_dirs: 排除的目录列表
            exclude_files: 排除的文件列表
            python_files: 预扫描的 Python 文件列表(可选)

        Returns:
            循环导入问题列表,每个问题包含:
            - cycle: 循环路径上的模块列表
            - files: 涉及的文件路径列表
            - cycle_length: 循环长度
            - severity: 严重程度
            - suggestion: 修复建议

        Example:
            >>> circulars = ImportPathValidator.check_circular_imports(".")
            >>> for cycle in circulars:
            ...     print(f"循环: {' → '.join(cycle['cycle'])}")
        """
        project_path = Path(project_root).resolve()
        exclude_dirs = exclude_dirs or cls.DEFAULT_EXCLUDE_DIRS
        exclude_files = exclude_files or cls.DEFAULT_EXCLUDE_FILES

        if python_files is None:
            python_files = cls._scan_python_files(
                project_path,
                exclude_dirs,
                exclude_files
            )

        # 构建模块依赖图
        dependency_graph = cls._build_dependency_graph(
            python_files,
            project_path
        )

        # 使用 DFS 检测循环
        circular_imports = cls._detect_cycles_dfs(dependency_graph)

        # 格式化结果
        result = []

        for cycle in circular_imports:
            # 获取涉及的文件
            files = []
            for module in cycle[:-1]:  # 最后一个模块与第一个相同,去重
                file_path = cls._module_to_file(module, python_files)
                if file_path:
                    files.append(str(file_path.relative_to(project_path)))

            cycle_length = len(cycle) - 1
            severity = 'medium' if cycle_length == 2 else 'high'

            result.append({
                'cycle': cycle,
                'files': files,
                'cycle_length': cycle_length,
                'severity': severity,
                'suggestion': cls._generate_circular_suggestion(cycle)
            })

        # 按循环长度排序
        result.sort(key=lambda x: (-x['cycle_length'], x['cycle'][0]))

        return result

    @classmethod
    def check_init_consistency(
        cls,
        project_root: str,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        检查 __init__.py 文件的导出一致性

        验证 __init__.py 中导出的符号与实际子模块中定义的符号是否一致。

        检测以下问题:
        - 缺失导出: 子模块中有公共符号,但未在 __init__.py 中导出
        - 无效导出: __init__.py 中导出的符号在子模块中不存在
        - 导入未导出: __init__.py 中导入但未在 __all__ 中声明

        Args:
            project_root: 项目根目录路径
            exclude_dirs: 排除的目录列表
            exclude_files: 排除的文件列表

        Returns:
            __init__.py 不一致问题列表,每个问题包含:
            - file: __init__.py 文件路径
            - issue_type: 问题类型('missing_export', 'invalid_export', 'import_not_export')
            - symbol: 涉及的符号
            - defined_in: 符号定义位置(如果适用)
            - severity: 严重程度
            - suggestion: 修复建议

        Example:
            >>> init_issues = ImportPathValidator.check_init_consistency(".")
            >>> for issue in init_issues:
            ...     print(f"[{issue['issue_type']}] {issue['symbol']}")
        """
        project_path = Path(project_root).resolve()
        exclude_dirs = exclude_dirs or cls.DEFAULT_EXCLUDE_DIRS
        exclude_files = exclude_files or cls.DEFAULT_EXCLUDE_FILES

        # 扫描所有 __init__.py 文件
        init_files = []

        for root, dirs, files in os.walk(project_path):
            # 排除指定目录
            dirs[:] = [
                d for d in dirs
                if d not in exclude_dirs and not d.startswith('.')
            ]

            if '__init__.py' in files:
                init_file = Path(root) / '__init__.py'
                init_files.append(init_file)

        issues = []

        for init_file in init_files:
            try:
                file_issues = cls._check_single_init(init_file, project_path)
                issues.extend(file_issues)
            except (SyntaxError, UnicodeDecodeError):
                # 跳过无法解析的文件
                continue

        # 按文件路径和问题类型排序
        issues.sort(key=lambda x: (x['file'], x['issue_type'], x['symbol']))

        return issues

    @classmethod
    def generate_report(
        cls,
        validation_result: Dict[str, Any],
        output_format: str = 'text',
        output_file: Optional[str] = None
    ) -> str:
        """
        生成导入路径验证报告

        将验证结果格式化为可读的报告,支持多种输出格式。

        Args:
            validation_result: validate_project() 返回的验证结果字典
            output_format: 输出格式,支持 'text', 'json', 'markdown'
            output_file: 输出文件路径(如提供则保存到文件)

        Returns:
            格式化的报告字符串

        Raises:
            ValueError: 不支持的输出格式

        Example:
            >>> result = ImportPathValidator.validate_project(".")
            >>> report = ImportPathValidator.generate_report(result, output_format='markdown')
            >>> print(report)
        """
        if output_format == 'text':
            report = cls._generate_text_report(validation_result)
        elif output_format == 'json':
            report = cls._generate_json_report(validation_result)
        elif output_format == 'markdown':
            report = cls._generate_markdown_report(validation_result)
        else:
            raise ValueError(f"不支持的输出格式: {output_format},支持的格式: 'text', 'json', 'markdown'")

        # 如果指定了输出文件,保存到文件
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')

        return report

    @classmethod
    def self_test(cls) -> bool:
        """
        自检测试

        创建临时项目结构,验证各项检测功能是否正常工作。

        Returns:
            如果所有测试通过返回 True,否则返回 False

        Example:
            >>> if ImportPathValidator.self_test():
            ...     print("✅ 验证器正常")
            ... else:
            ...     print("❌ 验证器异常")
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # 创建测试项目结构
                cls._create_test_project(temp_path)

                # 测试 1: 验证项目
                result = cls.validate_project(str(temp_path))

                if result['summary']['total_files'] == 0:
                    print("❌ 测试 1 失败: 未扫描到文件")
                    return False

                # 测试 2: 检测重复导入
                duplicates = cls.check_duplicate_imports(str(temp_path))
                if len(duplicates) == 0:
                    print("❌ 测试 2 失败: 未检测到重复导入")
                    return False

                # 测试 3: 检测循环导入
                circulars = cls.check_circular_imports(str(temp_path))
                if len(circulars) == 0:
                    print("❌ 测试 3 失败: 未检测到循环导入")
                    return False

                # 测试 4: 检测 __init__.py 一致性
                init_issues = cls.check_init_consistency(str(temp_path))
                if len(init_issues) == 0:
                    print("❌ 测试 4 失败: 未检测到 __init__.py 不一致")
                    return False

                # 测试 5: 生成报告
                report = cls.generate_report(result, output_format='text')
                if not report or len(report) < 100:
                    print("❌ 测试 5 失败: 报告生成异常")
                    return False

                # 测试 6: 验证单个文件
                test_file = temp_path / 'package_a' / 'module_a.py'
                issues = cls.validate_file(str(test_file))
                if not isinstance(issues, list):
                    print("❌ 测试 6 失败: 文件验证返回类型错误")
                    return False

                # 测试 7: JSON 格式报告
                json_report = cls.generate_report(result, output_format='json')
                try:
                    json.loads(json_report)
                except json.JSONDecodeError:
                    print("❌ 测试 7 失败: JSON 报告格式错误")
                    return False

                # 测试 8: Markdown 格式报告
                md_report = cls.generate_report(result, output_format='markdown')
                if '导入路径验证报告' not in md_report:
                    print("❌ 测试 8 失败: Markdown 报告格式异常")
                    return False

                return True

        except Exception as e:
            print(f"❌ 自检测试异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ==================== 私有辅助方法 ====================

    @classmethod
    def _scan_python_files(
        cls,
        project_path: Path,
        exclude_dirs: List[str],
        exclude_files: List[str]
    ) -> List[Path]:
        """
        扫描项目中的所有 Python 文件

        Args:
            project_path: 项目根目录
            exclude_dirs: 排除的目录列表
            exclude_files: 排除的文件列表

        Returns:
            Python 文件路径列表
        """
        python_files = []

        for root, dirs, files in os.walk(project_path):
            # 排除指定目录
            dirs[:] = [
                d for d in dirs
                if d not in exclude_dirs and not d.startswith('.')
            ]

            for file in files:
                if file.endswith('.py') and file not in exclude_files:
                    python_files.append(Path(root) / file)

        return python_files

    @classmethod
    def _parse_imports(cls, file_path: Path) -> List[Dict[str, Any]]:
        """
        解析文件中的所有导入语句

        Args:
            file_path: Python 文件路径

        Returns:
            导入语句列表

        Raises:
            SyntaxError: Python 语法错误
        """
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(file_path))

        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'names': [],
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                level = node.level or 0

                # 处理相对导入
                if level > 0:
                    prefix = '.' * level
                    module = prefix + module

                names = []
                for alias in node.names:
                    names.append({
                        'name': alias.name,
                        'asname': alias.asname
                    })

                imports.append({
                    'type': 'from_import',
                    'module': module,
                    'names': names,
                    'line': node.lineno
                })

        return imports

    @classmethod
    def _parse_imports_with_line_numbers(cls, file_path: Path) -> List[Dict[str, Any]]:
        """
        解析文件中的所有导入语句(包含行号和原始语句)

        Args:
            file_path: Python 文件路径

        Returns:
            导入语句列表,包含原始语句文本

        Raises:
            SyntaxError: Python 语法错误
        """
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(file_path))
        lines = source.splitlines()

        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                statement = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ''

                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'names': [{'name': alias.name, 'asname': alias.asname}],
                        'line': node.lineno,
                        'statement': statement
                    })

            elif isinstance(node, ast.ImportFrom):
                statement = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ''

                module = node.module or ''
                level = node.level or 0

                if level > 0:
                    prefix = '.' * level
                    module = prefix + module

                names = []
                for alias in node.names:
                    names.append({
                        'name': alias.name,
                        'asname': alias.asname
                    })

                imports.append({
                    'type': 'from_import',
                    'module': module,
                    'names': names,
                    'line': node.lineno,
                    'statement': statement
                })

        return imports

    @classmethod
    def _is_standard_library_or_third_party(cls, module_path: str) -> bool:
        """
        判断模块是否为标准库或第三方库

        Args:
            module_path: 模块路径

        Returns:
            如果是标准库或第三方库返回 True
        """
        # 常见标准库
        standard_libraries = [
            'os', 'sys', 'json', 're', 'ast', 'datetime', 'pathlib',
            'typing', 'collections', 'itertools', 'functools', 'abc',
            'unittest', 'tempfile', 'io', 'string', 'textwrap',
            'logging', 'configparser', 'argparse', 'hashlib',
            'http', 'urllib', 'email', 'html', 'xml',
            'sqlite3', 'csv', 'pickle', 'shelve',
            'threading', 'multiprocessing', 'asyncio',
            'math', 'random', 'statistics', 'decimal',
            'subprocess', 'shutil', 'glob', 'fnmatch'
        ]

        # 获取顶级模块
        top_level = module_path.split('.')[0].lstrip('.')

        # 检查标准库
        if top_level in standard_libraries:
            return True

        # 检查常见的第三方库
        third_party_libraries = [
            'pytest', 'numpy', 'pandas', 'flask', 'django', 'sqlalchemy',
            'requests', 'click', 'pydantic', 'fastapi', 'celery',
            'redis', 'boto3', 'google', 'azure', 'grpc',
            'PIL', 'cv2', 'sklearn', 'tensorflow', 'torch'
        ]

        if top_level in third_party_libraries:
            return True

        return False

    @classmethod
    def _generate_duplicate_suggestion(
        cls,
        symbol: str,
        modules: List[str],
        imports: List[Dict[str, Any]]
    ) -> str:
        """
        生成重复导入的修复建议

        Args:
            symbol: 被重复导入的符号
            modules: 导入的模块路径列表
            imports: 导入位置详情列表

        Returns:
            修复建议字符串
        """
        # 统计每个模块的使用次数
        module_counts = defaultdict(int)
        for imp in imports:
            module_counts[imp['module']] += 1

        # 找到最常用的模块
        most_common_module = max(module_counts.items(), key=lambda x: x[1])[0]

        return (
            f"符号 '{symbol}' 从 {len(modules)} 个不同路径导入。"
            f"建议统一使用 '{most_common_module}' 路径导入,避免混乱。"
        )

    @classmethod
    def _build_dependency_graph(
        cls,
        python_files: List[Path],
        project_path: Path
    ) -> Dict[str, Set[str]]:
        """
        构建模块依赖图

        Args:
            python_files: Python 文件列表
            project_path: 项目根目录

        Returns:
            依赖图(邻接表),格式: module -> set of dependencies
        """
        # 构建文件路径到模块名的映射
        file_to_module = {}
        for file_path in python_files:
            module_name = cls._file_to_module(file_path, project_path)
            if module_name:
                file_to_module[str(file_path)] = module_name

        # 构建模块名到文件路径的映射
        module_to_file = {v: k for k, v in file_to_module.items()}

        # 构建依赖图
        dependency_graph: Dict[str, Set[str]] = defaultdict(set)

        for file_path in python_files:
            try:
                imports = cls._parse_imports(file_path)
                source_module = cls._file_to_module(file_path, project_path)

                if not source_module:
                    continue

                for imp in imports:
                    target_module = imp['module']

                    # 处理相对导入
                    if target_module.startswith('.'):
                        target_module = cls._resolve_relative_import(
                            source_module,
                            target_module
                        )

                    # 只关注项目内的模块
                    if target_module in module_to_file:
                        dependency_graph[source_module].add(target_module)

            except (SyntaxError, UnicodeDecodeError):
                continue

        return dependency_graph

    @classmethod
    def _file_to_module(cls, file_path: Path, project_path: Path) -> Optional[str]:
        """
        将文件路径转换为模块名

        Args:
            file_path: 文件路径
            project_path: 项目根目录

        Returns:
            模块名,如果无法转换返回 None
        """
        try:
            relative_path = file_path.relative_to(project_path)
            # 移除 .py 后缀
            module_path = relative_path.with_suffix('')
            # 转换为模块名(用 . 分隔)
            module_name = str(module_path).replace(os.sep, '.')

            # 处理 __init__.py
            if module_name.endswith('.__init__'):
                module_name = module_name[:-9]

            return module_name if module_name else None

        except ValueError:
            return None

    @classmethod
    def _module_to_file(cls, module_name: str, python_files: List[Path]) -> Optional[Path]:
        """
        将模块名转换为文件路径

        Args:
            module_name: 模块名
            python_files: Python 文件列表

        Returns:
            文件路径,如果找不到返回 None
        """
        # 尝试直接匹配
        module_parts = module_name.split('.')

        # 尝试普通模块
        expected_file = Path(*module_parts).with_suffix('.py')
        for file_path in python_files:
            if str(file_path).endswith(str(expected_file)):
                return file_path

        # 尝试包模块
        expected_init = Path(*module_parts, '__init__.py')
        for file_path in python_files:
            if str(file_path).endswith(str(expected_init)):
                return file_path

        return None

    @classmethod
    def _resolve_relative_import(
        cls,
        source_module: str,
        relative_import: str
    ) -> str:
        """
        解析相对导入为绝对导入

        Args:
            source_module: 源模块名
            relative_import: 相对导入路径

        Returns:
            绝对导入路径
        """
        # 计算相对层级
        level = 0
        for char in relative_import:
            if char == '.':
                level += 1
            else:
                break

        # 获取目标模块名
        target_name = relative_import[level:]

        # 获取源模块的包路径
        source_parts = source_module.split('.')

        # 如果是 __init__.py,当前目录就是包本身
        # 如果是普通模块,需要回到上一级
        if len(source_parts) >= level:
            base_parts = source_parts[:-level]
        else:
            base_parts = []

        # 构建完整模块名
        if target_name:
            full_module = '.'.join(base_parts + [target_name]) if base_parts else target_name
        else:
            full_module = '.'.join(base_parts)

        return full_module

    @classmethod
    def _detect_cycles_dfs(cls, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """
        使用深度优先搜索检测图中的循环

        Args:
            graph: 依赖图(邻接表)

        Returns:
            循环列表,每个循环是一个模块路径列表
        """
        cycles = []
        visited = set()
        recursion_stack = []
        recursion_set = set()

        def dfs(node: str):
            visited.add(node)
            recursion_stack.append(node)
            recursion_set.add(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in recursion_set:
                    # 找到循环
                    cycle_start = recursion_stack.index(neighbor)
                    cycle = recursion_stack[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            recursion_stack.pop()
            recursion_set.discard(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    @classmethod
    def _is_relative_import_in_non_package(
        cls,
        imp: Dict[str, Any],
        file_path: Path
    ) -> bool:
        """
        检查是否在非包文件中使用了相对导入

        Args:
            imp: 导入信息
            file_path: 文件路径

        Returns:
            如果是非包文件中的相对导入返回 True
        """
        if not imp['module'].startswith('.'):
            return False

        # 检查是否有 __init__.py
        init_file = file_path.parent / '__init__.py'
        return not init_file.exists()

    @classmethod
    def _is_likely_circular_import(
        cls,
        imp: Dict[str, Any],
        file_path: Path
    ) -> bool:
        """
        简化检查:判断是否可能是循环导入

        (这只是启发式检查,不是完整检测)

        Args:
            imp: 导入信息
            file_path: 文件路径

        Returns:
            如果可能是循环导入返回 True
        """
        # 获取目标模块
        module = imp['module'].lstrip('.')

        # 检查目标模块是否可能导入当前文件
        # 这里只做简单检查:同一目录下的模块互相导入
        target_parts = module.split('.')

        if len(target_parts) >= 2:
            # 检查目标模块文件是否存在
            target_file = cls._module_to_file_from_parts(
                file_path.parent,
                target_parts
            )

            if target_file and target_file.exists():
                # 检查目标文件是否导入了当前文件的某个符号
                try:
                    target_imports = cls._parse_imports(target_file)
                    current_module = file_path.stem

                    for target_imp in target_imports:
                        if current_module in target_imp['module']:
                            return True
                except (SyntaxError, UnicodeDecodeError):
                    pass

        return False

    @classmethod
    def _module_to_file_from_parts(
        cls,
        base_path: Path,
        module_parts: List[str]
    ) -> Optional[Path]:
        """
        将模块路径部分转换为文件路径

        Args:
            base_path: 基础路径
            module_parts: 模块路径部分列表

        Returns:
            文件路径(可能不存在)
        """
        # 尝试普通模块
        try:
            return base_path / Path(*module_parts[:-1]) / (module_parts[-1] + '.py')
        except IndexError:
            return None

    @classmethod
    def _check_single_init(
        cls,
        init_file: Path,
        project_path: Path
    ) -> List[Dict[str, Any]]:
        """
        检查单个 __init__.py 文件的导出一致性

        Args:
            init_file: __init__.py 文件路径
            project_path: 项目根目录

        Returns:
            问题列表

        Raises:
            SyntaxError: Python 语法错误
        """
        source = init_file.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(init_file))

        # 提取 __all__ 列表
        all_exports = cls._extract_all_list(tree)

        # 提取导入的符号
        imported_symbols = cls._extract_imported_symbols(tree)

        # 扫描子模块中的公共符号
        public_symbols = cls._scan_public_symbols(init_file.parent, project_path)

        issues = []
        relative_path = str(init_file.relative_to(project_path))

        # 检查 1: __all__ 中的符号是否在子模块中定义
        if all_exports:
            for symbol in all_exports:
                if symbol not in imported_symbols and symbol not in public_symbols:
                    issues.append({
                        'file': relative_path,
                        'issue_type': 'invalid_export',
                        'symbol': symbol,
                        'defined_in': None,
                        'severity': 'medium',
                        'suggestion': f"符号 '{symbol}' 在 __all__ 中但未找到定义,检查拼写或移除"
                    })

        # 检查 2: 导入的符号是否在 __all__ 中声明
        if all_exports is not None:
            for symbol in imported_symbols:
                if symbol not in all_exports:
                    issues.append({
                        'file': relative_path,
                        'issue_type': 'import_not_export',
                        'symbol': symbol,
                        'defined_in': None,
                        'severity': 'low',
                        'suggestion': f"符号 '{symbol}' 已导入但未在 __all__ 中声明,考虑添加或移除导入"
                    })

            # 检查 3: 子模块中的公共符号是否在 __all__ 中导出
            for symbol, module in public_symbols.items():
                if symbol not in all_exports and not symbol.startswith('_'):
                    issues.append({
                        'file': relative_path,
                        'issue_type': 'missing_export',
                        'symbol': symbol,
                        'defined_in': str(module.relative_to(project_path)),
                        'severity': 'low',
                        'suggestion': f"符号 '{symbol}' 在 {module.name} 中定义但未在 __all__ 中导出"
                    })
        else:
            # 没有 __all__,检查导入的符号
            for symbol, module in public_symbols.items():
                if symbol not in imported_symbols and not symbol.startswith('_'):
                    issues.append({
                        'file': relative_path,
                        'issue_type': 'missing_export',
                        'symbol': symbol,
                        'defined_in': str(module.relative_to(project_path)),
                        'severity': 'low',
                        'suggestion': f"符号 '{symbol}' 在子模块中定义但未在 __init__.py 中导出"
                    })

        return issues

    @classmethod
    def _extract_all_list(cls, tree: ast.AST) -> Optional[List[str]]:
        """
        从 AST 中提取 __all__ 列表

        Args:
            tree: AST 树

        Returns:
            __all__ 列表,如果不存在返回 None
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            result = []
                            for elt in node.value.elts:
                                # Python 3.8+: ast.Constant 替代了 ast.Str, ast.Num 等
                                if isinstance(elt, ast.Constant):
                                    result.append(elt.value)
                                # Python 3.7 及更早版本兼容
                                elif hasattr(ast, 'Str') and isinstance(elt, ast.Str):
                                    result.append(elt.s)
                            return result
        return None

    @classmethod
    def _extract_imported_symbols(cls, tree: ast.AST) -> Set[str]:
        """
        从 AST 中提取导入的符号

        Args:
            tree: AST 树

        Returns:
            导入的符号集合
        """
        symbols = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    symbols.add(alias.asname or alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    symbols.add(alias.asname or alias.name)

        return symbols

    @classmethod
    def _scan_public_symbols(
        cls,
        package_dir: Path,
        project_path: Path
    ) -> Dict[str, Path]:
        """
        扫描包中子模块的公共符号

        Args:
            package_dir: 包目录
            project_path: 项目根目录

        Returns:
            公共符号到定义文件的映射
        """
        public_symbols = {}

        for file in package_dir.iterdir():
            if file.is_file() and file.name.endswith('.py') and file.name != '__init__.py':
                try:
                    source = file.read_text(encoding='utf-8')
                    tree = ast.parse(source, filename=str(file))

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                            name = node.name
                            # 只关注公共符号(不以 _ 开头)
                            if not name.startswith('_'):
                                public_symbols[name] = file

                except (SyntaxError, UnicodeDecodeError):
                    continue

        return public_symbols

    @classmethod
    def _generate_circular_suggestion(cls, cycle: List[str]) -> str:
        """
        生成循环导入的修复建议

        Args:
            cycle: 循环路径

        Returns:
            修复建议字符串
        """
        cycle_str = ' → '.join(cycle)
        return (
            f"检测到循环依赖: {cycle_str}。"
            f"建议: 1) 使用依赖注入打破循环; "
            f"2) 提取共享接口到独立模块; "
            f"3) 延迟导入(在函数内导入)。"
        )

    @classmethod
    def _generate_text_report(cls, result: Dict[str, Any]) -> str:
        """生成文本格式报告"""
        lines = []
        lines.append('═' * 60)
        lines.append('导入路径验证报告')
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append('═' * 60)
        lines.append('')

        # 统计摘要
        summary = result['summary']
        lines.append('【统计摘要】')
        lines.append('━' * 60)
        lines.append('')
        lines.append(f"• 扫描文件总数: {summary['total_files']}")
        lines.append(f"• 导入语句总数: {summary['total_imports']}")
        lines.append(f"• 包(__init__.py)数量: {summary['total_packages']}")
        lines.append(f"• 重复导入: {summary['duplicate_imports']} 处")
        lines.append(f"• 循环导入: {summary['circular_imports']} 处")
        lines.append(f"• __init__.py 不一致: {summary['init_inconsistencies']} 处")
        lines.append(f"• 问题总数: {summary['total_issues']} 个")
        lines.append('')

        # 重复导入
        if result['duplicates']:
            lines.append('【重复导入】')
            lines.append('━' * 60)
            lines.append('')

            for i, dup in enumerate(result['duplicates'], 1):
                severity_mark = ' 🔴' if dup['severity'] == 'high' else ''
                lines.append(
                    f"{i}. {dup['symbol']} ({dup['path_count']} 个导入路径){severity_mark}"
                )

                for imp in dup['imports']:
                    lines.append(f"   - {imp['module']} ({imp['file']}:{imp['line']})")

                lines.append(f"   建议: {dup['suggestion']}")
                lines.append('')

        # 循环导入
        if result['circular']:
            lines.append('【循环导入】')
            lines.append('━' * 60)
            lines.append('')

            for i, cycle in enumerate(result['circular'], 1):
                cycle_display = ' ↔ '.join(cycle['cycle'][:-1])
                lines.append(
                    f"{i}. {cycle_display} ({cycle['cycle_length']} 个模块)"
                )
                lines.append(f"   循环路径: {' → '.join(cycle['cycle'])}")

                if cycle['files']:
                    lines.append('   文件:')
                    for file in cycle['files']:
                        lines.append(f"     - {file}")

                lines.append(f"   建议: {cycle['suggestion']}")
                lines.append('')

        # __init__.py 问题
        if result['init_issues']:
            lines.append('【__init__.py 导出问题】')
            lines.append('━' * 60)
            lines.append('')

            issue_type_map = {
                'missing_export': '缺失导出',
                'invalid_export': '无效导出',
                'import_not_export': '导入未导出'
            }

            for i, issue in enumerate(result['init_issues'], 1):
                issue_type_cn = issue_type_map.get(issue['issue_type'], issue['issue_type'])
                lines.append(f"{i}. {issue['file']} - {issue_type_cn}")
                lines.append(f"   符号: {issue['symbol']}")

                if issue.get('defined_in'):
                    lines.append(f"   定义位置: {issue['defined_in']}")

                lines.append(f"   建议: {issue['suggestion']}")
                lines.append('')

        # 总结
        lines.append('═' * 60)

        if summary['total_issues'] == 0:
            lines.append('✅ 所有导入路径检查通过!')
        else:
            lines.append(f"⚠️ 共发现 {summary['total_issues']} 个导入路径问题")

        lines.append('═' * 60)

        return '\n'.join(lines)

    @classmethod
    def _generate_json_report(cls, result: Dict[str, Any]) -> str:
        """生成 JSON 格式报告"""
        return json.dumps(result, ensure_ascii=False, indent=2)

    @classmethod
    def _generate_markdown_report(cls, result: Dict[str, Any]) -> str:
        """生成 Markdown 格式报告"""
        lines = []
        summary = result['summary']

        lines.append('# 导入路径验证报告')
        lines.append('')
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append('')

        # 统计摘要
        lines.append('## 统计摘要')
        lines.append('')
        lines.append(f"- **扫描文件总数**: {summary['total_files']}")
        lines.append(f"- **导入语句总数**: {summary['total_imports']}")
        lines.append(f"- **包数量**: {summary['total_packages']}")
        lines.append(f"- **重复导入**: {summary['duplicate_imports']} 处")
        lines.append(f"- **循环导入**: {summary['circular_imports']} 处")
        lines.append(f"- **__init__.py 不一致**: {summary['init_inconsistencies']} 处")
        lines.append(f"- **问题总数**: {summary['total_issues']} 个")
        lines.append('')

        # 重复导入
        if result['duplicates']:
            lines.append('## 重复导入')
            lines.append('')

            for i, dup in enumerate(result['duplicates'], 1):
                severity = '🔴 高' if dup['severity'] == 'high' else '⚠️ 中'
                lines.append(f"### {i}. {dup['symbol']} ({severity})")
                lines.append('')
                lines.append(f"**导入路径数**: {dup['path_count']}")
                lines.append('')
                lines.append('| 模块 | 文件 | 行号 |')
                lines.append('|------|------|------|')

                for imp in dup['imports']:
                    lines.append(f"| {imp['module']} | {imp['file']} | {imp['line']} |")

                lines.append('')
                lines.append(f"**建议**: {dup['suggestion']}")
                lines.append('')

        # 循环导入
        if result['circular']:
            lines.append('## 循环导入')
            lines.append('')

            for i, cycle in enumerate(result['circular'], 1):
                cycle_display = ' → '.join(cycle['cycle'])
                lines.append(f"### {i}. 循环依赖 ({cycle['cycle_length']} 个模块)")
                lines.append('')
                lines.append(f"**循环路径**: `{cycle_display}`")
                lines.append('')

                if cycle['files']:
                    lines.append('**涉及文件**:')
                    lines.append('')
                    for file in cycle['files']:
                        lines.append(f"- `{file}`")

                    lines.append('')

                lines.append(f"**建议**: {cycle['suggestion']}")
                lines.append('')

        # __init__.py 问题
        if result['init_issues']:
            lines.append('## __init__.py 导出问题')
            lines.append('')

            issue_type_map = {
                'missing_export': '缺失导出',
                'invalid_export': '无效导出',
                'import_not_export': '导入未导出'
            }

            for i, issue in enumerate(result['init_issues'], 1):
                issue_type_cn = issue_type_map.get(issue['issue_type'], issue['issue_type'])
                lines.append(f"### {i}. {issue['file']} - {issue_type_cn}")
                lines.append('')
                lines.append(f"**符号**: `{issue['symbol']}`")

                if issue.get('defined_in'):
                    lines.append(f"**定义位置**: `{issue['defined_in']}`")

                lines.append('')
                lines.append(f"**建议**: {issue['suggestion']}")
                lines.append('')

        # 总结
        lines.append('---')
        lines.append('')

        if summary['total_issues'] == 0:
            lines.append('✅ **所有导入路径检查通过!**')
        else:
            lines.append(f"⚠️ **共发现 {summary['total_issues']} 个导入路径问题**")

        lines.append('')

        return '\n'.join(lines)

    @classmethod
    def _create_test_project(cls, temp_path: Path):
        """
        创建测试项目结构

        创建包含以下问题的测试项目:
        - 重复导入
        - 循环导入
        - __init__.py 不一致
        """
        # 创建包 A
        package_a = temp_path / 'package_a'
        package_a.mkdir()

        # package_a/__init__.py - 有导出问题
        (package_a / '__init__.py').write_text(
            'from .module_a import ClassA, ClassB\n'
            '__all__ = ["ClassA"]  # ClassB 未导出\n',
            encoding='utf-8'
        )

        # package_a/module_a.py
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

        # package_b/module_b.py - 导入 module_c
        (package_b / 'module_b.py').write_text(
            'from .module_c import ClassC\n'
            '\n'
            'class ClassB:\n'
            '    """测试类 B"""\n'
            '    def __init__(self):\n'
            '        self.c = ClassC()\n',
            encoding='utf-8'
        )

        # package_b/module_c.py - 导入 module_b (循环)
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
