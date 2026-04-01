# 业务逻辑层文档 (已废弃 ⚠️)

## 📋 重要提示

**本模块已在 v3.0 版本中废弃！**

### 迁移指南

| 旧代码 (v2.x) | 新代码 (v3.0+) |
|--------------|---------------|
| `WorkflowOrchestrator` | `TranslationWorkflowCoordinator` (application 层) |
| `TerminologyManager` | `TerminologyDomainService` (domain 层) |
| `business_logic.*` | `application.*` + `domain.*` |

### 为什么废弃？

1. **职责混乱** - business_logic 层承担了过多职责
2. **紧耦合** - 各组件之间依赖复杂
3. **难测试** - 难以进行单元测试
4. **性能差** - 缺少缓存和批量优化

### 新的六层架构

```
Presentation Layer (表示层)
    ↓
Application Layer (应用层) ← 新增的流程编排层
    ↓
Domain Layer (领域层) ← 纯业务逻辑层
    ↓
Service Layer (服务层)
    ↓
Data Access Layer (数据访问层)
    ↓
Infrastructure Layer (基础设施层)
```

---

## 📋 历史概述（仅供参考）

`business_logic/` 模块负责翻译流程编排和术语库管理，是系统的核心业务逻辑层。

## 📁 文件结构

```
business_logic/
├── __init__.py              # 模块导出
├── workflow_orchestrator.py # 工作流编排器
└── terminology_manager.py   # 术语管理器
```

## 🔧 核心类

### 1. WorkflowOrchestrator (工作流编排器)

#### 功能说明

工作流编排器负责协调整个翻译流程，包括:
- 任务分发和执行
- 并发控制
- 进度跟踪
- 结果汇总

#### 使用示例

```python
from translation import WorkflowOrchestrator, Config

config = Config(api_key="your-key")
orchestrator = WorkflowOrchestrator(config=config)

# 执行翻译任务
results = await orchestrator.execute(
    tasks=tasks,
    out_file="result.xlsx"
)
```

#### 主要方法

##### execute(tasks, out_file)

执行翻译任务列表。

**参数**:
- `tasks`: TaskContext 列表
- `out_file`: 输出文件路径

**返回**:
- FinalResult 列表

**示例**:
```python
tasks = [
    TaskContext(idx=0, key="TM_0", source_text="紫钻", target_lang="英语"),
    TaskContext(idx=1, key="TM_1", source_text="蓝钻", target_lang="英语")
]

results = await orchestrator.execute(tasks, "result.xlsx")
```

### 2. TerminologyManager (术语管理器)

#### 功能说明

术语管理器负责术语库的加载、查询和更新:
- 从 Excel 加载术语库
- 模糊匹配查询
- 增量添加术语
- 自动保存和导出

#### 使用示例

```python
from translation import TerminologyManager, Config

config = Config()
tm = TerminologyManager(
    filepath="terminology.xlsx",
    config=config
)

# 查询术语
match = tm.query("紫钻")
if match:
    print(f"英语：{match.get('英语')}")
    print(f"日语：{match.get('日语')}")
```

#### 主要方法

##### query(source_text, fuzzy_threshold=0.6)

查询术语库。

**参数**:
- `source_text`: 源文本
- `fuzzy_threshold`: 模糊匹配阈值 (默认 0.6)

**返回**:
- Dict[str, str]: 匹配的术语字典

**示例**:
```python
# 精确匹配
exact_match = tm.query("紫钻")

# 模糊匹配
fuzzy_match = tm.query("紫色钻石", fuzzy_threshold=0.5)
```

##### add_entry(key, source_text, translations)

添加术语条目。

**参数**:
- `key`: 术语键
- `source_text`: 中文原文
- `translations`: 翻译字典 {语言：译文}

**示例**:
```python
tm.add_entry(
    key="TM_100",
    source_text="紫钻",
    translations={
        "英语": "Purple Diamond",
        "日语": "パープルダイヤモンド",
        "韩语": "퍼플 다이아몬드"
    }
)
```

##### export_to_excel(output_path, export_new_only=False)

导出术语库到 Excel。

**参数**:
- `output_path`: 输出文件路径
- `export_new_only`: 是否只导出新增术语

**返回**:
- str: 输出文件路径

**示例**:
```python
# 导出完整术语库
await tm.export_to_excel("full_terms.xlsx")

# 只导出本次会话新增的术语
await tm.export_to_excel("new_terms.xlsx", export_new_only=True)
```

##### get_history_timeline(days=7)

获取术语库变更历史时间线。

**参数**:
- `days`: 天数 (默认 7 天)

**返回**:
- List[Dict]: 历史记录列表

**示例**:
```python
history = await tm.get_history_timeline(days=30)
for record in history:
    print(f"{record['timestamp']}: {record['change_type']}")
```

##### shutdown()

关闭术语管理器并保存数据。

**示例**:
```python
await tm.shutdown()
```

## 📖 完整使用示例

### 1. 基本翻译流程

```python
import asyncio
from translation import (
    Config, WorkflowOrchestrator, 
    TerminologyManager, TaskContext
)

async def main():
    # 创建配置
    config = Config(api_key="your-key")
    
    # 创建术语管理器
    tm = TerminologyManager("terms.xlsx", config)
    
    # 创建工作流编排器
    orchestrator = WorkflowOrchestrator(config)
    
    # 创建任务列表
    tasks = [
        TaskContext(idx=0, key="TM_0", source_text="紫钻", target_lang="英语"),
        TaskContext(idx=1, key="TM_1", source_text="蓝钻", target_lang="英语"),
        TaskContext(idx=2, key="TM_2", source_text="红钻", target_lang="日语")
    ]
    
    # 执行翻译
    results = await orchestrator.execute(tasks, "result.xlsx")
    
    # 查看结果
    for r in results:
        if r.status == "SUCCESS":
            print(f"{r.source_text} -> {r.final_trans}")
    
    # 关闭术语管理器
    await tm.shutdown()

asyncio.run(main())
```

### 2. 术语库管理

```python
import asyncio
from translation import TerminologyManager, Config

async def manage_terminology():
    config = Config()
    tm = TerminologyManager("terms.xlsx", config)
    
    # 查询术语
    term = tm.query("紫钻")
    if term:
        print(f"找到术语：{term}")
    
    # 添加新术语
    tm.add_entry(
        key="TM_100",
        source_text="绿钻",
        translations={
            "英语": "Green Diamond",
            "日语": "グリーンダイヤモンド"
        }
    )
    
    # 导出术语库
    await tm.export_to_excel("updated_terms.xlsx")
    
    # 查看历史
    history = await tm.get_history_timeline(days=7)
    print(f"最近 7 天变更记录：{len(history)}条")
    
    # 保存并关闭
    await tm.shutdown()

asyncio.run(manage_terminology())
```

## 💡 最佳实践

### 1. 术语库管理

```python
# ✅ 好的做法：总是使用上下文管理器或确保关闭
tm = TerminologyManager("terms.xlsx", config)
try:
    # 使用术语管理器
    ...
finally:
    await tm.shutdown()

# ❌ 不好的做法：忘记关闭导致数据丢失
tm = TerminologyManager("terms.xlsx", config)
# 使用...
# 忘记关闭
```

### 2. 错误处理

```python
from translation import log_with_tag, LogLevel, LogTag

try:
    results = await orchestrator.execute(tasks, "result.xlsx")
except Exception as e:
    log_with_tag(
        f"翻译失败：{str(e)}",
        level=LogLevel.ERROR,
        tag=LogTag.CRITICAL
    )
    raise
```

### 3. 性能优化

```python
# 批量处理任务，而不是单个处理
tasks = [TaskContext(...) for i, row in data.iterrows()]
results = await orchestrator.execute(tasks, "result.xlsx")

# 避免频繁查询术语库
matches = {text: tm.query(text) for text in unique_texts}
```

## 🔗 相关文档

- [架构设计](../architecture/ARCHITECTURE.md)
- [快速开始](../guides/QUICKSTART.md)
- [API 参考](../api/API_REFERENCE.md)
