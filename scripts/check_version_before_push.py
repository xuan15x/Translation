#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本号一致性检查工具

用途：在 git push 前自动检查文档版本是否与代码版本一致
使用：python scripts/check_version_before_push.py

返回码:
- 0: 版本一致，可以安全推送
- 1: 版本不一致，需要先更新文档
"""

import re
import sys
from pathlib import Path


def extract_version_from_file(filepath, pattern):
    """从文件中提取版本号"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(pattern, content)
            if match:
                return match.group(1)
    except FileNotFoundError:
        print(f"❌ 文件不存在：{filepath}")
        return None
    return None


def check_versions():
    """检查所有关键文件的版本号是否一致"""
    print("=" * 60)
    print("🔍 检查文档版本号一致性...")
    print("=" * 60)
    
    # 定义要检查的文件和对应的正则表达式
    files_to_check = {
        'docs/VERSION.md': r'\*\*当前文档版本\*\*: (v\d+\.\d+\.\d+)',
        'CHANGELOG.md': r'\*\*当前版本\*\*: (v\d+\.\d+\.\d+)',
    }
    
    versions = {}
    max_length = max(len(path) for path in files_to_check.keys())
    
    # 提取每个文件的版本号
    print("\n📋 检查以下文件:")
    print("-" * 60)
    
    for filepath, pattern in files_to_check.items():
        version = extract_version_from_file(filepath, pattern)
        versions[filepath] = version
        status = "✓" if version else "✗"
        print(f"{status} {filepath:<{max_length}} -> {version or '未找到'}")
    
    print("-" * 60)
    
    # 检查所有版本号是否一致
    unique_versions = set(v for v in versions.values() if v)
    
    if len(unique_versions) == 0:
        print("\n❌ 错误：无法从任何文件中提取版本号！")
        print("\n请确保以下文件包含正确的版本信息:")
        for filepath in files_to_check.keys():
            print(f"  - {filepath}")
        return False
    
    elif len(unique_versions) == 1:
        version = unique_versions.pop()
        print(f"\n✅ 成功：所有文件的版本号一致！")
        print(f"   当前版本：{version}")
        print("\n🎉 可以安全推送！")
        return True
    
    else:
        print("\n❌ 错误：发现不一致的版本号！")
        print("\n详细情况:")
        for filepath, version in versions.items():
            if version:
                print(f"  - {filepath}: {version}")
            else:
                print(f"  - {filepath}: (未找到版本号)")
        
        print("\n⚠️  禁止推送！请先统一所有文件的版本号。")
        print("\n解决步骤:")
        print("  1. 更新 docs/VERSION.md 至最新版本")
        print("  2. 更新 CHANGELOG.md 至最新版本")
        print("  3. 提交并确认后再推送")
        return False


def main():
    """主函数"""
    # 检查是否在正确的项目目录
    root_files = ['docs/VERSION.md', 'CHANGELOG.md']
    for file in root_files:
        if not Path(file).exists():
            print(f"❌ 错误：请在项目根目录运行此脚本")
            print(f"   找不到文件：{file}")
            sys.exit(1)
    
    # 执行版本检查
    success = check_versions()
    
    # 根据检查结果返回相应的退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
