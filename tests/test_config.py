"""
config.py 单元测试
测试配置常量和默认值
"""
import pytest
from config import DEFAULT_DRAFT_PROMPT, DEFAULT_REVIEW_PROMPT, TARGET_LANGUAGES, GUI_CONFIG


class TestDefaultPrompts:
    """默认提示词测试"""
    
    def test_draft_prompt_exists(self):
        """测试初译提示词存在且非空"""
        assert DEFAULT_DRAFT_PROMPT is not None
        assert len(DEFAULT_DRAFT_PROMPT) > 0
    
    def test_draft_prompt_contains_placeholder(self):
        """测试初译提示词包含目标语言占位符"""
        assert '{target_lang}' in DEFAULT_DRAFT_PROMPT
    
    def test_draft_prompt_mentions_json(self):
        """测试初译提示词包含 JSON 格式要求"""
        assert 'json' in DEFAULT_DRAFT_PROMPT.lower() or 'JSON' in DEFAULT_DRAFT_PROMPT
    
    def test_review_prompt_exists(self):
        """测试校对提示词存在且非空"""
        assert DEFAULT_REVIEW_PROMPT is not None
        assert len(DEFAULT_REVIEW_PROMPT) > 0
    
    def test_review_prompt_contains_placeholder(self):
        """测试校对提示词包含目标语言占位符"""
        assert '{target_lang}' in DEFAULT_REVIEW_PROMPT
    
    def test_review_prompt_mentions_reason(self):
        """测试校对提示词包含原因说明要求"""
        assert 'Reason' in DEFAULT_REVIEW_PROMPT


class TestTargetLanguages:
    """目标语言列表测试"""
    
    def test_languages_list_not_empty(self):
        """测试语言列表非空"""
        assert len(TARGET_LANGUAGES) > 0
    
    def test_languages_are_strings(self):
        """测试所有语言都是字符串"""
        for lang in TARGET_LANGUAGES:
            assert isinstance(lang, str)
            assert len(lang) > 0
    
    def test_common_languages_included(self):
        """测试包含常用语言"""
        expected_languages = ['英语', '日语', '韩语', '法语', '德语']
        for lang in expected_languages:
            assert lang in TARGET_LANGUAGES
    
    def test_no_duplicate_languages(self):
        """测试语言列表无重复"""
        assert len(TARGET_LANGUAGES) == len(set(TARGET_LANGUAGES))


class TestGUIConfig:
    """GUI 配置测试"""
    
    def test_gui_config_exists(self):
        """测试 GUI 配置存在"""
        assert GUI_CONFIG is not None
        assert isinstance(GUI_CONFIG, dict)
    
    def test_gui_config_has_required_keys(self):
        """测试 GUI 配置包含必需的键"""
        required_keys = ['window_title', 'window_width', 'window_height']
        for key in required_keys:
            assert key in GUI_CONFIG
    
    def test_gui_config_window_title(self):
        """测试窗口标题"""
        assert 'window_title' in GUI_CONFIG
        assert len(GUI_CONFIG['window_title']) > 0
    
    def test_gui_config_window_dimensions(self):
        """测试窗口尺寸"""
        assert 'window_width' in GUI_CONFIG
        assert 'window_height' in GUI_CONFIG
        assert GUI_CONFIG['window_width'] > 0
        assert GUI_CONFIG['window_height'] > 0
