"""
提示词构建模块
"""
import logging
from infrastructure.models.models import TaskContext
from infrastructure.logging import ModuleLoggerMixin, LogCategory


class PromptBuilder(ModuleLoggerMixin):
    """提示词构建器"""
    LOG_CATEGORY = LogCategory.PROMPT

    @staticmethod
    def build_user_message(stage: str, context: TaskContext, draft_trans: str = "") -> str:
        parts = [f"Src: {context.source_text}"]
        if stage == "review":
            parts.append(f"Draft: {draft_trans}")
        if context.tm_suggestion:
            tm = context.tm_suggestion
            parts.append(f"TM({tm['score']}): {tm['original']}->{tm['translation']}")
        return "\n".join(parts)
