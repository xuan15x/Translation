"""
代码重复扫描器 - 核心实现

自动扫描 Python 项目中的重复类和相似文件，帮助识别代码重复问题，
提升代码质量和可维护性。

使用示例:
    >>> from .qwen.skills.code_dedup_scanner import CodeDedupScanner
    >>> duplicates = CodeDedupScanner.scan_duplicate_classes('/path/to/project')
    >>> similar_files = CodeDedupScanner.scan_duplicate_files('/path/to/project')
    >>> report = CodeDedupScanner.generate_report(duplicates, similar_files)
    >>> print(report)

版本: 1.0.0
创建日期: 2026-04-03
"""

import ast
import json
import os
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class CodeDedupScanner:
    """
    代码重复扫描器
    
    提供以下核心功能:
    - 扫描项目中的重复类定义
    - 检测高度相似的 Python 文件
    - 生成结构化的扫描报告
    
    Attributes:
        DEFAULT_EXCLUDE_DIRS: 默认排除的目录列表
        DEFAULT_EXCLUDE_FILES: 默认排除的文件列表
        MIN_SIMILARITY_THRESHOLD: 最小相似度阈值
    """
    
    # 默认排除的目录
    DEFAULT_EXCLUDE_DIRS = [
        '.git',
        '.venv',
        'venv',
        '__pycache__',
        'node_modules',
        '.mypy_cache',
        '.pytest_cache',
        'dist',
        'build',
        '.tox'
    ]
    
    # 默认排除的文件
    DEFAULT_EXCLUDE_FILES = [
        '__init__.py',
        'conftest.py',
        'setup.py',
        'manage.py'
    ]
    
    # 最小相似度阈值
    MIN_SIMILARITY_THRESHOLD = 0.8
    
    @classmethod
    def scan_duplicate_classes(
        cls,
        project_root: str,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        include_tests: bool = False
    ) -> List[Dict[str, Any]]:
        """
        扫描项目中的重复类定义
        
        使用 Python AST (Abstract Syntax Tree) 解析所有 Python 文件，
        提取类定义信息，并按类名分组统计，识别重复的类。
        
        Args:
            project_root: 项目根目录路径
            exclude_dirs: 需要排除的目录列表，默认使用 DEFAULT_EXCLUDE_DIRS
            exclude_files: 需要排除的文件列表，默认使用 DEFAULT_EXCLUDE_FILES
            include_tests: 是否包含测试文件（文件名包含 'test' 的文件），默认 False
            
        Returns:
            重复类信息列表，每个元素包含:
            - class_name: 类名
            - locations: 类定义位置列表，每项包含:
                - file: 文件路径
                - line: 行号
                - code_snippet: 代码片段（类定义及上下文）
            - count: 出现次数
            
        Raises:
            ValueError: 当 project_root 不存在或不是目录时
            PermissionError: 当无权访问某些文件时
            
        Example:
            >>> duplicates = CodeDedupScanner.scan_duplicate_classes('/path/to/project')
            >>> for dup in duplicates:
            ...     print(f"{dup['class_name']}: {dup['count']} 处定义")
        """
        # 验证项目根目录
        project_path = Path(project_root)
        if not project_path.exists():
            raise ValueError(f"项目路径不存在: {project_root}")
        if not project_path.is_dir():
            raise ValueError(f"项目路径不是目录: {project_root}")
        
        # 设置默认排除列表
        exclude_dirs = exclude_dirs or cls.DEFAULT_EXCLUDE_DIRS
        exclude_files = exclude_files or cls.DEFAULT_EXCLUDE_FILES
        
        # 存储所有类定义: {class_name: [locations]}
        class_definitions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # 扫描所有 Python 文件
        python_files = cls._find_python_files(
            project_path,
            exclude_dirs=exclude_dirs,
            exclude_files=exclude_files,
            include_tests=include_tests
        )
        
        # 解析每个文件，提取类定义
        for file_path in python_files:
            try:
                classes = cls._extract_classes_from_file(file_path, project_path)
                for class_info in classes:
                    class_definitions[class_info['class_name']].append(class_info)
            except (SyntaxError, UnicodeDecodeError, PermissionError) as e:
                # 忽略无法解析的文件
                continue
        
        # 过滤出重复的类（出现次数 > 1）
        duplicates = [
            {
                'class_name': class_name,
                'locations': locations,
                'count': len(locations)
            }
            for class_name, locations in class_definitions.items()
            if len(locations) > 1
        ]
        
        # 按出现次数降序排序
        duplicates.sort(key=lambda x: x['count'], reverse=True)
        
        return duplicates
    
    @classmethod
    def scan_duplicate_files(
        cls,
        project_root: str,
        similarity_threshold: float = MIN_SIMILARITY_THRESHOLD,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        min_lines: int = 10
    ) -> List[Dict[str, Any]]:
        """
        扫描项目中相似的 Python 文件
        
        通过计算文件间的 Jaccard 相似度，识别高度相似的文件对。
        相似度计算基于标准化后的代码行集合。
        
        Args:
            project_root: 项目根目录路径
            similarity_threshold: 相似度阈值 (0.0-1.0)，只返回相似度 >= 该值的文件对
                                 默认 0.8 (80%)
            exclude_dirs: 需要排除的目录列表，默认使用 DEFAULT_EXCLUDE_DIRS
            exclude_files: 需要排除的文件列表，默认使用 DEFAULT_EXCLUDE_FILES
            min_lines: 最小代码行数，低于此行数的文件将被忽略，默认 10
            
        Returns:
            相似文件对列表，每个元素包含:
            - file1: 第一个文件的路径（相对项目根目录）
            - file2: 第二个文件的路径（相对项目根目录）
            - similarity: 相似度分数 (0.0-1.0)
            - common_lines: 共同代码行数
            - total_lines_file1: 第一个文件的总代码行数
            - total_lines_file2: 第二个文件的总代码行数
            
        Raises:
            ValueError: 当 similarity_threshold 不在 [0.0, 1.0] 范围内时
            ValueError: 当 project_root 不存在或不是目录时
            
        Example:
            >>> similar = CodeDedupScanner.scan_duplicate_files(
            ...     '/path/to/project',
            ...     similarity_threshold=0.85
            ... )
            >>> for pair in similar:
            ...     print(f"{pair['file1']} ↔ {pair['file2']}: {pair['similarity']:.1%}")
        """
        # 验证参数
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError(
                f"similarity_threshold 必须在 [0.0, 1.0] 范围内，当前值: {similarity_threshold}"
            )
        
        project_path = Path(project_root)
        if not project_path.exists():
            raise ValueError(f"项目路径不存在: {project_root}")
        if not project_path.is_dir():
            raise ValueError(f"项目路径不是目录: {project_root}")
        
        # 设置默认排除列表
        exclude_dirs = exclude_dirs or cls.DEFAULT_EXCLUDE_DIRS
        exclude_files = exclude_files or cls.DEFAULT_EXCLUDE_FILES
        
        # 扫描所有 Python 文件
        python_files = cls._find_python_files(
            project_path,
            exclude_dirs=exclude_dirs,
            exclude_files=exclude_files,
            include_tests=True  # 文件相似度扫描包含所有文件
        )
        
        # 提取每个文件的代码行（标准化后）
        file_lines: Dict[Path, set] = {}
        for file_path in python_files:
            try:
                lines = cls._extract_code_lines(file_path, min_lines=min_lines)
                if lines:  # 只保留有效代码行
                    file_lines[file_path] = lines
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # 计算文件对相似度
        similar_pairs = []
        file_list = list(file_lines.keys())
        
        for i in range(len(file_list)):
            for j in range(i + 1, len(file_list)):
                file1 = file_list[i]
                file2 = file_list[j]
                
                lines1 = file_lines[file1]
                lines2 = file_lines[file2]
                
                # 计算 Jaccard 相似度
                intersection = lines1 & lines2
                union = lines1 | lines2
                
                if not union:
                    continue
                
                similarity = len(intersection) / len(union)
                
                # 如果超过阈值，记录该文件对
                if similarity >= similarity_threshold:
                    similar_pairs.append({
                        'file1': str(file1.relative_to(project_path)),
                        'file2': str(file2.relative_to(project_path)),
                        'similarity': similarity,
                        'common_lines': len(intersection),
                        'total_lines_file1': len(lines1),
                        'total_lines_file2': len(lines2)
                    })
        
        # 按相似度降序排序
        similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_pairs
    
    @classmethod
    def generate_report(
        cls,
        duplicates: List[Dict[str, Any]],
        similar_files: List[Dict[str, Any]],
        output_format: str = 'text',
        output_file: Optional[str] = None
    ) -> str:
        """
        生成扫描报告
        
        根据扫描结果生成格式化的报告，支持文本、JSON 和 Markdown 格式。
        可选择将报告保存到文件。
        
        Args:
            duplicates: 重复类清单（来自 scan_duplicate_classes）
            similar_files: 相似文件对清单（来自 scan_duplicate_files）
            output_format: 输出格式，可选值:
                - 'text': 纯文本格式（默认）
                - 'json': JSON 格式
                - 'markdown': Markdown 格式
            output_file: 输出文件路径，如提供则将报告保存到该文件
            
        Returns:
            生成的报告字符串
            
        Raises:
            ValueError: 当 output_format 不支持时
            
        Example:
            >>> report = CodeDedupScanner.generate_report(
            ...     duplicates,
            ...     similar_files,
            ...     output_format='markdown'
            ... )
            >>> print(report)
        """
        # 根据格式生成报告
        if output_format == 'text':
            report = cls._generate_text_report(duplicates, similar_files)
        elif output_format == 'json':
            report = cls._generate_json_report(duplicates, similar_files)
        elif output_format == 'markdown':
            report = cls._generate_markdown_report(duplicates, similar_files)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}，支持的格式: 'text', 'json', 'markdown'")
        
        # 如果指定了输出文件，保存到文件
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report
    
    @classmethod
    def self_test(cls) -> bool:
        """
        执行自检测试
        
        使用内置的测试数据验证扫描器的核心功能是否正常工作。
        
        Returns:
            True 如果所有测试通过，否则 False
            
        Example:
            >>> if CodeDedupScanner.self_test():
            ...     print("✅ 扫描器自检通过")
        """
        try:
            # 测试 1: 扫描重复类
            test_duplicates = [
                {
                    'class_name': 'TestClass',
                    'locations': [
                        {'file': 'test1.py', 'line': 10, 'code_snippet': 'class TestClass:'},
                        {'file': 'test2.py', 'line': 20, 'code_snippet': 'class TestClass:'}
                    ],
                    'count': 2
                }
            ]
            
            # 测试 2: 扫描相似文件
            test_similar_files = [
                {
                    'file1': 'file1.py',
                    'file2': 'file2.py',
                    'similarity': 0.85,
                    'common_lines': 42,
                    'total_lines_file1': 50,
                    'total_lines_file2': 48
                }
            ]
            
            # 测试 3: 生成报告
            text_report = cls.generate_report(test_duplicates, test_similar_files, 'text')
            json_report = cls.generate_report(test_duplicates, test_similar_files, 'json')
            md_report = cls.generate_report(test_duplicates, test_similar_files, 'markdown')
            
            # 验证报告不为空
            if not all([text_report, json_report, md_report]):
                return False
            
            # 验证 JSON 报告可以解析
            json_data = json.loads(json_report)
            if 'duplicates' not in json_data or 'similar_files' not in json_data:
                return False
            
            return True
            
        except Exception as e:
            print(f"自检测试失败: {e}")
            return False
    
    # ==================== 私有方法 ====================
    
    @classmethod
    def _find_python_files(
        cls,
        project_path: Path,
        exclude_dirs: List[str],
        exclude_files: List[str],
        include_tests: bool = False
    ) -> List[Path]:
        """
        查找项目中所有 Python 文件
        
        Args:
            project_path: 项目根目录路径
            exclude_dirs: 排除的目录列表
            exclude_files: 排除的文件列表
            include_tests: 是否包含测试文件
            
        Returns:
            Python 文件路径列表
        """
        python_files = []
        
        for root, dirs, files in os.walk(project_path):
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if not file.endswith('.py'):
                    continue
                
                # 过滤排除的文件
                if file in exclude_files:
                    continue
                
                # 过滤测试文件
                if not include_tests and ('test' in file.lower() or file.startswith('test_')):
                    continue
                
                file_path = Path(root) / file
                python_files.append(file_path)
        
        return python_files
    
    @classmethod
    def _extract_classes_from_file(
        cls,
        file_path: Path,
        project_path: Path
    ) -> List[Dict[str, Any]]:
        """
        从 Python 文件中提取所有类定义
        
        Args:
            file_path: 文件路径
            project_path: 项目根目录路径
            
        Returns:
            类定义信息列表
        """
        classes = []
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 解析 AST
        tree = ast.parse(source, filename=str(file_path))
        
        # 提取类定义
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 提取代码片段（类定义及后面 2 行）
                lines = source.split('\n')
                start_line = node.lineno - 1  # AST 行号从 1 开始
                end_line = min(start_line + 3, len(lines))
                code_snippet = '\n'.join(lines[start_line:end_line])
                
                classes.append({
                    'class_name': node.name,
                    'file': str(file_path.relative_to(project_path)),
                    'line': node.lineno,
                    'code_snippet': code_snippet
                })
        
        return classes
    
    @classmethod
    def _extract_code_lines(cls, file_path: Path, min_lines: int = 10) -> set:
        """
        提取文件的标准化代码行
        
        去除空行、注释和文档字符串，保留有效代码行并进行标准化处理，
        以便进行相似度比较。
        
        Args:
            file_path: 文件路径
            min_lines: 最小代码行数，低于此行数返回空集
            
        Returns:
            标准化后的代码行集合
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, PermissionError):
            return set()
        
        code_lines = set()
        in_docstring = False
        docstring_char = None
        
        for line in lines:
            stripped = line.strip()
            
            # 跳过空行
            if not stripped:
                continue
            
            # 处理文档字符串
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    docstring_char = stripped[:3]
                    if stripped.count(docstring_char) >= 2:
                        # 单行文档字符串
                        continue
                    else:
                        in_docstring = True
                        continue
            else:
                if docstring_char in stripped:
                    in_docstring = False
                continue
            
            # 跳过单行注释
            if stripped.startswith('#'):
                continue
            
            # 标准化处理：移除变量名差异，保留结构
            normalized = cls._normalize_line(stripped)
            if normalized:
                code_lines.add(normalized)
        
        # 如果代码行数不足，返回空集
        if len(code_lines) < min_lines:
            return set()
        
        return code_lines
    
    @classmethod
    def _normalize_line(cls, line: str) -> str:
        """
        标准化代码行，保留结构特征

        通过提取关键字和优化模式匹配，减少误判相似文件的可能性。
        保留Python关键字序列，对赋值语句进行特殊处理。

        Args:
            line: 原始代码行

        Returns:
            标准化后的代码行，保留关键结构信息
        """
        import re
        
        # 移除行尾注释
        if '#' in line:
            line = line[:line.index('#')].strip()
        
        # 替换字符串字面量
        line = re.sub(r'""".*?"""', '"""STR"""', line, flags=re.DOTALL)
        line = re.sub(r"'''.*?'''", "'''STR'''", line, flags=re.DOTALL)
        line = re.sub(r'"[^"]*"', '"STR"', line)
        line = re.sub(r"'[^']*'", "'STR'", line)
        
        # 替换数字
        line = re.sub(r'\b\d+\b', 'NUM', line)
        
        # 提取关键字
        keywords = [
            'class', 'def', 'if', 'elif', 'else', 'for', 'while', 'try',
            'except', 'finally', 'with', 'as', 'import', 'from', 'return',
            'yield', 'raise', 'pass', 'break', 'continue', 'and', 'or',
            'not', 'is', 'in', 'True', 'False', 'None', 'self', 'async',
            'await'
        ]
        
        # 保留关键字序列
        parts = [kw for kw in keywords if f' {kw} ' in f' {line} ' or line.startswith(kw + ' ')]
        
        # 如果有关键字，返回关键字序列；否则返回标准化后的行
        if parts:
            return ' '.join(parts)
        
        # 对赋值语句特殊处理
        if '=' in line and '==' not in line and '!=' not in line:
            parts = line.split('=')
            if len(parts) == 2:
                return 'VAR = VAR'  # 统一赋值语句
        
        return line.strip() if line.strip() else ''
    
    @classmethod
    def _generate_text_report(
        cls,
        duplicates: List[Dict[str, Any]],
        similar_files: List[Dict[str, Any]]
    ) -> str:
        """生成文本格式报告"""
        lines = []
        separator = "═" * 60
        
        # 报告头部
        lines.append(separator)
        lines.append("代码重复扫描报告")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(separator)
        lines.append("")
        
        # 重复类部分
        lines.append("【重复类】")
        lines.append("━" * 60)
        lines.append("")
        
        if duplicates:
            for idx, dup in enumerate(duplicates, 1):
                lines.append(f"{idx}. {dup['class_name']} ({dup['count']} 处定义)")
                for loc in dup['locations']:
                    lines.append(f"   • {loc['file']}:{loc['line']}")
                lines.append("")
        else:
            lines.append("未发现重复类 ✓")
            lines.append("")
        
        # 相似文件部分
        lines.append("【相似文件】")
        lines.append("━" * 60)
        lines.append("")
        
        if similar_files:
            for idx, pair in enumerate(similar_files, 1):
                lines.append(
                    f"{idx}. {pair['file1']} ↔ {pair['file2']}"
                )
                lines.append(
                    f"   相似度: {pair['similarity']:.1%} | "
                    f"共同代码行: {pair['common_lines']}/{pair['total_lines_file1']}"
                )
                lines.append("")
        else:
            lines.append("未发现相似文件 ✓")
            lines.append("")
        
        # 统计摘要
        lines.append("【统计摘要】")
        lines.append("━" * 60)
        lines.append("")
        lines.append(f"• 发现重复类: {len(duplicates)} 个")
        lines.append(
            f"  涉及定义数: {sum(d['count'] for d in duplicates)} 处"
        )
        lines.append(f"• 发现相似文件对: {len(similar_files)} 对")
        
        if similar_files:
            avg_similarity = sum(p['similarity'] for p in similar_files) / len(similar_files)
            lines.append(f"• 平均相似度: {avg_similarity:.1%}")
        
        lines.append("")
        lines.append(separator)
        
        return '\n'.join(lines)
    
    @classmethod
    def _generate_json_report(
        cls,
        duplicates: List[Dict[str, Any]],
        similar_files: List[Dict[str, Any]]
    ) -> str:
        """生成 JSON 格式报告"""
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'scanner_version': '1.0.0'
            },
            'duplicates': duplicates,
            'similar_files': similar_files,
            'summary': {
                'duplicate_classes_count': len(duplicates),
                'duplicate_definitions_count': sum(d['count'] for d in duplicates),
                'similar_file_pairs_count': len(similar_files),
                'average_similarity': (
                    sum(p['similarity'] for p in similar_files) / len(similar_files)
                    if similar_files else 0.0
                )
            }
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    @classmethod
    def _generate_markdown_report(
        cls,
        duplicates: List[Dict[str, Any]],
        similar_files: List[Dict[str, Any]]
    ) -> str:
        """生成 Markdown 格式报告"""
        lines = []
        
        # 报告头部
        lines.append("# 代码重复扫描报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**扫描器版本**: 1.0.0")
        lines.append("")
        
        # 重复类部分
        lines.append("## 重复类")
        lines.append("")
        
        if duplicates:
            lines.append(f"共发现 **{len(duplicates)}** 个重复类：")
            lines.append("")
            
            for idx, dup in enumerate(duplicates, 1):
                lines.append(f"### {idx}. `{dup['class_name']}`")
                lines.append("")
                lines.append(f"**出现次数**: {dup['count']} 次")
                lines.append("")
                lines.append("| 文件 | 行号 | 代码片段 |")
                lines.append("|------|------|---------|")
                
                for loc in dup['locations']:
                    # 转义 Markdown 特殊字符
                    snippet = loc['code_snippet'].replace('|', '\\|').replace('\n', '<br>')
                    lines.append(
                        f"| `{loc['file']}` | {loc['line']} | `{snippet}` |"
                    )
                
                lines.append("")
        else:
            lines.append("✅ 未发现重复类")
            lines.append("")
        
        # 相似文件部分
        lines.append("## 相似文件")
        lines.append("")
        
        if similar_files:
            lines.append(f"共发现 **{len(similar_files)}** 对相似文件：")
            lines.append("")
            lines.append("| # | 文件 1 | 文件 2 | 相似度 | 共同行数 |")
            lines.append("|---|--------|--------|--------|---------|")
            
            for idx, pair in enumerate(similar_files, 1):
                lines.append(
                    f"| {idx} | `{pair['file1']}` | `{pair['file2']}` | "
                    f"{pair['similarity']:.1%} | {pair['common_lines']} |"
                )
            
            lines.append("")
        else:
            lines.append("✅ 未发现相似文件")
            lines.append("")
        
        # 统计摘要
        lines.append("## 统计摘要")
        lines.append("")
        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")
        lines.append(f"| 重复类数量 | {len(duplicates)} |")
        lines.append(f"| 重复定义总数 | {sum(d['count'] for d in duplicates)} |")
        lines.append(f"| 相似文件对数 | {len(similar_files)} |")
        
        if similar_files:
            avg_similarity = sum(p['similarity'] for p in similar_files) / len(similar_files)
            lines.append(f"| 平均相似度 | {avg_similarity:.1%} |")
        
        lines.append("")
        
        return '\n'.join(lines)
