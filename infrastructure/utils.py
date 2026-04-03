"""
通用工具函数
提供跨模块共享的工具方法
"""
from typing import Any, Dict


def get_nested_value(data: Dict, key_path: str, default: Any = None) -> Any:
    """
    从嵌套字典中获取值
    
    Args:
        data: 字典对象
        key_path: 键路径，支持点号分隔，如 'api.base_url'
        default: 默认值
    
    Returns:
        嵌套字典中的值
    
    Examples:
        >>> config = {'api': {'base_url': 'https://api.example.com'}}
        >>> get_nested_value(config, 'api.base_url')
        'https://api.example.com'
        >>> get_nested_value(config, 'api.timeout', 30)
        30
    """
    if not isinstance(data, dict):
        return default
    
    keys = key_path.split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def set_nested_value(data: Dict, key_path: str, value: Any) -> None:
    """
    设置嵌套字典的值
    
    Args:
        data: 字典对象
        key_path: 键路径，支持点号分隔，如 'api.base_url'
        value: 要设置的值
    
    Examples:
        >>> config = {}
        >>> set_nested_value(config, 'api.base_url', 'https://api.example.com')
        >>> config
        {'api': {'base_url': 'https://api.example.com'}}
    """
    if not isinstance(data, dict):
        return
    
    keys = key_path.split('.')
    current = data
    
    # 遍历到倒数第二个键
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    # 设置最后一个键的值
    current[keys[-1]] = value


def has_nested_key(data: Dict, key_path: str) -> bool:
    """
    检查嵌套字典中是否存在指定键
    
    Args:
        data: 字典对象
        key_path: 键路径，支持点号分隔
    
    Returns:
        如果键存在返回True，否则返回False
    
    Examples:
        >>> config = {'api': {'base_url': 'https://api.example.com'}}
        >>> has_nested_key(config, 'api.base_url')
        True
        >>> has_nested_key(config, 'api.timeout')
        False
    """
    if not isinstance(data, dict):
        return False
    
    keys = key_path.split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return False
    
    return True
