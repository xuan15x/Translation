#!/usr/bin/env python
"""批量检查和修复所有 Markdown 文档的 TOC 链接"""
import os
import re
from pathlib import Path

def replace_emoji_with_dash(text):
    """将 emoji 替换为横杠，变体选择符直接移除"""
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
            # 变体选择符，直接移除
            pass
        else:
            result.append(char)
    return ''.join(result)

def generate_github_anchor(title):
    """根据 GitHub 规则生成锚点"""
    anchor = title.lower()
    anchor = replace_emoji_with_dash(anchor)
    anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
    anchor = re.sub(r'\s+', '-', anchor)
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    return f"#{anchor}"

def extract_headings(content):
    """提取所有标题及其锚点"""
    headings = {}
    pattern = r'^(#{2,6})\s+(.+)$'
    for match in re.finditer(pattern, content, re.MULTILINE):
        title = match.group(2).strip()
        anchor = generate_github_anchor(title)
        headings[anchor] = title
    return headings

def fix_toc_links(content, headings):
    """修复 TOC 链接"""
    lines = content.split('\n')
    fixed_lines = []
    toc_pattern = re.compile(r'^(\s*)-\s+\[([^\]]+)\]\((#[^)]+)\)')
    
    for line in lines:
        match = toc_pattern.match(line)
        if match:
            indent = match.group(1)
            link_text = match.group(2)
            
            # 查找正确的锚点（移除 emoji 后匹配）
            correct_anchor = None
            clean_link = re.sub(r'[^\w\s\u4e00-\u9fff]', '', link_text).strip()
            
            for anchor, title in headings.items():
                clean_title = re.sub(r'[^\w\s\u4e00-\u9fff]', '', title).strip()
                if clean_title == clean_link:
                    correct_anchor = anchor
                    break
            
            if correct_anchor:
                new_line = f"{indent}- [{link_text}]({correct_anchor})"
                fixed_lines.append(new_line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def process_all_md_files(root_dir='.'):
    """处理所有 Markdown 文件"""
    print("=" * 80)
    print("批量检查和修复所有 Markdown 文档的 TOC 链接")
    print("=" * 80)
    
    md_files = list(Path(root_dir).rglob('*.md'))
    # 排除虚拟环境和 .pytest_cache
    md_files = [f for f in md_files if '.venv' not in str(f) and '.pytest_cache' not in str(f)]
    
    total_files = len(md_files)
    fixed_count = 0
    
    for i, filepath in enumerate(md_files, 1):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            headings = extract_headings(content)
            fixed_content = fix_toc_links(content, headings)
            
            if fixed_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"[{i}/{total_files}] ✅ {filepath}")
                fixed_count += 1
            else:
                print(f"[{i}/{total_files}] ⚪ {filepath} (无需修复)")
        except Exception as e:
            print(f"[{i}/{total_files}] ❌ {filepath} - 错误：{e}")
    
    print("\n" + "=" * 80)
    print(f"✅ 完成！共检查 {total_files} 个文件，修复了 {fixed_count} 个文件")
    print("=" * 80)

if __name__ == '__main__':
    process_all_md_files()
