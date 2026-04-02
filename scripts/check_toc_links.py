"""
检查 Markdown 文件中目录索引链接是否匹配标题
"""
import re
import glob
from pathlib import Path

def extract_headings(content):
    """提取所有标题及其锚点 ID"""
    headings = {}
    # 匹配##到######的标题
    pattern = r'^(#{2,6})\s+(.+)$'
    for match in re.finditer(pattern, content, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        # 生成锚点 ID（GitHub 规则）
        anchor = title.lower()
        
        # 关键修正：GitHub 会将 emoji 替换为横杠 -
        # 但变体选择符（U+FE00-U+FE0F）会被直接移除，不会生成横杠
        def replace_emoji_with_dash(text):
            result = []
            for char in text:
                code = ord(char)
                # 检测是否是 emoji（不包括变体选择符）
                is_emoji_char = (
                    0x1F300 <= code <= 0x1F9FF or  # Miscellaneous Symbols and Pictographs
                    0x1FA00 <= code <= 0x1FAFF or  # Chess Symbols, Alchemical Symbols
                    0x2600 <= code <= 0x26FF or    # Miscellaneous Symbols
                    0x2700 <= code <= 0x27BF       # Dingbats
                )
                if is_emoji_char:
                    result.append('-')
                elif 0xFE00 <= code <= 0xFE0F:
                    # 变体选择符，直接移除（不添加横杠）
                    pass
                else:
                    result.append(char)
            return ''.join(result)
        
        anchor = replace_emoji_with_dash(anchor)
        
        # 移除其他特殊字符，保留中文、字母、数字、横杠
        anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
        # 空格转横杠
        anchor = re.sub(r'\s+', '-', anchor)
        # 简化连续横杠（不要移除开头结尾的横杠，因为 GitHub 会保留）
        anchor = re.sub(r'-+', '-', anchor)
        
        headings[anchor] = title
    return headings

def extract_toc_links(content):
    """提取目录中的链接"""
    links = []
    # 匹配目录中的链接格式 [text](#anchor)
    pattern = r'\[([^\]]+)\]\(#([^)]+)\)'
    for match in re.finditer(pattern, content):
        text = match.group(1)
        anchor = match.group(2)
        links.append((text, anchor, match.start()))
    return links

def check_file(filepath):
    """检查单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    headings = extract_headings(content)
    toc_links = extract_toc_links(content)
    
    issues = []
    for text, anchor, pos in toc_links:
        # 只检查目录部分的链接（文件前 1/3 部分）
        if pos > len(content) / 3:
            continue
        
        # 检查锚点是否存在
        if anchor not in headings:
            # 查找最接近的标题
            line_num = content[:pos].count('\n') + 1
            issues.append({
                'line': line_num,
                'text': text,
                'anchor': anchor,
                'available': list(headings.keys())
            })
    
    return issues

def main():
    import sys
    
    # 支持命令行参数指定文件
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # 默认检查所有 Markdown 文件
        files = (
            glob.glob('docs/**/*.md', recursive=True) + 
            glob.glob('*.md') +
            glob.glob('docs/*.md')
        )
    
    total_issues = 0
    
    for filepath in files:
        issues = check_file(filepath)
        if issues:
            print(f"\n❌ {filepath}")
            print("=" * 60)
            for issue in issues:
                print(f"  第 {issue['line']} 行：[{issue['text']}](#{issue['anchor']})")
                print(f"    ❌ 锚点 '#{issue['anchor']}' 不存在")
                print(f"    💡 可用的锚点:")
                for anchor in issue['available'][:5]:  # 只显示前 5 个
                    print(f"       - #{anchor}")
                if len(issue['available']) > 5:
                    print(f"       ... 还有 {len(issue['available']) - 5} 个")
                total_issues += 1
    
    if total_issues == 0:
        print("\n✅ 所有文件的目录链接都正确！")
        return 0
    else:
        print(f"\n📊 共发现 {total_issues} 个问题")
        return 1  # 返回错误码，用于 CI/CD

if __name__ == '__main__':
    main()
