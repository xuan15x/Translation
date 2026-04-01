"""
测试数据管理模块
统一管理测试数据的生成、加载和清理
"""
import os
import json
import tempfile
import pytest
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_terminology_data(count: int = 100, 
                                  languages: List[str] = None) -> pd.DataFrame:
        """
        生成术语库测试数据
        
        Args:
            count: 数据条数
            languages: 目标语言列表
            
        Returns:
            DataFrame 格式的术语数据
        """
        if languages is None:
            languages = ['英语', '法语', '德语', '日语']
        
        data = {
            '中文原文': [],
        }
        
        # 添加语言列
        for lang in languages:
            data[lang] = []
        
        # 生成数据
        for i in range(count):
            data['中文原文'].append(f'测试术语_{i}')
            
            for lang in languages:
                translation = f'Test_Term_{i}_{lang}'
                data[lang].append(translation)
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_source_data(count: int = 50, 
                            include_original: bool = False) -> pd.DataFrame:
        """
        生成源文件测试数据
        
        Args:
            count: 数据条数
            include_original: 是否包含原译文
            
        Returns:
            DataFrame 格式的源数据
        """
        data = {
            'key': [f'key_{i}' for i in range(count)],
            '中文原文': [f'需要翻译的文本_{i}' for i in range(count)],
        }
        
        if include_original:
            data['原译文'] = [f'Original Translation {i}' for i in range(count)]
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_translation_result(source_df: pd.DataFrame,
                                   target_lang: str = '英语') -> pd.DataFrame:
        """
        生成翻译结果测试数据
        
        Args:
            source_df: 源数据 DataFrame
            target_lang: 目标语言
            
        Returns:
            DataFrame 格式的翻译结果
        """
        results = []
        
        for _, row in source_df.iterrows():
            result = {
                'key': row['key'],
                'source_text': row['中文原文'],
                'target_lang': target_lang,
                'draft_trans': f'Draft Translation of {row["中文原文"]}',
                'final_trans': f'Final Translation of {row["中文原文"]}',
                'status': 'SUCCESS',
                'diagnosis': 'AI Translated',
                'api_provider': 'test_provider',
                'model_name': 'test_model'
            }
            results.append(result)
        
        return pd.DataFrame(results)


class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self, base_dir: str = None):
        """
        初始化测试数据管理器
        
        Args:
            base_dir: 基础目录，默认为临时目录
        """
        if base_dir is None:
            base_dir = tempfile.mkdtemp(prefix='test_data_')
        
        self.base_dir = base_dir
        self.created_files: List[str] = []
        
        # 确保目录存在
        os.makedirs(base_dir, exist_ok=True)
        
        # 子目录
        self.term_dir = os.path.join(base_dir, 'terminology')
        self.source_dir = os.path.join(base_dir, 'source')
        self.result_dir = os.path.join(base_dir, 'results')
        self.config_dir = os.path.join(base_dir, 'configs')
        
        for dir_path in [self.term_dir, self.source_dir, 
                        self.result_dir, self.config_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def create_test_terminology(self, count: int = 100, 
                               filename: str = None) -> str:
        """
        创建测试术语库
        
        Args:
            count: 术语数量
            filename: 文件名（可选）
            
        Returns:
            术语库文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'terms_{timestamp}.xlsx'
        
        filepath = os.path.join(self.term_dir, filename)
        
        # 生成数据
        df = TestDataGenerator.generate_terminology_data(count=count)
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        self.created_files.append(filepath)
        return filepath
    
    def create_test_source(self, count: int = 50,
                          filename: str = None) -> str:
        """
        创建测试源文件
        
        Args:
            count: 数据条数
            filename: 文件名（可选）
            
        Returns:
            源文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'source_{timestamp}.xlsx'
        
        filepath = os.path.join(self.source_dir, filename)
        
        # 生成数据
        df = TestDataGenerator.generate_source_data(count=count)
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        self.created_files.append(filepath)
        return filepath
    
    def create_test_config(self, config_dict: Dict,
                          filename: str = None) -> str:
        """
        创建测试配置文件
        
        Args:
            config_dict: 配置字典
            filename: 文件名（可选）
            
        Returns:
            配置文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'config_{timestamp}.json'
        
        filepath = os.path.join(self.config_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        
        self.created_files.append(filepath)
        return filepath
    
    def load_test_data(self, filepath: str) -> pd.DataFrame:
        """
        加载测试数据
        
        Args:
            filepath: 文件路径
            
        Returns:
            DataFrame 格式的数据
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"测试数据文件不存在：{filepath}")
        
        return pd.read_excel(filepath, engine='openpyxl')
    
    def cleanup(self, force: bool = False):
        """
        清理测试数据
        
        Args:
            force: 是否强制删除所有文件
        """
        if force:
            # 删除整个基础目录
            import shutil
            if os.path.exists(self.base_dir):
                shutil.rmtree(self.base_dir)
        else:
            # 只删除创建的文件
            for filepath in self.created_files:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as e:
                    print(f"删除文件失败：{filepath}, 错误：{e}")
        
        self.created_files.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取测试数据统计信息"""
        stats = {
            'base_dir': self.base_dir,
            'created_files_count': len(self.created_files),
            'files': {}
        }
        
        # 统计各目录
        for dir_name in ['terminology', 'source', 'results', 'configs']:
            dir_path = getattr(self, f'{dir_name}_dir')
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                stats['files'][dir_name] = {
                    'count': len(files),
                    'files': files
                }
        
        return stats


class TestDataSet:
    """测试数据集（预定义的数据集合）"""
    
    # 小型数据集（用于快速测试）
    SMALL = {
        'terminology_count': 10,
        'source_count': 5,
        'expected_duration': '< 5s'
    }
    
    # 中型数据集（用于常规测试）
    MEDIUM = {
        'terminology_count': 100,
        'source_count': 50,
        'expected_duration': '< 30s'
    }
    
    # 大型数据集（用于性能测试）
    LARGE = {
        'terminology_count': 1000,
        'source_count': 500,
        'expected_duration': '< 5min'
    }
    
    # 超大型数据集（用于压力测试）
    XLARGE = {
        'terminology_count': 10000,
        'source_count': 5000,
        'expected_duration': '> 5min'
    }
    
    @classmethod
    def create_dataset(cls, size: str = 'MEDIUM',
                      manager: TestDataManager = None) -> TestDataManager:
        """
        创建指定规模的数据集
        
        Args:
            size: 数据集规模（SMALL/MEDIUM/LARGE/XLARGE）
            manager: 数据管理器实例
            
        Returns:
            TestDataManager 实例
        """
        if manager is None:
            manager = TestDataManager()
        
        config = getattr(cls, size.upper())
        
        # 创建术语库
        manager.create_test_terminology(count=config['terminology_count'])
        
        # 创建源文件
        manager.create_test_source(count=config['source_count'])
        
        return manager


# 全局测试数据管理器实例
_global_test_data_manager: Optional[TestDataManager] = None


def get_test_data_manager() -> TestDataManager:
    """获取全局测试数据管理器"""
    global _global_test_data_manager
    if _global_test_data_manager is None:
        _global_test_data_manager = TestDataManager()
    return _global_test_data_manager


def setup_test_data(size: str = 'MEDIUM') -> TestDataManager:
    """设置测试数据"""
    manager = get_test_data_manager()
    return TestDataSet.create_dataset(size, manager)


def cleanup_test_data(force: bool = False):
    """清理测试数据"""
    manager = get_test_data_manager()
    manager.cleanup(force=force)


# pytest fixtures
@pytest.fixture
def test_data_manager():
    """pytest fixture: 测试数据管理器"""
    manager = TestDataManager()
    yield manager
    manager.cleanup()
