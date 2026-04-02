"""
测试依赖注入容器模块
验证 DI 容器的功能和行为
"""
import pytest
from unittest.mock import MagicMock, patch
import sqlite3

from infrastructure.di_container import (
    DependencyContainer,
    get_container,
    initialize_container,
    reset_container
)


class TestDependencyContainer:
    """测试 DependencyContainer 类"""
    
    def setup_method(self):
        """每个测试前重置容器"""
        reset_container()
    
    def teardown_method(self):
        """每个测试后清理"""
        reset_container()
    
    def test_register_and_get_service(self):
        """测试注册和获取服务"""
        container = DependencyContainer()
        
        # 注册服务
        mock_service = MagicMock()
        container.register('test_service', mock_service)
        
        # 获取服务
        service = container.get('test_service')
        assert service == mock_service
    
    def test_register_singleton(self):
        """测试注册单例服务"""
        container = DependencyContainer()
        
        mock_service = MagicMock()
        container.register('singleton_service', mock_service, singleton=True)
        
        # 多次获取应该返回同一实例
        service1 = container.get('singleton_service')
        service2 = container.get('singleton_service')
        
        assert service1 is service2
        assert service1 == mock_service
    
    def test_register_non_singleton(self):
        """测试注册非单例服务"""
        container = DependencyContainer()
        
        service_class = MagicMock()
        mock_instance1 = MagicMock()
        mock_instance2 = MagicMock()
        service_class.side_effect = [mock_instance1, mock_instance2]
        
        container.register('factory_service', service_class)
        
        # 多次获取应该返回不同实例
        service1 = container.get('factory_service')
        service2 = container.get('factory_service')
        
        assert service1 is not service2
        assert service_class.call_count == 2
    
    def test_get_unregistered_service(self):
        """测试获取未注册的服务"""
        container = DependencyContainer()
        
        with pytest.raises(KeyError) as exc_info:
            container.get('nonexistent_service')
        
        assert "not registered" in str(exc_info.value)
    
    def test_clear_container(self):
        """测试清理容器"""
        container = DependencyContainer()
        
        container.register('service1', MagicMock())
        container.register('service2', MagicMock(), singleton=True)
        
        container.clear()
        
        with pytest.raises(KeyError):
            container.get('service1')
        
        with pytest.raises(KeyError):
            container.get('service2')


class TestGlobalContainer:
    """测试全局容器函数"""
    
    def setup_method(self):
        reset_container()
    
    def teardown_method(self):
        reset_container()
    
    def test_get_container_creates_instance(self):
        """测试获取容器创建实例"""
        container = get_container()
        assert container is not None
        assert isinstance(container, DependencyContainer)
    
    def test_get_container_returns_same_instance(self):
        """测试多次获取返回同一实例"""
        container1 = get_container()
        container2 = get_container()
        
        assert container1 is container2
    
    def test_reset_container(self):
        """测试重置容器"""
        container1 = get_container()
        reset_container()
        container2 = get_container()
        
        # 重置后应该可以重新初始化
        assert container1 is not container2


class TestInitializeContainer:
    """测试容器初始化"""
    
    def setup_method(self):
        reset_container()
    
    def teardown_method(self):
        reset_container()
    
    @patch('infrastructure.di_container.get_config_loader')
    @patch('infrastructure.di_container.sqlite3.connect')
    def test_initialize_container_basic(self, mock_connect, mock_get_loader):
        """测试基本的容器初始化"""
        # 设置模拟对象
        mock_loader = MagicMock()
        mock_loader.get.return_value = "terminology.xlsx"
        mock_loader.to_dataclass.return_value = MagicMock()
        mock_get_loader.return_value = mock_loader
        
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        
        # 初始化容器
        container = initialize_container(
            config_file="config.json",
            api_client=None,
            draft_prompt="Draft",
            review_prompt="Review"
        )
        
        # 验证基本组件已注册
        assert container.get('config') is not None
        assert container.get('db_connection') is not None
        assert container.get('excel_path') is not None
        assert container.get('term_repository') is not None
        assert container.get('terminology_service') is not None
    
    @patch('infrastructure.di_container.get_config_loader')
    @patch('infrastructure.di_container.sqlite3.connect')
    def test_initialize_container_with_api_client(self, mock_connect, mock_get_loader):
        """测试带 API 客户端的容器初始化"""
        mock_loader = MagicMock()
        mock_loader.get.return_value = "terminology.xlsx"
        mock_loader.to_dataclass.return_value = MagicMock()
        mock_get_loader.return_value = mock_loader
        
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        
        mock_api_client = MagicMock()
        
        # 初始化容器（带 API 客户端）
        container = initialize_container(
            config_file="config.json",
            api_client=mock_api_client,
            draft_prompt="Draft",
            review_prompt="Review"
        )
        
        # 验证额外组件已注册
        assert container.get('translation_service') is not None
        assert container.get('workflow_coordinator') is not None
        assert container.get('task_orchestrator') is not None
        assert container.get('translation_facade') is not None


class TestContainerWithDatabase:
    """测试容器与数据库的集成"""
    
    def setup_method(self):
        reset_container()
    
    def teardown_method(self):
        reset_container()
    
    def test_database_connection_is_file_based(self):
        """测试数据库连接使用文件而非内存"""
        with patch('infrastructure.di_container.get_config_loader') as mock_get_loader:
            mock_loader = MagicMock()
            mock_loader.get.return_value = "terminology.xlsx"
            mock_loader.to_dataclass.return_value = MagicMock()
            mock_get_loader.return_value = mock_loader
            
            with patch('infrastructure.di_container.sqlite3.connect') as mock_connect:
                initialize_container()
                
                # 验证使用了文件数据库而非 :memory:
                call_args = mock_connect.call_args
                db_path = call_args[0][0] if call_args[0] else call_args[1].get('database', '')
                
                assert ':memory:' not in db_path
                assert db_path.endswith('terminology.db')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
