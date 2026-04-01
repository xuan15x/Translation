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

# ============================================================================
# 支持的语言列表（按大陆板块和优先级分类）
# ============================================================================

# T1 - 主要发达国家/经济体（优先支持）
T1_LANGUAGES = [
    # 亚洲（东亚 + 东南亚）
    "日语",      # Japanese - 日本
    "韩语",      # Korean - 韩国
    "英语",      # English - 国际通用
    
    # 欧洲（西欧）
    "法语",      # French - 法国/瑞士/比利时
    "德语",      # German - 德国/奥地利/瑞士
    "西班牙语",   # Spanish - 西班牙
    "意大利语",   # Italian - 意大利/瑞士
    "葡萄牙语",   # Portuguese - 葡萄牙
    
    # 北美洲
    "英语",      # English - 美国/加拿大
    
    # 大洋洲
    "英语",      # English - 澳大利亚/新西兰
]

# T2 - 重要发展中国家/新兴市场
T2_LANGUAGES = [
    # 亚洲
    "泰语",      # Thai - 泰国
    "越南语",    # Vietnamese - 越南
    "马来语",    # Malay - 马来西亚/新加坡
    "印尼语",    # Indonesian - 印度尼西亚
    "菲律宾语",  # Filipino - 菲律宾
    "印地语",    # Hindi - 印度
    "孟加拉语",  # Bengali - 孟加拉国
    "乌尔都语",  # Urdu - 巴基斯坦
    
    # 欧洲（东欧 + 北欧）
    "俄语",      # Russian - 俄罗斯/白俄罗斯
    "波兰语",    # Polish - 波兰
    "乌克兰语",  # Ukrainian - 乌克兰
    "捷克语",    # Czech - 捷克
    "罗马尼亚语", # Romanian - 罗马尼亚
    "匈牙利语",  # Hungarian - 匈牙利
    "瑞典语",    # Swedish - 瑞典
    "挪威语",    # Norwegian - 挪威
    "丹麦语",    # Danish - 丹麦
    "芬兰语",    # Finnish - 芬兰
    "荷兰语",    # Dutch - 荷兰/比利时
    
    # 中东
    "阿拉伯语",  # Arabic - 沙特/阿联酋/埃及等
    "土耳其语",  # Turkish - 土耳其
    "波斯语",    # Persian/Farsi - 伊朗
    "希伯来语",  # Hebrew - 以色列
    
    # 非洲
    "斯瓦希里语", # Swahili - 肯尼亚/坦桑尼亚
    "南非荷兰语", # Afrikaans - 南非
    "祖鲁语",    # Zulu - 南非
]

# T3 - 其他语种（小众但重要）
T3_LANGUAGES = [
    # 亚洲
    "老挝语",    # Lao - 老挝
    "柬埔寨语",  # Khmer - 柬埔寨
    "缅甸语",    # Burmese - 缅甸
    "僧伽罗语",  # Sinhala - 斯里兰卡
    "尼泊尔语",  # Nepali - 尼泊尔
    "不丹语",    # Dzongkha - 不丹
    "蒙古语",    # Mongolian - 蒙古
    "藏语",      # Tibetan - 西藏
    "维吾尔语",  # Uyghur - 新疆
    "哈萨克语",  # Kazakh - 哈萨克斯坦
    "乌兹别克语", # Uzbek - 乌兹别克斯坦
    "吉尔吉斯语", # Kyrgyz - 吉尔吉斯斯坦
    "塔吉克语",  # Tajik - 塔吉克斯坦
    "土库曼语",  # Turkmen - 土库曼斯坦
    "阿塞拜疆语", # Azerbaijani - 阿塞拜疆
    "格鲁吉亚语", # Georgian - 格鲁吉亚
    "亚美尼亚语", # Armenian - 亚美尼亚
    
    # 欧洲（巴尔干 + 波罗的海）
    "希腊语",    # Greek - 希腊/塞浦路斯
    "保加利亚语", # Bulgarian - 保加利亚
    "塞尔维亚语", # Serbian - 塞尔维亚
    "克罗地亚语", # Croatian - 克罗地亚
    "波斯尼亚语", # Bosnian - 波黑
    "斯洛文尼亚语", # Slovenian - 斯洛文尼亚
    "斯洛伐克语", # Slovak - 斯洛伐克
    "阿尔巴尼亚语", # Albanian - 阿尔巴尼亚
    "马其顿语",  # Macedonian - 北马其顿
    "爱沙尼亚语", # Estonian - 爱沙尼亚
    "拉脱维亚语", # Latvian - 拉脱维亚
    "立陶宛语",  # Lithuanian - 立陶宛
    "冰岛语",    # Icelandic - 冰岛
    "爱尔兰语",  # Irish - 爱尔兰
    "威尔士语",  # Welsh - 威尔士
    "巴斯克语",  # Basque - 西班牙/法国
    "加泰罗尼亚语", # Catalan - 西班牙
    "加利西亚语", # Galician - 西班牙
    "马耳他语",  # Maltese - 马耳他
    "卢森堡语",  # Luxembourgish - 卢森堡
    
    # 非洲
    "豪萨语",    # Hausa - 尼日利亚
    "约鲁巴语",  # Yoruba - 尼日利亚
    "伊博语",    # Igbo - 尼日利亚
    "阿姆哈拉语", # Amharic - 埃塞俄比亚
    "索马里语",  # Somali - 索马里
    "奥罗莫语",  # Oromo - 埃塞俄比亚
    "提格里尼亚语", # Tigrinya - 厄立特里亚
    "林加拉语",  # Lingala - 刚果
    "刚果语",    # Kongo - 刚果
    "绍纳语",    # Shona - 津巴布韦
    "科萨语",    # Xhosa - 南非
    "茨瓦纳语",  # Tswana - 博茨瓦纳
    "索托语",    # Sotho - 莱索托
    "恩德贝莱语", # Ndebele - 南非/津巴布韦
    
    # 美洲原住民语言
    "克丘亚语",  # Quechua - 秘鲁/玻利维亚
    "艾马拉语",  # Aymara - 玻利维亚
    "瓜拉尼语",  # Guarani - 巴拉圭
    "玛雅语",    # Mayan - 危地马拉
    "纳瓦特尔语", # Nahuatl - 墨西哥
    
    # 大洋洲
    "毛利语",    # Maori - 新西兰
    "斐济语",    # Fijian - 斐济
    "萨摩亚语",  # Samoan - 萨摩亚
    "汤加语",    # Tongan - 汤加
    
    # 其他
    "世界语",    # Esperanto - 人造语言
    "拉丁语",    # Latin - 古典语言
    "梵语",      # Sanskrit - 古典语言
    "满语",      # Manchu - 中国东北
    "朝鲜语",    # Korean (朝鲜) - 朝鲜
]

# 合并所有语言（去重）
TARGET_LANGUAGES = list(dict.fromkeys(T1_LANGUAGES + T2_LANGUAGES + T3_LANGUAGES))

# 按优先级分类的语言字典
LANGUAGES_BY_TIER = {
    'T1': T1_LANGUAGES,
    'T2': T2_LANGUAGES,
    'T3': T3_LANGUAGES,
}

# 按大陆板块分类的语言字典
LANGUAGES_BY_CONTINENT = {
    '亚洲': [
        '日语', '韩语', '泰语', '越南语', '马来语', '印尼语', '菲律宾语',
        '印地语', '孟加拉语', '乌尔都语', '老挝语', '柬埔寨语', '缅甸语',
        '僧伽罗语', '尼泊尔语', '不丹语', '蒙古语', '藏语', '维吾尔语',
        '哈萨克语', '乌兹别克语', '吉尔吉斯语', '塔吉克语', '土库曼语',
        '阿塞拜疆语', '格鲁吉亚语', '亚美尼亚语', '阿拉伯语', '土耳其语',
        '波斯语', '希伯来语'
    ],
    '欧洲': [
        '英语', '法语', '德语', '西班牙语', '意大利语', '葡萄牙语',
        '俄语', '波兰语', '乌克兰语', '捷克语', '罗马尼亚语', '匈牙利语',
        '瑞典语', '挪威语', '丹麦语', '芬兰语', '荷兰语', '希腊语',
        '保加利亚语', '塞尔维亚语', '克罗地亚语', '波斯尼亚语', '斯洛文尼亚语',
        '斯洛伐克语', '阿尔巴尼亚语', '马其顿语', '爱沙尼亚语', '拉脱维亚语',
        '立陶宛语', '冰岛语', '爱尔兰语', '威尔士语', '巴斯克语',
        '加泰罗尼亚语', '加利西亚语', '马耳他语', '卢森堡语'
    ],
    '非洲': [
        '斯瓦希里语', '南非荷兰语', '祖鲁语', '豪萨语', '约鲁巴语',
        '伊博语', '阿姆哈拉语', '索马里语', '奥罗莫语', '提格里尼亚语',
        '林加拉语', '刚果语', '绍纳语', '科萨语', '茨瓦纳语', '索托语',
        '恩德贝莱语'
    ],
    '美洲': [
        '英语', '西班牙语', '葡萄牙语', '克丘亚语', '艾马拉语',
        '瓜拉尼语', '玛雅语', '纳瓦特尔语'
    ],
    '大洋洲': [
        '英语', '毛利语', '斐济语', '萨摩亚语', '汤加语'
    ],
    '古典/人造语言': [
        '世界语', '拉丁语', '梵语', '满语'
    ]
}

GUI_CONFIG = {
    "window_title": "AI 智能翻译工作台 v3.0",
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
