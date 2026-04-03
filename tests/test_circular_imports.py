"""
循环导入综合验证测试
确保所有模块可以正常导入，无循环依赖
"""
import pytest
import importlib
import sys


class TestCircularImports:
    """循环导入测试类"""

    def test_infrastructure_module(self):
        """测试 infrastructure 模块导入"""
        import infrastructure
        assert hasattr(infrastructure, 'models')

    def test_domain_module(self):
        """测试 domain 模块导入"""
        import domain
        assert hasattr(domain, 'services')
        assert hasattr(domain, 'models')

    def test_data_access_module(self):
        """测试 data_access 模块导入"""
        import data_access
        assert hasattr(data_access, 'config_persistence')

    def test_service_module(self):
        """测试 service 模块导入"""
        import service
        assert hasattr(service, 'api_provider')

    def test_application_module(self):
        """测试 application 模块导入"""
        import application
        assert hasattr(application, 'translation_facade')

    def test_presentation_module(self):
        """测试 presentation 模块导入"""
        import presentation
        assert hasattr(presentation, 'gui_app')

    def test_infrastructure_database(self):
        """测试 infrastructure.database 导入"""
        from infrastructure.database import ConnectionPool, DatabaseManager
        assert ConnectionPool is not None
        assert DatabaseManager is not None

    def test_infrastructure_database_iterm_repository(self):
        """测试 infrastructure.database.ITermRepository 延迟导入"""
        from infrastructure.database import ITermRepository
        assert ITermRepository is not None

    def test_infrastructure_models(self):
        """测试 infrastructure.models 导入"""
        from infrastructure.models.models import Config, TaskContext, StageResult, FinalResult
        assert Config is not None

    def test_infrastructure_utils(self):
        """测试 infrastructure.utils 导入"""
        from infrastructure.utils import AdaptiveConcurrencyController
        assert AdaptiveConcurrencyController is not None

    def test_domain_services(self):
        """测试 domain.services 导入"""
        from domain.services import (
            ITerminologyDomainService,
            ITranslationDomainService,
            ITermRepository,
            IBatchProcessor
        )
        assert ITerminologyDomainService is not None
        assert ITermRepository is not None

    def test_domain_models(self):
        """测试 domain.models 导入"""
        from domain.models import TranslationTask, TranslationResult, TermMatch, MatchType
        assert TranslationTask is not None
        assert TermMatch is not None

    def test_domain_terminology_service_impl(self):
        """测试 domain.terminology_service_impl 导入（关键测试）"""
        from domain.terminology_service_impl import TerminologyDomainService
        assert TerminologyDomainService is not None

    def test_domain_translation_service_impl(self):
        """测试 domain.translation_service_impl 导入"""
        from domain.translation_service_impl import TranslationDomainServiceImpl
        assert TranslationDomainServiceImpl is not None

    def test_data_access_repositories(self):
        """测试 data_access.repositories 导入（关键测试）"""
        from data_access.repositories import TerminologyRepository
        assert TerminologyRepository is not None

    def test_cross_import_data_access_to_domain(self):
        """测试跨层导入：data_access → domain"""
        from data_access.repositories import TerminologyRepository
        from domain.services import ITermRepository
        # 确保实现类实现了接口
        assert issubclass(TerminologyRepository, ITermRepository)

    def test_cross_import_domain_to_infrastructure(self):
        """测试跨层导入：domain → infrastructure"""
        from domain.translation_service_impl import TranslationDomainServiceImpl
        from infrastructure.models.models import Config
        assert Config is not None

    def test_itern_repository_from_multiple_paths(self):
        """测试 ITermRepository 可以从多个路径导入"""
        from domain.services import ITermRepository as ITermRepo1
        from domain import ITermRepository as ITermRepo2
        from infrastructure.database import ITermRepository as ITermRepo3

        # 所有导入应该指向同一个类
        assert ITermRepo1 is ITermRepo2
        assert ITermRepo1 is ITermRepo3

    def test_no_partial_initialization(self):
        """确保没有部分初始化的模块"""
        # 重新导入所有模块
        modules_to_reload = [
            'infrastructure',
            'domain',
            'data_access',
            'service',
            'application',
        ]

        for module_name in modules_to_reload:
            module = importlib.import_module(module_name)
            # 确保模块完全初始化
            assert hasattr(module, '__all__') or hasattr(module, '__file__')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
