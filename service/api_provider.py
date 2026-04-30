"""
API 提供商管理模块
专用于 DeepSeek API 的配置和客户端管理
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProviderConfig:
    """DeepSeek 提供商配置"""
    name: str = "DeepSeek"
    base_url: str = "https://api.deepseek.com"
    api_key_env: str = "DEEPSEEK_API_KEY"
    default_model: str = "deepseek-chat"
    models: List[str] = field(default_factory=lambda: ["deepseek-chat", "deepseek-reasoner"])
    max_tokens: int = 8192
    supports_temperature: bool = True
    supports_top_p: bool = True
    supports_system_prompt: bool = True


class DeepSeekProviderManager:
    """DeepSeek 提供商管理器（单例）"""

    def __init__(self):
        self._config = ProviderConfig()
        self._api_key: Optional[str] = None

    @property
    def provider_name(self) -> str:
        return "deepseek"

    def get_config(self) -> ProviderConfig:
        """获取 DeepSeek 配置"""
        return self._config

    def set_api_key(self, api_key: str) -> None:
        """设置 API 密钥"""
        self._api_key = api_key

    def get_api_key(self) -> Optional[str]:
        """获取 API 密钥"""
        import os
        return self._api_key or os.environ.get(self._config.api_key_env)

    def get_base_url(self) -> str:
        """获取 API 基础 URL"""
        return self._config.base_url

    def get_default_model(self) -> str:
        """获取默认模型"""
        return self._config.default_model

    def list_models(self) -> List[str]:
        """列出 DeepSeek 可用模型"""
        return self._config.models

    def create_client(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        创建 DeepSeek API 客户端

        Args:
            api_key: API 密钥，如果为 None 则从配置/环境变量读取
            base_url: 自定义基础 URL

        Returns:
            AsyncOpenAI 客户端实例
        """
        from openai import AsyncOpenAI

        if api_key is None:
            api_key = self.get_api_key()

        if base_url is None:
            base_url = self._config.base_url

        return AsyncOpenAI(api_key=api_key, base_url=base_url)


# 全局单例
_provider_manager: Optional[DeepSeekProviderManager] = None


def get_provider_manager() -> DeepSeekProviderManager:
    """获取全局 DeepSeek 提供商管理器实例"""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = DeepSeekProviderManager()
    return _provider_manager


def create_api_client(api_key: Optional[str] = None):
    """
    创建 DeepSeek API 客户端的便捷函数

    Args:
        api_key: API 密钥

    Returns:
        API 客户端实例
    """
    return get_provider_manager().create_client(api_key=api_key)
