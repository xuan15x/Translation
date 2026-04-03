"""
架构依赖检查器 (Arch Dependency Checker)

验证分层架构依赖规则，检测违反架构的导入。

使用示例:
    >>> import sys
    >>> sys.path.insert(0, '/path/to/project')
    >>> from .qwen.skills.arch_dependency_checker import ArchDependencyChecker
    >>>
    >>> # 检查整个项目
    >>> violations = ArchDependencyChecker.check_project('/path/to/project')
    >>>
    >>> # 生成报告
    >>> report = ArchDependencyChecker.generate_report(violations)
    >>> print(report)

版本: 1.0.0
创建日期: 2026-04-03
"""

from .checker import ArchDependencyChecker

__all__ = ['ArchDependencyChecker']
__version__ = '1.0.0'
__author__ = 'Qwen Code'
__description__ = '架构依赖检查器 - 验证分层架构规则'
