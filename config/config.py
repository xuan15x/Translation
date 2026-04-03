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
# 支持的语言列表（按游戏市场 T1/T2/T3 分级）
# ============================================================================

# T1 - 核心市场（高付费、高竞争、高成本）
T1_LANGUAGES = [
    "英语",      # 美国、加拿大、英国、澳大利亚
    "德语",      # 德国、奥地利、瑞士
    "法语",      # 法国、比利时、瑞士
    "日语",      # 日本
    "韩语",      # 韩国
    "瑞典语",    # 瑞典
    "挪威语",    # 挪威
    "丹麦语",    # 丹麦
    "芬兰语",    # 芬兰
]

# T2 - 潜力市场（中等付费、大流量、高增长）
T2_LANGUAGES = [
    "意大利语",   # 意大利、瑞士
    "西班牙语",   # 西班牙、墨西哥、阿根廷等
    "葡萄牙语",   # 葡萄牙、巴西
    "泰语",      # 泰国
    "越南语",    # 越南
    "印尼语",    # 印度尼西亚
    "马来语",    # 马来西亚
    "俄语",      # 俄罗斯、东欧
    "波兰语",    # 波兰
    "土耳其语",   # 土耳其
    "阿拉伯语",   # 中东、北非
]

# T3 - 新兴市场（低付费、低成本、大流量）
T3_LANGUAGES = [
    "印地语",    # 印度
    "乌尔都语",   # 巴基斯坦
    "孟加拉语",   # 孟加拉国
    "菲律宾语",   # 菲律宾
    "缅甸语",    # 缅甸
    "柬埔寨语",   # 柬埔寨
    "老挝语",    # 老挝
    "波斯语",    # 伊朗
    "希伯来语",   # 以色列
    "斯瓦希里语", # 东非
    "豪萨语",    # 尼日利亚
    "哈萨克语",   # 哈萨克斯坦
    "乌兹别克语", # 乌兹别克斯坦
]

# 合并所有语言（去重）
TARGET_LANGUAGES = list(dict.fromkeys(T1_LANGUAGES + T2_LANGUAGES + T3_LANGUAGES))

# 按市场分级分类的语言字典
LANGUAGES_BY_TIER = {
    'T1': T1_LANGUAGES,
    'T2': T2_LANGUAGES,
    'T3': T3_LANGUAGES,
}

GUI_CONFIG = {
    "window_title": "AI 智能翻译工作台 v3.0",
    "window_width": 950,
    "window_height": 800,
}

# ============================================================================
# 提示词注入配置 - 禁止事项（通过配置文件配置，自动注入）
# ============================================================================

# 默认禁止事项配置（如果配置文件中没有提供，则使用以下默认值）
DEFAULT_PROHIBITION_CONFIG = {
    # 通用禁止事项（适用于所有翻译方向）
    'global_prohibitions': [
        "禁止输出原文或保留未翻译的内容",
        "禁止添加解释性文字或注释",
        "禁止改变原文的语气和情感色彩",
        "禁止使用过于书面化或学术化的表达",
        "禁止创造原文没有的新内容",
        "禁止遗漏原文的关键信息",
        "禁止使用敏感或不适当的词汇",
        "禁止混用不同语言的表达方式",
    ],
    
    # 三消游戏专项禁止事项
    'match3_prohibitions': [
        "禁止使用超过 4 个字的道具名称（UI 限制）",
        "禁止使用生僻字或难以识别的汉字",
        "禁止使用可能引起文化误解的颜色/形状描述",
        "禁止使用过于复杂或晦涩的比喻",
        "禁止使用成人向或暴力倾向的描述",
    ],
    
    # UI 界面专项禁止事项
    'ui_prohibitions': [
        "禁止使用超过按钮容量的长文本",
        "禁止使用需要思考才能理解的表达",
        "禁止使用非标准的 UI 术语（如用'设定'代替'设置'）",
        "禁止使用可能产生歧义的简短表达",
    ],
    
    # 对话剧情专项禁止事项
    'dialogue_prohibitions': [
        "禁止使用不符合角色性格的语言风格",
        "禁止过度本地化导致失去原作韵味",
        "禁止使用与时代背景不符的流行语",
        "禁止改变对话的情感倾向（严肃→玩笑等）",
    ],
}

# 默认禁止事项类型映射
DEFAULT_PROHIBITION_TYPE_MAP = {
    'match3_item': ['global', 'match3'],
    'match3_skill': ['global', 'match3'],
    'match3_level': ['global', 'match3'],
    'match3_dialogue': ['global', 'match3', 'dialogue'],
    'match3_ui': ['global', 'match3', 'ui'],
    'dialogue': ['global', 'dialogue'],
    'ui': ['global', 'ui'],
    'scene': ['global'],
    'tutorial': ['global'],
    'achievement': ['global'],
    'custom': ['global'],
}

# 全局变量：从配置文件加载的禁止事项配置
PROMPT_INJECTION_CONFIG = None
PROHIBITION_TYPE_MAP = None


def get_prohibition_config():
    """
    获取禁止事项配置（优先从配置文件加载，否则使用默认值）
    
    Returns:
        禁止事项配置字典
    """
    global PROMPT_INJECTION_CONFIG
    
    if PROMPT_INJECTION_CONFIG is not None:
        return PROMPT_INJECTION_CONFIG
    
    # 尝试从配置文件加载
    try:
        from config.loader import get_config_loader
        loader = get_config_loader()
        
        prohibition_config = loader.get('prohibition_config')
        if prohibition_config:
            PROMPT_INJECTION_CONFIG = prohibition_config
        else:
            PROMPT_INJECTION_CONFIG = DEFAULT_PROHIBITION_CONFIG
            
    except Exception as e:
        # 如果加载失败，使用默认配置
        PROMPT_INJECTION_CONFIG = DEFAULT_PROHIBITION_CONFIG
    
    return PROMPT_INJECTION_CONFIG


def get_prohibition_type_map():
    """
    获取禁止事项类型映射（优先从配置文件加载，否则使用默认值）
    
    Returns:
        禁止事项类型映射字典
    """
    global PROHIBITION_TYPE_MAP
    
    if PROHIBITION_TYPE_MAP is not None:
        return PROHIBITION_TYPE_MAP
    
    # 尝试从配置文件加载
    try:
        from config.loader import get_config_loader
        loader = get_config_loader()
        
        type_map = loader.get('prohibition_type_map')
        if type_map:
            PROHIBITION_TYPE_MAP = type_map
        else:
            PROHIBITION_TYPE_MAP = DEFAULT_PROHIBITION_TYPE_MAP
            
    except Exception as e:
        # 如果加载失败，使用默认映射
        PROHIBITION_TYPE_MAP = DEFAULT_PROHIBITION_TYPE_MAP

    return PROHIBITION_TYPE_MAP


# 延迟加载配置（避免循环导入）
# 使用函数而不是模块级常量，仅在首次访问时加载配置
def get_prompt_injection_config():
    """获取禁止事项配置（延迟加载）"""
    return get_prohibition_config()


def get_prohibition_type_map_global():
    """获取禁止事项类型映射（延迟加载）"""
    return get_prohibition_type_map()

# ============================================================================
# 游戏翻译方向配置（特别强化三消游戏）
# ============================================================================

# 游戏翻译方向类型
GAME_TRANSLATION_TYPES = {
    'match3_item': '🎮 三消 - 道具元素',
    'match3_skill': '⚡ 三消 - 技能特效',
    'match3_level': '🏆 三消 - 关卡目标',
    'match3_dialogue': '💬 三消 - 角色对话',
    'match3_ui': '🖥️ 三消 - UI 界面',
    'dialogue': '📖 通用 - 对话剧情',
    'ui': '🖥️ 通用 - UI 界面',
    'scene': '🌍 通用 - 场景描述',
    'tutorial': '📚 通用 - 教程提示',
    'achievement': '🏅 通用 - 成就称号',
    'custom': '⚙️ 自定义',
}

# 各方向的默认提示词模板（针对三消游戏优化）
GAME_DRAFT_PROMPTS = {
    'match3_item': """Role: Match-3 Game Item Translator.
Task: Translate match-3 game items/elements to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Keep names short, catchy, and memorable.
3. Preserve color/shape references (e.g., "Red Gem", "Golden Star").
4. Match casual game tone - fun and engaging.
5. Maintain consistency with existing item names.

Match-3 Specific Guidelines:
- Use simple, recognizable words
- Emphasize visual characteristics
- Keep 2-4 words max for UI fit
- Add emoji if appropriate for casual audience

Example:
Input: "Rainbow Crystal"
Output: {{"Trans": "彩虹水晶"}}""",

    'match3_skill': """Role: Match-3 Game Skill Effects Translator.
Task: Translate skill/bomb/boost effects to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Make skill names dynamic and exciting.
3. Clearly convey the effect type (explosion, swap, clear).
4. Use action-oriented language.
5. Keep power-ups sounding powerful and fun.

Match-3 Skill Types:
- Bombs/Explosives: Emphasize impact
- Boosters: Emphasize enhancement
- Special Combos: Emphasize uniqueness
- Magic Spells: Use fantasy terminology

Example:
Input: "Lightning Bolt - Clear entire row"
Output: {{"Trans": "闪电 - 清除整行"}}""",

    'match3_level': """Role: Match-3 Level Objective Translator.
Task: Translate level goals/objectives to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Make objectives clear and achievable.
3. Use encouraging, motivating language.
4. Specify numbers and targets precisely.
5. Keep casual, friendly tone.

Level Goal Types:
- Score targets: "Reach X points"
- Collection goals: "Collect X items"
- Clear objectives: "Clear all jelly"
- Move limits: "In X moves"

Example:
Input: "Collect 50 stars in 15 moves"
Output: {{"Trans": "15 步内收集 50 颗星星"}}""",

    'match3_dialogue': """Role: Match-3 Game Dialogue Translator.
Task: Translate character dialogues/stories to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Keep dialogue light-hearted and casual.
3. Match character personality (friendly, quirky, wise).
4. Use simple, conversational language.
5. Preserve humor and emotional moments.

Match-3 Story Style:
- Short, snappy sentences
- Emotional but not overly dramatic
- Family-friendly content
- Clear quest/narrative progression

Example:
Input: "Great job! Now let's save the kingdom!"
Output: {{"Trans": "太棒了！现在让我们拯救王国吧！"}}""",

    'match3_ui': """Role: Match-3 Game UI Translator.
Task: Translate UI elements/buttons/menus to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. EXTREMELY concise - fit in small buttons.
3. Use standard mobile game conventions.
4. Max 2-4 Chinese characters preferred.
5. Instantly understandable at a glance.

Common UI Elements:
- Play/Start: "开始" / "游玩"
- Settings: "设置"
- Shop: "商店"
- Lives/Energy: "体力" / "生命"
- Coins/Gems: "金币" / "宝石"
- Level Complete: "过关" / "完成"

Example:
Input: "Play Again"
Output: {{"Trans": "再玩一次"}}""",

    'dialogue': """Role: Game Dialogue Translator.
Task: Translate character dialogue to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Maintain character voice and personality.
3. Make it natural and fluent.
4. Adapt cultural references appropriately.

Example:
Input: "I'll protect you!"
Output: {{"Trans": "我会保护你的！"}}""",

    'ui': """Role: Game UI Translator.
Task: Translate UI text to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Keep concise for UI display.
3. Preserve formatting tags.
4. Match game terminology style.

Example:
Input: "Start Game"
Output: {{"Trans": "开始游戏"}}""",

    'scene': """Role: Scene Description Translator.
Task: Translate scene descriptions to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Create immersive atmosphere.
3. Use vivid descriptive language.
4. Maintain mood and tone.

Example:
Input: "The ancient ruins stood silently in the mist."
Output: {{"Trans": "古老的遗迹静静地矗立在薄雾中。"}}""",

    'tutorial': """Role: Tutorial/Hint Translator.
Task: Translate tutorial instructions to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Use clear, simple language.
3. Make instructions easy to follow.
4. Use imperative mood.

Example:
Input: "Match 3 gems to clear them"
Output: {{"Trans": "匹配 3 个宝石即可消除"}}""",

    'achievement': """Role: Achievement Title Translator.
Task: Translate achievement names/descriptions to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Make titles sound prestigious.
3. Keep descriptions concise.
4. Use formal or epic style.

Example:
Input: "Master Collector - Collect 1000 items"
Output: {{"Trans": "收藏大师 - 收集 1000 个物品"}}""",

    'custom': DEFAULT_DRAFT_PROMPT,
}

GAME_REVIEW_PROMPTS = {
    'match3_item': """Role: Senior Match-3 Item Editor.
Task: Polish item translation into catchy {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. Ensure names are short and memorable.
4. Verify color/shape clarity.
5. Check casual game appeal.

Focus: Catchiness, brevity, visual clarity""",

    'match3_skill': """Role: Senior Match-3 Skill Editor.
Task: Polish skill translation into exciting {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. Enhance impact and excitement.
4. Verify effect clarity.
5. Check power fantasy delivery.

Focus: Impact, excitement, clarity""",

    'match3_level': """Role: Senior Match-3 Level Editor.
Task: Polish level objectives into motivating {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. Ensure goals are crystal clear.
4. Verify numbers are accurate.
5. Check encouraging tone.

Focus: Clarity, motivation, accuracy""",

    'match3_dialogue': """Role: Senior Match-3 Dialogue Editor.
Task: Polish dialogue into natural {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. Ensure light-hearted tone.
4. Check character consistency.
5. Verify family-friendly content.

Focus: Tone, naturalness, consistency""",

    'match3_ui': """Role: Senior Match-3 UI Editor.
Task: Polish UI text into ultra-concise {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. MUST fit in small buttons.
4. Use standard conventions.
5. Instant recognition priority.

Focus: Brevity, convention, clarity""",

    'dialogue': """Role: Senior Dialogue Editor.
Task: Polish dialogue into natural {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. Ensure character voice consistency.
4. Make dialogue sound natural.
5. Check emotional tone.

Focus: Character voice, naturalness, emotion""",

    'ui': """Role: Senior UI Editor.
Task: Polish UI translation into concise {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. Ensure UI text is concise.
4. Check formatting preserved.
5. Verify terminology consistency.

Focus: Clarity, brevity, consistency""",

    'scene': """Role: Senior Scene Editor.
Task: Polish scene description into immersive {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. Enhance atmospheric quality.
4. Improve flow and readability.
5. Verify mood preservation.

Focus: Atmosphere, flow, immersion""",

    'tutorial': """Role: Senior Tutorial Editor.
Task: Polish tutorial into clear {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. Ensure instructions are crystal clear.
4. Simplify complex sentences.
5. Verify technical accuracy.

Focus: Clarity, simplicity, accuracy""",

    'achievement': """Role: Senior Achievement Editor.
Task: Polish achievement into prestigious {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars.
3. Ensure titles sound rewarding.
4. Verify descriptions motivating.
5. Check formal/epic tone.

Focus: Prestige, motivation, tone""",

    'custom': DEFAULT_REVIEW_PROMPT,
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
