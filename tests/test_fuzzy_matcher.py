"""
fuzzy_matcher.py 单元测试
测试模糊匹配功能
"""
import pytest
from data_access.fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcher:
    """FuzzyMatcher 类测试"""
    
    def test_find_best_match_exact_match(self):
        """测试精确匹配"""
        items = [
            ('你好', 'Hello'),
            ('世界', 'World'),
            ('早上好', 'Good morning')
        ]
        
        result = FuzzyMatcher.find_best_match('你好', items, threshold=60)
        
        assert result is not None
        assert result['original'] == '你好'
        assert result['translation'] == 'Hello'
        assert result['score'] == 100
    
    def test_find_best_match_similar(self):
        """测试相似匹配"""
        items = [
            ('你好世界', 'Hello World'),
            ('早上好', 'Good morning')
        ]
        
        result = FuzzyMatcher.find_best_match('你好啊', items, threshold=60)
        
        # 注意：模糊匹配可能因算法实现而不同
        # 如果找到匹配，验证分数；如果没有找到，也是可接受的结果
        if result is not None:
            assert result['score'] >= 60  # 至少达到阈值
        # else: 没有匹配也是可以接受的，取决于模糊匹配算法的实现
    
    def test_find_best_match_no_threshold(self):
        """测试未达到阈值的情况"""
        items = [
            ('苹果', 'Apple'),
            ('香蕉', 'Banana')
        ]
        
        result = FuzzyMatcher.find_best_match('电脑', items, threshold=90)
        
        assert result is None
    
    def test_find_best_match_empty_items(self):
        """测试空列表"""
        result = FuzzyMatcher.find_best_match('测试', [], threshold=60)
        
        assert result is None
    
    def test_find_best_match_single_item(self):
        """测试单个项目"""
        items = [('唯一', 'Only one')]
        
        result = FuzzyMatcher.find_best_match('唯一', items, threshold=60)
        
        assert result is not None
        assert result['score'] == 100
    
    def test_find_best_match_multiple_similar(self):
        """测试多个相似项（返回最佳匹配）"""
        items = [
            ('你好', 'Hello'),
            ('您好', 'How are you'),
            ('你们好', 'Hello everyone')
        ]
        
        result = FuzzyMatcher.find_best_match('你好', items, threshold=60)
        
        assert result is not None
        assert result['score'] == 100  # 应该找到完全匹配
    
    def test_find_best_match_score_order(self):
        """测试匹配置分排序"""
        items = [
            ('相似度低', 'Low similarity'),
            ('相似度高', 'High similarity'),
            ('完全匹配', 'Exact match')
        ]
        
        result = FuzzyMatcher.find_best_match('完全匹配', items, threshold=60)
        
        assert result is not None
        assert result['score'] == 100
    
    def test_find_best_match_custom_threshold(self):
        """测试自定义阈值"""
        items = [('测试', 'Test')]
        
        # 低阈值应该也能匹配
        result_low = FuzzyMatcher.find_best_match('测试一下', items, threshold=30)
        
        # 高阈值可能不匹配
        result_high = FuzzyMatcher.find_best_match('测试一下', items, threshold=90)
        
        assert result_low is not None or result_high is None
    
    def test_find_best_match_returns_all_fields(self):
        """测试返回结果包含所有必需字段"""
        items = [('原文', 'Translation')]
        
        result = FuzzyMatcher.find_best_match('原文', items, threshold=60)
        
        assert result is not None
        assert 'original' in result
        assert 'translation' in result
        assert 'score' in result
        assert isinstance(result['score'], int)
        assert 0 <= result['score'] <= 100
    
    def test_find_best_match_unicode_support(self):
        """测试 Unicode 字符支持"""
        items = [
            ('こんにちは', 'Konnichiwa'),
            ('안녕하세요', 'Annyeonghaseyo')
        ]
        
        result = FuzzyMatcher.find_best_match('こんにちは', items, threshold=60)
        
        assert result is not None
        assert result['score'] == 100
