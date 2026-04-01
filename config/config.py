"""
配置常量模块
提供默认配置和配置加载功能
"""
import os
from typing import Any, Dict, List, Optional
from dataclasses import asdict

# ============================================================================
# 默认配置常量（可在 config.yaml/json 中覆盖）
# ============================================================================

DEFAULT_DRAFT_PROMPT = """Role: Professional Translator.
Task: Translate 'Src' to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Strictly follow provided TM.
3. Accurate and direct."""

DEFAULT_REVIEW_PROMPT = """Role: Senior Language Editor.
Task: Polish 'Draft' into native {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars. If no change, Reason="".
3. Focus on flow and tone."""

TARGET_LANGUAGES = [
    "英语", "日语", "韩语", "法语", "德语", 
    "西班牙语", "俄语", "葡萄牙语", "意大利语", 
    "阿拉伯语", "泰语", "越南语"
]

GUI_CONFIG = {
    "window_title": "AI 智能翻译工作台 v2.0",
    "window_width": 950,
    "window_height": 800,
}

# ============================================================================
# 配置管理函数
# ============================================================================

def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置字典
    
    Returns:
        包含所有默认配置的字典
    """
    return {
        # API 基础配置
        "api_provider": "deepseek",
        "api_key": "",  # 必须在配置文件中设置
        "base_url": "https://api.deepseek.com",
        
        # 全局模型配置（默认配置，可被子配置覆盖）
        "model_name": "deepseek-chat",
        "temperature": 0.3,
        "top_p": 0.8,
        "timeout": 60,
        "max_retries": 3,
        
        # 翻译阶段（Draft）专用模型配置
        "draft_model_name": None,  # 如果为 None 则使用全局 model_name
        "draft_temperature": None,  # 如果为 None 则使用全局 temperature
        "draft_top_p": None,  # 如果为 None 则使用全局 top_p
        "draft_timeout": None,  # 如果为 None 则使用全局 timeout
        "draft_max_tokens": 512,
        
        # 校对阶段（Review）专用模型配置
        "review_model_name": None,  # 如果为 None 则使用全局 model_name
        "review_temperature": None,  # 如果为 None 则使用全局 temperature
        "review_top_p": None,  # 如果为 None 则使用全局 top_p
        "review_timeout": None,  # 如果为 None 则使用全局 timeout
        "review_max_tokens": 512,
        
        # 并发控制
        "initial_concurrency": 8,
        "max_concurrency": 10,
        "concurrency_cooldown_seconds": 5.0,
        
        # 重试配置（全局）
        "retry_streak_threshold": 3,
        "base_retry_delay": 3.0,
        
        # 工作流配置
        "enable_two_pass": True,
        "skip_review_if_local_hit": True,
        "batch_size": 1000,
        "gc_interval": 2,
        
        # 术语库配置
        "similarity_low": 60,
        "exact_match_score": 100,
        "multiprocess_threshold": 1000,
        
        # 性能配置
        "pool_size": 5,
        "cache_capacity": 2000,
        "cache_ttl_seconds": 3600,
        
        # 日志配置
        "log_level": "INFO",
        "log_granularity": "normal",
        "log_max_lines": 1000,
        
        # GUI 配置
        "gui_window_title": GUI_CONFIG["window_title"],
        "gui_window_width": GUI_CONFIG["window_width"],
        "gui_window_height": GUI_CONFIG["window_height"],
        
        # 提示词配置
        "draft_prompt": DEFAULT_DRAFT_PROMPT,
        "review_prompt": DEFAULT_REVIEW_PROMPT,
        
        # 语言配置
        "target_languages": TARGET_LANGUAGES,
        "default_source_lang": "中文",
        "supported_source_langs": ["中文", "英语", "日语", "韩语", "法语", "德语"],
        
        # 版本控制和备份
        "enable_version_control": False,
        "enable_auto_backup": False,
        "backup_dir": ".terminology_backups",
        "backup_strategy": "daily",
        
        # 性能监控
        "enable_performance_monitor": False,
        "perf_sample_interval": 1.0,
        "perf_history_size": 300,
    }


def load_config_from_file(config_file: str) -> Dict[str, Any]:
    """
    从配置文件加载配置
    
    Args:
        config_file: 配置文件路径（.json/.yaml/.yml）
        
    Returns:
        合并后的配置字典
    """
    from data_access.config_persistence import ConfigPersistence
    
    persistence = ConfigPersistence(config_file)
    file_config = persistence.load()
    
    # 合并默认配置和文件配置
    default_config = get_default_config()
    default_config.update(file_config)
    
    return default_config


def save_config_to_file(config: Dict[str, Any], config_file: str) -> None:
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        config_file: 保存路径
    """
    from data_access.config_persistence import ConfigPersistence
    
    persistence = ConfigPersistence(config_file)
    persistence.save(config)


def create_sample_config_file(output_path: str, format: str = "yaml") -> None:
    """
    创建示例配置文件
    
    Args:
        output_path: 输出文件路径
        format: 文件格式（yaml/json）
    """
    sample_config = get_default_config()
    
    # 添加注释说明
    if format == "yaml":
        yaml_content = """# AI 智能翻译工作台 - 配置文件
# 复制此文件为 config.yaml 并修改配置值
# 所有配置项都可以通过 GUI 界面或环境变量覆盖

"""
        
        sections = {
            "# ==================== API 提供商配置 ====================": [
                "api_provider", "api_key", "base_url", "model_name"
            ],
            "# ==================== 模型参数 ====================": [
                "temperature", "top_p"
            ],
            "# ==================== 并发控制 ====================": [
                "initial_concurrency", "max_concurrency", "concurrency_cooldown_seconds"
            ],
            "# ==================== 重试配置 ====================": [
                "retry_streak_threshold", "base_retry_delay", "max_retries", "timeout"
            ],
            "# ==================== 工作流配置 ====================": [
                "enable_two_pass", "skip_review_if_local_hit", "batch_size", "gc_interval"
            ],
            "# ==================== 术语库配置 ====================": [
                "similarity_low", "exact_match_score", "multiprocess_threshold"
            ],
            "# ==================== 性能优化 ====================": [
                "pool_size", "cache_capacity", "cache_ttl_seconds"
            ],
            "# ==================== 日志配置 ====================": [
                "log_level", "log_granularity", "log_max_lines"
            ],
            "# ==================== GUI 配置 ====================": [
                "gui_window_title", "gui_window_width", "gui_window_height"
            ],
            "# ==================== 提示词配置 ====================": [
                "draft_prompt", "review_prompt"
            ],
            "# ==================== 语言配置 ====================": [
                "target_languages", "default_source_lang", "supported_source_langs"
            ],
            "# ==================== 版本控制和备份 ====================": [
                "enable_version_control", "enable_auto_backup", "backup_dir", "backup_strategy"
            ],
            "# ==================== 性能监控 ====================": [
                "enable_performance_monitor", "perf_sample_interval", "perf_history_size"
            ],
        }
        
        import yaml
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
            
            for section_header, keys in sections.items():
                f.write(f"\n{section_header}\n")
                for key in keys:
                    if key in sample_config:
                        value = sample_config[key]
                        # 字符串值添加引号
                        if isinstance(value, str):
                            if '\n' in value:
                                # 多行字符串使用字面量块
                                f.write(f"{key}: |\n")
                                for line in value.split('\n'):
                                    f.write(f"  {line}\n")
                            else:
                                f.write(f'{key}: "{value}"\n')
                        elif isinstance(value, bool):
                            f.write(f"{key}: {str(value).lower()}\n")
                        elif isinstance(value, list):
                            f.write(f"{key}:\n")
                            for item in value:
                                f.write(f"  - {item}\n")
                        else:
                            f.write(f"{key}: {value}\n")
    else:
        from data_access.config_persistence import ConfigPersistence
        persistence = ConfigPersistence(output_path)
        persistence.save(sample_config)
