# 服务层文档

## 📋 概述

`service/` 模块负责 API 提供商管理和翻译历史管理。

## 📁 文件结构

```
service/
├── __init__.py              # 模块导出
├── api_provider.py          # API 提供商管理
└── translation_history.py   # 翻译历史管理
```

## 🔧 核心服务

### 1. API Provider (API 提供商)

#### get_provider_manager()

获取 API 提供商管理器。

**功能**:
- 管理多个 API 提供商配置
- 动态切换 API 提供商
- 创建 API 客户端

**使用示例**:

```python
from translation import get_provider_manager

manager = get_provider_manager()

# 查看可用提供商
providers = manager.get_available_providers()
print(f"可用提供商：{providers}")

# 切换提供商
await manager.switch_provider("DeepSeek")

# 创建客户端
client = await manager.create_api_client()
```

#### switch_provider(provider_name)

切换 API 提供商。

**参数**:
- `provider_name`: 提供商名称 (如 "DeepSeek")

**示例**:

```python
from translation import get_provider_manager

manager = get_provider_manager()
await manager.switch_provider("DeepSeek")
```

### 2. Translation History Manager (翻译历史管理器)

#### get_history_manager()

获取翻译历史管理器。

**功能**:
- 记录所有翻译历史
- 查询历史记录
- 生成统计报告

**使用示例**:

```python
from translation import get_history_manager

history_manager = get_history_manager()

# 查询最近记录
records = history_manager.get_recent_records(limit=100)

# 获取统计信息
stats = history_manager.get_statistics()
print(f"总记录数：{stats['total_count']}")
print(f"成功率：{stats['success_rate']:.2%}")
```

#### get_recent_records(limit=100)

获取最近的翻译记录。

**参数**:
- `limit`: 记录数量限制 (默认 100)

**返回**:
- List[Dict]: 历史记录列表

**字段说明**:
- `id`: 记录 ID
- `timestamp`: 时间戳
- `source_text`: 源文本
- `target_lang`: 目标语言
- `translation`: 翻译结果
- `status`: 状态

**示例**:

```python
records = history_manager.get_recent_records(limit=50)
for r in records:
    print(f"{r['timestamp']}: {r['source_text']} -> {r['translation']}")
```

#### get_statistics()

获取翻译统计信息。

**返回**:
- Dict[str, Any]: 统计字典

**字段说明**:
- `total_count`: 总记录数
- `success_count`: 成功数
- `failed_count`: 失败数
- `success_rate`: 成功率
- `avg_response_time`: 平均响应时间

**示例**:

```python
stats = history_manager.get_statistics()
print(f"""
翻译统计:
- 总记录：{stats['total_count']}
- 成功：{stats['success_count']}
- 失败：{stats['failed_count']}
- 成功率：{stats['success_rate']:.2%}
- 平均响应：{stats['avg_response_time']:.2f}s
""")
```

## 📖 完整使用示例

### 1. API 提供商管理

```python
import asyncio
from translation import get_provider_manager, Config

async def manage_api():
    config = Config(api_key="your-key")
    
    # 获取管理器
    manager = get_provider_manager()
    
    # 查看可用提供商
    providers = manager.get_available_providers()
    print(f"可用提供商：{providers}")
    
    # 切换到 DeepSeek
    await manager.switch_provider("DeepSeek")
    
    # 创建客户端
    client = await manager.create_api_client()
    
    # 使用客户端调用 API
    response = await client.translate(
        text="你好",
        target_lang="英语"
    )
    
    print(f"翻译结果：{response}")

asyncio.run(manage_api())
```

### 2. 翻译历史查询

```python
import asyncio
from translation import get_history_manager

async def query_history():
    history_manager = get_history_manager()
    
    # 查询最近 100 条记录
    records = history_manager.get_recent_records(limit=100)
    
    # 筛选成功的记录
    success_records = [r for r in records if r['status'] == 'SUCCESS']
    print(f"成功记录：{len(success_records)}")
    
    # 按语言分组
    by_language = {}
    for r in records:
        lang = r['target_lang']
        if lang not in by_language:
            by_language[lang] = []
        by_language[lang].append(r)
    
    for lang, items in by_language.items():
        print(f"{lang}: {len(items)}条")
    
    # 获取统计信息
    stats = history_manager.get_statistics()
    print(f"成功率：{stats['success_rate']:.2%}")

asyncio.run(query_history())
```

## 💡 最佳实践

### 1. API 切换

```python
# ✅ 好的做法：检查提供商是否存在
manager = get_provider_manager()
if "DeepSeek" in manager.get_available_providers():
    await manager.switch_provider("DeepSeek")

# ❌ 不好的做法：直接切换不检查
await manager.switch_provider("UnknownProvider")  # 可能报错
```

### 2. 历史查询

```python
# ✅ 好的做法：添加异常处理
try:
    records = history_manager.get_recent_records(limit=100)
    for r in records:
        print(r['source_text'])
except Exception as e:
    print(f"查询失败：{e}")

# ❌ 不好的做法：不处理异常
records = history_manager.get_recent_records(limit=100)
for r in records:
    print(r['source_text'])  # 可能因为字段不存在而报错
```

## 🔗 相关文档

- [架构设计](../architecture/ARCHITECTURE.md)
- [API 参考](../api/MODEL_CONFIG_API.md)
- [快速开始](../guides/QUICKSTART.md)
