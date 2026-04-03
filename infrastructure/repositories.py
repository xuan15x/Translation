"""
仓储层/数据访问接口
定义数据访问的抽象接口，隔离业务逻辑与具体实现

注意：接口定义已移至 domain.services，此处仅为向后兼容的重新导出
"""
# 从领域层导入接口（避免循环导入）
from domain.services import ITermRepository

__all__ = ['ITermRepository']
