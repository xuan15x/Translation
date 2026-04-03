"""
多语言翻译领域服务
支持一次 API 请求翻译多种语言
"""
import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from domain.models import (
    MultiLanguageTask,
    MultiLanguageResult,
    TranslationResult,
    TranslationStatus,
    TermMatch
)
from domain.services import ITermRepository
from infrastructure.models.models import Config
from service.api_stage_multilingual import MultilingualAPIStage
from infrastructure.utils import AdaptiveConcurrencyController
import asyncio

logger = logging.getLogger(__name__)


class MultilingualTranslationService:
    """多语言翻译领域服务 - 一次请求翻译多种语言"""

    def __init__(self,
                 config: Config,
                 client: AsyncOpenAI,
                 terminology_repo: ITermRepository,
                 draft_prompt: str):
        """
        初始化多语言翻译服务

        Args:
            config: 配置对象
            client: OpenAI 异步客户端
            terminology_repo: 术语仓储
            draft_prompt: 翻译提示词
        """
        self.config = config
        self.client = client
        self.terminology_repo = terminology_repo
        self.draft_prompt = draft_prompt

        # 初始化并发控制
        self.controller = AdaptiveConcurrencyController(config)
        self.semaphore = asyncio.Semaphore(self.controller.get_limit())

        # 初始化多语言 API 阶段
        self.multilingual_stage = MultilingualAPIStage(
            client=client,
            controller=self.controller,
            semaphore=self.semaphore,
            config=config,
            system_prompt=draft_prompt
        )

    async def translate_multilingual(self, task: MultiLanguageTask) -> MultiLanguageResult:
        """
        执行多语言翻译

        Args:
            task: 多语言任务

        Returns:
            多语言翻译结果
        """
        try:
            # 查询术语匹配（所有目标语言）
            for lang in task.target_langs:
                try:
                    tm_match = await self.terminology_repo.find_by_source(task.source_text, lang)
                    task.tm_matches[lang] = tm_match
                except Exception as e:
                    logger.warning(f"查询术语匹配失败 ({lang}): {e}")
                    task.tm_matches[lang] = None

            # 检查是否全部本地命中
            all_exact_hits = all(
                tm and tm.is_exact
                for tm in task.tm_matches.values()
            )

            if all_exact_hits and task.tm_matches:
                # 全部本地命中，直接使用术语
                translations = {
                    lang: tm.translation
                    for lang, tm in task.tm_matches.items()
                    if tm
                }
                
                return MultiLanguageResult(
                    task=task,
                    translations=translations,
                    success_langs=list(translations.keys()),
                    failed_langs=[],
                    diagnosis="Local TM Hit",
                    status=TranslationStatus.LOCAL_HIT
                )
            
            # 调用多语言 API 翻译
            result = await self.multilingual_stage.execute(task)
            
            # 保存翻译结果到术语库
            if result.success:
                for lang, trans in result.translations.items():
                    try:
                        await self.terminology_repo.save(task.source_text, lang, trans)
                    except Exception as e:
                        logger.warning(f"保存术语失败 ({lang}): {e}")
            
            return result

        except Exception as e:
            logger.exception(f"多语言翻译失败: {e}")
            return MultiLanguageResult(
                task=task,
                translations={},
                success_langs=[],
                failed_langs=task.target_langs.copy(),
                diagnosis=f"Exception: {str(e)}",
                status=TranslationStatus.FAILED
            )

    async def translate_multilingual_batch(self, tasks: List[MultiLanguageTask]) -> List[TranslationResult]:
        """
        批量执行多语言翻译

        Args:
            tasks: 多语言任务列表

        Returns:
            单语言翻译结果列表（兼容现有系统）
        """
        all_results = []
        
        for task in tasks:
            multi_result = await self.translate_multilingual(task)
            # 转换为单语言结果
            single_results = multi_result.to_single_results()
            all_results.extend(single_results)
        
        return all_results


def create_multilingual_service(config: Config, client: AsyncOpenAI, terminology_repo, draft_prompt: str) -> MultilingualTranslationService:
    """
    创建多语言翻译服务

    Args:
        config: 配置对象
        client: OpenAI 异步客户端
        terminology_repo: 术语仓储
        draft_prompt: 翻译提示词

    Returns:
        多语言翻译服务实例
    """
    return MultilingualTranslationService(
        config=config,
        client=client,
        terminology_repo=terminology_repo,
        draft_prompt=draft_prompt
    )
