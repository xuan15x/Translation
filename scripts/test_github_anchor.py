"""
测试 GitHub 锚点生成规则
"""
import re

def github_anchor(text):
    """
    模拟 GitHub 的锚点生成规则
    """
    # 1. 转小写
    anchor = text.lower()
    
    # 2. 移除所有非字母、数字、中文、横杠的字符（包括 emoji）
    anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
    
    # 3. 空格转横杠
    anchor = re.sub(r'\s+', '-', anchor)
    
    # 4. 连续横杠简化为单个，并移除首尾横杠
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    
    return f"#{anchor}"

# 测试用例
test_cases = [
    "✨ 核心特性",
    "🏗️ 系统架构", 
    "🚀 快速开始",
    "📖 文档导航",
    "🧪 测试",
    "❓ 常见问题",
    "🤝 贡献",
]

print("GitHub 锚点生成测试结果：")
print("=" * 60)
for title in test_cases:
    anchor = github_anchor(title)
    print(f"{title:20} -> {anchor}")
