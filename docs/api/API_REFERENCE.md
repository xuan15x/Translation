# AI 智能翻译工作台 API 文档

欢迎使用 AI 智能翻译工作台的 API 文档。本文档提供了完整的 API 参考，包括所有公开类、方法和函数的详细说明。

## 📚 文档结构

```
API 文档/
├── 核心模块/
│   ├── models - 数据模型
│   ├── config - 配置管理
│   └── logging_config - 日志系统
├── 业务逻辑层/
│   ├── workflow_orchestrator - 工作流编排
│   ├── terminology_manager - 术语库管理
│   └── api_stages - API 处理阶段
├── 服务层/
│   ├── api_provider - API 提供商
│   ├── translation_history - 翻译历史
│   └── terminology_version - 版本控制
├── 数据访问层/
│   ├── fuzzy_matcher - 模糊匹配
│   ├── config_persistence - 配置持久化
│   └── terminology_update - 术语更新
└── 基础设施层/
    ├── concurrency_controller - 并发控制
    ├── cache - 缓存系统
    ├── db_pool - 数据库连接池
    └── performance_monitor - 性能监控
```

## 🚀 快速开始

### 1. 基础使用示例

```python
from infrastructure.models import Config, TaskContext, FinalResult
from business_logic.terminology_manager import TerminologyManager
from business_logic.workflow_orchestrator import WorkflowOrchestrator
from openai import AsyncOpenAI

# 初始化配置
config = Config()

# 创建术语库管理器
tm = TerminologyManager("terms.xlsx", config)

# 创建 OpenAI 客户端
client = AsyncOpenAI(
    api_key=config.api_key,
    base_url=config.base_url
)

# 创建工作流编排器
orchestrator = WorkflowOrchestrator(
    config=config,
    client=client,
    tm=tm,
    p_draft="请将以下文本翻译成{target_lang}",
    p_review="请校对以下翻译"
)

# 创建并执行任务
ctx = TaskContext(
    idx=0,
    key="test_key",
    source_text="你好世界",
    original_trans="",
    target_lang="英语"
)

result = await orchestrator.process_task(ctx)
print(f"翻译结果：{result.final_trans}")
```

### 2. 术语库管理

```python
from business_logic.terminology_manager import TerminologyManager
from infrastructure.models import Config

config = Config()
tm = TerminologyManager("terms.xlsx", config)

# 查询相似术语
result = await tm.find_similar("人工智能", "英语")
if result:
    print(f"匹配：{result['original']} -> {result['translation']}")
    print(f"分数：{result['score']}")

# 添加新术语
await tm.add_entry("机器学习", "英语", "Machine Learning")

# 批量添加
entries = [
    ("深度学习", "英语", "Deep Learning"),
    ("神经网络", "英语", "Neural Network")
]
await tm.batch_add_entries_optimized(entries, batch_size=50)

# 获取性能统计
stats = await tm.get_performance_stats()
print(f"术语总数：{stats['database']['total_entries']}")
```

### 3. 版本控制和备份

```python
from business_logic.terminology_manager import TerminologyManager
from service.auto_backup import BackupStrategy

tm = TerminologyManager("terms.xlsx", Config())

# 启用版本控制
tm.enable_version_control(repo_path=".")

# 启用自动备份（每日备份）
tm.enable_auto_backup(
    backup_dir=".terminology_backups",
    strategy=BackupStrategy.DAILY
)

# 启动自动备份
await tm.start_auto_backup()

# 提交更改
await tm.commit_changes("添加新术语")

# 创建手动备份
backup_path = await tm.create_backup("重大更新前")

# 列出备份
backups = tm.list_backups(limit=10)

# 恢复备份
await tm.restore_from_backup(backup_path)
```

## 📖 API 参考索引

### 核心数据模型

**文件位置**: `infrastructure/models.py`

```{toctree}
:maxdepth: 2

api_reference/models
api_reference/config
api_reference/task_context
```

### 业务逻辑层

**文件位置**: `business_logic/`

```{toctree}
:maxdepth: 2

api_reference/workflow_orchestrator
api_reference/terminology_manager
api_reference/api_stages
```

### 服务层

**文件位置**: `service/`

```{toctree}
:maxdepth: 2

api_reference/api_provider
api_reference/translation_history
api_reference/terminology_version
api_reference/auto_backup
```

### 数据访问层

**文件位置**: `data_access/`

```{toctree}
:maxdepth: 2

api_reference/fuzzy_matcher
api_reference/config_persistence
api_reference/terminology_update
```

### 基础设施层

**文件位置**: `infrastructure/`

```{toctree}
:maxdepth: 2

api_reference/concurrency_controller
api_reference/cache
api_reference/db_pool
api_reference/performance_monitor
api_reference/undo_manager
api_reference/progress_estimator
```

## 🔍 常用 API 速查

### 配置相关

| API | 说明 | 示例 |
|-----|------|------|
| `Config()` | 创建默认配置 | `config = Config()` |
| `Config.from_file(path)` | 从文件加载配置 | `config = Config.from_file("config.json")` |
| `config.validate()` | 验证配置有效性 | `config.validate()` |

### 任务处理相关

| API | 说明 | 示例 |
|-----|------|------|
| `TaskContext(...)` | 创建任务上下文 | `ctx = TaskContext(idx=0, ...)` |
| `WorkflowOrchestrator.process_task()` | 处理单个任务 | `result = await orchestrator.process_task(ctx)` |
| `FinalResult` | 最终翻译结果 | `print(result.final_trans)` |

### 术语库相关

| API | 说明 | 示例 |
|-----|------|------|
| `TerminologyManager()` | 创建术语库管理器 | `tm = TerminologyManager(path, config)` |
| `tm.find_similar()` | 查询相似术语 | `result = await tm.find_similar(text, lang)` |
| `tm.add_entry()` | 添加术语 | `await tm.add_entry(src, lang, trans)` |
| `tm.shutdown()` | 关闭并保存 | `await tm.shutdown()` |

### 缓存相关

| API | 说明 | 示例 |
|-----|------|------|
| `LRUCache(capacity)` | 创建 LRU 缓存 | `cache = LRUCache(1000)` |
| `cache.set(key, value)` | 设置缓存 | `await cache.set("key", "value")` |
| `cache.get(key)` | 获取缓存 | `value = await cache.get("key")` |

### 性能监控相关

| API | 说明 | 示例 |
|-----|------|------|
| `PerformanceMonitor()` | 创建性能监控器 | `monitor = PerformanceMonitor()` |
| `monitor.start()` | 启动监控 | `await monitor.start()` |
| `monitor.get_stats()` | 获取统计信息 | `stats = monitor.get_stats()` |

## 🎯 最佳实践

### 1. 错误处理

```python
try:
    result = await orchestrator.process_task(ctx)
    if result.status == "SUCCESS":
        print(f"成功：{result.final_trans}")
    else:
        print(f"失败：{result.error_detail}")
except Exception as e:
    print(f"异常：{e}")
finally:
    await tm.shutdown()
```

### 2. 批量处理

```python
# 分批处理大量任务
batch_size = 50
for i in range(0, len(tasks), batch_size):
    batch = tasks[i:i + batch_size]
    results = await asyncio.gather(
        *[orchestrator.process_task(t) for t in batch],
        return_exceptions=True
    )
    
    # 定期垃圾回收
    if i % 100 == 0:
        gc.collect()
```

### 3. 资源管理

```python
# 使用 context manager 管理资源
async with TerminologyManager(path, config) as tm:
    # 使用术语库
    result = await tm.find_similar("文本", "英语")

# 自动调用 shutdown() 清理资源
```

### 4. GUI 应用使用

```python
import tkinter as tk
from presentation.gui_app import TranslationApp

def main():
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

## 📊 性能建议

- **缓存命中率**: 目标 > 80%
- **并发度**: 根据 API 限制动态调整（默认 5-10）
- **批处理大小**: 50-100 条/批
- **超时设置**: 30-60 秒
- **内存使用**: 监控峰值，定期 GC
- **GUI 响应**: 使用后台线程执行翻译任务，保持界面流畅

## 🔗 相关资源

- [用户使用指南](../guides/README.md)
- [架构设计文档](../architecture/README.md)
- [故障排查手册](troubleshooting.md)
- [测试总结](../development/TEST_SUMMARY.md)
- [GitHub 仓库](https://github.com/your-repo/translation)

---

**最后更新**: 2026-03-20  
**版本**: 2.0.0
