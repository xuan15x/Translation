# API 参考手册

## 📋 概述

本手册提供完整的 API 参考，包括所有公开类、函数和方法的详细说明。

## 📦 模块索引

### config (配置模块)
- [DEFAULT_DRAFT_PROMPT](#default_draft_prompt) - 初译提示词模板
- [DEFAULT_REVIEW_PROMPT](#default_review_prompt) - 校对提示词模板
- [TARGET_LANGUAGES](#target_languages) - 目标语言列表
- [GUI_CONFIG](#gui_config) - GUI 配置常量

### infrastructure (基础设施层)
- [Config](#config) - 运行时配置类
- [TaskContext](#taskcontext) - 任务上下文
- [StageResult](#stageresult) - 阶段结果
- [FinalResult](#finalresult) - 最终结果
- [setup_logger()](#setup_logger) - 设置日志
- [get_logger()](#get_logger) - 获取日志器
- [AdaptiveConcurrencyController](#adaptiveconcurrencycontroller) - 并发控制器

### business_logic (业务逻辑层)
- [WorkflowOrchestrator](#workfloworchestrator) - 工作流编排器
- [TerminologyManager](#terminologymanager) - 术语管理器

### service (服务层)
- [get_provider_manager()](#get_provider_manager) - 获取 API 提供商管理器
- [TranslationHistoryManager](#translationhistorymanager) - 翻译历史管理器
- [get_history_manager()](#get_history_manager) - 获取历史管理器

### data_access (数据访问层)
- [ConfigPersistence](#configpersistence) - 配置持久化
- [FuzzyMatcher](#fuzzymatcher) - 模糊匹配器

---

## 🔧 详细 API 说明

### DEFAULT_DRAFT_PROMPT

**类型**: `str`

**说明**: 初译提示词模板，用于第一阶段翻译。

**示例**:
```python
from translation import DEFAULT_DRAFT_PROMPT
print(DEFAULT_DRAFT_PROMPT)
```

---

### DEFAULT_REVIEW_PROMPT

**类型**: `str`

**说明**: 校对提示词模板，用于第二阶段优化。

**示例**:
```python
from translation import DEFAULT_REVIEW_PROMPT
print(DEFAULT_REVIEW_PROMPT)
```

---

### TARGET_LANGUAGES

**类型**: `List[str]`

**说明**: 支持的目标语言列表。

**值**:
```python
[
    "英语", "日语", "韩语", "法语", "德语", 
    "西班牙语", "俄语", "葡萄牙语", "意大利语", 
    "阿拉伯语", "泰语", "越南语"
]
```

---

### GUI_CONFIG

**类型**: `Dict[str, Any]`

**说明**: GUI 界面配置常量。

**字段**:
- `window_title`: 窗口标题
- `window_width`: 窗口宽度
- `window_height`: 窗口高度

---

### Config

**类**: 运行时配置对象

**参数**:
- `api_key` (str): API 密钥
- `base_url` (str): API 基础 URL
- `model_name` (str): 模型名称
- `temperature` (float): 温度参数
- `top_p` (float): Top-p 采样参数
- `max_tokens` (int): 最大 token 数
- `initial_concurrency` (int): 初始并发数
- `max_concurrency` (int): 最大并发数
- `batch_size` (int): 批次大小
- `max_retries` (int): 最大重试次数
- `retry_delay` (int): 重试延迟

**示例**:
```python
from translation import Config

config = Config(
    api_key="your-key",
    base_url="https://api.deepseek.com",
    model_name="deepseek-chat",
    temperature=0.3
)
```

---

### TaskContext

**数据类**: 任务上下文

**字段**:
- `idx` (int): 任务索引
- `key` (str): 业务唯一标识
- `source_text` (str): 源文本
- `original_trans` (str): 原译文
- `target_lang` (str): 目标语言

**示例**:
```python
from translation import TaskContext

ctx = TaskContext(
    idx=0,
    key="TM_001",
    source_text="紫钻",
    target_lang="英语"
)
```

---

### StageResult

**数据类**: 阶段执行结果

**字段**:
- `success` (bool): 是否成功
- `translation` (str): 翻译结果
- `reason` (str): 修改原因
- `source` (str): 结果来源

**示例**:
```python
from translation import StageResult

result = StageResult(
    success=True,
    translation="Purple Diamond",
    reason="术语匹配",
    source="LOCAL_HIT"
)
```

---

### FinalResult

**数据类**: 最终翻译结果

**字段**:
- `idx` (int): 任务索引
- `key` (str): 业务唯一标识
- `source_text` (str): 源文本
- `draft_trans` (str): 初译结果
- `final_trans` (str): 最终结果
- `reason` (str): 修改原因
- `diagnosis` (str): 诊断信息
- `target_lang` (str): 目标语言
- `status` (str): 状态

**示例**:
```python
from translation import FinalResult

final = FinalResult(
    idx=0,
    key="TM_001",
    source_text="紫钻",
    draft_trans="Purple Diamond",
    final_trans="Purple Diamond",
    reason="术语匹配",
    diagnosis="LOCAL_HIT",
    target_lang="英语",
    status="SUCCESS"
)
```

---

### setup_logger()

**函数**: 设置日志系统

**参数**:
- `config` (LogConfig, 可选): 日志配置

**返回**:
- Logger: 日志器实例

**示例**:
```python
from translation import setup_logger, LogConfig, LogLevel

config = LogConfig(level=LogLevel.INFO)
logger = setup_logger(config=config)
```

---

### get_logger()

**函数**: 获取全局日志器

**返回**:
- Logger: 日志器实例

**示例**:
```python
from translation import get_logger

logger = get_logger()
logger.info("这是一条日志信息")
```

---

### AdaptiveConcurrencyController

**类**: 自适应并发控制器

**参数**:
- `initial_concurrency` (int): 初始并发数
- `max_concurrency` (int): 最大并发数

**方法**:
- `acquire()`: 获取并发令牌 (异步上下文管理器)

**示例**:
```python
from translation import AdaptiveConcurrencyController

controller = AdaptiveConcurrencyController(
    initial_concurrency=8,
    max_concurrency=10
)

async with controller.acquire():
    # 执行任务
    await process_task()
```

---

### WorkflowOrchestrator

**类**: 工作流编排器

**参数**:
- `config` (Config): 运行时配置

**方法**:
- `execute(tasks, out_file)`: 执行翻译任务

**示例**:
```python
from translation import WorkflowOrchestrator, Config, TaskContext

config = Config(api_key="your-key")
orchestrator = WorkflowOrchestrator(config)

tasks = [
    TaskContext(idx=0, key="TM_0", source_text="紫钻", target_lang="英语")
]

results = await orchestrator.execute(tasks, "result.xlsx")
```

---

### TerminologyManager

**类**: 术语管理器

**参数**:
- `filepath` (str): 术语库文件路径
- `config` (Config): 运行时配置

**方法**:
- `query(source_text, fuzzy_threshold)`: 查询术语
- `add_entry(key, source_text, translations)`: 添加术语
- `export_to_excel(output_path, export_new_only)`: 导出术语库
- `get_history_timeline(days)`: 获取变更历史
- `shutdown()`: 关闭并保存

**示例**:
```python
from translation import TerminologyManager, Config

tm = TerminologyManager("terms.xlsx", config)

# 查询术语
term = tm.query("紫钻")

# 添加术语
tm.add_entry(
    key="TM_100",
    source_text="绿钻",
    translations={"英语": "Green Diamond"}
)

# 导出
await tm.export_to_excel("updated_terms.xlsx")

# 关闭
await tm.shutdown()
```

---

### get_provider_manager()

**函数**: 获取 API 提供商管理器

**返回**:
- ProviderManager: API 提供商管理器实例

**方法**:
- `get_available_providers()`: 获取可用提供商列表
- `switch_provider(provider_name)`: 切换提供商
- `create_api_client()`: 创建 API 客户端

**示例**:
```python
from translation import get_provider_manager

manager = get_provider_manager()
providers = manager.get_available_providers()
await manager.switch_provider("DeepSeek")
```

---

### TranslationHistoryManager

**类**: 翻译历史管理器

**方法**:
- `get_recent_records(limit)`: 获取最近记录
- `get_statistics()`: 获取统计信息

**示例**:
```python
from translation import get_history_manager

history_manager = get_history_manager()
records = history_manager.get_recent_records(limit=100)
stats = history_manager.get_statistics()
```

---

### get_history_manager()

**函数**: 获取翻译历史管理器

**返回**:
- TranslationHistoryManager: 历史管理器实例

**示例**:
```python
from translation import get_history_manager

history_manager = get_history_manager()
records = history_manager.get_recent_records()
```

---

### ConfigPersistence

**类**: 配置持久化工具

**方法**:
- `load_json(filepath)`: 加载 JSON 配置
- `save_json(filepath, data)`: 保存 JSON 配置

**示例**:
```python
from translation import ConfigPersistence

persistence = ConfigPersistence()
config = persistence.load_json("config/config.json")
persistence.save_json("config/config.json", config)
```

---

### FuzzyMatcher

**类**: 模糊匹配器

**方法**:
- `calculate_similarity(s1, s2)`: 计算相似度
- `find_best_match(query, candidates, threshold)`: 查找最佳匹配

**示例**:
```python
from translation import FuzzyMatcher

matcher = FuzzyMatcher()
similarity = matcher.calculate_similarity("紫钻", "紫色钻石")
best = matcher.find_best_match(
    query="紫色钻石",
    candidates=["紫钻", "蓝钻"]
)
```

---

## 🔗 相关文档

- [快速开始](../guides/QUICKSTART.md)
- [架构设计](../architecture/ARCHITECTURE.md)
- [使用指南](../guides/BEST_PRACTICES.md)
