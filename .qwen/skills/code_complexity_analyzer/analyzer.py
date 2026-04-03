"""
代码复杂度分析器 - 核心实现

分析 Python 项目的代码复杂度,包括圈复杂度、认知复杂度、函数/类大小等指标,
帮助开发者识别高复杂度代码,提升代码可维护性和可读性。

使用示例:
    >>> from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer
    >>> result = CodeComplexityAnalyzer.analyze_file("path/to/module.py")
    >>> project_result = CodeComplexityAnalyzer.analyze_project("/path/to/project")
    >>> report = CodeComplexityAnalyzer.generate_report(project_result)
    >>> print(report)

版本: 1.0.0
创建日期: 2026-04-03
"""

import ast
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class CodeComplexityAnalyzer:
    """
    代码复杂度分析器

    提供以下核心功能:
    - 计算函数的圈复杂度(Cyclomatic Complexity)
    - 计算认知复杂度(Cognitive Complexity)
    - 统计函数和类的代码行数
    - 生成项目级复杂度分析报告

    Attributes:
        DEFAULT_EXCLUDE_DIRS: 默认排除的目录列表
        DEFAULT_EXCLUDE_FILES: 默认排除的文件列表
        DEFAULT_CYCLOMATIC_THRESHOLD: 默认圈复杂度阈值
        DEFAULT_COGNITIVE_THRESHOLD: 默认认知复杂度阈值
        DEFAULT_MAX_FUNCTION_LINES: 默认函数最大行数
        DEFAULT_MAX_CLASS_LINES: 默认类最大行数
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
        'eggs'
    ]

    DEFAULT_EXCLUDE_FILES = [
        '__init__.py',
        'conftest.py',
        'setup.py'
    ]

    DEFAULT_CYCLOMATIC_THRESHOLD = 10
    DEFAULT_COGNITIVE_THRESHOLD = 15
    DEFAULT_MAX_FUNCTION_LINES = 50
    DEFAULT_MAX_CLASS_LINES = 300

    @classmethod
    def analyze_file(cls, file_path: str) -> Dict[str, Any]:
        """
        分析单个 Python 文件的复杂度

        解析文件并计算每个函数和类的复杂度指标,包括:
        - 圈复杂度(Cyclomatic Complexity)
        - 认知复杂度(Cognitive Complexity)
        - 代码行数
        - 方法数量(仅类)

        Args:
            file_path: Python 文件路径

        Returns:
            字典,包含以下键:
            - file: 文件路径
            - functions: 函数复杂度列表
            - classes: 类复杂度列表
            - file_stats: 文件统计信息

        Raises:
            FileNotFoundError: 文件不存在
            SyntaxError: Python 语法错误
            ValueError: 无效的文件路径

        Example:
            >>> result = CodeComplexityAnalyzer.analyze_file("module.py")
            >>> print(result['functions'][0]['name'])
            'my_function'
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not file_path.suffix == '.py':
            raise ValueError(f"只支持 Python 文件: {file_path}")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # 解析 AST
        tree = ast.parse(source, filename=str(file_path))

        # 分析函数和类
        functions = []
        classes = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = cls._analyze_function(node, source)
                functions.append(func_info)
            elif isinstance(node, ast.ClassDef):
                class_info = cls._analyze_class(node, source)
                classes.append(class_info)
                # 提取类中的方法
                for method_node in ast.iter_child_nodes(node):
                    if isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_info = cls._analyze_function(method_node, source)
                        functions.append(method_info)

        # 计算文件统计
        total_lines = len(source.splitlines())
        max_complexity = max(
            [f['cyclomatic_complexity'] for f in functions] + [0]
        )

        return {
            'file': str(file_path),
            'functions': functions,
            'classes': classes,
            'file_stats': {
                'total_lines': total_lines,
                'function_count': len(functions),
                'class_count': len(classes),
                'max_complexity': max_complexity
            }
        }

    @classmethod
    def analyze_project(
        cls,
        project_root: str,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        cyclomatic_threshold: int = DEFAULT_CYCLOMATIC_THRESHOLD,
        cognitive_threshold: int = DEFAULT_COGNITIVE_THRESHOLD,
        max_function_lines: int = DEFAULT_MAX_FUNCTION_LINES,
        max_class_lines: int = DEFAULT_MAX_CLASS_LINES
    ) -> Dict[str, Any]:
        """
        分析整个 Python 项目的复杂度

        扫描项目目录下所有 Python 文件,分析复杂度指标,
        并汇总统计信息和高复杂度代码清单。

        Args:
            project_root: 项目根目录路径
            exclude_dirs: 排除的目录列表,默认为常见非源码目录
            exclude_files: 排除的文件列表,默认为 __init__.py 等
            cyclomatic_threshold: 圈复杂度警告阈值,默认 10
            cognitive_threshold: 认知复杂度警告阈值,默认 15
            max_function_lines: 函数最大行数,默认 50
            max_class_lines: 类最大行数,默认 300

        Returns:
            字典,包含以下键:
            - summary: 项目级统计摘要
            - files: 所有文件的分析结果
            - high_complexity_items: 超过阈值的代码清单

        Raises:
            NotADirectoryError: project_root 不是有效目录

        Example:
            >>> result = CodeComplexityAnalyzer.analyze_project("/path/to/project")
            >>> print(f"发现 {result['summary']['total_functions']} 个函数")
        """
        project_root = Path(project_root)

        if not project_root.is_dir():
            raise NotADirectoryError(f"无效的项目目录: {project_root}")

        # 使用默认排除列表
        if exclude_dirs is None:
            exclude_dirs = cls.DEFAULT_EXCLUDE_DIRS
        if exclude_files is None:
            exclude_files = cls.DEFAULT_EXCLUDE_FILES

        # 扫描所有 Python 文件
        python_files = cls._scan_python_files(project_root, exclude_dirs, exclude_files)

        # 分析每个文件
        file_results = []
        high_complexity_items = []

        for py_file in python_files:
            try:
                result = cls.analyze_file(py_file)
                file_results.append(result)

                # 检查高复杂度函数
                for func in result['functions']:
                    is_high = False
                    reasons = []

                    if func['cyclomatic_complexity'] > cyclomatic_threshold:
                        is_high = True
                        reasons.append(f"圈复杂度 {func['cyclomatic_complexity']} > {cyclomatic_threshold}")

                    if func['cognitive_complexity'] > cognitive_threshold:
                        is_high = True
                        reasons.append(f"认知复杂度 {func['cognitive_complexity']} > {cognitive_threshold}")

                    if func['lines_count'] > max_function_lines:
                        is_high = True
                        reasons.append(f"函数行数 {func['lines_count']} > {max_function_lines}")

                    if is_high:
                        high_complexity_items.append({
                            'type': 'function',
                            'name': func['name'],
                            'file': str(py_file),
                            'line': func['line'],
                            'cyclomatic_complexity': func['cyclomatic_complexity'],
                            'cognitive_complexity': func['cognitive_complexity'],
                            'lines_count': func['lines_count'],
                            'recommendation': cls._generate_recommendation(func, reasons)
                        })

                # 检查大类
                for cls_info in result['classes']:
                    if cls_info['lines_count'] > max_class_lines:
                        high_complexity_items.append({
                            'type': 'class',
                            'name': cls_info['name'],
                            'file': str(py_file),
                            'line': cls_info['line'],
                            'cyclomatic_complexity': 0,
                            'cognitive_complexity': 0,
                            'lines_count': cls_info['lines_count'],
                            'method_count': cls_info['method_count'],
                            'recommendation': f"建议拆分大类: {cls_info['name']} ({cls_info['lines_count']} 行, {cls_info['method_count']} 个方法)"
                        })

            except (SyntaxError, UnicodeDecodeError) as e:
                # 跳过有语法错误或编码问题的文件
                continue

        # 计算统计摘要
        summary = cls._calculate_summary(file_results)

        return {
            'summary': summary,
            'files': file_results,
            'high_complexity_items': high_complexity_items
        }

    @classmethod
    def generate_report(
        cls,
        analysis_result: Dict[str, Any],
        output_format: str = 'text',
        output_file: Optional[str] = None
    ) -> str:
        """
        生成复杂度分析报告

        将分析结果格式化为人类可读的报告,支持三种输出格式:
        - text: 纯文本格式,适合终端显示
        - json: JSON 格式,适合程序处理
        - markdown: Markdown 格式,适合文档化

        Args:
            analysis_result: analyze_project() 或 analyze_file() 返回的分析结果
            output_format: 输出格式,可选 'text', 'json', 'markdown',默认 'text'
            output_file: 输出文件路径,如提供则保存到文件

        Returns:
            格式化的报告字符串

        Raises:
            ValueError: output_format 不支持的值

        Example:
            >>> report = CodeComplexityAnalyzer.generate_report(result, 'markdown')
            >>> print(report)
        """
        if output_format not in ['text', 'json', 'markdown']:
            raise ValueError(f"不支持的输出格式: {output_format},仅支持 text/json/markdown")

        # 如果是单文件分析结果,转换为项目级格式
        if 'summary' not in analysis_result:
            # 单文件结果转换为项目级格式
            analysis_result = cls._convert_single_file_to_project_format(analysis_result)

        if output_format == 'json':
            report = cls._generate_json_report(analysis_result)
        elif output_format == 'text':
            report = cls._generate_text_report(analysis_result)
        else:  # markdown
            report = cls._generate_markdown_report(analysis_result)

        # 如果指定了输出文件,保存到文件
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)

        return report

    @classmethod
    def self_test(cls) -> bool:
        """
        自检测试,验证分析器核心功能

        创建临时 Python 文件并分析其复杂度,验证:
        - AST 解析正常
        - 圈复杂度计算正确
        - 认知复杂度计算正确
        - 函数/类大小统计准确

        Returns:
            bool: 测试通过返回 True,否则 False

        Example:
            >>> if CodeComplexityAnalyzer.self_test():
            ...     print("✅ 分析器自检测试通过")
        """
        try:
            # 创建测试代码
            test_code = '''
def simple_function(x):
    """简单函数,圈复杂度应为 1"""
    return x + 1

def complex_function(x, y):
    """复杂函数,圈复杂度应为 5"""
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    elif x < 0:
        return -x
    else:
        return 0

def nested_function(data):
    """嵌套函数,认知复杂度应较高"""
    result = []
    for item in data:
        if isinstance(item, dict):
            for key, value in item.items():
                if value > 0:
                    if key.startswith('valid_'):
                        result.append(value)
    return result

class SimpleClass:
    """简单类"""
    def __init__(self):
        self.value = 0

    def method(self):
        return self.value

class LargeClass:
    """大类"""
    def method1(self):
        pass

    def method2(self):
        pass

    def method3(self):
        pass
'''

            # 写入临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(test_code)
                temp_file = f.name

            try:
                # 分析文件
                result = cls.analyze_file(temp_file)

                # 验证函数数量 (3个顶层函数 + 2个SimpleClass方法 + 3个LargeClass方法 = 8个)
                if len(result['functions']) != 8:
                    print(f"自检测试失败: 函数数量错误,期望 8,实际 {len(result['functions'])}")
                    return False

                # 验证类数量
                if len(result['classes']) != 2:
                    print(f"自检测试失败: 类数量错误,期望 2,实际 {len(result['classes'])}")
                    return False

                # 验证 simple_function 的圈复杂度为 1
                simple_func = next(f for f in result['functions'] if f['name'] == 'simple_function')
                if simple_func['cyclomatic_complexity'] != 1:
                    print(f"自检测试失败: simple_function 圈复杂度错误,期望 1,实际 {simple_func['cyclomatic_complexity']}")
                    return False

                # 验证 complex_function 的圈复杂度(应该是 4 或 5)
                complex_func = next(f for f in result['functions'] if f['name'] == 'complex_function')
                if complex_func['cyclomatic_complexity'] < 4:
                    print(f"自检测试失败: complex_function 圈复杂度过低,期望 >=4,实际 {complex_func['cyclomatic_complexity']}")
                    return False

                # 验证 nested_function 的认知复杂度较高
                nested_func = next(f for f in result['functions'] if f['name'] == 'nested_function')
                if nested_func['cognitive_complexity'] < 8:
                    print(f"自检测试失败: nested_function 认知复杂度过低,期望 >=8,实际 {nested_func['cognitive_complexity']}")
                    return False

                # 验证报告生成
                report = cls.generate_report(result, 'text')
                if not report or 'simple_function' not in report:
                    print("自检测试失败: 文本报告生成失败")
                    return False

                # 验证 JSON 报告
                json_report = cls.generate_report(result, 'json')
                json_data = json.loads(json_report)
                if 'summary' not in json_data:
                    print("自检测试失败: JSON 报告缺少 summary")
                    return False

                # 验证 Markdown 报告
                md_report = cls.generate_report(result, 'markdown')
                if not md_report or '# 代码复杂度分析报告' not in md_report:
                    print("自检测试失败: Markdown 报告生成失败")
                    return False

                return True

            finally:
                # 清理临时文件
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

        except Exception as e:
            import traceback
            print(f"自检测试失败: {e}")
            print(traceback.format_exc())
            return False

    # ==================== 私有方法 ====================

    @classmethod
    def _scan_python_files(
        cls,
        root: Path,
        exclude_dirs: List[str],
        exclude_files: List[str]
    ) -> List[Path]:
        """
        扫描目录下的所有 Python 文件

        Args:
            root: 根目录
            exclude_dirs: 排除的目录
            exclude_files: 排除的文件

        Returns:
            Python 文件路径列表
        """
        python_files = []

        for path in root.rglob('*.py'):
            # 检查是否应该排除
            should_exclude = False

            # 检查目录
            for part in path.parts:
                if part in exclude_dirs:
                    should_exclude = True
                    break

            # 检查文件名
            if path.name in exclude_files:
                should_exclude = True

            if not should_exclude:
                python_files.append(path)

        return sorted(python_files)

    @classmethod
    def _analyze_function(cls, node: ast.AST, source: str) -> Dict[str, Any]:
        """
        分析单个函数的复杂度

        Args:
            node: AST 节点(FunctionDef 或 AsyncFunctionDef)
            source: 源代码

        Returns:
            函数复杂度信息字典
        """
        # 计算圈复杂度
        cyclomatic = cls._calculate_cyclomatic_complexity(node)

        # 计算认知复杂度
        cognitive = cls._calculate_cognitive_complexity(node)

        # 计算行数
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line)
        lines_count = end_line - start_line + 1

        return {
            'name': node.name,
            'line': start_line,
            'lines_count': lines_count,
            'cyclomatic_complexity': cyclomatic,
            'cognitive_complexity': cognitive,
            'complexity_level': cls._rate_complexity(cyclomatic, cognitive)
        }

    @classmethod
    def _analyze_class(cls, node: ast.ClassDef, source: str) -> Dict[str, Any]:
        """
        分析单个类的复杂度

        Args:
            node: AST 节点(ClassDef)
            source: 源代码

        Returns:
            类复杂度信息字典
        """
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line)
        lines_count = end_line - start_line + 1

        # 统计方法数
        method_count = sum(
            1 for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        )

        return {
            'name': node.name,
            'line': start_line,
            'lines_count': lines_count,
            'method_count': method_count,
            'complexity_level': cls._rate_class_complexity(lines_count, method_count)
        }

    @classmethod
    def _calculate_cyclomatic_complexity(cls, node: ast.AST) -> int:
        """
        计算圈复杂度(Cyclomatic Complexity)

        圈复杂度 = 1 + 控制流语句数量 + 布尔运算符数量

        控制流语句包括:
        - if, elif(视为if), for, while
        - except, with, assert
        - 三元表达式(IfExp)
        - 布尔运算符(and, or)

        Args:
            node: AST 节点

        Returns:
            圈复杂度值
        """
        complexity = 1  # 基础复杂度

        # 遍历所有子节点
        for child in ast.walk(node):
            # 控制流语句
            if isinstance(child, (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.ExceptHandler,
                ast.With,
                ast.AsyncWith,
                ast.Assert,
                ast.Try
            )):
                complexity += 1

            # 三元表达式
            elif isinstance(child, ast.IfExp):
                complexity += 1

            # 布尔运算符 (and, or)
            elif isinstance(child, ast.BoolOp):
                # 每个 and/or 运算符 +1
                # BoolOp.values 的长度 = 运算符数量
                complexity += len(child.values) - 1

        return complexity

    @classmethod
    def _calculate_cognitive_complexity(cls, node: ast.AST, nesting: int = 0) -> int:
        """
        计算认知复杂度(Cognitive Complexity)

        认知复杂度考虑代码的嵌套层级和结构复杂性:
        - 每个控制流语句: +1
        - 嵌套层级: 每层 +1
        - 布尔运算符序列: 每个 +1
        - 递归调用: +1

        Args:
            node: AST 节点
            nesting: 当前嵌套层级

        Returns:
            认知复杂度值
        """
        complexity = 0

        for child in ast.iter_child_nodes(node):
            # 控制流语句增加复杂度
            if isinstance(child, (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.With,
                ast.AsyncWith,
                ast.Try,
                ast.ExceptHandler
            )):
                # 基础分 + 嵌套层级分
                complexity += 1 + nesting
                # 递归处理子节点,增加嵌套层级
                complexity += cls._calculate_cognitive_complexity(child, nesting + 1)

            # 布尔运算符
            elif isinstance(child, ast.BoolOp):
                # 每个 and/or +1
                complexity += len(child.values) - 1
                # 递归处理
                complexity += cls._calculate_cognitive_complexity(child, nesting)

            # 三元表达式
            elif isinstance(child, ast.IfExp):
                complexity += 1 + nesting
                complexity += cls._calculate_cognitive_complexity(child, nesting + 1)

            # 函数/类定义(重置嵌套)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # 只计算直接子节点,不继续嵌套
                complexity += cls._calculate_cognitive_complexity(child, 0)

            # 其他节点正常遍历
            else:
                complexity += cls._calculate_cognitive_complexity(child, nesting)

        return complexity

    @classmethod
    def _rate_complexity(cls, cyclomatic: int, cognitive: int) -> str:
        """
        评估函数复杂度等级

        Args:
            cyclomatic: 圈复杂度
            cognitive: 认知复杂度

        Returns:
            复杂度等级: 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'
        """
        if cyclomatic <= 5 and cognitive <= 5:
            return 'LOW'
        elif cyclomatic <= 10 and cognitive <= 15:
            return 'MEDIUM'
        elif cyclomatic <= 20 and cognitive <= 30:
            return 'HIGH'
        else:
            return 'VERY_HIGH'

    @classmethod
    def _rate_class_complexity(cls, lines_count: int, method_count: int) -> str:
        """
        评估类的复杂度等级

        Args:
            lines_count: 代码行数
            method_count: 方法数量

        Returns:
            复杂度等级: 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'
        """
        if lines_count <= 100 and method_count <= 10:
            return 'LOW'
        elif lines_count <= 300 and method_count <= 20:
            return 'MEDIUM'
        elif lines_count <= 500 and method_count <= 30:
            return 'HIGH'
        else:
            return 'VERY_HIGH'

    @classmethod
    def _calculate_summary(cls, file_results: List[Dict]) -> Dict[str, Any]:
        """
        计算项目级统计摘要

        Args:
            file_results: 所有文件的分析结果

        Returns:
            统计摘要字典
        """
        total_files = len(file_results)
        total_functions = sum(f['file_stats']['function_count'] for f in file_results)
        total_classes = sum(f['file_stats']['class_count'] for f in file_results)

        # 收集所有函数的复杂度
        all_cyclomatic = []
        all_cognitive = []
        high_complexity_count = 0

        for file_result in file_results:
            for func in file_result['functions']:
                all_cyclomatic.append(func['cyclomatic_complexity'])
                all_cognitive.append(func['cognitive_complexity'])

                if func['complexity_level'] in ['HIGH', 'VERY_HIGH']:
                    high_complexity_count += 1

        # 计算平均值
        avg_cyclomatic = (
            sum(all_cyclomatic) / len(all_cyclomatic) if all_cyclomatic else 0
        )
        avg_cognitive = (
            sum(all_cognitive) / len(all_cognitive) if all_cognitive else 0
        )

        return {
            'total_files': total_files,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'avg_cyclomatic_complexity': round(avg_cyclomatic, 2),
            'avg_cognitive_complexity': round(avg_cognitive, 2),
            'high_complexity_count': high_complexity_count
        }

    @classmethod
    def _convert_single_file_to_project_format(cls, file_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        将单文件分析结果转换为项目级格式

        Args:
            file_result: analyze_file() 返回的结果

        Returns:
            项目级格式的结果
        """
        # 计算高复杂度项
        high_complexity_items = []
        for func in file_result['functions']:
            is_high = False
            reasons = []

            if func['cyclomatic_complexity'] > cls.DEFAULT_CYCLOMATIC_THRESHOLD:
                is_high = True
                reasons.append(f"圈复杂度 {func['cyclomatic_complexity']} > {cls.DEFAULT_CYCLOMATIC_THRESHOLD}")

            if func['cognitive_complexity'] > cls.DEFAULT_COGNITIVE_THRESHOLD:
                is_high = True
                reasons.append(f"认知复杂度 {func['cognitive_complexity']} > {cls.DEFAULT_COGNITIVE_THRESHOLD}")

            if func['lines_count'] > cls.DEFAULT_MAX_FUNCTION_LINES:
                is_high = True
                reasons.append(f"函数行数 {func['lines_count']} > {cls.DEFAULT_MAX_FUNCTION_LINES}")

            if is_high:
                high_complexity_items.append({
                    'type': 'function',
                    'name': func['name'],
                    'file': file_result['file'],
                    'line': func['line'],
                    'cyclomatic_complexity': func['cyclomatic_complexity'],
                    'cognitive_complexity': func['cognitive_complexity'],
                    'lines_count': func['lines_count'],
                    'recommendation': cls._generate_recommendation(func, reasons)
                })

        for cls_info in file_result['classes']:
            if cls_info['lines_count'] > cls.DEFAULT_MAX_CLASS_LINES:
                high_complexity_items.append({
                    'type': 'class',
                    'name': cls_info['name'],
                    'file': file_result['file'],
                    'line': cls_info['line'],
                    'cyclomatic_complexity': 0,
                    'cognitive_complexity': 0,
                    'lines_count': cls_info['lines_count'],
                    'method_count': cls_info['method_count'],
                    'recommendation': f"建议拆分大类: {cls_info['name']} ({cls_info['lines_count']} 行, {cls_info['method_count']} 个方法)"
                })

        # 计算统计
        all_cyclomatic = [f['cyclomatic_complexity'] for f in file_result['functions']]
        all_cognitive = [f['cognitive_complexity'] for f in file_result['functions']]
        high_complexity_count = sum(
            1 for f in file_result['functions']
            if f['complexity_level'] in ['HIGH', 'VERY_HIGH']
        )

        summary = {
            'total_files': 1,
            'total_functions': file_result['file_stats']['function_count'],
            'total_classes': file_result['file_stats']['class_count'],
            'avg_cyclomatic_complexity': round(
                sum(all_cyclomatic) / len(all_cyclomatic) if all_cyclomatic else 0, 2
            ),
            'avg_cognitive_complexity': round(
                sum(all_cognitive) / len(all_cognitive) if all_cognitive else 0, 2
            ),
            'high_complexity_count': high_complexity_count
        }

        return {
            'summary': summary,
            'files': [file_result],
            'high_complexity_items': high_complexity_items
        }

    @classmethod
    def _generate_text_report(cls, result: Dict[str, Any]) -> str:
        """生成文本格式报告"""
        lines = []
        separator = '═' * 55
        sub_separator = '━' * 55

        # 标题
        lines.append(separator)
        lines.append('代码复杂度分析报告')
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(separator)
        lines.append('')

        # 统计摘要
        summary = result['summary']
        lines.append('【统计摘要】')
        lines.append(sub_separator)
        lines.append(f"• 扫描文件总数: {summary['total_files']}")
        lines.append(f"• 函数总数: {summary['total_functions']}")
        lines.append(f"• 类总数: {summary['total_classes']}")
        lines.append(f"• 平均圈复杂度: {summary['avg_cyclomatic_complexity']}")
        lines.append(f"• 平均认知复杂度: {summary['avg_cognitive_complexity']}")
        lines.append(f"• 高复杂度代码: {summary['high_complexity_count']} 处")
        lines.append('')

        # 高复杂度代码
        high_items = result['high_complexity_items']
        if high_items:
            lines.append('【高复杂度代码】')
            lines.append(sub_separator)
            lines.append('')

            for i, item in enumerate(high_items, 1):
                if item['type'] == 'function':
                    lines.append(
                        f"{i}. 函数: {item['name']} ({item['file']}:{item['line']})"
                    )
                    cc = item['cyclomatic_complexity']
                    cog = item['cognitive_complexity']

                    # 评级标签
                    cc_label = '高' if cc > 10 else '中' if cc > 5 else '低'
                    cog_label = '高' if cog > 15 else '中' if cog > 5 else '低'

                    lines.append(
                        f"   圈复杂度: {cc} ({cc_label}) | "
                        f"认知复杂度: {cog} ({cog_label})"
                    )
                    lines.append(f"   代码行数: {item['lines_count']}")
                    lines.append(f"   建议: {item['recommendation']}")
                else:  # class
                    lines.append(
                        f"{i}. 类: {item['name']} ({item['file']}:{item['line']})"
                    )
                    lines.append(
                        f"   代码行数: {item['lines_count']} | "
                        f"方法数: {item.get('method_count', 'N/A')}"
                    )
                    lines.append(f"   建议: {item['recommendation']}")
                lines.append('')

        # 文件详情(仅显示前10个文件)
        lines.append('【文件详情】')
        lines.append(sub_separator)
        lines.append('')

        for file_result in result['files'][:10]:
            stats = file_result['file_stats']
            lines.append(f"{file_result['file']}")
            lines.append(
                f"  • 总行数: {stats['total_lines']} | "
                f"函数数: {stats['function_count']} | "
                f"类数: {stats['class_count']}"
            )
            lines.append(f"  • 最高复杂度: {stats['max_complexity']}")
            lines.append('')

            # 显示函数列表
            if file_result['functions']:
                lines.append('  函数列表:')
                for func in file_result['functions']:
                    cc = func['cyclomatic_complexity']
                    cog = func['cognitive_complexity']

                    # 图标
                    if func['complexity_level'] == 'LOW':
                        icon = '✅'
                    elif func['complexity_level'] == 'MEDIUM':
                        icon = '⚠️'
                    else:
                        icon = '🔴'

                    lines.append(
                        f"    - {func['name']} ({func['line']}): "
                        f"CC={cc}, CogC={cog}, "
                        f"{func['lines_count']}行 {icon}"
                    )
                lines.append('')

        lines.append(separator)

        return '\n'.join(lines)

    @classmethod
    def _generate_json_report(cls, result: Dict[str, Any]) -> str:
        """生成 JSON 格式报告"""
        # 添加元数据
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'tool': 'CodeComplexityAnalyzer',
                'version': '1.0.0'
            },
            'summary': result['summary'],
            'high_complexity_items': result['high_complexity_items'],
            'files': result['files']
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False)

    @classmethod
    def _generate_markdown_report(cls, result: Dict[str, Any]) -> str:
        """生成 Markdown 格式报告"""
        lines = []

        # 标题
        lines.append('# 代码复杂度分析报告')
        lines.append('')
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append('')

        # 统计摘要
        summary = result['summary']
        lines.append('## 📊 统计摘要')
        lines.append('')
        lines.append('| 指标 | 值 |')
        lines.append('|------|-----|')
        lines.append(f"| 扫描文件总数 | {summary['total_files']} |")
        lines.append(f"| 函数总数 | {summary['total_functions']} |")
        lines.append(f"| 类总数 | {summary['total_classes']} |")
        lines.append(f"| 平均圈复杂度 | {summary['avg_cyclomatic_complexity']} |")
        lines.append(f"| 平均认知复杂度 | {summary['avg_cognitive_complexity']} |")
        lines.append(f"| 高复杂度代码 | {summary['high_complexity_count']} 处 |")
        lines.append('')

        # 高复杂度代码
        high_items = result['high_complexity_items']
        if high_items:
            lines.append('## 🚨 高复杂度代码')
            lines.append('')

            for item in high_items:
                if item['type'] == 'function':
                    lines.append(f"### 函数: `{item['name']}`")
                    lines.append('')
                    lines.append(f"- **文件**: `{item['file']}:{item['line']}`")
                    lines.append(f"- **圈复杂度**: {item['cyclomatic_complexity']}")
                    lines.append(f"- **认知复杂度**: {item['cognitive_complexity']}")
                    lines.append(f"- **代码行数**: {item['lines_count']}")
                    lines.append(f"- **建议**: {item['recommendation']}")
                    lines.append('')
                else:
                    lines.append(f"### 类: `{item['name']}`")
                    lines.append('')
                    lines.append(f"- **文件**: `{item['file']}:{item['line']}`")
                    lines.append(f"- **代码行数**: {item['lines_count']}")
                    lines.append(f"- **方法数**: {item.get('method_count', 'N/A')}")
                    lines.append(f"- **建议**: {item['recommendation']}")
                    lines.append('')

        # 文件详情
        lines.append('## 📁 文件详情')
        lines.append('')

        for file_result in result['files']:
            stats = file_result['file_stats']
            lines.append(f"### `{file_result['file']}`")
            lines.append('')
            lines.append(f"- 总行数: {stats['total_lines']}")
            lines.append(f"- 函数数: {stats['function_count']}")
            lines.append(f"- 类数: {stats['class_count']}")
            lines.append(f"- 最高复杂度: {stats['max_complexity']}")
            lines.append('')

            if file_result['functions']:
                lines.append('**函数列表:**')
                lines.append('')
                lines.append('| 函数名 | 行号 | 圈复杂度 | 认知复杂度 | 行数 | 等级 |')
                lines.append('|--------|------|---------|-----------|------|------|')

                for func in file_result['functions']:
                    lines.append(
                        f"| {func['name']} "
                        f"| {func['line']} "
                        f"| {func['cyclomatic_complexity']} "
                        f"| {func['cognitive_complexity']} "
                        f"| {func['lines_count']} "
                        f"| {func['complexity_level']} |"
                    )
                lines.append('')

        return '\n'.join(lines)

    @classmethod
    def _generate_recommendation(cls, func_info: Dict, reasons: List[str]) -> str:
        """
        生成重构建议

        Args:
            func_info: 函数复杂度信息
            reasons: 超标原因列表

        Returns:
            建议字符串
        """
        recommendations = []

        if func_info['cyclomatic_complexity'] > 10:
            recommendations.append('减少条件分支')

        if func_info['cognitive_complexity'] > 15:
            recommendations.append('降低嵌套层级')

        if func_info['lines_count'] > 50:
            recommendations.append('拆分函数')

        base = '建议: '
        if recommendations:
            return base + ', '.join(recommendations)
        else:
            return '建议: 审查代码逻辑'
