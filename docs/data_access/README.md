# 数据访问层文档

## 📑 目录

- [📋 概述](#概述)
- [📁 文件结构](#文件结构)
- [🔧 核心类](#核心类)
  - [1. ConfigPersistence (配置持久化)](#1-configpersistence-配置持久化)
    - [功能说明](#功能说明)
    - [使用示例](#使用示例)
    - [主要方法](#主要方法)
  - [2. FuzzyMatcher (模糊匹配器)](#2-fuzzymatcher-模糊匹配器)
    - [功能说明](#功能说明)
    - [使用示例](#使用示例)
    - [主要方法](#主要方法)
- [📖 完整使用示例](#完整使用示例)
  - [1. 配置管理](#1-配置管理)
  - [2. 模糊匹配](#2-模糊匹配)
- [💡 最佳实践](#最佳实践)
  - [1. 配置加载](#1-配置加载)
  - [2. 模糊匹配阈值](#2-模糊匹配阈值)
- [🔗 相关文档](#相关文档)

---

## 📋 概述

`data_access/` 模块负责配置文件读写、术语导入和模糊匹配算法。

## 📁 文件结构

```
data_access/
├── __init__.py              # 模块导出
├── config_persistence.py    # 配置持久化
├── terminology_update.py    # 术语更新
└── fuzzy_matcher.py         # 模糊匹配
```

## 🔧 核心类

### 1. ConfigPersistence (配置持久化)

#### 功能说明

负责配置文件的加载和保存，支持 JSON 和 YAML 格式。

#### 使用示例

```python
from translation import ConfigPersistence

persistence = ConfigPersistence()

# 加载 JSON 配置
config_dict = persistence.load_json("config/config.json")
print(f"API Key: {config_dict['api_key']}")

# 保存配置
new_config = {"api_key": "new-key"}
persistence.save_json("config/config.json", new_config)
```

#### 主要方法

##### load_json(filepath)

加载 JSON 配置文件。

**参数**:
- `filepath`: 文件路径

**返回**:
- Dict: 配置字典

**示例**:
```python
config = persistence.load_json("config/config.json")
```

##### save_json(filepath, data)

保存 JSON 配置文件。

**参数**:
- `filepath`: 文件路径
- `data`: 配置字典

**示例**:
```python
persistence.save_json(
    "config/config.json",
    {"api_key": "your-key"}
)
```

### 2. FuzzyMatcher (模糊匹配器)

#### 功能说明

基于编辑距离的模糊匹配算法，用于术语库查询。

#### 使用示例

```python
from translation import FuzzyMatcher

matcher = FuzzyMatcher()

# 计算相似度
similarity = matcher.calculate_similarity("紫钻", "紫色钻石")
print(f"相似度：{similarity:.2%}")

# 查找最佳匹配
best_match = matcher.find_best_match(
    query="紫色钻石",
    candidates=["紫钻", "蓝钻", "红钻"]
)
print(f"最佳匹配：{best_match}")
```

#### 主要方法

##### calculate_similarity(s1, s2)

计算两个字符串的相似度。

**参数**:
- `s1`: 字符串 1
- `s2`: 字符串 2

**返回**:
- float: 相似度 (0-1)

**示例**:
```python
similarity = matcher.calculate_similarity("你好", "您好")
print(f"相似度：{similarity:.2%}")  # 输出：66.67%
```

##### find_best_match(query, candidates, threshold=0.5)

从候选列表中查找最佳匹配。

**参数**:
- `query`: 查询字符串
- `candidates`: 候选列表
- `threshold`: 匹配阈值 (默认 0.5)

**返回**:
- str or None: 最佳匹配，如果没有达到阈值的匹配则返回 None

**示例**:
```python
best = matcher.find_best_match(
    query="紫色钻石",
    candidates=["紫钻", "蓝钻", "红钻"],
    threshold=0.6
)
print(f"最佳匹配：{best}")  # 输出：紫钻
```

## 📖 完整使用示例

### 1. 配置管理

```python
from translation import ConfigPersistence

persistence = ConfigPersistence()

# 加载配置
config = persistence.load_json("config/config.json")

# 修改配置
config["temperature"] = 0.5

# 保存配置
persistence.save_json("config/config.json", config)

print("配置已更新")
```

### 2. 模糊匹配

```python
from translation import FuzzyMatcher

matcher = FuzzyMatcher()

# 测试不同相似度
test_cases = [
    ("紫钻", "紫钻"),      # 完全相同
    ("紫钻", "紫色钻石"),   # 相似
    ("紫钻", "蓝钻"),      # 部分相似
    ("紫钻", "红宝石"),     # 不相似
]

for s1, s2 in test_cases:
    similarity = matcher.calculate_similarity(s1, s2)
    print(f"{s1} vs {s2}: {similarity:.2%}")

# 查找最佳匹配
query = "紫色钻石"
candidates = ["紫钻", "蓝钻", "红钻", "红宝石"]
best_match = matcher.find_best_match(query, candidates, threshold=0.5)

if best_match:
    print(f"\n'{query}' 的最佳匹配是：{best_match}")
else:
    print(f"\n未找到 '{query}' 的匹配项")
```

## 💡 最佳实践

### 1. 配置加载

```python
# ✅ 好的做法：添加异常处理
try:
    config = persistence.load_json("config/config.json")
except FileNotFoundError:
    print("配置文件不存在，使用默认配置")
    config = {}

# ❌ 不好的做法：不处理异常
config = persistence.load_json("config/config.json")
```

### 2. 模糊匹配阈值

```python
# ✅ 好的做法：根据场景选择合适的阈值
# 精确匹配场景
exact_match = matcher.find_best_match(query, candidates, threshold=0.8)

# 宽松匹配场景
fuzzy_match = matcher.find_best_match(query, candidates, threshold=0.4)

# ❌ 不好的做法：总是使用固定阈值
match = matcher.find_best_match(query, candidates, threshold=0.5)
```

## 🔗 相关文档

- [架构设计](../architecture/ARCHITECTURE.md)
- [配置管理](../../config/README.md)
- [快速开始](../guides/QUICKSTART.md)
