"""
测试基础设施和共享 fixtures
"""
import os
import sys
import asyncio
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入所有待测试的模块
from infrastructure.models import Config, TaskContext, StageResult, FinalResult
from config import DEFAULT_DRAFT_PROMPT, DEFAULT_REVIEW_PROMPT, TARGET_LANGUAGES

# 导入测试数据管理器
from test_data_manager import (
    TestDataManager,
    TestDataSet,
    get_test_data_manager,
    setup_test_data,
    cleanup_test_data
)


@pytest.fixture(scope="session")
def test_data_dir():
    """获取测试数据目录路径"""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_excel_file():
    """创建临时 Excel 文件用于测试"""
    import pandas as pd
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        temp_path = f.name
    
    # 创建示例数据
    df = pd.DataFrame({
        'key': ['test_1', 'test_2'],
        '中文原文': ['你好', '世界'],
        '原译文': ['Hello', 'World']
    })
    df.to_excel(temp_path, index=False, engine='openpyxl')
    
    yield temp_path
    
    # 清理临时文件
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def sample_config():
    """创建示例配置对象"""
    # 设置测试模式，跳过配置验证
    os.environ['TEST_MODE'] = 'skip_all'
    
    # 使用模拟的 API key 进行测试，不再依赖环境变量
    return Config(
        api_key='test_api_key_for_unit_tests',
        base_url='https://api.test.com',
        model_name='test-model',
        temperature=0.5,
        initial_concurrency=2,
        max_concurrency=4,
        batch_size=10,
        similarity_low=60,
        multiprocess_threshold=5
    )


@pytest.fixture
def sample_task_context():
    """创建示例任务上下文"""
    return TaskContext(
        idx=0,
        key='test_key',
        source_text='你好世界',
        original_trans='',
        target_lang='英语',
        tm_suggestion=None,
        is_exact_hit=False
    )


@pytest.fixture
def sample_stage_result():
    """创建示例阶段结果（精简版）"""
    return StageResult(
        success=True,
        translation='Hello World'
    )


@pytest.fixture
def sample_final_result():
    """创建示例最终结果（精简版）"""
    return FinalResult(
        key='test_key',
        target_lang='英语',
        source_text='你好世界',
        final_trans='Hello World',
        status='SUCCESS',
        error_detail=None
    )


@pytest.fixture
def mock_openai_client(mocker):
    """创建 Mock OpenAI 客户端"""
    mock_client = mocker.MagicMock()
    
    # 设置 mock 响应
    mock_response = mocker.MagicMock()
    mock_response.choices = [mocker.MagicMock()]
    mock_response.choices[0].message.content = '{"Trans": "Hello", "Reason": ""}'
    
    mock_client.chat.completions.create = mocker.AsyncMock(return_value=mock_response)
    
    return mock_client


@pytest.fixture
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_performance_config():
    """性能测试配置"""
    config = Config()
    config.batch_size = 20
    config.max_concurrency = 5
    config.timeout = 30
    return config


@pytest.fixture
def test_data_generator():
    """测试数据生成器 fixture"""
    return TestDataManager()


@pytest.fixture
def small_test_data(test_data_generator):
    """小型测试数据集"""
    term_file = test_data_generator.create_test_terminology(count=10)
    source_file = test_data_generator.create_test_source(count=5)
    
    yield {
        'term_file': term_file,
        'source_file': source_file
    }
    
    test_data_generator.cleanup()


@pytest.fixture
def medium_test_data(test_data_generator):
    """中型测试数据集"""
    term_file = test_data_generator.create_test_terminology(count=100)
    source_file = test_data_generator.create_test_source(count=50)
    
    yield {
        'term_file': term_file,
        'source_file': source_file
    }
    
    test_data_generator.cleanup()


@pytest.fixture
def performance_monitor_fixture():
    """性能监控器 fixture"""
    from infrastructure.utils import PerformanceMonitor
    
    monitor = PerformanceMonitor(sample_interval=0.5)
    asyncio.run(monitor.start())
    
    yield monitor
    
    asyncio.run(monitor.stop())
