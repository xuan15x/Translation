# 模块使用指南

**版本**: v3.2.0
**日期**: 2026-04-03

本文档提供六层架构中每个模块的详细说明，包括职责、依赖关系、导入路径和使用示例。

---

## 📑 目录

- [架构概览](#架构概览)
- [模块详细指南](#模块详细指南)
  - [Presentation Layer](#1-presentation-layer-表示层)
  - [Application Layer](#2-application-layer-应用层)
  - [Domain Layer](#3-domain-layer-领域层)
  - [Service Layer](#4-service-layer-服务层)
  - [Data Access Layer](#5-data-access-layer-数据访问层)
  - [Infrastructure Layer](#6-infrastructure-layer-基础设施层)
- [模块依赖关系](#模块依赖关系)
- [导入路径变更](#导入路径变更)
- [常见问题](#常见问题)

---

## 架构概览

```
Presentation (表示层)
       ↓
Application (应用层)
       ↓
Domain (领域层)
       ↓
Service (服务层)
       ↓
Data Access (数据访问层)
       ↓
Infrastructure (基础设施层)
```

**依赖规则**:
- 上层可以依赖下层
- 下层不能依赖上层
- 同层模块尽量独立

---

## 模块详细指南

### 1. Presentation Layer (表示层)

**位置**: `presentation/`

#### 1.1 `gui_app.py` - GUI 主界面

**职责**:
- 提供 Tkinter 图形界面
- 文件选择、语言配置、提示词编辑
- 任务执行控制和进度显示
- 异步任务调度和日志集成

**依赖**:
- `application/translation_facade.py`
- `infrastructure/logging/`
- `infrastructure/config/`

**导入示例**:
```python
from presentation.gui_app import TranslationApp

app = TranslationApp(config_path="config.json")
app.run()
```

---

#### 1.2 `translation.py` - 程序入口

**职责**:
- 应用启动入口
- 初始化配置和依赖
- 错误处理和资源清理

**使用方式**:
```bash
python presentation/translation.py
```

---

#### 1.3 `error_handler.py` - 错误处理

**职责**:
- 全局异常处理
- 错误 UI 提示
- 用户友好的错误信息

**导入示例**:
```python
from presentation.error_handler import ErrorHandler

handler = ErrorHandler()
handler.show_error("操作失败", "请检查配置文件")
```

---

### 2. Application Layer (应用层)

**位置**: `application/`

#### 2.1 `translation_facade.py` - 外观模式 ⭐

**职责**:
- **TranslationServiceFacade**: 统一对外接口
- 简化调用流程
- 提供高级 API，一行代码完成复杂翻译

**依赖**:
- `application/workflow_coordinator.py`
- `domain/translation_service_impl.py`
- `service/api_provider.py`

**导入示例**:
```python
from application.translation_facade import TranslationServiceFacade

facade = TranslationServiceFacade(config_path="config.json")

# 一行代码完成翻译
result = await facade.translate_file(
    input_file="input.xlsx",
    source_lang="中文",
    target_lang="英语"
)
```

**主要方法**:
- `translate_file()`: 文件翻译
- `translate_text()`: 文本翻译
- `get_statistics()`: 获取统计信息

---

#### 2.2 `workflow_coordinator.py` - 工作流协调器

**职责**:
- **TranslationWorkflowCoordinator**: 翻译流程协调
- 协调初译、校对、术语查询
- 支持双阶段翻译流程

**依赖**:
- `domain/terminology_service_impl.py`
- `domain/translation_service_impl.py`
- `service/api_stages.py`

**导入示例**:
```python
from application.workflow_coordinator import TranslationWorkflowCoordinator

coordinator = TranslationWorkflowCoordinator(
    terminology_service=terminology_service,
    translation_service=translation_service
)

result = await coordinator.process_task(task_context)
```

---

#### 2.3 `batch_processor.py` - 批量处理器

**职责**:
- **BatchTaskProcessor**: 批量任务处理
- 动态分批、预分配内存
- 并发控制和进度跟踪

**导入示例**:
```python
from application.batch_processor import BatchTaskProcessor

processor = BatchTaskProcessor(
    coordinator=coordinator,
    max_concurrency=10
)

results = await processor.process_batch(tasks)
```

---

#### 2.4 `result_builder.py` - 结果构建器

**职责**:
- 翻译结果组装
- 格式化和导出
- 统计信息生成

**导入示例**:
```python
from application.result_builder import ResultBuilder

builder = ResultBuilder()
builder.add_result(task_id, result)
df = builder.to_dataframe()
builder.export_to_excel("output.xlsx")
```

---

### 3. Domain Layer (领域层)

**位置**: `domain/`

#### 3.1 `models.py` - 领域模型 ⭐

**职责**:
- **Config**: 系统配置类
- **TaskContext**: 任务上下文
- **StageResult**: 阶段执行结果
- **FinalResult**: 最终翻译结果

**导入示例**:
```python
from domain.models import Config, TaskContext, FinalResult

config = Config(api_key="your_key", target_lang="英语")
task = TaskContext(text="需要翻译的文本", config=config)
```

---

#### 3.2 `services.py` - 服务接口

**职责**:
- **ITerminologyDomainService**: 术语服务接口
- **ITranslationDomainService**: 翻译服务接口
- 业务规则契约

**导入示例**:
```python
from domain.services import ITerminologyDomainService, ITranslationDomainService

# 接口定义，用于依赖注入
class CustomTerminologyService(ITerminologyDomainService):
    def find_match(self, text, lang):
        # 实现
        pass
```

---

#### 3.3 `terminology_service_impl.py` - 术语领域服务 ⭐

**职责**:
- **TerminologyDomainServiceImpl**: 术语服务实现
- 6 级性能优化
- 纯业务逻辑，无外部依赖

**依赖**:
- `domain/models.py`
- `domain/services.py`
- `data_access/fuzzy_matcher.py` (通过接口)

**导入示例**:
```python
from domain.terminology_service_impl import TerminologyDomainServiceImpl
from domain.models import Config

config = Config()
service = TerminologyDomainServiceImpl(
    repository=terminology_repository,
    fuzzy_matcher=fuzzy_matcher
)

# 查找匹配术语
match = await service.find_match("查询文本", "英语")
```

---

#### 3.4 `translation_service_impl.py` - 翻译领域服务 ⭐

**职责**:
- **TranslationDomainServiceImpl**: 翻译服务实现
- translate() / proofread() 双阶段翻译
- 纯业务逻辑，无外部依赖

**依赖**:
- `domain/models.py`
- `domain/services.py`
- API 服务 (通过依赖注入)

**导入示例**:
```python
from domain.translation_service_impl import TranslationDomainServiceImpl
from domain.models import TaskContext

service = TranslationDomainServiceImpl(
    api_service=api_service,
    terminology_service=terminology_service
)

result = await service.translate(task_context)
```

---

#### 3.5 `cache_decorators.py` - 缓存装饰器

**职责**:
- **CachedTerminologyService**: 术语缓存装饰器
- LRU 缓存装饰器
- 性能提升 100 倍

**导入示例**:
```python
from domain.cache_decorators import cached_terminology_service

# 为术语服务添加缓存
cached_service = cached_terminology_service(terminology_service, max_size=2000)
```

---

### 4. Service Layer (服务层)

**位置**: `service/`

#### 4.1 `api_provider.py` - API 服务 ⭐

**职责**:
- **APIProviderManager**: 7 种 API 提供商管理
- DeepSeekClient / OpenAIClient
- API 调用封装 / 错误处理

**导入示例**:
```python
from service.api_provider import APIProviderManager

manager = APIProviderManager(config)
manager.add_provider("deepseek", api_key="key", base_url="url")

response = await manager.call_provider("deepseek", prompt)
```

---

#### 4.2 `api_stages.py` - API 阶段

**职责**:
- **APIDraftStage**: 初译阶段
- **APIReviewStage**: 校对阶段
- 统一的 API 调用接口

**导入示例**:
```python
from service.api_stages import APIDraftStage, APIReviewStage

draft_stage = APIDraftStage(api_provider)
review_stage = APIReviewStage(api_provider)

draft_result = await draft_stage.execute(task_context)
final_result = await review_stage.execute(task_context, draft_result)
```

---

### 5. Data Access Layer (数据访问层)

**位置**: `data_access/`

#### 5.1 `repositories.py` - 仓储实现 ⭐

**职责**:
- **TerminologyRepository**: 术语库仓储
- 术语库 CRUD 操作
- 查询优化和缓存

**导入示例**:
```python
from data_access.repositories import TerminologyRepository

repo = TerminologyRepository(db_path="terms.db")
await repo.add_entry("source", "target", "translation")
entries = await repo.search("source")
```

---

#### 5.2 `fuzzy_matcher.py` - 模糊匹配引擎

**职责**:
- **FuzzyMatcher**: 模糊匹配
- thefuzz 字符串相似度匹配
- 多进程加速支持

**导入示例**:
```python
from data_access.fuzzy_matcher import FuzzyMatcher

matcher = FuzzyMatcher(threshold=60)
best_match = matcher.find_best_match("query", candidates)
```

---

### 6. Infrastructure Layer (基础设施层)

**位置**: `infrastructure/`

Infrastructure 层拆分为 **6 个子模块**：

---

#### 📦 `cache/` - 缓存子模块

**职责**:
- LRU 缓存实现
- 统一缓存接口
- 内存限制和过期清理

**导入示例**:
```python
from infrastructure.cache.cache import LRUCache, TerminologyCache

cache = LRUCache(max_size=1000)
cache.set("key", "value")
value = cache.get("key")
```

---

#### ⚙️ `config/` - 配置子模块

**职责**:
- 配置常量定义
- JSON/YAML 配置加载
- 配置验证和检查
- 模型提供商管理

**导入示例**:
```python
from infrastructure.config.config import Config
from infrastructure.config.loader import ConfigLoader

config = Config()
loader = ConfigLoader()
config = loader.load("config.json")
```

---

#### 🗄️ `database/` - 数据库子模块

**职责**:
- 数据库连接池
- 仓储基类
- 连接管理

**导入示例**:
```python
from infrastructure.database.db_pool import DatabasePool

pool = DatabasePool(db_path="data.db", pool_size=5)
connection = pool.get_connection()
```

---

#### 💉 `di/` - 依赖注入子模块 ⭐

**职责**:
- DI 容器
- 服务注册和解析
- 生命周期管理

**导入示例**:
```python
from infrastructure.di.di_container import DIContainer

container = DIContainer()

# 注册服务
container.register_singleton(Config, lambda: Config())
container.register_transient(ITerminologyDomainService, TerminologyDomainServiceImpl)

# 解析服务
config = container.resolve(Config)
terminology_service = container.resolve(ITerminologyDomainService)
```

---

#### 📝 `logging/` - 日志子模块

**职责**:
- 日志配置
- 日志系统
- GUI 日志控制器
- 日志切片

**导入示例**:
```python
from infrastructure.logging.log_config import ModuleLoggerMixin, setup_logger

logger = setup_logger("my_module")
logger.info("信息")
logger.error("错误")
```

---

#### 🛠️ `utils/` - 工具子模块

**职责**:
- 并发控制器
- 性能监控
- 进度估算
- 冲突解决
- 撤销管理

**导入示例**:
```python
from infrastructure.utils.concurrency_controller import AdaptiveConcurrencyController
from infrastructure.utils.performance_monitor import PerformanceMonitor
from infrastructure.utils.progress_estimator import ProgressEstimator

# 并发控制
controller = AdaptiveConcurrencyController(config)
await controller.adjust(success=True)

# 性能监控
monitor = PerformanceMonitor()
monitor.start()

# 进度估算
estimator = ProgressEstimator()
estimator.update(completed=10, total=100)
eta = estimator.get_eta()
```

---

## 模块依赖关系

### 依赖规则

```
Presentation → Application → Domain ← Service → Data Access → Infrastructure
                                      ↑
                              (通过接口依赖)
```

### 详细依赖矩阵

| 模块 | 依赖 |
|------|------|
| `presentation/gui_app.py` | `application/translation_facade.py`, `infrastructure/logging/` |
| `application/translation_facade.py` | `application/workflow_coordinator.py`, `domain/` |
| `application/workflow_coordinator.py` | `domain/`, `service/api_stages.py` |
| `domain/terminology_service_impl.py` | `domain/models.py`, `data_access/fuzzy_matcher.py` (接口) |
| `domain/translation_service_impl.py` | `domain/models.py`, API 服务 (接口) |
| `service/api_provider.py` | `infrastructure/config/`, `infrastructure/logging/` |
| `data_access/repositories.py` | `infrastructure/database/`, `domain/models.py` |
| `infrastructure/*` | 无上层依赖 |

---

## 导入路径变更

### v3.0 → v3.1 导入路径变更

#### Infrastructure 层

```python
# 缓存
# 旧 (v3.0)
from infrastructure.cache import LRUCache

# 新 (v3.1)
from infrastructure.cache.cache import LRUCache

# 并发控制
# 旧
from infrastructure.concurrency_controller import AdaptiveConcurrencyController

# 新
from infrastructure.utils.concurrency_controller import AdaptiveConcurrencyController

# 日志
# 旧
from infrastructure.log_config import ModuleLoggerMixin

# 新
from infrastructure.logging.log_config import ModuleLoggerMixin

# 配置
# 旧
from infrastructure.config import Config

# 新
from infrastructure.config.config import Config

# 性能监控
# 旧
from infrastructure.performance_monitor import PerformanceMonitor

# 新
from infrastructure.utils.performance_monitor import PerformanceMonitor

# 进度估算
# 旧
from infrastructure.progress_estimator import ProgressEstimator

# 新
from infrastructure.utils.progress_estimator import ProgressEstimator
```

#### Domain 层

```python
# 模型
# 旧 (v3.0) - 多个模型文件
from infrastructure.models import Config
from domain.models import TaskContext

# 新 (v3.1) - 统一到 domain/models.py
from domain.models import Config, TaskContext, FinalResult

# 服务接口
# 旧
from infrastructure.repositories import ITerminologyRepository

# 新
from domain.services import ITerminologyDomainService
```

#### Data Access 层

```python
# 仓储
# 旧
from infrastructure.repositories import TerminologyRepository

# 新
from data_access.repositories import TerminologyRepository
```

---

## 常见问题

### Q1: 为什么要拆分 Infrastructure 层？

**A**: Infrastructure 层包含 26 个文件，职责混乱。拆分为 6 个子模块后：
- 每个子模块职责单一
- 降低维护复杂度
- 便于团队协作

---

### Q2: 旧的导入路径还能用吗？

**A**: 暂时可以。我们保留了向后兼容文件，但会显示 Deprecated 警告。建议在 30 天内完成迁移。

---

### Q3: Domain 层为什么不能依赖 Service 层？

**A**: 根据分层架构原则：
- Domain 层是纯业务逻辑
- Service 层是外部服务集成
- Domain 应该独立，便于测试和复用

---

### Q4: 如何使用 DI 容器？

**A**: 参考 `infrastructure/di/di_container.py` 示例：
```python
container = DIContainer()
container.register_singleton(Config, lambda: Config())
config = container.resolve(Config)
```

---

### Q5: 如何添加新的子模块？

**A**: 在 `infrastructure/` 下创建新目录，确保：
1. 添加 `__init__.py`
2. 更新 `infrastructure/__init__.py` 导出
3. 更新架构文档

---

### Q6: 配置应该放在哪里？

**A**: 
- 新配置: `infrastructure/config/`
- 旧配置: `config/` (向后兼容，已弃用)

---

### Q7: 如何迁移旧代码？

**A**: 参考 `MIGRATION_GUIDE.md` 获取详细迁移步骤。

---

**更新日期**: 2026-04-03
**版本**: v3.1
**维护**: 架构团队