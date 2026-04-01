#!/usr/bin/env python3
"""
文档整理工具 - 为已整合的文档添加标记头部
"""

import os
from pathlib import Path

# 文档映射关系：文件路径 -> (替代文档，章节)
DOC_MAPPINGS = {
    # 配置相关
    "docs/guides/CONFIGURATION_GUIDE.md": ("COMPLETE_MANUAL.md", "第 3 章 - 配置指南"),
    "docs/guides/CONFIG_GUIDE_DETAILED.md": ("COMPLETE_MANUAL.md", "第 3 章 - 配置指南"),
    "docs/guides/CONFIG_CHECKER_GUIDE.md": ("COMPLETE_MANUAL.md", "第 5 章 - 故障排查"),
    "docs/guides/CONFIG_QUICK_REFERENCE.md": ("COMPLETE_MANUAL.md", "第 3 章 - 配置指南"),
    "docs/guides/CONFIGURATION_CAUTIONS.md": ("COMPLETE_MANUAL.md", "第 3 章 - 配置指南"),
    "docs/guides/README_CONFIG.md": ("COMPLETE_MANUAL.md", "第 3 章 - 配置指南"),
    "docs/guides/MODEL_CONFIG_SPLIT.md": ("COMPLETE_MANUAL.md", "第 3 章 - 配置指南"),
    "docs/guides/MODEL_CONFIG_CHEATSHEET.md": ("COMPLETE_MANUAL.md", "第 3 章 - 配置指南"),
    
    # 快速开始相关
    "docs/guides/QUICKSTART.md": ("COMPLETE_MANUAL.md", "第 1 章 - 快速开始"),
    "docs/guides/TESTING_QUICKSTART.md": ("COMPLETE_MANUAL.md", "第 1 章 - 快速开始"),
    "docs/guides/COMPLETE_GUIDE.md": ("COMPLETE_MANUAL.md", "第 4 章 - 使用教程"),
    
    # 开发总结相关
    "docs/development/CODE_OPTIMIZATION_SUMMARY.md": ("PERFORMANCE_OPTIMIZATIONS.md", "性能优化"),
    "docs/development/CODE_REVIEW_REPORT.md": ("../../PROJECT_STRUCTURE.md", "项目结构"),
    "docs/development/CONFIG_VALIDATION_ENHANCEMENT.md": ("ERROR_HANDLING_GUIDE.md", "错误处理"),
    "docs/development/ERROR_HANDLING_SUMMARY.md": ("ERROR_HANDLING_GUIDE.md", "错误处理"),
    "docs/development/PERFORMANCE_IMPLEMENTATION_REPORT.md": ("PERFORMANCE_OPTIMIZATIONS.md", "性能优化"),
    "docs/development/PERFORMANCE_OPTIMIZATION_SUMMARY.md": ("PERFORMANCE_OPTIMIZATIONS.md", "性能优化"),
    "docs/development/PERFORMANCE_QUICK_REFERENCE.md": ("PERFORMANCE_OPTIMIZATIONS.md", "性能优化"),
    "docs/development/PROJECT_RESTRUCTURE_SUMMARY.md": ("../../PROJECT_STRUCTURE.md", "项目结构"),
    "docs/development/TEST_SUMMARY.md": ("TESTING_GUIDE.md", "测试指南"),
    "docs/development/UNIT_TESTS_README.md": ("TESTING_GUIDE.md", "测试指南"),
    "docs/development/UNIT_TESTS_SUMMARY.md": ("TESTING_GUIDE.md", "测试指南"),
    "docs/development/GLOBAL_EXIT_AND_EXCEL_SAVE.md": ("COMPLETE_MANUAL.md", "使用教程"),
}

DEPRECATION_NOTICE_TEMPLATE = """> ⚠️ **重要提示**: 本文档内容已整合到 [{replacement_doc}]({replacement_doc_link})  
> 建议优先阅读新手册获取更全面、更准确的信息
> 
> **整合日期**: 2026-04-01  
> **替代文档**: [{replacement_doc}]({replacement_doc_link}) {chapter_info}

---

"""

def add_deprecation_notice(file_path: str, replacement_doc: str, chapter_info: str):
    """为文档添加废弃标记"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ 文件不存在：{file_path}")
        return False
    
    # 读取原文件内容
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有标记
    if "> ⚠️ **重要提示**:" in content:
        print(f"⚠️  已有标记，跳过：{file_path}")
        return True
    
    # 计算相对路径
    file_dir = path.parent
    replacement_path = Path(replacement_doc)
    if not replacement_path.is_absolute():
        # 从当前文件目录到目标文件的相对路径
        try:
            relative_path = os.path.relpath(file_dir / replacement_path.parent, file_dir)
            replacement_doc_link = str(Path(relative_path) / replacement_path.name)
        except ValueError:
            replacement_doc_link = replacement_doc
    else:
        replacement_doc_link = replacement_doc
    
    # 生成新的标记头部
    notice = DEPRECATION_NOTICE_TEMPLATE.format(
        replacement_doc=replacement_doc,
        replacement_doc_link=replacement_doc_link,
        chapter_info=chapter_info
    )
    
    # 写入新内容
    with open(path, 'w', encoding='utf-8') as f:
        f.write(notice + content)
    
    print(f"✅ 已标记：{file_path}")
    return True

def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    print("📝 开始为已整合的文档添加标记...\n")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for file_path, (replacement_doc, chapter_info) in DOC_MAPPINGS.items():
        full_path = project_root / file_path
        result = add_deprecation_notice(str(full_path), replacement_doc, chapter_info)
        
        if result:
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n✅ 完成！")
    print(f"成功标记：{success_count} 个文档")
    print(f"错误：{error_count} 个文档")
    
    if error_count == 0:
        print("\n🎉 所有文档标记成功！")

if __name__ == "__main__":
    main()
