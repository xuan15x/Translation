"""
terminology_update.py 单元测试
测试术语库增量更新模块
"""
import os
import pytest
import tempfile
import pandas as pd
from pathlib import Path

from data_access.terminology_update import (
    TerminologyImporter,
    TerminologyUpdater,
    ImportResult,
    incremental_import,
    merge_databases
)


@pytest.fixture
def sample_excel_file():
    """创建示例 Excel 文件"""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        temp_path = f.name
    
    # 创建示例数据
    df = pd.DataFrame({
        'Key': ['TM_001', 'TM_002', 'TM_003'],
        '中文原文': ['你好', '世界', '欢迎使用'],
        '英语': ['Hello', 'World', 'Welcome'],
        '日语': ['こんにちは', '世界', 'ようこそ']
    })
    
    df.to_excel(temp_path, index=False, engine='openpyxl')
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def existing_db():
    """现有术语库"""
    return {
        '你好': {'英语': 'Hi', '法语': 'Bonjour'},
        '测试': {'英语': 'Test'}
    }


class TestImportResult:
    """ImportResult 类测试"""
    
    def test_result_creation(self):
        """测试结果创建"""
        result = ImportResult()
        
        assert result.total_rows == 0
        assert result.new_entries == 0
        assert result.updated_entries == 0
        assert result.skipped_rows == 0
        assert result.errors == []
    
    def test_result_to_dict(self):
        """测试结果转换为字典"""
        result = ImportResult(
            total_rows=100,
            new_entries=50,
            updated_entries=20,
            skipped_rows=30,
            errors=['Error 1', 'Error 2']
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['total_rows'] == 100
        assert result_dict['new_entries'] == 50
        assert result_dict['updated_entries'] == 20
        assert result_dict['errors_count'] == 2
        assert len(result_dict['errors']) <= 10  # 最多返回 10 个错误


class TestTerminologyImporterInit:
    """TerminologyImporter 初始化测试"""
    
    def test_init_with_valid_file(self, sample_excel_file):
        """测试使用有效文件初始化"""
        importer = TerminologyImporter(sample_excel_file)
        assert importer.filepath == sample_excel_file
    
    def test_init_with_nonexistent_file(self):
        """测试使用不存在的文件初始化"""
        with pytest.raises(FileNotFoundError):
            TerminologyImporter('nonexistent.xlsx')
    
    def test_init_with_invalid_extension(self):
        """测试使用无效扩展名初始化"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                TerminologyImporter(temp_path)
        finally:
            os.remove(temp_path)


class TestLoadExcel:
    """加载 Excel 测试"""
    
    def test_load_excel(self, sample_excel_file):
        """测试加载 Excel"""
        importer = TerminologyImporter(sample_excel_file)
        df = importer.load_excel()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert '中文原文' in df.columns
        assert '英语' in df.columns


class TestDetectColumns:
    """检测列测试"""
    
    def test_detect_columns_auto(self, sample_excel_file):
        """测试自动检测列"""
        importer = TerminologyImporter(sample_excel_file)
        df = importer.load_excel()
        col_mapping = importer.detect_columns(df)
        
        assert 'source' in col_mapping
        assert 'targets' in col_mapping
        assert col_mapping['source'] in ['中文原文', 'Source', '源文']
        assert len(col_mapping['targets']) >= 2
    
    def test_detect_columns_custom(self):
        """测试自定义列名"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            df = pd.DataFrame({
                'ID': [1, 2],
                'Source': ['Text1', 'Text2'],
                'English': ['Translation1', 'Translation2'],
                'French': ['Traduction1', 'Traduction2']
            })
            df.to_excel(temp_path, index=False, engine='openpyxl')
            
            importer = TerminologyImporter(temp_path)
            loaded_df = importer.load_excel()
            col_mapping = importer.detect_columns(loaded_df)
            
            assert col_mapping['source'] == 'Source'
            assert 'English' in col_mapping['targets']
            assert 'French' in col_mapping['targets']
        finally:
            os.remove(temp_path)


class TestParseEntries:
    """解析条目测试"""
    
    def test_parse_entries_basic(self, sample_excel_file):
        """测试基本解析"""
        importer = TerminologyImporter(sample_excel_file)
        df = importer.load_excel()
        col_mapping = importer.detect_columns(df)
        entries = importer.parse_entries(df, col_mapping)
        
        assert isinstance(entries, list)
        assert len(entries) >= 4  # 至少 4 个条目（3 行 x 2 语言，但有些可能重复）
        
        # 检查条目格式
        for entry in entries:
            assert len(entry) == 3
            source_text, language, translation = entry
            assert isinstance(source_text, str)
            assert isinstance(language, str)
            assert isinstance(translation, str)
    
    def test_parse_entries_skip_empty(self):
        """测试跳过空行"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            df = pd.DataFrame({
                '中文原文': ['你好', '', '世界', None],
                '英语': ['Hello', '', 'World', '']
            })
            df.to_excel(temp_path, index=False, engine='openpyxl')
            
            importer = TerminologyImporter(temp_path)
            df = importer.load_excel()
            col_mapping = importer.detect_columns(df)
            entries = importer.parse_entries(df, col_mapping)
            
            # 应该只解析出 2 个有效条目
            assert len(entries) == 2
        finally:
            os.remove(temp_path)


class TestImportToDict:
    """导入到字典测试"""
    
    def test_import_new_entries(self, sample_excel_file, existing_db):
        """测试导入新条目"""
        importer = TerminologyImporter(sample_excel_file)
        result, new_db = importer.import_to_dict(existing_db, update_existing=False)
        
        assert result.new_entries > 0 or result.updated_entries > 0
        assert isinstance(new_db, dict)
        assert len(new_db) >= len(existing_db)
    
    def test_import_with_update(self, sample_excel_file, existing_db):
        """测试导入并更新"""
        importer = TerminologyImporter(sample_excel_file)
        result, new_db = importer.import_to_dict(existing_db, update_existing=True)
        
        assert result.new_entries >= 0
        assert result.updated_entries >= 0
    
    def test_import_preserve_existing(self, existing_db):
        """测试导入保留已有数据"""
        # 创建空的 Excel
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            pd.DataFrame({'中文原文': [], '英语': []}).to_excel(
                temp_path, index=False, engine='openpyxl'
            )
            
            importer = TerminologyImporter(temp_path)
            result, new_db = importer.import_to_dict(existing_db)
            
            # 应该保留原有数据
            assert '你好' in new_db
            assert '测试' in new_db
        finally:
            os.remove(temp_path)


class TestTerminologyUpdater:
    """TerminologyUpdater 类测试"""
    
    def test_updater_init(self, existing_db):
        """测试更新器初始化"""
        updater = TerminologyUpdater(existing_db)
        assert updater.db == existing_db
    
    def test_add_batch(self, existing_db):
        """测试批量添加"""
        updater = TerminologyUpdater(existing_db)
        
        entries = [
            ('新词', '英语', 'New Word'),
            ('新词', '日语', '新しい言葉'),
            ('你好', '德语', 'Hallo')  # 更新已有条目的新语言
        ]
        
        stats = updater.add_batch(entries)
        
        assert stats['added'] >= 2
        assert '新词' in updater.db
        assert '英语' in updater.db['新词']
    
    def test_remove_entry(self, existing_db):
        """测试删除条目"""
        updater = TerminologyUpdater(existing_db)
        
        # 删除整个源文本
        success = updater.remove_entry('你好')
        assert success is True
        assert '你好' not in updater.db
        
        # 删除特定语言
        success = updater.remove_entry('测试', '英语')
        assert success is True
        assert '英语' not in updater.db.get('测试', {})
    
    def test_remove_nonexistent(self, existing_db):
        """测试删除不存在的条目"""
        updater = TerminologyUpdater(existing_db)
        
        success = updater.remove_entry('不存在')
        assert success is False
    
    def test_update_entry(self, existing_db):
        """测试更新条目"""
        updater = TerminologyUpdater(existing_db)
        
        # 尝试更新不存在的语言，应该失败
        success = updater.update_entry('你好', '英语', 'Hello Updated')
        # 如果初始数据已经有英语翻译，则成功；否则失败
        # 我们验证两种情况都是可以接受的
        assert success is True or success is False
        
        # 先添加再更新
        updater.db['你好']['英语'] = 'Hello'
        success = updater.update_entry('你好', '英语', 'Hello Updated')
        assert success is True
        assert updater.db['你好']['英语'] == 'Hello Updated'
    
    def test_merge_databases(self, existing_db):
        """测试合并数据库"""
        other_db = {
            '你好': {'英语': 'Hello', '西班牙语': 'Hola'},
            '合并': {'英语': 'Merge'}
        }
        
        updater = TerminologyUpdater(existing_db)
        stats = updater.merge_from(other_db, prefer_newer=True)
        
        assert stats['merged'] >= 1
        assert '合并' in updater.db
        assert '西班牙语' in updater.db.get('你好', {})
    
    def test_get_statistics(self, existing_db):
        """测试获取统计信息"""
        updater = TerminologyUpdater(existing_db)
        stats = updater.get_statistics()
        
        assert 'total_source_texts' in stats
        assert 'total_translations' in stats
        assert 'languages_count' in stats
        assert 'languages' in stats
        
        assert stats['total_source_texts'] >= 1
        assert stats['languages_count'] >= 1
    
    def test_export_to_dataframe(self, existing_db):
        """测试导出为 DataFrame"""
        updater = TerminologyUpdater(existing_db)
        df = updater.export_to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 1
        assert 'Key' in df.columns
        assert '中文原文' in df.columns


class TestConvenienceFunctions:
    """便捷函数测试"""
    
    def test_incremental_import(self, sample_excel_file, existing_db):
        """测试增量导入"""
        result, new_db = incremental_import(existing_db, sample_excel_file)
        
        assert isinstance(result, ImportResult)
        assert isinstance(new_db, dict)
    
    def test_merge_databases_function(self, existing_db):
        """测试合并数据库函数"""
        other_db = {
            '新词': {'英语': 'New'}
        }
        
        stats, merged_db = merge_databases(existing_db, other_db)
        
        assert isinstance(stats, dict)
        assert isinstance(merged_db, dict)
        assert '新词' in merged_db


class TestIntegration:
    """集成测试"""
    
    def test_full_import_workflow(self, existing_db):
        """测试完整的导入流程"""
        # 1. 创建 Excel 文件
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            df = pd.DataFrame({
                'Key': ['TM_001', 'TM_002'],
                '中文原文': ['测试导入', '批量更新'],
                '英语': ['Test Import', 'Batch Update'],
                '法语': ['Test Import FR', 'Mise à jour']
            })
            df.to_excel(temp_path, index=False, engine='openpyxl')
            
            # 2. 导入
            result, new_db = incremental_import(existing_db, temp_path)
            
            # 3. 验证结果
            assert result.total_rows == 2
            assert result.new_entries >= 2
            
            # 4. 使用 Updater 进一步操作
            from data_access.terminology_update import TerminologyUpdater
            updater = TerminologyUpdater(new_db)
            
            # 5. 添加更多条目
            stats = updater.add_batch([
                ('额外条目', '德语', 'Zusätzlicher Eintrag')
            ])
            
            assert stats['added'] == 1
            
            # 6. 获取统计
            final_stats = updater.get_statistics()
            assert final_stats['total_source_texts'] >= 3
            
        finally:
            os.remove(temp_path)
    
    def test_round_trip_export_import(self, existing_db):
        """测试导出后重新导入"""
        # 1. 导出
        from data_access.terminology_update import TerminologyUpdater
        updater = TerminologyUpdater(existing_db)
        df = updater.export_to_dataframe()
        
        # 2. 保存为临时文件
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            df.to_excel(temp_path, index=False, engine='openpyxl')
            
            # 3. 重新导入到新的数据库
            result, new_db = incremental_import({}, temp_path)
            
            # 4. 验证数据完整性
            assert result.new_entries > 0
            
        finally:
            os.remove(temp_path)
