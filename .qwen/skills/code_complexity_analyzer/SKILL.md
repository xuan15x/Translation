---
name: code-complexity-analyzer
description: >
  分析 Python 项目的代码复杂度，包括圈复杂度、认知复杂度、函数/类大小等指标。
  帮助识别高复杂度代码，提升代码可维护性和可读性。
  当需要代码审查、重构指导、质量门禁、技术债务评估、代码规范检查时使用。
  触发关键字：复杂度分析、复杂度检查、代码质量、圈复杂度、认知复杂度、重构建议。
---

# 代码复杂度分析器 (Code Complexity Analyzer)

**版本**: 1.0.0
**创建日期**: 2026-04-03
**适用范围**: 所有 Python 项目
**触发方式**: 手动调用或 CI/CD 集成

---

## 📋 概述

代码复杂度分析器是一个自动化工具,用于分析 Python 项目的代码复杂度,包括圈复杂度、认知复杂度、函数/类大小等指标。它帮助开发者识别高复杂度代码,提升代码可维护性和可读性。

### 核心功能

- 🔢 **圈复杂度分析**: 计算函数的圈复杂度(Cyclomatic Complexity)
- 🧠 **认知复杂度分析**: 评估代码的认知复杂度(Cognitive Complexity)
- 📏 **函数/类大小检测**: 统计函数和类的代码行数
- 📊 **项目级分析**: 扫描整个项目,生成汇总报告
- 📝 **多格式报告**: 支持 text、json、markdown 三种输出格式

---

## 🎯 使用场景

### 1. 代码审查
在代码审查前运行分析器,快速识别高复杂度的函数和类,重点关注需要重构的代码。

### 2. 重构指导
分析现有代码库,找出复杂度超标的代码段,作为重构的优先级参考。

### 3. 质量门禁
集成到 CI/CD 流程中,设置复杂度阈值,阻止高复杂度代码合入主分支。

### 4. 技术债务评估
定期扫描项目,评估代码复杂度趋势,跟踪技术债务的变化。

### 5. 代码规范检查
作为代码规范的一部分,确保新代码符合复杂度标准。

---

## 🔧 使用方法

### 基础用法

```python
from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer

# 分析单个文件
result = CodeComplexityAnalyzer.analyze_file("path/to/module.py")
print(result)

# 分析整个项目
project_result = CodeComplexityAnalyzer.analyze_project("/path/to/project")

# 生成报告
report = CodeComplexityAnalyzer.generate_report(project_result)
print(report)
```

### 高级用法

```python
from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer

# 自定义配置
config = {
    'exclude_dirs': ['tests', 'migrations', 'venv'],
    'cyclomatic_threshold': 10,      # 圈复杂度警告阈值
    'cognitive_threshold': 15,       # 认知复杂度警告阈值
    'max_function_lines': 50,        # 函数最大行数
    'max_class_lines': 300           # 类最大行数
}

# 分析项目并应用配置
result = CodeComplexityAnalyzer.analyze_project(
    project_root="/path/to/project",
    **config
)

# 导出为 JSON 格式报告
report_json = CodeComplexityAnalyzer.generate_report(
    result,
    output_format='json'
)
```

---

## 📊 支持的复杂度指标

### 1. 圈复杂度 (Cyclomatic Complexity)

**定义**: 衡量代码中独立路径的数量,通过控制流语句的数量计算。

**计算规则**:
- 基础复杂度: 1
- 每个 `if`/`elif`: +1
- 每个 `for`/`while`: +1
- 每个 `except`: +1
- 每个 `with`: +1
- 每个 `assert`: +1
- 布尔运算符 `and`/`or`: +1
- 三元表达式: +1

**复杂度评级**:
- 1-5: ✅ 低 (优秀)
- 6-10: ⚠️ 中 (可接受)
- 11-20: 🔴 高 (建议重构)
- 21+: 🚨 极高 (必须重构)

### 2. 认知复杂度 (Cognitive Complexity)

**定义**: 衡量代码理解难度,考虑控制流的嵌套层级。

**计算规则**:
- 每个控制流语句(if/for/while/try等): +1
- 嵌套层级递增: 每增加一层嵌套 +1
- 布尔运算符序列: 每个 +1
- 递归调用: +1

**复杂度评级**:
- 1-5: ✅ 低 (易于理解)
- 6-15: ⚠️ 中 (需要关注)
- 16-30: 🔴 高 (难以理解)
- 31+: 🚨 极高 (必须简化)

### 3. 函数大小

**定义**: 函数的代码行数(不包含空行和注释)。

**评级标准**:
- 1-20 行: ✅ 优秀
- 21-50 行: ⚠️ 可接受
- 51-100 行: 🔴 建议拆分
- 100+ 行: 🚨 必须重构

### 4. 类大小

**定义**: 类的总代码行数和包含的方法数量。

**评级标准**:
- 1-100 行: ✅ 优秀
- 101-300 行: ⚠️ 可接受
- 301-500 行: 🔴 建议拆分
- 500+ 行: 🚨 必须重构

---

## ⚙️ 配置选项

### analyze_file() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `file_path` | `str` | 必需 | Python 文件路径 |

### analyze_project() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `project_root` | `str` | 必需 | 项目根目录路径 |
| `exclude_dirs` | `List[str]` | `['.git', '.venv', 'venv', '__pycache__', 'node_modules']` | 排除的目录 |
| `exclude_files` | `List[str]` | `['__init__.py']` | 排除的文件 |
| `cyclomatic_threshold` | `int` | `10` | 圈复杂度警告阈值 |
| `cognitive_threshold` | `int` | `15` | 认知复杂度警告阈值 |
| `max_function_lines` | `int` | `50` | 函数最大行数 |
| `max_class_lines` | `int` | `300` | 类最大行数 |

### generate_report() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `analysis_result` | `Dict` | 必需 | 分析结果字典 |
| `output_format` | `str` | `'text'` | 输出格式: `'text'`, `'json'`, `'markdown'` |
| `output_file` | `Optional[str]` | `None` | 输出文件路径(如提供则保存到文件) |

---

## 📤 输出格式

### 分析结果数据结构

```python
{
    'summary': {
        'total_files': 156,
        'total_functions': 423,
        'total_classes': 85,
        'avg_cyclomatic_complexity': 4.2,
        'avg_cognitive_complexity': 6.8,
        'high_complexity_count': 12
    },
    'files': [
        {
            'file': 'path/to/module.py',
            'functions': [
                {
                    'name': 'process_data',
                    'line': 15,
                    'lines_count': 45,
                    'cyclomatic_complexity': 12,
                    'cognitive_complexity': 18,
                    'complexity_level': 'HIGH'
                }
            ],
            'classes': [
                {
                    'name': 'DataProcessor',
                    'line': 10,
                    'lines_count': 280,
                    'method_count': 15,
                    'complexity_level': 'MEDIUM'
                }
            ],
            'file_stats': {
                'total_lines': 450,
                'function_count': 8,
                'class_count': 2,
                'max_complexity': 18
            }
        }
    ],
    'high_complexity_items': [
        {
            'type': 'function',
            'name': 'process_data',
            'file': 'path/to/module.py',
            'cyclomatic_complexity': 12,
            'cognitive_complexity': 18,
            'recommendation': '建议拆分函数,降低嵌套层级'
        }
    ]
}
```

### 文本报告示例

```
═══════════════════════════════════════════════════════
代码复杂度分析报告
生成时间: 2026-04-03 15:30:45
═══════════════════════════════════════════════════════

【统计摘要】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• 扫描文件总数: 156
• 函数总数: 423
• 类总数: 85
• 平均圈复杂度: 4.2
• 平均认知复杂度: 6.8
• 高复杂度代码: 12 处

【高复杂度代码】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 函数: process_data (path/to/module.py:15)
   圈复杂度: 12 (高) | 认知复杂度: 18 (高)
   代码行数: 45
   建议: 建议拆分函数,降低嵌套层级

2. 类: DataProcessor (path/to/module.py:10)
   代码行数: 280 | 方法数: 15
   复杂度等级: 中

【文件详情】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

path/to/module.py
  • 总行数: 450 | 函数数: 8 | 类数: 2
  • 最高复杂度: 18
  
  函数列表:
    - process_data (15): CC=12, CogC=18, 45行 ⚠️
    - validate_input (120): CC=5, CogC=6, 20行 ✅
    ...

═══════════════════════════════════════════════════════
```

---

## 💡 示例

### 示例 1: 分析单个文件

```python
from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer

# 分析文件
result = CodeComplexityAnalyzer.analyze_file("service/translator.py")

# 打印函数复杂度
for func in result['functions']:
    print(f"{func['name']}: CC={func['cyclomatic_complexity']}, "
          f"CogC={func['cognitive_complexity']}, "
          f"Lines={func['lines_count']}")
```

### 示例 2: 分析整个项目并导出报告

```python
from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer

# 分析项目
result = CodeComplexityAnalyzer.analyze_project(
    project_root="/path/to/project",
    exclude_dirs=['tests', 'venv']
)

# 生成 Markdown 报告
report = CodeComplexityAnalyzer.generate_report(
    result,
    output_format='markdown',
    output_file='docs/complexity_report.md'
)
```

### 示例 3: 检查是否超过阈值

```python
from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer

result = CodeComplexityAnalyzer.analyze_project(".")

# 检查是否有高复杂度代码
if result['high_complexity_items']:
    print("⚠️ 发现高复杂度代码:")
    for item in result['high_complexity_items']:
        print(f"  - {item['type']}: {item['name']} "
              f"(CC={item['cyclomatic_complexity']}, "
              f"CogC={item['cognitive_complexity']})")
else:
    print("✅ 所有代码复杂度都在可接受范围内")
```

### 示例 4: 自定义阈值

```python
from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer

# 设置更严格的阈值
result = CodeComplexityAnalyzer.analyze_project(
    project_root="/path/to/project",
    cyclomatic_threshold=8,      # 降低圈复杂度阈值
    cognitive_threshold=12,      # 降低认知复杂度阈值
    max_function_lines=40,       # 降低函数行数限制
    max_class_lines=250          # 降低类行数限制
)

# 生成报告
report = CodeComplexityAnalyzer.generate_report(result)
print(report)
```

---

## 🔍 算法说明

### 圈复杂度计算

1. **AST 解析**: 使用 Python `ast` 模块解析代码
2. **控制流计数**: 遍历 AST,统计控制流语句数量
3. **基础复杂度**: 从 1 开始,每遇到一个控制流语句 +1
4. **布尔运算符**: `and`/`or` 运算符也计入复杂度

### 认知复杂度计算

1. **嵌套层级追踪**: 记录每个控制流语句的嵌套深度
2. **增量计算**: 
   - 控制流语句基础分: +1
   - 嵌套层级加分: 每层 +1
   - 布尔运算符序列: 每个 +1
3. **递归检测**: 识别递归调用并加分

### 函数/类大小计算

1. **行号范围**: 通过 AST 节点的 `lineno` 和 `end_lineno` 确定范围
2. **有效行数**: 排除空行和纯注释行
3. **方法计数**: 统计类中定义的方法数量

---

## ⚠️ 注意事项

### 误报处理

分析器可能产生误报,以下情况属于正常现象:

- **复杂业务逻辑**: 某些业务规则天然复杂,难以简化
- **性能优化代码**: 为性能优化的代码可能增加复杂度
- **自动生成代码**: 代码生成器产生的文件可能复杂度高

### 性能建议

- **大型项目**: 对于超过 1000 个 Python 文件的项目,建议分模块扫描
- **CI/CD 集成**: 设置合理的阈值,避免过多误报
- **增量分析**: 定期分析时,可只分析变更过的文件

### 最佳实践

1. **定期分析**: 建议每周或每次重大重构后运行
2. **设定基线**: 首次分析后记录基线数据,后续对比改进
3. **结合审查**: 分析结果应结合人工代码审查使用
4. **持续改进**: 根据分析结果制定代码简化计划
5. **渐进式重构**: 优先处理复杂度最高的代码

---

## 📈 质量指标

### 分析器自检测试

运行以下命令验证分析器功能:

```python
from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer

# 自检测试
test_result = CodeComplexityAnalyzer.self_test()
print(f"自检测试: {'✅ 通过' if test_result else '❌ 失败'}")
```

### 性能基准

| 项目规模 | 分析时间(估计) | 内存占用 |
|---------|--------------|---------|
| < 100 文件 | < 2 秒 | < 50 MB |
| 100-500 文件 | 2-10 秒 | 50-150 MB |
| 500-1000 文件 | 10-30 秒 | 150-300 MB |
| > 1000 文件 | 30+ 秒 | 300+ MB |

---

## 🔄 CI/CD 集成示例

### GitHub Actions

```yaml
name: Code Complexity Check
on: [push, pull_request]

jobs:
  check-complexity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Check Code Complexity
        run: |
          python -c "
          from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer
          import sys
          
          result = CodeComplexityAnalyzer.analyze_project('.')
          report = CodeComplexityAnalyzer.generate_report(result)
          print(report)
          
          # 如果有高复杂度代码,退出并报错
          if result['high_complexity_items']:
              print('❌ 发现高复杂度代码,请重构后再合入')
              sys.exit(1)
          "
```

### GitLab CI

```yaml
code_complexity:
  stage: test
  script:
    - python -c "
      from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer
      import sys
      
      result = CodeComplexityAnalyzer.analyze_project('.')
      
      if result['high_complexity_items']:
          print('⚠️ 高复杂度代码检测报告:')
          for item in result['high_complexity_items']:
              print(f\"  - {item['type']}: {item['name']}\")
          sys.exit(1)
      else:
          print('✅ 代码复杂度检查通过')
      "
  allow_failure: true
```

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
python -c "
from .qwen.skills.code_complexity_analyzer import CodeComplexityAnalyzer
import sys

result = CodeComplexityAnalyzer.analyze_project('.')
if result['high_complexity_items']:
    print('⚠️ 发现高复杂度代码,请审查后再提交')
    for item in result['high_complexity_items'][:5]:
        print(f\"  - {item['type']}: {item['name']} (CC={item['cyclomatic_complexity']})\")
    sys.exit(1)
"
```

---

## 📚 相关文件

- `analyzer.py`: 核心实现代码
- `__init__.py`: 模块初始化文件
- `SKILL.md`: 本文档
- `tests/test_analyzer.py`: 测试用例

---

**Skill 版本**: 1.0.0
**生效日期**: 2026-04-03
**下次审查**: 2026-05-03
