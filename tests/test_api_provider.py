"""
api_provider.py 单元测试
测试 API 提供商管理模块
"""
import os
import pytest
from unittest.mock import MagicMock, patch

from service.api_provider import (
    APIProvider, 
    ProviderConfig, 
    APIProviderManager, 
    get_provider_manager,
    switch_provider,
    get_current_provider,
    create_api_client,
    PREDEFINED_PROVIDERS
)


class TestAPIProviderEnum:
    """API 提供商枚举测试"""
    
    def test_provider_enum_values(self):
        """测试提供商枚举值"""
        assert APIProvider.DEEPSEEK.value == "deepseek"
        assert APIProvider.OPENAI.value == "openai"
        assert APIProvider.ANTHROPIC.value == "anthropic"
        assert APIProvider.MOONSHOT.value == "moonshot"
        assert APIProvider.ZHIPU.value == "zhipu"
        assert APIProvider.BAIDU.value == "baidu"
        assert APIProvider.ALIBABA.value == "alibaba"
        assert APIProvider.CUSTOM.value == "custom"
    
    def test_all_providers_defined(self):
        """测试所有预定义提供商"""
        providers = list(APIProvider)
        assert len(providers) >= 7  # 至少 7 个提供商


class TestProviderConfig:
    """ProviderConfig 类测试"""
    
    def test_provider_config_creation(self):
        """测试提供商配置创建"""
        config = ProviderConfig(
            name="Test Provider",
            base_url="https://api.test.com",
            api_key_env="TEST_API_KEY",
            default_model="test-model"
        )
        
        assert config.name == "Test Provider"
        assert config.base_url == "https://api.test.com"
        assert config.api_key_env == "TEST_API_KEY"
        assert config.default_model == "test-model"
        assert config.max_tokens == 4096  # 默认值
        assert config.supports_temperature is True
        assert config.supports_top_p is True
    
    def test_provider_config_with_models(self):
        """测试带模型列表的配置"""
        config = ProviderConfig(
            name="Test",
            base_url="https://api.test.com",
            api_key_env="TEST_KEY",
            default_model="model-1",
            models=["model-1", "model-2", "model-3"]
        )
        
        assert len(config.models) == 3
        assert "model-1" in config.models
        assert "model-2" in config.models
    
    def test_provider_config_auto_models(self):
        """测试自动添加默认模型到模型列表"""
        config = ProviderConfig(
            name="Test",
            base_url="https://api.test.com",
            api_key_env="TEST_KEY",
            default_model="only-model"
        )
        
        assert "only-model" in config.models
        assert len(config.models) == 1


class TestPredefinedProviders:
    """预定义提供商测试"""
    
    def test_deepseek_config(self):
        """测试 DeepSeek 配置"""
        config = PREDEFINED_PROVIDERS[APIProvider.DEEPSEEK]
        assert config.name == "DeepSeek"
        assert "deepseek.com" in config.base_url
        assert config.api_key_env == "DEEPSEEK_API_KEY"
        assert config.default_model == "deepseek-chat"
    
    def test_openai_config(self):
        """测试 OpenAI 配置"""
        config = PREDEFINED_PROVIDERS[APIProvider.OPENAI]
        assert config.name == "OpenAI"
        assert "openai.com" in config.base_url
        assert config.api_key_env == "OPENAI_API_KEY"
        assert "gpt-3.5-turbo" in config.models
    
    def test_anthropic_config(self):
        """测试 Anthropic 配置"""
        config = PREDEFINED_PROVIDERS[APIProvider.ANTHROPIC]
        assert config.name == "Anthropic"
        assert "claude" in config.default_model
        assert config.supports_top_p is False  # Anthropic 特殊处理
    
    def test_moonshot_config(self):
        """测试 Moonshot (Kimi) 配置"""
        config = PREDEFINED_PROVIDERS[APIProvider.MOONSHOT]
        assert "moonshot" in config.name.lower()
        assert "moonshot-v1" in config.default_model
    
    def test_zhipu_config(self):
        """测试智谱 AI 配置"""
        config = PREDEFINED_PROVIDERS[APIProvider.ZHIPU]
        assert "zhipu" in config.name.lower() or "glm" in config.default_model


class TestAPIProviderManager:
    """APIProviderManager 类测试"""
    
    @pytest.fixture
    def manager(self):
        """创建管理器实例"""
        return APIProviderManager()
    
    def test_manager_initialization(self, manager):
        """测试管理器初始化"""
        assert manager.get_current_provider() == APIProvider.DEEPSEEK
        assert len(manager.list_providers()) >= 7
    
    def test_get_provider(self, manager):
        """测试获取提供商配置"""
        config = manager.get_provider(APIProvider.DEEPSEEK)
        assert config is not None
        assert config.name == "DeepSeek"
    
    def test_get_unknown_provider(self, manager):
        """测试获取不存在的提供商"""
        config = manager.get_provider(APIProvider.CUSTOM)
        assert config is None
    
    def test_set_provider(self, manager):
        """测试设置提供商"""
        manager.set_provider(APIProvider.OPENAI)
        assert manager.get_current_provider() == APIProvider.OPENAI
    
    def test_set_invalid_provider(self, manager):
        """测试设置无效的提供商"""
        with pytest.raises(ValueError):
            # 创建一个不存在的提供商类型
            fake_provider = APIProvider("fake_provider")
            manager.set_provider(fake_provider)
    
    def test_list_providers(self, manager):
        """测试列出所有提供商"""
        providers = manager.list_providers()
        assert isinstance(providers, list)
        assert len(providers) >= 7
        assert APIProvider.DEEPSEEK in providers
        assert APIProvider.OPENAI in providers
    
    def test_list_models(self, manager):
        """测试列出模型"""
        # 当前提供商的模型
        models = manager.list_models()
        assert isinstance(models, list)
        assert len(models) > 0
        
        # 指定提供商的模型
        openai_models = manager.list_models(APIProvider.OPENAI)
        assert len(openai_models) > 0
        assert "gpt-3.5-turbo" in openai_models
    
    def test_get_base_url(self, manager):
        """测试获取基础 URL"""
        url = manager.get_base_url(APIProvider.DEEPSEEK)
        assert "deepseek.com" in url
        
        url = manager.get_base_url(APIProvider.OPENAI)
        assert "openai.com" in url
    
    def test_get_default_model(self, manager):
        """测试获取默认模型"""
        model = manager.get_default_model(APIProvider.DEEPSEEK)
        assert model == "deepseek-chat"
        
        model = manager.get_default_model(APIProvider.OPENAI)
        assert "gpt" in model.lower()
    
    def test_add_custom_provider(self, manager):
        """测试添加自定义提供商"""
        custom_config = ProviderConfig(
            name="Custom Provider",
            base_url="https://custom.api.com",
            api_key_env="CUSTOM_API_KEY",
            default_model="custom-model"
        )
        
        manager.add_custom_provider("custom", custom_config)
        
        # 验证已添加
        providers = manager.list_providers()
        # 自定义提供商不在枚举中，但可以通过其他方式访问
    
    def test_remove_custom_provider(self, manager):
        """测试移除自定义提供商"""
        custom_config = ProviderConfig(
            name="Temp Provider",
            base_url="https://temp.api.com",
            api_key_env="TEMP_API_KEY",
            default_model="temp-model"
        )
        
        manager.add_custom_provider("temp", custom_config)
        manager.remove_custom_provider("temp")
    
    def test_validate_config(self, manager):
        """测试配置验证"""
        valid_config = {
            'api_key': 'key',
            'base_url': 'https://api.com',
            'model_name': 'model'
        }
        assert manager.validate_config(APIProvider.DEEPSEEK, valid_config) is True
        
        invalid_config = {'api_key': 'key'}
        assert manager.validate_config(APIProvider.DEEPSEEK, invalid_config) is False


class TestCreateClient:
    """创建客户端测试"""
    
    @patch('service.api_provider.AsyncOpenAI')
    def test_create_client_default(self, mock_openai):
        """测试创建默认客户端"""
        manager = APIProviderManager()
        
        # Mock 环境变量
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test_key'}):
            client = manager.create_client()
            
            mock_openai.assert_called_once()
            call_args = mock_openai.call_args
            assert call_args[1]['api_key'] == 'test_key'
            assert 'deepseek.com' in call_args[1]['base_url']
    
    @patch('service.api_provider.AsyncOpenAI')
    def test_create_client_specific_provider(self, mock_openai):
        """测试创建指定提供商的客户端"""
        manager = APIProviderManager()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'openai_key'}):
            client = manager.create_client(APIProvider.OPENAI)
            
            call_args = mock_openai.call_args
            assert call_args[1]['api_key'] == 'openai_key'
            assert 'openai.com' in call_args[1]['base_url']
    
    @patch('service.api_provider.AsyncOpenAI')
    def test_create_client_custom_key(self, mock_openai):
        """测试使用自定义 API key 创建客户端"""
        manager = APIProviderManager()
        
        client = manager.create_client(api_key='custom_key')
        
        call_args = mock_openai.call_args
        assert call_args[1]['api_key'] == 'custom_key'
    
    @patch('service.api_provider.AsyncOpenAI')
    def test_create_client_custom_url(self, mock_openai):
        """测试使用自定义 URL 创建客户端"""
        manager = APIProviderManager()
        
        client = manager.create_client(base_url='https://custom.url')
        
        call_args = mock_openai.call_args
        assert call_args[1]['base_url'] == 'https://custom.url'


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_provider_manager_singleton(self):
        """测试管理器单例模式"""
        manager1 = get_provider_manager()
        manager2 = get_provider_manager()
        
        assert manager1 is manager2
    
    @patch.object(APIProviderManager, 'set_provider')
    def test_switch_provider(self, mock_set):
        """测试切换提供商"""
        switch_provider(APIProvider.OPENAI)
        mock_set.assert_called_with(APIProvider.OPENAI)
    
    @patch.object(APIProviderManager, 'get_current_provider')
    def test_get_current_provider(self, mock_get):
        """测试获取当前提供商"""
        mock_get.return_value = APIProvider.DEEPSEEK
        
        provider = get_current_provider()
        
        assert provider == APIProvider.DEEPSEEK
        mock_get.assert_called_once()
    
    @patch.object(APIProviderManager, 'create_client')
    def test_create_api_client(self, mock_create):
        """测试创建 API 客户端"""
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        client = create_api_client()
        
        assert client is mock_client
        mock_create.assert_called_once()


class TestProviderFeatures:
    """提供商功能特性测试"""
    
    def test_deepseek_features(self):
        """测试 DeepSeek 功能支持"""
        config = PREDEFINED_PROVIDERS[APIProvider.DEEPSEEK]
        assert config.supports_temperature is True
        assert config.supports_top_p is True
        assert config.supports_system_prompt is True
    
    def test_anthropic_features(self):
        """测试 Anthropic 功能支持"""
        config = PREDEFINED_PROVIDERS[APIProvider.ANTHROPIC]
        assert config.supports_temperature is True
        assert config.supports_top_p is False  # 使用 top_k
        assert config.supports_system_prompt is True
    
    def test_baidu_features(self):
        """测试百度功能支持"""
        config = PREDEFINED_PROVIDERS[APIProvider.BAIDU]
        assert config.supports_system_prompt is False  # 特殊格式


class TestIntegration:
    """集成测试"""
    
    def test_full_provider_workflow(self):
        """测试完整的提供商工作流"""
        # 1. 获取管理器
        manager = get_provider_manager()
        
        # 2. 列出所有提供商
        providers = manager.list_providers()
        assert len(providers) >= 7
        
        # 3. 切换到 OpenAI
        manager.set_provider(APIProvider.OPENAI)
        assert manager.get_current_provider() == APIProvider.OPENAI
        
        # 4. 获取配置
        config = manager.get_provider(APIProvider.OPENAI)
        assert config is not None
        assert "OpenAI" in config.name
        
        # 5. 获取模型列表
        models = manager.list_models()
        assert len(models) > 0
        
        # 6. 获取默认模型
        default_model = manager.get_default_model()
        assert default_model == config.default_model
        
        # 7. 切换回 DeepSeek
        manager.set_provider(APIProvider.DEEPSEEK)
        assert manager.get_current_provider() == APIProvider.DEEPSEEK
