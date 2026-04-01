"""
统一数据持久化管理器
负责在程序退出时将所有 SQLite 内存数据库的数据保存回 Excel 文件
"""
import logging
from typing import List, Dict, Any
from data_access.excel_sqlite_persistence import (
    TerminologyPersistence, 
    HistoryPersistence,
    ExcelSQLiteManager
)
from service.translation_history import TranslationHistoryManager
from service.terminology_history import TerminologyHistoryManager

logger = logging.getLogger(__name__)


class GlobalPersistenceManager:
    """全局持久化管理器 - 管理所有使用 SQLite 内存数据库的模块"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化管理器"""
        if GlobalPersistenceManager._initialized:
            return
        
        self._persistences: Dict[str, Any] = {}
        self._history_managers: Dict[str, Any] = {}  # 存储历史管理器
        self._registered = False
        GlobalPersistenceManager._initialized = True
        
        logger.info("✅ 全局持久化管理器已初始化")
    
    @classmethod
    def get_instance(cls) -> 'GlobalPersistenceManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_terminology(self, persistence: TerminologyPersistence):
        """
        注册术语库持久化
        
        Args:
            persistence: 术语库持久化实例
        """
        self._persistences['terminology'] = persistence
        logger.info("📚 术语库已注册到全局管理器")
    
    def register_history(self, persistence: HistoryPersistence):
        """
        注册历史库持久化
        
        Args:
            persistence: 历史库持久化实例
        """
        self._persistences['history'] = persistence
        logger.info("📜 历史库已注册到全局管理器")
    
    def register_translation_history(self, manager: TranslationHistoryManager):
        """
        注册翻译历史管理器
        
        Args:
            manager: 翻译历史管理器实例
        """
        self._history_managers['translation_history'] = manager
        logger.info("📝 翻译历史已注册到全局管理器")
    
    def register_terminology_history(self, manager: TerminologyHistoryManager):
        """
        注册术语历史管理器
        
        Args:
            manager: 术语历史管理器实例
        """
        self._history_managers['terminology_history'] = manager
        logger.info("📚 术语历史已注册到全局管理器")
    
    def save_all(self):
        """
        保存所有注册的数据库到 Excel 文件
        
        Returns:
            保存结果统计
        """
        if not self._persistences and not self._history_managers:
            logger.info("ℹ️ 无已注册的数据库，跳过保存")
            return {'saved': 0, 'failed': 0}
        
        results = {'saved': 0, 'failed': 0, 'details': []}
        
        logger.info("💾 开始保存所有数据库到 Excel...")
        
        # 保存持久化实例（术语库、历史库等）
        for name, persistence in self._persistences.items():
            try:
                if hasattr(persistence, 'save_to_excel') and callable(persistence.save_to_excel):
                    output_path = persistence.save_to_excel()
                    logger.info(f"✅ {name} 已保存：{output_path}")
                    results['saved'] += 1
                    results['details'].append({
                        'name': name,
                        'status': 'success',
                        'path': output_path
                    })
                else:
                    logger.warning(f"⚠️ {name} 不支持 save_to_excel 方法，跳过")
                    results['details'].append({
                        'name': name,
                        'status': 'skipped',
                        'reason': 'no save_to_excel method'
                    })
                    
            except Exception as e:
                logger.error(f"❌ {name} 保存失败：{e}")
                results['failed'] += 1
                results['details'].append({
                    'name': name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 导出历史管理器数据到 Excel
        for name, manager in self._history_managers.items():
            try:
                if hasattr(manager, 'export_to_excel') and callable(manager.export_to_excel):
                    output_path = manager.export_to_excel()
                    logger.info(f"✅ {name} 已导出：{output_path}")
                    results['saved'] += 1
                    results['details'].append({
                        'name': name,
                        'status': 'success',
                        'path': output_path
                    })
                else:
                    logger.warning(f"⚠️ {name} 不支持 export_to_excel 方法，跳过")
                    results['details'].append({
                        'name': name,
                        'status': 'skipped',
                        'reason': 'no export_to_excel method'
                    })
                    
            except Exception as e:
                logger.error(f"❌ {name} 导出失败：{e}")
                results['failed'] += 1
                results['details'].append({
                    'name': name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        total = results['saved'] + results['failed']
        logger.info(f"💾 保存完成：成功 {results['saved']}/{total}, 失败 {results['failed']}/{total}")
        
        return results
    
    def close_all(self):
        """
        关闭所有注册的数据库连接
        
        Returns:
            关闭结果统计
        """
        if not self._persistences:
            return {'closed': 0}
        
        results = {'closed': 0, 'failed': 0}
        
        for name, persistence in self._persistences.items():
            try:
                if hasattr(persistence, 'close') and callable(persistence.close):
                    persistence.close()
                    results['closed'] += 1
                    logger.info(f"🔒 {name} 连接已关闭")
                else:
                    results['failed'] += 1
                    logger.warning(f"⚠️ {name} 不支持 close 方法")
            except Exception as e:
                results['failed'] += 1
                logger.error(f"❌ {name} 关闭失败：{e}")
        
        logger.info(f"🔒 关闭完成：成功 {results['closed']}, 失败 {results['failed']}")
        return results
    
    def shutdown_all(self):
        """
        完整关闭流程：先保存，再关闭
        
        Returns:
            关闭结果统计
        """
        logger.info("🛑 开始关闭全局持久化管理器...")
        
        # 先保存所有数据
        save_results = self.save_all()
        
        # 再关闭所有连接
        close_results = self.close_all()
        
        # 清空注册表
        self._persistences.clear()
        
        results = {
            'save': save_results,
            'close': close_results,
            'total_saved': save_results['saved'],
            'total_failed': save_results['failed'] + close_results['failed']
        }
        
        if results['total_failed'] == 0:
            logger.info("✅ 全局持久化管理器已正常关闭")
        else:
            logger.warning(f"⚠️ 全局持久化管理器关闭时有 {results['total_failed']} 个错误")
        
        return results


# 便捷函数
def get_global_persistence_manager() -> GlobalPersistenceManager:
    """获取全局持久化管理器单例"""
    return GlobalPersistenceManager.get_instance()


def save_all_databases():
    """保存所有数据库到 Excel"""
    manager = get_global_persistence_manager()
    return manager.save_all()


def shutdown_all_databases():
    """关闭所有数据库连接并保存"""
    manager = get_global_persistence_manager()
    return manager.shutdown_all()
