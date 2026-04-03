"""
api_stages.py 单元测试
测试 API 处理阶段：APIDraftStage, APIReviewStage, LocalHitStage
"""
import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from infrastructure.models import Config, StageResult, TaskContext
from infrastructure.utils import AdaptiveConcurrencyController
from service.api_stages import APIDraftStage, APIReviewStage


@pytest.fixture
def mock_config():
    """创建模拟配置"""
    config = MagicMock(spec=Config)
    config.model_name = "test-model"
    config.temperature = 0.5
    config.top_p = 0.8
    config.max_retries = 3
    config.base_retry_delay = 0.1
    config.timeout = 30
    return config


@pytest.fixture
def mock_controller():
    """创建模拟并发控制器"""
    controller = MagicMock(spec=AdaptiveConcurrencyController)
    controller.adjust = AsyncMock()
    return controller


@pytest.fixture
def mock_semaphore():
    """创建模拟信号量"""
    semaphore = MagicMock(spec=asyncio.Semaphore)
    semaphore.__aenter__ = AsyncMock(return_value=None)
    semaphore.__aexit__ = AsyncMock(return_value=None)
    return semaphore


@pytest.fixture
def mock_client():
    """创建模拟 OpenAI 客户端"""
    client = MagicMock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def sample_context():
    """创建示例任务上下文"""
    return TaskContext(
        idx=0,
        key='test_key',
        source_text='你好世界',
        original_trans='',
        target_lang='英语'
    )


class TestAPIDraftStage:
    """APIDraftStage 类测试"""
    
    @pytest.mark.asyncio
    async def test_draft_stage_success(self, mock_client, mock_controller, 
                                        mock_semaphore, mock_config, sample_context):
        """测试初译阶段成功场景"""
        # 设置 mock 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"Trans": "Hello World", "Reason": "翻译完成"}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # 创建阶段实例
        stage = APIDraftStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a translator to {target_lang}"
        )
        
        # 执行测试
        result = await stage.execute(sample_context)
        
        # 验证结果
        assert result.success is True
        assert result.translation == "Hello World"
        assert result.reason == "翻译完成"
        assert result.source == "API"
        mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_draft_stage_invalid_json(self, mock_client, mock_controller,
                                             mock_semaphore, mock_config, sample_context):
        """测试初译阶段 JSON 解析失败"""
        # 设置无效的 JSON 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Invalid JSON Response'
        mock_client.chat.completions.create.return_value = mock_response
        
        stage = APIDraftStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a translator to {target_lang}"
        )
        
        result = await stage.execute(sample_context)
        
        assert result.success is False
        assert "Invalid JSON" in result.error_msg  # 使用包含匹配而非精确匹配
    
    @pytest.mark.asyncio
    async def test_draft_stage_empty_trans(self, mock_client, mock_controller,
                                            mock_semaphore, mock_config, sample_context):
        """测试初译阶段 Trans 字段为空"""
        # 设置空 Trans 的响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"Trans": "", "Reason": ""}'
        mock_client.chat.completions.create.return_value = mock_response
        
        stage = APIDraftStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a translator to {target_lang}"
        )
        
        result = await stage.execute(sample_context)
        
        assert result.success is False
        assert "Empty" in result.error_msg or "空" in result.error_msg  # 兼容不同的错误消息
    
    @pytest.mark.asyncio
    async def test_draft_stage_api_error(self, mock_client, mock_controller,
                                          mock_semaphore, mock_config, sample_context):
        """测试初译阶段 API 调用错误"""
        # 设置 API 错误
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        stage = APIDraftStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a translator to {target_lang}"
        )
        
        result = await stage.execute(sample_context)
        
        assert result.success is False
        assert "API Error" in result.error_msg
    
    @pytest.mark.asyncio
    async def test_draft_stage_with_code_block_json(self, mock_client, mock_controller,
                                                     mock_semaphore, mock_config, sample_context):
        """测试处理包含 markdown code block 的 JSON 响应"""
        # 设置带 markdown 的响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '```json\n{"Trans": "Hello", "Reason": "OK"}\n```'
        mock_client.chat.completions.create.return_value = mock_response
        
        stage = APIDraftStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a translator to {target_lang}"
        )
        
        result = await stage.execute(sample_context)
        
        assert result.success is True
        assert result.translation == "Hello"
    
    @pytest.mark.asyncio
    async def test_draft_stage_max_retries(self, mock_client, mock_controller,
                                            mock_semaphore, mock_config, sample_context):
        """测试达到最大重试次数"""
        # 设置持续返回无效 JSON
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Invalid'
        mock_client.chat.completions.create.return_value = mock_response
        
        stage = APIDraftStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a translator to {target_lang}"
        )
        
        result = await stage.execute(sample_context)
        
        assert result.success is False
        assert "Invalid JSON" in result.error_msg  # 使用包含匹配而非精确匹配


class TestAPIReviewStage:
    """APIReviewStage 类测试"""
    
    @pytest.mark.asyncio
    async def test_review_stage_success(self, mock_client, mock_controller,
                                         mock_semaphore, mock_config, sample_context):
        """测试校对阶段成功场景"""
        # 设置 mock 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"Trans": "Hello World Refined", "Reason": "优化表达"}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # 创建阶段实例
        stage = APIReviewStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a proofreader for {target_lang}"
        )
        
        # 执行测试
        result = await stage.execute(sample_context, "Hello World")
        
        # 验证结果
        assert result.success is True
        assert result.translation == "Hello World Refined"
        assert result.reason == "优化表达"
        assert result.source == "API"
    
    @pytest.mark.asyncio
    async def test_review_stage_no_change_needed(self, mock_client, mock_controller,
                                                  mock_semaphore, mock_config, sample_context):
        """测试校对阶段无需修改"""
        # 设置无需修改的响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"Trans": "Hello World", "Reason": "无需修改"}'
        mock_client.chat.completions.create.return_value = mock_response
        
        stage = APIReviewStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a proofreader for {target_lang}"
        )
        
        result = await stage.execute(sample_context, "Hello World")
        
        assert result.success is True
        assert result.translation == "Hello World"
        assert result.reason == "无需修改"


class TestLocalHitStage:
    """LocalHitStage 类测试"""
    
    @pytest.mark.asyncio
    async def test_local_hit_success(self, sample_context):
        """测试本地术语命中成功场景"""
        # 设置术语库建议
        sample_context.tm_suggestion = {
            'original': '你好',
            'translation': 'Hello',
            'score': 100
        }
        
        # 创建阶段实例
        stage = LocalHitStage()
        
        # 执行测试
        result = await stage.execute(sample_context)
        
        # 验证结果
        assert result.success is True
        assert result.translation == "Hello"
        assert result.source == "LOCAL_HIT"
    
    @pytest.mark.asyncio
    async def test_local_hit_no_suggestion(self, sample_context):
        """测试本地术语无建议"""
        # 确保没有术语库建议
        sample_context.tm_suggestion = None
        
        stage = LocalHitStage()
        result = await stage.execute(sample_context)
        
        assert result.success is False
        assert result.source == "NONE"
    
    @pytest.mark.asyncio
    async def test_local_hit_partial_match(self, sample_context):
        """测试本地术语部分匹配"""
        # 设置部分匹配的建议
        sample_context.tm_suggestion = {
            'original': '你好世界',
            'translation': 'Hello World',
            'score': 80
        }
        
        stage = LocalHitStage()
        result = await stage.execute(sample_context)
        
        assert result.success is True
        assert result.translation == "Hello World"
        assert result.source == "LOCAL_HIT"


class TestAPIDraftStageIntegration:
    """APIDraftStage 集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_api_call_simulation(self):
        """测试完整的 API 调用模拟"""
        # 使用真实的配置对象
        config = Config(
            api_key='test_key',
            base_url='https://api.test.com',
            model_name='test-model',
            temperature=0.5,
            initial_concurrency=2,
            max_concurrency=4
        )
        
        # 创建真实但被 mock 的客户端
        with patch('openai.AsyncOpenAI') as MockClient:
            mock_client_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '{"Trans": "Test Translation", "Reason": "Success"}'
            mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            MockClient.return_value = mock_client_instance
            
            controller = AdaptiveConcurrencyController(config)
            semaphore = asyncio.Semaphore(2)
            
            stage = APIDraftStage(
                mock_client_instance, controller, semaphore, config,
                "Translate to {target_lang}"
            )
            
            ctx = TaskContext(
                idx=0,
                key='test',
                source_text='测试文本',
                target_lang='英语'
            )
            
            result = await stage.execute(ctx)
            
            assert result.success is True
            assert result.translation == "Test Translation"
            assert result.source == "API"


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self, mock_client, mock_controller,
                                              mock_semaphore, mock_config, sample_context):
        """测试 429 限流错误处理"""
        # 设置 429 错误
        mock_client.chat.completions.create.side_effect = Exception("429 Too Many Requests")
        
        stage = APIDraftStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a translator to {target_lang}"
        )
        
        result = await stage.execute(sample_context)
        
        # 应该会重试直到失败
        assert result.success is False
        assert mock_client.chat.completions.create.call_count <= mock_config.max_retries
    
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, mock_client, mock_controller,
                                          mock_semaphore, mock_config, sample_context):
        """测试超时错误处理"""
        # 设置超时错误
        mock_client.chat.completions.create.side_effect = Exception("Request timeout")
        
        stage = APIDraftStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a translator to {target_lang}"
        )
        
        result = await stage.execute(sample_context)
        
        assert result.success is False
