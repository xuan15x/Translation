"""
配置管理 - 包含配置文件和常量
"""

from .config import (
    DEFAULT_DRAFT_PROMPT,
    DEFAULT_REVIEW_PROMPT,
    TARGET_LANGUAGES,
    GUI_CONFIG
)

__all__ = [
    'DEFAULT_DRAFT_PROMPT',
    'DEFAULT_REVIEW_PROMPT',
    'TARGET_LANGUAGES',
    'GUI_CONFIG'
]
