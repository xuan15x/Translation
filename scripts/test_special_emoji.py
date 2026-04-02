#!/usr/bin/env python
"""测试特殊 emoji 的 GitHub 锚点规则"""

emoji = '🛠️'
print(f'Emoji: {emoji}')
print(f'字符数：{len(emoji)}')
print('字符列表:')
for i, c in enumerate(emoji):
    print(f'  [{i}] {c} - U+{ord(c):04X}')

# 根据 GitHub 实际 URL: #️-技术特性
# 说明变体选择符被保留了！
print('\nGitHub 实际生成的锚点：#️-技术特性')
print('这说明变体选择符 U+FE0F 被保留了')
