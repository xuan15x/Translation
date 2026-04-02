"""
models.py 单元测试
测试数据模型类：Config, TaskContext, StageResult, FinalResult
"""
import os
import pytest
from dataclasses import asdict

from infrastructure.models import Config, TaskContext, StageResult, FinalResult


class TestConfig:
    """Config 类测试"""
    
    def test_config_default_initialization(self):
        """测试配置默认初始化 - 需要显式提供 api_key"""
        # 临时禁用日志
        import logging
        logging.disable(logging.CRITICAL)
        
        try:
            # 现在必须显式提供 api_key，不再从环境变量读取
            config = Config(api_key='test_key')
            
            assert config.api_key == 'test_key'
            assert config.base_url == "https://api.deepseek.com"
            assert config.model_name == "deepseek-chat"
            assert config.temperature == 0.3
            assert config.top_p == 0.8
            assert config.initial_concurrency == 8
            assert config.max_concurrency == 10
        finally:
            # 恢复日志
            logging.disable(logging.NOTSET)
    
    def test_config_custom_initialization(self):
        """测试配置自定义初始化"""
        config = Config(
            api_key='custom_key',
            base_url='https://custom.api.com',
            model_name='custom-model',
            temperature=0.7,
            initial_concurrency=4,
            max_concurrency=8
        )
        
        assert config.api_key == 'custom_key'
        assert config.base_url == 'https://custom.api.com'
        assert config.model_name == 'custom-model'
        assert config.temperature == 0.7
        assert config.initial_concurrency == 4
        assert config.max_concurrency == 8
    
    def test_config_missing_api_key(self):
        """测试缺少 API key 时抛出异常"""
        # 清除测试模式，确保正常验证
        if 'TEST_MODE' in os.environ:
            del os.environ['TEST_MODE']
        
        # 临时禁用日志
        import logging
        logging.disable(logging.CRITICAL)

        try:
            # 不提供 api_key 应该抛出 AuthenticationError
            with pytest.raises(Exception):  # 可能是 AuthenticationError 或 RuntimeError
                Config()
        finally:
            # 恢复日志
            logging.disable(logging.NOTSET)

    def test_config_dataclass_fields(self):
        """测试配置的数据类字段"""
        # 设置测试模式以跳过验证
        os.environ['TEST_MODE'] = 'skip_all'
        
        config = Config(api_key='test')
        config_dict = asdict(config)

        expected_fields = [
            'api_key', 'base_url', 'model_name', 'temperature', 'top_p',
            'initial_concurrency', 'max_concurrency', 'retry_streak_threshold',
            'base_retry_delay', 'max_retries', 'timeout', 'enable_two_pass',
            'skip_review_if_local_hit', 'batch_size', 'gc_interval',
            'similarity_low', 'exact_match_score', 'multiprocess_threshold',
            'concurrency_cooldown_seconds'
        ]

        for field in expected_fields:
            assert field in config_dict


class TestTaskContext:
    """TaskContext 类测试"""
    
    def test_task_context_minimal_initialization(self):
        """测试任务上下文最小化初始化"""
        ctx = TaskContext(idx=0, key='test', source_text='你好')
        
        assert ctx.idx == 0
        assert ctx.key == 'test'
        assert ctx.source_text == '你好'
        assert ctx.original_trans == ''
        assert ctx.target_lang == '英语'
        assert ctx.tm_suggestion is None
        assert ctx.is_exact_hit is False
    
    def test_task_context_full_initialization(self):
        """测试任务上下文完整初始化"""
        tm_suggestion = {
            'original': '你好',
            'translation': 'Hello',
            'score': 100
        }
        
        ctx = TaskContext(
            idx=1,
            key='key_1',
            source_text='世界',
            original_trans='World',
            target_lang='日语',
            tm_suggestion=tm_suggestion,
            is_exact_hit=True
        )
        
        assert ctx.idx == 1
        assert ctx.key == 'key_1'
        assert ctx.source_text == '世界'
        assert ctx.original_trans == 'World'
        assert ctx.target_lang == '日语'
        assert ctx.tm_suggestion == tm_suggestion
        assert ctx.is_exact_hit is True
    
    def test_task_context_mutable(self):
        """测试任务上下文的可变性"""
        ctx = TaskContext(idx=0, key='test', source_text='你好')
        
        # 修改属性
        ctx.target_lang = '法语'
        ctx.is_exact_hit = True
        
        assert ctx.target_lang == '法语'
        assert ctx.is_exact_hit is True


class TestStageResult:
    """StageResult 类测试"""
    
    def test_stage_result_success(self):
        """测试成功的阶段结果"""
        result = StageResult(
            success=True,
            translation='Hello',
            reason='翻译完成',
            source='API'
        )
        
        assert result.success is True
        assert result.translation == 'Hello'
        assert result.reason == '翻译完成'
        assert result.error_msg is None
        assert result.source == 'API'
    
    def test_stage_result_failure(self):
        """测试失败的阶段结果"""
        result = StageResult(
            success=False,
            translation='',
            error_msg='API Error',
            source='API'
        )
        
        assert result.success is False
        assert result.translation == ''
        assert result.error_msg == 'API Error'
        assert result.reason == ''
    
    def test_stage_result_default_values(self):
        """测试阶段结果默认值"""
        result = StageResult(success=True, translation='Test')

        assert result.reason == ''
        assert result.error_msg is None
        assert result.source == ''  # 默认值为空字符串


class TestFinalResult:
    """FinalResult 类测试"""
    
    def test_final_result_success(self):
        """测试成功的最终结果"""
        result = FinalResult(
            key='test_key',
            target_lang='英语',
            source_text='你好世界',
            final_trans='Hello World',
            status='SUCCESS'
        )
        
        assert result.key == 'test_key'
        assert result.target_lang == '英语'
        assert result.source_text == '你好世界'
        assert result.final_trans == 'Hello World'
        assert result.status == 'SUCCESS'
        assert result.error_detail is None
    
    def test_final_result_failure(self):
        """测试失败的最终结果"""
        result = FinalResult(
            key='test_key',
            target_lang='英语',
            source_text='你好',
            final_trans='(Failed)',
            status='FAILED',
            error_detail='API timeout'
        )
        
        assert result.status == 'FAILED'
        assert result.error_detail == 'API timeout'
        assert result.final_trans == '(Failed)'
    
    def test_final_result_dataclass_conversion(self):
        """测试最终结果转换为字典"""
        result = FinalResult(
            key='test',
            target_lang='英语',
            source_text='测试',
            final_trans='Test',
            status='SUCCESS'
        )
        
        result_dict = asdict(result)
        
        assert isinstance(result_dict, dict)
        assert result_dict['key'] == 'test'
        assert result_dict['final_trans'] == 'Test'
        assert result_dict['status'] == 'SUCCESS'


class TestDataModelIntegration:
    """数据模型集成测试"""
    
    def test_task_context_to_final_result_flow(self):
        """测试从任务上下文到最终结果的转换流程"""
        # 创建任务上下文
        ctx = TaskContext(
            idx=0,
            key='key_1',
            source_text='你好',
            target_lang='英语'
        )
        
        # 模拟处理过程
        draft_trans = 'Hello'
        final_trans = 'Hello'
        
        # 创建最终结果
        result = FinalResult(
            key=ctx.key,
            target_lang=ctx.target_lang,
            source_text=ctx.source_text,
            final_trans=final_trans,
            status='SUCCESS'
        )
        
        # 验证数据一致性
        assert result.key == ctx.key
        assert result.target_lang == ctx.target_lang
        assert result.source_text == ctx.source_text
        assert result.status == 'SUCCESS'
