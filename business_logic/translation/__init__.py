"""
翻译工作流接口
定义翻译流程的抽象接口
"""
from abc import ABC, abstractmethod
from typing import Optional
from infrastructure.models import FinalResult, TaskContext


class ITranslationWorkflow(ABC):
    """翻译工作流接口"""
    
    @abstractmethod
    async def execute(self, ctx: TaskContext) -> FinalResult:
        """
        执行翻译任务
        
        Args:
            ctx: 任务上下文
            
        Returns:
            最终翻译结果
        """
        pass


class ITaskProcessor(ABC):
    """任务处理器接口"""
    
    @abstractmethod
    async def process(self, ctx: TaskContext) -> FinalResult:
        """
        处理单个任务
        
        Args:
            ctx: 任务上下文
            
        Returns:
            处理结果
        """
        pass


class IStageExecutor(ABC):
    """阶段执行器接口"""
    
    @abstractmethod
    async def execute(self, ctx: TaskContext, draft_trans: Optional[str] = None) -> FinalResult:
        """
        执行阶段任务
        
        Args:
            ctx: 任务上下文
            draft_trans: 初译结果（可选）
            
        Returns:
            执行结果
        """
        pass
