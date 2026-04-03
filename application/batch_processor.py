"""
批量任务处理器
实现并发控制、进度跟踪的批量处理逻辑
"""
import asyncio
from typing import List, Callable, Awaitable
from domain.models import TranslationTask, TranslationResult, BatchResult, TranslationStatus
from domain.services import IBatchProcessor


class BatchTaskProcessor(IBatchProcessor):
    """批量任务处理器 - 支持并发控制和进度回调"""

    def __init__(self,
                 task_executor: Callable[[TranslationTask], Awaitable[TranslationResult]],
                 concurrency_limit: int = 10,
                 progress_callback: Callable[[int, int], None] = None):
        """
        初始化批量处理器

        Args:
            task_executor: 任务执行函数（异步）
            concurrency_limit: 并发限制
            progress_callback: 进度回调函数 (current, total)
        """
        self.task_executor = task_executor
        self.concurrency_limit = concurrency_limit
        self.progress_callback = progress_callback

    async def process_batch(self, tasks: List[TranslationTask]) -> BatchResult:
        """批量处理任务（使用默认并发数）"""
        return await self.process_concurrent(tasks, self.concurrency_limit)

    async def process_concurrent(self, tasks: List[TranslationTask], concurrency_limit: int) -> BatchResult:
        """并发处理任务（可配置并发数）"""
        batch_result = BatchResult(
            total=len(tasks),
            success_count=0,
            failed_count=0,
            local_hit_count=0
        )

        if not tasks:
            return batch_result

        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(concurrency_limit)

        async def process_with_semaphore(task: TranslationTask):
            async with semaphore:
                try:
                    result = await self.task_executor(task)

                    # 更新进度
                    if self.progress_callback:
                        current = len([r for r in batch_result.results if r.status != TranslationStatus.PENDING])
                        self.progress_callback(current + 1, len(tasks))

                    return result
                except Exception as e:
                    return TranslationResult(
                        task=task,
                        final_trans="(Error)",
                        initial_trans="",
                        reason=str(e),
                        diagnosis="Execution Error",
                        status=TranslationStatus.FAILED
                    )

        # 并发执行所有任务
        coroutines = [process_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # 统计结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_task = tasks[i]
                failed_result = TranslationResult(
                    task=failed_task,
                    final_trans="(Failed)",
                    initial_trans="",
                    reason=str(result),
                    diagnosis="Unhandled Exception",
                    status=TranslationStatus.FAILED
                )
                batch_result.add_result(failed_result)
            elif isinstance(result, TranslationResult):
                batch_result.add_result(result)

        return batch_result


class SequentialTaskProcessor(IBatchProcessor):
    """顺序任务处理器 - 逐个处理，便于调试"""
    
    def __init__(self,
                 task_executor: Callable[[TranslationTask], Awaitable[TranslationResult]],
                 progress_callback: Callable[[int, int], None] = None):
        """
        初始化顺序处理器
        
        Args:
            task_executor: 任务执行函数（异步）
            progress_callback: 进度回调函数
        """
        self.task_executor = task_executor
        self.progress_callback = progress_callback
    
    async def process_batch(self, tasks: List[TranslationTask]) -> BatchResult:
        """顺序处理任务"""
        batch_result = BatchResult(
            total=len(tasks),
            success_count=0,
            failed_count=0,
            local_hit_count=0
        )
        
        for i, task in enumerate(tasks):
            try:
                result = await self.task_executor(task)
                batch_result.add_result(result)
                
                # 更新进度
                if self.progress_callback:
                    self.progress_callback(i + 1, len(tasks))
            
            except Exception as e:
                # 异常处理
                failed_result = TranslationResult(
                    task=task,
                    final_trans="(Error)",
                    initial_trans="",
                    reason=str(e),
                    diagnosis="Exception",
                    status=TranslationStatus.FAILED
                )
                batch_result.add_result(failed_result)
        
        return batch_result
    
    async def process_concurrent(self, tasks: List[TranslationTask], concurrency_limit: int) -> BatchResult:
        """并发处理任务（可配置并发数）"""
        batch_result = BatchResult(
            total=len(tasks),
            success_count=0,
            failed_count=0,
            local_hit_count=0
        )
        
        if not tasks:
            return batch_result
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(concurrency_limit)
        
        async def process_with_semaphore(task: TranslationTask):
            async with semaphore:
                try:
                    result = await self.task_executor(task)
                    
                    # 更新进度
                    if self.progress_callback:
                        current = len([r for r in batch_result.results if r.status != TranslationStatus.PENDING])
                        self.progress_callback(current + 1, len(tasks))
                    
                    return result
                except Exception as e:
                    return TranslationResult(
                        task=task,
                        final_trans="(Error)",
                        initial_trans="",
                        reason=str(e),
                        diagnosis="Execution Error",
                        status=TranslationStatus.FAILED
                    )
        
        # 并发执行所有任务
        coroutines = [process_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # 统计结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_task = tasks[i]
                failed_result = TranslationResult(
                    task=failed_task,
                    final_trans="(Failed)",
                    initial_trans="",
                    reason=str(result),
                    diagnosis="Unhandled Exception",
                    status=TranslationStatus.FAILED
                )
                batch_result.add_result(failed_result)
            elif isinstance(result, TranslationResult):
                batch_result.add_result(result)
        
        return batch_result
