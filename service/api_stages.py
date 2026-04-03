"""
API 阶段处理模块
使用 api_stage_base 中的抽象基类实现初译、校对和本地命中的处理逻辑
"""
import asyncio
from typing import Any
import logging

from openai import AsyncOpenAI

from infrastructure.models.models import Config, StageResult, TaskContext
from infrastructure.utils import AdaptiveConcurrencyController
from .api_stage_base import APIDraftStage as APIDraftStageBase, APIReviewStage as APIReviewStageBase

logger = logging.getLogger(__name__)


# 使用基类中的实现
APIDraftStage = APIDraftStageBase
APIReviewStage = APIReviewStageBase


class LocalHitStage:
    """本地术语命中阶段"""

    async def execute(self, context: TaskContext) -> StageResult:
        """
        执行本地术语匹配检查

        Args:
            context: 任务上下文

        Returns:
            阶段执行结果
        """
        if not context.tm_suggestion:
            return StageResult(False, "", source="NONE")

        return StageResult(
            success=True,
            translation=context.tm_suggestion['translation'],
            source="LOCAL_HIT"
        )
