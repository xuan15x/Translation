---
name: doc-sync-checker
description: >
  检测代码变更后相关文档是否同步更新，避免文档与代码不一致的问题。
  支持函数签名变更检测、配置结构变更检测、链接验证、API 文档检查。
  当需要代码文档对比、提交前检查、版本发布前验证、批量文档修复时使用。
  触发关键字：文档同步、文档检查、文档更新、文档一致性、链接验证、API 文档。
---

# 文档同步检查器 (Doc Sync Checker)

**版本**: 1.0.0
**创建日期**: 2026-04-03
**适用范围**: 所有需要维护文档的代码项目
**触发方式**: 代码变更后、提交前、版本发布前

---

## 📋 概述

文档同步检查器用于检测代码变更后相关文档是否同步更新,避免文档与代码不一致的问题。它能够识别过时的文档、缺失的更新和链接错误,确保文档与代码保持同步。

### 核心功能

- 🔍 **代码文档对比**: 检测代码变更后文档是否更新
- 🔗 **链接验证**: 验证文档中的链接和锚点有效性
- 📝 **API 文档检查**: 验证 API 文档与实现一致
- 📊 **同步报告**: 生成文档同步状态报告
- 🛠️ **修复建议**: 提供文档更新建议

---

## 🎯 使用场景

### 1. 代码变更后
修改函数签名、配置结构或接口后,检查相关文档是否更新。

### 2. 提交前检查
Git 提交前自动检查文档同步状态。

### 3. 版本发布前
发布新版本前,全面验证文档与代码的一致性。

### 4. 批量文档修复后
批量修改文档后,验证修复质量。

---

## 🔧 使用方法

### 基础用法

```python
from .qwen.skills.doc_sync_checker import DocSyncChecker

# 检查整个项目
checker = DocSyncChecker()
result = checker.check_project('/path/to/project')

print(f"文档同步状态: {'✅ 同步' if result.is_synced else '⚠️ 不同步'}")
for issue in result.issues:
    print(f"  - {issue.file}: {issue.description}")
```

### 检查特定代码变更的文档同步

```python
from .qwen.skills.doc_sync_checker import DocSyncChecker

checker = DocSyncChecker()

# 检查特定函数变更
result = checker.check_function_change(
    module='core.config',
    function_name='get_api_key',
    old_signature='get_api_key(config)',
    new_signature='get_api_key(config, provider)',
    doc_files=['docs/api/config.md', 'README.md']
)

if not result.is_synced:
    print("⚠️ 以下文档需要更新:")
    for doc in result.outdated_docs:
        print(f"  - {doc}")
```

### 验证文档链接

```python
from .qwen.skills.doc_sync_checker import LinkChecker

link_checker = LinkChecker()
result = link_checker.check_file('docs/guides/config.md')

print(f"链接验证结果:")
print(f"  ✅ 有效链接: {result.valid_count}")
print(f"  ❌ 无效链接: {result.broken_count}")
for broken in result.broken_links:
    print(f"    - {broken.url}: {broken.error}")
```

---

## 📊 检查规则

### 1. 函数签名变更检测

**规则**: 函数签名变更后,相关文档中的示例和 API 说明必须更新。

**检测流程**:
1. 解析代码文件中的函数签名（使用 AST）
2. 扫描文档中对该函数的引用
3. 对比签名是否一致
4. 标记不一致的位置

**示例**:
```python
# 代码变更
# 旧: def get_api_key(config: Dict) -> str
# 新: def get_api_key(config: Dict, provider: str) -> str

# 文档检查
# docs/api/config.md 中是否有:
# ```python
# api_key = get_api_key(config, provider)  # ✅ 正确
# api_key = get_api_key(config)            # ❌ 过时
# ```
```

### 2. 配置结构变更检测

**规则**: 配置结构变更后,所有使用旧配置的文档必须更新。

**检测流程**:
1. 解析配置 Schema 变更
2. 扫描文档中的配置示例
3. 验证示例配置是否符合新结构
4. 标记使用旧结构的文档

**示例**:
```python
# 配置变更
# 旧: config['api_key']
# 新: config['api_keys'][provider]['api_key']

# 文档检查
# 搜索文档中包含 'api_key' 的代码块
# 验证是否使用了新结构
```

### 3. 链接和锚点验证

**规则**: 文档中的所有链接和锚点必须有效。

**检测类型**:
- **内部链接**: 验证链接的目标文件存在
- **锚点链接**: 验证锚点在目标文件中存在
- **外部链接**: 验证 URL 可访问（可选）
- **图片链接**: 验证图片文件存在

**示例**:
```markdown
# 文档中的链接

✅ [配置指南](docs/guides/config.md)  # 验证 docs/guides/config.md 存在

✅ [API 说明](#api-reference)         # 验证当前文件有 ## API Reference

❌ [过时链接](docs/old_config.md)     # 文件已删除

❌ [错误锚点](#nonexistent)           # 锚点不存在
```

### 4. 版本信息同步

**规则**: 文档中的版本号必须与实际版本一致。

**检测流程**:
1. 从代码或 version 文件读取当前版本
2. 扫描文档中的版本号引用
3. 对比版本号是否一致
4. 标记过时的版本信息

---

## 💡 完整示例

### 示例 1: 配置变更后的文档同步检查

```python
from .qwen.skills.doc_sync_checker import DocSyncChecker, ConfigChangeDetector

# 1. 检测配置结构变更
config_detector = ConfigChangeDetector()
changes = config_detector.detect_changes(
    old_config='docs/examples/old_config.json',
    new_config='config/config.json'
)

print(f"检测到 {len(changes)} 个配置变更:")
for change in changes:
    print(f"  - {change.field}: {change.old_value} → {change.new_value}")

# 2. 检查文档同步
checker = DocSyncChecker()
result = checker.check_config_docs(
    config_changes=changes,
    doc_dir='docs/'
)

if not result.is_synced:
    print("\n⚠️ 以下文档需要更新:")
    for issue in result.issues:
        print(f"  📄 {issue.file}")
        print(f"     原因: {issue.description}")
        print(f"     建议: {issue.suggestion}")
```

### 示例 2: Git 提交前检查

```python
#!/usr/bin/env python
# .git/hooks/pre-commit 钩子

import sys
from pathlib import Path
from .qwen.skills.doc_sync_checker import DocSyncChecker

def main():
    project_root = Path(__file__).parent.parent
    checker = DocSyncChecker()
    
    # 获取变更的文件
    changed_files = get_staged_files()
    
    # 检查是否有代码变更
    code_files = [f for f in changed_files if f.endswith('.py')]
    if not code_files:
        return 0  # 没有代码变更,跳过检查
    
    # 检查文档同步
    result = checker.check_files(code_files)
    
    if not result.is_synced:
        print("⚠️ 检测到文档不同步:")
        for issue in result.issues:
            print(f"  📄 {issue.file}: {issue.description}")
        print("\n请更新相关文档后再提交。")
        print("或者使用 git commit --no-verify 跳过检查（不推荐）。")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

### 示例 3: 批量验证文档链接

```python
from .qwen.skills.doc_sync_checker import LinkChecker, BatchLinkChecker

# 批量检查所有 Markdown 文档
checker = BatchLinkChecker()
result = checker.check_directory('docs/', pattern='**/*.md')

print(f"文档链接验证报告:")
print(f"  📄 检查文件数: {result.files_checked}")
print(f"  🔗 链接总数: {result.total_links}")
print(f"  ✅ 有效链接: {result.valid_count}")
print(f"  ❌ 无效链接: {result.broken_count}")

if result.broken_count > 0:
    print("\n无效链接列表:")
    for broken in result.broken_links:
        print(f"  📄 {broken.file}:{broken.line}")
        print(f"     链接: {broken.url}")
        print(f"     错误: {broken.error}")
```

---

## 📝 检查清单

### 代码变更前
- [ ] 识别可能影响文档的变更点（函数签名、配置、接口）
- [ ] 列出所有相关文档
- [ ] 规划文档更新内容

### 代码变更后
- [ ] 运行 `doc_sync_checker` 检查文档同步
- [ ] 更新所有过时的文档
- [ ] 验证文档中的示例代码可运行
- [ ] 检查链接和锚点有效性
- [ ] 更新版本号（如适用）

### 提交前
- [ ] 运行完整的文档同步检查
- [ ] 修复所有发现的问题
- [ ] 验证文档格式正确
- [ ] 确认文档与代码同提交

### 版本发布前
- [ ] 全面检查所有文档
- [ ] 验证所有示例代码可运行
- [ ] 检查所有链接有效
- [ ] 确认版本号正确
- [ ] 生成文档同步报告

---

## ⚠️ 常见陷阱

### 1. 示例代码过时

**症状**: 文档中的示例代码无法运行或行为不同

**原因**: 代码变更后未更新文档示例

**解决方案**: 
- 使用 doctest 或 pytest 示例测试
- 定期检查文档示例可运行性
- 代码变更时自动标记相关示例

### 2. 锚点链接错误

**症状**: 点击链接跳转到错误位置

**原因**: 标题变更后锚点未更新

**解决方案**:
- 使用工具自动生成锚点
- 批量修改后验证所有锚点
- 遵循 GitHub 锚点生成规则

### 3. 文档遗漏

**症状**: 新功能没有对应文档

**原因**: 开发者忘记编写或更新文档

**解决方案**:
- 代码审查时检查文档完整性
- 使用工具自动识别未文档化的公共接口
- 建立文档编写规范和模板

### 4. 多处文档不一致

**症状**: 不同文档对同一功能的描述不一致

**原因**: 更新了一个文档但忘记更新其他文档

**解决方案**:
- 维护单一事实来源（Single Source of Truth）
- 使用文档生成工具从代码注释生成
- 定期检查文档一致性

---

## 🛠️ 自动化工具集成

### GitHub Actions

```yaml
name: Documentation Sync Check
on: [push, pull_request]

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Check Doc Sync
        run: |
          python -c "
          from .qwen.skills.doc_sync_checker import DocSyncChecker
          import sys

          checker = DocSyncChecker()
          result = checker.check_project('.')
          
          if not result.is_synced:
              print('⚠️ 文档不同步')
              for issue in result.issues:
                  print(f'  - {issue.file}: {issue.description}')
              sys.exit(1)
          
          print('✅ 文档同步')
          "
```

### Makefile 集成

```makefile
.PHONY: check-docs

check-docs:
	@echo "检查文档同步..."
	@python -c "\
	from .qwen.skills.doc_sync_checker import DocSyncChecker; \
	checker = DocSyncChecker(); \
	result = checker.check_project('.'); \
	print(f'文档同步状态: {\"✅ 同步\" if result.is_synced else \"⚠️ 不同步\"}'); \
	for issue in result.issues: \
	    print(f'  - {issue.file}: {issue.description}'); \
	exit(0 if result.is_synced else 1)"
```

---

## 📚 关联技能

- **import_path_validator**: 验证文档中引用的导入路径
- **config_structure_validator**: 验证文档中的配置示例
- **self_optimization**: 持续优化文档同步检查规则

---

**Skill 版本**: 1.0.0
**生效日期**: 2026-04-03
**下次审查**: 2026-05-03
**创建依据**: 最近修复任务中的文档与代码不同步问题分析