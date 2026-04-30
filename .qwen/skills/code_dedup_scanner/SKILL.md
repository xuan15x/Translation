---
name: code-dedup-scanner
description: >
  扫描 Python 项目中的重复类和相似文件，识别代码重复问题。
  支持重复类检测、相似文件扫描、报告生成等功能。
  当需要代码去重、重构辅助、质量门禁、技术债务评估时使用。
  触发关键字：代码重复、重复类、相似文件、代码去重、重复扫描、重复检测。
---

# 代码重复扫描器 (Code Dedup Scanner)

**版本**: 1.0.0
**创建日期**: 2026-04-03
**适用范围**: 所有 Python 项目
**触发方式**: 手动调用或 CI/CD 集成

---

## 📋 概述

代码重复扫描器是一个自动化工具，用于扫描 Python 项目中的重复类和相似文件。它帮助开发者识别代码重复问题，提升代码质量和可维护性。

### 核心功能

- 🔍 **重复类扫描**: 检测项目中同名类的定义
- 📄 **相似文件扫描**: 基于相似度算法识别重复或高度相似的文件
- 📊 **报告生成**: 生成结构化的扫描报告，支持多种输出格式
- ⚙️ **灵活配置**: 支持自定义扫描路径、过滤规则和相似度阈值

---

## 🎯 使用场景

### 1. 代码审查
在代码审查前运行扫描器，快速识别潜在的重复代码问题。

### 2. 重构辅助
在重构大型项目时，帮助识别可以合并或抽象的重复类。

### 3. 质量门禁
集成到 CI/CD 流程中，作为代码质量检查的一部分。

### 4. 技术债务评估
定期扫描项目，评估和跟踪代码重复导致的技术债务。

---

## 🔧 使用方法

### 基础用法

```python
from .qwen.skills.code_dedup_scanner import CodeDedupScanner

# 扫描重复类
duplicates = CodeDedupScanner.scan_duplicate_classes("/path/to/project")

# 扫描相似文件
similar_files = CodeDedupScanner.scan_duplicate_files("/path/to/project")

# 生成报告
report = CodeDedupScanner.generate_report(duplicates, similar_files)
print(report)
```

### 高级用法

```python
from .qwen.skills.code_dedup_scanner import CodeDedupScanner

# 自定义配置
config = {
    'exclude_dirs': ['tests', 'migrations', 'venv'],
    'exclude_files': ['__init__.py', 'conftest.py'],
    'similarity_threshold': 0.85,
    'include_tests': False
}

# 扫描并应用配置
duplicates = CodeDedupScanner.scan_duplicate_classes(
    project_root="/path/to/project",
    **config
)

similar_files = CodeDedupScanner.scan_duplicate_files(
    project_root="/path/to/project",
    **config
)

# 导出为 JSON 格式报告
report_json = CodeDedupScanner.generate_report(
    duplicates, 
    similar_files,
    output_format='json'
)
```

---

## ⚙️ 配置选项

### scan_duplicate_classes() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `project_root` | `str` | 必需 | 项目根目录路径 |
| `exclude_dirs` | `List[str]` | `['.git', '.venv', 'venv', '__pycache__', 'node_modules']` | 排除的目录 |
| `exclude_files` | `List[str]` | `['__init__.py']` | 排除的文件 |
| `include_tests` | `bool` | `False` | 是否扫描测试文件 |

### scan_duplicate_files() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `project_root` | `str` | 必需 | 项目根目录路径 |
| `similarity_threshold` | `float` | `0.8` | 相似度阈值 (0.0-1.0) |
| `exclude_dirs` | `List[str]` | 同上 | 排除的目录 |
| `exclude_files` | `List[str]` | 同上 | 排除的文件 |
| `min_lines` | `int` | `10` | 最小代码行数（过滤过短文件） |

### generate_report() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `duplicates` | `List[Dict]` | 必需 | 重复类清单 |
| `similar_files` | `List[Dict]` | 必需 | 相似文件对清单 |
| `output_format` | `str` | `'text'` | 输出格式：`'text'`, `'json'`, `'markdown'` |
| `output_file` | `Optional[str]` | `None` | 输出文件路径（如提供则保存到文件） |

---

## 📊 输出格式

### 重复类扫描结果结构

```python
[
    {
        'class_name': 'ClassName',
        'locations': [
            {
                'file': 'path/to/file1.py',
                'line': 10,
                'code_snippet': 'class ClassName:\n    ...'
            },
            {
                'file': 'path/to/file2.py',
                'line': 25,
                'code_snippet': 'class ClassName:\n    ...'
            }
        ],
        'count': 2
    }
]
```

### 相似文件扫描结果结构

```python
[
    {
        'file1': 'path/to/file1.py',
        'file2': 'path/to/file2.py',
        'similarity': 0.85,
        'common_lines': 42,
        'total_lines_file1': 50,
        'total_lines_file2': 48
    }
]
```

### 文本报告示例

```
═══════════════════════════════════════════════════════
代码重复扫描报告
生成时间: 2026-04-03 15:30:45
═══════════════════════════════════════════════════════

【重复类】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. UserService (2 处定义)
   • src/services/user_service.py:15
   • src/api/v1/user_service.py:22

2. ConfigManager (3 处定义)
   • src/config/manager.py:8
   • src/utils/config.py:45
   • tests/test_config.py:12

【相似文件】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. src/services/user_service.py ↔ src/api/v1/user_service.py
   相似度: 85.2% | 共同代码行: 42/50

2. src/models/user.py ↔ src/models/admin.py
   相似度: 82.1% | 共同代码行: 38/46

【统计摘要】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• 扫描文件总数: 156
• 发现重复类: 5 个（涉及 12 处定义）
• 发现相似文件对: 8 对
• 平均相似度: 83.5%

═══════════════════════════════════════════════════════
```

---

## 💡 示例

### 示例 1: 扫描当前项目

```python
from .qwen.skills.code_dedup_scanner import CodeDedupScanner
import os

# 获取项目根目录
project_root = os.getcwd()

# 执行扫描
duplicates = CodeDedupScanner.scan_duplicate_classes(project_root)
similar_files = CodeDedupScanner.scan_duplicate_files(project_root)

# 生成并打印报告
report = CodeDedupScanner.generate_report(duplicates, similar_files)
print(report)
```

### 示例 2: 导出 JSON 报告

```python
import json
from .qwen.skills.code_dedup_scanner import CodeDedupScanner

# 扫描
duplicates = CodeDedupScanner.scan_duplicate_classes("/path/to/project")
similar_files = CodeDedupScanner.scan_duplicate_files("/path/to/project")

# 生成 JSON 报告
report_json = CodeDedupScanner.generate_report(
    duplicates, 
    similar_files,
    output_format='json'
)

# 解析和使用
data = json.loads(report_json)
print(f"发现 {len(data['duplicates'])} 个重复类")
print(f"发现 {len(data['similar_files'])} 对相似文件")
```

### 示例 3: 保存到文件

```python
from .qwen.skills.code_dedup_scanner import CodeDedupScanner

# 扫描并保存报告
CodeDedupScanner.generate_report(
    duplicates,
    similar_files,
    output_format='markdown',
    output_file='docs/code_duplication_report.md'
)
```

### 示例 4: 自定义过滤规则

```python
from .qwen.skills.code_dedup_scanner import CodeDedupScanner

# 只扫描 src 目录，排除测试和迁移文件
duplicates = CodeDedupScanner.scan_duplicate_classes(
    project_root="/path/to/project",
    exclude_dirs=['tests', 'migrations', 'venv', '.venv'],
    exclude_files=['__init__.py', 'conftest.py', 'alembic.env.py'],
    include_tests=False
)

# 使用更高的相似度阈值
similar_files = CodeDedupScanner.scan_duplicate_files(
    project_root="/path/to/project",
    similarity_threshold=0.9,  # 只报告 90% 以上相似度的文件
    min_lines=20  # 忽略 20 行以下的文件
)
```

---

## 🔍 算法说明

### 类重复检测

1. **AST 解析**: 使用 Python `ast` 模块解析所有 Python 文件
2. **类名提取**: 提取所有 `ClassDef` 节点的名称和位置信息
3. **分组对比**: 按类名分组，统计出现次数
4. **上下文提取**: 提取类定义前后几行代码作为上下文

### 文件相似度计算

1. **代码行提取**: 去除空行和注释，保留有效代码行
2. **标准化处理**: 去除变量名差异，保留结构特征
3. **Jaccard 相似度**: 计算两个文件代码行的 Jaccard 相似系数
4. **阈值过滤**: 只返回超过设定阈值的文件对

---

## ⚠️ 注意事项

### 误报处理

扫描器可能产生误报，以下情况属于正常现象：

- **同名不同义**: 不同模块中可能有同名但功能不同的类（如 `Config`、`Manager`）
- **模板生成代码**: 使用代码生成器产生的文件可能高度相似
- **测试文件**: 测试用例可能因结构相似而被标记

### 性能建议

- **大型项目**: 对于超过 1000 个 Python 文件的项目，建议分模块扫描
- **CI/CD 集成**: 设置合理的相似度阈值，避免过多误报
- **增量扫描**: 定期扫描时，可只扫描变更过的文件

### 最佳实践

1. **定期扫描**: 建议每周或每次重大重构后运行
2. **设定基线**: 首次扫描后记录基线数据，后续对比改进
3. **结合审查**: 扫描结果应结合人工代码审查使用
4. **持续改进**: 根据扫描结果制定代码去重计划

---

## 📈 质量指标

### 扫描器自检测试

运行以下命令验证扫描器功能：

```python
from .qwen.skills.code_dedup_scanner import CodeDedupScanner

# 自检测试
test_result = CodeDedupScanner.self_test()
print(f"自检测试: {'✅ 通过' if test_result else '❌ 失败'}")
```

### 性能基准

| 项目规模 | 扫描时间（估计） | 内存占用 |
|---------|----------------|---------|
| < 100 文件 | < 2 秒 | < 50 MB |
| 100-500 文件 | 2-10 秒 | 50-150 MB |
| 500-1000 文件 | 10-30 秒 | 150-300 MB |
| > 1000 文件 | 30+ 秒 | 300+ MB |

---

## 🔄 集成示例

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
python -c "
from .qwen.skills.code_dedup_scanner import CodeDedupScanner
import sys

duplicates = CodeDedupScanner.scan_duplicate_classes('.')
if duplicates:
    print('⚠️ 发现重复类，请审查后再提交')
    for dup in duplicates:
        print(f\"  - {dup['class_name']}: {dup['count']} 处定义\")
    sys.exit(1)
"
```

### GitHub Actions

```yaml
name: Code Quality Check
on: [push, pull_request]

jobs:
  scan-duplicates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Scan Duplicate Classes
        run: |
          python -c "
          from .qwen.skills.code_dedup_scanner import CodeDedupScanner
          duplicates = CodeDedupScanner.scan_duplicate_classes('.')
          similar = CodeDedupScanner.scan_duplicate_files('.')
          report = CodeDedupScanner.generate_report(duplicates, similar)
          print(report)
          "
```

---

## 📚 相关文件

- `scanner.py`: 核心实现代码
- `__init__.py`: 模块初始化文件
- `SKILL.md`: 本文档

---

**Skill 版本**: 1.0.0  
**生效日期**: 2026-04-03  
**下次审查**: 2026-05-03
