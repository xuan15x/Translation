# 导入路径规范指南

本文档定义了项目的导入路径规范，确保代码的一致性和可维护性。

## 目录结构概览

```
translation/
├── presentation/        # 表示层 (GUI)
├── application/         # 应用层 (流程编排)
├── domain/             # 领域层 (核心业务逻辑)
├── service/            # 服务层 (API集成)
├── data_access/        # 数据访问层 (仓储)
├── infrastructure/     # 基础设施层 (工具/日志/DI)
├── config/             # 配置管理
└── tests/              # 测试代码
```

## 正确的导入路径

### 1. 配置模块 (config/)

```python
# ✅ 正确
from config import ConfigLoader, DEFAULT_DRAFT_PROMPT
from config.config import get_default_config
from config.loader import get_config_loader

# ❌ 错误 - infrastructure.config 已删除
from infrastructure.config import ...
```

### 2. 数据模型 (infrastructure/models/)

```python
# ✅ 正确
from infrastructure.models.models import Config, TaskContext, StageResult, FinalResult
from infrastructure.models import Config  # 通过 __init__.py 导出

# ❌ 错误 - 旧的 infrastructure.models.py 已删除
# 注意：不要直接从 infrastructure 导入模型
```

### 3. 依赖注入 (infrastructure/di/)

```python
# ✅ 正确
from infrastructure.di import DependencyContainer, get_container, initialize_container
from infrastructure.di.di_container import DependencyContainer

# ❌ 错误
from infrastructure.di_container import ...  # 已删除
```

### 4. 缓存模块 (infrastructure/cache/ 和 domain/)

```python
# ✅ 正确 - 基础缓存
from infrastructure.cache import TerminologyCache, LRUCache, UnifiedCacheManager

# ✅ 正确 - 缓存装饰器（在 domain 层）
from domain.cache_decorators import CachedTerminologyService, CachedTranslationService

# ❌ 错误
from infrastructure.cache.cache_decorators import ...  # 已删除
```

### 5. 日志模块 (infrastructure/logging/)

```python
# ✅ 正确 - 配置相关
from infrastructure.logging import (
    LogLevel, LogGranularity, LogTag, LogConfig,
    setup_logger, LogManager, get_logger, get_log_manager
)

# ✅ 正确 - 切片相关
from infrastructure.logging import (
    LogCategory, LogContext, LoggerSlice,
    log_slice, create_logger_slice, get_category_by_module
)

# ✅ 正确 - GUI相关
from infrastructure.logging import GUILogController, GUILogHandler, ColorFormatter

# ❌ 错误 - formatter.py 中的 GUILogController 已删除
# 应该从 gui_log_controller.py 导入
```

### 6. 数据库模块 (infrastructure/database/)

```python
# ✅ 正确
from infrastructure.database import ConnectionPool, DatabaseManager

# ✅ 正确 - 仓储（在 data_access 层）
from data_access.repositories import ITermRepository

# ❌ 错误
from infrastructure.database.repositories import ...  # 已删除
```

### 7. 工具模块 (infrastructure/utils/)

```python
# ✅ 正确
from infrastructure.utils import (
    AdaptiveConcurrencyController,
    HealthCheckService,
    PerformanceMonitor
)

# ❌ 错误 - infrastructure.utils.py 已删除
from infrastructure.utils import ...  # 应该从 infrastructure.utils.utils 导入
```

### 8. 仓储模块 (data_access/)

```python
# ✅ 正确
from data_access.repositories import ITermRepository
from data_access.config_persistence import ConfigPersistence

# ❌ 错误
from infrastructure.database.repositories import ...  # 已删除
```

## 分层导入规则

### 各层只能导入下层或同层模块

| 层级 | 可以导入 |
|------|----------|
| presentation | application, domain, infrastructure, config |
| application | domain, service, data_access, infrastructure, config |
| domain | infrastructure (仅基础工具), config |
| service | domain, infrastructure, config |
| data_access | domain, infrastructure, config |
| infrastructure | config (仅常量) |
| config | 无 |

### 禁止的导入模式

```python
# ❌ 禁止：上层导入下层的具体实现
from application import SomeInfrastructureImpl  # 应该导入接口

# ❌ 禁止：循环导入
# domain -> application -> domain

# ❌ 禁止：跨层导入
# presentation -> data_access (应该通过 application 层)
```

## 导入路径检查清单

在提交代码前，请检查：

- [ ] 所有导入路径都指向正确的文件位置
- [ ] 没有使用已删除的模块路径
- [ ] 遵循分层导入规则
- [ ] `__init__.py` 中的导出与实际文件一致
- [ ] 没有循环导入
- [ ] 使用绝对导入而非相对导入（除非必要）

## 常见错误及解决方案

### 错误1: ModuleNotFoundError: No module named 'infrastructure.config'

**原因**: `infrastructure/config/` 目录已删除  
**解决**: 改为 `from config import ...`

### 错误2: ImportError: cannot import name 'X' from 'infrastructure.models'

**原因**: `infrastructure/models.py` 已删除  
**解决**: 改为 `from infrastructure.models.models import X` 或 `from infrastructure.models import X`

### 错误3: ModuleNotFoundError: No module named 'infrastructure.cache.cache_decorators'

**原因**: 缓存装饰器已移至 domain 层  
**解决**: 改为 `from domain.cache_decorators import ...`

### 错误4: ImportError: cannot import name 'ITermRepository' from 'infrastructure.database'

**原因**: 仓储接口已移至 data_access 层  
**解决**: 改为 `from data_access.repositories import ITermRepository`

## __init__.py 导出规范

每个模块的 `__init__.py` 应该：

1. 只导出公共API
2. 使用 `__all__` 明确声明导出内容
3. 保持导出内容与实际实现一致
4. 避免导出内部实现细节

示例：

```python
# infrastructure/logging/__init__.py
from .config import LogLevel, LogConfig, setup_logger
from .log_config import LogManager, get_logger
from .slice import LoggerSlice, LogCategory

__all__ = [
    'LogLevel', 'LogConfig', 'setup_logger',
    'LogManager', 'get_logger',
    'LoggerSlice', 'LogCategory'
]
```

## 维护指南

1. **添加新模块时**：立即更新相关的 `__init__.py` 文件
2. **重构代码时**：同步更新导入路径
3. **删除文件时**：检查并更新所有引用
4. **定期验证**：运行 `python -m pytest` 确保所有导入正常

## 自动化检查工具

使用以下命令验证导入路径：

```bash
# 编译检查
python -m py_compile <file.py>

# 导入验证
python -c "from module import ClassName"

# 运行测试
pytest tests/ -v
```

## 版本历史

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-04-03 | v3.1 | 删除重复文件，统一导入路径 |
| 2026-01-01 | v3.0 | 初始六层架构 |
