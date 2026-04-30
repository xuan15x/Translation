---
name: arch-dependency-checker
description: >
  验证 Python 项目的分层架构依赖规则，检测违反架构规范的导入关系。
  适用于六层架构（presentation/application/domain/service/data_access/infrastructure）的项目。
  当需要检查架构一致性、识别违规依赖、生成架构报告时使用。
  触发关键字：架构检查、依赖检查、架构验证、分层架构、六层架构、违规依赖。
---

# 架构依赖检查器 (Arch Dependency Checker)

**版本**: 1.0.0
**创建日期**: 2026-04-03
**适用范围**: 六层架构 Python 项目
**触发方式**: 手动调用或 CI/CD 集成

---

## 📋 概述

架构依赖检查器是一个自动化工具，用于验证项目的分层架构依赖规则。它能够检测违反架构规范的导入关系，确保代码库保持清晰的层次结构和良好的依赖方向。

### 核心功能

- 🏗️ **架构规则验证**: 检查各层之间的导入依赖是否符合架构规范
- 📊 **违规报告生成**: 生成详细的违规清单，支持多种输出格式
- 🔍 **文件和项目级扫描**: 支持单文件检查和全项目扫描
- 🚫 **误报过滤**: 智能识别标准库和第三方库导入，避免误报

---

## 🎯 架构规则说明

本项目采用**六层架构**，各层职责和依赖规则如下：

### 架构层次（从高层到低层）

| 层次 | 目录 | 职责 | 依赖规则 |
|------|------|------|----------|
| **表示层** | `presentation/` | 用户界面和交互 | 应主要通过 application 层访问 |
| **应用层** | `application/` | 流程编排和业务协调 | 可访问 domain 和 service 层 |
| **领域层** | `domain/` | 纯业务逻辑，无外部依赖 | ❌ 不应访问 infrastructure、service、data_access |
| **服务层** | `service/` | API 集成和外部服务 | 可访问 domain 和 infrastructure |
| **数据访问层** | `data_access/` | 仓储模式和持久化 | 可访问 domain，❌ 不应访问 service |
| **基础设施层** | `infrastructure/` | 通用工具和基础服务 | ❌ 不应访问 domain 的业务逻辑（仅支持基础工具） |

### 依赖方向原则

```
presentation → application → domain ← service → infrastructure
                           ↓
                      data_access
```

**核心规则**:
1. **依赖倒置**: 高层模块不应依赖低层模块，都应依赖抽象
2. **单向依赖**: 依赖关系应单向，避免循环依赖
3. **领域纯净**: 领域层应保持纯净，不依赖任何外部实现
4. **基础设施隔离**: 基础设施层仅提供通用工具，不应包含业务逻辑

### 详细规则矩阵

| 源层 \ 目标层 | presentation | application | domain | service | data_access | infrastructure |
|--------------|--------------|-------------|--------|---------|-------------|----------------|
| **presentation** | ✅ | ⚠️ 应避免 | ✅ 通过 app | ✅ 通过 app | ⚠️ 应避免 | ✅ |
| **application** | ❌ | ✅ | ✅ | ✅ | ✅ 通过 domain | ✅ |
| **domain** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **service** | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| **data_access** | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **infrastructure** | ❌ | ❌ | ⚠️ 仅模型 | ❌ | ❌ | ✅ |

**符号说明**:
- ✅ 允许
- ❌ 禁止
- ⚠️ 有条件允许（需特殊说明）

---

## 🔧 使用方法

### 基础用法

```python
from .qwen.skills.arch_dependency_checker import ArchDependencyChecker

# 检查整个项目
result = ArchDependencyChecker.check_project("/path/to/project")
print(f"发现 {len(result['violations'])} 个违规")

# 检查单个文件
violations = ArchDependencyChecker.check_file("/path/to/file.py")
for v in violations:
    print(f"违规: {v['source_layer']} -> {v['target_layer']}")

# 生成报告
report = ArchDependencyChecker.generate_report(
    result['violations'],
    output_format='markdown'
)
print(report)
```

### 高级用法

```python
from .qwen.skills.arch_dependency_checker import ArchDependencyChecker

# 自定义架构规则
custom_rules = {
    'domain': {
        'can_import': ['domain', 'infrastructure.models'],  # 允许访问模型
        'cannot_import': ['infrastructure', 'service', 'data_access', 'presentation']
    }
}

# 使用自定义规则检查
result = ArchDependencyChecker.check_project(
    project_root="/path/to/project",
    custom_rules=custom_rules
)

# 排除特定目录
result = ArchDependencyChecker.check_project(
    project_root="/path/to/project",
    exclude_dirs=['tests', 'scripts', '.qwen']
)

# 生成 JSON 报告并保存
report_json = ArchDependencyChecker.generate_report(
    result['violations'],
    output_format='json',
    output_file='docs/architecture_violations.json'
)
```

---

## ⚙️ 配置选项

### check_project() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `project_root` | `str` | 必需 | 项目根目录路径 |
| `custom_rules` | `Optional[Dict]` | `None` | 自定义架构规则（覆盖默认规则） |
| `exclude_dirs` | `Optional[List[str]]` | `['.git', '.venv', 'venv', '__pycache__', 'tests', '.qwen']` | 排除的目录 |
| `exclude_files` | `Optional[List[str]]` | `['__init__.py', 'conftest.py']` | 排除的文件 |
| `strict_mode` | `bool` | `False` | 严格模式（将 ⚠️ 规则视为 ❌） |

### check_file() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `file_path` | `str` | 必需 | 文件路径 |
| `project_root` | `str` | 必需 | 项目根目录（用于确定文件所属层） |
| `custom_rules` | `Optional[Dict]` | `None` | 自定义架构规则 |

### generate_report() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `violations` | `List[Dict]` | 必需 | 违规清单 |
| `output_format` | `str` | `'text'` | 输出格式：`'text'`, `'json'`, `'markdown'` |
| `output_file` | `Optional[str]` | `None` | 输出文件路径（如提供则保存到文件） |
| `include_suggestions` | `bool` | `True` | 是否包含修复建议 |

---

## 📊 输出格式

### 违规数据结构

```python
{
    'source_file': 'domain/services.py',
    'source_layer': 'domain',
    'target_file': 'infrastructure/cache.py',
    'target_layer': 'infrastructure',
    'import_statement': 'from infrastructure.cache import CacheManager',
    'line_number': 15,
    'rule_violated': 'domain 层不应导入 infrastructure 层',
    'severity': 'high',  # 'high', 'medium', 'low'
    'suggestion': '考虑使用依赖注入或接口抽象'
}
```

### 检查结果结构

```python
{
    'violations': [...],  # 违规清单
    'summary': {
        'total_files_scanned': 156,
        'total_violations': 12,
        'violations_by_layer': {
            'domain': 5,
            'data_access': 3,
            'infrastructure': 4
        },
        'violations_by_severity': {
            'high': 8,
            'medium': 3,
            'low': 1
        }
    },
    'metadata': {
        'project_root': '/path/to/project',
        'scan_time': '2026-04-03T15:30:45',
        'rules_version': '1.0.0'
    }
}
```

### 文本报告示例

```
═══════════════════════════════════════════════════════
架构依赖检查报告
生成时间: 2026-04-03 15:30:45
═══════════════════════════════════════════════════════

【违规清单】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [严重] domain/services.py → infrastructure/cache.py
   行号: 15
   导入: from infrastructure.cache import CacheManager
   规则: domain 层不应导入 infrastructure 层
   建议: 考虑使用依赖注入或接口抽象

2. [中等] data_access/repositories.py → service/api_provider.py
   行号: 42
   导入: from service.api_provider import APIProviderManager
   规则: data_access 层不应导入 service 层
   建议: 通过领域服务接口访问数据

【统计摘要】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• 扫描文件总数: 156
• 发现违规: 12 个
  - domain 层: 5 个违规
  - data_access 层: 3 个违规
  - infrastructure 层: 4 个违规
• 严重程度:
  - 高: 8 个
  - 中: 3 个
  - 低: 1 个

═══════════════════════════════════════════════════════
```

---

## 💡 示例

### 示例 1: 检查当前项目

```python
from .qwen.skills.arch_dependency_checker import ArchDependencyChecker
import os

# 获取项目根目录
project_root = os.getcwd()

# 执行检查
result = ArchDependencyChecker.check_project(project_root)

# 生成并打印报告
report = ArchDependencyChecker.generate_report(result['violations'])
print(report)
```

### 示例 2: 严格模式检查

```python
from .qwen.skills.arch_dependency_checker import ArchDependencyChecker

# 使用严格模式（将所有警告视为错误）
result = ArchDependencyChecker.check_project(
    project_root="/path/to/project",
    strict_mode=True
)

if result['violations']:
    print("❌ 架构检查失败")
    for v in result['violations']:
        print(f"  - {v['source_file']} -> {v['target_layer']}")
else:
    print("✅ 架构检查通过")
```

### 示例 3: 导出 JSON 报告

```python
import json
from .qwen.skills.arch_dependency_checker import ArchDependencyChecker

# 检查项目
result = ArchDependencyChecker.check_project("/path/to/project")

# 生成 JSON 报告
report_json = ArchDependencyChecker.generate_report(
    result['violations'],
    output_format='json'
)

# 解析和使用
data = json.loads(report_json)
print(f"发现 {data['summary']['total_violations']} 个违规")

# 按严重程度过滤
high_severity = [v for v in data['violations'] if v['severity'] == 'high']
print(f"高严重程度违规: {len(high_severity)}")
```

### 示例 4: 自定义规则

```python
from .qwen.skills.arch_dependency_checker import ArchDependencyChecker

# 自定义规则：允许 domain 层访问 infrastructure.models
custom_rules = {
    'domain': {
        'can_import': ['domain', 'infrastructure.models'],
        'cannot_import': ['infrastructure', 'service', 'data_access', 'presentation']
    },
    'presentation': {
        'can_import': ['presentation', 'application', 'infrastructure'],
        'cannot_import': ['domain', 'service', 'data_access']
    }
}

result = ArchDependencyChecker.check_project(
    project_root="/path/to/project",
    custom_rules=custom_rules
)
```

### 示例 5: 只检查特定层

```python
from .qwen.skills.arch_dependency_checker import ArchDependencyChecker

# 只检查 domain 层的违规
result = ArchDependencyChecker.check_project("/path/to/project")
domain_violations = [
    v for v in result['violations']
    if v['source_layer'] == 'domain'
]

report = ArchDependencyChecker.generate_report(domain_violations)
print(report)
```

---

## 🔍 算法说明

### 导入解析

1. **AST 解析**: 使用 Python `ast` 模块解析所有 Python 文件
2. **导入提取**: 提取 `import` 和 `from ... import ...` 语句
3. **模块解析**: 将导入语句解析为目标模块路径
4. **行号记录**: 记录每个导入语句的行号

### 层次判定

1. **文件路径分析**: 根据文件相对于项目根的路径确定所属层
2. **模块映射**: 将导入的模块路径映射到对应的层
3. **相对导入处理**: 处理相对导入（`from . import xxx`）

### 规则检查

1. **规则匹配**: 根据源文件的层和目标模块的层，查找对应的规则
2. **违规判定**: 判断导入是否在允许列表中
3. **严重性评估**: 根据违规类型评估严重程度
   - **high**: domain 层违规访问其他层
   - **medium**: data_access 访问 service，infrastructure 访问 domain 业务逻辑
   - **low**: presentation 直接访问低层（应通过 application）

### 修复建议生成

根据违规类型自动生成针对性的修复建议：
- 依赖注入模式推荐
- 接口抽象建议
- 层次重构指导

---

## ⚠️ 注意事项

### 误报处理

检查器可能产生误报，以下情况需要特别处理：

- **测试文件**: 测试代码可能需要访问多个层，建议排除测试目录
- **启动脚本**: 项目入口文件（如 `main.py`）可能需要跨层访问
- **配置模块**: 配置加载器可能需要访问多个层
- **工具脚本**: `scripts/` 目录中的工具脚本不受架构约束

### 特殊例外

某些情况下可以允许例外：

1. **领域模型依赖**: domain 层可以访问 `infrastructure.models`（如果模型定义在那里）
2. **工具类导入**: 各层都可以导入纯工具类（如日志、异常定义）
3. **接口定义**: 接口和抽象类可以跨层定义

### 性能建议

- **大型项目**: 对于超过 500 个 Python 文件的项目，建议分模块检查
- **CI/CD 集成**: 设置增量检查，只检查变更的文件
- **缓存结果**: 定期扫描时，可缓存未变更文件的结果

### 最佳实践

1. **早期集成**: 在项目初期就集成架构检查
2. **持续改进**: 根据检查结果逐步重构违规代码
3. **团队共识**: 确保团队理解并遵守架构规则
4. **规则演进**: 随着项目发展，适时调整架构规则

---

## 📈 质量指标

### 检查器自检测试

运行以下命令验证检查器功能：

```python
from .qwen.skills.arch_dependency_checker import ArchDependencyChecker

# 自检测试
test_result = ArchDependencyChecker.self_test()
print(f"自检测试: {'✅ 通过' if test_result else '❌ 失败'}")
```

### 性能基准

| 项目规模 | 扫描时间（估计） | 内存占用 |
|---------|----------------|---------|
| < 100 文件 | < 2 秒 | < 50 MB |
| 100-500 文件 | 2-10 秒 | 50-150 MB |
| > 500 文件 | 10-30 秒 | 150-300 MB |

---

## 🔄 CI/CD 集成示例

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
python -c "
from .qwen.skills.arch_dependency_checker import ArchDependencyChecker
import sys

result = ArchDependencyChecker.check_project('.')
if result['violations']:
    print('⚠️ 发现架构违规，请审查后再提交')
    for v in result['violations']:
        print(f\"  - {v['source_file']} -> {v['target_layer']}\")
    sys.exit(1)
"
```

### GitHub Actions

```yaml
name: Architecture Check
on: [push, pull_request]

jobs:
  check-architecture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Check Architecture
        run: |
          python -c "
          from .qwen.skills.arch_dependency_checker import ArchDependencyChecker
          result = ArchDependencyChecker.check_project('.')
          report = ArchDependencyChecker.generate_report(
              result['violations'],
              output_format='markdown'
          )
          print(report)
          
          if result['violations']:
              exit(1)
          "
```

### Makefile 集成

```makefile
.PHONY: check-arch

check-arch:
	@echo "运行架构依赖检查..."
	@python -c "\
	from .qwen.skills.arch_dependency_checker import ArchDependencyChecker; \
	result = ArchDependencyChecker.check_project('.'); \
	report = ArchDependencyChecker.generate_report(result['violations']); \
	print(report); \
	exit(1 if result['violations'] else 0)"
```

---

## 📚 相关文件

- `checker.py`: 核心实现代码
- `__init__.py`: 模块初始化文件
- `SKILL.md`: 本文档

---

**Skill 版本**: 1.0.0
**生效日期**: 2026-04-03
**下次审查**: 2026-05-03
