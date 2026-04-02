#!/usr/bin/env python
"""测试 GitHub emoji 短代码锚点规则"""
import re

# Emoji 到短代码的映射
EMOJI_TO_SHORTCODE = {
    '📑': ':bookmark_tabs:',
    '✨': ':sparkles:',
    '🏗️': ':building_construction:',
    '🚀': ':rocket:',
    '📖': ':books:',
    '🧪': ':test_tube:',
    '❓': ':question:',
    '🤝': ':handshake:',
    '🎯': ':dart:',
    '📊': ':bar_chart:',
    '🛠️': ':hammer_and_wrench:',
    '📘': ':blue_book:',
    '🔧': ':wrench:',
    '⚠️': ':warning:',
    '✅': ':white_check_mark:',
    '📝': ':memo:',
    '🎉': ':tada:',
    '🔄': ':arrows_counterclockwise:',
    '📦': ':package:',
    '💡': ':bulb:',
    '📁': ':file_folder:',
}

def generate_github_anchor_with_shortcode(title):
    """
    GitHub 原生规则：emoji 替换为短代码（前后加冒号），并添加前导横杠
    例如：## 🚀 快速开始 → #-rocket-快速开始
    """
    anchor = title.lower()
    
    # 将 emoji 替换为短代码（去掉前后的冒号，只保留中间的文字）
    for emoji, shortcode in EMOJI_TO_SHORTCODE.items():
        # shortcode 格式：:name: → name
        short_name = shortcode.strip(':')
        anchor = anchor.replace(emoji, f'-{short_name}')
    
    # 移除其他特殊字符（括号、标点等）
    anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
    
    # 空格转横杠
    anchor = re.sub(r'\s+', '-', anchor)
    
    # 简化连续横杠
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    
    return f"#{anchor}"

# 测试用例
test_cases = [
    ("🚀 快速开始", "#-rocket-快速开始"),
    ("✨ 核心特性", "#-sparkles-核心特性"),
    ("🏗️ 系统架构", "#-building_construction-系统架构"),
    ("📑 目录", "#-bookmark_tabs-目录"),
    ("❓ 常见问题", "#-question-常见问题"),
]

print("测试 GitHub emoji 短代码锚点规则：")
print("=" * 80)
for title, expected in test_cases:
    result = generate_github_anchor_with_shortcode(title)
    status = "✅" if result == expected else "❌"
    print(f"{status} 标题：{title}")
    print(f"   期望：{expected}")
    print(f"   实际：{result}")
    print()
