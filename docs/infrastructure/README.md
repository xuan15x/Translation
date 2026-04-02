# 基础设施层文档

## 📑 目录

- [📋 概述](#-概述)
- [📁 文件结构](#-file_folder-文件结构)
- [🔧 核心模块](#-wrench-核心模块)
  - [1. 数据模型 (models.py)](#1-数据模型-modelspy)
    - [Config 类](#config-类)
    - [TaskContext 类](#taskcontext-类)
    - [StageResult 类](#stageresult-类)
    - [FinalResult 类](#finalresult-类)
  - [2. 日志配置 (log_config.py)](#2-日志配置-log_configpy)
    - [LogManager 类](#logmanager-类)
    - [LogConfig 类](#logconfig-类)
    - [LogLevel 枚举](#loglevel-枚举)
    - [LogGranularity 枚举](#loggranularity-枚举)
    - [LogTag 枚举](#logtag-枚举)
    - [log_with_tag 函数](#log_with_tag-函数)
  - [3. 并发控制 (concurrency_controller.py)](#3-并发控制-concurrency_controllerpy)
    - [AdaptiveConcurrencyController 类](#adaptiveconcurrencycontroller-类)
- [📖 使用示例](#-books-使用示例)
  - [1. 创建配置](#1-创建配置)
  - [2. 设置日志](#2-设置日志)
  - [3. 创建任务上下文](#3-创建任务上下文)
  - [4. 记录日志](#4-记录日志)
- [🔗 相关文档](#-相关文档)

---

## 📋 概述

`infrastructure/` 模块提供数据模型、日志配置、并发控制等基础功能。

## 📁 文件结构

```
infrastructure/
├── __init__.py              # 模块导出
├── models.py                # 数据模型
├── log_config.py            # 日志配置
├── logging_config.py        # 日志设置
├── concurrency_controller.py # 并发控制
└── ... (其他工具模块)
```

## 🔧 核心模块

### 1. 数据模型 (models.py)

#### Config 类

运行时配置对象，包含 API 配置和翻译参数。

```python
from translation import Config

config = Config(
    api_key="your-key",
    base_url="https://api.deepseek.com",
    model_name="deepseek-chat",
    temperature=0.3,
    top_p=0.8,
    max_tokens=512,
    initial_concurrency=8,
    max_concurrency=10,
    batch_size=10,
    max_retries=3,
    retry_delay=1
)
```

**属性说明**:
- `api_key`: API 密钥
- `base_url`: API 基础 URL
- `model_name`: 模型名称
- `temperature`: 温度参数
- `top_p`: Top-p 采样参数
- `max_tokens`: 最大 token 数
- `initial_concurrency`: 初始并发数
- `max_concurrency`: 最大并发数
- `batch_size`: 批次大小
- `max_retries`: 最大重试次数
- `retry_delay`: 重试延迟 (秒)

#### TaskContext 类

任务上下文，封装单个翻译任务的所有信息。

```python
from translation import TaskContext

ctx = TaskContext(
    idx=0,
    key="term_001",
    source_text="紫钻",
    original_trans="",
    target_lang="日语"
)
```

**属性说明**:
- `idx`: 任务索引 (从 0 开始)
- `key`: 业务唯一标识
- `source_text`: 源文本 (中文原文)
- `original_trans`: 原译文 (校对模式使用)
- `target_lang`: 目标语言

#### StageResult 类

阶段执行结果。

```python
from translation import StageResult

result = StageResult(
    success=True,
    translation="パープルダイヤモンド",
    reason="术语匹配",
    source="LOCAL_HIT"
)
```

**属性说明**:
- `success`: 是否成功
- `translation`: 翻译结果
- `reason`: 修改原因
- `source`: 结果来源

#### FinalResult 类

最终翻译结果。

```python
from translation import FinalResult

final = FinalResult(
    idx=0,
    key="term_001",
    source_text="紫钻",
    draft_trans="パープルダイヤモンド",
    final_trans="パープルダイヤモンド",
    reason="术语匹配",
    diagnosis="LOCAL_HIT",
    target_lang="日语",
    status="SUCCESS"
)
```

**属性说明**:
- `idx`: 任务索引
- `key`: 业务唯一标识
- `source_text`: 源文本
- `draft_trans`: 初译结果
- `final_trans`: 最终结果
- `reason`: 修改原因
- `diagnosis`: 诊断信息
- `target_lang`: 目标语言
- `status`: 状态 (SUCCESS/FAILED)

### 2. 日志配置 (log_config.py)

#### LogManager 类

日志管理器，提供全局日志控制。

```python
from translation import get_log_manager

log_manager = get_log_manager()

# 设置日志级别
log_manager.set_level("INFO")

# 设置日志粒度
log_manager.set_granularity("detailed")

# 设置标签过滤
log_manager.set_tag_filter(["CRITICAL", "ERROR"])
```

#### LogConfig 类

日志配置对象。

```python
from translation import LogConfig, LogLevel, LogGranularity

config = LogConfig(
    level=LogLevel.INFO,
    granularity=LogGranularity.DETAILED,
    show_colors=True,
    enable_gui=True,
    enable_console=True,
    max_lines=1000
)
```

**属性说明**:
- `level`: 日志级别
- `granularity`: 日志粒度
- `show_colors`: 显示颜色
- `enable_gui`: 启用 GUI 日志
- `enable_console`: 启用控制台日志
- `max_lines`: 最大行数

#### LogLevel 枚举

日志级别。

```python
from translation import LogLevel

LogLevel.DEBUG    # 调试
LogLevel.INFO     # 信息
LogLevel.WARNING # 警告
LogLevel.ERROR    # 错误
LogLevel.CRITICAL # 严重
```

#### LogGranularity 枚举

日志粒度级别。

```python
from translation import LogGranularity

LogGranularity.MINIMAL   # 最小化 (只显示错误)
LogGranularity.BASIC     # 基本 (错误 + 警告)
LogGranularity.NORMAL    # 正常 (错误 + 警告 + 重要)
LogGranularity.DETAILED  # 详细 (正常 + 进度)
LogGranularity.VERBOSE   # 最详细 (调试模式)
```

#### LogTag 枚举

日志标签 (按重要程度)。

```python
from translation import LogTag

LogTag.CRITICAL   # 💀 严重错误
LogTag.ERROR      # ❌ 错误
LogTag.WARNING    # ⚠️ 警告
LogTag.IMPORTANT  # ⭐ 重要
LogTag.PROGRESS   # 📊 进度
LogTag.NORMAL     # ℹ️ 普通
LogTag.DEBUG      # 🔍 调试
LogTag.TRACE      # 📝 追踪
```

#### log_with_tag 函数

带标签的日志记录函数。

```python
from translation import log_with_tag, LogLevel, LogTag

log_with_tag(
    "术语库精确匹配：紫钻 -> パープルダイヤモンド",
    level=LogLevel.INFO,
    tag=LogTag.IMPORTANT
)
```

**参数说明**:
- `message`: 日志消息
- `level`: 日志级别
- `tag`: 日志标签
- `**kwargs`: 其他参数

### 3. 并发控制 (concurrency_controller.py)

#### AdaptiveConcurrencyController 类

自适应并发控制器，动态调整并发数。

```python
from translation import AdaptiveConcurrencyController

controller = AdaptiveConcurrencyController(
    initial_concurrency=8,
    max_concurrency=10
)

# 获取令牌
async with controller.acquire():
    # 执行任务
    await process_task()
```

**参数说明**:
- `initial_concurrency`: 初始并发数
- `max_concurrency`: 最大并发数

**功能说明**:
- 自动根据成功率调整并发数
- 失败时降低并发，成功时提升并发
- 防止 API 限流

## 📖 使用示例

### 1. 创建配置

```python
from translation import Config

config = Config(
    api_key="your-key",
    base_url="https://api.deepseek.com",
    model_name="deepseek-chat"
)
```

### 2. 设置日志

```python
from translation import LogConfig, setup_logger, LogLevel

config = LogConfig(
    level=LogLevel.INFO,
    granularity=LogGranularity.DETAILED
)

logger = setup_logger(config=config)
```

### 3. 创建任务上下文

```python
from translation import TaskContext

ctx = TaskContext(
    idx=0,
    key="term_001",
    source_text="紫钻",
    original_trans="",
    target_lang="日语"
)
```

### 4. 记录日志

```python
from translation import log_with_tag, LogLevel, LogTag

log_with_tag(
    f"[行{ctx.idx+1}] 查询术语：{ctx.source_text}",
    level=LogLevel.INFO,
    tag=LogTag.DEBUG
)
```

## 🔗 相关文档

- [架构设计](../docs/architecture/ARCHITECTURE.md)
- [日志使用指南](../docs/development/LOGGING_GUIDE.md)
- [性能优化](../docs/development/PERFORMANCE_OPTIMIZATIONS.md)
