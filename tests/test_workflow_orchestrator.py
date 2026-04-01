"""
workflow_orchestrator.py 单元测试
测试工作流编排器类：WorkflowOrchestrator
"""
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from infrastructure.models import Config, FinalResult, TaskContext
from business_logic.terminology_manager import TerminologyManager
from business_logic.workflow_orchestrator import WorkflowOrchestrator


@pytest.fixture
def mock_config():
    """创建模拟配置"""
    config = MagicMock(spec=Config)
    config.api_key = 'test_key'
    config.base_url = 'https://api.test.com'
    config.model_name = 'test-model'
    config.temperature = 0.5
    config.initial_concurrency = 2
    config.max_concurrency = 4
    config.exact_match_score = 100
    config.enable_two_pass = True
    config.skip_review_if_local_hit = False
    # 添加缺失的属性
    config.max_retries = 3
    config.timeout = 30
    return config


@pytest.fixture
def mock_client():
    """创建模拟 OpenAI 客户端"""
    client = MagicMock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def mock_tm():
    """创建模拟术语库管理器"""
    tm = MagicMock(spec=TerminologyManager)
    tm.find_similar = AsyncMock()
    tm.add_entry = AsyncMock()
    return tm


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


class TestWorkflowOrchestratorInitialization:
    """工作流编排器初始化测试"""
    
    def test_orchestrator_init(self, mock_config, mock_client, mock_tm):
        """测试编排器初始化"""
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        assert orchestrator.config == mock_config
        assert orchestrator.client == mock_client
        assert orchestrator.tm == mock_tm
        assert orchestrator.draft_stage is not None
        assert orchestrator.review_stage is not None
        assert orchestrator.local_stage is not None
    
    def test_orchestrator_with_different_prompts(self, mock_config, mock_client, mock_tm):
        """测试使用不同提示词初始化"""
        custom_draft = "Custom draft prompt for {target_lang}"
        custom_review = "Custom review prompt for {target_lang}"
        
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            custom_draft, custom_review
        )
        
        assert orchestrator.draft_stage.system_prompt == custom_draft
        assert orchestrator.review_stage.system_prompt == custom_review


class TestProcessTaskNewTranslation:
    """新文档翻译模式测试"""
    
    @pytest.mark.asyncio
    async def test_new_translation_success(self, mock_config, mock_client, mock_tm):
        """测试新文档翻译成功场景"""
        # 设置术语库查询无结果
        mock_tm.find_similar.return_value = None
        
        # 设置 API 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"Trans": "Hello World", "Reason": "翻译完成"}'
        mock_client.chat.completions.create.return_value = mock_response
        
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='你好世界',
            target_lang='英语'
        )
        
        result = await orchestrator.process_task(ctx)
        
        assert isinstance(result, FinalResult)
        assert result.key == 'test'
        assert result.status in ['SUCCESS', 'LOCAL_HIT']
        assert result.final_trans == "Hello World"
        mock_tm.add_entry.assert_called()
    
    @pytest.mark.asyncio
    async def test_new_translation_with_exact_tm_hit(self, mock_config, mock_client, mock_tm):
        """测试新文档精确命中术语库"""
        # 设置精确匹配
        tm_suggestion = {
            'original': '你好世界',
            'translation': 'Hello World',
            'score': 100
        }
        mock_tm.find_similar.return_value = tm_suggestion
        
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='你好世界',
            target_lang='英语'
        )
        
        result = await orchestrator.process_task(ctx)
        
        assert result.status == 'SUCCESS'
        assert result.final_trans == "Hello World"
        assert result.diagnosis == "Local Hit (Skipped Review)" or result.draft_trans == "Hello World"
    
    @pytest.mark.asyncio
    async def test_new_translation_api_failure(self, mock_config, mock_client, mock_tm):
        """测试新文档翻译 API 失败"""
        # 设置术语库无结果
        mock_tm.find_similar.return_value = None
        
        # 设置 API 失败
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='你好世界',
            target_lang='英语'
        )
        
        result = await orchestrator.process_task(ctx)
        
        assert result.status in ['FAILED', 'ERROR']
        assert result.final_trans == "(Failed)"


class TestProcessTaskProofread:
    """旧文档校对模式测试"""
    
    @pytest.mark.asyncio
    async def test_proofread_exact_match(self, mock_config, mock_client, mock_tm):
        """测试校对模式精确匹配无需修改"""
        # 设置精确匹配且译文一致
        tm_suggestion = {
            'original': '你好世界',
            'translation': 'Hello World',
            'score': 100
        }
        mock_tm.find_similar.return_value = tm_suggestion
        
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='你好世界',
            original_trans='Hello World',
            target_lang='英语'
        )
        
        result = await orchestrator.process_task(ctx)
        
        assert result.status in ['SUCCESS', 'LOCAL_HIT']  # 本地命中也是成功
        assert result.final_trans == "Hello World"
        assert "No Change" in result.diagnosis or "TM" in result.diagnosis
        assert result.reason == ""
    
    @pytest.mark.asyncio
    async def test_proofread_ai_polish(self, mock_config, mock_client, mock_tm):
        """测试校对模式 AI 优化"""
        # 设置术语库建议但需要优化
        tm_suggestion = {
            'original': '你好世界',
            'translation': 'Hello Earth',
            'score': 80
        }
        mock_tm.find_similar.return_value = tm_suggestion
        
        # 设置 AI 校对响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"Trans": "Hello World", "Reason": "更准确的翻译"}'
        mock_client.chat.completions.create.return_value = mock_response
        
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='你好世界',
            original_trans='Hello Earth',
            target_lang='英语'
        )
        
        result = await orchestrator.process_task(ctx)
        
        assert result.status == 'SUCCESS'
        assert result.final_trans == "Hello World"
        assert "Proofread" in result.diagnosis or result.reason == "更准确的翻译"
        mock_tm.add_entry.assert_called()
    
    @pytest.mark.asyncio
    async def test_proofread_api_failure(self, mock_config, mock_client, mock_tm):
        """测试校对模式 API 失败"""
        # 设置术语库不匹配
        mock_tm.find_similar.return_value = None
        
        # 设置 API 失败
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='你好世界',
            original_trans='Old Translation',
            target_lang='英语'
        )
        
        result = await orchestrator.process_task(ctx)
        
        # API 失败时会保留原译文，状态为 ERROR
        assert result.status in ['FAILED', 'ERROR']
        assert result.final_trans in ["Old Translation", "(Error)"]


class TestTwoPassProcessing:
    """双阶段处理测试"""
    
    @pytest.mark.asyncio
    async def test_two_pass_enabled(self, mock_config, mock_client, mock_tm):
        """测试启用双阶段处理"""
        mock_config.enable_two_pass = True
        mock_config.skip_review_if_local_hit = False
        
        # 设置术语库无结果
        mock_tm.find_similar.return_value = None
        
        # 设置初译响应
        draft_response = MagicMock()
        draft_response.choices = [MagicMock()]
        draft_response.choices[0].message.content = '{"Trans": "Initial Draft", "Reason": ""}'
        
        # 设置校对响应
        review_response = MagicMock()
        review_response.choices = [MagicMock()]
        review_response.choices[0].message.content = '{"Trans": "Refined Draft", "Reason": "优化"}'
        
        mock_client.chat.completions.create.side_effect = [draft_response, review_response]
        
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='测试文本',
            target_lang='英语'
        )
        
        result = await orchestrator.process_task(ctx)
        
        assert result.status == 'SUCCESS'
        assert result.draft_trans == "Initial Draft"
        assert result.final_trans == "Refined Draft"
    
    @pytest.mark.asyncio
    async def test_skip_review_on_local_hit(self, mock_config, mock_client, mock_tm):
        """测试本地命中时跳过校对"""
        mock_config.enable_two_pass = True
        mock_config.skip_review_if_local_hit = True
        
        # 设置本地命中
        tm_suggestion = {
            'original': '测试',
            'translation': 'Test',
            'score': 100
        }
        mock_tm.find_similar.return_value = tm_suggestion
        
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='测试',
            target_lang='英语'
        )
        
        result = await orchestrator.process_task(ctx)
        
        assert result.status == 'SUCCESS'
        assert result.final_trans == "Test"


class TestMakeResult:
    """结果构建测试"""
    
    def test_make_result_success(self, mock_config, mock_client, mock_tm):
        """测试构建成功的结果"""
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='你好',
            original_trans='',
            target_lang='英语'
        )
        
        result = orchestrator._make_result(
            ctx=ctx,
            draft='Hello',
            final='Hello',
            reason='Direct translation',
            diag='Draft Only',
            status='SUCCESS'
        )
        
        assert isinstance(result, FinalResult)
        assert result.key == 'test'
        assert result.source_text == '你好'
        assert result.final_trans == 'Hello'
        assert result.status == 'SUCCESS'
    
    def test_make_result_failure(self, mock_config, mock_client, mock_tm):
        """测试构建失败的结果"""
        orchestrator = WorkflowOrchestrator(
            mock_config, mock_client, mock_tm,
            "Draft prompt", "Review prompt"
        )
        
        ctx = TaskContext(
            idx=0,
            key='test',
            source_text='你好',
            target_lang='英语'
        )
        
        result = orchestrator._make_result(
            ctx=ctx,
            draft='',
            final='(Failed)',
            reason='',
            diag='Stage 1 Failed',
            status='FAILED',
            error='API timeout'
        )
        
        assert result.status == 'FAILED'
        assert result.error_detail == 'API timeout'
        assert result.final_trans == '(Failed)'


class TestWorkflowOrchestratorIntegration:
    """工作流编排器集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_simulation(self):
        """测试完整工作流模拟"""
        # 使用真实配置
        config = Config(
            api_key='test_key',
            base_url='https://api.test.com',
            model_name='test-model',
            temperature=0.5,
            initial_concurrency=2,
            max_concurrency=4
        )
        
        # 创建模拟客户端和术语库
        with patch('openai.AsyncOpenAI') as MockClient:
            mock_client_instance = MagicMock()
            
            # 设置两次 API 调用响应（初译 + 校对）
            draft_response = MagicMock()
            draft_response.choices = [MagicMock()]
            draft_response.choices[0].message.content = '{"Trans": "Hello", "Reason": ""}'
            
            review_response = MagicMock()
            review_response.choices = [MagicMock()]
            review_response.choices[0].message.content = '{"Trans": "Hello Refined", "Reason": "优化"}'
            
            mock_client_instance.chat.completions.create.side_effect = [
                draft_response, review_response
            ]
            MockClient.return_value = mock_client_instance
            
            # 创建术语库 mock
            mock_tm_instance = MagicMock()
            mock_tm_instance.find_similar = AsyncMock(return_value=None)
            mock_tm_instance.add_entry = AsyncMock()
            
            orchestrator = WorkflowOrchestrator(
                config, mock_client_instance, mock_tm_instance,
                "Translate to {target_lang}",
                "Proofread {target_lang}"
            )
            
            ctx = TaskContext(
                idx=0,
                key='test',
                source_text='你好',
                target_lang='英语'
            )
            
            result = await orchestrator.process_task(ctx)
            
            assert isinstance(result, FinalResult)
            assert result.status == 'SUCCESS'
            assert mock_tm_instance.add_entry.called
