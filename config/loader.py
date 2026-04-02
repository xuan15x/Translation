"""
配置加载器模块
提供便捷的配置加载和管理功能
"""
import os
from typing import Any, Dict, Optional, Type, TypeVar
from pathlib import Path

# 类型变量用于 dataclass
T = TypeVar('T')


class ConfigLoader:
    """配置加载器 - 单例模式"""

    _instance: Optional['ConfigLoader'] = None
    _config_cache: Dict[str, Any] = {}

    def __new__(cls) -> 'ConfigLoader':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化配置加载器"""
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._initialized = True
        self.config_file: Optional[str] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """从配置文件加载配置"""
        # 查找配置文件
        config_paths = [
            'config.yaml',
            'config.yml',
            'config.json',
            os.path.join('config', 'config.yaml'),
            os.path.join('config', 'config.json'),
        ]

        for path in config_paths:
            if os.path.exists(path):
                self.config_file = path
                break

        if self.config_file:
            try:
                from data_access.config_persistence import ConfigPersistence
                persistence = ConfigPersistence(self.config_file)
                self._config_cache = persistence.load()
                print(f"✅ 已加载配置文件：{self.config_file}")

                # 自动检查配置
                self._auto_check_config()

            except Exception as e:
                print(f"⚠️  配置文件加载失败：{e}，使用默认配置")
                self._load_default_config()
        else:
            print("ℹ️  未找到配置文件，使用默认配置")
            self._load_default_config()

    def _load_default_config(self) -> None:
        """加载默认配置"""
        from config.config import get_default_config
        self._config_cache = get_default_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键（支持嵌套，如 'api.base_url'）
            default: 默认值
            
        Returns:
            配置值
        """
        # 支持嵌套键
        keys = key.split('.')
        value = self._config_cache
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config_cache

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """获取完整配置字典"""
        return self._config_cache.copy()

    def update(self, updates: Dict[str, Any]) -> None:
        """
        批量更新配置

        Args:
            updates: 配置更新字典
        """
        self._config_cache.update(updates)

    def reload(self) -> None:
        """重新加载配置"""
        self._config_cache.clear()
        self._load_config()

    def _auto_check_config(self) -> None:
        """自动检查配置有效性"""
        try:
            from config.checker import check_config
            passed, results = check_config(self._config_cache, verbose=False)
            
            if not passed:
                errors = [r for r in results if r.level.value == 'error']
                if errors:
                    print("\n⚠️  配置存在严重问题:")
                    for error in errors[:3]:  # 只显示前 3 个错误
                        print(f"  ❌ {error.key}: {error.message}")
                    
                    warnings = [r for r in results if r.level.value == 'warning']
                    if warnings:
                        print(f"\n还有 {len(warnings)} 个警告，运行以下命令查看详情:")
                        print(f"  python scripts/check_config.py check {self.config_file}")
        except Exception as e:
            # 检查过程不影响主流程
            print(f"⚠️  配置检查异常：{e}")
    
    def save(self, output_path: Optional[str] = None) -> None:
        """
        保存配置到文件

        Args:
            output_path: 保存路径，如果为 None 则保存到原配置文件
        """
        from data_access.config_persistence import ConfigPersistence

        path = output_path or self.config_file
        if not path:
            raise ValueError("未指定保存路径")

        persistence = ConfigPersistence(path)
        persistence.save(self._config_cache)
        print(f"💾 配置已保存：{path}")

    def to_dataclass(self, config_class: Type[T]) -> T:
        """
        将配置转换为 dataclass 实例

        Args:
            config_class: dataclass 类

        Returns:
            dataclass 实例
        """
        valid_keys = set(config_class.__dataclass_fields__.keys())
        filtered_config = {k: v for k, v in self._config_cache.items()
                          if k in valid_keys}

        return config_class(**filtered_config)
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取 API 相关配置"""
        return {
            'provider': self.get('api_provider', 'deepseek'),
            'api_key': self.get('api_key', ''),
            'base_url': self.get('base_url', 'https://api.deepseek.com'),
            'model_name': self.get('model_name', 'deepseek-chat'),
            'temperature': self.get('temperature', 0.3),
            'top_p': self.get('top_p', 0.8),
        }

    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能相关配置"""
        return {
            'initial_concurrency': self.get('initial_concurrency', 8),
            'max_concurrency': self.get('max_concurrency', 10),
            'pool_size': self.get('pool_size', 5),
            'cache_capacity': self.get('cache_capacity', 2000),
            'timeout': self.get('timeout', 60),
        }

    def get_workflow_config(self) -> Dict[str, Any]:
        """获取工作流相关配置"""
        return {
            'enable_two_pass': self.get('enable_two_pass', True),
            'skip_review_if_local_hit': self.get('skip_review_if_local_hit', True),
            'batch_size': self.get('batch_size', 1000),
            'gc_interval': self.get('gc_interval', 2),
        }

    def get_terminology_config(self) -> Dict[str, Any]:
        """获取术语库相关配置"""
        return {
            'similarity_low': self.get('similarity_low', 60),
            'exact_match_score': self.get('exact_match_score', 100),
            'multiprocess_threshold': self.get('multiprocess_threshold', 1000),
        }

    def get_log_config(self) -> Dict[str, Any]:
        """获取日志相关配置"""
        return {
            'log_level': self.get('log_level', 'INFO'),
            'log_granularity': self.get('log_granularity', 'normal'),
            'log_max_lines': self.get('log_max_lines', 1000),
        }

    def get_gui_config(self) -> Dict[str, Any]:
        """获取 GUI 相关配置"""
        return {
            'window_title': self.get('gui_window_title', 'AI 智能翻译工作台 v3.0'),
            'window_width': self.get('gui_window_width', 950),
            'window_height': self.get('gui_window_height', 800),
        }

    def get_prompts(self) -> Dict[str, str]:
        """获取提示词配置"""
        return {
            'draft_prompt': self.get('draft_prompt', ''),
            'review_prompt': self.get('review_prompt', ''),
        }

    def get_languages(self) -> Dict[str, Any]:
        """获取语言配置"""
        return {
            'target_languages': self.get('target_languages', []),
            'default_source_lang': self.get('default_source_lang', '中文'),
            'supported_source_langs': self.get('supported_source_langs', []),
        }

    def get_backup_config(self) -> Dict[str, Any]:
        """获取备份相关配置"""
        return {
            'enable_version_control': self.get('enable_version_control', False),
            'enable_auto_backup': self.get('enable_auto_backup', False),
            'backup_dir': self.get('backup_dir', '.terminology_backups'),
            'backup_strategy': self.get('backup_strategy', 'daily'),
        }

    def get_monitor_config(self) -> Dict[str, Any]:
        """获取性能监控配置"""
        return {
            'enable_performance_monitor': self.get('enable_performance_monitor', False),
            'perf_sample_interval': self.get('perf_sample_interval', 1.0),
            'perf_history_size': self.get('perf_history_size', 300),
        }

    def __str__(self) -> str:
        """字符串表示"""
        return f"ConfigLoader(config_file={self.config_file}, items={len(self._config_cache)})"

    def __repr__(self) -> str:
        """调试表示"""
        return self.__str__()


# 全局配置加载器实例
_global_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """获取全局配置加载器实例"""
    global _global_loader
    if _global_loader is None:
        _global_loader = ConfigLoader()
    return _global_loader


def get_config(key: str, default: Any = None) -> Any:
    """
    便捷函数：获取配置值

    Args:
        key: 配置键
        default: 默认值

    Returns:
        配置值
    """
    loader = get_config_loader()
    return loader.get(key, default)


def get_all_config() -> Dict[str, Any]:
    """
    便捷函数：获取完整配置

    Returns:
        配置字典
    """
    loader = get_config_loader()
    return loader.get_all()


def update_config(updates: Dict[str, Any]) -> None:
    """
    便捷函数：批量更新配置

    Args:
        updates: 配置更新字典
    """
    loader = get_config_loader()
    loader.update(updates)


def reload_config() -> None:
    """便捷函数：重新加载配置"""
    loader = get_config_loader()
    loader.reload()


def save_config(output_path: Optional[str] = None) -> None:
    """
    便捷函数：保存配置到文件

    Args:
        output_path: 保存路径
    """
    loader = get_config_loader()
    loader.save(output_path)


# 测试代码
if __name__ == "__main__":
    # 测试配置加载器
    print("🧪 测试配置加载器...\n")
    
    loader = get_config_loader()
    print(f"配置加载器：{loader}\n")
    
    # 测试获取配置
    print("📊 配置摘要:")
    print(f"  API 提供商：{loader.get('api_provider')}")
    print(f"  模型：{loader.get('model_name')}")
    print(f"  并发度：{loader.get('initial_concurrency')}")
    print(f"  超时：{loader.get('timeout')}秒\n")
    
    # 测试获取分类配置
    print("🔧 API 配置:")
    api_config = loader.get_api_config()
    for key, value in api_config.items():
        print(f"  {key}: {value}")
    
    print("\n⚡ 性能配置:")
    perf_config = loader.get_performance_config()
    for key, value in perf_config.items():
        print(f"  {key}: {value}")
    
    print("\n✅ 测试完成")
