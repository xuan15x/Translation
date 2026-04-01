# 项目结构说明 - v3.0 六层架构

## 📁 完整目录结构

```
translation/
├── config/                     # 配置管理模块
│   ├── __init__.py            # 配置导出
│   ├── config.py              # 配置常量定义
│   ├── checker.py             # 配置验证器
│   ├── loader.py              # 配置加载器
│   ├── config.example.json    # JSON 配置示例
│   ├── config.example.yaml    # YAML 配置示例
│   └── README.md              # 配置说明
│
├── presentation/               # 表示层 (Presentation Layer)
│   ├── __init__.py            # 模块导出
│   ├── gui_app.py             # GUI 主界面 (405 行精简版)
│   └── translation.py         # 程序启动入口
│
├── application/                # 应用层 (Application Layer) ⭐ NEW
│   ├── __init__.py            # 模块导出
│   ├── translation_facade.py  # 外观模式 - 简化 API
│   ├── workflow_coordinator.py# 工作流协调器
│   ├── batch_processor.py     # 批量处理器
│   └── result_builder.py      # 结果构建器
│
├── domain/                     # 领域层 (Domain Layer) ⭐ NEW
│   ├── __init__.py            # 模块导出
│   ├── models.py              # 领域模型
│   ├── services.py            # 服务接口
│   ├── terminology_service_impl.py  # 术语服务实现
│   ├── translation_service_impl.py  # 翻译服务实现
│   └── cache_decorators.py    # 缓存装饰器
│
├── service/                    # 服务层 (Service Layer)
│   ├── __init__.py            # 模块导出
│   ├── api_provider.py        # API 提供商管理
│   ├── api_stages.py          # API 调用阶段
│   ├── translation_history.py # 翻译历史管理
│   └── auto_backup.py         # 自动备份服务
│
├── data_access/                # 数据访问层 (Data Access Layer)
│   ├── __init__.py            # 模块导出
│   ├── repositories.py        # 仓储实现 ⭐ NEW
│   ├── excel_sqlite_persistence.py  # Excel-SQLite持久化
│   ├── config_persistence.py  # 配置持久化
│   ├── terminology_update.py  # 术语更新
│   ├── fuzzy_matcher.py       # 模糊匹配引擎
│   └── global_persistence_manager.py # 全局持久化管理器
│
├── infrastructure/             # 基础设施层 (Infrastructure Layer)
│   ├── __init__.py            # 模块导出
│   ├── di_container.py        # 依赖注入容器 ⭐ NEW
│   ├── models.py              # 基础数据模型
│   ├── exceptions.py          # 统一异常处理
│   ├── log_config.py          # 日志配置
│   ├── concurrency_controller.py  # 并发控制器
│   ├── cache.py               # LRU 缓存
│   ├── prompt_builder.py      # 提示词构建器
│   ├── performance_monitor.py # 性能监控器
│   ├── progress_estimator.py  # 进度估算器
│   ├── conflict_resolver.py   # 冲突解决器
│   ├── undo_manager.py        # 撤销管理器
│   ├── db_pool.py             # 数据库连接池
│   └── memory_manager.py      # 内存管理器
│
├── scripts/                    # 工具脚本
│   ├── start_new_architecture.py    # 新架构启动脚本 ⭐ NEW
│   ├── example_new_architecture.py  # 新架构使用示例 ⭐ NEW
│   ├── demo_advanced_features.py    # 高级功能演示
│   ├── demo_performance.py          # 性能演示
│   ├── demo_multi_language.py       # 多语言演示
│   └── ...其他工具脚本
│
├── tests/                      # 测试文件
│   ├── conftest.py            # pytest 配置
│   ├── test_api_provider.py   # API 测试
│   ├── test_terminology.py    # 术语测试
│   ├── test_translation.py    # 翻译测试
│   └── ...其他测试文件
│
├── docs/                       # 文档目录
│   ├── INDEX.md               # 文档总索引
│   ├── architecture/          # 架构文档
│   ├── application/           # 应用层文档 ⭐ NEW
│   ├── domain/                # 领域层文档 ⭐ NEW
│   ├── guides/                # 使用指南
│   └── ...其他文档
│
├── .gitignore                  # Git 忽略文件
├── LICENSE                     # 开源协议
├── README.md                   # 项目说明 (v3.0)
├── requirements.txt            # 依赖列表
├── requirements-test.txt       # 测试依赖
├── pytest.ini                  # pytest 配置
├── start_new_architecture.py   # 快速启动脚本 ⭐ NEW
└── 启动翻译平台.bat             # Windows 启动脚本
```

---

## 🏗️ 六层架构说明

### 1. **表示层 (Presentation Layer)**
- **职责**: 用户界面交互
- **核心文件**: `gui_app.py`, `translation.py`
- **特点**: 精简至 405 行，使用依赖注入

### 2. **应用层 (Application Layer)** ⭐ NEW
- **职责**: 流程编排和业务协调
- **核心组件**:
  - `TranslationServiceFacade` - 外观模式，简化 API
  - `TranslationWorkflowCoordinator` - 工作流协调
  - `BatchTaskProcessor` - 批量处理
  - `ResultBuilder` - 结果构建

### 3. **领域层 (Domain Layer)** ⭐ NEW
- **职责**: 纯业务逻辑，无外部依赖
- **核心组件**:
  - `TerminologyDomainService` - 术语领域服务
  - `TranslationDomainServiceImpl` - 翻译领域服务
  - `CachedTerminologyService` - 缓存装饰器

### 4. **服务层 (Service Layer)**
- **职责**: 外部服务集成
- **核心组件**:
  - `APIProviderManager` - API 提供商管理
  - `TranslationHistoryManager` - 翻译历史
  - `AutoBackupManager` - 自动备份

### 5. **数据访问层 (Data Access Layer)**
- **职责**: 数据持久化和仓储
- **核心组件**:
  - `TerminologyRepository` - 术语仓储 ⭐ NEW
  - `ConfigPersistence` - 配置持久化
  - `FuzzyMatcher` - 模糊匹配

### 6. **基础设施层 (Infrastructure Layer)**
- **职责**: 技术支撑和工具
- **核心组件**:
  - `DependencyContainer` - 依赖注入 ⭐ NEW
  - `LogManager` - 日志管理
  - `AdaptiveConcurrencyController` - 自适应并发控制
  - `PerformanceMonitor` - 性能监控

---

## 🎯 核心设计原则

### 1. **单一职责原则 (SRP)**
每个类只负责一项职责

### 2. **依赖倒置原则 (DIP)**
依赖抽象接口，而非具体实现

### 3. **开闭原则 (OCP)**
对扩展开放，对修改封闭

### 4. **接口隔离原则 (ISP)**
使用多个专用接口

---

## 📊 代码统计

| 层级 | 文件数 | 代码行数 | 占比 |
|------|--------|---------|------|
| 表示层 | 3 | ~450 | 22% |
| 应用层 | 4 | ~400 | 20% |
| 领域层 | 5 | ~350 | 17% |
| 服务层 | 4 | ~300 | 15% |
| 数据访问层 | 6 | ~300 | 15% |
| 基础设施层 | 14 | ~200 | 11% |
| **总计** | **36** | **~2000** | **100%** |

---

## 🔧 快速开始

### 方式 1: 使用启动脚本
```bash
python start_new_architecture.py
```

### 方式 2: 直接运行
```bash
python presentation/translation.py
```

### 方式 3: 代码调用
```python
from infrastructure.di_container import initialize_container

container = initialize_container(
    api_client=client,
    draft_prompt=DRAFT_PROMPT,
    review_prompt=REVIEW_PROMPT
)

facade = container.get('translation_facade')
result = await facade.translate_file(...)
```

---

## 📝 版本历史

- **v3.0** (当前): 六层架构，完全重构
- **v2.x**: 五层架构（已废弃）
- **v1.x**: 单体架构（已废弃）

---

**最后更新**: 2026-04-01  
**维护者**: Translation Team
