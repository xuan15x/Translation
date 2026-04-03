"""
代码重复扫描器 (Code Dedup Scanner)

自动扫描 Python 项目中的重复类和相似文件。

使用示例:
    >>> import sys
    >>> sys.path.insert(0, '/path/to/project')
    >>> from .qwen.skills.code_dedup_scanner import CodeDedupScanner
    >>>
    >>> # 扫描重复类
    >>> duplicates = CodeDedupScanner.scan_duplicate_classes('/path/to/project')
    >>>
    >>> # 扫描相似文件
    >>> similar_files = CodeDedupScanner.scan_duplicate_files('/path/to/project')
    >>>
    >>> # 生成报告
    >>> report = CodeDedupScanner.generate_report(duplicates, similar_files)
    >>> print(report)

版本: 1.0.0
创建日期: 2026-04-03
"""

from .scanner import CodeDedupScanner

__all__ = ['CodeDedupScanner']
__version__ = '1.0.0'
__author__ = 'Qwen Code'
__description__ = '代码重复扫描器 - 检测重复类和相似文件'
