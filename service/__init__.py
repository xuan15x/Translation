"""
服务层 - DeepSeek API 集成和翻译历史管理
"""
from .api_provider import get_provider_manager, create_api_client
from .translation_history import TranslationHistoryManager, get_history_manager

__all__ = [
    'get_provider_manager',
    'create_api_client',
    'TranslationHistoryManager',
    'get_history_manager',
]
