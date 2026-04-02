"""
依赖注入容器
统一管理各层组件的创建和依赖关系

安全修复：添加数据库连接关闭机制，防止连接泄漏
"""
from typing import Dict, Any, Optional
import sqlite3
import atexit
import logging

logger = logging.getLogger(__name__)


class DependencyContainer:
    """依赖注入容器 - 管理所有组件的生命周期"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._resources_to_cleanup: list = []  # 需要清理的资源列表

    def register(self, name: str, service: Any, singleton: bool = False):
        """注册服务"""
        if singleton:
            self._singletons[name] = service
            # 注册需要清理的资源（如数据库连接）
            if isinstance(service, sqlite3.Connection):
                self._resources_to_cleanup.append((name, service))
        else:
            self._services[name] = service

    def get(self, name: str) -> Any:
        """获取服务"""
        if name in self._singletons:
            return self._singletons[name]
        if name in self._services:
            return self._services[name]()
        raise KeyError(f"Service '{name}' not registered")

    def clear(self):
        """清理所有服务"""
        # 先清理资源（关闭数据库连接等）
        self._cleanup_resources()
        self._services.clear()
        self._singletons.clear()

    def _cleanup_resources(self):
        """清理所有注册的资源（如数据库连接）"""
        for name, resource in self._resources_to_cleanup:
            try:
                if isinstance(resource, sqlite3.Connection):
                    resource.close()
                    logger.debug(f"已关闭数据库连接：{name}")
            except Exception as e:
                logger.error(f"关闭资源 {name} 时出错：{e}")
        self._resources_to_cleanup.clear()

    def shutdown(self):
        """优雅关闭容器，清理所有资源"""
        logger.info("正在关闭依赖容器...")
        self._cleanup_resources()
        logger.info("依赖容器已关闭")


# 全局容器实例
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """获取全局依赖容器"""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def initialize_container(config_file: Optional[str] = None,
                        api_client=None,
                        draft_prompt: str = "",
                        review_prompt: str = ""):
    """
    初始化依赖容器 - 从配置文件加载配置并创建所有组件
    
    Args:
        config_file: 配置文件路径（可选）
        api_client: OpenAI 客户端（可选）
        draft_prompt: 初译提示词
        review_prompt: 校对提示词
        
    Returns:
        DependencyContainer
    """
    container = get_container()
    container.clear()
    
    # ========== 从配置文件加载配置 ==========
    from config.loader import get_config_loader
    
    loader = get_config_loader()
    
    # 如果有配置文件，重新加载
    if config_file:
        from data_access.config_persistence import ConfigPersistence
        persistence = ConfigPersistence(config_file)
        file_config = persistence.load()
        loader.update(file_config)
    
    # 从配置加载器获取配置值
    from infrastructure.models import Config
    config = loader.to_dataclass(Config)
    container.register('config', config, singleton=True)
    
    # ========== Infrastructure Layer ==========
    # 1. 数据库连接 - 修复：使用文件数据库而非内存数据库，避免数据丢失
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'terminology.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_conn = sqlite3.connect(db_path, check_same_thread=False)
    container.register('db_connection', db_conn, singleton=True)
    
    # 2. Excel 路径（从配置加载）
    excel_path = loader.get('terminology_excel_path', "terminology.xlsx")
    container.register('excel_path', excel_path, singleton=True)
    
    # ========== Data Access Layer ==========
    # 3. 仓储实现
    from data_access.repositories import TerminologyRepository
    term_repo = TerminologyRepository(
        db_conn=container.get('db_connection'),
        excel_path=container.get('excel_path')
    )
    container.register('term_repository', term_repo, singleton=True)
    
    # ========== Domain Layer ==========
    # 4. 领域服务
    from domain.terminology_service_impl import TerminologyDomainService
    term_service = TerminologyDomainService(
        repo=container.get('term_repository')
    )
    container.register('terminology_service', term_service, singleton=True)
    
    # 添加缓存装饰器
    from domain.cache_decorators import CachedTerminologyService
    cached_term_service = CachedTerminologyService(
        service=term_service,
        cache_manager=None,
        ttl=3600
    )
    container.register('terminology_service_cached', cached_term_service, singleton=True)
    
    # ========== Application Layer ==========
    # 5. 翻译服务（如果提供了 API 客户端）
    if api_client and draft_prompt and review_prompt:
        from domain.translation_service_impl import TranslationDomainServiceImpl
        translation_service = TranslationDomainServiceImpl(
            client=api_client,
            terminology_service=term_service,
            draft_prompt=draft_prompt,
            review_prompt=review_prompt
        )
        container.register('translation_service', translation_service, singleton=True)
        
        # 6. 工作流协调器
        from application.workflow_coordinator import TranslationWorkflowCoordinator
        workflow_coordinator = TranslationWorkflowCoordinator(
            terminology_service=term_service,
            translation_service=translation_service,
            batch_processor=None
        )
        container.register('workflow_coordinator', workflow_coordinator, singleton=True)
        
        # 7. 任务编排器
        from application.workflow_coordinator import TaskOrchestrator
        orchestrator = TaskOrchestrator(
            coordinator=workflow_coordinator
        )
        container.register('task_orchestrator', orchestrator, singleton=True)
        
        # 8. 外观服务
        from application.translation_facade import TranslationServiceFacade
        facade = TranslationServiceFacade(
            terminology_service=term_service,
            translation_service=translation_service
        )
        container.register('translation_facade', facade, singleton=True)
    
    print("✅ 依赖容器初始化完成")
    print("   - Database Connection")
    print("   - Repositories")
    print("   - Domain Services (with Cache)")
    print("   - Application Coordinators")
    if api_client:
        print("   - Translation Services")
        print("   - Facade Pattern")
    
    return container


def reset_container():
    """重置容器（用于测试）"""
    global _container
    if _container:
        _container.shutdown()  # 使用 shutdown 方法清理资源
    _container = None


def _cleanup_on_exit():
    """程序退出时清理资源"""
    global _container
    if _container:
        _container.shutdown()


# 注册退出时的清理函数
atexit.register(_cleanup_on_exit)
