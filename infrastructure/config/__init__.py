"""
配置管理 - 包含配置文件和常量
"""

from .config import (
    DEFAULT_DRAFT_PROMPT,
    DEFAULT_REVIEW_PROMPT,
    TARGET_LANGUAGES,
    GUI_CONFIG,
    T1_LANGUAGES,
    T2_LANGUAGES,
    T3_LANGUAGES,
    LANGUAGES_BY_TIER,
    GAME_TRANSLATION_TYPES,
    GAME_DRAFT_PROMPTS,
    GAME_REVIEW_PROMPTS,
    get_prompt_injection_config,
    get_prohibition_type_map_global
)

__all__ = [
    'DEFAULT_DRAFT_PROMPT',
    'DEFAULT_REVIEW_PROMPT',
    'TARGET_LANGUAGES',
    'GUI_CONFIG',
    'T1_LANGUAGES',
    'T2_LANGUAGES',
    'T3_LANGUAGES',
    'LANGUAGES_BY_TIER',
    'GAME_TRANSLATION_TYPES',
    'GAME_DRAFT_PROMPTS',
    'GAME_REVIEW_PROMPTS',
    'get_prompt_injection_config',
    'get_prohibition_type_map_global'
]
