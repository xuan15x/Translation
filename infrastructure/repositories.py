"""
仓储层/数据访问接口
定义数据访问的抽象接口，隔离业务逻辑与具体实现

注意：为了避免循环导入，接口定义已移至 domain.services。
此处使用 TYPE_CHECKING 进行类型检查时的导入，运行时不导入。
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.services import ITermRepository

# 定义 __all__ 以便外部可以访问
__all__ = []

# 延迟访问支持
def __getattr__(name):
    if name == 'ITermRepository':
        from domain.services import ITermRepository
        return ITermRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
