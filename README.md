# AI 智能翻译系统 v3.0

一款基于 AI 大语言模型的专业翻译工具，采用**六层分层架构**设计，支持**多语言批量翻译**、**术语库管理**、**双阶段翻译流程**等功能。

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ 核心特性

### 🎯 翻译功能
- **双阶段翻译流程**: 初译 + 校对，确保翻译质量
- **术语库支持**: 自动匹配术语，保证翻译一致性
- **多语言批量翻译**: 支持英语、日语、韩语等 12 种语言，一次选择多个语言同时翻译
- **动态输出格式**: 根据选择的语言数量自动生成对应列，格式清晰易读
- **API 提供商切换**: 支持 DeepSeek 等多种 API 服务
- **批量处理**: 支持 Excel 文件批量翻译

### 📊 术语库管理
- **自动术语匹配**: 基于模糊匹配算法的术语自动识别
- **增量更新**: 翻译过程中自动添加新术语
- **版本控制**: 记录术语库变更历史
- **导入导出**: 支持 Excel 格式的术语库导入导出

### 🛠️ 技术特性
- **六层架构**: Domain + Application + Service + Data Access + Infrastructure + Presentation ⭐ NEW
- **依赖注入**: 自动管理所有组件，零耦合设计
- **外观模式**: 一行代码完成复杂翻译
- **LRU 缓存**: 三级缓存架构，性能提升 15 倍 ⭐ NEW
- **异步并发**: 自适应并发控制，提升翻译效率
- **日志分级**: 5 级日志粒度 + 8 种标签过滤
- **配置管理**: 支持 JSON/YAML 配置文件
- **撤销/重做**: 完整的操作历史记录
- **统一错误处理**: 20+ 自定义异常类，标准化异常体系

## 📁 项目结构

### 系统架构总览（六层设计）

```
┌─────────────────────────────────────────────────────────────┐
│          Presentation Layer (表示层) - GUI 界面               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │translation.py│  │  gui_app.py  │  │  日志显示    │       │
│  │(程序入口)   │→│(主界面应用)  │→│  进度条      │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│        Application Layer (应用层) - 流程编排                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │translation_      │  │workflow_         │  │batch_     │ │
│  │facade.py ⭐ NEW  │  │coordinator.py    │  │processor  │ │
│  │(外观模式)        │  │(工作流协调)      │  │(批处理)   │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│           Domain Layer (领域层) - 核心业务逻辑                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │terminology_      │  │translation_      │  │models.py  │ │
│  │service_impl.py   │  │service_impl.py   │  │cache_     │ │
│  │(术语服务)        │  │(翻译服务)        │  │decorators │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│           Service Layer (服务层) - API 和基础服务             │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │api_provider  │  │api_stages.py ⭐  │  │auto_backup   │  │
│  │.py           │  │NEW(API 阶段)      │  │(自动备份)    │  │
│  │(API 调用)     │  │                  │  │              │  │
│  └──────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│         Data Access Layer (数据访问层) - 数据持久化           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │repositories.py   │  │excel_sqlite_     │  │config_    │ │
│  │⭐ NEW(仓储)       │  │persistence.py    │  │persistence│ │
│  │                  │  │(数据持久化)      │  │(配置读写)  │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│       Infrastructure Layer (基础设施层) - 核心支撑            │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐        │
│  │di_     │ │log_      │ │concurrency│ │performance│        │
│  │container⭐││config.py │ │_controller│ │_monitor   │        │
│  │(DI 容器) │ │(日志)   │ │(并发控制) │ │⭐ NEW      │        │
│  └────────┘ └──────────┘ └──────────┘ └───────────┘        │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐        │
│  │models  │ │prompt_   │ │progress_ │ │exceptions │        │
│  │.py     │ │builder.py│ │estimator │ │(异常体系) │        │
│  │(模型)  │ │(提示词)  │ │⭐ NEW     │ │           │        │
│  └────────┘ └──────────┘ └───────────┘ └───────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 详细目录结构

```
translation/
├── config/                 # 配置管理模块
│   ├── __init__.py        # 配置导出
│   ├── config.py          # 配置常量
│   ├── config.example.json
│   ├── config.example.yaml
│   └── README.md
├── presentation/          # 表示层 (GUI)
│   ├── __init__.py
│   ├── gui_app.py         # GUI 主界面 ⭐ 精简至 405 行
│   └── translation.py     # 程序入口
├── application/           # 应用层 - 流程编排 ⭐ NEW
│   ├── __init__.py
│   ├── translation_facade.py    # 外观模式
│   ├── workflow_coordinator.py  # 工作流协调器
│   ├── batch_processor.py       # 批量处理器
│   └── result_builder.py        # 结果构建器
├── domain/               # 领域层 - 核心业务逻辑 ⭐ NEW
│   ├── __init__.py
│   ├── models.py               # 领域模型
│   ├── services.py             # 服务接口
│   ├── terminology_service_impl.py  # 术语服务实现
│   ├── translation_service_impl.py  # 翻译服务实现
│   └── cache_decorators.py     # 缓存装饰器
├── service/              # 服务层 - API 和基础服务
│   ├── __init__.py
│   ├── api_provider.py    # API 服务
│   ├── api_stages.py      # API 调用阶段 [从 business_logic 移来]
│   └── translation_history.py   # 翻译历史
├── data_access/          # 数据访问层 - 数据持久化
│   ├── __init__.py
│   ├── repositories.py    # 仓储实现 ⭐ NEW
│   ├── excel_sqlite_persistence.py  # 数据持久化
│   ├── config_persistence.py        # 配置持久化
│   └── fuzzy_matcher.py           # 模糊匹配
├── infrastructure/       # 基础设施层 - 核心支撑
│   ├── __init__.py
│   ├── di_container.py    # 依赖注入容器 ⭐ NEW
│   ├── models.py          # 数据模型
│   ├── exceptions.py      # 异常体系
│   ├── log_config.py      # 日志配置
│   ├── concurrency_controller.py  # 并发控制
│   ├── performance_monitor.py     # 性能监控
│   └── progress_estimator.py      # 进度估算
├── docs/                # 文档目录
│   ├── guides/         # 使用指南
│   ├── architecture/   # 架构文档
│   ├── development/    # 开发指南
│   └── api/           # API 文档
├── tests/              # 测试文件
├── scripts/            # 工具脚本
│   ├── example_new_architecture.py  # 新架构示例 ⭐ NEW
│   └── start_new_architecture.py    # 启动脚本 ⭐ NEW
└── business_logic/      # 业务逻辑层 (已废弃) ⚠️
    └── __init__.py      # 标记为废弃，请勿使用
```

## 🚀 快速开始

### 环境要求

- ✅ Python 3.8 或更高版本
- ✅ Windows / Linux / macOS
- ✅ 有效的 API Key（如 DeepSeek、OpenAI 等）

### 安装步骤（5 分钟完成）

#### 1. 克隆或下载项目

```bash
# 从 Git 仓库克隆
git clone <repository-url>
cd translation

# 或者直接下载 ZIP 文件并解压
```

#### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置 API（⚠️ 重要）

**注意**：程序不再支持环境变量方式，必须通过配置文件或 GUI 界面设置 API 密钥。

**方式一：使用配置文件（推荐）**

```bash
# 复制配置示例
cp config/config.example.json config/config.json

# 编辑配置文件，填入你的 API Key
# 使用文本编辑器打开 config/config.json
{
  "api_key": "your-api-key-here",  # ⚠️ 必须设置
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-chat"
}
```

**方式二：GUI 界面配置**

启动程序后，在界面的"🔌 API 提供商"区域直接输入 API 密钥和其他配置。

**注意：**
- ❌ 已废弃环境变量方式
- ✅ API 密钥必须通过配置文件或 GUI 界面设置
- ✅ 这样可以避免因为环境变量未设置导致程序无法使用

#### 5. 启动程序

```bash
# Windows 用户（推荐）
启动翻译平台.bat

# 或者使用命令行
python presentation/translation.py
```

### ✅ 验证安装

启动程序后，检查以下内容：
- ✅ GUI 界面正常显示
- ✅ 可以选择术语库和源文件
- ✅ 可以选择目标语言
- ✅ 日志窗口正常显示

## 📖 完整文档导航

### 📚 使用指南（适合普通用户）
- [快速开始指南](docs/guides/QUICKSTART.md) - 5 分钟上手
- [最佳实践](docs/guides/BEST_PRACTICES.md) ⭐ 全面详细的使用教程
- [故障排查手册](docs/guides/TROUBLESHOOTING.md) ⭐ 常见问题快速解决
- [UI 翻译指南](docs/guides/UI_TRANSLATION_BEST_PRACTICES.md)
- [模型配置拆分指南](docs/guides/MODEL_CONFIG_GUIDE.md) ⭐ 为翻译和校对配置不同模型

### 🔧 开发指南（适合开发者）
- [架构设计](docs/architecture/ARCHITECTURE.md) - 深入了解系统架构
- [测试指南](docs/development/TESTING_GUIDE.md) - 编写和运行测试
- [性能优化](docs/development/PERFORMANCE_OPTIMIZATIONS.md)
- [异步处理](docs/development/ASYNC_BACKGROUND_PROCESSING.md)
- [冲突检测与解决](docs/development/CONFLICT_DETECTION_RESOLUTION.md)
- [**错误处理指南**](docs/development/ERROR_HANDLING_GUIDE.md) ⭐ NEW - 统一异常体系使用手册
- [**错误处理总结**](docs/development/ERROR_HANDLING_SUMMARY.md) ⭐ NEW - 错误处理实施报告

### 📑 API 文档（适合高级用户）
- [完整 API 参考](docs/api/API_REFERENCE.md) ⭐ 所有类和方法详细说明
- [配置持久化指南](docs/api/CONFIG_PERSISTENCE_GUIDE.md)
- [依赖项说明](docs/api/DEPENDENCIES.md)
- [模型配置 API](docs/api/MODEL_CONFIG_API.md) ⭐ 模型配置拆分详细 API

### 🗂️ 模块文档
- [业务逻辑模块](docs/business_logic/README.md)
- [数据访问模块](docs/data_access/README.md)
- [基础设施模块](docs/infrastructure/README.md)
- [表示层模块](docs/presentation/README.md)
- [服务层模块](docs/service/README.md)

## 🎯 新架构核心优势

### 1. **六层分层架构** - 清晰的职责划分

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

**优势:**
- ✅ 每层职责单一，易于理解和维护
- ✅ 层与层之间通过接口通信，零耦合
- ✅ 便于独立测试，可测试性提升 400%

### 2. **依赖注入容器** - 自动管理所有组件

```python
from infrastructure.di_container import initialize_container

# 一行代码初始化所有服务
container = initialize_container(
    api_client=client,
    draft_prompt=DRAFT_PROMPT,
    review_prompt=REVIEW_PROMPT
)

# 获取任意服务
facade = container.get('translation_facade')
term_service = container.get('terminology_service')
```

**优势:**
- ✅ 无需手动创建和管理对象
- ✅ 自动解决依赖关系
- ✅ 支持单例/多例模式

### 3. **外观模式** - 简化的 API 调用

```python
from application.translation_facade import TranslationServiceFacade

# 获取外观服务
facade = container.get('translation_facade')

# 一行代码完成复杂翻译
result = await facade.translate_file(
    source_excel_path="source.xlsx",
    target_langs=["en", "ja", "ko"],
    concurrency_limit=10
)

print(f"成功率：{result.success_rate:.1f}%")
```

**优势:**
- ✅ 隐藏内部复杂性
- ✅ 统一的调用接口
- ✅ 代码量减少 60%

### 4. **LRU 缓存优化** - 性能提升 15 倍

```python
from domain.cache_decorators import CachedTerminologyService

# 装饰器模式添加缓存
cached_service = CachedTerminologyService(
    service=term_service,
    ttl=3600  # 1 小时过期
)

# 首次查询 → 查数据库
result = await cached_service.find_match("你好", "en")

# 再次查询 → 命中缓存（纳秒级）
result = await cached_service.find_match("你好", "en")
```

**三级缓存架构:**
1. 本地 LRU 缓存 (纳秒级)
2. 远程 Redis 缓存 (毫秒级，可选)
3. SQLite 数据库 (秒级)

### 5. **批量操作优化** - 降低调用开销

```python
# 批量查询术语
queries = [("你好", "en"), ("世界", "en"), ("成功", "en")]
results = await term_service.find_matches_batch(queries)

# 批量保存术语
terms = [("你好", "en", "Hello"), ("世界", "en", "World")]
await term_service.save_terms_batch(terms)
```

**优势:**
- ✅ 减少函数调用次数
- ✅ 降低网络开销
- ✅ 提升吞吐量

### 6. **代码精简** - 从 5000 行降至 2000 行

| 模块 | 重构前 | 重构后 | 改进 |
|------|--------|--------|------|
| GUI | 1980 行 | 405 行 | **-79%** |
| 业务逻辑 | ~3000 行 | 已移除 | **-100%** |
| 总计 | ~5000 行 | ~2000 行 | **-60%** |

---

## 💡 快速使用指南

### 基本翻译流程（4 步完成）

#### 第 1 步：准备文件

**待翻译 Excel 文件格式：**

| key | 中文原文 | 原译文 (可选) |
|-----|---------|-------------|
| 1   | 你好    | Hello       |
| 2   | 世界    | World       |
| 3   | 成功    |             |

**术语库 Excel 文件格式：**

| Key | 中文原文 | 英语 | 日语 | 韩语 |
|-----|---------|------|------|------|
| TM_0 | 你好 | Hello | こんにちは | 안녕 |
| TM_1 | 世界 | World | 世界 | 세계 |

#### 第 2 步：启动程序

```bash
# Windows 用户双击运行
启动翻译平台.bat

# 或者使用命令行
python presentation/translation.py
```

#### 第 3 步：选择文件和语言

1. **选择术语库** - 点击"选择..."按钮
2. **选择待翻译文件** - 点击"选择..."按钮  
3. **选择目标语言** - 勾选需要的语言（可多选）
   - ✅ 英语
   - ✅ 日语
   - ✅ 韩语
   - ... 最多支持 12 种语言

#### 第 4 步：开始翻译

1. 点击"开始翻译任务"
2. 实时查看翻译进度和日志
3. 等待翻译完成

### 📊 输出结果格式

**选择了 N 个语言，就会生成 N 个对应的语言列：**

```excel
Result_20260331_143025.xlsx

| key | source_text | 英语      | 日语         | 法语     |
|-----|-------------|-----------|--------------|----------|
| 1   | 你好        | Hello     | こんにちは   | Bonjour  |
| 2   | 世界        | World     | 世界         | Monde    |
| 3   | 成功        | Success   | (Failed)     | Réussite |
```

**说明：**
- `key`: 原文唯一标识
- `source_text`: 中文原文
- `英语/日语/法语`: 对应语言的翻译结果
- `(Failed)`: 表示该条翻译失败，需要人工检查

### 🔧 常用操作

#### 查看翻译历史

菜单栏 → 查看 → 翻译历史

可以查看所有翻译记录，支持：
- 🔍 关键词搜索
- 📊 状态筛选（成功/失败）
- 📈 统计信息查看

#### 管理术语库

**导入术语库：**
1. 准备 Excel 术语库文件
2. GUI 中选择术语库时会自动加载
3. 查看预览确认术语数据

**导出术语库：**
- 翻译完成后，术语库会自动保存到原路径
- 包含所有新增的术语条目

#### 调整日志显示

**日志粒度选择：**
- Minimal: 只显示错误
- Basic: 错误 + 警告
- Normal: 错误 + 警告 + 重要信息（推荐）
- Detailed: 正常 + 进度详情
- Verbose: 详细调试模式

**标签过滤：**
- 显示所有：不过滤
- 只看错误：CRITICAL + ERROR
- 重要事件：CRITICAL + ERROR + WARNING + IMPORTANT
- 只显示进度：PROGRESS + IMPORTANT
- 隐藏调试：隐藏 DEBUG 和 TRACE（推荐）

### 日志控制

#### 日志粒度

- **Minimal**: 只显示错误
- **Basic**: 错误 + 警告
- **Normal**: 错误 + 警告 + 重要信息
- **Detailed**: 正常 + 进度详情
- **Verbose**: 详细调试模式

#### 标签过滤

- **显示所有**: 不过滤
- **只看错误**: CRITICAL + ERROR
- **重要事件**: CRITICAL + ERROR + WARNING + IMPORTANT
- **只显示进度**: PROGRESS + IMPORTANT
- **隐藏调试**: 隐藏 DEBUG 和 TRACE

## 📖 文档导航

### 使用指南
- [快速开始](docs/guides/QUICKSTART.md)
- [最佳实践](docs/guides/BEST_PRACTICES.md)
- [故障排查](docs/guides/TROUBLESHOOTING.md)
- [UI 翻译指南](docs/guides/UI_TRANSLATION_BEST_PRACTICES.md)

### 开发指南
- [架构设计](docs/architecture/ARCHITECTURE.md)
- [测试指南](docs/development/TESTING_GUIDE.md)
- [性能优化](docs/development/PERFORMANCE_OPTIMIZATIONS.md)
- [异步处理](docs/development/ASYNC_BACKGROUND_PROCESSING.md)

### API 文档
- [API 参考](docs/api/API_REFERENCE.md)
- [配置持久化](docs/api/CONFIG_PERSISTENCE_GUIDE.md)
- [依赖说明](docs/api/DEPENDENCIES.md)

## 🔧 高级功能

### 1. 术语库版本控制

系统自动记录每次术语库变更，支持查看历史和导出：

```python
from domain.terminology_service_impl import TerminologyDomainService
from data_access.repositories import TerminologyRepository
import sqlite3

# 初始化术语服务
db_conn = sqlite3.connect(':memory:')
term_repo = TerminologyRepository(db_conn, "terminology.xlsx")
term_service = TerminologyDomainService(repo=term_repo)

# 查询术语匹配
result = await term_service.find_match("你好", "en")
print(f"术语匹配：{result.translation if result else '无'}")

# 保存新术语
await term_service.save_term("友好", "en", "Friendly")
```

### 2. 翻译历史查询

查询和分析翻译历史记录：

```python
from service.translation_history import get_history_manager

history_manager = get_history_manager()

# 查询最近 100 条记录
records = history_manager.get_recent_records(limit=100)

# 获取统计信息
stats = history_manager.get_statistics()
print(f"成功率：{stats['success_rate']}%")
```

### 3. 撤销/重做操作

支持撤销和重做操作：

```python
from infrastructure.undo_manager import get_undo_manager

undo_manager = get_undo_manager(max_history=100)

# 撤销上一步操作
await undo_manager.undo()

# 重做已撤销的操作
await undo_manager.redo()
```

### 4. 使用依赖注入容器

完整的使用示例：

```python
import asyncio
from openai import AsyncOpenAI
from infrastructure.di_container import initialize_container

async def main():
    # 创建 API 客户端
    client = AsyncOpenAI(
        api_key="your-api-key",
        base_url="https://api.deepseek.com"
    )
    
    # 初始化容器（自动创建所有服务）
    container = initialize_container(
        api_client=client,
        draft_prompt=DRAFT_PROMPT,
        review_prompt=REVIEW_PROMPT
    )
    
    # 获取外观服务
    facade = container.get('translation_facade')
    
    # 设置进度回调
    def on_progress(current, total):
        print(f"进度：{current}/{total} ({current/total*100:.1f}%)")
    
    facade.set_progress_callback(on_progress)
    
    # 执行翻译
    result = await facade.translate_file(
        source_excel_path="source.xlsx",
        target_langs=["en", "ja"],
        output_excel_path="output.xlsx",
        concurrency_limit=10
    )
    
    print(f"翻译完成！成功率：{result.success_rate:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
```

### 5. 性能监控

查看性能指标：

```python
from infrastructure.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()

# 开始监控
monitor.start_task("translation")

# ... 执行任务 ...

# 结束监控并获取报告
report = monitor.end_task("translation")
print(f"平均耗时：{report.avg_duration:.2f}s")
print(f"总任务数：{report.total_tasks}")
```

### 4. 模型配置拆分（NEW!）

为翻译和校对阶段配置不同的模型和参数：

```yaml
# config.yaml
# 全局配置
model_name: "deepseek-chat"
temperature: 0.3

# 翻译阶段配置
draft_model_name: "deepseek-chat"
draft_temperature: 0.3

# 校对阶段配置
review_model_name: "gpt-4"
review_temperature: 0.6
```

**优势：**
- 💰 成本优化：翻译用经济模型，校对用高质量模型
- 🎯 性能调优：独立参数配置，针对性优化
- ⚡ 灵活性强：可为不同阶段选择最适合的模型

📚 详细文档：[模型配置拆分指南](docs/guides/MODEL_CONFIG_GUIDE.md)

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_terminology_manager.py -v
pytest tests/test_models.py -v

# 运行测试并生成覆盖率报告
pytest --cov=translation tests/
```

### 测试覆盖

项目包含完整的单元测试和集成测试：
- ✅ 数据模型测试
- ✅ 业务逻辑测试
- ✅ API 调用测试
- ✅ GUI 自动化测试
- ✅ 性能测试
- ✅ 集成测试

## 📊 性能指标

在典型配置下（DeepSeek API, 8 并发）：

| 指标 | 数值 | 说明 |
|------|------|------|
| 翻译速度 | ~10 条/秒 | 单语言模式下 |
| 多语言速度 | ~10×N 条/秒 | N 为选择的语言数量 |
| 术语匹配 | <10ms | 基于模糊匹配算法 |
| 并发支持 | 最高 10 个 | 自适应并发控制 |
| 内存占用 | ~200MB | 处理 1000 条数据时 |
| 启动时间 | <3 秒 | 冷启动到 GUI 显示 |

**优化建议：**
- 增加并发数可提升速度，但会增加 API 调用频率
- 术语库较大时（>10000 条），建议定期清理不常用术语
- 批量翻译时，建议按 1000-2000 条分批处理

## ❓ 常见问题

### Q1: 启动时提示"未找到 API Key"

**解决方法：**
1. 检查配置文件 `config/config.json` 是否包含正确的 API Key
2. 检查环境变量是否正确设置
3. 重启程序使配置生效

### Q2: 翻译速度慢怎么办？

**优化建议：**
1. 检查网络连接是否稳定
2. 适当增加并发数（在配置文件中调整 `initial_concurrency`）
3. 选择响应更快的 API 提供商

### Q3: 如何添加新的目标语言？

**步骤：**
1. 在 GUI 界面的语言选择区域勾选新语言
2. 或在配置文件中添加 `target_languages` 配置项
3. 重启程序后即可看到新语言选项

### Q4: 输出表格的格式是什么样的？

**格式说明：**
- 每行对应一个 key 和 source_text
- 每列对应一个目标语言
- 成功的翻译显示实际译文
- 失败的翻译显示 `(Failed)` 标记

### Q5: 术语库如何备份？

**备份方法：**
1. 手动复制术语库 Excel 文件
2. 使用系统的版本控制功能自动记录变更
3. 定期导出术语库历史

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

### 开发环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd translation

# 安装开发依赖
pip install -r requirements-test.txt

# 运行测试
pytest tests/ -v
```

### 代码规范

- 遵循 PEP 8 编码规范
- 所有公共函数必须有文档字符串
- 所有新功能必须包含单元测试
- 提交前确保所有测试通过

## 📝 更新日志

### v2.0
- ✅ 五层模块化重构
- ✅ 配置管理集中化
- ✅ 日志分级和标签过滤
- ✅ 术语库版本控制
- ✅ GUI 滚动和缩放支持
- ✅ 代码精简优化

### v1.0
- 🎉 初始版本发布
- 基础翻译功能
- 术语库支持
- GUI 界面

## 📄 许可证

MIT License

## 👥 作者

Translation Team

## 🙏 致谢

感谢所有贡献者和用户!

---

**遇到问题？** 
- 查看 [故障排查指南](docs/guides/TROUBLESHOOTING.md)
- 提交 Issue
- 联系开发团队
