"""
应用层/编排层
协调领域服务完成业务流程
"""
from typing import List, Optional
from domain.models import TranslationTask, TranslationResult, BatchResult, TranslationStatus
from domain.services import (
    ITerminologyDomainService,
    ITranslationDomainService,
    IBatchProcessor
)


class TranslationWorkflowCoordinator:
    """翻译工作流协调器 - 应用层核心"""
    
    def __init__(self,
                 terminology_service: ITerminologyDomainService,
                 translation_service: ITranslationDomainService,
                 batch_processor: Optional[IBatchProcessor] = None):
        """
        初始化工作流协调器
        
        Args:
            terminology_service: 术语服务
            translation_service: 翻译服务
            batch_processor: 批量处理器（可选）
        """
        self.terminology_service = terminology_service
        self.translation_service = translation_service
        self.batch_processor = batch_processor
    
    async def execute_task(self, task: TranslationTask) -> TranslationResult:
        """
        执行单个翻译任务
        
        Args:
            task: 翻译任务
            
        Returns:
            翻译结果
        """
        # 1. 查询术语库
        tm_match = await self.terminology_service.find_match(
            task.source_text,
            task.target_lang
        )
        
        # 2. 精确匹配 → 直接使用
        if tm_match and tm_match.is_exact:
            return TranslationResult(
                task=task,
                final_trans=tm_match.translation,
                initial_trans=tm_match.translation,
                reason="",
                diagnosis="Exact Match (TM)",
                status=TranslationStatus.LOCAL_HIT,
                tm_match=tm_match
            )
        
        # 3. 有原译文 → 校对模式
        if task.original_trans:
            return await self.translation_service.proofread(task, task.original_trans)
        
        # 4. 无原译文 → 初译模式
        return await self.translation_service.translate(task)
    
    async def execute_batch(self, tasks: List[TranslationTask]) -> BatchResult:
        """
        批量执行翻译任务
        
        Args:
            tasks: 任务列表
            
        Returns:
            批量结果
        """
        # 使用批量处理器（如果有）
        if self.batch_processor:
            return await self.batch_processor.process_batch(tasks)
        
        # 否则逐个处理
        batch_result = BatchResult(total=len(tasks))
        
        for task in tasks:
            try:
                result = await self.execute_task(task)
                batch_result.add_result(result)
            except Exception as e:
                # 记录错误，继续处理下一个
                pass
        
        return batch_result


class TaskOrchestrator:
    """任务编排器 - 负责并发控制和流程管理"""
    
    def __init__(self, coordinator: TranslationWorkflowCoordinator):
        """
        初始化任务编排器
        
        Args:
            coordinator: 工作流协调器
        """
        self.coordinator = coordinator
        self.concurrency_limit = 10  # 默认并发数
    
    async def orchestrate(self, tasks: List[TranslationTask]) -> BatchResult:
        """
        编排执行所有任务
        
        Args:
            tasks: 任务列表
            
        Returns:
            批量结果
        """
        import asyncio
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        
        async def process_with_semaphore(task: TranslationTask):
            async with semaphore:
                return await self.coordinator.execute_task(task)
        
        # 并发执行所有任务
        coroutines = [process_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # 统计结果
        batch_result = BatchResult(total=len(tasks))
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 任务失败
                failed_task = tasks[i]
                failed_result = TranslationResult(
                    task=failed_task,
                    final_trans="(Failed)",
                    initial_trans="",
                    reason=str(result),
                    diagnosis="Execution Error",
                    status=TranslationStatus.FAILED
                )
                batch_result.add_result(failed_result)
            elif isinstance(result, TranslationResult):
                batch_result.add_result(result)
        
        return batch_result
