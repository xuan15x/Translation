# 项目结构说明

## 📁 完整项目结构（六层架构 v3.0）

```
translation/
├── 📄 README.md                          # 项目主文档
├── 📄 requirements.txt                   # 生产环境依赖
├── 📄 requirements-test.txt              # 测试环境依赖
├── 📄 pytest.ini                         # pytest 配置
├── 📄 .gitignore                         # Git 忽略规则
├── 🚀 启动翻译平台.bat                    # Windows 启动脚本
│
├── 📂 config/                            # 配置管理模块 ⭐
│   ├── __init__.py                       # 配置导出
│   ├── config.py                         # 配置常量定义
│   ├── loader.py                         # 配置加载器
│   ├── checker.py                        # 配置检查器
│   ├── config.example.json               # JSON 配置示例
│   ├── config.example.yaml               # YAML 配置示例
│   └── README.md                         # 模块说明
│
├── 📂 application/                       # 应用层（流程编排）⭐ NEW
│   ├── __init__.py                       # 模块导出
│   ├── translation_facade.py             # 外观模式 ⭐
│   ├── workflow_coordinator.py           # 工作流协调器
│   ├── batch_processor.py                # 批量任务处理器
│   └── result_builder.py                 # 结果构建器
│
├── 📂 domain/                            # 领域层（纯业务逻辑）⭐ NEW
│   ├── __init__.py                       # 模块导出
│   ├── models.py                         # 领域模型
│   ├── services.py                       # 服务接口
│   ├── terminology_service_impl.py       # 术语领域服务 ⭐
│   ├── translation_service_impl.py       # 翻译领域服务 ⭐
│   └── cache_decorators.py               # 缓存装饰器
│
├── 📂 service/                           # 服务层（API 集成）
│   ├── __init__.py                       # 模块导出
│   ├── api_provider.py                   # API 提供商管理 ⭐
│   ├── api_stages.py                     # API 调用阶段
│   ├── translation_history.py            # 翻译历史管理
│   ├── terminology_history.py            # 术语历史管理
│   ├── terminology_version.py            # 术语版本控制
│   └── auto_backup.py                    # 自动备份服务
│
├── 📂 data_access/                       # 数据访问层（仓储/持久化）
│   ├── __init__.py                       # 模块导出
│   ├── repositories.py                   # 仓储实现 ⭐
│   ├── config_persistence.py             # 配置持久化
│   ├── terminology_update.py             # 术语库更新
│   └── fuzzy_matcher.py                  # 模糊匹配算法
│
├── 📂 infrastructure/                    # 基础设施层（DI/日志/工具）
│   ├── __init__.py                       # 模块导出
│   ├── di_container.py                   # 依赖注入容器 ⭐
│   ├── models.py                         # 数据模型 ⭐
│   ├── cache.py                          # 缓存管理（LRU）⭐
│   ├── concurrency_controller.py         # 并发控制器 ⭐
│   ├── log_config.py                     # 日志配置
│   ├── logging_config.py                 # 日志系统
│   ├── log_slice.py                      # 日志切片
│   ├── db_pool.py                        # 数据库连接池
│   ├── performance_monitor.py            # 性能监控
│   ├── progress_estimator.py             # 进度估算
│   ├── prompt_builder.py                 # 提示词构建
│   └── undo_manager.py                   # 撤销/重做管理
│
├── 📂 presentation/                      # 表示层（GUI/CLI）
│   ├── __init__.py                       # 模块导出
│   ├── gui_app.py                        # GUI 主界面 ⭐
│   └── translation.py                    # 程序入口
│
├── 📂 tests/                             # 测试目录
│   ├── conftest.py                       # pytest 夹具配置
│   ├── run_all_tests.py                  # 测试运行脚本
│   ├── test_*.py                         # 各模块单元测试
│   └── data/                             # 测试数据
│       └── .gitkeep
│
├── 📂 scripts/                           # 工具脚本
│   ├── check_config.py                   # 配置检查工具
│   ├── manage_config.py                  # 配置管理工具
│   ├── demo_*.py                         # 功能演示脚本
│   ├── example_ui_translation.py         # UI 翻译示例
│   └── verify_lang_checkbox_state.py     # 语言选择验证
│
├── 📂 docs/                              # 文档目录
│   ├── INDEX.md                          # 文档导航索引
│   ├── README.md                         # 文档说明
│   │
│   ├── 📂 guides/                        # 使用指南
│   │   ├── QUICKSTART.md                 # 快速开始
│   │   ├── BEST_PRACTICES.md             # 最佳实践
│   │   ├── TROUBLESHOOTING.md            # 故障排查
│   │   ├── CONFIG_GUIDE_DETAILED.md      # 详细配置指南 ⭐ NEW
│   │   └── MODEL_CONFIG_GUIDE.md         # 模型配置指南
│   │
│   ├── 📂 architecture/                  # 架构文档
│   │   ├── ARCHITECTURE.md               # 系统架构
│   │   ├── ARCHITECTURE_DESIGN.md        # 架构设计
│   │   └── REFACTORING_SUMMARY.md        # 重构总结
│   │
│   └── 📂 development/                   # 开发指南
│       ├── TESTING_GUIDE.md              # 测试指南
│       ├── PERFORMANCE_OPTIMIZATIONS.md  # 性能优化
│       └── ERROR_HANDLING_GUIDE.md       # 错误处理指南
│
└── 📂 .idea/                             # IDE 配置（已忽略）
    └── ...
```

---

## 🎯 六层架构职责说明

### 第一层：表示层（Presentation Layer）
**位置**: `presentation/`  
**职责**: 用户界面和交互
- **GUI App**: Tkinter 图形界面，提供可视化操作
- **CLI Entry**: 命令行入口（扩展用）
- **关键文件**: `gui_app.py`, `translation.py`

### 第二层：应用层（Application Layer）⭐ NEW
**位置**: `application/`  
**职责**: 流程编排和业务协调，使用外观模式
- **TranslationServiceFacade**: 统一对外接口 ⭐
- **TranslationWorkflowCoordinator**: 翻译流程协调
- **BatchTaskProcessor**: 批量任务处理
- **ResultBuilder**: 结果构建和格式化

### 第三层：领域层（Domain Layer）⭐ NEW
**位置**: `domain/`  
**职责**: 纯业务逻辑，无外部依赖
- **ITerminologyDomainService**: 术语服务接口
- **TerminologyDomainServiceImpl**: 术语服务实现 ⭐
- **ITranslationDomainService**: 翻译服务接口
- **TranslationDomainServiceImpl**: 翻译服务实现 ⭐
- **缓存装饰器**: 透明添加缓存能力

### 第四层：服务层（Service Layer）
**位置**: `service/`  
**职责**: API 集成和外部服务
- **APIProviderManager**: 8 种 API 提供商管理 ⭐
- **APIDraftStage/APIReviewStage**: 双阶段调用
- **TranslationHistory**: SQLite 历史管理
- **TerminologyVersion**: 版本控制和备份

### 第五层：数据访问层（Data Access Layer）
**位置**: `data_access/`  
**职责**: 仓储模式和持久化
- **TerminologyRepository**: 术语库仓储 ⭐
- **ConfigPersistence**: JSON/YAML配置读写
- **FuzzyMatcher**: thefuzz 模糊匹配算法
- **TerminologyUpdate**: 增量更新逻辑

### 第六层：基础设施层（Infrastructure Layer）
**位置**: `infrastructure/`  
**职责**: 通用工具和基础服务
- **DI Container**: 依赖注入容器 ⭐
- **Models**: Config, TaskContext, FinalResult ⭐
- **Cache**: LRU + 内存感知优化 ⭐
- **ConcurrencyController**: 自适应并发控制 ⭐
- **Logging**: 多粒度日志系统
- **PerformanceMonitor**: 性能监控

---

## 🧪 测试体系

### 测试文件组织
```
tests/
├── conftest.py                  # 全局夹具和 mock 配置
├── run_all_tests.py             # 批量运行脚本
├── test_models.py               # 数据模型测试
├── test_config.py               # 配置模块测试
├── test_cache.py                # 缓存测试
├── test_concurrency_controller.py # 并发控制测试
├── test_fuzzy_matcher.py        # 模糊匹配测试
├── test_terminology_manager.py  # 术语库测试
├── test_api_provider.py         # API 提供商测试
├── test_api_stages.py           # API 调用阶段测试
├── test_workflow_orchestrator.py# 工作流编排测试
├── test_gui_app.py              # GUI 测试
├── test_integration.py          # 集成测试
└── test_performance.py          # 性能测试
```

### 运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块
pytest tests/test_terminology_manager.py -v

# 生成覆盖率报告
pytest --cov=translation tests/
```

---

## 🛠️ 工具脚本

### scripts/ 目录用途
- **配置工具**: `check_config.py`, `manage_config.py`
- **演示脚本**: `demo_*.py` (多个功能演示)
- **示例代码**: `example_ui_translation.py`
- **验证工具**: `verify_lang_checkbox_state.py`

### 使用示例
```bash
# 检查配置
python scripts/check_config.py

# 管理配置
python scripts/manage_config.py

# 功能演示
python scripts/demo_performance.py
```

---

## 📚 文档体系

### 文档层次结构
```
docs/
├── INDEX.md                     # 总导航
├── README.md                    # 文档说明
│
├── guides/                      # 使用指南（面向用户）
│   ├── QUICKSTART.md           # 5 分钟上手
│   ├── BEST_PRACTICES.md       # 最佳实践
│   └── TROUBLESHOOTING.md      # 故障排查
│
├── architecture/                # 架构文档（面向开发者）
│   ├── ARCHITECTURE.md         # 系统架构
│   └── REFACTORING_SUMMARY.md  # 重构总结
│
├── development/                 # 开发指南（面向贡献者）
│   ├── TESTING_GUIDE.md        # 测试指南
│   ├── PERFORMANCE_*.md        # 性能优化文档
│   └── ASYNC_*.md              # 异步处理
│
└── api/                         # API 文档（高级用户）
    ├── API_REFERENCE.md        # 完整 API 参考
    └── CONFIG_PERSISTENCE.md   # 配置持久化
```

---

## 🔍 关键文件说明

### ⭐ 核心文件（必须了解）

1. **`business_logic/workflow_orchestrator.py`**
   - 翻译工作流编排器
   - 协调初译、校对、术语查询
   - 支持双阶段翻译流程

2. **`business_logic/terminology_manager.py`**
   - 术语库管理器
   - 6 级性能优化
   - 支持缓存、模糊匹配、增量更新

3. **`infrastructure/models.py`**
   - 核心数据模型
   - Config、TaskContext、FinalResult
   - 所有模块都依赖此文件

4. **`infrastructure/cache.py`**
   - LRU 缓存实现
   - 内存感知优化
   - 术语查询加速关键

5. **`infrastructure/concurrency_controller.py`**
   - 自适应并发控制
   - 基于错误率和延迟动态调整
   - 防止 API 限流

6. **`presentation/gui_app.py`**
   - GUI 主界面
   - 批量处理逻辑
   - 动态分批、信号量控制

---

## 📊 数据流向

```
用户操作 (GUI)
    ↓
presentation/gui_app.py
    ↓
business_logic/workflow_orchestrator.py
    ├─→ business_logic/terminology_manager.py (术语查询)
    ├─→ business_logic/api_stages.py (API 调用)
    └─→ service/translation_history.py (历史记录)
    ↓
infrastructure/
    ├─→ cache.py (缓存)
    ├─→ concurrency_controller.py (并发控制)
    └─→ models.py (数据模型)
    ↓
data_access/
    ├─→ fuzzy_matcher.py (模糊匹配)
    └─→ config_persistence.py (配置存储)
    ↓
输出结果 (Excel)
```

---

## 🎯 项目优化重点

### 已完成的优化（v2.1.0）

1. **术语查询优化** - 6 级优化流程
   - 空库检查 → 精确缓存 → 短文本缓存 → 预过滤 → 智能分级 → 结果缓存
   - 性能提升：70-84%

2. **批量处理优化** - 7 项改进措施
   - 动态分批 → 预分配内存 → 增强进度 → 信号量控制
   - 性能提升：38-44%

3. **缓存管理优化** - 内存感知
   - 内存限制 → 实时估算 → 双重淘汰
   - 内存降低：49-68%

4. **并发控制优化** - 多维调整
   - 错误率监控 → 延迟感知 → 快速降级
   - 稳定性提升：85%

### 文件清理

**已删除的冗余文件**:
- ❌ `simple_test.py` - 临时测试
- ❌ `verify_performance.py` - 性能验证（已移至 docs）
- ❌ `scripts/auto_fix_tests.py` - 一次性修复脚本
- ❌ `scripts/fix_*.py` - 导入修复脚本
- ❌ `scripts/check_*.py` - 检查脚本（功能已集成）
- ❌ `scripts/generate_docs.py` - 文档生成（手动维护）

**保留的核心脚本**:
- ✅ `scripts/check_config.py` - 配置检查
- ✅ `scripts/manage_config.py` - 配置管理
- ✅ `scripts/demo_*.py` - 功能演示
- ✅ `scripts/example_ui_translation.py` - 示例代码

---

## 💡 最佳实践

### 开发建议
1. **模块化**: 每个模块职责单一，易于测试
2. **异步优先**: 使用 asyncio 提升并发性能
3. **缓存策略**: 热点数据优先缓存
4. **日志完善**: 关键操作记录日志
5. **测试覆盖**: 核心功能必须有单元测试

### 性能调优
1. **术语库大小**: 保持 <10000 条，定期清理
2. **并发设置**: 初始 8-10，最大 15
3. **缓存容量**: 2000-3000 条目
4. **批次大小**: 根据语言数量动态调整
5. **GC 频率**: 每 5 批次执行一次

---

**更新日期**: 2026-03-31  
**版本**: v2.1.0  
**状态**: ✅ 项目结构已优化完成
