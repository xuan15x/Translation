"""
测试 API 阶段基类模块
验证抽象基类的功能和行为
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from service.api_stage_base import APIStageBase, APIDraftStage, APIReviewStage
from infrastructure.models import Config, StageResult, TaskContext
from infrastructure.concurrency_controller import AdaptiveConcurrencyController


class MockAPIStage(APIStageBase):
    """用于测试的模拟阶段"""
    
    def _get_stage_config(self) -> Dict[str, Any]:
        return {
            'model_name': 'test-model',
            'temperature': 0.5,
            'top_p': 0.8,
            'timeout': 30,
            'max_tokens': 512
        }
    
    def _build_messages(self, context: TaskContext) -> list:
        return [
            {"role": "system", "content": f"Translate to {context.target_lang}"},
            {"role": "user", "content": context.source_text}
        ]


@pytest.fixture
def mock_config():
    """创建模拟配置"""
    config = MagicMock(spec=Config)
    config.max_retries = 3
    config.base_retry_delay = 0.1
    return config


@pytest.fixture
def mock_controller():
    """创建模拟并发控制器"""
    controller = MagicMock(spec=AdaptiveConcurrencyController)
    controller.adjust = AsyncMock()
    return controller


@pytest.fixture
def semaphore():
    """创建信号量"""
    return asyncio.Semaphore(2)


@pytest.fixture
def stage(mock_config, mock_controller, semaphore):
    """创建测试阶段实例"""
    with patch('service.api_stage_base.AsyncOpenAI'):
        return MockAPIStage(
            client=MagicMock(),
            controller=mock_controller,
            semaphore=semaphore,
            config=mock_config,
            system_prompt="Test prompt"
        )


@pytest.mark.asyncio
async def test_extract_translation_valid(stage):
    """测试提取有效的翻译结果"""
    data = {"Trans": "Hello world", "Other": "data"}
    result = stage._extract_translation(data)
    assert result == "Hello world"


@pytest.mark.asyncio
async def test_extract_translation_empty(stage):
    """测试提取空的翻译结果"""
    data = {"Trans": "", "Other": "data"}
    result = stage._extract_translation(data)
    assert result is None


@pytest.mark.asyncio
async def test_extract_translation_missing_key(stage):
    """测试提取缺少键的翻译结果"""
    data = {"Other": "data"}
    result = stage._extract_translation(data)
    assert result is None


@pytest.mark.asyncio
async def test_get_stage_config(stage):
    """测试获取阶段配置"""
    config = stage._get_stage_config()
    assert config['model_name'] == 'test-model'
    assert config['temperature'] == 0.5
    assert config['top_p'] == 0.8
    assert config['timeout'] == 30
    assert config['max_tokens'] == 512


@pytest.mark.asyncio
async def test_build_messages(stage):
    """测试构建消息"""
    context = TaskContext(
        row_id=1,
        source_text="Hello",
        target_lang="Chinese",
        tm_suggestion=None
    )
    messages = stage._build_messages(context)
    assert len(messages) == 2
    assert messages[0]['role'] == 'system'
    assert messages[1]['role'] == 'user'
    assert "Chinese" in messages[0]['content']
    assert messages[1]['content'] == "Hello"


@pytest.mark.asyncio
async def test_draft_stage_config():
    """测试初译阶段配置"""
    mock_config = MagicMock(spec=Config)
    mock_config.get_draft_model_name.return_value = 'draft-model'
    mock_config.get_draft_temperature.return_value = 0.3
    mock_config.get_draft_top_p.return_value = 0.8
    mock_config.get_draft_timeout.return_value = 60
    mock_config.get_draft_max_tokens.return_value = 512
    
    with patch('service.api_stage_base.AsyncOpenAI'):
        stage = APIDraftStage(
            client=MagicMock(),
            controller=MagicMock(),
            semaphore=asyncio.Semaphore(2),
            config=mock_config,
            system_prompt="Draft prompt"
        )
    
    config = stage._get_stage_config()
    assert config['model_name'] == 'draft-model'
    assert config['temperature'] == 0.3
    assert config['max_tokens'] == 512


@pytest.mark.asyncio
async def test_review_stage_config():
    """测试校对阶段配置"""
    mock_config = MagicMock(spec=Config)
    mock_config.get_review_model_name.return_value = 'review-model'
    mock_config.get_review_temperature.return_value = 0.5
    mock_config.get_review_top_p.return_value = 0.9
    mock_config.get_review_timeout.return_value = 90
    mock_config.get_review_max_tokens.return_value = 512
    
    with patch('service.api_stage_base.AsyncOpenAI'):
        stage = APIReviewStage(
            client=MagicMock(),
            controller=MagicMock(),
            semaphore=asyncio.Semaphore(2),
            config=mock_config,
            system_prompt="Review prompt"
        )
    
    config = stage._get_stage_config()
    assert config['model_name'] == 'review-model'
    assert config['temperature'] == 0.5
    assert config['max_tokens'] == 512


@pytest.mark.asyncio
async def test_review_stage_execute():
    """测试校对阶段执行"""
    mock_config = MagicMock(spec=Config)
    mock_config.get_review_model_name.return_value = 'review-model'
    mock_config.get_review_temperature.return_value = 0.5
    mock_config.get_review_top_p.return_value = 0.9
    mock_config.get_review_timeout.return_value = 90
    mock_config.get_review_max_tokens.return_value = 512
    mock_config.max_retries = 3
    mock_config.base_retry_delay = 0.1
    
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '```json\n{"Trans": "Polished text", "Reason": "Better flow"}\n```'
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    mock_controller = MagicMock(spec=AdaptiveConcurrencyController)
    mock_controller.adjust = AsyncMock()
    
    with patch('service.api_stage_base.AsyncOpenAI', return_value=mock_client):
        stage = APIReviewStage(
            client=mock_client,
            controller=mock_controller,
            semaphore=asyncio.Semaphore(2),
            config=mock_config,
            system_prompt="Review prompt"
        )
        
        context = TaskContext(
            row_id=1,
            source_text="Original text",
            target_lang="Chinese",
            tm_suggestion=None,
            draft_translation="Draft text"
        )
        
        result = await stage.execute(context, "Draft text")
        
        assert isinstance(result, StageResult)
        assert result.success is True
        assert result.translation == "Polished text"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
