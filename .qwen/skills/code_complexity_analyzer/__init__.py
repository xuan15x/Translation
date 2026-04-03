"""
代码复杂度分析器 (Code Complexity Analyzer)

分析 Python 项目的代码复杂度,包括圈复杂度、认知复杂度、函数/类大小等指标。

使用示例:
    >>> import sys
    >>> sys.path.insert(0, '/path/to/project')
    >>> from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer
    >>>
    >>> # 分析单个文件
    >>> result = CodeComplexityAnalyzer.analyze_file("module.py")
    >>>
    >>> # 分析整个项目
    >>> project_result = CodeComplexityAnalyzer.analyze_project("/path/to/project")
    >>>
    >>> # 生成报告
    >>> report = CodeComplexityAnalyzer.generate_report(project_result)
    >>> print(report)
    >>>
    >>> # 自检测试
    >>> if CodeComplexityAnalyzer.self_test():
    ...     print("✅ 分析器正常")

版本: 1.0.0
创建日期: 2026-04-03
"""

from .analyzer import CodeComplexityAnalyzer

__all__ = ['CodeComplexityAnalyzer']
__version__ = '1.0.0'
__author__ = 'Qwen Code'
__description__ = '代码复杂度分析器 - 分析圈复杂度、认知复杂度、函数/类大小'
