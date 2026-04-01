"""
服务层 - 负责 API 提供商和翻译历史管理
"""
from .api_provider import get_provider_manager
from .translation_history import TranslationHistoryManager, get_history_manager

__all__ = ['get_provider_manager', 'TranslationHistoryManager', 'get_history_manager']
