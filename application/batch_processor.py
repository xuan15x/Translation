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
        self.task_executor = task_executor
        self.concurrency_limit = concurrency_limit
        self.progress_callback = progress_callback

    async def process_batch(self, tasks: List[TranslationTask]) -> BatchResult:
        """批量处理任务（使用默认并发数）"""
        return await self.process_concurrent(tasks, self.concurrency_limit)

    async def process_concurrent(self, tasks: List[TranslationTask], concurrency_limit: int) -> BatchResult:
        """并发处理任务（可配置并发数）"""
        return await _process_tasks_concurrently(
            tasks, self.task_executor, concurrency_limit, self.progress_callback
        )


class SequentialTaskProcessor(IBatchProcessor):
    """顺序任务处理器 - 逐个处理，便于调试"""

    def __init__(self,
                 task_executor: Callable[[TranslationTask], Awaitable[TranslationResult]],
                 progress_callback: Callable[[int, int], None] = None):
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
                if self.progress_callback:
                    self.progress_callback(i + 1, len(tasks))
            except Exception as e:
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
        return await _process_tasks_concurrently(
            tasks, self.task_executor, concurrency_limit, self.progress_callback
        )


async def _process_tasks_concurrently(
    tasks: List[TranslationTask],
    task_executor: Callable[[TranslationTask], Awaitable[TranslationResult]],
    concurrency_limit: int,
    progress_callback: Callable[[int, int], None] = None,
) -> BatchResult:
    """共享的并发处理逻辑，供 BatchTaskProcessor 和 SequentialTaskProcessor 复用"""
    batch_result = BatchResult(
        total=len(tasks),
        success_count=0,
        failed_count=0,
        local_hit_count=0
    )

    if not tasks:
        return batch_result

    semaphore = asyncio.Semaphore(concurrency_limit)
    completed_count = 0

    async def process_with_semaphore(task: TranslationTask):
        nonlocal completed_count
        async with semaphore:
            try:
                result = await task_executor(task)
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, len(tasks))
                return result
            except Exception as e:
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, len(tasks))
                return TranslationResult(
                    task=task,
                    final_trans="(Error)",
                    initial_trans="",
                    reason=str(e),
                    diagnosis="Execution Error",
                    status=TranslationStatus.FAILED
                )

    coroutines = [process_with_semaphore(task) for task in tasks]
    results = await asyncio.gather(*coroutines, return_exceptions=True)

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
