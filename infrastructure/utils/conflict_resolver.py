"""
冲突检测和解决模块
检测并解决术语库并发修改冲突
"""
import asyncio
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """冲突类型"""
    CONCURRENT_EDIT = "concurrent_edit"  # 并发编辑同一术语
    DUPLICATE_ADD = "duplicate_add"      # 重复添加
    VERSION_MISMATCH = "version_mismatch"  # 版本不匹配
    DATA_INCONSISTENCY = "data_inconsistency"  # 数据不一致


class ResolutionStrategy(Enum):
    """解决策略"""
    LAST_WRITE_WINS = "last_write_wins"    # 最后写入获胜
    FIRST_WRITE_WINS = "first_write_wins"  # 最先写入获胜
    MANUAL_REVIEW = "manual_review"        # 人工审核
    MERGE_CHANGES = "merge_changes"        # 合并变更
    KEEP_NEWER = "keep_newer"              # 保留更新的
    KEEP_EXISTING = "keep_existing"        # 保留现有的


@dataclass
class ConflictRecord:
    """冲突记录"""
    id: int
    conflict_type: ConflictType
    timestamp: float
    source_text: str
    language: str
    existing_value: Any
    incoming_value: Any
    resolution_strategy: ResolutionStrategy
    resolved: bool = False
    resolution_result: Optional[Any] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'conflict_type': self.conflict_type.value,
            'timestamp': self.timestamp,
            'source_text': self.source_text,
            'language': self.language,
            'existing_value': self.existing_value,
            'incoming_value': self.incoming_value,
            'resolution_strategy': self.resolution_strategy.value,
            'resolved': self.resolved,
            'resolution_result': self.resolution_result,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConflictRecord':
        """从字典创建"""
        return cls(
            id=data['id'],
            conflict_type=ConflictType(data['conflict_type']),
            timestamp=data['timestamp'],
            source_text=data['source_text'],
            language=data['language'],
            existing_value=data['existing_value'],
            incoming_value=data['incoming_value'],
            resolution_strategy=ResolutionStrategy(data['resolution_strategy']),
            resolved=data.get('resolved', False),
            resolution_result=data.get('resolution_result'),
            metadata=data.get('metadata', {})
        )


class ConflictDetector:
    """冲突检测器"""
    
    def __init__(self):
        """初始化冲突检测器"""
        self.pending_operations: Dict[str, Dict] = {}  # 正在执行的操作
        self.term_checksums: Dict[str, str] = {}  # 术语校验和
        self.lock = asyncio.Lock()
        self.conflict_counter = 0
    
    def _make_operation_key(self, source_text: str, language: str) -> str:
        """生成操作键"""
        return f"{source_text}:{language}"
    
    def _calculate_checksum(self, data: Dict) -> str:
        """计算数据校验和"""
        data_str = str(sorted(data.items()))
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def check_conflict(
        self,
        source_text: str,
        language: str,
        new_value: Any,
        current_db_state: Dict
    ) -> Optional[ConflictType]:
        """
        检查是否存在冲突
        
        Args:
            source_text: 源文本
            language: 目标语言
            new_value: 新值
            current_db_state: 当前数据库状态
            
        Returns:
            冲突类型，如果没有冲突则返回 None
        """
        async with self.lock:
            op_key = self._make_operation_key(source_text, language)
            
            # 1. 检测并发编辑冲突
            if op_key in self.pending_operations:
                logger.debug(f"检测到并发编辑冲突：{op_key}")
                return ConflictType.CONCURRENT_EDIT
            
            # 2. 检测数据不一致
            if source_text in current_db_state:
                existing = current_db_state[source_text]
                if language in existing:
                    old_checksum = self.term_checksums.get(op_key)
                    current_checksum = self._calculate_checksum({language: existing[language]})
                    
                    if old_checksum and old_checksum != current_checksum:
                        logger.debug(f"检测到版本不匹配：{op_key}")
                        return ConflictType.VERSION_MISMATCH
            
            # 3. 检测重复添加
            if (source_text in current_db_state and 
                language in current_db_state[source_text]):
                existing_value = current_db_state[source_text][language]
                if existing_value == new_value:
                    logger.debug(f"检测到重复添加：{op_key}")
                    return ConflictType.DUPLICATE_ADD
            
            return None
    
    async def register_operation(
        self,
        source_text: str,
        language: str,
        operation_data: Dict
    ):
        """注册正在进行的操作"""
        async with self.lock:
            op_key = self._make_operation_key(source_text, language)
            self.pending_operations[op_key] = {
                'data': operation_data,
                'start_time': time.time()
            }
            
            # 更新校验和
            if source_text in operation_data:
                self.term_checksums[op_key] = self._calculate_checksum(
                    operation_data[source_text]
                )
    
    async def complete_operation(self, source_text: str, language: str):
        """完成操作"""
        async with self.lock:
            op_key = self._make_operation_key(source_text, language)
            self.pending_operations.pop(op_key, None)
    
    async def get_conflicts_count(self) -> int:
        """获取冲突数量"""
        return self.conflict_counter


class ConflictResolver:
    """冲突解决器"""
    
    def __init__(self, default_strategy: ResolutionStrategy = ResolutionStrategy.LAST_WRITE_WINS):
        """
        初始化冲突解决器
        
        Args:
            default_strategy: 默认解决策略
        """
        self.default_strategy = default_strategy
        self.conflict_history: List[ConflictRecord] = []
        self.conflict_counter = 0
        self.lock = asyncio.Lock()
        
        # 统计信息
        self.stats = {
            'total_conflicts': 0,
            'resolved_conflicts': 0,
            'pending_conflicts': 0,
            'by_type': {},
            'by_strategy': {}
        }
    
    async def resolve_conflict(
        self,
        conflict_type: ConflictType,
        source_text: str,
        language: str,
        existing_value: Any,
        incoming_value: Any,
        strategy: Optional[ResolutionStrategy] = None
    ) -> Tuple[bool, Any]:
        """
        解决冲突
        
        Args:
            conflict_type: 冲突类型
            source_text: 源文本
            language: 目标语言
            existing_value: 现有值
            incoming_value: 传入值
            strategy: 解决策略（可选）
            
        Returns:
            (是否成功解决，解决结果)
        """
        async with self.lock:
            self.conflict_counter += 1
            self.stats['total_conflicts'] += 1
            self.stats['pending_conflicts'] += 1
            
            # 使用默认策略
            if strategy is None:
                strategy = self.default_strategy
            
            # 创建冲突记录
            record = ConflictRecord(
                id=self.conflict_counter,
                conflict_type=conflict_type,
                timestamp=time.time(),
                source_text=source_text,
                language=language,
                existing_value=existing_value,
                incoming_value=incoming_value,
                resolution_strategy=strategy
            )
            
            # 根据策略解决冲突
            result = await self._apply_strategy(
                conflict_type, existing_value, incoming_value, strategy
            )
            
            if result is not None:
                record.resolved = True
                record.resolution_result = result
                self.stats['resolved_conflicts'] += 1
                self.stats['pending_conflicts'] -= 1
                
                # 更新统计
                type_key = conflict_type.value
                strategy_key = strategy.value
                self.stats['by_type'][type_key] = self.stats['by_type'].get(type_key, 0) + 1
                self.stats['by_strategy'][strategy_key] = self.stats['by_strategy'].get(strategy_key, 0) + 1
            
            self.conflict_history.append(record)
            
            logger.info(
                f"解决冲突 #{self.conflict_counter}: {conflict_type.value} - "
                f"{source_text}:{language} -> {strategy.value}"
            )
            
            return record.resolved, result
    
    async def _apply_strategy(
        self,
        conflict_type: ConflictType,
        existing_value: Any,
        incoming_value: Any,
        strategy: ResolutionStrategy
    ) -> Optional[Any]:
        """应用解决策略"""
        
        if strategy == ResolutionStrategy.LAST_WRITE_WINS:
            # 最后写入获胜（总是接受新值）
            return incoming_value
        
        elif strategy == ResolutionStrategy.FIRST_WRITE_WINS:
            # 最先写入获胜（保留旧值）
            return existing_value
        
        elif strategy == ResolutionStrategy.KEEP_NEWER:
            # 保留更新的（基于时间戳比较）
            # 这里简化处理，假设 incoming 是更新的
            return incoming_value
        
        elif strategy == ResolutionStrategy.KEEP_EXISTING:
            # 保留现有的
            return existing_value
        
        elif strategy == ResolutionStrategy.MERGE_CHANGES:
            # 合并变更（适用于字典等可合并的数据）
            if isinstance(existing_value, dict) and isinstance(incoming_value, dict):
                merged = {**existing_value, **incoming_value}
                return merged
            else:
                # 无法合并，回退到最后写入获胜
                return incoming_value
        
        elif strategy == ResolutionStrategy.MANUAL_REVIEW:
            # 需要人工审核，返回 None 表示未解决
            logger.warning(f"冲突需要人工审核：{conflict_type.value} - {existing_value} vs {incoming_value}")
            return None
        
        return None
    
    async def get_unresolved_conflicts(self) -> List[ConflictRecord]:
        """获取未解决的冲突"""
        async with self.lock:
            return [r for r in self.conflict_history if not r.resolved]
    
    async def get_stats(self) -> Dict:
        """获取统计信息"""
        async with self.lock:
            return {
                **self.stats,
                'unresolved_count': len(await self.get_unresolved_conflicts()),
                'history_size': len(self.conflict_history)
            }
    
    async def clear_history(self, keep_recent: int = 100):
        """清理历史记录（保留最近的记录）"""
        async with self.lock:
            if len(self.conflict_history) > keep_recent:
                self.conflict_history = self.conflict_history[-keep_recent:]
                logger.info(f"已清理冲突历史记录，保留最近 {keep_recent} 条")


class TerminologyConflictManager:
    """术语库冲突管理器（整合检测和解决）"""
    
    def __init__(self, default_strategy: ResolutionStrategy = ResolutionStrategy.LAST_WRITE_WINS):
        """
        初始化冲突管理器
        
        Args:
            default_strategy: 默认解决策略
        """
        self.detector = ConflictDetector()
        self.resolver = ConflictResolver(default_strategy)
        self.db_state_cache: Dict = {}  # 数据库状态缓存
        self.lock = asyncio.Lock()
    
    async def update_db_state(self, db_state: Dict):
        """更新数据库状态缓存"""
        async with self.lock:
            self.db_state_cache = db_state.copy()
    
    async def try_add_term(
        self,
        source_text: str,
        language: str,
        translation: str,
        auto_resolve: bool = True
    ) -> Tuple[bool, Optional[str], Any]:
        """
        尝试添加术语（带冲突检测）
        
        Args:
            source_text: 源文本
            language: 目标语言
            translation: 翻译
            auto_resolve: 是否自动解决冲突
            
        Returns:
            (是否成功，冲突原因，最终值)
        """
        async with self.lock:
            # 1. 检测冲突
            conflict_type = await self.detector.check_conflict(
                source_text, language, translation, self.db_state_cache
            )
            
            if conflict_type:
                if not auto_resolve:
                    return False, f"检测到冲突：{conflict_type.value}", None
                
                # 尝试自动解决
                existing = self.db_state_cache.get(source_text, {}).get(language, "")
                success, result = await self.resolver.resolve_conflict(
                    conflict_type, source_text, language, existing, translation
                )
                
                if not success:
                    return False, "冲突解决失败", None
                
                # 使用解决后的值
                translation = result
            
            # 2. 注册操作
            await self.detector.register_operation(
                source_text, language,
                {source_text: {language: translation}}
            )
            
            try:
                # 3. 执行添加（由调用者实际写入数据库）
                return True, None, translation
            finally:
                # 4. 完成操作
                await self.detector.complete_operation(source_text, language)
    
    async def get_conflict_stats(self) -> Dict:
        """获取冲突统计"""
        detector_count = await self.detector.get_conflicts_count()
        resolver_stats = await self.resolver.get_stats()
        
        return {
            'detected_conflicts': detector_count,
            **resolver_stats
        }
    
    async def set_resolution_strategy(self, strategy: ResolutionStrategy):
        """设置解决策略"""
        self.resolver.default_strategy = strategy
        logger.info(f"冲突解决策略已更新：{strategy.value}")


# 全局单例
_global_conflict_manager: Optional[TerminologyConflictManager] = None


def get_conflict_manager(
    default_strategy: ResolutionStrategy = ResolutionStrategy.LAST_WRITE_WINS
) -> TerminologyConflictManager:
    """获取全局冲突管理器实例"""
    global _global_conflict_manager
    if _global_conflict_manager is None:
        _global_conflict_manager = TerminologyConflictManager(default_strategy)
    return _global_conflict_manager


async def check_and_resolve_conflict(
    source_text: str,
    language: str,
    new_value: Any,
    existing_value: Any,
    strategy: Optional[ResolutionStrategy] = None
) -> Tuple[bool, Any]:
    """
    检查并解决冲突的便捷函数
    
    Args:
        source_text: 源文本
        language: 目标语言
        new_value: 新值
        existing_value: 现有值
        strategy: 解决策略
        
    Returns:
        (是否成功解决，解决结果)
    """
    manager = get_conflict_manager()
    
    # 检测冲突
    conflict_type = await manager.detector.check_conflict(
        source_text, language, new_value, manager.db_state_cache
    )
    
    if not conflict_type:
        return True, new_value  # 无冲突，直接返回
    
    # 解决冲突
    return await manager.resolver.resolve_conflict(
        conflict_type, source_text, language, existing_value, new_value, strategy
    )
