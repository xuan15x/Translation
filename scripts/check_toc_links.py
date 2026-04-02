"""
检查 Markdown 文件中目录索引链接是否匹配标题
"""
import re
import glob
from pathlib import Path

def extract_headings(content):
    """提取所有标题及其锚点 ID"""
    headings = {}
    # 匹配 ## 到 ###### 的标题
    pattern = r'^(#{2,6})\s+(.+)$'
    for match in re.finditer(pattern, content, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        # 生成锚点 ID（GitHub 规则）
        anchor = title.lower()
        # 移除特殊字符，保留中文
        anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
        # 空格转横杠
        anchor = re.sub(r'\s+', '-', anchor)
        # 移除多余横杠
        anchor = re.sub(r'-+', '-', anchor).strip('-')
        
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
    # 查找所有 Markdown 文件
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
    else:
        print(f"\n📊 共发现 {total_issues} 个问题")

if __name__ == '__main__':
    main()
