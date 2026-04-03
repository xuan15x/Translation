# AI 智能翻译工作台 v3.1 - 六层分层架构说明

## 📑 目录

- [🏗️ 完整系统架构图](#️-完整系统架构图)
  - [系统层次架构（六层设计）](#系统层次架构六层设计)
- [🔄 核心数据流向图](#核心数据流向图)
  - [完整翻译流程数据流](#完整翻译流程数据流)
- [📦 模块依赖关系图](#模块依赖关系图)
- [📁 项目结构](#项目结构)
- [🔧 模块职责说明](#模块职责说明)
- [🎯 解耦优势](#解耦优势)
- [📊 性能优化](#性能优化)

---

## 🏗️ 完整系统架构图

### 系统层次架构（六层设计）

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Presentation Layer (表示层)                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                     gui_app.py (GUI 应用)                      │    │
│  │  - TranslationApp 主界面                                      │    │
│  │  - 文件选择 / 语言配置 / 提示词编辑                            │    │
│  │  - 任务执行控制 / 进度显示                                    │    │
│  │  - 日志实时展示                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  translation.py (程序入口)                     │    │
│  │  - 应用启动入口                                              │    │
│  │  - 初始化配置和依赖                                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                 error_handler.py (错误处理)                    │    │
│  │  - 全局异常处理                                              │    │
│  │  - 错误 UI 提示                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                ↑ ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       Application Layer (应用层)                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              translation_facade.py (外观模式)                 │    │
│  │  - TranslationServiceFacade                                  │    │
│  │  - 简化的 API 接口                                            │    │
│  │  - 一行代码完成复杂翻译                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              workflow_coordinator.py (工作流协调器)            │    │
│  │  - TranslationWorkflowCoordinator                            │    │
│  │  - 协调领域服务执行                                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                batch_processor.py (批量处理器)                │    │
│  │  - BatchTaskProcessor                                        │    │
│  │  - 并发控制和进度跟踪                                         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │               result_builder.py (结果构建器)                   │    │
│  │  - 翻译结果组装                                              │    │
│  │  - 格式化和导出                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │             enhanced_translator.py (增强翻译器)               │    │
│  │  - 高级翻译功能                                              │    │
│  │  - 多语言支持                                                │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                ↑ ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         Domain Layer (领域层)                        │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   models.py (领域模型)                        │    │
│  │  - 核心业务实体                                              │    │
│  │  - 值对象和聚合根                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  services.py (服务接口)                        │    │
│  │  - 领域服务接口定义                                          │    │
│  │  - 业务规则契约                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │         terminology_service_impl.py (术语领域服务)             │    │
│  │  - TerminologyDomainService                                  │    │
│  │  - 纯业务逻辑（无外部依赖）                                    │    │
│  │  - find_match() / save_term()                                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │        translation_service_impl.py (翻译领域服务)             │    │
│  │  - TranslationDomainServiceImpl                              │    │
│  │  - translate() / proofread()                                 │    │
│  │  - 集成术语服务和 API 调用                                     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │            cache_decorators.py (缓存装饰器)                   │    │
│  │  - CachedTerminologyService                                  │    │
│  │  - LRU 缓存装饰器                                             │    │
│  │  - 性能提升 100 倍                                             │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                ↑ ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         Service Layer (服务层)                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   api_provider.py (API 服务)                   │    │
│  │  - DeepSeekClient / OpenAIClient                             │    │
│  │  - API 调用封装 / 错误处理                                    │    │
│  │  - 响应解析和格式化                                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  api_stages.py (API 阶段)                      │    │
│  │  - APIDraftStage / APIReviewStage                            │    │
│  │  - 双阶段 API 调用                                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              translation_history.py (翻译历史服务)            │    │
│  │  - 历史记录管理                                              │    │
│  │  - 统计信息生成                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │               auto_backup.py (自动备份服务)                    │    │
│  │  - AutoBackupManager                                         │    │
│  │  - 定时备份策略                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │          terminology_version.py (版本控制服务)                 │    │
│  │  - TerminologyVersionController                              │    │
│  │  - Git 版本控制集成                                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                ↑ ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      Data Access Layer (数据访问层)                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │               repositories.py (仓储实现)                       │    │
│  │  - TerminologyRepository                                     │    │
│  │  - 术语库 CRUD 操作                                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              config_persistence.py (配置持久化)               │    │
│  │  - JSON/YAML配置文件读写                                     │    │
│  │  - 配置验证和迁移                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │        excel_sqlite_persistence.py (Excel/SQLite持久化)       │    │
│  │  - Excel 文件读写                                            │    │
│  │  - SQLite 数据存储                                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              terminology_update.py (术语更新服务)             │    │
│  │  - TerminologyImporter / TerminologyUpdater                  │    │
│  │  - 批量导入和增量更新                                        │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                fuzzy_matcher.py (模糊匹配引擎)               │    │
│  │  - FuzzyMatcher                                              │    │
│  │  - thefuzz 字符串相似度匹配                                  │    │
│  │  - 多进程加速支持                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                ↑ ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer (基础设施层)                  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  📦 cache/ - 缓存子模块                                       │    │
│  │  - cache.py (LRU 缓存)                                       │    │
│  │  - unified_cache.py (统一缓存接口)                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  ⚙️ config/ - 配置子模块                                      │    │
│  │  - config.py / loader.py / checker.py                        │    │
│  │  - model_manager.py / model_providers.py                     │    │
│  │  - constants.py / smart_config.py                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  🗄️ database/ - 数据库子模块                                  │    │
│  │  - db_pool.py (连接池)                                       │    │
│  │  - repositories.py (仓储基类)                                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  💉 di/ - 依赖注入子模块                                      │    │
│  │  - di_container.py (DI 容器)                                 │    │
│  │  - 服务注册和解析                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  📝 logging/ - 日志子模块                                     │    │
│  │  - log_config.py / logging_config.py                         │    │
│  │  - gui_log_controller.py / log_slice.py                      │    │
│  │  - formatter.py / slice.py                                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  🛠️ utils/ - 工具子模块                                       │    │
│  │  - concurrency_controller.py (并发控制)                      │    │
│  │  - performance_monitor.py (性能监控)                         │    │
│  │  - progress_estimator.py (进度估算)                          │    │
│  │  - conflict_resolver.py (冲突解决)                           │    │
│  │  - undo_manager.py (撤销管理)                                │    │
│  │  - health_check.py / memory_manager.py                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↑ ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  📦 models/ - 数据模型子模块 (迁移至 domain/models.py)         │    │
│  │  - models.py (向后兼容)                                      │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 核心数据流向图

### 完整翻译流程数据流

```
用户操作 (GUI)
    │
    ├─→ 1. 选择文件和语言
    │      ↓
    ├─→ 2. 加载配置 (Config)
    │      ↓
    │      ├─→ 从 config.json 读取
    │      ├─→ 验证配置参数 (ValidationError)
    │      └─→ 初始化日志系统
    │
    ├─→ 3. 初始化引擎
    │      ↓
    │      ├─→ DI Container 注册服务
    │      ├─→ TerminologyDomainService 加载术语库
    │      │     ├─→ Repository 读取数据
    │      │     ├─→ 构建内存数据库
    │      │     └─→ 启动缓存
    │      │
    │      ├─→ WorkflowCoordinator 初始化
    │      │     ├─→ 获取并发控制器
    │      │     ├─→ 初始化 API 客户端
    │      │     └─→ 准备提示词构建器
    │      │
    │      └─→ 性能监控启动 (可选)
    │
    ├─→ 4. 任务批处理
    │      ↓
    │      ┌──────────────────────────────────────┐
    │      │  For each task in batch:             │
    │      │   ┌────────────────────────────┐     │
    │      │   │ 4.1 术语匹配               │     │
    │      │   │    ├─→ TerminologyService  │     │
    │      │   │    │   ├─→ 查缓存         │     │
    │      │   │    │   ├─→ 模糊匹配       │     │
    │      │   │    │   └─→ 返回最佳匹配   │     │
    │      │   │    └─→ Cache 更新          │     │
    │      │   └────────────────────────────┘     │
    │      │             ↓                        │
    │      │   ┌────────────────────────────┐     │
    │      │   │ 4.2 工作流编排             │     │
    │      │   │    WorkflowCoordinator     │     │
    │      │   │    ├─→ LocalHit (本地命中) │     │
    │      │   │    │   └─→ 使用 TM 建议      │     │
    │      │   │    ├─→ APIDraft (初译)     │     │
    │      │   │    │   ├─→ 构建提示词     │     │
    │      │   │    │   ├─→ API 调用        │     │
    │      │   │    │   ├─→ 解析响应       │     │
    │      │   │    │   └─→ 重试机制       │     │
    │      │   │    └─→ APIReview (校对)   │     │
    │      │   │        ├─→ 优化翻译       │     │
    │      │   │        └─→ 质量检查       │     │
    │      │   └────────────────────────────┘     │
    │      │             ↓                        │
    │      │   ┌────────────────────────────┐     │
    │      │   │ 4.3 更新术语库             │     │
    │      │   │    ├─→ Repository 写入    │     │
    │      │   │    ├─→ 记录变更历史       │     │
    │      │   │    └─→ 更新缓存           │     │
    │      │   └────────────────────────────┘     │
    │      │             ↓                        │
    │      │   ┌────────────────────────────┐     │
    │      │   │ 4.4 并发控制调整           │     │
    │      │   │    ├─→ 记录成功率         │     │
    │      │   │    ├─→ 动态调整并发数     │     │
    │      │   │    └─→ 冷却机制触发       │     │
    │      │   └────────────────────────────┘     │
    │      └──────────────────────────────────────┘
    │
    ├─→ 5. 结果输出
    │      ↓
    │      ├─→ ResultBuilder 构建结果
    │      ├─→ 转换为 DataFrame
    │      ├─→ 保存为 Excel 文件
    │      └─→ 显示完成消息
    │
    └─→ 6. 清理资源
           ↓
           ├─→ 关闭领域服务
           ├─→ 停止性能监控
           ├─→ 日志系统刷新
           └─→ GUI 状态恢复
```

---

## 📦 模块依赖关系图

```
                    ┌─────────────────┐
                    │   gui_app.py    │
                    │  (Presentation) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ↓              ↓              ↓
     ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
     │ translation │ │workflow_    │ │  error_      │
     │   _facade   │ │coordinator  │ │  handler     │
     └──────┬──────┘ └──────┬──────┘ └──────────────┘
            │               │
     ┌──────┴───────────────┴──────┐
     │                             │
     ↓                             ↓
┌──────────────┐          ┌──────────────┐
│  Domain      │          │   Service    │
│  Layer       │          │   Layer      │
│  (纯业务逻辑) │          │  (API集成)   │
└──────┬───────┘          └──────┬───────┘
       │                         │
       └──────────┬──────────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
     ↓            ↓            ↓
┌─────────┐ ┌──────────┐ ┌────────────┐
│Data     │ │Infra-    │ │  Config    │
│Access   │ │structure │ │  Files     │
│Layer    │ │  Layer   │ │            │
└─────────┘ └──────────┘ └────────────┘

Infrastructure Layer 子模块:
┌─────────────────────────────────────────────────┐
│  ┌───────┐ ┌──────┐ ┌──────┐ ┌────┐ ┌────┐    │
│  │cache/ │ │config│ │database│ │ di │ │log │    │
│  │       │ │      │ │      │ │    │ │ging│    │
│  └───────┘ └──────┘ └──────┘ └────┘ └────┘    │
│  ┌───────────────────────────────────────┐    │
│  │            utils/                      │    │
│  └───────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘

依赖方向: Presentation → Application → Domain → Service → Data Access
                                                    ↓
                                              Infrastructure
```

---

## 📁 项目结构

```
translation/
├── 📄 README.md                          # 项目主文档
├── 📄 requirements.txt                   # 生产环境依赖
├── 📄 requirements-test.txt              # 测试环境依赖
├── 📄 pytest.ini                         # pytest 配置
├── 📄 mypy.ini                           # 类型检查配置
├── 📄 .pre-commit-config.yaml            # 代码质量钩子
├── 📄 .gitignore                         # Git 忽略规则
├── 🚀 启动翻译平台.bat                    # Windows 启动脚本
├── 🧪 run_tests.bat                      # 测试运行脚本
│
├── 📂 presentation/                      # 表示层（GUI/CLI）
│   ├── __init__.py                       # 模块导出
│   ├── gui_app.py                        # GUI 主界面 ⭐
│   ├── translation.py                    # 程序入口
│   └── error_handler.py                  # 错误处理
│
├── 📂 application/                       # 应用层（流程编排）
│   ├── __init__.py                       # 模块导出
│   ├── translation_facade.py             # 外观模式 ⭐
│   ├── workflow_coordinator.py           # 工作流协调器
│   ├── batch_processor.py                # 批量任务处理器
│   ├── result_builder.py                 # 结果构建器
│   └── enhanced_translator.py            # 增强翻译器
│
├── 📂 domain/                            # 领域层（纯业务逻辑）
│   ├── __init__.py                       # 模块导出
│   ├── models.py                         # 领域模型 ⭐
│   ├── services.py                       # 服务接口
│   ├── terminology_service_impl.py       # 术语领域服务 ⭐
│   ├── translation_service_impl.py       # 翻译领域服务 ⭐
│   └── cache_decorators.py               # 缓存装饰器
│
├── 📂 service/                           # 服务层（API 集成）
│   ├── __init__.py                       # 模块导出
│   ├── api_provider.py                   # API 提供商管理 ⭐
│   ├── api_stages.py                     # API 调用阶段
│   ├── api_stage_base.py                 # API 阶段基类
│   ├── translation_history.py            # 翻译历史管理
│   ├── terminology_history.py            # 术语历史管理
│   ├── terminology_version.py            # 术语版本控制
│   ├── auto_backup.py                    # 自动备份服务
│   ├── session_config.py                 # 会话配置
│   ├── version_history.py                # 版本历史
│   └── advanced_translation.py           # 高级翻译功能
│
├── 📂 data_access/                       # 数据访问层（仓储/持久化）
│   ├── __init__.py                       # 模块导出
│   ├── repositories.py                   # 仓储实现 ⭐
│   ├── config_persistence.py             # 配置持久化
│   ├── terminology_update.py             # 术语库更新
│   ├── fuzzy_matcher.py                  # 模糊匹配算法
│   ├── excel_sqlite_persistence.py       # Excel/SQLite持久化
│   ├── csv_json_persistence.py           # CSV/JSON持久化
│   └── global_persistence_manager.py     # 全局持久化管理器
│
├── 📂 infrastructure/                    # 基础设施层（6个子模块）⭐ NEW
│   ├── __init__.py                       # 模块导出
│   │
│   ├── 📂 cache/                         # 缓存子模块
│   │   ├── __init__.py
│   │   ├── cache.py                      # LRU 缓存实现
│   │   └── unified_cache.py              # 统一缓存接口
│   │
│   ├── 📂 config/                        # 配置子模块
│   │   ├── __init__.py
│   │   ├── config.py                     # 配置常量定义
│   │   ├── loader.py                     # 配置加载器
│   │   ├── checker.py                    # 配置检查器
│   │   ├── constants.py                  # 系统常量
│   │   ├── model_manager.py              # 模型管理器
│   │   ├── model_providers.py            # 模型提供商配置
│   │   └── smart_config.py               # 智能配置
│   │
│   ├── 📂 database/                      # 数据库子模块
│   │   ├── __init__.py
│   │   ├── db_pool.py                    # 数据库连接池
│   │   └── repositories.py               # 仓储基类
│   │
│   ├── 📂 di/                            # 依赖注入子模块
│   │   ├── __init__.py
│   │   └── di_container.py               # DI 容器 ⭐
│   │
│   ├── 📂 logging/                       # 日志子模块
│   │   ├── __init__.py
│   │   ├── log_config.py                 # 日志配置
│   │   ├── logging_config.py             # 日志系统
│   │   ├── gui_log_controller.py         # GUI 日志控制器
│   │   ├── log_slice.py                  # 日志切片
│   │   ├── formatter.py                  # 格式化器
│   │   └── slice.py                      # 切片工具
│   │
│   ├── 📂 utils/                         # 工具子模块
│   │   ├── __init__.py
│   │   ├── concurrency_controller.py     # 并发控制器 ⭐
│   │   ├── performance_monitor.py        # 性能监控
│   │   ├── progress_estimator.py         # 进度估算
│   │   ├── conflict_resolver.py          # 冲突解决
│   │   ├── undo_manager.py               # 撤销管理
│   │   ├── health_check.py               # 健康检查
│   │   ├── memory_manager.py             # 内存管理
│   │   ├── config_metrics.py             # 配置指标
│   │   └── utils.py                      # 通用工具
│   │
│   ├── models.py                         # 数据模型 (向后兼容)
│   ├── exceptions.py                     # 统一异常处理 ⭐
│   ├── prompt_builder.py                 # 提示词构建
│   ├── cache.py                          # 缓存 (向后兼容)
│   ├── concurrency_controller.py         # 并发控制 (向后兼容)
│   └── ...                               # 其他向后兼容文件
│
├── 📂 tests/                             # 测试目录
│   ├── conftest.py                       # pytest 夹具配置
│   ├── run_all_tests.py                  # 测试运行脚本
│   ├── test_*.py                         # 各模块单元测试
│   └── data/                             # 测试数据
│
├── 📂 scripts/                           # 工具脚本
│   ├── check_config.py                   # 配置检查工具
│   ├── manage_config.py                  # 配置管理工具
│   ├── demo_*.py                         # 功能演示脚本
│   └── ...
│
├── 📂 docs/                              # 文档目录
│   ├── INDEX.md                          # 文档导航索引
│   ├── README.md                         # 文档说明
│   ├── guides/                           # 使用指南
│   ├── architecture/                     # 架构文档
│   ├── development/                      # 开发指南
│   └── api/                              # API 文档
│
└── 📂 config/                            # 配置文件 (已迁移至 infrastructure/config/)
    └── ...                               # 保留用于向后兼容
```

---

## 🔧 模块职责说明

### 1. **Presentation Layer (表示层)**

#### `gui_app.py` - GUI 主界面
- **TranslationApp**: 主应用程序界面
- 文件选择、语言配置、提示词编辑
- 任务执行控制和进度显示
- 异步任务调度和日志集成

#### `translation.py` - 程序入口
- 应用启动入口
- 初始化配置和依赖
- 错误处理和资源清理

#### `error_handler.py` - 错误处理
- 全局异常处理
- 错误 UI 提示
- 用户友好的错误信息

### 2. **Application Layer (应用层)**

#### `translation_facade.py` - 外观模式
- **TranslationServiceFacade**: 统一对外接口 ⭐
- 简化调用流程
- 提供高级 API，一行代码完成复杂翻译

#### `workflow_coordinator.py` - 工作流协调器
- **TranslationWorkflowCoordinator**: 翻译流程协调
- 协调初译、校对、术语查询
- 支持双阶段翻译流程

#### `batch_processor.py` - 批量处理器
- **BatchTaskProcessor**: 批量任务处理
- 动态分批、预分配内存
- 并发控制和进度跟踪

#### `result_builder.py` - 结果构建器
- 翻译结果组装
- 格式化和导出
- 统计信息生成

#### `enhanced_translator.py` - 增强翻译器
- 高级翻译功能
- 多语言支持
- 特殊场景处理

### 3. **Domain Layer (领域层)**

#### `models.py` - 领域模型
- **Config**: 系统配置类，管理所有 API 和运行时参数
- **TaskContext**: 任务上下文，封装单个翻译任务的所有信息
- **StageResult**: 阶段执行结果，用于各处理阶段之间的数据传递
- **FinalResult**: 最终翻译结果，包含完整的翻译信息和状态

#### `services.py` - 服务接口
- **ITerminologyDomainService**: 术语服务接口
- **ITranslationDomainService**: 翻译服务接口
- 业务规则契约

#### `terminology_service_impl.py` - 术语领域服务
- **TerminologyDomainServiceImpl**: 术语服务实现 ⭐
- 6 级性能优化
- 支持缓存、模糊匹配、增量更新
- 纯业务逻辑，无外部依赖

#### `translation_service_impl.py` - 翻译领域服务
- **TranslationDomainServiceImpl**: 翻译服务实现 ⭐
- translate() / proofread() 双阶段翻译
- 集成术语服务和 API 调用
- 纯业务逻辑，无外部依赖

#### `cache_decorators.py` - 缓存装饰器
- **CachedTerminologyService**: 术语缓存装饰器
- LRU 缓存装饰器
- 性能提升 100 倍

### 4. **Service Layer (服务层)**

#### `api_provider.py` - API 服务
- **APIProviderManager**: 8 种 API 提供商管理 ⭐
- DeepSeekClient / OpenAIClient
- API 调用封装 / 错误处理
- 响应解析和格式化

#### `api_stages.py` - API 阶段
- **APIDraftStage**: 初译阶段，调用 API 生成初始翻译
- **APIReviewStage**: 校对阶段，优化初译结果
- 统一的 API 调用接口和重试机制

#### `translation_history.py` - 翻译历史服务
- 历史记录管理
- 统计信息生成
- SQLite 持久化

#### `auto_backup.py` - 自动备份服务
- **AutoBackupManager**: 自动备份管理
- 定时备份策略
- 备份恢复

#### `terminology_version.py` - 版本控制服务
- **TerminologyVersionController**: 版本控制
- Git 版本控制集成
- 版本比较和回滚

### 5. **Data Access Layer (数据访问层)**

#### `repositories.py` - 仓储实现
- **TerminologyRepository**: 术语库仓储 ⭐
- 术语库 CRUD 操作
- 查询优化和缓存

#### `config_persistence.py` - 配置持久化
- JSON/YAML 配置文件读写
- 配置验证和迁移
- 配置版本管理

#### `excel_sqlite_persistence.py` - Excel/SQLite持久化
- Excel 文件读写
- SQLite 数据存储
- 批量导入导出

#### `terminology_update.py` - 术语更新服务
- **TerminologyImporter**: 术语导入
- **TerminologyUpdater**: 术语更新
- 批量导入和增量更新

#### `fuzzy_matcher.py` - 模糊匹配引擎
- **FuzzyMatcher**: 模糊匹配
- thefuzz 字符串相似度匹配
- 多进程加速支持

### 6. **Infrastructure Layer (基础设施层)** ⭐ NEW

Infrastructure 层已拆分为 **6 个子模块**，每个子模块职责明确：

#### 📦 `cache/` - 缓存子模块
- **cache.py**: LRU 缓存实现
  - LRUCache: LRU 缓存
  - TerminologyCache: 术语缓存
  - 内存限制和过期清理
- **unified_cache.py**: 统一缓存接口
  - 统一缓存 API
  - 多缓存实例管理

#### ⚙️ `config/` - 配置子模块
- **config.py**: 配置常量定义
- **loader.py**: 配置加载器
  - JSON/YAML 配置加载
  - 配置验证
- **checker.py**: 配置检查器
  - 配置完整性检查
  - 配置问题报告
- **constants.py**: 系统常量
- **model_manager.py**: 模型管理器
  - 模型配置管理
  - 模型切换
- **model_providers.py**: 模型提供商配置
  - 多模型提供商支持
  - API Key 管理
- **smart_config.py**: 智能配置
  - 自动配置优化
  - 配置推荐

#### 🗄️ `database/` - 数据库子模块
- **db_pool.py**: 数据库连接池
  - 连接池管理
  - 连接复用
- **repositories.py**: 仓储基类
  - 仓储通用接口
  - CRUD 基类实现

#### 💉 `di/` - 依赖注入子模块
- **di_container.py**: DI 容器 ⭐
  - 服务注册和解析
  - 依赖注入
  - 生命周期管理

#### 📝 `logging/` - 日志子模块
- **log_config.py**: 日志配置
  - ModuleLoggerMixin: 日志混入
  - LogCategory: 日志分类
- **logging_config.py**: 日志系统
  - 全局日志配置
  - 日志级别管理
- **gui_log_controller.py**: GUI 日志控制器
  - GUI 日志输出
  - 日志过滤
- **log_slice.py**: 日志切片
  - 日志切片分析
  - 日志统计
- **formatter.py**: 格式化器
  - ColorFormatter: 彩色控制台
  - 日志格式化
- **slice.py**: 切片工具
  - 日志切片工具

#### 🛠️ `utils/` - 工具子模块
- **concurrency_controller.py**: 并发控制器 ⭐
  - AdaptiveConcurrencyController
  - 自适应并发度调整
  - 冷却机制和成功累积策略
- **performance_monitor.py**: 性能监控
  - PerformanceMonitor
  - CPU/内存/磁盘/网络监控
  - 性能告警和统计
- **progress_estimator.py**: 进度估算
  - ProgressEstimator
  - ETA 剩余时间估算
  - 速度统计和趋势分析
- **conflict_resolver.py**: 冲突解决
  - ConflictResolver
  - 4 种冲突类型检测
  - 6 种解决策略
- **undo_manager.py**: 撤销管理
  - UndoManager
  - 操作历史记录
  - 撤销/重做功能
- **health_check.py**: 健康检查
  - 系统健康检查
  - 依赖服务检查
- **memory_manager.py**: 内存管理
  - 内存监控
  - 内存优化
- **config_metrics.py**: 配置指标
  - 配置使用统计
  - 配置性能指标
- **utils.py**: 通用工具
  - 通用工具函数
  - 辅助方法

---

## 🎯 解耦优势

### 1. **单一职责原则**
每个模块只负责一个明确的业务领域，代码更易理解和维护。

### 2. **依赖关系清晰**
模块间通过明确定义的接口通信，降低耦合度。

### 3. **易于测试**
独立的模块可以单独进行单元测试，提高测试覆盖率。

### 4. **可扩展性**
- 新增功能只需修改或添加相关模块
- 可以轻松替换某个模块而不影响其他部分
- 例如：更换匹配算法只需修改 `data_access/fuzzy_matcher.py`

### 5. **代码复用**
核心逻辑（如术语管理、并发控制）可以在其他项目中复用。

### 6. **团队协作**
不同开发者可以并行开发不同模块，减少冲突。

### 7. **Infrastructure 子模块化优势** ⭐ NEW
- **清晰职责**: 6 个子模块各司其职
- **易于维护**: 模块独立演进
- **灵活扩展**: 可按需添加新子模块
- **降低复杂度**: 每个子模块职责单一

---

## 🔄 数据流向

```
GUI App (presentation/gui_app.py)
    ↓
加载配置 → Infrastructure/config/
    ↓
初始化引擎 → DI Container 注册服务
    ↓
应用层 → Application/translation_facade.py
    ↓
工作流协调 → Application/workflow_coordinator.py
    ├─→ Domain/terminology_service_impl.py (术语查询)
    ├─→ Service/api_stages.py (API 调用)
    └─→ Service/translation_history.py (历史记录)
    ↓
数据访问 → Data Access/repositories.py
    ├─→ Infrastructure/cache/ (缓存)
    ├─→ Infrastructure/utils/concurrency_controller.py (并发控制)
    └─→ Infrastructure/logging/ (日志)
    ↓
输出结果 (Excel)
```

## 🚀 运行方式

直接运行主入口文件：
```bash
python presentation/translation.py
```

或使用启动脚本：
```bash
启动翻译平台.bat
```

## 📝 依赖项

确保安装以下依赖：
```bash
pip install pandas openai thefuzz tkinter
```

## 💡 使用示例

1. **使用外观模式进行翻译**（推荐）：
```python
from application.translation_facade import TranslationServiceFacade

facade = TranslationServiceFacade(config_path="config.json")
result = await facade.translate_file(
    input_file="input.xlsx",
    source_lang="中文",
    target_lang="英语"
)
```

2. **术语库管理**（独立使用）：
```python
from domain.terminology_service_impl import TerminologyDomainServiceImpl
from domain.models import Config

config = Config()
service = TerminologyDomainServiceImpl(config)

# 查询相似翻译
result = await service.find_match("需要翻译的文本", "英语")

# 添加新术语
await service.save_term("原文", "英语", "译文")
```

3. **模糊匹配**（独立使用）：
```python
from data_access.fuzzy_matcher import FuzzyMatcher

items = [("原文 1", "译文 1"), ("原文 2", "译文 2")]
best = FuzzyMatcher.find_best_match("查询文本", items, threshold=60)
```

4. **并发控制**（独立使用）：
```python
from infrastructure.utils.concurrency_controller import AdaptiveConcurrencyController
from infrastructure.config.config import Config

config = Config()
controller = AdaptiveConcurrencyController(config)

# 根据请求结果调整并发
await controller.adjust(success=True)
current_limit = controller.get_limit()
```

## 🔍 模块间接口

所有模块都通过清晰的接口进行通信：

- **输入参数**: 使用类型注解明确参数类型
- **返回值**: 使用 TypedDict/Dataclass 规范返回结构
- **异常处理**: 各模块内部处理异常，向外暴露友好的错误信息

## 📊 性能优化

- **多进程支持**: 大数据量模糊匹配自动切换到多进程
- **异步 IO**: 术语库读写采用异步机制
- **批量处理**: 任务分批执行，避免内存溢出
- **GC 优化**: 定期垃圾回收
- **缓存优化**: 6 级缓存优化策略
- **并发控制**: 自适应并发度调整

---

**版本**: 3.1
**架构**: 六层架构 + Infrastructure 6 子模块
**最后更新**: 2026-04-03
**变更**: Infrastructure 层拆分为 6 个子模块 (cache/config/database/di/logging/utils)