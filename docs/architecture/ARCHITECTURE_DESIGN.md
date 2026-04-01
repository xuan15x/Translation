# 系统架构设计文档

## 📋 概述

本文档详细介绍 AI 智能翻译系统的五层模块化架构设计。

## 🏗️ 架构总览

```
┌─────────────────────────────────────────────────┐
│           Presentation Layer (表示层)            │
│   ┌───────────────┐  ┌─────────────────────┐   │
│   │ translation.py│  │    gui_app.py       │   │
│   └───────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│        Business Logic Layer (业务逻辑层)         │
│   ┌──────────────────┐  ┌──────────────────┐   │
│   │ workflow_        │  │ terminology_     │   │
│   │ orchestrator.py  │  │ manager.py       │   │
│   └──────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           Service Layer (服务层)                │
│   ┌───────────────┐  ┌─────────────────────┐   │
│   │ api_provider. │  │ translation_history.│   │
│   │ py            │  │ py                  │   │
│   └───────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          Data Access Layer (数据访问层)          │
│   ┌──────────────────┐  ┌──────────────────┐   │
│   │ config_persist.  │  │ terminology_upd. │   │
│   │ fuzzy_matcher.py │  └──────────────────┘   │
│   └──────────────────┘                         │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│        Infrastructure Layer (基础设施层)         │
│   ┌───────────────┐  ┌─────────────────────┐   │
│   │ models.py     │  │ log_config.py       │   │
│   │ concurrency_  │  │ ...                 │   │
│   │ controller.py │  │                     │   │
│   └───────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## 📦 层级职责

### 1. 表示层 (Presentation Layer)

**职责**: 
- 提供用户界面 (GUI)
- 处理用户交互
- 显示执行结果

**模块**:
- `translation.py`: 程序入口
- `gui_app.py`: GUI 主界面

**关键类**:
- `TranslationApp`: GUI 应用主类

### 2. 业务逻辑层 (Business Logic Layer)

**职责**:
- 编排翻译流程
- 管理术语库
- 实现核心业务规则

**模块**:
- `workflow_orchestrator.py`: 工作流编排
- `terminology_manager.py`: 术语管理

**关键类**:
- `WorkflowOrchestrator`: 工作流编排器
- `TerminologyManager`: 术语管理器

### 3. 服务层 (Service Layer)

**职责**:
- 封装外部 API 服务
- 管理翻译历史
- 提供通用服务

**模块**:
- `api_provider.py`: API 提供商管理
- `translation_history.py`: 翻译历史管理

**关键类**:
- `APIProvider`: API 提供商
- `TranslationHistoryManager`: 历史管理器

### 4. 数据访问层 (Data Access Layer)

**职责**:
- 持久化配置文件
- 导入/导出术语库
- 实现模糊匹配算法

**模块**:
- `config_persistence.py`: 配置持久化
- `terminology_update.py`: 术语更新
- `fuzzy_matcher.py`: 模糊匹配

**关键类**:
- `ConfigPersistence`: 配置持久化工具
- `FuzzyMatcher`: 模糊匹配器

### 5. 基础设施层 (Infrastructure Layer)

**职责**:
- 提供数据模型
- 日志系统
- 并发控制
- 基础工具

**模块**:
- `models.py`: 数据模型
- `log_config.py`: 日志配置
- `concurrency_controller.py`: 并发控制

**关键类**:
- `Config`: 运行时配置
- `TaskContext`: 任务上下文
- `AdaptiveConcurrencyController`: 并发控制器

## 🔄 数据流

### 翻译流程数据流

```
用户输入 (GUI)
    ↓
[表示层] TranslationApp
    ↓
[业务逻辑层] WorkflowOrchestrator
    ├─→ [数据访问层] FuzzyMatcher (术语匹配)
    ├─→ [服务层] APIProvider (API 调用)
    └─→ [基础设施层] Config (配置)
    ↓
[业务逻辑层] TerminologyManager (更新术语)
    ↓
[表示层] 显示结果
```

### 具体示例

```python
# 1. 用户在 GUI 点击"开始翻译"
app.start_translation()  # presentation/gui_app.py

# 2. 创建工作流编排器
orchestrator = WorkflowOrchestrator(config)  # business_logic

# 3. 准备任务列表
tasks = [
    TaskContext(idx=0, source_text="紫钻", target_lang="英语")
]

# 4. 执行翻译
results = await orchestrator.execute(tasks, "result.xlsx")

# 5. 内部流程
# 4.1 查询术语库
term_match = tm.query("紫钻")  # data_access.FuzzyMatcher

# 4.2 调用 API
response = await api_client.translate(...)  # service.APIProvider

# 4.3 记录日志
log_with_tag("翻译完成", tag=LogTag.IMPORTANT)  # infrastructure.log_config

# 6. 保存结果并显示
save_results(results)  # data_access
show_in_gui(results)   # presentation
```

## 🎯 设计原则

### 1. 单一职责原则 (SRP)

每个类只负责一个职责:

```python
# ✅ 好的设计
class TerminologyManager:  # 只负责术语管理
    def query(self, text): ...
    def add_entry(self, ...): ...

class WorkflowOrchestrator:  # 只负责流程编排
    async def execute(self, tasks): ...
```

### 2. 依赖倒置原则 (DIP)

高层模块不依赖低层模块，都依赖抽象:

```python
# ✅ 好的设计
class WorkflowOrchestrator:
    def __init__(self, config: Config):  # 依赖抽象
        self.config = config
    
    async def execute(self, tasks):
        # 使用 config
        pass
```

### 3. 接口隔离原则 (ISP)

使用多个专门的接口，而不是单个总接口:

```python
# ✅ 好的设计
class ConfigPersistence:  # 专门处理配置
    def load_json(self, path): ...
    def save_json(self, path, data): ...

class FuzzyMatcher:  # 专门处理匹配
    def calculate_similarity(self, s1, s2): ...
    def find_best_match(self, query, candidates): ...
```

## 📊 模块关系

### 依赖关系图

```
presentation
    ↓
business_logic
    ↓
service
    ↓
data_access
    ↓
infrastructure
```

### 导入规则

```python
# ✅ 允许的导入
from infrastructure import Config
from data_access import FuzzyMatcher
from service import APIProvider
from business_logic import WorkflowOrchestrator
from presentation import TranslationApp

# ❌ 不允许的导入 (反向依赖)
# from infrastructure import WorkflowOrchestrator
# from business_logic import TranslationApp
```

## 🔧 核心机制

### 1. 双阶段翻译机制

```python
# 第一阶段：初译
draft_result = await api_draft(
    source_text="紫钻",
    target_lang="英语",
    term_matches={"英语": "Purple Diamond"}
)

# 第二阶段：校对
final_result = await api_review(
    draft_trans=draft_result.translation,
    target_lang="英语"
)
```

### 2. 术语匹配机制

```python
# 精确匹配 → 模糊匹配 → API 翻译
if exact_match := tm.query(source_text):
    result = exact_match
elif fuzzy_match := tm.query(source_text, fuzzy_threshold=0.6):
    result = fuzzy_match
else:
    result = await api_translate(source_text)
```

### 3. 自适应并发机制

```python
# 根据成功率动态调整并发数
async with controller.acquire():
    try:
        await task()
        controller.record_success()  # 成功，可能增加并发
    except Exception:
        controller.record_failure()  # 失败，降低并发
```

## 💡 扩展性设计

### 1. 支持新的 API 提供商

```python
# 在 service/api_provider.py 中添加
class NewProvider(APIProvider):
    async def translate(self, text, target_lang):
        # 实现新提供商的 API 调用
        pass
```

### 2. 添加新的日志级别

```python
# 在 infrastructure/log_config.py 中添加
class LogTag(Enum):
    CUSTOM = "custom"  # 新标签
```

### 3. 扩展术语库功能

```python
# 继承 TerminologyManager
class EnhancedTerminologyManager(TerminologyManager):
    async def batch_import(self, files):
        # 批量导入功能
        pass
```

## 🔗 相关文档

- [API 参考](../api/API_REFERENCE_FULL.md)
- [快速开始](../guides/QUICKSTART.md)
- [开发指南](../development/TESTING_GUIDE.md)
