"""
翻译服务外观模式 - 重构版
支持新旧两种翻译模式和多语言批量翻译
"""
import asyncio
from typing import List, Optional, Callable, Dict
import logging

from domain.models import TranslationTask, BatchResult, TranslationStatus
from application.result_builder import TaskFactory, ResultBuilder
from application.batch_processor import BatchTaskProcessor
from application.workflow_coordinator import TranslationWorkflowCoordinator
from application.enhanced_translator import EnhancedTranslator, TranslationState, TranslationProgress

logger = logging.getLogger(__name__)


class TranslationServiceFacade:
    """翻译服务外观 - 重构版"""

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

        # 增强型翻译器（支持断点续传）
        self.enhanced_translator: Optional[EnhancedTranslator] = None
        self._use_enhanced = False  # 是否使用增强型翻译器

        # 保存服务引用供增强型翻译器使用
        self._terminology_service = terminology_service
        self._translation_service = translation_service
        
        # 多语言翻译服务
        self._multilingual_service = None

    def set_progress_callback(self, callback: Callable[[int, int], None]):
        """设置进度回调函数"""
        self.progress_callback = callback

    def enable_enhanced_translator(self, enable: bool = True) -> None:
        """
        启用/禁用增强型翻译器

        Args:
            enable: 是否启用
        """
        self._use_enhanced = enable
        if enable and not self.enhanced_translator:
            self.enhanced_translator = EnhancedTranslator(
                translation_facade=self,
                state_dir=".translation_state",
                preview_lines=10
            )
            logger.info("✅ 增强型翻译器已启用（支持断点续传）")

    def set_progress_callback_enhanced(self, callback: Callable[[TranslationProgress], None]) -> None:
        """
        设置增强型进度回调

        Args:
            callback: 进度回调函数
        """
        if self.enhanced_translator:
            self.enhanced_translator.on_progress = callback

    def set_preview_callback(self, callback: Callable[[List[dict]], None]) -> None:
        """
        设置预览回调

        Args:
            callback: 预览回调函数
        """
        if self.enhanced_translator:
            self.enhanced_translator.on_preview = callback

    def pause_translation(self) -> bool:
        """暂停翻译"""
        if self.enhanced_translator:
            return self.enhanced_translator.pause()
        return False

    def resume_translation(self) -> bool:
        """恢复翻译"""
        if self.enhanced_translator:
            return self.enhanced_translator.resume()
        return False

    def stop_translation(self) -> bool:
        """停止翻译"""
        if self.enhanced_translator:
            return self.enhanced_translator.stop()
        return False

    def enable_multilingual_mode(self, enable: bool = True) -> None:
        """
        启用/禁用多语言翻译模式（一次请求翻译多种语言）

        Args:
            enable: 是否启用
        """
        if enable and not self._multilingual_service:
            from domain.translation_service_multilingual import create_multilingual_service
            from infrastructure.di.di_container import get_container
            
            container = get_container()
            config = container.get('config')
            client = container.get('translation_service').client
            term_repo = container.get('term_repository')
            draft_prompt = container.get('translation_service').draft_prompt
            
            self._multilingual_service = create_multilingual_service(
                config=config,
                client=client,
                terminology_repo=term_repo,
                draft_prompt=draft_prompt
            )
            logger.info("✅ 多语言翻译模式已启用（一次请求翻译多种语言）")

    async def translate_file(self,
                           source_excel_path: str,
                           target_langs: List[str],
                           output_excel_path: Optional[str] = None,
                           concurrency_limit: int = 10,
                           source_lang: Optional[str] = None,
                           use_multilingual: bool = True) -> BatchResult:
        """翻译 Excel 文件

        Args:
            source_excel_path: 源 Excel 文件路径
            target_langs: 目标语言列表
            output_excel_path: 输出文件路径（可选）
            concurrency_limit: 并发数限制
            source_lang: 源语言（可选，None 表示自动检测）
            use_multilingual: 是否使用多语言模式（默认启用）
        """
        logger.info(f"开始翻译文件：{source_excel_path}")
        logger.info(f"目标语言：{target_langs}")
        if source_lang:
            logger.info(f"源语言：{source_lang}")
        else:
            logger.info("源语言：自动检测")
        
        # 如果启用多语言模式且目标语言数>1，使用多语言模式
        if use_multilingual and len(target_langs) > 1 and self._multilingual_service:
            logger.info(f"🌐 使用多语言翻译模式（一次请求翻译 {len(target_langs)} 种语言）")
            return await self._translate_file_multilingual(
                source_excel_path,
                target_langs,
                output_excel_path,
                concurrency_limit,
                source_lang
            )
        else:
            logger.info("📝 使用单语言翻译模式")
            return await self._translate_file_single(
                source_excel_path,
                target_langs,
                output_excel_path,
                concurrency_limit,
                source_lang
            )
    
    async def _translate_file_multilingual(self,
                                         source_excel_path: str,
                                         target_langs: List[str],
                                         output_excel_path: Optional[str] = None,
                                         concurrency_limit: int = 10,
                                         source_lang: Optional[str] = None) -> BatchResult:
        """使用多语言模式翻译文件（一次请求翻译多种语言）"""
        from domain.models import MultiLanguageTask, MultiLanguageResult
        import asyncio
        
        # 1. 创建多语言任务
        multi_tasks = TaskFactory.from_excel_file_multilingual(
            source_excel_path, target_langs, source_lang
        )
        logger.info(f"创建了 {len(multi_tasks)} 个多语言翻译任务")
        
        # 2. 执行多语言翻译
        all_results = []
        semaphore = asyncio.Semaphore(concurrency_limit)
        
        async def process_multi_task(task: MultiLanguageTask):
            async with semaphore:
                result = await self._multilingual_service.translate_multilingual(task)
                # 转换为单语言结果
                single_results = result.to_single_results()
                all_results.extend(single_results)
                
                # 更新进度
                if self.progress_callback:
                    completed = len([r for r in all_results if r.status != TranslationStatus.PENDING])
                    total = len(multi_tasks) * len(target_langs)
                    self.progress_callback(completed, total)
        
        # 并发执行所有多语言任务
        tasks = [process_multi_task(task) for task in multi_tasks]
        await asyncio.gather(*tasks)
        
        # 3. 创建批量结果
        batch_result = BatchResult(
            total=len(all_results),
            success_count=sum(1 for r in all_results if r.success),
            failed_count=sum(1 for r in all_results if not r.success),
            local_hit_count=sum(1 for r in all_results if r.status == TranslationStatus.LOCAL_HIT),
            results=all_results
        )
        
        # 4. 导出结果（多语言格式：原文 + 各语言列）
        if output_excel_path:
            self._export_multilingual_results(all_results, output_excel_path, target_langs)
            logger.info(f"多语言结果已导出到：{output_excel_path}")
        
        # 5. 打印汇总
        ResultBuilder.print_summary(batch_result)
        
        return batch_result
    
    def _export_multilingual_results(self, results, output_path, target_langs):
        """导出多语言翻译结果（所有语言在一个文件中）"""
        import pandas as pd
        from collections import defaultdict
        
        # 按行索引组织数据
        rows = defaultdict(dict)
        
        for result in results:
            idx = result.task.idx
            rows[idx]['行号'] = idx + 1
            rows[idx]['Key'] = result.task.key
            rows[idx]['原文'] = result.task.source_text
            rows[idx][f'译文_{result.task.target_lang}'] = result.final_trans if result.success else '(Failed)'
            rows[idx][f'状态_{result.task.target_lang}'] = result.status.value
        
        # 转换为 DataFrame
        df = pd.DataFrame.from_dict(rows, orient='index')
        
        # 确保列顺序
        base_cols = ['行号', 'Key', '原文']
        lang_cols = []
        for lang in target_langs:
            lang_cols.append(f'译文_{lang}')
            lang_cols.append(f'状态_{lang}')
        
        all_cols = base_cols + lang_cols
        # 只保留存在的列
        final_cols = [c for c in all_cols if c in df.columns]
        
        df = df[final_cols]
        df.to_excel(output_path, index=False, engine='openpyxl')
        logger.info(f"多语言 Excel 导出完成：{output_path}")
    
    async def _translate_file_single(self,
                                    source_excel_path: str,
                                    target_langs: List[str],
                                    output_excel_path: Optional[str] = None,
                                    concurrency_limit: int = 10,
                                    source_lang: Optional[str] = None) -> BatchResult:
        """使用单语言模式翻译文件（原有逻辑）"""
        # 1. 从 Excel 创建任务（传递源语言参数）
        tasks = TaskFactory.from_excel_file(source_excel_path, target_langs, source_lang)
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
