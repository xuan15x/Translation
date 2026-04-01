"""
terminology_history.py 单元测试
测试术语库历史记录模块
"""
import os
import pytest
import tempfile
import json
from datetime import datetime, timedelta

from service.terminology_history import (
    TerminologyHistoryManager,
    TermChange,
    Snapshot,
    ChangeType,
    get_history_manager,
    record_term_change
)


@pytest.fixture
def clean_db():
    """创建干净的数据库"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def history_manager(clean_db):
    """创建历史管理器实例"""
    return TerminologyHistoryManager(clean_db)


class TestTermChange:
    """TermChange 数据类测试"""
    
    def test_creation(self):
        """测试创建变更记录"""
        change = TermChange(
            id=1,
            timestamp="2024-01-01T10:00:00",
            change_type=ChangeType.ADDED.value,
            source_text="你好",
            language="英语",
            old_value="",
            new_value="Hello",
            batch_id="batch_001",
            operator="system",
            notes=""
        )
        
        assert change.id == 1
        assert change.change_type == "added"
        assert change.source_text == "你好"
        assert change.new_value == "Hello"
    
    def test_to_dict(self):
        """测试转换为字典"""
        change = TermChange(id=1, timestamp="2024-01-01T10:00:00",
                          change_type="added", source_text="测试",
                          language="英语", old_value="", new_value="Test")
        
        d = change.to_dict()
        
        assert isinstance(d, dict)
        assert d['id'] == 1
        assert d['source_text'] == "测试"
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'id': 2,
            'timestamp': "2024-01-01T10:00:00",
            'change_type': "updated",
            'source_text': "世界",
            'language': "法语",
            'old_value': "Monde",
            'new_value': "Le Monde",
            'batch_id': "",
            'operator': "user",
            'notes': "修正翻译"
        }
        
        change = TermChange.from_dict(data)
        
        assert change.id == 2
        assert change.change_type == "updated"
        assert change.operator == "user"


class TestSnapshot:
    """Snapshot 快照类测试"""
    
    def test_snapshot_creation(self):
        """测试创建快照"""
        snapshot = Snapshot(
            id=1,
            timestamp="2024-01-01T10:00:00",
            total_entries=100,
            total_translations=250,
            languages_count=5,
            snapshot_data='{"test": "data"}',
            batch_id="batch_001",
            notes="定期备份"
        )
        
        assert snapshot.total_entries == 100
        assert snapshot.languages_count == 5


class TestRecordChange:
    """记录变更测试"""
    
    def test_record_add(self, history_manager):
        """测试记录添加操作"""
        change_id = history_manager.record_add(
            source_text="新词",
            language="英语",
            new_value="New Word",
            batch_id="batch_001"
        )
        
        assert change_id > 0
        
        # 验证记录存在
        changes = history_manager.get_changes(limit=10)
        assert len(changes) >= 1
        
        last_change = changes[0]
        assert last_change.change_type == ChangeType.ADDED.value
        assert last_change.source_text == "新词"
        assert last_change.new_value == "New Word"
    
    def test_record_update(self, history_manager):
        """测试记录更新操作"""
        change_id = history_manager.record_update(
            source_text="旧词",
            language="日语",
            old_value="古い言葉",
            new_value="新しい表現",
            operator="translator"
        )
        
        assert change_id > 0
        
        changes = history_manager.get_changes(change_type="updated", limit=10)
        assert len(changes) >= 1
        
        update = changes[0]
        assert update.old_value == "古い言葉"
        assert update.new_value == "新しい表現"
    
    def test_record_delete(self, history_manager):
        """测试记录删除操作"""
        change_id = history_manager.record_delete(
            source_text="删除词",
            language="德语",
            old_value="Löschen",
            batch_id="batch_002"
        )
        
        assert change_id > 0
        
        changes = history_manager.get_changes(change_type="deleted", limit=10)
        assert len(changes) >= 1
        
        delete = changes[0]
        assert delete.change_type == "deleted"
        assert delete.old_value == "Löschen"
    
    def test_record_batch_import(self, history_manager):
        """测试记录批量导入"""
        change_id = history_manager.record_batch_import(
            source_text="导入词",
            language="西班牙语",
            new_value="Importado",
            batch_id="import_20240101"
        )
        
        assert change_id > 0
        
        changes = history_manager.get_changes(batch_id="import_20240101", limit=10)
        assert len(changes) >= 1
        
        imported = changes[0]
        assert imported.change_type == "imported"
        assert imported.batch_id == "import_20240101"


class TestGetChanges:
    """查询变更记录测试"""
    
    def test_get_all_changes(self, history_manager):
        """测试获取所有变更记录"""
        # 添加多条记录
        history_manager.record_add("词 1", "英语", "Word1")
        history_manager.record_add("词 2", "英语", "Word2")
        history_manager.record_update("词 3", "法语", "Old", "New")
        
        changes = history_manager.get_changes(limit=100)
        
        assert len(changes) >= 3
    
    def test_get_changes_by_type(self, history_manager):
        """测试按类型筛选"""
        history_manager.record_add("词 1", "英语", "Word1")
        history_manager.record_add("词 2", "英语", "Word2")
        history_manager.record_update("词 3", "法语", "Old", "New")
        
        added_changes = history_manager.get_changes(change_type="added", limit=10)
        
        assert len(added_changes) >= 2
        assert all(c.change_type == "added" for c in added_changes)
    
    def test_get_changes_by_date(self, history_manager):
        """测试按日期筛选"""
        now = datetime.now()
        yesterday = (now - timedelta(days=1)).isoformat()
        tomorrow = (now + timedelta(days=1)).isoformat()
        
        history_manager.record_add("今天", "英语", "Today")
        
        changes = history_manager.get_changes(
            start_date=yesterday,
            end_date=tomorrow,
            limit=10
        )
        
        assert len(changes) >= 1
    
    def test_get_changes_by_source(self, history_manager):
        """测试按源文本筛选"""
        history_manager.record_add("特定词", "英语", "Specific")
        history_manager.record_add("其他词", "英语", "Other")
        
        changes = history_manager.get_changes(source_text="特定词", limit=10)
        
        assert len(changes) >= 1
        assert changes[0].source_text == "特定词"
    
    def test_get_changes_pagination(self, history_manager):
        """测试分页"""
        # 添加 20 条记录
        for i in range(20):
            history_manager.record_add(f"词{i}", "英语", f"Word{i}")
        
        # 第一页
        page1 = history_manager.get_changes(limit=10, offset=0)
        assert len(page1) == 10
        
        # 第二页
        page2 = history_manager.get_changes(limit=10, offset=10)
        assert len(page2) == 10
        
        # 验证不重复
        ids1 = {c.id for c in page1}
        ids2 = {c.id for c in page2}
        assert ids1.isdisjoint(ids2)


class TestTimeline:
    """时间线功能测试"""
    
    def test_get_timeline(self, history_manager):
        """测试获取时间线"""
        # 添加一些记录
        history_manager.record_add("词 1", "英语", "Word1")
        history_manager.record_add("词 2", "英语", "Word2")
        history_manager.record_update("词 3", "法语", "Old", "New")
        
        timeline = history_manager.get_timeline(days=7, limit=100)
        
        assert isinstance(timeline, list)
        assert len(timeline) > 0
        
        # 检查返回的数据结构
        for entry in timeline:
            assert 'date' in entry
            assert 'change_type' in entry
            assert 'count' in entry
            assert 'sources' in entry
    
    def test_timeline_grouping(self, history_manager):
        """测试时间线分组"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 同一天添加多条记录
        history_manager.record_add("词 1", "英语", "Word1")
        history_manager.record_add("词 2", "英语", "Word2")
        history_manager.record_add("词 3", "英语", "Word3")
        
        timeline = history_manager.get_timeline(days=7)
        
        # 应该按日期和类型分组
        today_entries = [e for e in timeline if e['date'] == today]
        if today_entries:
            assert sum(e['count'] for e in today_entries) >= 3


class TestSnapshots:
    """快照功能测试"""
    
    def test_create_snapshot(self, history_manager):
        """测试创建快照"""
        db = {
            '你好': {'英语': 'Hello', '法语': 'Bonjour'},
            '世界': {'英语': 'World', '日语': '世界'}
        }
        
        snapshot_id = history_manager.create_snapshot(
            db, 
            batch_id="snapshot_001",
            notes="测试快照"
        )
        
        assert snapshot_id > 0
        
        # 验证快照可以检索
        snapshot = history_manager.get_snapshot(snapshot_id)
        assert snapshot is not None
        assert snapshot.total_entries == 2
        assert snapshot.total_translations == 4
        assert snapshot.languages_count == 3
    
    def test_get_latest_snapshot(self, history_manager):
        """测试获取最新快照"""
        db1 = {'词 1': {'英语': 'Word1'}}
        db2 = {'词 1': {'英语': 'Word1'}, '词 2': {'英语': 'Word2'}}
        
        history_manager.create_snapshot(db1, notes="第一个快照")
        import time
        time.sleep(0.1)  # 确保时间戳不同
        history_manager.create_snapshot(db2, notes="第二个快照")
        
        latest = history_manager.get_latest_snapshot()
        
        assert latest is not None
        assert latest.total_entries == 2
    
    def test_compare_snapshots(self, history_manager):
        """测试对比快照"""
        db1 = {
            '你好': {'英语': 'Hello'},
            '删除': {'英语': 'Delete'}
        }
        
        db2 = {
            '你好': {'英语': 'Hi'},  # 更新
            '新增': {'英语': 'New'}   # 新增
        }
        
        id1 = history_manager.create_snapshot(db1)
        id2 = history_manager.create_snapshot(db2)
        
        comparison = history_manager.compare_snapshots(id1, id2)
        
        assert 'summary' in comparison
        assert 'changes' in comparison
        
        summary = comparison['summary']
        assert summary['added_count'] >= 1
        assert summary['updated_count'] >= 1
        assert summary['deleted_count'] >= 1


class TestStatistics:
    """统计信息测试"""
    
    def test_get_statistics(self, history_manager):
        """测试获取统计信息"""
        # 添加不同类型的记录
        for i in range(5):
            history_manager.record_add(f"词{i}", "英语", f"Word{i}")
        
        for i in range(3):
            history_manager.record_update(f"旧词{i}", "法语", "Old", "New")
        
        stats = history_manager.get_statistics(days=30)
        
        assert 'total_changes' in stats
        assert 'by_type' in stats
        assert 'by_language' in stats
        
        assert stats['total_changes'] >= 8
        assert stats['by_type'].get('added', 0) >= 5
        assert stats['by_type'].get('updated', 0) >= 3


class TestExport:
    """导出功能测试"""
    
    def test_export_json(self, history_manager):
        """测试导出为 JSON"""
        history_manager.record_add("测试", "英语", "Test")
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            output_file = history_manager.export_history(temp_path, format='json')
            
            assert os.path.exists(output_file)
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert 'exported_at' in data
            assert 'total_records' in data
            assert 'changes' in data
            assert len(data['changes']) >= 1
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_export_csv(self, history_manager):
        """测试导出为 CSV"""
        history_manager.record_add("CSV 测试", "英语", "CSV Test")
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            output_file = history_manager.export_history(temp_path, format='csv')
            
            assert os.path.exists(output_file)
            
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert '时间戳' in content
            assert '变更类型' in content
            assert 'CSV 测试' in content
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_history_manager_singleton(self):
        """测试单例模式"""
        manager1 = get_history_manager()
        manager2 = get_history_manager()
        
        assert manager1 is manager2
    
    def test_record_term_change_function(self):
        """测试便捷记录函数"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_path = f.name
        
        try:
            # 重置全局变量
            import service.terminology_history
            terminology_history._history_manager = None
            
            manager = get_history_manager(temp_path)
            
            change_id = record_term_change(
                change_type="added",
                source_text="全局函数测试",
                language="英语",
                new_value="Global Test"
            )
            
            assert change_id > 0
            
            changes = manager.get_changes(limit=10)
            assert len(changes) >= 1
            assert changes[0].source_text == "全局函数测试"
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            # 重置全局变量
            import service.terminology_history
            terminology_history._history_manager = None


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow(self, history_manager):
        """测试完整工作流程"""
        # 1. 初始快照
        initial_db = {'你好': {'英语': 'Hello'}}
        snap1_id = history_manager.create_snapshot(initial_db, notes="初始状态")
        
        # 2. 添加术语
        history_manager.record_add("世界", "英语", "World")
        history_manager.record_add("欢迎", "日语", "ようこそ")
        
        # 3. 更新术语
        history_manager.record_update("你好", "英语", "Hello", "Hi")
        
        # 4. 再次快照
        updated_db = {
            '你好': {'英语': 'Hi'},
            '世界': {'英语': 'World'},
            '欢迎': {'日语': 'ようこそ'}
        }
        snap2_id = history_manager.create_snapshot(updated_db, notes="更新后")
        
        # 5. 对比快照
        comparison = history_manager.compare_snapshots(snap1_id, snap2_id)
        
        assert comparison['summary']['added_count'] >= 2
        assert comparison['summary']['updated_count'] >= 1
        
        # 6. 获取统计
        stats = history_manager.get_statistics(days=30)
        
        assert stats['total_changes'] >= 3
        assert stats['snapshot_count'] >= 2
        
        # 7. 获取时间线
        timeline = history_manager.get_timeline(days=7)
        
        assert len(timeline) > 0
        
        # 8. 导出历史
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            history_manager.export_history(temp_path)
            assert os.path.exists(temp_path)
        finally:
            os.remove(temp_path)
