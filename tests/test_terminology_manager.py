"""
terminology_manager.py 单元测试
测试术语库管理功能
"""
import pytest
import asyncio
import os
import tempfile
from pathlib import Path

# 旧的测试已废弃，使用新架构的 domain/terminology_service_impl.py
# from business_logic.terminology_manager import TerminologyManager
from infrastructure.models.models import Config


class TestTerminologyManager:
    """TerminologyManager 类测试"""
    
    @pytest.mark.asyncio
    async def test_initialization_creates_empty_db(self, sample_config):
        """测试初始化创建空数据库"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            assert hasattr(tm, 'db')
            assert isinstance(tm.db, dict)
            
            await tm.shutdown()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @pytest.mark.asyncio
    async def test_add_entry_basic(self, sample_config):
        """测试添加基本条目"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            # 添加条目
            await tm.add_entry('你好', '英语', 'Hello')
            
            # 验证内存中的数据
            assert '你好' in tm.db
            assert tm.db['你好']['英语'] == 'Hello'
            
            await tm.shutdown()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @pytest.mark.asyncio
    async def test_add_entry_updates_existing(self, sample_config):
        """测试更新已存在条目"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            # 添加第一个语言
            await tm.add_entry('世界', '英语', 'World')
            # 添加第二个语言到同一原文
            await tm.add_entry('世界', '日语', 'Sekai')
            
            assert '世界' in tm.db
            assert len(tm.db['世界']) == 2
            assert tm.db['世界']['英语'] == 'World'
            assert tm.db['世界']['日语'] == 'Sekai'
            
            await tm.shutdown()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @pytest.mark.asyncio
    async def test_add_entry_validates_input(self, sample_config):
        """测试输入验证"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            # 空源文本应该被忽略
            await tm.add_entry('', '英语', 'Hello')
            # 空翻译应该被忽略
            await tm.add_entry('测试', '英语', '')
            
            # 验证没有添加无效数据
            assert '' not in tm.db
            
            await tm.shutdown()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @pytest.mark.asyncio
    async def test_find_similar_exact_match(self, sample_config):
        """测试精确匹配查找"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            # 添加测试数据
            await tm.add_entry('精确匹配', '英语', 'Exact Match')
            await asyncio.sleep(0.5)  # 等待写入
            
            result = await tm.find_similar('精确匹配', '英语')
            
            assert result is not None
            assert result['score'] == 100
            assert result['translation'] == 'Exact Match'
            
            await tm.shutdown()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @pytest.mark.asyncio
    async def test_find_similar_no_match(self, sample_config):
        """测试无匹配情况"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            # 添加不相关的数据
            await tm.add_entry('苹果', '英语', 'Apple')
            await asyncio.sleep(0.5)
            
            result = await tm.find_similar('电脑', '英语')
            
            # 可能返回 None 或低分匹配
            if result is not None:
                assert result['score'] < 100
            
            await tm.shutdown()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @pytest.mark.asyncio
    async def test_find_similar_empty_database(self, sample_config):
        """测试空数据库查找"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            result = await tm.find_similar('任何文本', '英语')
            
            assert result is None
            
            await tm.shutdown()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @pytest.mark.asyncio
    async def test_shutdown_saves_to_excel(self, sample_config):
        """测试关闭时保存到 Excel"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            # 添加数据
            await tm.add_entry('保存测试', '英语', 'Save Test')
            
            # 关闭并保存
            await tm.shutdown()
            
            # 验证文件存在
            assert os.path.exists(temp_path)
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @pytest.mark.asyncio
    async def test_background_writer_queue(self, sample_config):
        """测试后台写入队列机制"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            # 验证队列属性存在
            assert hasattr(tm, 'queue')
            assert hasattr(tm, 'queue_lock')
            assert hasattr(tm, 'event')
            
            await tm.shutdown()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @pytest.mark.asyncio
    async def test_load_from_existing_file(self, temp_excel_file, sample_config):
        """测试从现有文件加载"""
        tm = TerminologyManager(temp_excel_file, sample_config)
        
        # 验证数据已加载
        assert hasattr(tm, 'db')
        
        await tm.shutdown()


class TestTerminologyManagerIntegration:
    """TerminologyManager 集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, sample_config):
        """测试完整工作流"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            tm = TerminologyManager(temp_path, sample_config)
            
            # 1. 添加多个条目
            await tm.add_entry('术语 1', '英语', 'Term 1')
            await tm.add_entry('术语 2', '英语', 'Term 2')
            await tm.add_entry('术语 3', '法语', 'Terme 3')
            
            await asyncio.sleep(0.5)
            
            # 2. 查找相似
            result1 = await tm.find_similar('术语 1', '英语')
            result2 = await tm.find_similar('术语 2', '英语')
            
            assert result1 is not None or result2 is not None
            
            # 3. 关闭保存
            await tm.shutdown()
            
            # 4. 重新加载
            tm2 = TerminologyManager(temp_path, sample_config)
            
            # 验证数据持久化
            assert len(tm2.db) > 0
            
            await tm2.shutdown()
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
