"""
提示词注入模块 - 自动注入禁止事项
在发送翻译请求前，自动将禁止事项注入到提示词中
"""
import logging
from typing import Dict, List, Optional
from config.config import (
    get_prohibition_config, 
    get_prohibition_type_map,
    DEFAULT_PROHIBITION_CONFIG,
    DEFAULT_PROHIBITION_TYPE_MAP
)

logger = logging.getLogger(__name__)


class PromptInjector:
    """提示词注入器 - 负责将禁止事项自动注入到提示词中"""

    def __init__(self):
        """初始化注入器"""
        # 安全获取配置，如果为 None 则使用默认值
        self.config = get_prohibition_config() or DEFAULT_PROHIBITION_CONFIG
        self.type_map = get_prohibition_type_map() or DEFAULT_PROHIBITION_TYPE_MAP
    
    def get_prohibitions(self, translation_type: str) -> List[str]:
        """
        根据翻译类型获取对应的禁止事项列表
        
        Args:
            translation_type: 翻译类型（如 'match3_item', 'match3_dialogue' 等）
            
        Returns:
            禁止事项列表
        """
        if translation_type not in self.type_map:
            logger.warning(f"未知的翻译类型：{translation_type}，使用通用禁止事项")
            return self.config['global_prohibitions']
        
        prohibition_types = self.type_map[translation_type]
        prohibitions = []
        
        for ptype in prohibition_types:
            key = f"{ptype}_prohibitions"
            if key in self.config:
                prohibitions.extend(self.config[key])
        
        return prohibitions
    
    def format_prohibitions(self, prohibitions: List[str]) -> str:
        """
        格式化禁止事项为提示词文本
        
        Args:
            prohibitions: 禁止事项列表
            
        Returns:
            格式化后的禁止事项文本
        """
        if not prohibitions:
            return ""
        
        formatted = "⚠️ STRICT PROHIBITIONS (必须严格遵守):\n"
        for i, prohibition in enumerate(prohibitions, 1):
            formatted += f"{i}. {prohibition}\n"
        
        return formatted
    
    def inject_to_prompt(self, 
                        original_prompt: str, 
                        translation_type: str,
                        position: str = 'end') -> str:
        """
        将禁止事项注入到原始提示词中
        
        Args:
            original_prompt: 原始提示词
            translation_type: 翻译类型
            position: 注入位置 ('start' | 'end' | 'before_constraints')
            
        Returns:
            注入后的完整提示词
        """
        prohibitions = self.get_prohibitions(translation_type)
        
        if not prohibitions:
            return original_prompt
        
        formatted = self.format_prohibitions(prohibitions)
        
        if position == 'start':
            # 注入到开头
            return f"{formatted}\n{original_prompt}"
        
        elif position == 'before_constraints':
            # 注入到 Constraints 之前
            lines = original_prompt.split('\n')
            constraints_line = -1
            
            # 查找包含 "Constraints" 的行
            for i, line in enumerate(lines):
                if 'Constraints:' in line or '约束:' in line:
                    constraints_line = i
                    break
            
            if constraints_line >= 0:
                # 在 Constraints 之前插入
                new_lines = lines[:constraints_line] + [formatted] + lines[constraints_line:]
                return '\n'.join(new_lines)
            else:
                # 没找到 Constraints，注入到末尾
                return f"{original_prompt}\n\n{formatted}"
        
        else:  # position == 'end'
            # 注入到末尾（默认）
            return f"{original_prompt}\n\n{formatted}"
    
    def inject_draft_prompt(self, 
                           draft_prompt: str, 
                           translation_type: str) -> str:
        """
        注入初译提示词
        
        Args:
            draft_prompt: 初译提示词
            translation_type: 翻译类型
            
        Returns:
            注入后的初译提示词
        """
        # 初译提示词通常注入到 Constraints 之前或末尾
        return self.inject_to_prompt(draft_prompt, translation_type, position='before_constraints')
    
    def inject_review_prompt(self, 
                            review_prompt: str, 
                            translation_type: str) -> str:
        """
        注入校对提示词
        
        Args:
            review_prompt: 校对提示词
            translation_type: 翻译类型
            
        Returns:
            注入后的校对提示词
        """
        # 校对提示词通常注入到末尾
        return self.inject_to_prompt(review_prompt, translation_type, position='end')


# 全局单例
_injector_instance: Optional[PromptInjector] = None


def get_prompt_injector() -> PromptInjector:
    """获取提示词注入器单例"""
    global _injector_instance
    if _injector_instance is None:
        _injector_instance = PromptInjector()
    return _injector_instance


def inject_prompts(draft_prompt: str, 
                  review_prompt: str, 
                  translation_type: str) -> tuple[str, str]:
    """
    便捷函数：同时注入初译和校对提示词
    
    Args:
        draft_prompt: 初译提示词
        review_prompt: 校对提示词
        translation_type: 翻译类型
        
    Returns:
        (injected_draft, injected_review) 元组
    """
    injector = get_prompt_injector()
    
    injected_draft = injector.inject_draft_prompt(draft_prompt, translation_type)
    injected_review = injector.inject_review_prompt(review_prompt, translation_type)
    
    logger.debug(f"已注入禁止事项到提示词 - 类型：{translation_type}")
    logger.debug(f"初译提示词长度：{len(injected_draft)}")
    logger.debug(f"校对提示词长度：{len(injected_review)}")
    
    return injected_draft, injected_review
