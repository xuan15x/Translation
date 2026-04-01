"""
翻译服务外观模式 - 精简版
基于新架构，零依赖旧代码
"""
import asyncio
from typing import List, Optional, Callable
import logging

from domain.models import TranslationTask, BatchResult
from application.result_builder import TaskFactory, ResultBuilder
from application.batch_processor import BatchTaskProcessor
from application.workflow_coordinator import TranslationWorkflowCoordinator


logger = logging.getLogger(__name__)


class TranslationServiceFacade:
    """翻译服务外观 - 精简版"""
    
    def __init__(self,
                 terminology_service,
                 translation_service):
        """
        初始化翻译服务外观
        
        Args:
            terminology_service: 术语服务
            translation_service: 翻译服务
        """
        # 创建工作流协调器（使用依赖注入的服务）
        self.coordinator = TranslationWorkflowCoordinator(
            terminology_service=terminology_service,
            translation_service=translation_service,
            batch_processor=None
        )
        
        # 进度回调
        self.progress_callback: Optional[Callable[[int, int], None]] = None
    
    def set_progress_callback(self, callback: Callable[[int, int], None]):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    async def translate_file(self,
                           source_excel_path: str,
                           target_langs: List[str],
                           output_excel_path: Optional[str] = None,
                           concurrency_limit: int = 10) -> BatchResult:
        """翻译 Excel 文件"""
        logger.info(f"开始翻译文件：{source_excel_path}")
        logger.info(f"目标语言：{target_langs}")
        
        # 1. 从 Excel 创建任务
        tasks = TaskFactory.from_excel_file(source_excel_path, target_langs)
        logger.info(f"创建了 {len(tasks)} 个翻译任务")
        
        # 2. 创建批量处理器
        batch_processor = BatchTaskProcessor(
            task_executor=self.coordinator.execute_task,
            concurrency_limit=concurrency_limit,
            progress_callback=self.progress_callback
        )
        
        # 3. 执行批量翻译
        batch_result = await batch_processor.process_batch(tasks)
        
        # 4. 导出结果
        if output_excel_path:
            ResultBuilder.to_excel(batch_result.results, output_excel_path)
            logger.info(f"结果已导出到：{output_excel_path}")
        
        # 5. 打印汇总
        ResultBuilder.print_summary(batch_result)
        
        return batch_result
    
    async def translate_text(self,
                            text: str,
                            target_lang: str,
                            source_lang: Optional[str] = "zh") -> str:
        """翻译单个文本"""
        task = TranslationTask(
            idx=0,
            key="single_text",
            source_text=text,
            original_trans=None,
            target_lang=target_lang,
            source_lang=source_lang
        )
        
        result = await self.coordinator.execute_task(task)
        
        if result.success:
            return result.final_trans
        else:
            raise RuntimeError(f"翻译失败：{result.reason}")
    
    async def get_statistics(self, excel_path: str, target_langs: List[str]) -> dict:
        """获取文件统计信息"""
        tasks = TaskFactory.from_excel_file(excel_path, target_langs)
        
        return {
            '总任务数': len(tasks),
            '唯一原文数': len(set(t.source_text for t in tasks)),
            '目标语言数': len(target_langs),
            '预估耗时 (秒)': len(tasks) * 2
        }
