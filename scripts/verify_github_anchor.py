"""
测试 GitHub 如何处理带 emoji 的标题
"""
import re

def github_anchor_github(text):
    """
    GitHub 实际的锚点生成规则（通过实验验证）
    """
    # 1. 转小写
    anchor = text.lower()
    
    # 2. 移除所有非字母、数字、中文、横杠、空格的字符（包括 emoji）
    anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
    
    # 3. 空格转横杠
    anchor = re.sub(r'\s+', '-', anchor)
    
    # 4. 连续横杠简化为单个，并移除首尾横杠
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    
    return f"#{anchor}"

# 关键测试：emoji 在开头时会怎样？
test_cases = [
    ("✨ 核心特性", "#核心特性"),
    ("🏗️ 系统架构", "#系统架构"),
    ("## ✨ 核心特性", "#-核心特性"),  # 如果包含##会怎样？
]

print("GitHub 锚点生成规则验证：")
print("=" * 60)
for title, expected in test_cases:
    result = github_anchor_github(title)
    match = "✓" if result == expected else "✗"
    print(f"{match} {title:20} -> {result:20} (期望：{expected})")

# 重点：检查我们的当前链接格式
print("\n" + "=" * 60)
print("当前 README.md 中的链接格式：")
print("=" * 60)

with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()
    toc_start = content.find('## 📑 目录')
    toc_end = content.find('---', toc_start)
    toc_section = content[toc_start:toc_end]
    
    # 提取所有链接
    links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', toc_section)
    for text, anchor in links:
        print(f"[{text}](#{anchor})")
