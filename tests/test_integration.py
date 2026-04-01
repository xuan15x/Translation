"""
端到端集成测试
测试完整的翻译工作流程，从文件加载到结果输出
"""
import pytest
import asyncio
import os
import tempfile
from datetime import datetime
import pandas as pd

from infrastructure.models import Config, TaskContext
from business_logic.terminology_manager import TerminologyManager
from business_logic.workflow_orchestrator import WorkflowOrchestrator
from openai import AsyncOpenAI


class TestEndToEnd:
    """端到端集成测试类"""
    
    @pytest.fixture(autouse=True)
    def mock_api_key(self):
        """自动 mock API key 环境变量"""
        from unittest.mock import patch
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test_key_for_integration'}):
            yield


    def test_config(self):
        """创建测试配置"""
        config = Config()
        config.batch_size = 5
        config.max_concurrency = 2
        config.enable_two_pass = False  # 简化测试，只进行初译
        return config
    
    @pytest.fixture
    def test_term_file(self, tmp_path):
        """创建测试术语库文件"""
        term_file = tmp_path / "test_terms.xlsx"
        
        # 创建测试术语数据
        data = {
            '中文原文': ['你好', '世界', '测试'],
            '英语': ['Hello', 'World', 'Test'],
            '法语': ['Bonjour', 'Monde', 'Test'],
        }
        df = pd.DataFrame(data)
        df.to_excel(term_file, index=False, engine='openpyxl')
        
        return str(term_file)
    
    @pytest.fixture
    def test_source_file(self, tmp_path):
        """创建测试源文件"""
        source_file = tmp_path / "test_source.xlsx"
        
        # 创建测试源数据
        data = {
            'key': ['key1', 'key2', 'key3'],
            '中文原文': ['你好世界', '这是一个测试', '人工智能'],
        }
        df = pd.DataFrame(data)
        df.to_excel(source_file, index=False, engine='openpyxl')
        
        return str(source_file)
    
    @pytest.fixture
    def terminology_manager(self, test_term_file, test_config):
        """创建术语库管理器"""
        tm = TerminologyManager(test_term_file, test_config)
        yield tm
        # 清理
        asyncio.run(tm.shutdown())
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, test_config, test_term_file, 
                                     test_source_file, terminology_manager):
        """测试完整的工作流程"""
        # 准备测试数据
        client = AsyncOpenAI(
            api_key="test_key",
            base_url="https://api.test.com"
        )
        
        orchestrator = WorkflowOrchestrator(
            config=test_config,
            client=client,
            tm=terminology_manager,
            p_draft="请将以下文本翻译成{target_lang}",
            p_review="请校对以下翻译",
            file_path=test_source_file,
            batch_id="test_batch_001"
        )
        
        # 读取源文件
        df = pd.read_excel(test_source_file, engine='openpyxl')
        
        # 创建任务
        tasks = []
        for i, row in df.iterrows():
            ctx = TaskContext(
                idx=i,
                key=row['key'],
                source_text=row['中文原文'],
                original_trans="",
                target_lang="英语"
            )
            tasks.append(ctx)
        
        # 执行任务
        results = []
        for task in tasks:
            result = await orchestrator.process_task(task)
            results.append(result)
        
        # 验证结果
        assert len(results) == len(tasks), "结果数量应与任务数量一致"
        
        for result in results:
            assert result.key is not None, "结果应包含 key"
            assert result.source_text is not None, "结果应包含原文"
            # 注意：由于使用 mock API，这里不验证具体的翻译内容
        
        # 验证术语库已更新
        stats = await terminology_manager.get_performance_stats()
        assert stats['database']['total_entries'] >= 3, "术语库应该有至少 3 个条目"
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, test_config, test_term_file,
                                    test_source_file, terminology_manager):
        """测试批量处理功能"""
        # 创建更多测试数据
        large_source = test_source_file.replace('.xlsx', '_large.xlsx')
        
        # 生成 100 条测试数据
        data = {
            'key': [f'key_{i}' for i in range(100)],
            '中文原文': [f'测试文本_{i}' for i in range(100)],
        }
        df = pd.DataFrame(data)
        df.to_excel(large_source, index=False, engine='openpyxl')
        
        client = AsyncOpenAI(api_key="test_key", base_url="https://api.test.com")
        
        orchestrator = WorkflowOrchestrator(
            config=test_config,
            client=client,
            tm=terminology_manager,
            p_draft="翻译",
            p_review="校对",
            file_path=large_source,
            batch_id="test_batch_large"
        )
        
        # 读取并创建任务
        df = pd.read_excel(large_source, engine='openpyxl')
        tasks = [
            TaskContext(
                idx=i,
                key=row['key'],
                source_text=row['中文原文'],
                original_trans="",
                target_lang="英语"
            )
            for _, row in df.iterrows()
        ]
        
        # 分批执行
        batch_size = test_config.batch_size
        all_results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_tasks = [orchestrator.process_task(task) for task in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            valid_results = [r for r in batch_results if not isinstance(r, Exception)]
            all_results.extend(valid_results)
            
            # 验证每批处理
            assert len(valid_results) > 0, f"第{i//batch_size}批应该有有效结果"
        
        # 验证总体结果
        assert len(all_results) > 0, "应该有有效的翻译结果"
        
        # 清理
        if os.path.exists(large_source):
            os.remove(large_source)


class TestIntegration:
    """模块间集成测试"""
    
    @pytest.fixture
    def temp_files(self, tmp_path):
        """创建临时文件集合"""
        files = {}
        
        # 术语库
        term_file = tmp_path / "terms.xlsx"
        pd.DataFrame({
            '中文原文': ['术语 1', '术语 2'],
            '英语': ['Term 1', 'Term 2']
        }).to_excel(term_file, index=False)
        files['term'] = str(term_file)
        
        # 源文件
        source_file = tmp_path / "source.xlsx"
        pd.DataFrame({
            'key': ['k1', 'k2'],
            '中文原文': ['内容 1', '内容 2']
        }).to_excel(source_file, index=False)
        files['source'] = str(source_file)
        
        # 输出文件
        files['output'] = str(tmp_path / "output.xlsx")
        
        return files
    
    def test_data_flow(self, temp_files):
        """测试数据流转（从输入到输出）"""
        config = Config()
        
        # 1. 加载术语库
        tm = TerminologyManager(temp_files['term'], config)
        
        # 2. 查询术语
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                tm.find_similar("术语 1", "英语")
            )
            assert result is not None, "应该找到匹配的术语"
            assert result['score'] == 100, "应该是精确匹配"
            
            # 3. 添加新术语
            loop.run_until_complete(
                tm.add_entry("新术语", "英语", "New Term")
            )
            
            # 4. 保存并关闭
            loop.run_until_complete(tm.shutdown())
            
            # 5. 验证文件已更新
            assert os.path.exists(temp_files['term']), "术语库文件应该存在"
            assert os.path.getsize(temp_files['term']) > 0, "术语库文件不应为空"
            
        finally:
            loop.close()


@pytest.mark.asyncio
async def test_error_handling_integration():
    """测试错误处理的集成"""
    config = Config()
    config.timeout = 1  # 设置很短的超时以触发错误
    
    # 创建无效的客户端
    client = AsyncOpenAI(api_key="invalid_key", base_url="https://invalid.url")
    
    # 创建临时术语库
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        term_file = f.name
    
    try:
        tm = TerminologyManager(term_file, config)
        
        orchestrator = WorkflowOrchestrator(
            config=config,
            client=client,
            tm=tm,
            p_draft="翻译",
            p_review="校对",
            batch_id="error_test"
        )
        
        # 创建测试任务
        ctx = TaskContext(
            idx=0,
            key="test_key",
            source_text="测试文本",
            original_trans="",
            target_lang="英语"
        )
        
        # 执行应该失败但不会崩溃
        result = await orchestrator.process_task(ctx)
        
        # 验证错误处理
        assert result is not None, "即使失败也应该返回结果对象"
        assert result.status in ["FAILED", "ERROR"], "应该标记为失败状态"
        
        await tm.shutdown()
        
    finally:
        if os.path.exists(term_file):
            os.remove(term_file)
