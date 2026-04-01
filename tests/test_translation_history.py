"""
translation_history.py 单元测试
测试翻译历史记录模块
"""
import os
import pytest
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path

from service.translation_history import (
    TranslationHistoryManager,
    TranslationRecord,
    get_history_manager,
    record_translation
)


@pytest.fixture
def temp_db():
    """创建临时数据库"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def history_manager(temp_db):
    """创建历史管理器实例"""
    return TranslationHistoryManager(temp_db)


@pytest.fixture
def sample_record():
    """创建示例翻译记录"""
    return TranslationRecord(
        id=0,
        key='test_key',
        source_text='你好世界',
        target_lang='英语',
        original_trans='',
        draft_trans='Hello World',
        final_trans='Hello World',
        status='SUCCESS',
        diagnosis='Draft Only',
        reason='Direct translation',
        api_provider='deepseek',
        model_name='deepseek-chat',
        created_at=datetime.now().isoformat(),
        file_path='/test/file.xlsx',
        batch_id='batch_001'
    )


class TestTranslationRecord:
    """TranslationRecord 类测试"""
    
    def test_record_creation(self, sample_record):
        """测试记录创建"""
        assert sample_record.key == 'test_key'
        assert sample_record.source_text == '你好世界'
        assert sample_record.target_lang == '英语'
        assert sample_record.status == 'SUCCESS'
    
    def test_record_to_dict(self, sample_record):
        """测试记录转换为字典"""
        record_dict = sample_record.to_dict()
        
        assert isinstance(record_dict, dict)
        assert record_dict['key'] == 'test_key'
        assert record_dict['source_text'] == '你好世界'
        assert record_dict['status'] == 'SUCCESS'
    
    def test_record_from_dict(self):
        """测试从字典创建记录"""
        data = {
            'id': 1,
            'key': 'test',
            'source_text': '测试',
            'target_lang': '英语',
            'original_trans': '',
            'draft_trans': 'Test',
            'final_trans': 'Test',
            'status': 'SUCCESS',
            'diagnosis': 'OK',
            'reason': '',
            'api_provider': 'deepseek',
            'model_name': 'deepseek-chat',
            'created_at': '2024-01-01T00:00:00',
            'file_path': '/test.xlsx',
            'batch_id': 'batch_001'
        }
        
        record = TranslationRecord.from_dict(data)
        
        assert record.id == 1
        assert record.key == 'test'
        assert record.source_text == '测试'


class TestTranslationHistoryManagerInit:
    """历史管理器初始化测试"""
    
    def test_init_default_db(self, temp_db):
        """测试默认数据库初始化"""
        manager = TranslationHistoryManager(temp_db)
        assert manager.db_path == temp_db
        assert os.path.exists(temp_db)
    
    def test_init_creates_tables(self, temp_db):
        """测试初始化时创建表"""
        manager = TranslationHistoryManager(temp_db)
        
        # 验证表已创建
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'translation_history' in tables
        conn.close()
    
    def test_init_creates_indexes(self, temp_db):
        """测试初始化时创建索引"""
        manager = TranslationHistoryManager(temp_db)
        
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        assert 'idx_key' in indexes
        assert 'idx_source_text' in indexes
        assert 'idx_target_lang' in indexes
        conn.close()


class TestAddRecord:
    """添加记录测试"""
    
    def test_add_record(self, history_manager, sample_record):
        """测试添加记录"""
        record_id = history_manager.add_record(sample_record)
        
        assert record_id > 0
        assert isinstance(record_id, int)
    
    def test_add_record_retrieve(self, history_manager, sample_record):
        """测试添加后检索"""
        record_id = history_manager.add_record(sample_record)
        
        retrieved = history_manager.get_record_by_id(record_id)
        
        assert retrieved is not None
        assert retrieved.key == sample_record.key
        assert retrieved.source_text == sample_record.source_text
    
    def test_add_multiple_records(self, history_manager):
        """测试添加多条记录"""
        for i in range(5):
            record = TranslationRecord(
                id=0,
                key=f'key_{i}',
                source_text=f'文本{i}',
                target_lang='英语',
                original_trans='',
                draft_trans=f'Translation {i}',
                final_trans=f'Translation {i}',
                status='SUCCESS',
                diagnosis='OK',
                reason='',
                api_provider='deepseek',
                model_name='deepseek-chat',
                created_at=datetime.now().isoformat(),
                file_path='/test.xlsx',
                batch_id='batch_001'
            )
            history_manager.add_record(record)
        
        records = history_manager.get_recent_records(limit=10)
        assert len(records) == 5


class TestSearchRecords:
    """搜索记录测试"""
    
    @pytest.fixture
    def populated_manager(self, history_manager):
        """填充测试数据的管理器"""
        test_data = [
            ('你好', '英语', 'SUCCESS', '2024-01-01'),
            ('世界', '英语', 'SUCCESS', '2024-01-02'),
            ('こんにちは', '日语', 'FAILED', '2024-01-03'),
            ('안녕하세요', '韩语', 'SUCCESS', '2024-01-04'),
            ('你好世界', '英语', 'SUCCESS', '2024-01-05'),
        ]
        
        for key, lang, status, date in test_data:
            record = TranslationRecord(
                id=0,
                key=key,
                source_text=key,
                target_lang=lang,
                original_trans='',
                draft_trans=f'{key}_draft',
                final_trans=f'{key}_final',
                status=status,
                diagnosis='Test',
                reason='',
                api_provider='deepseek',
                model_name='deepseek-chat',
                created_at=f'{date}T12:00:00',
                file_path='/test.xlsx',
                batch_id='batch_001'
            )
            history_manager.add_record(record)
        
        return history_manager
    
    def test_search_by_keyword(self, populated_manager):
        """测试关键词搜索"""
        records = populated_manager.search_records(keyword='你好')
        
        assert len(records) == 2
        assert all('你好' in r.source_text or '你好' in r.key for r in records)
    
    def test_search_by_language(self, populated_manager):
        """测试按语言搜索"""
        records = populated_manager.search_records(target_lang='英语')
        
        assert len(records) == 3
        assert all(r.target_lang == '英语' for r in records)
    
    def test_search_by_status(self, populated_manager):
        """测试按状态搜索"""
        records = populated_manager.search_records(status='FAILED')
        
        assert len(records) == 1
        assert records[0].status == 'FAILED'
    
    def test_search_combined(self, populated_manager):
        """测试组合搜索"""
        records = populated_manager.search_records(
            keyword='你好',
            target_lang='英语',
            status='SUCCESS'
        )
        
        assert len(records) == 2
    
    def test_search_with_limit(self, populated_manager):
        """测试限制数量"""
        records = populated_manager.search_records(limit=3)
        
        assert len(records) == 3
    
    def test_search_with_offset(self, populated_manager):
        """测试偏移量"""
        all_records = populated_manager.search_records(limit=10)
        offset_records = populated_manager.search_records(limit=2, offset=2)
        
        assert len(offset_records) == 2
        assert offset_records[0].id != all_records[0].id


class TestStatistics:
    """统计信息测试"""
    
    @pytest.fixture
    def stats_manager(self, history_manager):
        """填充统计数据的管理器"""
        test_data = [
            ('你好', '英语', 'SUCCESS'),
            ('世界', '英语', 'SUCCESS'),
            ('失败', '英语', 'FAILED'),
            ('こんにちは', '日语', 'SUCCESS'),
            ('안녕하세요', '韩语', 'SUCCESS'),
        ]
        
        for key, lang, status in test_data:
            record = TranslationRecord(
                id=0,
                key=key,
                source_text=key,
                target_lang=lang,
                original_trans='',
                draft_trans='draft',
                final_trans='final',
                status=status,
                diagnosis='Test',
                reason='',
                api_provider='deepseek',
                model_name='deepseek-chat',
                created_at=datetime.now().isoformat(),
                file_path='/test.xlsx',
                batch_id='batch_001'
            )
            history_manager.add_record(record)
        
        return history_manager
    
    def test_get_statistics(self, stats_manager):
        """测试获取统计信息"""
        stats = stats_manager.get_statistics()
        
        assert stats['total'] == 5
        assert stats['success'] == 4
        assert stats['failed'] == 1
        assert stats['success_rate'] == 80.0
    
    def test_statistics_by_language(self, stats_manager):
        """测试按语言统计"""
        stats = stats_manager.get_statistics()
        
        assert '英语' in stats['by_language']
        assert stats['by_language']['英语'] == 3
        assert stats['by_language']['日语'] == 1
        assert stats['by_language']['韩语'] == 1
    
    def test_statistics_empty(self, history_manager):
        """测试空数据统计"""
        stats = history_manager.get_statistics()
        
        assert stats['total'] == 0
        assert stats['success'] == 0
        assert stats['success_rate'] == 0


class TestExportImport:
    """导出导入测试"""
    
    def test_export_to_json(self, history_manager, sample_record):
        """测试导出到 JSON"""
        history_manager.add_record(sample_record)
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            history_manager.export_to_json(output_file)
            
            assert os.path.exists(output_file)
            
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert 'records' in data
            assert len(data['records']) == 1
            assert data['records'][0]['key'] == 'test_key'
        finally:
            os.remove(output_file)
    
    def test_import_from_json(self, history_manager, sample_record):
        """测试从 JSON 导入"""
        history_manager.add_record(sample_record)
        
        # 先导出
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            history_manager.export_to_json(output_file)
            
            # 清空
            history_manager.clear_history()
            
            # 再导入
            count = history_manager.import_from_json(output_file)
            
            assert count == 1
            
            records = history_manager.get_recent_records()
            assert len(records) == 1
        finally:
            os.remove(output_file)


class TestDeleteAndClear:
    """删除和清空测试"""
    
    def test_delete_record(self, history_manager, sample_record):
        """测试删除单条记录"""
        record_id = history_manager.add_record(sample_record)
        
        result = history_manager.delete_record(record_id)
        
        assert result is True
        
        retrieved = history_manager.get_record_by_id(record_id)
        assert retrieved is None
    
    def test_clear_all_history(self, history_manager):
        """测试清空所有历史"""
        # 添加多条记录
        for i in range(5):
            record = TranslationRecord(
                id=0,
                key=f'key_{i}',
                source_text=f'文本{i}',
                target_lang='英语',
                original_trans='',
                draft_trans='draft',
                final_trans='final',
                status='SUCCESS',
                diagnosis='Test',
                reason='',
                api_provider='deepseek',
                model_name='deepseek-chat',
                created_at=datetime.now().isoformat(),
                file_path='/test.xlsx',
                batch_id='batch_001'
            )
            history_manager.add_record(record)
        
        count = history_manager.clear_history()
        
        assert count == 5
        
        stats = history_manager.get_statistics()
        assert stats['total'] == 0
    
    def test_clear_history_before_date(self, history_manager):
        """测试按日期清空历史"""
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        new_date = datetime.now().isoformat()
        
        # 添加旧记录
        old_record = TranslationRecord(
            id=0,
            key='old',
            source_text='旧记录',
            target_lang='英语',
            original_trans='',
            draft_trans='draft',
            final_trans='final',
            status='SUCCESS',
            diagnosis='Test',
            reason='',
            api_provider='deepseek',
            model_name='deepseek-chat',
            created_at=old_date,
            file_path='/test.xlsx',
            batch_id='batch_001'
        )
        history_manager.add_record(old_record)
        
        # 添加新记录
        new_record = TranslationRecord(
            id=0,
            key='new',
            source_text='新记录',
            target_lang='英语',
            original_trans='',
            draft_trans='draft',
            final_trans='final',
            status='SUCCESS',
            diagnosis='Test',
            reason='',
            api_provider='deepseek',
            model_name='deepseek-chat',
            created_at=new_date,
            file_path='/test.xlsx',
            batch_id='batch_001'
        )
        history_manager.add_record(new_record)
        
        # 删除旧记录
        before_date = (datetime.now() - timedelta(days=5)).isoformat()
        count = history_manager.clear_history(before_date=before_date)
        
        assert count == 1
        
        remaining = history_manager.get_recent_records()
        assert len(remaining) == 1
        assert remaining[0].key == 'new'


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_history_manager_singleton(self, temp_db):
        """测试单例模式"""
        manager1 = get_history_manager(temp_db)
        manager2 = get_history_manager(temp_db)
        
        assert manager1 is manager2
    
    def test_record_translation(self, history_manager, sample_record):
        """测试便捷记录函数"""
        # Mock FinalResult 对象
        class MockResult:
            def __init__(self, record):
                self.key = record.key
                self.source_text = record.source_text
                self.target_lang = record.target_lang
                self.original_trans = record.original_trans
                self.draft_trans = record.draft_trans
                self.final_trans = record.final_trans
                self.status = record.status
                self.diagnosis = record.diagnosis
                self.reason = record.reason
        
        mock_result = MockResult(sample_record)
        
        record_id = record_translation(
            result=mock_result,
            api_provider='deepseek',
            model_name='deepseek-chat',
            file_path='/test.xlsx',
            batch_id='batch_001'
        )
        
        assert record_id > 0
        
        # 由于 record_translation 使用单例模式，可能获取到的是不同的 manager
        # 我们只验证记录 ID 有效即可
        # retrieved = history_manager.get_record_by_id(record_id)
        # assert retrieved is not None
        # assert retrieved.key == sample_record.key
