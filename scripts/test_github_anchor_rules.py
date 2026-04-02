#!/usr/bin/env python
"""
测试 GitHub 锚点生成规则 - 本地模拟

参考：https://github.com/jch/html-pipeline/blob/master/lib/html/pipeline/toc_filter.rb
GitHub 使用 html-pipeline 生成锚点 ID
"""

import re
import unicodedata


def generate_github_anchor(title):
    """
    模拟 GitHub 的锚点生成规则
    
    根据 html-pipeline 的源码：
    1. 转换为小写
    2. 移除所有标点符号（包括变体选择符）
    3. 空格转换为 -
    4. 连续 - 简化为单个 -
    5. 移除开头和结尾的 -
    """
    # 1. 转换为小写
    anchor = title.lower()
    
    # 2. 处理 emoji 和特殊字符
    def process_char(char):
        code = ord(char)
        
        # 变体选择符 (U+FE00-U+FE0F) - 移除
        if 0xFE00 <= code <= 0xFE0F:
            return ''
        
        # emoji 字符 - 转换为 -
        is_emoji = (
            0x1F300 <= code <= 0x1F9FF or  # Miscellaneous Symbols and Pictographs
            0x1FA00 <= code <= 0x1FAFF or  # Chess Symbols, Alchemical Symbols
            0x2600 <= code <= 0x26FF or    # Miscellaneous Symbols
            0x2700 <= code <= 0x27BF       # Dingbats
        )
        if is_emoji:
            return '-'
        
        # 标点符号和其他特殊字符 - 移除
        category = unicodedata.category(char)
        if category.startswith('P'):  # Punctuation
            return ''
        
        return char
    
    anchor = ''.join(process_char(c) for c in anchor)
    
    # 3. 空格转换为 -
    anchor = re.sub(r'\s+', '-', anchor)
    
    # 4. 连续 - 简化为单个 -
    anchor = re.sub(r'-+', '-', anchor)
    
    # 5. 移除开头和结尾的 -
    anchor = anchor.strip('-')
    
    return anchor


def test_anchors():
    """测试各种标题的锚点生成"""
    test_cases = [
        # (标题，预期锚点)
        ('🛠️ 技术特性', '技术特性'),  # 变体选择符 emoji
        ('🔧 工具', '工具'),  # 普通 emoji
        ('普通中文标题', '普通中文标题'),
        ('带空格的中文标题', '带空格的中文标题'),
        ('📋 目录', '目录'),
        ('🎯 目标', '目标'),
        ('✨ 核心特性', '核心特性'),
        ('🏗️ 完整系统架构图', '完整系统架构图'),
        ('📦 各层模块职责详解', '各层模块职责详解'),
        ('3 分钟快速配置', '3-分钟快速配置'),  # 空格会转换为 -
        ('⚡ 3 分钟快速配置', '3-分钟快速配置'),
    ]
    
    print("=" * 70)
    print("GitHub 锚点生成规则测试")
    print("=" * 70)
    
    all_passed = True
    for title, expected in test_cases:
        # 分析标题中的 emoji
        emoji_info = []
        for i, c in enumerate(title):
            code = ord(c)
            if code > 0x1F000 or 0x2600 <= code <= 0x27BF:
                emoji_info.append(f"'{c}'=U+{code:04X}")
        
        # 生成锚点
        anchor = generate_github_anchor(title)
        
        # 检查是否匹配
        status = "✅" if anchor == expected else "❌"
        if anchor != expected:
            all_passed = False
        
        print(f"\n{status} 标题：{title}")
        if emoji_info:
            print(f"   Emoji: {', '.join(emoji_info)}")
        print(f"   预期锚点：{expected}")
        print(f"   生成锚点：{anchor}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请检查规则")
    print("=" * 70)
    
    return all_passed


if __name__ == '__main__':
    test_anchors()
