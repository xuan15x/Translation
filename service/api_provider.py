"""
API 提供商管理模块
支持多种 LLM API 提供商的切换和配置
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class APIProvider(Enum):
    """支持的 API 提供商枚举"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOONSHOT = "moonshot"  # Kimi
    ZHIPU = "zhipu"  # 智谱 AI
    BAIDU = "baidu"  # 文心一言
    ALIBABA = "alibaba"  # 通义千问
    CUSTOM = "custom"  # 自定义


@dataclass
class ProviderConfig:
    """单个提供商的配置"""
    name: str
    base_url: str
    api_key_env: str  # 环境变量名
    default_model: str
    models: List[str] = field(default_factory=list)
    max_tokens: int = 4096
    supports_temperature: bool = True
    supports_top_p: bool = True
    supports_system_prompt: bool = True
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.models:
            self.models = [self.default_model]


# 预定义的提供商配置
PREDEFINED_PROVIDERS: Dict[APIProvider, ProviderConfig] = {
    APIProvider.DEEPSEEK: ProviderConfig(
        name="DeepSeek",
        base_url="https://api.deepseek.com",
        api_key_env="DEEPSEEK_API_KEY",
        default_model="deepseek-chat",
        models=["deepseek-chat", "deepseek-coder"],
        max_tokens=4096,
    ),
    
    APIProvider.OPENAI: ProviderConfig(
        name="OpenAI",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        default_model="gpt-3.5-turbo",
        models=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        max_tokens=4096,
    ),
    
    APIProvider.ANTHROPIC: ProviderConfig(
        name="Anthropic",
        base_url="https://api.anthropic.com",
        api_key_env="ANTHROPIC_API_KEY",
        default_model="claude-3-sonnet-20240229",
        models=["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        max_tokens=4096,
        supports_top_p=False,  # Anthropic 使用 top_k
    ),
    
    APIProvider.MOONSHOT: ProviderConfig(
        name="Moonshot (Kimi)",
        base_url="https://api.moonshot.cn/v1",
        api_key_env="MOONSHOT_API_KEY",
        default_model="moonshot-v1-8k",
        models=["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        max_tokens=8192,
    ),
    
    APIProvider.ZHIPU: ProviderConfig(
        name="Zhipu AI (智谱)",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key_env="ZHIPU_API_KEY",
        default_model="glm-4",
        models=["glm-4", "glm-4-flash", "glm-3-turbo"],
        max_tokens=2048,
    ),
    
    APIProvider.BAIDU: ProviderConfig(
        name="Baidu (文心一言)",
        base_url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1",
        api_key_env="BAIDU_API_KEY",
        default_model="ernie-bot-4",
        models=["ernie-bot-4", "ernie-bot-3.5", "ernie-bot-turbo"],
        max_tokens=2048,
        supports_system_prompt=False,  # 百度有特殊格式
    ),
    
    APIProvider.ALIBABA: ProviderConfig(
        name="Alibaba (通义千问)",
        base_url="https://dashscope.aliyuncs.com/api/v1",
        api_key_env="ALIBABA_API_KEY",
        default_model="qwen-turbo",
        models=["qwen-turbo", "qwen-plus", "qwen-max"],
        max_tokens=2048,
    ),
}


class APIProviderManager:
    """API 提供商管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self._providers: Dict[APIProvider, ProviderConfig] = PREDEFINED_PROVIDERS.copy()
        self._current_provider: APIProvider = APIProvider.DEEPSEEK
        self._custom_providers: Dict[str, ProviderConfig] = {}
    
    def get_provider(self, provider: APIProvider) -> Optional[ProviderConfig]:
        """
        获取指定提供商的配置
        
        Args:
            provider: API 提供商枚举
            
        Returns:
            提供商配置，如果不存在则返回 None
        """
        return self._providers.get(provider)
    
    def get_current_provider(self) -> APIProvider:
        """获取当前选中的提供商"""
        return self._current_provider
    
    def set_provider(self, provider: APIProvider) -> None:
        """
        设置当前使用的提供商
        
        Args:
            provider: API 提供商枚举
            
        Raises:
            ValueError: 如果提供商不存在
        """
        if provider not in self._providers and provider not in self._custom_providers:
            raise ValueError(f"未知的 API 提供商：{provider}")
        
        self._current_provider = provider
        self._update_env_for_provider(provider)
    
    def _update_env_for_provider(self, provider: APIProvider) -> None:
        """更新环境变量以匹配当前提供商"""
        import os
        from infrastructure.models import Config
        
        config = self._providers.get(provider)
        if config:
            # 确保正确的环境变量被使用
            if config.api_key_env not in os.environ:
                # 尝试从其他常见变量名获取
                common_names = ["API_KEY", "LLM_API_KEY"]
                for name in common_names:
                    if name in os.environ:
                        os.environ[config.api_key_env] = os.environ[name]
                        break
    
    def add_custom_provider(self, name: str, config: ProviderConfig) -> None:
        """
        添加自定义提供商
        
        Args:
            name: 提供商名称
            config: 提供商配置
        """
        self._custom_providers[name] = config
    
    def remove_custom_provider(self, name: str) -> None:
        """移除自定义提供商"""
        if name in self._custom_providers:
            del self._custom_providers[name]
    
    def list_providers(self) -> List[APIProvider]:
        """列出所有可用的提供商"""
        return list(self._providers.keys())
    
    def list_models(self, provider: Optional[APIProvider] = None) -> List[str]:
        """
        列出指定提供商的所有可用模型
        
        Args:
            provider: API 提供商，如果为 None 则使用当前提供商
            
        Returns:
            模型列表
        """
        if provider is None:
            provider = self._current_provider
        
        config = self._providers.get(provider)
        if config:
            return config.models
        return []
    
    def get_base_url(self, provider: Optional[APIProvider] = None) -> str:
        """获取指定提供商的 API 基础 URL"""
        if provider is None:
            provider = self._current_provider
        
        config = self._providers.get(provider)
        if config:
            return config.base_url
        raise ValueError(f"未知的 API 提供商：{provider}")
    
    def get_default_model(self, provider: Optional[APIProvider] = None) -> str:
        """获取指定提供商的默认模型"""
        if provider is None:
            provider = self._current_provider
        
        config = self._providers.get(provider)
        if config:
            return config.default_model
        raise ValueError(f"未知的 API 提供商：{provider}")
    
    def create_client(self, provider: Optional[APIProvider] = None, 
                     api_key: Optional[str] = None,
                     base_url: Optional[str] = None):
        """
        创建 API 客户端
        
        Args:
            provider: API 提供商，如果为 None 则使用当前提供商
            api_key: API 密钥，如果为 None 则从环境变量读取
            base_url: 自定义基础 URL
            
        Returns:
            API 客户端实例
        """
        from openai import AsyncOpenAI
        
        if provider is None:
            provider = self._current_provider
        
        config = self._providers.get(provider)
        
        # 确定 API key - 从传入参数或提供商配置读取
        if api_key is None:
            # 不再从环境变量读取，必须由调用方提供
            if config and hasattr(config, 'api_key'):
                # 如果提供商配置中有 api_key 属性，使用它（这个场景已被废弃）
                pass
            # api_key 应该由调用方直接传入
        
        # 确定 base_url
        if base_url is None:
            if config:
                base_url = config.base_url
            else:
                raise ValueError(f"未知的 API 提供商：{provider}")
        
        # 创建客户端
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        return client
    
    def validate_config(self, provider: APIProvider, config_dict: dict) -> bool:
        """
        验证配置是否有效
        
        Args:
            provider: API 提供商
            config_dict: 配置字典
            
        Returns:
            配置是否有效
        """
        required_fields = ['api_key', 'base_url', 'model_name']
        return all(field in config_dict for field in required_fields)


# 全局单例
_provider_manager: Optional[APIProviderManager] = None


def get_provider_manager() -> APIProviderManager:
    """获取全局提供商管理器实例"""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = APIProviderManager()
    return _provider_manager


def switch_provider(provider: APIProvider) -> None:
    """
    切换到指定的 API 提供商
    
    Args:
        provider: API 提供商枚举
    """
    manager = get_provider_manager()
    manager.set_provider(provider)


def get_current_provider() -> APIProvider:
    """获取当前 API 提供商"""
    manager = get_provider_manager()
    return manager.get_current_provider()


def create_api_client(provider: Optional[APIProvider] = None):
    """
    创建 API 客户端的便捷函数
    
    Args:
        provider: API 提供商，如果为 None 则使用当前提供商
        
    Returns:
        API 客户端实例
    """
    manager = get_provider_manager()
    return manager.create_client(provider)
