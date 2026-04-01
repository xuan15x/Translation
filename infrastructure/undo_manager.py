"""
撤销/重做管理器
实现操作历史的追踪和恢复功能
"""
import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """操作类型枚举"""
    TERM_ADD = "term_add"
    TERM_UPDATE = "term_update"
    TERM_DELETE = "term_delete"
    BATCH_IMPORT = "batch_import"
    CONFIG_CHANGE = "config_change"
    TRANSLATION_ADD = "translation_add"
    TRANSLATION_UPDATE = "translation_update"


@dataclass
class Operation:
    """操作记录"""
    id: int
    type: OperationType
    timestamp: float
    description: str
    old_value: Any
    new_value: Any
    metadata: Dict = field(default_factory=dict)
    undone: bool = False
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'type': self.type.value,
            'timestamp': self.timestamp,
            'description': self.description,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'metadata': self.metadata,
            'undone': self.undone
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Operation':
        """从字典创建"""
        return cls(
            id=data['id'],
            type=OperationType(data['type']),
            timestamp=data['timestamp'],
            description=data['description'],
            old_value=data['old_value'],
            new_value=data['new_value'],
            metadata=data.get('metadata', {}),
            undone=data.get('undone', False)
        )


class UndoManager:
    """撤销/重做管理器"""
    
    def __init__(self, max_history: int = 100):
        """
        初始化撤销管理器
        
        Args:
            max_history: 最大历史记录数量
        """
        self.max_history = max_history
        self.history: List[Operation] = []
        self.redo_stack: List[Operation] = []
        self.lock = asyncio.Lock()
        self.operation_counter = 0
        
        # 回调函数
        self.on_operation_added: Optional[Callable[[Operation], None]] = None
        self.on_undo: Optional[Callable[[Operation], None]] = None
        self.on_redo: Optional[Callable[[Operation], None]] = None
        
        # 统计信息
        self.stats = {
            'total_operations': 0,
            'undo_count': 0,
            'redo_count': 0,
            'auto_cleaned': 0
        }
    
    async def record(
        self,
        operation_type: OperationType,
        old_value: Any,
        new_value: Any,
        description: str = "",
        metadata: Dict = None
    ):
        """
        记录新操作
        
        Args:
            operation_type: 操作类型
            old_value: 操作前的值
            new_value: 操作后的值
            description: 操作描述
            metadata: 附加元数据
        """
        async with self.lock:
            self.operation_counter += 1
            
            op = Operation(
                id=self.operation_counter,
                type=operation_type,
                timestamp=time.time(),
                description=description or f"{operation_type.value}",
                old_value=old_value,
                new_value=new_value,
                metadata=metadata or {}
            )
            
            self.history.append(op)
            self.redo_stack.clear()  # 新操作后清空重做栈
            
            # 限制历史记录数量
            if len(self.history) > self.max_history:
                removed = self.history.pop(0)
                self.stats['auto_cleaned'] += 1
                logger.debug(f"自动清理旧操作记录：{removed.id}")
            
            self.stats['total_operations'] += 1
            
            logger.info(f"记录操作：{op.id} - {op.type.value} - {op.description}")
            
            # 触发回调
            if self.on_operation_added:
                await self._safe_callback(self.on_operation_added, op)
    
    async def undo(self) -> Optional[Operation]:
        """
        撤销最近的操作
        
        Returns:
            被撤销的操作，如果没有可撤销的操作则返回 None
        """
        async with self.lock:
            # 找到最后一个未撤销的操作
            for op in reversed(self.history):
                if not op.undone:
                    op.undone = True
                    self.redo_stack.append(op)
                    self.stats['undo_count'] += 1
                    
                    logger.info(f"撤销操作：{op.id} - {op.type.value}")
                    
                    # 触发回调
                    if self.on_undo:
                        await self._safe_callback(self.on_undo, op)
                    
                    return op
            
            logger.warning("没有可撤销的操作")
            return None
    
    async def redo(self) -> Optional[Operation]:
        """
        重做最近撤销的操作
        
        Returns:
            被重做的操作，如果没有可重做的操作则返回 None
        """
        async with self.lock:
            if not self.redo_stack:
                logger.warning("没有可重做的操作")
                return None
            
            op = self.redo_stack.pop()
            op.undone = False
            self.stats['redo_count'] += 1
            
            logger.info(f"重做操作：{op.id} - {op.type.value}")
            
            # 触发回调
            if self.on_redo:
                await self._safe_callback(self.on_redo, op)
            
            return op
    
    async def undo_multiple(self, count: int = 1) -> List[Operation]:
        """
        批量撤销多个操作
        
        Args:
            count: 要撤销的操作数量
            
        Returns:
            被撤销的操作列表
        """
        undone_ops = []
        
        for _ in range(count):
            op = await self.undo()
            if op:
                undone_ops.append(op)
            else:
                break
        
        return undone_ops
    
    async def redo_multiple(self, count: int = 1) -> List[Operation]:
        """
        批量重做多个操作
        
        Args:
            count: 要重做的操作数量
            
        Returns:
            被重做的操作列表
        """
        redone_ops = []
        
        for _ in range(count):
            op = await self.redo()
            if op:
                redone_ops.append(op)
            else:
                break
        
        return redone_ops
    
    def can_undo(self) -> bool:
        """检查是否有可撤销的操作"""
        return any(not op.undone for op in reversed(self.history))
    
    def can_redo(self) -> bool:
        """检查是否有可重做的操作"""
        return len(self.redo_stack) > 0
    
    def get_recent_operations(self, limit: int = 10) -> List[Operation]:
        """获取最近的 N 个操作"""
        return list(reversed(self.history[:limit]))
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'history_size': len(self.history),
            'redo_stack_size': len(self.redo_stack),
            'can_undo': self.can_undo(),
            'can_redo': self.can_redo()
        }
    
    async def clear(self):
        """清空所有历史记录"""
        async with self.lock:
            self.history.clear()
            self.redo_stack.clear()
            self.operation_counter = 0
            logger.info("已清空所有操作历史")
    
    async def _safe_callback(self, callback: Callable, *args):
        """安全地调用回调函数"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"回调函数执行失败：{e}")
    
    async def export_history(self, format: str = 'json') -> str:
        """
        导出操作历史
        
        Args:
            format: 导出格式（json/csv）
            
        Returns:
            导出的数据字符串
        """
        import json
        
        if format == 'json':
            data = [op.to_dict() for op in self.history]
            return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的导出格式：{format}")


# 全局撤销管理器实例
_global_undo_manager: Optional[UndoManager] = None


def get_undo_manager(max_history: int = 100) -> UndoManager:
    """获取全局撤销管理器实例"""
    global _global_undo_manager
    if _global_undo_manager is None:
        _global_undo_manager = UndoManager(max_history=max_history)
    return _global_undo_manager


async def record_operation(
    operation_type: OperationType,
    old_value: Any,
    new_value: Any,
    description: str = "",
    metadata: Dict = None
):
    """记录操作到全局撤销管理器"""
    manager = get_undo_manager()
    await manager.record(operation_type, old_value, new_value, description, metadata)


async def undo_last_operation() -> Optional[Operation]:
    """撤销最后一个操作"""
    manager = get_undo_manager()
    return await manager.undo()


async def redo_last_operation() -> Optional[Operation]:
    """重做最后一个撤销的操作"""
    manager = get_undo_manager()
    return await manager.redo()
