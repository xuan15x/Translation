# 应用层文档 (Application Layer)

## 📑 目录

- [📋 概述](#-概述)
  - [核心职责](#核心职责)
- [📁 文件结构](#-文件结构)
- [🔧 核心组件](#-核心组件)
  - [1. TranslationServiceFacade (外观模式)](#1-translationservicefacade-外观模式)
    - [功能说明](#功能说明)
    - [使用示例](#使用示例)
    - [主要方法](#主要方法)
  - [2. TranslationWorkflowCoordinator (工作流协调器)](#2-translationworkflowcoordinator-工作流协调器)
    - [功能说明](#功能说明)
    - [主要方法](#主要方法)
  - [3. BatchTaskProcessor (批量处理器)](#3-batchtaskprocessor-批量处理器)
    - [功能说明](#功能说明)
    - [主要方法](#主要方法)
  - [4. ResultBuilder (结果构建器)](#4-resultbuilder-结果构建器)
    - [功能说明](#功能说明)
    - [主要方法](#主要方法)
- [📖 完整使用示例](#-完整使用示例)
  - [示例 1: 使用外观服务](#示例-1-使用外观服务)
  - [示例 2: 自定义工作流](#示例-2-自定义工作流)
- [💡 最佳实践](#-最佳实践)
  - [1. 使用外观模式简化调用](#1-使用外观模式简化调用)
  - [2. 批量操作优于单个操作](#2-批量操作优于单个操作)
  - [3. 使用进度回调](#3-使用进度回调)
- [🔗 相关文档](#-相关文档)

---

## 📋 概述

`application/` 模块负责**流程编排和业务协调**，是六层架构中的关键一层。

### 核心职责

1. **流程编排** - 协调领域服务完成复杂业务
2. **外观模式** - 提供简化的 API 接口
3. **批量处理** - 并发控制和进度跟踪
4. **结果构建** - 数据格式转换和导出

---

## 📁 文件结构

```
application/
├── __init__.py                    # 模块导出
├── translation_facade.py          # 外观模式 ⭐
├── workflow_coordinator.py        # 工作流协调器
├── batch_processor.py             # 批量处理器
└── result_builder.py              # 结果构建器
```

---

## 🔧 核心组件

### 1. TranslationServiceFacade (外观模式)

#### 功能说明

为 GUI 或 CLI 提供简化的 API，隐藏内部复杂性。

**设计模式**: Facade Pattern（外观模式）

#### 使用示例

```python
from application.translation_facade import TranslationServiceFacade

# 通过依赖注入容器获取
facade = container.get('translation_facade')

# 一行代码完成复杂翻译
result = await facade.translate_file(
    source_excel_path="source.xlsx",
    target_langs=["en", "ja", "ko"],
    concurrency_limit=10
)

print(f"成功率：{result.success_rate:.1f}%")
```

#### 主要方法

##### translate_file(source_excel_path, target_langs, output_excel_path, concurrency_limit)

翻译 Excel 文件。

**参数**:
- `source_excel_path`: 源 Excel 文件路径
- `target_langs`: 目标语言列表
- `output_excel_path`: 输出路径（可选）
- `concurrency_limit`: 并发限制（默认 10）

**返回**:
- `BatchResult`: 批量翻译结果

##### translate_text(text, target_lang, source_lang)

翻译单个文本。

**参数**:
- `text`: 待翻译文本
- `target_lang`: 目标语言
- `source_lang`: 源语言（默认中文）

**返回**:
- `str`: 翻译结果

##### get_statistics(excel_path, target_langs)

获取文件统计信息。

**返回**:
- `dict`: 统计信息字典

---

### 2. TranslationWorkflowCoordinator (工作流协调器)

#### 功能说明

协调领域服务执行完整的翻译工作流。

#### 主要方法

##### execute_task(task)

执行单个翻译任务。

**流程**:
1. 查询术语库 → TerminologyDomainService
2. 如有匹配 → 直接使用术语
3. 如无匹配 → 调用翻译服务
4. 保存新术语 → TerminologyDomainService
5. 返回结果

##### execute_batch(tasks)

批量执行任务。

---

### 3. BatchTaskProcessor (批量处理器)

#### 功能说明

负责批量任务的并发控制和进度跟踪。

#### 主要方法

##### process_batch(tasks)

处理批量任务。

**特性**:
- ✅ 自适应并发控制
- ✅ 实时进度回调
- ✅ 错误重试机制
- ✅ 性能监控

---

### 4. ResultBuilder (结果构建器)

#### 功能说明

负责结果数据的格式转换和导出。

#### 主要方法

##### to_dataframe(results)

转换为 pandas DataFrame。

##### to_excel(results, output_path)

导出到 Excel 文件。

##### print_summary(batch_result)

打印汇总报告。

---

## 📖 完整使用示例

### 示例 1: 使用外观服务

```python
import asyncio
from infrastructure.di_container import initialize_container

async def main():
    # 初始化容器
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

asyncio.run(main())
```

### 示例 2: 自定义工作流

```python
from application.workflow_coordinator import TranslationWorkflowCoordinator
from domain.terminology_service_impl import TerminologyDomainService
from domain.translation_service_impl import TranslationDomainServiceImpl

# 创建服务
term_service = TerminologyDomainService(repo=term_repo)
trans_service = TranslationDomainServiceImpl(client, term_service, ...)

# 创建协调器
coordinator = TranslationWorkflowCoordinator(
    terminology_service=term_service,
    translation_service=trans_service,
    batch_processor=None
)

# 执行任务
task = TranslationTask(...)
result = await coordinator.execute_task(task)
```

---

## 💡 最佳实践

### 1. 使用外观模式简化调用

```python
# ✅ 推荐：使用外观服务
facade = container.get('translation_facade')
result = await facade.translate_file(...)

# ❌ 不推荐：手动协调多个服务
term_service = container.get('terminology_service')
trans_service = container.get('translation_service')
coordinator = TranslationWorkflowCoordinator(...)
```

### 2. 批量操作优于单个操作

```python
# ✅ 推荐：批量查询
queries = [("你好", "en"), ("世界", "en")]
results = await term_service.find_matches_batch(queries)

# ❌ 不推荐：逐个查询
for source, lang in queries:
    result = await term_service.find_match(source, lang)
```

### 3. 使用进度回调

```python
def on_progress(current, total):
    logger.info(f"进度：{current}/{total}")

facade.set_progress_callback(on_progress)
```

---

## 🔗 相关文档

- [领域层](../domain/README.md) - 核心业务逻辑
- [基础设施层](../infrastructure/README.md) - 依赖注入容器
- [快速开始](../guides/QUICKSTART.md) - 使用指南
