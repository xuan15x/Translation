"""
快速检查指定 Markdown 文件的 TOC 链接
"""
import sys
import re

def extract_headings(content):
    headings = {}
    pattern = r'^(#{2,6})\s+(.+)$'
    for match in re.finditer(pattern, content, re.MULTILINE):
        title = match.group(2).strip()
        anchor = title.lower()
        anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)
        anchor = re.sub(r'-+', '-', anchor).strip('-')
        
        # GitHub 规则：emoji 开头会留下前导横杠
        import unicodedata
        if title and unicodedata.category(title[0]) == 'So':  # Symbol, other (emoji)
            anchor = '-' + anchor
        
        headings[anchor] = title
    return headings

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    headings = extract_headings(content)
    
    # 提取目录链接
    lines = content.split('\n')
    toc_end = len(lines) // 3
    
    issues = []
    for i, line in enumerate(lines[:toc_end]):
        matches = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', line)
        for text, anchor in matches:
            if anchor not in headings:
                issues.append((i+1, text, anchor))
    
    return issues, list(headings.keys())[:10]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        filepath = 'README.md'
    else:
        filepath = sys.argv[1]
    
    print(f"检查文件：{filepath}")
    print("=" * 60)
    
    issues, sample_anchors = check_file(filepath)
    
    if issues:
        print(f"发现 {len(issues)} 个问题:")
        for line, text, anchor in issues[:5]:
            print(f"  第{line}行：[{text}](#{anchor}) - 锚点不存在")
        if len(issues) > 5:
            print(f"  ... 还有 {len(issues)-5} 个问题")
    else:
        print("✅ 所有目录链接都正确！")
    
    print("\n可用的锚点示例:")
    for anchor in sample_anchors:
        print(f"  #{anchor}")
