"""
修复 docs/README.md 中的目录链接问题
将所有 [#-xxx](#-xxx) 改为正确的锚点格式
"""
import re

def fix_toc_links(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有实际标题
    headings = {}
    heading_pattern = r'^(#{2,6})\s+(.+)$'
    for match in re.finditer(heading_pattern, content, re.MULTILINE):
        title = match.group(2).strip()
        # 生成正确的锚点 ID
        anchor = title.lower()
        anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)
        anchor = re.sub(r'-+', '-', anchor).strip('-')
        headings[title] = anchor
    
    # 修复目录链接
    def replace_link(match):
        text = match.group(1)
        old_anchor = match.group(2)
        
        # 从文本中提取标题（移除 emoji）
        # 例如："🌟 重点推荐文档" -> "重点推荐文档"
        title_text = re.sub(r'^[^\w\u4e00-\u9fff]+', '', text).strip()
        
        # 查找对应的正确锚点
        if title_text in headings:
            correct_anchor = headings[title_text]
            return f'[{text}](#{correct_anchor})'
        
        # 如果找不到，尝试使用旧锚点（去掉前导的"-"）
        if old_anchor.startswith('-'):
            return f'[{text}](#{old_anchor[1:]})'
        
        return match.group(0)
    
    # 只替换目录部分的链接（文件前 1/3）
    lines = content.split('\n')
    toc_end_line = len(lines) // 3
    
    new_lines = []
    for i, line in enumerate(lines):
        if i < toc_end_line and '[#-' in line:
            # 修复链接
            fixed_line = re.sub(r'\[([^\]]+)\]\(#([^)]+)\)', replace_link, line)
            new_lines.append(fixed_line)
        else:
            new_lines.append(line)
    
    fixed_content = '\n'.join(new_lines)
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ 已修复 {filepath}")

if __name__ == '__main__':
    fix_toc_links('docs/README.md')
    print("完成！")
