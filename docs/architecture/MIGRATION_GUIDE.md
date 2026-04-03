# 迁移指南 v3.0 → v3.1

**日期**: 2026-04-03
**目标**: 从 v3.0 架构迁移到 v3.1 架构

本文档提供详细的迁移步骤，帮助你将代码从 v3.0 升级到 v3.1 架构。

---

## 📑 目录

- [迁移概述](#迁移概述)
- [旧路径到新路径的映射](#旧路径到新路径的映射)
- [导入语句变更清单](#导入语句变更清单)
- [迁移步骤](#迁移步骤)
- [自动化迁移脚本](#自动化迁移脚本)
- [常见问题](#常见问题)

---

## 迁移概述

### v3.1 主要变更

1. **Infrastructure 层拆分**: 26 个文件 → 6 个子模块
2. **Domain 层独立**: 消除对 Service 层的依赖
3. **仓储接口移动**: 从 Infrastructure 移至 Domain
4. **配置模块整合**: 游离配置移至 Infrastructure/config/

### 迁移影响

| 影响范围 | 程度 | 说明 |
|----------|------|------|
| 导入语句 | 🔴 高 | 大量导入路径变更 |
| 依赖注入 | 🟡 中 | Domain 服务需通过 DI |
| 配置文件 | 🟡 中 | 配置路径变更 |
| 测试代码 | 🟡 中 | Mock 路径变更 |

### 迁移时间估算

| 项目规模 | 文件数 | 预计时间 |
|----------|--------|----------|
| 小型项目 | < 10 | 1-2 小时 |
| 中型项目 | 10-30 | 3-5 小时 |
| 大型项目 | > 30 | 1-2 天 |

---

## 旧路径到新路径的映射

### Infrastructure 层路径映射

| 旧路径 (v3.0) | 新路径 (v3.1) | 变更类型 |
|---------------|---------------|----------|
| `infrastructure/cache.py` | `infrastructure/cache/cache.py` | 📦 移动 |
| `infrastructure/unified_cache.py` | `infrastructure/cache/unified_cache.py` | 📦 移动 |
| `infrastructure/config.py` | `infrastructure/config/config.py` | ⚙️ 移动 |
| `infrastructure/loader.py` | `infrastructure/config/loader.py` | ⚙️ 移动 |
| `infrastructure/checker.py` | `infrastructure/config/checker.py` | ⚙️ 移动 |
| `infrastructure/constants.py` | `infrastructure/config/constants.py` | ⚙️ 移动 |
| `infrastructure/model_manager.py` | `infrastructure/config/model_manager.py` | ⚙️ 移动 |
| `infrastructure/model_providers.py` | `infrastructure/config/model_providers.py` | ⚙️ 移动 |
| `infrastructure/smart_config.py` | `infrastructure/config/smart_config.py` | ⚙️ 移动 |
| `infrastructure/db_pool.py` | `infrastructure/database/db_pool.py` | 🗄️ 移动 |
| `infrastructure/repositories.py` | `infrastructure/database/repositories.py` | 🗄️ 移动 |
| `infrastructure/di_container.py` | `infrastructure/di/di_container.py` | 💉 移动 |
| `infrastructure/log_config.py` | `infrastructure/logging/log_config.py` | 📝 移动 |
| `infrastructure/logging_config.py` | `infrastructure/logging/logging_config.py` | 📝 移动 |
| `infrastructure/gui_log_controller.py` | `infrastructure/logging/gui_log_controller.py` | 📝 移动 |
| `infrastructure/log_slice.py` | `infrastructure/logging/log_slice.py` | 📝 移动 |
| `infrastructure/concurrency_controller.py` | `infrastructure/utils/concurrency_controller.py` | 🛠️ 移动 |
| `infrastructure/performance_monitor.py` | `infrastructure/utils/performance_monitor.py` | 🛠️ 移动 |
| `infrastructure/progress_estimator.py` | `infrastructure/utils/progress_estimator.py` | 🛠️ 移动 |
| `infrastructure/conflict_resolver.py` | `infrastructure/utils/conflict_resolver.py` | 🛠️ 移动 |
| `infrastructure/undo_manager.py` | `infrastructure/utils/undo_manager.py` | 🛠️ 移动 |
| `infrastructure/health_check.py` | `infrastructure/utils/health_check.py` | 🛠️ 移动 |
| `infrastructure/memory_manager.py` | `infrastructure/utils/memory_manager.py` | 🛠️ 移动 |
| `infrastructure/config_metrics.py` | `infrastructure/utils/config_metrics.py` | 🛠️ 移动 |
| `infrastructure/utils.py` | `infrastructure/utils/utils.py` | 🛠️ 移动 |

### Domain 层路径映射

| 旧路径 (v3.0) | 新路径 (v3.1) | 变更类型 |
|---------------|---------------|----------|
| `infrastructure/models.py` | `domain/models.py` | 🔄 合并 |
| `infrastructure/repositories.py` (接口) | `domain/services.py` | 🔄 移动 |

### Data Access 层路径映射

| 旧路径 (v3.0) | 新路径 (v3.1) | 变更类型 |
|---------------|---------------|----------|
| `infrastructure/repositories.py` (实现) | `data_access/repositories.py` | 🔄 移动 |
| `config_persistence.py` | `data_access/config_persistence.py` | 📦 移动 |
| `terminology_update.py` | `data_access/terminology_update.py` | 📦 移动 |
| `fuzzy_matcher.py` | `data_access/fuzzy_matcher.py` | 📦 移动 |

---

## 导入语句变更清单

### 1. 缓存模块

```python
# ❌ 旧代码 (v3.0)
from infrastructure.cache import LRUCache, TerminologyCache
from infrastructure.cache import cached

# ✅ 新代码 (v3.1)
from infrastructure.cache.cache import LRUCache, TerminologyCache
from infrastructure.cache.cache import cached
```

---

### 2. 配置模块

```python
# ❌ 旧代码 (v3.0)
from infrastructure.config import Config
from infrastructure.config import load_config
from infrastructure.constants import TARGET_LANGUAGES

# ✅ 新代码 (v3.1)
from infrastructure.config.config import Config
from infrastructure.config.loader import load_config
from infrastructure.config.constants import TARGET_LANGUAGES
```

---

### 3. 并发控制

```python
# ❌ 旧代码 (v3.0)
from infrastructure.concurrency_controller import AdaptiveConcurrencyController

# ✅ 新代码 (v3.1)
from infrastructure.utils.concurrency_controller import AdaptiveConcurrencyController
```

---

### 4. 日志模块

```python
# ❌ 旧代码 (v3.0)
from infrastructure.log_config import ModuleLoggerMixin, setup_logger
from infrastructure.logging_config import init_logging
from infrastructure.gui_log_controller import GUILogController

# ✅ 新代码 (v3.1)
from infrastructure.logging.log_config import ModuleLoggerMixin, setup_logger
from infrastructure.logging.logging_config import init_logging
from infrastructure.logging.gui_log_controller import GUILogController
```

---

### 5. 性能监控

```python
# ❌ 旧代码 (v3.0)
from infrastructure.performance_monitor import PerformanceMonitor

# ✅ 新代码 (v3.1)
from infrastructure.utils.performance_monitor import PerformanceMonitor
```

---

### 6. 进度估算

```python
# ❌ 旧代码 (v3.0)
from infrastructure.progress_estimator import ProgressEstimator

# ✅ 新代码 (v3.1)
from infrastructure.utils.progress_estimator import ProgressEstimator
```

---

### 7. 依赖注入

```python
# ❌ 旧代码 (v3.0)
from infrastructure.di_container import DIContainer

# ✅ 新代码 (v3.1)
from infrastructure.di.di_container import DIContainer
```

---

### 8. 数据库

```python
# ❌ 旧代码 (v3.0)
from infrastructure.db_pool import DatabasePool

# ✅ 新代码 (v3.1)
from infrastructure.database.db_pool import DatabasePool
```

---

### 9. 模型

```python
# ❌ 旧代码 (v3.0)
from infrastructure.models import Config, TaskContext, FinalResult
from domain.models import TerminologyEntry

# ✅ 新代码 (v3.1)
from domain.models import Config, TaskContext, FinalResult, TerminologyEntry
```

---

### 10. 仓储

```python
# ❌ 旧代码 (v3.0)
from infrastructure.repositories import TerminologyRepository
from infrastructure.repositories import ITerminologyRepository

# ✅ 新代码 (v3.1)
from data_access.repositories import TerminologyRepository
from domain.services import ITerminologyRepository
```

---

### 11. 模糊匹配

```python
# ❌ 旧代码 (v3.0)
from infrastructure.fuzzy_matcher import FuzzyMatcher

# ✅ 新代码 (v3.1)
from data_access.fuzzy_matcher import FuzzyMatcher
```

---

### 12. 提示词构建

```python
# ❌ 旧代码 (v3.0)
from infrastructure.prompt_builder import PromptBuilder

# ✅ 新代码 (v3.1)
from infrastructure.prompt_builder import PromptBuilder  # 路径不变
```

---

### 13. 异常处理

```python
# ❌ 旧代码 (v3.0)
from infrastructure.exceptions import TranslationError

# ✅ 新代码 (v3.1)
from infrastructure.exceptions import TranslationError  # 路径不变
```

---

### 14. 撤销管理

```python
# ❌ 旧代码 (v3.0)
from infrastructure.undo_manager import UndoManager

# ✅ 新代码 (v3.1)
from infrastructure.utils.undo_manager import UndoManager
```

---

### 15. 冲突解决

```python
# ❌ 旧代码 (v3.0)
from infrastructure.conflict_resolver import ConflictResolver

# ✅ 新代码 (v3.1)
from infrastructure.utils.conflict_resolver import ConflictResolver
```

---

## 迁移步骤

### 阶段一：准备工作 (15 分钟)

#### 1.1 创建分支

```bash
git checkout -b migrate/v3.0-to-v3.1
```

#### 1.2 备份当前代码

```bash
# 创建备份
git archive --format=zip --output=backup_v3.0.zip HEAD
```

#### 1.3 运行测试基线

```bash
# 确保当前测试通过
pytest tests/ -v
pytest --cov=translation tests/ > coverage_before.txt
```

---

### 阶段二：更新导入语句 (1-2 小时)

#### 2.1 批量替换 Infrastructure 导入

使用 IDE 的全局查找替换功能：

```
查找: from infrastructure\.cache import
替换: from infrastructure.cache.cache import

查找: from infrastructure\.concurrency_controller import
替换: from infrastructure.utils.concurrency_controller import

查找: from infrastructure\.log_config import
替换: from infrastructure.logging.log_config import

查找: from infrastructure\.performance_monitor import
替换: from infrastructure.utils.performance_monitor import

查找: from infrastructure\.progress_estimator import
替换: from infrastructure.utils.progress_estimator import

查找: from infrastructure\.di_container import
替换: from infrastructure.di.di_container import

查找: from infrastructure\.db_pool import
替换: from infrastructure.database.db_pool import

查找: from infrastructure\.fuzzy_matcher import
替换: from data_access.fuzzy_matcher import
```

#### 2.2 更新模型导入

```python
# 查找所有 infrastructure.models 导入
# 替换为 domain.models

# ❌ 旧
from infrastructure.models import Config

# ✅ 新
from domain.models import Config
```

#### 2.3 更新仓储导入

```python
# ❌ 旧
from infrastructure.repositories import TerminologyRepository

# ✅ 新
from data_access.repositories import TerminologyRepository
```

---

### 阶段三：修复 Domain 层依赖 (30 分钟)

#### 3.1 修改 translation_service_impl.py

```python
# ❌ 旧代码 (v3.0)
from service.api_stages import APIDraftStage

class TranslationDomainServiceImpl:
    def __init__(self):
        self.api_stage = APIDraftStage()

# ✅ 新代码 (v3.1)
from domain.services import ITranslationDomainService
from typing import Protocol

class IAPIService(Protocol):
    async def call_api(self, prompt: str) -> str:
        ...

class TranslationDomainServiceImpl(ITranslationDomainService):
    def __init__(self, api_service: IAPIService):
        self.api_service = api_service
```

#### 3.2 更新 DI 容器配置

```python
# 在 di_container.py 中注册服务
container.register_singleton(
    IAPIService,
    lambda: APIProviderManager(config)
)

container.register_transient(
    ITranslationDomainService,
    TranslationDomainServiceImpl
)
```

---

### 阶段四：更新测试代码 (30 分钟)

#### 4.1 更新测试导入

```python
# ❌ 旧测试代码
from infrastructure.cache import LRUCache
from infrastructure.concurrency_controller import AdaptiveConcurrencyController

# ✅ 新测试代码
from infrastructure.cache.cache import LRUCache
from infrastructure.utils.concurrency_controller import AdaptiveConcurrencyController
```

#### 4.2 更新 Mock 路径

```python
# ❌ 旧
@patch('infrastructure.api_stages.APIDraftStage')

# ✅ 新
@patch('service.api_stages.APIDraftStage')
```

---

### 阶段五：验证和测试 (30 分钟)

#### 5.1 运行类型检查

```bash
mypy translation/
```

#### 5.2 运行测试

```bash
pytest tests/ -v
```

#### 5.3 检查覆盖率

```bash
pytest --cov=translation tests/
# 对比 coverage_before.txt
```

#### 5.4 手动测试

```bash
# 启动应用
python presentation/translation.py

# 测试核心功能
# 1. 加载配置
# 2. 翻译文本
# 3. 保存结果
```

---

### 阶段六：提交和合并 (15 分钟)

#### 6.1 提交变更

```bash
git add .
git commit -m "refactor: 迁移到 v3.1 架构

- 更新 Infrastructure 导入路径
- 修复 Domain 层依赖
- 更新测试代码
- 更新文档"
```

#### 6.2 创建 PR

```bash
git push origin migrate/v3.0-to-v3.1
# 创建 Pull Request
```

---

## 自动化迁移脚本

### 脚本 1: 导入路径自动替换

```python
#!/usr/bin/env python3
"""
导入路径迁移脚本
用法: python migrate_imports.py --dry-run (预览)
     python migrate_imports.py --apply (执行)
"""

import os
import re
from pathlib import Path

# 导入映射表
IMPORT_MAP = {
    r'from infrastructure\.cache import': 'from infrastructure.cache.cache import',
    r'from infrastructure\.concurrency_controller import': 'from infrastructure.utils.concurrency_controller import',
    r'from infrastructure\.log_config import': 'from infrastructure.logging.log_config import',
    r'from infrastructure\.performance_monitor import': 'from infrastructure.utils.performance_monitor import',
    r'from infrastructure\.progress_estimator import': 'from infrastructure.utils.progress_estimator import',
    r'from infrastructure\.di_container import': 'from infrastructure.di.di_container import',
    r'from infrastructure\.db_pool import': 'from infrastructure.database.db_pool import',
    r'from infrastructure\.fuzzy_matcher import': 'from data_access.fuzzy_matcher import',
    r'from infrastructure\.models import': 'from domain.models import',
    r'from infrastructure\.repositories import': 'from data_access.repositories import',
}

def migrate_file(file_path: Path, dry_run: bool = True):
    content = file_path.read_text(encoding='utf-8')
    new_content = content
    
    for pattern, replacement in IMPORT_MAP.items():
        new_content = re.sub(pattern, replacement, new_content)
    
    if content != new_content:
        if dry_run:
            print(f"[预览] {file_path}")
        else:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"[更新] {file_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    
    dry_run = args.dry_run or not args.apply
    
    for py_file in Path('.').rglob('*.py'):
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        migrate_file(py_file, dry_run)

if __name__ == '__main__':
    main()
```

**使用方式**:

```bash
# 预览变更
python scripts/migrate_imports.py --dry-run

# 执行迁移
python scripts/migrate_imports.py --apply
```

---

## 常见问题

### Q1: 迁移后测试失败怎么办？

**A**: 按以下步骤排查：
1. 检查导入路径是否正确
2. 检查 Mock 路径是否更新
3. 检查 DI 容器配置
4. 对比迁移前后的覆盖率报告

---

### Q2: 旧的导入路径还能用多久？

**A**: 我们提供了向后兼容文件，但会显示 Deprecated 警告。建议在 **30 天内** 完成迁移。

---

### Q3: 如何处理自定义的 Infrastructure 模块？

**A**: 
1. 判断模块职责
2. 移动到对应子模块：
   - 缓存相关 → `infrastructure/cache/`
   - 配置相关 → `infrastructure/config/`
   - 工具相关 → `infrastructure/utils/`
3. 更新导入路径

---

### Q4: Domain 层为什么不能直接实例化 Service？

**A**: 违反分层架构原则。应通过：
- 依赖注入 (DI)
- 接口隔离
- 控制反转 (IoC)

---

### Q5: 迁移过程中可以继续使用旧代码吗？

**A**: 可以。向后兼容文件允许新旧路径并存。建议：
1. 先创建分支
2. 逐步迁移
3. 验证后合并

---

### Q6: 如何处理第三方库的导入？

**A**: 第三方库导入不变，只变更项目内部模块导入。

---

### Q7: 迁移失败如何回滚？

**A**: 
```bash
# 如果使用 Git
git reset --hard HEAD

# 如果有备份
unzip backup_v3.0.zip
```

---

## 迁移检查清单

### 迁移前

- [ ] 创建 Git 分支
- [ ] 备份当前代码
- [ ] 运行测试基线
- [ ] 记录覆盖率

### 迁移中

- [ ] 更新 Infrastructure 导入
- [ ] 更新 Domain 导入
- [ ] 更新 Data Access 导入
- [ ] 修复 Domain 依赖
- [ ] 更新 DI 配置
- [ ] 更新测试代码

### 迁移后

- [ ] 运行类型检查 (mypy)
- [ ] 运行测试 (pytest)
- [ ] 检查覆盖率
- [ ] 手动测试核心功能
- [ ] 提交变更
- [ ] 创建 PR

---

## 支持和反馈

如遇到问题：
1. 查看 `docs/architecture/ARCHITECTURE_CHANGES.md`
2. 查看 `docs/architecture/MODULE_GUIDE.md`
3. 提交 Issue

---

**更新日期**: 2026-04-03
**版本**: v3.1
**维护**: 架构团队
**预计迁移完成**: 2026-04-10