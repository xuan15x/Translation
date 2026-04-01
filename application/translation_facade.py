"""
翻译服务外观模式
为 GUI 提供简化的 API，内部使用新的分层架构
"""
import asyncio
from typing import List, Optional, Callable
import logging
from openai import AsyncOpenAI

from infrastructure.models import Config
from domain.models import TranslationTask, BatchResult
from application.result_builder import TaskFactory, ResultBuilder
from application.batch_processor import BatchTaskProcessor
from application.workflow_coordinator import TranslationWorkflowCoordinator, TaskOrchestrator
from domain.translation_service_impl import TranslationDomainServiceImpl
from business_logic.terminology_adapter import TerminologyManagerAdapter

logger = logging.getLogger(__name__)


class TranslationServiceFacade:
    """翻译服务外观 - 简化版 API"""
    
    def __init__(self,
                 config: Config,
                 terminology_manager,
                 api_client: AsyncOpenAI,
                 draft_prompt: str,
                 review_prompt: str):
        """
        初始化翻译服务外观
        
        Args:
            config: 配置对象
            terminology_manager: 旧的术语管理器（将通过适配器转换）
            api_client: OpenAI 客户端
            draft_prompt: 初译提示词
            review_prompt: 校对提示词
        """
        self.config = config
        self.api_client = api_client
        
        # 适配旧的术语管理器到新架构
        self.terminology_service = TerminologyManagerAdapter(terminology_manager)
        
        # 创建翻译服务
        self.translation_service = TranslationDomainServiceImpl(
            config=config,
            client=api_client,
            terminology_service=self.terminology_service,
            draft_prompt=draft_prompt,
            review_prompt=review_prompt
        )
        
        # 创建工作流协调器
        self.coordinator = TranslationWorkflowCoordinator(
            terminology_service=self.terminology_service,
            translation_service=self.translation_service,
            batch_processor=None  # 稍后创建
        )
        
        # 创建任务编排器
        self.orchestrator = TaskOrchestrator(
            coordinator=self.coordinator
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
        """
        翻译 Excel 文件
        
        Args:
            source_excel_path: 源 Excel 文件路径
            target_langs: 目标语言列表
            output_excel_path: 输出 Excel 路径（可选）
            concurrency_limit: 并发限制
            
        Returns:
            批量翻译结果
        """
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
        """
        翻译单个文本
        
        Args:
            text: 待翻译文本
            target_lang: 目标语言
            source_lang: 源语言（默认中文）
            
        Returns:
            翻译结果
        """
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
        """
        获取文件统计信息
        
        Args:
            excel_path: Excel 文件路径
            target_langs: 目标语言列表
            
        Returns:
            统计信息字典
        """
        tasks = TaskFactory.from_excel_file(excel_path, target_langs)
        
        return {
            '总任务数': len(tasks),
            '唯一原文数': len(set(t.source_text for t in tasks)),
            '目标语言数': len(target_langs),
            '预估耗时 (秒)': len(tasks) * 2  # 粗略估计
        }
