"""
翻译领域服务实现
整合 API 调用、缓存、历史记录等服务
"""
import logging
from typing import Optional
from openai import AsyncOpenAI
from domain.services import ITranslationDomainService
from domain.models import (
    TranslationTask, 
    TranslationResult, 
    TranslationStatus,
    TermMatch
)
from infrastructure.models import Config, TaskContext, FinalResult
from service.api_stages import APIDraftStage, APIReviewStage
from infrastructure.concurrency_controller import AdaptiveConcurrencyController
import asyncio

logger = logging.getLogger(__name__)


class TranslationDomainServiceImpl(ITranslationDomainService):
    """翻译领域服务实现"""
    
    def __init__(self,
                 config: Config,
                 client: AsyncOpenAI,
                 terminology_service,
                 draft_prompt: str,
                 review_prompt: str):
        """
        初始化翻译服务
        
        Args:
            config: 配置对象
            client: OpenAI 客户端
            terminology_service: 术语服务（用于保存新术语）
            draft_prompt: 初译提示词
            review_prompt: 校对提示词
        """
        self.config = config
        self.client = client
        self.terminology_service = terminology_service
        self.draft_prompt = draft_prompt
        self.review_prompt = review_prompt
        
        # 初始化并发控制
        self.controller = AdaptiveConcurrencyController(config)
        self.semaphore = asyncio.Semaphore(self.controller.get_limit())
        
        # 初始化 API 阶段
        self.draft_stage = APIDraftStage(
            client=client,
            controller=self.controller,
            semaphore=self.semaphore,
            config=config,
            prompt=draft_prompt
        )
        
        self.review_stage = APIReviewStage(
            client=client,
            controller=self.controller,
            semaphore=self.semaphore,
            config=config,
            prompt=review_prompt
        )
    
    async def translate(self, task: TranslationTask) -> TranslationResult:
        """执行初译"""
        try:
            # 转换为旧的任务上下文（兼容现有 API）
            ctx = TaskContext(
                idx=task.idx,
                key=task.key,
                source_text=task.source_text,
                original_trans=None,
                target_lang=task.target_lang,
                source_lang=task.source_lang or "zh",
                tm_suggestion=None,
                is_exact_hit=False
            )
            
            # 调用 API 初译阶段
            draft_result = await self.draft_stage.execute(ctx)
            
            if draft_result.success:
                # 翻译成功，保存到术语库
                await self.terminology_service.save_term(
                    task.source_text,
                    task.target_lang,
                    draft_result.translation
                )
                
                return TranslationResult(
                    task=task,
                    final_trans=draft_result.translation,
                    initial_trans=draft_result.translation,
                    reason="",
                    diagnosis=draft_result.diagnosis,
                    status=TranslationStatus.SUCCESS
                )
            else:
                return TranslationResult(
                    task=task,
                    final_trans="(Failed)",
                    initial_trans="",
                    reason=draft_result.error_msg,
                    diagnosis="API Error",
                    status=TranslationStatus.FAILED
                )
        
        except Exception as e:
            logger.exception(f"翻译失败：{e}")
            return TranslationResult(
                task=task,
                final_trans="(Error)",
                initial_trans="",
                reason=str(e),
                diagnosis="Exception",
                status=TranslationStatus.FAILED
            )
    
    async def proofread(self, task: TranslationTask, draft: str) -> TranslationResult:
        """执行校对"""
        try:
            # 转换为旧的任务上下文
            ctx = TaskContext(
                idx=task.idx,
                key=task.key,
                source_text=task.source_text,
                original_trans=draft,
                target_lang=task.target_lang,
                source_lang=task.source_lang or "zh",
                tm_suggestion=None,
                is_exact_hit=False
            )
            
            # 调用 API 校对阶段
            review_result = await self.review_stage.execute(ctx, draft)
            
            if review_result.success:
                final_trans = review_result.translation if review_result.translation else draft
                
                # 如果有修改，保存新术语
                if final_trans != draft:
                    await self.terminology_service.save_term(
                        task.source_text,
                        task.target_lang,
                        final_trans
                    )
                
                return TranslationResult(
                    task=task,
                    final_trans=final_trans,
                    initial_trans=draft,
                    reason=review_result.reason,
                    diagnosis=review_result.diagnosis,
                    status=TranslationStatus.SUCCESS
                )
            else:
                return TranslationResult(
                    task=task,
                    final_trans=draft,
                    initial_trans=draft,
                    reason=review_result.error_msg,
                    diagnosis="API Error",
                    status=TranslationStatus.FAILED
                )
        
        except Exception as e:
            logger.exception(f"校对失败：{e}")
            return TranslationResult(
                task=task,
                final_trans=draft,
                initial_trans=draft,
                reason=str(e),
                diagnosis="Exception",
                status=TranslationStatus.FAILED
            )
