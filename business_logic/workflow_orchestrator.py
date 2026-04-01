"""
工作流编排模块
负责协调各个处理阶段，管理任务执行流程
"""
import asyncio
from typing import Optional
import logging
from openai import AsyncOpenAI

from infrastructure.models import Config, FinalResult, TaskContext
from infrastructure.log_config import log_with_tag, LogLevel, LogTag
from business_logic.terminology_manager import TerminologyManager
from infrastructure.concurrency_controller import AdaptiveConcurrencyController
from business_logic.api_stages import APIDraftStage, APIReviewStage, LocalHitStage
from service.translation_history import get_history_manager, record_translation

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """工作流编排器"""
    
    def __init__(self, config: Config, client: AsyncOpenAI, tm: TerminologyManager, 
                 p_draft: str, p_review: str, file_path: str = "", batch_id: str = ""):
        """
        初始化工作流编排器
        
        Args:
            config: 系统配置
            client: OpenAI 异步客户端
            tm: 术语库管理器
            p_draft: 初译提示词
            p_review: 校对提示词
            file_path: 源文件路径
            batch_id: 批次 ID
        """
        self.config = config
        self.client = client
        self.tm = tm
        self.file_path = file_path
        self.batch_id = batch_id
        
        # 初始化并发控制器和信号量
        self.controller = AdaptiveConcurrencyController(config)
        self.semaphore = asyncio.Semaphore(self.controller.get_limit())
        
        # 初始化各处理阶段
        self.draft_stage = APIDraftStage(
            client, self.controller, self.semaphore, config, p_draft
        )
        self.review_stage = APIReviewStage(
            client, self.controller, self.semaphore, config, p_review
        )
        self.local_stage = LocalHitStage()
        
        # 历史管理器
        self.history_manager = get_history_manager()

    async def process_task(self, ctx: TaskContext) -> FinalResult:
        """
        处理单个翻译任务
            
        Args:
            ctx: 任务上下文
                
        Returns:
            最终翻译结果
        """
        try:
            # 1. 查询术语库 (传入源语言)
            log_with_tag(
                f"[行{ctx.idx+1}] 查询术语：{ctx.source_text[:30]}... ({ctx.target_lang})",
                level=LogLevel.INFO,
                tag=LogTag.DEBUG
            )
                
            ctx.tm_suggestion = await self.tm.find_similar(
                ctx.source_text, 
                ctx.target_lang,
                ctx.source_lang  # 新增：传入源语言
            )
            ctx.is_exact_hit = (
                ctx.tm_suggestion and 
                ctx.tm_suggestion['score'] == self.config.exact_match_score
            )
                
            # 记录术语库匹配结果
            if ctx.is_exact_hit:
                log_with_tag(
                    f"[行{ctx.idx+1}] 术语库精确匹配：{ctx.source_text} -> {ctx.tm_suggestion['translation']} (得分:{ctx.tm_suggestion['score']})",
                    level=LogLevel.INFO,
                    tag=LogTag.IMPORTANT
                )
            elif ctx.tm_suggestion:
                log_with_tag(
                    f"[行{ctx.idx+1}] 术语库模糊匹配：{ctx.source_text} -> {ctx.tm_suggestion['translation']} (得分:{ctx.tm_suggestion['score']})",
                    level=LogLevel.INFO,
                    tag=LogTag.NORMAL
                )
            else:
                log_with_tag(
                    f"[行{ctx.idx+1}] 术语库无匹配",
                    level=LogLevel.INFO,
                    tag=LogTag.DEBUG
                )

            # 2. 如果有原译文，进入校对模式
            if ctx.original_trans:
                log_with_tag(
                    f"[行{ctx.idx+1}] 校对模式 | 原译：{ctx.original_trans[:50]}...",
                    level=LogLevel.INFO,
                    tag=LogTag.NORMAL
                )
                # 完全匹配且无需修改
                if (ctx.is_exact_hit and 
                    ctx.tm_suggestion['translation'] == ctx.original_trans):
                    log_with_tag(
                        f"[行{ctx.idx+1}] 原译文与术语库完全匹配，无需修改",
                        level=LogLevel.INFO,
                        tag=LogTag.IMPORTANT
                    )
                    return self._make_result(
                        ctx, 
                        ctx.original_trans, 
                        ctx.original_trans, 
                        "", 
                        "No Change (TM)", 
                        "LOCAL_HIT"
                    )
                
                # AI 校对
                log_with_tag(
                    f"[行{ctx.idx+1}] 调用 AI 校对...",
                    level=LogLevel.INFO,
                    tag=LogTag.PROGRESS
                )
                res = await self.review_stage.execute(ctx, ctx.original_trans)
                if res.success:
                    final_trans = res.translation if res.translation else ctx.original_trans
                    if final_trans != ctx.original_trans:
                        log_with_tag(
                            f"[行{ctx.idx+1}] AI 修改：{ctx.original_trans[:30]}... -> {final_trans[:30]}... (原因:{res.reason})",
                            level=LogLevel.INFO,
                            tag=LogTag.IMPORTANT
                        )
                        await self.tm.add_entry(ctx.source_text, ctx.target_lang, final_trans)
                        log_with_tag(
                            f"[行{ctx.idx+1}] 新术语已保存：{ctx.source_text} -> {final_trans}",
                            level=LogLevel.INFO,
                            tag=LogTag.IMPORTANT
                        )
                    else:
                        log_with_tag(
                            f"[行{ctx.idx+1}] AI 确认无需修改",
                            level=LogLevel.INFO,
                            tag=LogTag.NORMAL
                        )
                    return self._make_result(
                        ctx, 
                        ctx.original_trans, 
                        final_trans, 
                        res.reason, 
                        "AI Proofread", 
                        "SUCCESS"
                    )
                
                return self._make_result(
                    ctx, 
                    ctx.original_trans, 
                    ctx.original_trans, 
                    "", 
                    f"API Error: {res.error_msg}", 
                    "FAILED"
                )

            # 3. 新文档翻译模式
            # 本地精确命中直接使用，否则调用 API 初译
            if ctx.is_exact_hit:
                log_with_tag(
                    f"[行{ctx.idx+1}] 使用术语库翻译：{ctx.tm_suggestion['translation']}",
                    level=LogLevel.INFO,
                    tag=LogTag.IMPORTANT
                )
                draft_res = await self.local_stage.execute(ctx)
            else:
                log_with_tag(
                    f"[行{ctx.idx+1}] 调用 API 初译...",
                    level=LogLevel.INFO,
                    tag=LogTag.PROGRESS
                )
                draft_res = await self.draft_stage.execute(ctx)
            
            if not draft_res.success:
                return self._make_result(
                    ctx, 
                    "", 
                    "(Failed)", 
                    "", 
                    f"Stage 1 Failed: {draft_res.error_msg}", 
                    "FAILED"
                )

            # 4. 双阶段处理 (如果需要)
            final_trans, reason, diagnosis = draft_res.translation, "", "Draft Only"
                        
            if self.config.enable_two_pass:
                should_skip = (
                    self.config.skip_review_if_local_hit and 
                    draft_res.source == "LOCAL_HIT"
                )
                            
                if not should_skip:
                    log_with_tag(
                        f"[行{ctx.idx+1}] 调用 AI 校对 (双阶段)...",
                        level=LogLevel.INFO,
                        tag=LogTag.PROGRESS
                    )
                    review_res = await self.review_stage.execute(ctx, draft_res.translation)
                    if review_res.success:
                        if review_res.translation and review_res.translation != draft_res.translation:
                            final_trans, reason, diagnosis = (
                                review_res.translation, 
                                review_res.reason, 
                                "AI Polished"
                            )
                            log_with_tag(
                                f"[行{ctx.idx+1}] AI 优化：{draft_res.translation[:30]}... -> {final_trans[:30]}...",
                                level=LogLevel.INFO,
                                tag=LogTag.IMPORTANT
                            )
                        else:
                            reason, diagnosis = "No Change Needed", "Draft Verified"
                            log_with_tag(
                                f"[行{ctx.idx+1}] 校对确认无需修改",
                                level=LogLevel.INFO,
                                tag=LogTag.NORMAL
                            )
                    else:
                        diagnosis, reason = "Review Failed (Kept Draft)", f"API Error: {review_res.error_msg}"
                        log_with_tag(
                            f"[行{ctx.idx+1}] 校对失败，保留初译",
                            level=LogLevel.WARNING,
                            tag=LogTag.WARNING
                        )
                else:
                    diagnosis = "Local Hit (Skipped Review)"
                    log_with_tag(
                        f"[行{ctx.idx+1}] 跳过校对 (本地命中)",
                        level=LogLevel.INFO,
                        tag=LogTag.DEBUG
                    )

            # 5. 保存翻译结果到术语库
            if final_trans and final_trans != "(Failed)":
                try:
                    await self.tm.add_entry(ctx.source_text, ctx.target_lang, final_trans)
                    log_with_tag(
                        f"[行{ctx.idx+1}] 术语已入库：{ctx.source_text} -> {final_trans} ({ctx.target_lang})",
                        level=LogLevel.INFO,
                        tag=LogTag.IMPORTANT
                    )
                except Exception as e:
                    log_with_tag(
                        f"[行{ctx.idx+1}] 保存术语失败：{e},但不影响主流程",
                        level=LogLevel.WARNING,
                        tag=LogTag.WARNING
                    )
            
            # 6. 记录到翻译历史
            result = self._make_result(
                ctx, 
                draft_res.translation, 
                final_trans, 
                reason, 
                diagnosis, 
                status="SUCCESS" if final_trans != "(Failed)" else "FAILED"
            )
                        
            log_with_tag(
                f"[行{ctx.idx+1}] 处理完成 | 状态:{result.status} | 诊断:{result.diagnosis} | 最终译文:{final_trans[:50]}...",
                level=LogLevel.INFO,
                tag=LogTag.PROGRESS
            )
                        
            try:
                record_translation(
                    result=result,
                    api_provider=self.config.api_provider,
                    model_name=self.config.model_name,
                    file_path=self.file_path,
                    batch_id=self.batch_id
                )
                log_with_tag(
                    f"[行{ctx.idx+1}] 翻译历史已记录",
                    level=LogLevel.DEBUG,
                    tag=LogTag.TRACE
                )
            except Exception as e:
                # 历史记录失败不影响主流程
                log_with_tag(
                    f"[行{ctx.idx+1}] 记录翻译历史失败:{e}",
                    level=LogLevel.WARNING,
                    tag=LogTag.WARNING
                )
            
            return result
            
        except asyncio.CancelledError:
            # 任务被取消
            logger.warning(f"任务被取消：{ctx.key}")
            return self._make_result(
                ctx, 
                "", 
                "(Cancelled)", 
                "", 
                "Task cancelled",
                "CANCELLED"
            )
        except Exception as e:
            # 未预期的异常
            logger.exception(f"处理任务时发生异常：{ctx.key}, error: {e}")
            return self._make_result(
                ctx, 
                "", 
                "(Error)", 
                "", 
                f"Unexpected error: {str(e)}",
                "ERROR"
            )

    def _make_result(self, ctx: TaskContext, draft: str, final: str, 
                     reason: str, diag: str, status: str, 
                     error: str = None) -> FinalResult:
        """
        构建最终结果对象（精简版）
        
        Args:
            ctx: 任务上下文
            draft: 初译文本
            final: 最终译文
            reason: 原因说明（保留但不会返回）
            diag: 诊断信息（保留但不会返回）
            status: 状态标识
            error: 错误详情
            
        Returns:
            FinalResult 实例
        """
        return FinalResult(
            key=ctx.key,
            target_lang=ctx.target_lang,
            source_text=ctx.source_text,
            final_trans=final,
            status=status,
            error_detail=error
        )
