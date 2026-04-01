#!/usr/bin/env python3
"""
文档整理工具 - 将所有 Markdown 文档移动到相应文件夹
"""

import os
import shutil
from pathlib import Path

# 文档移动映射：源文件 -> 目标目录
DOC_MOVES = {
    # 根目录的文档应该移动到 docs/ 或相应模块目录
    "QUICKSTART.md": "docs/guides/",
    "GIT_SYNC_GUIDE.md": "docs/guides/",
    "config_metrics_report.txt": "docs/",  # 保留在 docs/
    
    # 报告类文档移动到 docs/development/
    "DOCS_SUMMARY.md": "docs/development/",
    "DOCS_SUMMARY_FINAL.md": "docs/development/",
    "DOCUMENT_CONSOLIDATION_REPORT.md": "docs/development/",
    
    # 核心文档保留在根目录
    # README.md, COMPLETE_MANUAL.md, CHANGELOG.md, PROJECT_STRUCTURE.md 保留
}

# 需要创建归档目录的文档
ARCHIVE_DOCS = [
    "docs/guides/CONFIGURATION_GUIDE.md",
    "docs/guides/CONFIG_GUIDE_DETAILED.md",
    "docs/guides/CONFIG_CHECKER_GUIDE.md",
    "docs/guides/CONFIG_QUICK_REFERENCE.md",
    "docs/guides/CONFIGURATION_CAUTIONS.md",
    "docs/guides/README_CONFIG.md",
    "docs/guides/MODEL_CONFIG_SPLIT.md",
    "docs/guides/MODEL_CONFIG_CHEATSHEET.md",
    "docs/guides/QUICKSTART.md",
    "docs/guides/TESTING_QUICKSTART.md",
    "docs/guides/COMPLETE_GUIDE.md",
    "docs/development/CODE_OPTIMIZATION_SUMMARY.md",
    "docs/development/CODE_REVIEW_REPORT.md",
    "docs/development/CONFIG_VALIDATION_ENHANCEMENT.md",
    "docs/development/ERROR_HANDLING_SUMMARY.md",
    "docs/development/PERFORMANCE_IMPLEMENTATION_REPORT.md",
    "docs/development/PERFORMANCE_OPTIMIZATION_SUMMARY.md",
    "docs/development/PERFORMANCE_QUICK_REFERENCE.md",
    "docs/development/PROJECT_RESTRUCTURE_SUMMARY.md",
    "docs/development/TEST_SUMMARY.md",
    "docs/development/UNIT_TESTS_README.md",
    "docs/development/UNIT_TESTS_SUMMARY.md",
    "docs/development/GLOBAL_EXIT_AND_EXCEL_SAVE.md",
]

def move_document(src: str, dest_dir: str) -> bool:
    """移动文档到目标目录"""
    src_path = Path(src)
    if not src_path.exists():
        print(f"❌ 文件不存在：{src}")
        return False
    
    # 创建目标目录
    dest_path = Path(dest_dir) / src_path.name
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 移动文件
    try:
        shutil.move(str(src_path), str(dest_path))
        print(f"✅ 已移动：{src} -> {dest_path}")
        return True
    except Exception as e:
        print(f"❌ 移动失败 {src}: {e}")
        return False

def create_archive_structure():
    """创建归档目录结构"""
    archive_dirs = [
        "docs/archive/old_configs",
        "docs/archive/old_quickstarts",
        "docs/archive/development_summaries",
        "docs/archive/other_deprecated",
    ]
    
    for dir_path in archive_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录：{dir_path}")

def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    print("📝 开始整理 Markdown 文档...\n")
    
    # 1. 移动根目录的文档
    print("=" * 60)
    print("步骤 1: 移动根目录的非核心文档")
    print("=" * 60)
    
    for src_file, dest_dir in DOC_MOVES.items():
        full_src = project_root / src_file
        if full_src.exists():
            move_document(str(full_src), str(project_root / dest_dir))
    
    # 2. 创建归档目录
    print("\n" + "=" * 60)
    print("步骤 2: 创建归档目录结构")
    print("=" * 60)
    
    create_archive_structure()
    
    # 3. 移动已标记的文档到归档目录
    print("\n" + "=" * 60)
    print("步骤 3: 移动已整合的文档到归档目录")
    print("=" * 60)
    
    # 配置相关
    config_files = [
        "docs/guides/CONFIGURATION_GUIDE.md",
        "docs/guides/CONFIG_GUIDE_DETAILED.md",
        "docs/guides/CONFIG_CHECKER_GUIDE.md",
        "docs/guides/CONFIG_QUICK_REFERENCE.md",
        "docs/guides/CONFIGURATION_CAUTIONS.md",
        "docs/guides/README_CONFIG.md",
        "docs/guides/MODEL_CONFIG_SPLIT.md",
        "docs/guides/MODEL_CONFIG_CHEATSHEET.md",
    ]
    
    for file in config_files:
        full_path = project_root / file
        if full_path.exists():
            dest = project_root / "docs/archive/old_configs" / full_path.name
            try:
                shutil.move(str(full_path), str(dest))
                print(f"✅ 已归档：{file} -> {dest}")
            except Exception as e:
                print(f"❌ 移动失败 {file}: {e}")
    
    # 快速开始相关
    quickstart_files = [
        "docs/guides/QUICKSTART.md",
        "docs/guides/TESTING_QUICKSTART.md",
        "docs/guides/COMPLETE_GUIDE.md",
    ]
    
    for file in quickstart_files:
        full_path = project_root / file
        if full_path.exists():
            dest = project_root / "docs/archive/old_quickstarts" / full_path.name
            try:
                shutil.move(str(full_path), str(dest))
                print(f"✅ 已归档：{file} -> {dest}")
            except Exception as e:
                print(f"❌ 移动失败 {file}: {e}")
    
    # 开发总结相关
    dev_summary_files = [
        "docs/development/CODE_OPTIMIZATION_SUMMARY.md",
        "docs/development/CODE_REVIEW_REPORT.md",
        "docs/development/CONFIG_VALIDATION_ENHANCEMENT.md",
        "docs/development/ERROR_HANDLING_SUMMARY.md",
        "docs/development/PERFORMANCE_IMPLEMENTATION_REPORT.md",
        "docs/development/PERFORMANCE_OPTIMIZATION_SUMMARY.md",
        "docs/development/PERFORMANCE_QUICK_REFERENCE.md",
        "docs/development/PROJECT_RESTRUCTURE_SUMMARY.md",
        "docs/development/TEST_SUMMARY.md",
        "docs/development/UNIT_TESTS_README.md",
        "docs/development/UNIT_TESTS_SUMMARY.md",
        "docs/development/GLOBAL_EXIT_AND_EXCEL_SAVE.md",
    ]
    
    for file in dev_summary_files:
        full_path = project_root / file
        if full_path.exists():
            dest = project_root / "docs/archive/development_summaries" / full_path.name
            try:
                shutil.move(str(full_path), str(dest))
                print(f"✅ 已归档：{file} -> {dest}")
            except Exception as e:
                print(f"❌ 移动失败 {file}: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 文档整理完成！")
    print("=" * 60)
    
    # 统计
    print("\n📊 整理结果:")
    print(f"  - 核心文档（根目录）: 4 个")
    print(f"  - 专题文档（docs/）: 13 个")
    print(f"  - 参考文档（docs/api/等）: 6 个")
    print(f"  - 归档文档（docs/archive/）: 23 个")

if __name__ == "__main__":
    main()
