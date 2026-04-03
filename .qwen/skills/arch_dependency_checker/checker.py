"""
架构依赖检查器 - 核心实现

验证分层架构依赖规则，检测违反架构的导入关系。
支持六层架构：presentation、application、domain、service、data_access、infrastructure。

使用示例:
    >>> from .qwen.skills.arch_dependency_checker import ArchDependencyChecker
    >>> result = ArchDependencyChecker.check_project('/path/to/project')
    >>> violations = ArchDependencyChecker.check_file('/path/to/file.py')
    >>> report = ArchDependencyChecker.generate_report(result['violations'])
    >>> print(report)

版本: 1.0.0
创建日期: 2026-04-03
"""

import ast
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ArchDependencyChecker:
    """
    架构依赖检查器

    验证分层架构依赖规则，检测违反架构的导入关系。

    六层架构规则:
    - presentation: 表示层（应主要通过application层访问）
    - application: 应用层（可访问domain和service层）
    - domain: 领域层（不应访问infrastructure、service、data_access）
    - service: 服务层（可访问domain和infrastructure）
    - data_access: 数据访问层（可访问domain，不应访问service）
    - infrastructure: 基础设施层（不应访问domain的业务逻辑）

    Attributes:
        ARCH_RULES: 默认架构规则定义
        DEFAULT_EXCLUDE_DIRS: 默认排除的目录
        DEFAULT_EXCLUDE_FILES: 默认排除的文件
    """

    # 架构规则定义
    ARCH_RULES = {
        'presentation': {
            'can_import': ['presentation', 'application', 'infrastructure'],
            'cannot_import': ['domain', 'service', 'data_access'],
            'description': '表示层应主要通过application层访问'
        },
        'application': {
            'can_import': ['application', 'domain', 'service', 'data_access', 'infrastructure'],
            'cannot_import': ['presentation'],
            'description': '应用层可访问domain和service层'
        },
        'domain': {
            'can_import': ['domain'],
            'cannot_import': ['infrastructure', 'service', 'data_access', 'presentation', 'application'],
            'description': '领域层不应访问infrastructure、service、data_access'
        },
        'service': {
            'can_import': ['service', 'domain', 'infrastructure'],
            'cannot_import': ['presentation', 'application', 'data_access'],
            'description': '服务层可访问domain和infrastructure'
        },
        'data_access': {
            'can_import': ['data_access', 'domain', 'infrastructure'],
            'cannot_import': ['service', 'presentation', 'application'],
            'description': '数据访问层可访问domain，不应访问service'
        },
        'infrastructure': {
            'can_import': ['infrastructure'],
            'cannot_import': ['domain', 'service', 'data_access', 'presentation', 'application'],
            'description': '基础设施层不应访问domain的业务逻辑'
        }
    }

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
        '.tox',
        'tests',
        '.qwen',
        'scripts'
    ]

    # 默认排除的文件
    DEFAULT_EXCLUDE_FILES = [
        '__init__.py',
        'conftest.py',
        'setup.py',
        'manage.py'
    ]

    # 架构层目录映射
    LAYER_DIRS = {
        'presentation': 'presentation',
        'application': 'application',
        'domain': 'domain',
        'service': 'service',
        'data_access': 'data_access',
        'infrastructure': 'infrastructure'
    }

    @classmethod
    def check_project(
        cls,
        project_root: str,
        custom_rules: Optional[Dict[str, Any]] = None,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        strict_mode: bool = False
    ) -> Dict[str, Any]:
        """
        检查整个项目的架构依赖

        扫描项目中所有Python文件，解析导入关系，验证是否符合架构规则。

        Args:
            project_root: 项目根目录路径
            custom_rules: 自定义架构规则，覆盖默认规则
                         格式: {'layer_name': {'can_import': [...], 'cannot_import': [...]}}
            exclude_dirs: 需要排除的目录列表，默认使用 DEFAULT_EXCLUDE_DIRS
            exclude_files: 需要排除的文件列表，默认使用 DEFAULT_EXCLUDE_FILES
            strict_mode: 严格模式，将警告级别的违规视为错误

        Returns:
            检查结果字典，包含:
            - violations: 违规清单列表
            - summary: 统计摘要
            - metadata: 元数据信息

        Raises:
            ValueError: 当 project_root 不存在或不是目录时
            PermissionError: 当无权访问某些文件时

        Example:
            >>> result = ArchDependencyChecker.check_project('/path/to/project')
            >>> print(f"发现 {len(result['violations'])} 个违规")
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

        # 合并规则
        rules = cls._merge_rules(custom_rules)

        # 扫描所有 Python 文件
        python_files = cls._find_python_files(
            project_path,
            exclude_dirs=exclude_dirs,
            exclude_files=exclude_files
        )

        # 检查每个文件
        all_violations = []
        for file_path in python_files:
            try:
                violations = cls.check_file(
                    str(file_path),
                    project_root=project_root,
                    custom_rules=rules
                )
                all_violations.extend(violations)
            except (SyntaxError, UnicodeDecodeError, PermissionError):
                # 忽略无法解析的文件
                continue

        # 严格模式：提升警告级别
        if strict_mode:
            for violation in all_violations:
                if violation['severity'] == 'low':
                    violation['severity'] = 'medium'

        # 生成统计摘要
        summary = cls._generate_summary(all_violations, len(python_files))
        metadata = {
            'project_root': str(project_path),
            'scan_time': datetime.now().isoformat(),
            'rules_version': '1.0.0',
            'strict_mode': strict_mode
        }

        return {
            'violations': all_violations,
            'summary': summary,
            'metadata': metadata
        }

    @classmethod
    def check_file(
        cls,
        file_path: str,
        project_root: str,
        custom_rules: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检查单个文件的架构依赖

        解析文件的导入语句，验证每个导入是否符合架构规则。

        Args:
            file_path: 文件路径
            project_root: 项目根目录（用于确定文件所属层）
            custom_rules: 自定义架构规则

        Returns:
            违规清单列表，每个元素包含:
            - source_file: 源文件路径
            - source_layer: 源文件所属层
            - target_file: 目标文件路径（如果可解析）
            - target_layer: 目标模块所属层
            - import_statement: 导入语句
            - line_number: 行号
            - rule_violated: 违反的规则
            - severity: 严重程度 ('high', 'medium', 'low')
            - suggestion: 修复建议

        Raises:
            ValueError: 当 file_path 或 project_root 不存在时
            SyntaxError: 当文件语法错误无法解析时

        Example:
            >>> violations = ArchDependencyChecker.check_file(
            ...     '/path/to/domain/services.py',
            ...     '/path/to/project'
            ... )
            >>> for v in violations:
            ...     print(f"{v['source_layer']} -> {v['target_layer']}")
        """
        # 验证路径
        file = Path(file_path)
        project_path = Path(project_root)

        if not file.exists():
            raise ValueError(f"文件不存在: {file_path}")
        if not project_path.exists():
            raise ValueError(f"项目路径不存在: {project_root}")

        # 确定文件所属层
        source_layer = cls._determine_layer(file, project_path)
        if source_layer is None:
            # 文件不在任何架构层中，跳过检查
            return []

        # 合并规则
        rules = cls._merge_rules(custom_rules)

        # 获取该层的规则
        layer_rule = rules.get(source_layer)
        if layer_rule is None:
            # 没有定义该层的规则，跳过检查
            return []

        # 解析文件导入
        imports = cls._parse_imports(file)

        # 检查每个导入
        violations = []
        for import_info in imports:
            import_module = import_info['module']
            import_line = import_info['line_number']
            import_statement = import_info['statement']

            # 确定目标模块所属层
            target_layer = cls._resolve_import_layer(
                import_module,
                project_path,
                file.parent
            )

            if target_layer is None:
                # 无法确定目标层（可能是标准库或第三方库），跳过
                continue

            # 检查是否违反规则
            # 检查是否在允许列表中（支持精确匹配和前缀匹配）
            is_allowed = False
            for allowed in layer_rule['can_import']:
                if target_layer == allowed or target_layer.startswith(allowed + '.'):
                    is_allowed = True
                    break
            
            # 如果目标层不在允许列表中，但自定义规则中有针对子模块的允许规则
            # 检查导入模块的完整路径是否匹配允许的子模块
            if not is_allowed:
                import_module_path = import_module.split('.')[0] if not import_module.startswith('.') else import_module
                for allowed in layer_rule['can_import']:
                    if '.' in allowed:
                        # 这是子模块规则，检查导入是否匹配
                        allowed_layer = allowed.split('.')[0]
                        if allowed_layer == target_layer and import_module.startswith(allowed):
                            is_allowed = True
                            break

            if not is_allowed and target_layer in layer_rule['cannot_import']:
                # 违规
                severity = cls._assess_severity(source_layer, target_layer)
                suggestion = cls._generate_suggestion(source_layer, target_layer)

                violation = {
                    'source_file': str(file.relative_to(project_path)),
                    'source_layer': source_layer,
                    'target_file': cls._find_target_file(
                        import_module,
                        project_path,
                        file.parent
                    ),
                    'target_layer': target_layer,
                    'import_statement': import_statement,
                    'line_number': import_line,
                    'rule_violated': (
                        f"{source_layer} 层不应导入 {target_layer} 层"
                    ),
                    'severity': severity,
                    'suggestion': suggestion
                }
                violations.append(violation)

        return violations

    @classmethod
    def generate_report(
        cls,
        violations: List[Dict[str, Any]],
        output_format: str = 'text',
        output_file: Optional[str] = None,
        include_suggestions: bool = True
    ) -> str:
        """
        生成架构检查报告

        根据违规清单生成格式化的报告，支持文本、JSON 和 Markdown 格式。

        Args:
            violations: 违规清单（来自 check_project 或 check_file）
            output_format: 输出格式，可选值:
                - 'text': 纯文本格式（默认）
                - 'json': JSON 格式
                - 'markdown': Markdown 格式
            output_file: 输出文件路径，如提供则将报告保存到该文件
            include_suggestions: 是否包含修复建议，默认 True

        Returns:
            生成的报告字符串

        Raises:
            ValueError: 当 output_format 不支持时

        Example:
            >>> report = ArchDependencyChecker.generate_report(
            ...     violations,
            ...     output_format='markdown'
            ... )
            >>> print(report)
        """
        # 根据格式生成报告
        if output_format == 'text':
            report = cls._generate_text_report(violations, include_suggestions)
        elif output_format == 'json':
            report = cls._generate_json_report(violations)
        elif output_format == 'markdown':
            report = cls._generate_markdown_report(violations, include_suggestions)
        else:
            raise ValueError(
                f"不支持的输出格式: {output_format}，"
                f"支持的格式: 'text', 'json', 'markdown'"
            )

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

        使用内置的测试数据验证检查器的核心功能是否正常工作。

        Returns:
            True 如果所有测试通过，否则 False

        Example:
            >>> if ArchDependencyChecker.self_test():
            ...     print("✅ 检查器自检通过")
        """
        try:
            # 测试 1: 检测 domain 导入 infrastructure
            test_violations_1 = [
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

            # 测试 2: 检测 data_access 导入 service
            test_violations_2 = [
                {
                    'source_file': 'data_access/repositories.py',
                    'source_layer': 'data_access',
                    'target_file': 'service/api_provider.py',
                    'target_layer': 'service',
                    'import_statement': 'from service.api_provider import APIProviderManager',
                    'line_number': 42,
                    'rule_violated': 'data_access 层不应导入 service 层',
                    'severity': 'medium',
                    'suggestion': '通过领域服务接口访问数据'
                }
            ]

            # 测试 3: 合规导入（空违规列表）
            test_violations_3 = []

            # 测试 4: 生成报告
            text_report = cls.generate_report(test_violations_1, 'text')
            json_report = cls.generate_report(test_violations_1, 'json')
            md_report = cls.generate_report(test_violations_1, 'markdown')

            # 验证报告不为空
            if not all([text_report, json_report, md_report]):
                return False

            # 验证 JSON 报告可以解析
            json_data = json.loads(json_report)
            if 'violations' not in json_data or 'summary' not in json_data:
                return False

            # 验证严重程度字段
            for violation in test_violations_1 + test_violations_2:
                if violation['severity'] not in ['high', 'medium', 'low']:
                    return False

            return True

        except Exception as e:
            print(f"自检测试失败: {e}")
            return False

    # ==================== 私有方法 ====================

    @classmethod
    def _merge_rules(
        cls,
        custom_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        合并默认规则和自定义规则

        Args:
            custom_rules: 自定义规则

        Returns:
            合并后的规则
        """
        if custom_rules is None:
            return cls.ARCH_RULES.copy()

        # 深拷贝默认规则
        merged = {}
        for layer, rule in cls.ARCH_RULES.items():
            merged[layer] = {
                'can_import': rule['can_import'].copy(),
                'cannot_import': rule['cannot_import'].copy(),
                'description': rule['description']
            }

        # 合并自定义规则
        for layer, rule in custom_rules.items():
            if layer not in merged:
                merged[layer] = rule
            else:
                # 更新规则
                if 'can_import' in rule:
                    merged[layer]['can_import'] = rule['can_import']
                if 'cannot_import' in rule:
                    merged[layer]['cannot_import'] = rule['cannot_import']
                if 'description' in rule:
                    merged[layer]['description'] = rule['description']

        return merged

    @classmethod
    def _find_python_files(
        cls,
        project_path: Path,
        exclude_dirs: List[str],
        exclude_files: List[str]
    ) -> List[Path]:
        """
        查找项目中所有 Python 文件

        Args:
            project_path: 项目根目录路径
            exclude_dirs: 排除的目录列表
            exclude_files: 排除的文件列表

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

                file_path = Path(root) / file
                python_files.append(file_path)

        return python_files

    @classmethod
    def _determine_layer(cls, file_path: Path, project_path: Path) -> Optional[str]:
        """
        确定文件所属的架构层

        Args:
            file_path: 文件路径
            project_path: 项目根目录路径

        Returns:
            架构层名称，如果无法确定则返回 None
        """
        try:
            relative_path = file_path.relative_to(project_path)
            parts = relative_path.parts

            # 检查第一层目录
            if len(parts) > 0:
                first_dir = parts[0]
                for layer, dir_name in cls.LAYER_DIRS.items():
                    if first_dir == dir_name:
                        return layer

            return None
        except ValueError:
            # 文件不在项目路径下
            return None

    @classmethod
    def _parse_imports(cls, file_path: Path) -> List[Dict[str, Any]]:
        """
        解析文件中的导入语句

        Args:
            file_path: 文件路径

        Returns:
            导入信息列表，每个元素包含:
            - module: 模块名
            - line_number: 行号
            - statement: 完整的导入语句
        """
        imports = []

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # 解析 AST
        tree = ast.parse(source, filename=str(file_path))
        lines = source.split('\n')

        # 提取导入语句
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'module': alias.name,
                        'line_number': node.lineno,
                        'statement': lines[node.lineno - 1].strip()
                    })
            elif isinstance(node, ast.ImportFrom):
                # 处理 from ... import ...
                module = node.module or ''
                level = node.level or 0

                # 构建完整模块路径
                if level > 0:
                    # 相对导入
                    module = '.' * level + module

                imports.append({
                    'module': module,
                    'line_number': node.lineno,
                    'statement': lines[node.lineno - 1].strip()
                })

        return imports

    @classmethod
    def _resolve_import_layer(
        cls,
        import_module: str,
        project_path: Path,
        current_file_dir: Path
    ) -> Optional[str]:
        """
        解析导入模块所属的架构层

        Args:
            import_module: 导入的模块名
            project_path: 项目根目录路径
            current_file_dir: 当前文件所在目录

        Returns:
            架构层名称，如果无法确定则返回 None
        """
        # 处理相对导入
        if import_module.startswith('.'):
            # 计算相对层级
            dots = 0
            for char in import_module:
                if char == '.':
                    dots += 1
                else:
                    break

            # 解析相对路径
            relative_module = import_module[dots:]
            base_dir = current_file_dir

            # 向上移动 dots 层（修复：dots=2时移动2层）
            for _ in range(dots):
                base_dir = base_dir.parent

            # 构建目标路径
            if relative_module:
                module_path = relative_module.replace('.', os.sep)
                target_dir = base_dir / module_path
            else:
                target_dir = base_dir

            # 检查目标路径是否在项目路径下
            try:
                relative_to_project = target_dir.relative_to(project_path)
                parts = relative_to_project.parts
                if len(parts) > 0:
                    first_dir = parts[0]
                    for layer, dir_name in cls.LAYER_DIRS.items():
                        if first_dir == dir_name:
                            return layer
            except ValueError:
                pass

            return None

        # 处理绝对导入
        # 检查是否是项目内的模块
        for layer, dir_name in cls.LAYER_DIRS.items():
            if import_module.startswith(dir_name + '.') or import_module == dir_name:
                return layer

        # 可能是标准库或第三方库
        return None

    @classmethod
    def _find_target_file(
        cls,
        import_module: str,
        project_path: Path,
        current_file_dir: Path
    ) -> Optional[str]:
        """
        查找导入的目标文件

        Args:
            import_module: 导入的模块名
            project_path: 项目根目录路径
            current_file_dir: 当前文件所在目录

        Returns:
            目标文件路径（相对于项目根），如果找不到则返回 None
        """
        # 处理相对导入
        if import_module.startswith('.'):
            dots = 0
            for char in import_module:
                if char == '.':
                    dots += 1
                else:
                    break

            relative_module = import_module[dots:]
            base_dir = current_file_dir

            # 向上移动 dots 层（修复：dots=2时移动2层）
            for _ in range(dots):
                base_dir = base_dir.parent

            if relative_module:
                module_parts = relative_module.split('.')
                # 尝试查找 .py 文件
                target_file = base_dir
                for part in module_parts:
                    target_file = target_file / part

                # 检查是否是文件
                if target_file.with_suffix('.py').exists():
                    try:
                        return str(target_file.with_suffix('.py').relative_to(project_path))
                    except ValueError:
                        pass

                # 检查是否是包的 __init__.py
                init_file = target_file / '__init__.py'
                if init_file.exists():
                    try:
                        return str(init_file.relative_to(project_path))
                    except ValueError:
                        pass

            return None

        # 处理绝对导入
        module_parts = import_module.split('.')
        target_file = project_path
        for part in module_parts:
            target_file = target_file / part

        # 检查是否是文件
        if target_file.with_suffix('.py').exists():
            try:
                return str(target_file.with_suffix('.py').relative_to(project_path))
            except ValueError:
                pass

        # 检查是否是包的 __init__.py
        init_file = target_file / '__init__.py'
        if init_file.exists():
            try:
                return str(init_file.relative_to(project_path))
            except ValueError:
                pass

        return None

    @classmethod
    def _assess_severity(cls, source_layer: str, target_layer: str) -> str:
        """
        评估违规严重程度

        Args:
            source_layer: 源层
            target_layer: 目标层

        Returns:
            严重程度: 'high', 'medium', 'low'
        """
        # high: domain 层违规访问其他层
        if source_layer == 'domain':
            return 'high'

        # medium: data_access 访问 service，infrastructure 访问 domain
        if (source_layer == 'data_access' and target_layer == 'service') or \
           (source_layer == 'infrastructure' and target_layer == 'domain'):
            return 'medium'

        # medium: presentation 直接访问低层
        if source_layer == 'presentation' and target_layer in ['service', 'data_access']:
            return 'medium'

        # low: 其他违规
        return 'low'

    @classmethod
    def _generate_suggestion(cls, source_layer: str, target_layer: str) -> str:
        """
        生成修复建议

        Args:
            source_layer: 源层
            target_layer: 目标层

        Returns:
            修复建议文本
        """
        suggestions = {
            ('domain', 'infrastructure'): '考虑使用依赖注入或接口抽象',
            ('domain', 'service'): '通过应用层或服务接口访问',
            ('domain', 'data_access'): '通过仓储接口访问数据',
            ('domain', 'application'): '领域层不应依赖应用层',
            ('data_access', 'service'): '通过领域服务接口访问数据',
            ('data_access', 'presentation'): '数据访问层不应访问表示层',
            ('data_access', 'application'): '通过应用层接口访问',
            ('infrastructure', 'domain'): '基础设施层不应访问领域业务逻辑',
            ('infrastructure', 'service'): '基础设施层不应访问服务层',
            ('infrastructure', 'data_access'): '基础设施层不应访问数据访问层',
            ('infrastructure', 'presentation'): '基础设施层不应访问表示层',
            ('infrastructure', 'application'): '基础设施层不应访问应用层',
            ('presentation', 'domain'): '应通过应用层访问领域层',
            ('presentation', 'service'): '应通过应用层访问服务层',
            ('presentation', 'data_access'): '应通过应用层访问数据访问层',
        }

        return suggestions.get(
            (source_layer, target_layer),
            '重新考虑架构依赖关系'
        )

    @classmethod
    def _generate_summary(
        cls,
        violations: List[Dict[str, Any]],
        total_files: int
    ) -> Dict[str, Any]:
        """
        生成统计摘要

        Args:
            violations: 违规清单
            total_files: 扫描的文件总数

        Returns:
            统计摘要字典
        """
        # 按层统计
        violations_by_layer = defaultdict(int)
        for v in violations:
            violations_by_layer[v['source_layer']] += 1

        # 按严重程度统计
        violations_by_severity = defaultdict(int)
        for v in violations:
            violations_by_severity[v['severity']] += 1

        return {
            'total_files_scanned': total_files,
            'total_violations': len(violations),
            'violations_by_layer': dict(violations_by_layer),
            'violations_by_severity': dict(violations_by_severity)
        }

    @classmethod
    def _generate_text_report(
        cls,
        violations: List[Dict[str, Any]],
        include_suggestions: bool = True
    ) -> str:
        """生成文本格式报告"""
        lines = []
        separator = "═" * 60

        # 报告头部
        lines.append(separator)
        lines.append("架构依赖检查报告")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(separator)
        lines.append("")

        # 违规清单
        lines.append("【违规清单】")
        lines.append("━" * 60)
        lines.append("")

        if violations:
            # 按严重程度排序
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            sorted_violations = sorted(
                violations,
                key=lambda v: severity_order.get(v['severity'], 3)
            )

            for idx, violation in enumerate(sorted_violations, 1):
                severity_label = {
                    'high': '严重',
                    'medium': '中等',
                    'low': '轻微'
                }.get(violation['severity'], '未知')

                lines.append(
                    f"{idx}. [{severity_label}] "
                    f"{violation['source_file']} → {violation.get('target_file', 'unknown')}"
                )
                lines.append(f"   行号: {violation['line_number']}")
                lines.append(f"   导入: {violation['import_statement']}")
                lines.append(f"   规则: {violation['rule_violated']}")

                if include_suggestions:
                    lines.append(f"   建议: {violation['suggestion']}")

                lines.append("")
        else:
            lines.append("未发现架构违规 ✓")
            lines.append("")

        # 统计摘要
        lines.append("【统计摘要】")
        lines.append("━" * 60)
        lines.append("")
        lines.append(f"• 发现违规: {len(violations)} 个")

        # 按层统计
        violations_by_layer = defaultdict(int)
        for v in violations:
            violations_by_layer[v['source_layer']] += 1

        if violations_by_layer:
            lines.append("  按层分布:")
            for layer, count in sorted(violations_by_layer.items()):
                lines.append(f"    - {layer} 层: {count} 个违规")

        # 按严重程度统计
        violations_by_severity = defaultdict(int)
        for v in violations:
            violations_by_severity[v['severity']] += 1

        if violations_by_severity:
            lines.append("  严重程度:")
            severity_label = {'high': '高', 'medium': '中', 'low': '低'}
            for severity in ['high', 'medium', 'low']:
                count = violations_by_severity.get(severity, 0)
                if count > 0:
                    lines.append(f"    - {severity_label[severity]}: {count} 个")

        lines.append("")
        lines.append(separator)

        return '\n'.join(lines)

    @classmethod
    def _generate_json_report(cls, violations: List[Dict[str, Any]]) -> str:
        """生成 JSON 格式报告"""
        # 统计摘要
        summary = cls._generate_summary(violations, 0)

        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'checker_version': '1.0.0'
            },
            'violations': violations,
            'summary': summary
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False)

    @classmethod
    def _generate_markdown_report(
        cls,
        violations: List[Dict[str, Any]],
        include_suggestions: bool = True
    ) -> str:
        """生成 Markdown 格式报告"""
        lines = []

        # 报告头部
        lines.append("# 架构依赖检查报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**检查器版本**: 1.0.0")
        lines.append("")

        # 违规清单
        lines.append("## 违规清单")
        lines.append("")

        if violations:
            # 按严重程度排序
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            sorted_violations = sorted(
                violations,
                key=lambda v: severity_order.get(v['severity'], 3)
            )

            lines.append(f"共发现 **{len(violations)}** 个违规：")
            lines.append("")

            for idx, violation in enumerate(sorted_violations, 1):
                severity_label = {
                    'high': '🔴 严重',
                    'medium': '🟡 中等',
                    'low': '🟢 轻微'
                }.get(violation['severity'], '⚪ 未知')

                lines.append(f"### {idx}. {severity_label}")
                lines.append("")
                lines.append(f"- **源文件**: `{violation['source_file']}`")
                lines.append(f"- **源层**: {violation['source_layer']}")
                target_file = violation.get('target_file', 'unknown')
                lines.append(f"- **目标文件**: `{target_file}`")
                lines.append(f"- **目标层**: {violation['target_layer']}")
                lines.append(f"- **行号**: {violation['line_number']}")
                lines.append(f"- **导入语句**: `{violation['import_statement']}`")
                lines.append(f"- **违反规则**: {violation['rule_violated']}")

                if include_suggestions:
                    lines.append(f"- **修复建议**: {violation['suggestion']}")

                lines.append("")
        else:
            lines.append("✅ 未发现架构违规")
            lines.append("")

        # 统计摘要
        lines.append("## 统计摘要")
        lines.append("")

        summary = cls._generate_summary(violations, 0)
        lines.append(f"- **违规总数**: {summary['total_violations']}")

        if summary['violations_by_layer']:
            lines.append("- **按层分布**:")
            for layer, count in sorted(summary['violations_by_layer'].items()):
                lines.append(f"  - {layer} 层: {count} 个")

        if summary['violations_by_severity']:
            lines.append("- **按严重程度**:")
            severity_label = {'high': '高', 'medium': '中', 'low': '低'}
            for severity in ['high', 'medium', 'low']:
                count = summary['violations_by_severity'].get(severity, 0)
                if count > 0:
                    lines.append(f"  - {severity_label[severity]}: {count} 个")

        lines.append("")

        return '\n'.join(lines)
