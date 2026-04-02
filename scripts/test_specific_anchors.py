#!/usr/bin/env python
"""测试特定标题的 GitHub 锚点"""
import re

def replace_emoji_with_dash(text):
    result = []
    for char in text:
        code = ord(char)
        is_emoji_char = (
            0x1F300 <= code <= 0x1F9FF or
            0x1FA00 <= code <= 0x1FAFF or
            0x2600 <= code <= 0x26FF or
            0x2700 <= code <= 0x27BF
        )
        if is_emoji_char:
            result.append('-')
        elif 0xFE00 <= code <= 0xFE0F:
            pass  # 变体选择符，直接移除
        else:
            result.append(char)
    return ''.join(result)

def generate_anchor(title):
    anchor = title.lower()
    anchor = replace_emoji_with_dash(anchor)
    anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
    anchor = re.sub(r'\s+', '-', anchor)
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    return f"#{anchor}"

# 测试标题
test_titles = [
    "🏗️ 完整系统架构图",
    "📑 目录",
    "🔄 核心数据流向图",
    "📦 模块职责详解",
]

print("测试 emoji 组合标题的锚点生成：")
print("=" * 80)
for title in test_titles:
    anchor = generate_anchor(title)
    emojis = [c for c in title if 0x1F300 <= ord(c) <= 0x1F9FF or 0xFE00 <= ord(c) <= 0xFE0F]
    print(f"\n标题：{title}")
    print(f"字符数：{len(title)}")
    print(f"Emoji 相关字符：{[(c, hex(ord(c))) for c in title if ord(c) >= 0x1F300 or 0xFE00 <= ord(c) <= 0xFE0F]}")
    print(f"生成锚点：{anchor}")
