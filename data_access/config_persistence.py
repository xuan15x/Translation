"""
配置持久化模块
支持 JSON 和 YAML 格式的配置文件读写
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import asdict, is_dataclass


class ConfigPersistence:
    """配置持久化管理器"""
    
    # 默认配置文件名
    DEFAULT_CONFIG_FILES = {
        'json': 'config.json',
        'yaml': 'config.yaml',
        'yml': 'config.yml'
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置持久化
        
        Args:
            config_file: 配置文件路径，如果为 None 则使用默认文件名
        """
        self.config_file = config_file
        self._config_cache: Dict[str, Any] = {}
    
    def _get_file_type(self, file_path: str) -> str:
        """
        根据文件扩展名判断文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件类型 ('json', 'yaml', 'yml')
            
        Raises:
            ValueError: 不支持的文件格式
        """
        ext = Path(file_path).suffix.lower()
        if ext == '.json':
            return 'json'
        elif ext in ['.yaml', '.yml']:
            return ext[1:]  # 去掉点
        else:
            raise ValueError(f"不支持的配置文件格式：{ext}，支持的格式：.json, .yaml, .yml")
    
    def load(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            file_path: 配置文件路径，如果为 None 则使用初始化时指定的路径
            
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        path = file_path or self.config_file
        if not path:
            # 尝试查找默认配置文件
            path = self._find_default_config()
            if not path:
                return {}
        
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在：{path}")
        
        file_type = self._get_file_type(str(path))
        
        try:
            if file_type == 'json':
                config = self._load_json(path)
            else:  # yaml/yml
                config = self._load_yaml(path)
            
            self._config_cache = config
            return config
            
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败：{e}")
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """加载 JSON 配置文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        try:
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            raise ImportError("需要安装 PyYAML: pip install pyyaml")
    
    def save(self, config: Dict[str, Any], file_path: Optional[str] = None, 
             indent: int = 2) -> None:
        """
        保存配置文件
        
        Args:
            config: 配置字典
            file_path: 保存路径，如果为 None 则使用初始化时指定的路径
            indent: JSON 缩进空格数（YAML 忽略）
            
        Raises:
            ValueError: 不支持的文件格式
        """
        path = file_path or self.config_file
        if not path:
            path = self.DEFAULT_CONFIG_FILES['json']  # 默认使用 JSON
        
        path = Path(path)
        file_type = self._get_file_type(str(path))
        
        # 确保目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if file_type == 'json':
                self._save_json(path, config, indent)
            else:  # yaml/yml
                self._save_yaml(path, config)
                
            self._config_cache = config
            
        except Exception as e:
            raise RuntimeError(f"保存配置文件失败：{e}")
    
    def _save_json(self, path: Path, config: Dict[str, Any], indent: int) -> None:
        """保存 JSON 配置文件"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=indent, ensure_ascii=False)
    
    def _save_yaml(self, path: Path, config: Dict[str, Any]) -> None:
        """保存 YAML 配置文件"""
        try:
            import yaml
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
        except ImportError:
            raise ImportError("需要安装 PyYAML: pip install pyyaml")
    
    def _find_default_config(self) -> Optional[str]:
        """查找默认的配置文件"""
        for ext, filename in self.DEFAULT_CONFIG_FILES.items():
            if Path(filename).exists():
                return filename
        return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        if not self._config_cache:
            self.load()
        
        # 支持嵌套键，如 "api.base_url"
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
        if not self._config_cache:
            self.load()
        
        # 支持嵌套键
        keys = key.split('.')
        config = self._config_cache
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        批量更新配置
        
        Args:
            updates: 配置更新字典
        """
        if not self._config_cache:
            self.load()
        
        self._config_cache.update(updates)
    
    def to_dataclass(self, config_class) -> Any:
        """
        将配置转换为 dataclass 实例
        
        Args:
            config_class: dataclass 类
            
        Returns:
            dataclass 实例
        """
        if not self._config_cache:
            self.load()
        
        # 只提取 dataclass 中定义的字段
        valid_keys = set(config_class.__dataclass_fields__.keys())
        filtered_config = {k: v for k, v in self._config_cache.items() 
                          if k in valid_keys}
        
        return config_class(**filtered_config)
    
    def from_dataclass(self, config_obj) -> Dict[str, Any]:
        """
        从 dataclass 实例创建配置字典
        
        Args:
            config_obj: dataclass 实例
            
        Returns:
            配置字典
        """
        if is_dataclass(config_obj):
            return asdict(config_obj)
        else:
            raise TypeError("必须是 dataclass 实例")
    
    def merge_with_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        将配置文件与环境变量合并（此方法已废弃，仅保留用于向后兼容）
        
        Args:
            config: 配置字典
            
        Returns:
            合并后的配置字典
            
        Note:
            已废弃：API 密钥现在必须从配置文件读取，不再支持环境变量
        """
        # 不再合并环境变量，直接使用配置文件
        return config.copy()


# 便捷函数
def load_config(file_path: Optional[str] = None) -> Dict[str, Any]:
    """加载配置文件"""
    persistence = ConfigPersistence(file_path)
    return persistence.load()


def save_config(config: Dict[str, Any], file_path: Optional[str] = None) -> None:
    """保存配置文件"""
    persistence = ConfigPersistence(file_path)
    persistence.save(config)


def create_sample_config(file_path: str, include_comments: bool = True) -> None:
    """
    创建示例配置文件
    
    Args:
        file_path: 保存路径
        include_comments: 是否包含注释（仅对 YAML 有效）
    """
    sample_config = {
        "# API 配置": "如果使用 YAML 格式，这些注释会被保留",
        "api_key": "your_api_key_here",
        "base_url": "https://api.deepseek.com",
        "model_name": "deepseek-chat",
        
        "# 模型参数": "",
        "temperature": 0.3,
        "top_p": 0.8,
        
        "# 并发控制": "",
        "initial_concurrency": 8,
        "max_concurrency": 10,
        
        "# 重试配置": "",
        "retry_streak_threshold": 3,
        "base_retry_delay": 3.0,
        "max_retries": 3,
        "timeout": 60,
        
        "# 工作流配置": "",
        "enable_two_pass": True,
        "skip_review_if_local_hit": True,
        "batch_size": 1000,
        "gc_interval": 2,
        
        "# 术语库配置": "",
        "similarity_low": 60,
        "exact_match_score": 100,
        "multiprocess_threshold": 1000,
        
        "# 性能配置": "",
        "concurrency_cooldown_seconds": 5.0
    }
    
    persistence = ConfigPersistence(file_path)
    persistence.save(sample_config)
