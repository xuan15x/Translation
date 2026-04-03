"""
提示词构建模块
负责构建发送给 AI 的用户消息
"""
import logging
from infrastructure.models import TaskContext
from infrastructure.logging import ModuleLoggerMixin, LogCategory


class PromptBuilder(ModuleLoggerMixin):
    """提示词构建器"""
    LOG_CATEGORY = LogCategory.PROMPT
    
    @staticmethod
    def build_user_message(stage: str, context: TaskContext, draft_trans: str = "") -> str:
        """
        构建用户消息
        
        Args:
            stage: 阶段标识 ("draft" 或 "review")
            context: 任务上下文
            draft_trans: 初译文本（仅在 review 阶段需要）
            
        Returns:
            构建好的用户消息字符串
        """
        parts = [f"Src: {context.source_text}"]
        
        if stage == "review":
            parts.append(f"Draft: {draft_trans}")
        
        if context.tm_suggestion:
            tm = context.tm_suggestion
            parts.append(f"TM({tm['score']}): {tm['original']}->{tm['translation']}")
        
        return "\n".join(parts)
