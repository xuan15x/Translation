"""
数据模型 - 运行时上下文和结果
TaskContext, StageResult, FinalResult
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..exceptions import ValidationError


@dataclass
class TaskContext:
    """任务上下文，存储单个翻译任务的所有信息"""
    idx: int
    key: str
    source_text: str
    source_lang: str = "中文"
    original_trans: str = ""
    target_lang: str = "英语"
    tm_suggestion: Optional[Dict[str, Any]] = None
    is_exact_hit: bool = False

    def __post_init__(self):
        if not self.key:
            raise ValidationError("TaskContext 的 key 不能为空", field_name='key')
        if not self.source_text:
            raise ValidationError(
                "TaskContext 的 source_text 不能为空",
                field_name='source_text'
            )


@dataclass
class StageResult:
    """阶段执行结果 - 支持双阶段翻译"""
    success: bool
    translation: str
    error_msg: Optional[str] = None
    reason: str = ""
    source: str = ""
    diagnosis: str = ""

    def __post_init__(self):
        if self.success and not self.translation:
            raise ValidationError(
                "成功时 translation 不能为空字符串",
                field_name='translation'
            )


@dataclass
class FinalResult:
    """最终翻译结果"""
    key: str
    target_lang: str
    source_text: str
    final_trans: str
    status: str
    error_detail: Optional[str] = None
