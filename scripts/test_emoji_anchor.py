#!/usr/bin/env python
"""测试 GitHub 锚点生成规则，特别是 emoji 的处理"""
import re
import unicodedata

def test_github_anchor(title):
    """模拟 GitHub 的锚点生成规则"""
    anchor = title.lower()
    
    # 关键：GitHub 会将 emoji 替换为横杠 -
    # 每个 emoji 字符（包括组合字符）都会被替换为一个 -
    
    # 方法 1: 使用 Unicode 范围检测 emoji
    def replace_emoji_with_dash(text):
        result = []
        i = 0
        while i < len(text):
            char = text[i]
            # 检查是否是 emoji
            if is_emoji(char):
                result.append('-')
                i += 1
            else:
                # 检查是否是组合 emoji（如 👨‍👩‍👧‍👦）
                if i + 1 < len(text) and text[i+1] == '\u200d':  # ZWJ (Zero Width Joiner)
                    # 组合 emoji，整个序列替换为一个 -
                    result.append('-')
                    i += 1
                    while i < len(text):
                        if text[i] == '\u200d' or is_emoji(text[i]):
                            i += 1
                        else:
                            break
                else:
                    result.append(char)
                    i += 1
        return ''.join(result)
    
    anchor = replace_emoji_with_dash(anchor)
    
    # 移除其他特殊字符（保留中文、字母、数字、横杠）
    anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
    
    # 空格转横杠
    anchor = re.sub(r'\s+', '-', anchor)
    
    # 简化连续横杠
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    
    return f"#{anchor}"

def is_emoji(char):
    """检测字符是否是 emoji"""
    code = ord(char)
    # Common emoji ranges
    if 0x1F300 <= code <= 0x1F9FF:  # Miscellaneous Symbols and Pictographs, Emoticons
        return True
    if 0x1FA00 <= code <= 0x1FAFF:  # Chess Symbols, Alchemical Symbols
        return True
    if 0x2600 <= code <= 0x26FF:   # Miscellaneous Symbols
        return True
    if 0x2700 <= code <= 0x27BF:   # Dingbats
        return True
    if 0xFE00 <= code <= 0xFE0F:   # Variation Selectors (emoji presentation)
        return True
    # Check Unicode category
    return unicodedata.category(char) == 'So'  # Symbol, other

# 测试用例
test_cases = [
    "✨ 核心特性",
    "🏗️ 系统架构",
    "🚀 快速开始",
    "❓ 常见问题",
    "📝 更新日志",
    "🌟 重点推荐文档",
    "👉 新用户必读",
    "📁 完整文档结构",
    "🎯 按场景查找文档",
    "我是新手，想快速上手",  # 没有 emoji
    "问题 4: GUI 无响应",  # 包含冒号
]

print("=" * 80)
print("GitHub 锚点生成规则测试")
print("=" * 80)

for title in test_cases:
    anchor = test_github_anchor(title)
    print(f"\n标题：{title}")
    print(f"锚点：{anchor}")
    
    # 分析 emoji
    emojis = [c for c in title if is_emoji(c)]
    if emojis:
        print(f"Emoji 数量：{len(emojis)}")
        print(f"Emoji 字符：{emojis}")
