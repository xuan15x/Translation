"""
config_persistence.py 单元测试
测试配置持久化模块：ConfigPersistence
"""
import json
import os
import pytest
import tempfile
from pathlib import Path

from data_access.config_persistence import (
    ConfigPersistence, 
    load_config, 
    save_config, 
    create_sample_config
)


@pytest.fixture
def temp_json_file():
    """创建临时 JSON 配置文件"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
        json.dump({"test_key": "test_value", "number": 42}, f)
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def temp_yaml_file():
    """创建临时 YAML 配置文件"""
    try:
        import yaml
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w') as f:
            yaml.dump({"test_key": "test_value", "number": 42}, f)
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except ImportError:
        pytest.skip("PyYAML not installed")


class TestConfigPersistenceInit:
    """ConfigPersistence 初始化测试"""
    
    def test_init_without_file(self):
        """测试不指定文件初始化"""
        persistence = ConfigPersistence()
        assert persistence.config_file is None
        assert persistence._config_cache == {}
    
    def test_init_with_file(self, temp_json_file):
        """测试指定文件初始化"""
        persistence = ConfigPersistence(temp_json_file)
        assert persistence.config_file == temp_json_file


class TestGetFileType:
    """文件类型识别测试"""
    
    def test_json_extension(self):
        """测试 JSON 文件扩展名识别"""
        persistence = ConfigPersistence()
        file_type = persistence._get_file_type("config.json")
        assert file_type == 'json'
    
    def test_yaml_extension(self):
        """测试 YAML 文件扩展名识别"""
        persistence = ConfigPersistence()
        file_type = persistence._get_file_type("config.yaml")
        assert file_type == 'yaml'
    
    def test_yml_extension(self):
        """测试 YML 文件扩展名识别"""
        persistence = ConfigPersistence()
        file_type = persistence._get_file_type("config.yml")
        assert file_type == 'yml'
    
    def test_uppercase_extension(self):
        """测试大写扩展名识别"""
        persistence = ConfigPersistence()
        file_type = persistence._get_file_type("CONFIG.JSON")
        assert file_type == 'json'
    
    def test_unsupported_extension(self):
        """测试不支持的扩展名"""
        persistence = ConfigPersistence()
        with pytest.raises(ValueError) as exc_info:
            persistence._get_file_type("config.xml")
        assert "不支持的配置文件格式" in str(exc_info.value)


class TestLoadConfig:
    """加载配置测试"""
    
    def test_load_json_file(self, temp_json_file):
        """测试加载 JSON 文件"""
        persistence = ConfigPersistence(temp_json_file)
        config = persistence.load()
        
        assert config['test_key'] == 'test_value'
        assert config['number'] == 42
    
    def test_load_yaml_file(self, temp_yaml_file):
        """测试加载 YAML 文件"""
        persistence = ConfigPersistence(temp_yaml_file)
        config = persistence.load()
        
        assert config['test_key'] == 'test_value'
        assert config['number'] == 42
    
    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        persistence = ConfigPersistence("nonexistent.json")
        with pytest.raises(FileNotFoundError):
            persistence.load()
    
    def test_load_invalid_json(self):
        """测试加载无效的 JSON"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            f.write("{invalid json}")
            temp_path = f.name
        
        try:
            persistence = ConfigPersistence(temp_path)
            with pytest.raises(RuntimeError):
                persistence.load()
        finally:
            os.remove(temp_path)


class TestSaveConfig:
    """保存配置测试"""
    
    def test_save_json_file(self):
        """测试保存 JSON 文件"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            persistence = ConfigPersistence(temp_path)
            config = {"key": "value", "number": 123}
            persistence.save(config)
            
            # 验证文件已保存
            with open(temp_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            
            assert saved['key'] == 'value'
            assert saved['number'] == 123
        finally:
            os.remove(temp_path)
    
    def test_save_yaml_file(self):
        """测试保存 YAML 文件"""
        try:
            import yaml
            
            with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
                temp_path = f.name
            
            try:
                persistence = ConfigPersistence(temp_path)
                config = {"key": "value", "number": 123}
                persistence.save(config)
                
                # 验证文件已保存
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved = yaml.safe_load(f)
                
                assert saved['key'] == 'value'
                assert saved['number'] == 123
            finally:
                os.remove(temp_path)
        except ImportError:
            pytest.skip("PyYAML not installed")
    
    def test_save_creates_directory(self):
        """测试保存时自动创建目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "subdir", "config.json")
            
            persistence = ConfigPersistence(config_path)
            config = {"key": "value"}
            persistence.save(config)
            
            assert os.path.exists(config_path)


class TestGetSet:
    """获取和设置配置测试"""
    
    def test_get_simple_key(self, temp_json_file):
        """测试获取简单键"""
        persistence = ConfigPersistence(temp_json_file)
        value = persistence.get('test_key')
        assert value == 'test_value'
    
    def test_get_with_default(self):
        """测试获取带默认值"""
        persistence = ConfigPersistence()
        persistence._config_cache = {'key': 'value'}
        
        value = persistence.get('nonexistent', default='default')
        assert value == 'default'
    
    def test_get_nested_key(self):
        """测试获取嵌套键"""
        persistence = ConfigPersistence()
        persistence._config_cache = {
            'api': {
                'key': 'secret',
                'url': 'https://api.example.com'
            }
        }
        
        value = persistence.get('api.key')
        assert value == 'secret'
    
    def test_set_simple_key(self, temp_json_file):
        """测试设置简单键"""
        persistence = ConfigPersistence(temp_json_file)
        persistence.load()  # 先加载
        
        persistence.set('new_key', 'new_value')
        value = persistence.get('new_key')
        assert value == 'new_value'
    
    def test_set_nested_key(self):
        """测试设置嵌套键"""
        persistence = ConfigPersistence()
        persistence._config_cache = {}
        
        persistence.set('api.key', 'new_secret')
        assert persistence._config_cache['api']['key'] == 'new_secret'


class TestUpdate:
    """批量更新配置测试"""
    
    def test_update_dict(self, temp_json_file):
        """测试字典批量更新"""
        persistence = ConfigPersistence(temp_json_file)
        persistence.load()
        
        updates = {'new_key': 'new_value', 'number': 100}
        persistence.update(updates)
        
        assert persistence.get('new_key') == 'new_value'
        assert persistence.get('number') == 100


class TestDataclassConversion:
    """Dataclass 转换测试"""
    
    def test_from_dataclass(self):
        """测试从 dataclass 创建配置"""
        from dataclasses import dataclass
        
        @dataclass
        class TestConfig:
            key: str
            value: int
        
        config_obj = TestConfig(key="test", value=42)
        
        persistence = ConfigPersistence()
        config_dict = persistence.from_dataclass(config_obj)
        
        assert config_dict['key'] == 'test'
        assert config_dict['value'] == 42
    
    def test_to_dataclass(self):
        """测试转换为 dataclass"""
        from dataclasses import dataclass
        
        @dataclass
        class TestConfig:
            key: str
            value: int
        
        persistence = ConfigPersistence()
        persistence._config_cache = {'key': 'test', 'value': 42}
        
        config_obj = persistence.to_dataclass(TestConfig)
        
        assert config_obj.key == 'test'
        assert config_obj.value == 42
    
    def test_to_dataclass_filters_keys(self):
        """测试 to_dataclass 过滤键"""
        from dataclasses import dataclass
        
        @dataclass
        class TestConfig:
            key: str
        
        persistence = ConfigPersistence()
        persistence._config_cache = {'key': 'test', 'extra': 'should_be_filtered'}
        
        config_obj = persistence.to_dataclass(TestConfig)
        
        assert hasattr(config_obj, 'key')
        assert not hasattr(config_obj, 'extra')


class TestMergeWithEnv:
    """环境变量合并测试"""
    
    def test_merge_with_env_vars(self):
        """测试与环境变量合并"""
        persistence = ConfigPersistence()
        
        # 设置临时环境变量
        os.environ['DEEPSEEK_API_KEY'] = 'env_api_key'
        os.environ['DEEPSEEK_BASE_URL'] = 'https://env.api.com'
        
        try:
            config = {'api_key': 'file_api_key', 'base_url': 'https://file.api.com'}
            merged = persistence.merge_with_env(config)
            
            # 环境变量应该覆盖配置文件
            assert merged['api_key'] == 'env_api_key'
            assert merged['base_url'] == 'https://env.api.com'
        finally:
            # 清理环境变量
            del os.environ['DEEPSEEK_API_KEY']
            del os.environ['DEEPSEEK_BASE_URL']
    
    def test_merge_without_env_vars(self):
        """测试没有环境变量时的合并"""
        persistence = ConfigPersistence()
        
        config = {'api_key': 'file_api_key'}
        merged = persistence.merge_with_env(config)
        
        # 应该保持原样
        assert merged['api_key'] == 'file_api_key'


class TestConvenienceFunctions:
    """便捷函数测试"""
    
    def test_load_config_function(self, temp_json_file):
        """测试 load_config 函数"""
        config = load_config(temp_json_file)
        assert config['test_key'] == 'test_value'
    
    def test_save_config_function(self):
        """测试 save_config 函数"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config = {'key': 'value'}
            save_config(config, temp_path)
            
            loaded = load_config(temp_path)
            assert loaded['key'] == 'value'
        finally:
            os.remove(temp_path)
    
    def test_create_sample_config_json(self):
        """测试创建示例 JSON 配置"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            create_sample_config(temp_path, include_comments=False)
            
            config = load_config(temp_path)
            assert 'api_key' in config
            assert 'temperature' in config
        finally:
            os.remove(temp_path)
    
    def test_create_sample_config_yaml(self):
        """测试创建示例 YAML 配置"""
        try:
            import yaml
            
            with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
                temp_path = f.name
            
            try:
                create_sample_config(temp_path, include_comments=True)
                
                config = load_config(temp_path)
                assert 'api_key' in config
                assert 'temperature' in config
            finally:
                os.remove(temp_path)
        except ImportError:
            pytest.skip("PyYAML not installed")


class TestDefaultConfigDiscovery:
    """默认配置文件查找测试"""
    
    def test_find_default_config(self):
        """测试查找默认配置文件"""
        persistence = ConfigPersistence()
        
        # 在没有配置文件的环境中，应该返回 None
        result = persistence._find_default_config()
        
        # 这个测试结果取决于环境
        # 如果存在默认配置文件，验证其有效性
        if result:
            assert os.path.exists(result)
            assert result.endswith(('.json', '.yaml', '.yml'))


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow_json(self):
        """测试完整的 JSON 工作流"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # 1. 创建持久化管理器
            persistence = ConfigPersistence(temp_path)
            
            # 2. 保存配置
            original_config = {
                'api_key': 'test_key',
                'temperature': 0.5,
                'nested': {'key': 'value'}
            }
            persistence.save(original_config)
            
            # 3. 加载配置
            loaded_config = persistence.load()
            
            # 4. 验证配置
            assert loaded_config['api_key'] == 'test_key'
            assert loaded_config['temperature'] == 0.5
            assert loaded_config['nested']['key'] == 'value'
            
            # 5. 修改配置
            persistence.set('temperature', 0.7)
            persistence.save(persistence._config_cache)
            
            # 6. 重新加载验证
            reloaded_config = persistence.load()
            assert reloaded_config['temperature'] == 0.7
            
        finally:
            os.remove(temp_path)
