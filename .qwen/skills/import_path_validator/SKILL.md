# 导入路径验证器 (Import Path Validator)

**版本**: 1.0.0
**创建日期**: 2026-04-03
**适用范围**: 所有 Python 项目
**触发方式**: 手动调用或 CI/CD 集成

---

## 📋 概述

导入路径验证器是一个自动化工具,用于验证 Python 项目的导入路径规范性。它能够检测同一类的多个导入路径、循环导入、`__init__.py` 导出一致性等问题,帮助维护清晰、一致的模块导入结构。

### 核心功能

- 🔍 **重复导入检测**: 发现同一类/函数从多个路径导入的问题
- 🔄 **循环导入检测**: 识别模块间的循环依赖关系
- 📦 **`__init__.py` 一致性验证**: 检查包导出与实际定义的一致性
- 📊 **项目级扫描**: 扫描整个项目,生成汇总报告
- 📝 **多格式报告**: 支持 text、json、markdown 三种输出格式

---

## 🎯 使用场景

### 1. 代码审查
在代码审查前运行验证器,快速识别重复导入和循环依赖问题,确保导入路径的清晰性。

### 2. 重构指导
分析现有代码库,找出导入路径不一致的地方,作为重构的参考。

### 3. 质量门禁
集成到 CI/CD 流程中,阻止不规范的导入路径合入主分支。

### 4. 模块结构优化
定期检查项目的模块导出结构,确保 `__init__.py` 的公开 API 与实际实现一致。

### 5. 技术债务评估
评估导入路径的混乱程度,跟踪模块结构的健康度。

---

## 🔧 使用方法

### 基础用法

```python
from .qwen.skills.import_path_validator import ImportPathValidator

# 验证整个项目
result = ImportPathValidator.validate_project("/path/to/project")
print(result)

# 验证单个文件
issues = ImportPathValidator.validate_file("path/to/module.py")
for issue in issues:
    print(f"问题: {issue['type']} - {issue['message']}")

# 生成报告
report = ImportPathValidator.generate_report(result)
print(report)
```

### 高级用法

```python
from .qwen.skills.import_path_validator import ImportPathValidator

# 自定义配置
config = {
    'exclude_dirs': ['tests', 'migrations', 'venv'],
    'strict_mode': True,  # 严格模式,将所有警告视为错误
}

# 检查重复导入
duplicates = ImportPathValidator.check_duplicate_imports(
    project_root="/path/to/project",
    **config
)

# 检查循环导入
circulars = ImportPathValidator.check_circular_imports(
    project_root="/path/to/project",
    **config
)

# 检查 __init__.py 导出一致性
init_issues = ImportPathValidator.check_init_consistency(
    project_root="/path/to/project",
    **config
)
```

---

## 📊 检测类型说明

### 1. 重复导入 (Duplicate Imports)

**定义**: 同一个类或函数从多个不同的路径导入。

**检测规则**:
- 扫描所有 `from ... import ...` 语句
- 提取导入的符号名称(类名、函数名)
- 如果同一符号从多个不同模块导入,标记为重复导入

**问题评级**:
- 2 个路径: ⚠️ 中 (建议统一)
- 3+ 个路径: 🔴 高 (必须统一)

**示例**:
```python
# 文件 A
from service.translator import TranslationService

# 文件 B
from application.services.translation import TranslationService

# 文件 C
from domain.services.translation_service import TranslationService
```
这三处导入的 `TranslationService` 可能是同一个类,需要确认是否重复。

### 2. 循环导入 (Circular Imports)

**定义**: 模块 A 导入模块 B,模块 B 又导入模块 A,形成循环。

**检测规则**:
- 构建模块依赖图
- 使用深度优先搜索(DFS)检测循环
- 记录循环路径上的所有模块

**问题评级**:
- 2 个模块循环: ⚠️ 中 (建议解耦)
- 3+ 个模块循环: 🔴 高 (必须解耦)

**示例**:
```python
# module_a.py
from module_b import ClassB

# module_b.py
from module_a import ClassA  # 循环依赖!
```

### 3. `__init__.py` 导出一致性 (Init Consistency)

**定义**: `__init__.py` 中导出的符号与实际模块中定义的符号不一致。

**检测规则**:
- 解析 `__init__.py` 中的 `__all__` 列表和导入语句
- 检查导出的符号是否在子模块中实际定义
- 检查子模块中定义的公共符号(非 `_` 开头)是否在 `__init__.py` 中导出

**问题类型**:
- **缺失导出**: 子模块中有公共符号,但未在 `__init__.py` 中导出
- **无效导出**: `__init__.py` 中导出的符号在子模块中不存在
- **导入未导出**: `__init__.py` 中导入但未在 `__all__` 中声明

**示例**:
```python
# package/__init__.py
from .module import ClassA, ClassB
__all__ = ['ClassA']  # ClassB 未导出!

# package/module.py
class ClassA:
    pass

class ClassB:  # 定义了但未在 __all__ 中
    pass

class ClassC:  # 公共类但未导入!
    pass
```

---

## ⚙️ 配置选项

### validate_project() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `project_root` | `str` | 必需 | 项目根目录路径 |
| `exclude_dirs` | `List[str]` | `['.git', '.venv', 'venv', '__pycache__', 'node_modules', 'tests']` | 排除的目录 |
| `exclude_files` | `List[str]` | `['conftest.py', 'setup.py']` | 排除的文件 |
| `strict_mode` | `bool` | `False` | 严格模式(将所有警告视为错误) |
| `check_duplicates` | `bool` | `True` | 是否检查重复导入 |
| `check_circular` | `bool` | `True` | 是否检查循环导入 |
| `check_init` | `bool` | `True` | 是否检查 `__init__.py` 一致性 |

### validate_file() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `file_path` | `str` | 必需 | Python 文件路径 |

### generate_report() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `validation_result` | `Dict` | 必需 | 验证结果字典 |
| `output_format` | `str` | `'text'` | 输出格式: `'text'`, `'json'`, `'markdown'` |
| `output_file` | `Optional[str]` | `None` | 输出文件路径(如提供则保存到文件) |

---

## 📤 输出格式

### 验证结果数据结构

```python
{
    'summary': {
        'total_files': 156,
        'total_imports': 842,
        'total_packages': 28,
        'duplicate_imports': 12,
        'circular_imports': 3,
        'init_inconsistencies': 5,
        'total_issues': 20
    },
    'duplicates': [
        {
            'symbol': 'TranslationService',
            'imports': [
                {
                    'module': 'service.translator',
                    'file': 'presentation/views.py',
                    'line': 10
                },
                {
                    'module': 'application.services.translation',
                    'file': 'presentation/api.py',
                    'line': 15
                }
            ],
            'path_count': 2,
            'severity': 'medium',
            'suggestion': '建议统一使用 service.translator 路径导入'
        }
    ],
    'circular': [
        {
            'cycle': ['module_a', 'module_b', 'module_a'],
            'files': [
                'path/to/module_a.py',
                'path/to/module_b.py'
            ],
            'cycle_length': 2,
            'severity': 'medium',
            'suggestion': '考虑使用依赖注入或接口抽象打破循环'
        }
    ],
    'init_issues': [
        {
            'file': 'package/__init__.py',
            'issue_type': 'missing_export',
            'symbol': 'ClassC',
            'defined_in': 'package/module.py',
            'severity': 'low',
            'suggestion': '在 __all__ 中添加 ClassC,或明确标记为私有'
        }
    ]
}
```

### 文本报告示例

```
═══════════════════════════════════════════════════════
导入路径验证报告
生成时间: 2026-04-03 15:30:45
═══════════════════════════════════════════════════════

【统计摘要】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• 扫描文件总数: 156
• 导入语句总数: 842
• 包(__init__.py)数量: 28
• 重复导入: 12 处
• 循环导入: 3 处
• __init__.py 不一致: 5 处
• 问题总数: 20 个

【重复导入】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. TranslationService (2 个导入路径)
   - service.translator (presentation/views.py:10)
   - application.services.translation (presentation/api.py:15)
   建议: 建议统一使用 service.translator 路径导入

2. UserService (3 个导入路径) 🔴
   - service.user (presentation/views.py:12)
   - application.services.user (application/controllers.py:8)
   - domain.services.user (domain/models.py:5)
   建议: 多个导入路径,请确认是否为同一个类并统一路径

【循环导入】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. module_a ↔ module_b (2 个模块)
   循环路径: module_a → module_b → module_a
   文件:
     - path/to/module_a.py
     - path/to/module_b.py
   建议: 考虑使用依赖注入或接口抽象打破循环

【__init__.py 导出问题】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. package/__init__.py - 缺失导出
   符号: ClassC
   定义位置: package/module.py
   建议: 在 __all__ 中添加 ClassC,或明确标记为私有

═══════════════════════════════════════════════════════
```

---

## 💡 示例

### 示例 1: 验证单个文件

```python
from .qwen.skills.import_path_validator import ImportPathValidator

# 验证文件
issues = ImportPathValidator.validate_file("service/translator.py")

for issue in issues:
    print(f"[{issue['severity']}] {issue['type']}: {issue['message']}")
```

### 示例 2: 验证整个项目并导出报告

```python
from .qwen.skills.import_path_validator import ImportPathValidator

# 验证项目
result = ImportPathValidator.validate_project(
    project_root="/path/to/project",
    exclude_dirs=['tests', 'venv']
)

# 生成 Markdown 报告
report = ImportPathValidator.generate_report(
    result,
    output_format='markdown',
    output_file='docs/import_validation_report.md'
)
```

### 示例 3: 只检查特定类型问题

```python
from .qwen.skills.import_path_validator import ImportPathValidator

# 只检查循环导入
circulars = ImportPathValidator.check_circular_imports(".")

if circulars:
    print("⚠️ 发现循环导入:")
    for cycle in circulars:
        print(f"  {' → '.join(cycle['cycle'])}")
else:
    print("✅ 无循环导入")

# 只检查重复导入
duplicates = ImportPathValidator.check_duplicate_imports(".")

if duplicates:
    print("⚠️ 发现重复导入:")
    for dup in duplicates:
        print(f"  {dup['symbol']}: {dup['path_count']} 个路径")
```

### 示例 4: 严格模式

```python
from .qwen.skills.import_path_validator import ImportPathValidator

# 严格模式(所有问题都视为错误)
result = ImportPathValidator.validate_project(
    project_root="/path/to/project",
    strict_mode=True
)

if result['summary']['total_issues'] > 0:
    print(f"❌ 发现 {result['summary']['total_issues']} 个导入路径问题")
    # 生成详细报告
    report = ImportPathValidator.generate_report(result)
    print(report)
else:
    print("✅ 导入路径检查通过")
```

### 示例 5: 检查 __init__.py 一致性

```python
from .qwen.skills.import_path_validator import ImportPathValidator

# 检查所有 __init__.py 文件
init_issues = ImportPathValidator.check_init_consistency(".")

for issue in init_issues:
    print(f"[{issue['issue_type']}] {issue['file']}: {issue['symbol']}")
    print(f"  建议: {issue['suggestion']}")
```

---

## 🔍 算法说明

### 重复导入检测

1. **AST 解析**: 使用 Python `ast` 模块解析所有 Python 文件
2. **导入提取**: 提取所有 `from ... import ...` 语句中的符号
3. **符号映射**: 构建 符号 → [导入位置] 的映射关系
4. **重复检测**: 找出被从多个不同模块导入的符号
5. **路径规范化**: 尝试规范化模块路径,确认真正的重复导入

### 循环导入检测

1. **依赖图构建**: 扫描所有文件,构建模块依赖图(邻接表)
2. **DFS 遍历**: 使用深度优先搜索遍历依赖图
3. **循环检测**: 在 DFS 过程中检测回边(back edge),识别循环
4. **循环记录**: 记录所有检测到的循环路径

### `__init__.py` 一致性检查

1. **`__all__` 解析**: 提取 `__init__.py` 中的 `__all__` 列表
2. **导入语句解析**: 提取 `__init__.py` 中的所有导入
3. **子模块扫描**: 扫描子模块中定义的公共符号(非 `_` 开头的类/函数)
4. **一致性对比**:
   - 检查 `__all__` 中的符号是否在子模块中定义
   - 检查子模块中的公共符号是否在 `__all__` 中声明
5. **问题分类**: 将问题分为"缺失导出"、"无效导出"、"导入未导出"

---

## ⚠️ 注意事项

### 误报处理

验证器可能产生误报,以下情况属于正常现象:

- **别名导入**: 使用 `as` 关键字的别名导入可能是有意为之
- **重导出**: 某些模块专门用于重导出其他模块的符号
- **测试代码**: 测试文件可能需要从多个路径导入同一类
- **兼容性代码**: 为保持向后兼容,可能保留旧的导入路径

### 符号歧义

- **同名类/函数**: 不同模块可能定义同名但不同的类/函数
- **验证器会尝试通过模块路径和上下文判断是否真正重复**
- **建议人工审查重复导入报告**

### 性能建议

- **大型项目**: 对于超过 1000 个 Python 文件的项目,建议分模块扫描
- **CI/CD 集成**: 设置合理的规则,避免过多误报
- **增量检查**: 定期分析时,可只检查变更过的文件

### 最佳实践

1. **统一导入路径**: 项目中同一类/函数应只从一个标准路径导入
2. **避免循环依赖**: 使用依赖注入或接口抽象打破循环
3. **维护 `__init__.py`**: 保持包导出与实际实现一致
4. **定期验证**: 建议每周或每次重大重构后运行
5. **结合审查**: 验证结果应结合人工代码审查使用

---

## 📈 质量指标

### 验证器自检测试

运行以下命令验证验证器功能:

```python
from .qwen.skills.import_path_validator import ImportPathValidator

# 自检测试
test_result = ImportPathValidator.self_test()
print(f"自检测试: {'✅ 通过' if test_result else '❌ 失败'}")
```

### 性能基准

| 项目规模 | 验证时间(估计) | 内存占用 |
|---------|--------------|---------|
| < 100 文件 | < 3 秒 | < 50 MB |
| 100-500 文件 | 3-15 秒 | 50-150 MB |
| 500-1000 文件 | 15-40 秒 | 150-300 MB |
| > 1000 文件 | 40+ 秒 | 300+ MB |

---

## 🔄 CI/CD 集成示例

### GitHub Actions

```yaml
name: Import Path Validation
on: [push, pull_request]

jobs:
  check-imports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Check Import Paths
        run: |
          python -c "
          from .qwen.skills.import_path_validator import ImportPathValidator
          import sys

          result = ImportPathValidator.validate_project('.')
          report = ImportPathValidator.generate_report(result)
          print(report)

          # 如果有问题,退出并报错
          if result['summary']['total_issues'] > 0:
              print('❌ 发现导入路径问题,请修复后再合入')
              sys.exit(1)
          "
```

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
python -c "
from .qwen.skills.import_path_validator import ImportPathValidator
import sys

result = ImportPathValidator.validate_project('.')
if result['summary']['total_issues'] > 0:
    print('⚠️ 发现导入路径问题,请审查后再提交')
    print(f\"  重复导入: {result['summary']['duplicate_imports']}\")
    print(f\"  循环导入: {result['summary']['circular_imports']}\")
    print(f\"  __init__.py 不一致: {result['summary']['init_inconsistencies']}\")
    sys.exit(1)
"
```

### Makefile 集成

```makefile
.PHONY: check-imports

check-imports:
	@echo "运行导入路径验证..."
	@python -c "\
	from .qwen.skills.import_path_validator import ImportPathValidator; \
	result = ImportPathValidator.validate_project('.'); \
	report = ImportPathValidator.generate_report(result); \
	print(report); \
	exit(1 if result['summary']['total_issues'] > 0 else 0)"
```

---

## 📚 相关文件

- `validator.py`: 核心实现代码
- `__init__.py`: 模块初始化文件
- `SKILL.md`: 本文档

---

**Skill 版本**: 1.0.0
**生效日期**: 2026-04-03
**下次审查**: 2026-05-03
