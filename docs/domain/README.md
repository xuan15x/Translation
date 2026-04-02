# 领域层文档 (Domain Layer)

## 📑 目录

- [📋 概述](#概述)
  - [核心特性](#核心特性)
- [📁 文件结构](#文件结构)
- [🎯 领域模型](#领域模型)
  - [TranslationTask (翻译任务)](#translationtask-翻译任务)
  - [BatchResult (批量结果)](#batchresult-批量结果)
- [🔧 领域服务](#领域服务)
  - [1. TerminologyDomainService (术语领域服务)](#1-terminologydomainservice-术语领域服务)
    - [功能说明](#功能说明)
    - [使用示例](#使用示例)
    - [主要方法](#主要方法)
  - [2. TranslationDomainServiceImpl (翻译领域服务)](#2-translationdomainserviceimpl-翻译领域服务)
    - [功能说明](#功能说明)
    - [使用示例](#使用示例)
    - [主要方法](#主要方法)
- [💡 最佳实践](#最佳实践)
  - [1. 依赖仓储接口而非实现](#1-依赖仓储接口而非实现)
  - [2. 使用批量操作](#2-使用批量操作)
  - [3. 纯业务逻辑，不含技术细节](#3-纯业务逻辑不含技术细节)
- [🏗️ 架构位置](#️-架构位置)
- [🔗 相关文档](#相关文档)

---

## 📋 概述

`domain/` 模块包含**纯业务逻辑**，是六层架构的核心。这一层不依赖任何外部框架或基础设施。

### 核心特性

1. **纯业务逻辑** - 只包含业务规则，无技术细节
2. **零外部依赖** - 不依赖数据库、API、UI 等
3. **接口隔离** - 通过接口与外部通信
4. **高度可测试** - 易于编写单元测试

---

## 📁 文件结构

```
domain/
├── __init__.py                    # 模块导出
├── models.py                      # 领域模型
├── services.py                    # 服务接口
├── terminology_service_impl.py    # 术语服务实现 ⭐
└── translation_service_impl.py    # 翻译服务实现 ⭐
```

---

## 🎯 领域模型

### TranslationTask (翻译任务)

```python
@dataclass
class TranslationTask:
    idx: int                      # 索引
    key: str                      # 唯一标识
    source_text: str              # 原文
    original_trans: Optional[str] # 原译文
    target_lang: str              # 目标语言
    source_lang: str              # 源语言
```

### BatchResult (批量结果)

```python
@dataclass
class BatchResult:
    results: List[TranslationResult]  # 结果列表
    success_count: int                # 成功数
    fail_count: int                   # 失败数
    success_rate: float               # 成功率
```

---

## 🔧 领域服务

### 1. TerminologyDomainService (术语领域服务)

#### 功能说明

处理术语相关的纯业务逻辑。

**设计原则**: 
- ✅ 单一职责 - 只负责术语业务
- ✅ 依赖倒置 - 依赖仓储接口
- ✅ 接口隔离 - 提供专用接口

#### 使用示例

```python
from domain.terminology_service_impl import TerminologyDomainService
from data_access.repositories import TerminologyRepository

# 初始化（依赖仓储接口）
term_service = TerminologyDomainService(repo=term_repo)

# 查询术语匹配
result = await term_service.find_match("你好", "en")
if result:
    print(f"英语：{result.translation}")

# 保存新术语
await term_service.save_term("友好", "en", "Friendly")
```

#### 主要方法

##### find_match(source_text, target_lang)

查找术语匹配（精确优先）。

**参数**:
- `source_text`: 源文本
- `target_lang`: 目标语言

**返回**:
- `Optional[TermMatch]`: 术语匹配结果

##### find_matches_batch(queries)

批量查找术语匹配。

**参数**:
- `queries`: `[(source_text, target_lang), ...]`

**返回**:
- `List[TermMatch]`: 匹配结果列表

##### save_term(source_text, target_lang, translation)

保存术语。

**参数**:
- `source_text`: 源文本
- `target_lang`: 目标语言
- `translation`: 译文

##### save_terms_batch(terms)

批量保存术语。

**参数**:
- `terms`: `[(source_text, target_lang, translation), ...]`

---

### 2. TranslationDomainServiceImpl (翻译领域服务)

#### 功能说明

处理翻译相关的核心业务逻辑。

#### 使用示例

```python
from domain.translation_service_impl import TranslationDomainServiceImpl

# 初始化翻译服务
trans_service = TranslationDomainServiceImpl(
    client=api_client,
    terminology_service=term_service,
    draft_prompt=DRAFT_PROMPT,
    review_prompt=REVIEW_PROMPT
)

# 执行翻译
task = TranslationTask(...)
result = await trans_service.translate(task)
```

#### 主要方法

##### translate(task)

执行初译。

**流程**:
1. 构建提示词（集成术语建议）
2. 调用 API
3. 解析响应
4. 返回结果

##### proofread(task, draft_translation)

执行校对。

**流程**:
1. 对比原文和初译
2. 调用 API 校对
3. 返回优化后的译文

---

## 💡 最佳实践

### 1. 依赖仓储接口而非实现

```python
# ✅ 推荐：依赖接口
class TerminologyDomainService:
    def __init__(self, repo: ITermRepository):
        self.repo = repo  # ← 依赖抽象接口

# ❌ 不推荐：依赖具体实现
class TerminologyDomainService:
    def __init__(self, repo: TerminologyRepository):
        self.repo = repo  # ← 依赖具体类
```

### 2. 使用批量操作

```python
# ✅ 推荐：批量查询
queries = [("你好", "en"), ("世界", "en")]
results = await term_service.find_matches_batch(queries)

# ❌ 不推荐：逐个查询
for source, lang in queries:
    result = await term_service.find_match(source, lang)
```

### 3. 纯业务逻辑，不含技术细节

```python
# ✅ 推荐：领域服务只关心业务规则
async def find_match(self, source_text, target_lang):
    return await self.repo.find_by_source(source_text, target_lang)

# ❌ 不推荐：在领域服务中处理数据库连接
async def find_match(self, source_text, target_lang):
    conn = sqlite3.connect(...)  # ← 不应该在这里做
    cursor = conn.cursor()
    ...
```

---

## 🏗️ 架构位置

```
Presentation Layer (表示层)
    ↓
Application Layer (应用层)
    ↓
Domain Layer (领域层) ← 纯业务逻辑
    ↓
Service Layer (服务层)
    ↓
Data Access Layer (数据访问层)
    ↓
Infrastructure Layer (基础设施层)
```

---

## 🔗 相关文档

- [应用层](../application/README.md) - 流程编排
- [数据访问层](../data_access/README.md) - 仓储实现
- [架构设计](../architecture/ARCHITECTURE.md) - 六层架构详解
