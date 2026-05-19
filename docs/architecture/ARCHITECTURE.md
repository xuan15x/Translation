# 架构设计文档

## 整体架构（黑盒 CLI 模式）

```
┌─────────────────────────────────────────────┐
│                 run.py (CLI)                 │
│     任务配置读取 / 管线启动 / 结果上报       │
├─────────────────────────────────────────────┤
│               Application                    │
│     (外观模式 / 工作流编排)                  │
│  translation_facade / batch_processor        │
├─────────────────────────────────────────────┤
│                 Domain                       │
│     (核心业务逻辑 / 接口定义)                │
│  models / services / cache_decorators        │
├─────────────────────────────────────────────┤
│                 Service                      │
│     (DeepSeek API 集成)                      │
│  api_provider / api_stage_base / api_stages  │
├─────────────────────────────────────────────┤
│              Data Access                     │
│     (仓储模式 / SQLite 持久化)               │
│  repositories / fuzzy_matcher                │
├─────────────────────────────────────────────┤
│            Infrastructure                    │
│     (DI容器 / 缓存 / 日志 / 工具)             │
│  di_container / cache / logging / utils      │
└─────────────────────────────────────────────┘
```

> v3.3 黑盒 CLI 模式：通过 `python run.py` 驱动，所有配置通过 `translation_task.json` + `config/config.json` 管理。

## 设计模式

### 1. 外观模式（Facade）
`TranslationServiceFacade` 封装整个翻译流程，对外提供简洁接口：
- `translate_file_wide_format()` — 黑盒宽格式翻译（2列→36列）
- `translate_file()` — 通用文件翻译
- `translate_text()` — 单文本翻译

### 2. 依赖注入（Dependency Injection）
`DependencyContainer` 管理所有服务的生命周期，`initialize_container()` 从配置自动装配。

### 3. 仓储模式（Repository）
`TerminologyRepository` 封装术语库的持久化操作。

### 4. 策略模式（Strategy）
`APIStageBase` → `APIDraftStage` / `APIReviewStage` / `LocalHitStage`

### 5. 多语言模式（Multilingual Strategy）
一次 API 调用翻译所有目标语言，通过 `MultiLanguageTask` + `TranslationDomainServiceMultilingual` 实现。

## 数据流

```
translation_task.json → run.py → TranslationFacade → APIStage → DeepSeek
                               ↓
                          FinalResult → _export → 输出.xlsx (36列宽表)
```

## 配置管理

```
config/config.json (75参数, 系统配置)
    ↓ ConfigLoader (单例)
        ↓ Config (数据类) → 13个子验证器
            ↓ DI Container → 各层服务

translation_task.json (任务配置)
    ↓ run.py → 解析 → 传给 Facade
```

## 测试架构

```
tests/ (19 个测试文件, 285 tests, 51% 覆盖率)
├── test_module_imports.py   # 全模块导入
├── test_integration.py      # 端到端集成
├── test_boundaries.py       # 边界/异常
├── test_di_container.py     # 依赖注入
├── test_utils.py            # 工具函数
├── test_health_check.py     # 健康检查
├── test_application.py      # 应用层
└── ... (12 more)
```
