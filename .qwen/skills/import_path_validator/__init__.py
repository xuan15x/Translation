"""
导入路径验证器 (Import Path Validator)

验证 Python 项目的导入路径规范性,检测以下问题:
- 同一类/函数从多个路径导入(重复导入)
- 模块间的循环导入依赖
- __init__.py 导出与实际定义不一致

使用示例:
    >>> import sys
    >>> sys.path.insert(0, '/path/to/project')
    >>> from .qwen.skills.import_path_validator import ImportPathValidator
    >>>
    >>> # 验证整个项目
    >>> result = ImportPathValidator.validate_project("/path/to/project")
    >>>
    >>> # 验证单个文件
    >>> issues = ImportPathValidator.validate_file("module.py")
    >>>
    >>> # 生成报告
    >>> report = ImportPathValidator.generate_report(result)
    >>> print(report)
    >>>
    >>> # 自检测试
    >>> if ImportPathValidator.self_test():
    ...     print("✅ 验证器正常")

版本: 1.0.0
创建日期: 2026-04-03
"""

from .validator import ImportPathValidator

__all__ = ['ImportPathValidator']
__version__ = '1.0.0'
__author__ = 'Qwen Code'
__description__ = '导入路径验证器 - 检测重复导入、循环导入、__init__.py 导出一致性'
