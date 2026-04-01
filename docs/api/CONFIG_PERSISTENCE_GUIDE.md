# 配置持久化使用指南

## 📋 概述

项目现已支持使用 JSON 或 YAML 格式保存和加载配置，方便管理和部署。

## 🎯 功能特性

✅ **支持格式**: JSON (.json), YAML (.yaml, .yml)  
✅ **环境变量覆盖**: 配置文件可与环境变量合并  
✅ **GUI 集成**: 可通过界面加载/保存配置  
✅ **命令行参数**: 启动时可指定配置文件  
✅ **类型安全**: 自动验证配置项类型  

---

## 🚀 快速开始

### 方法 1: 使用示例配置文件

1. **复制示例文件**
```bash
# JSON 格式
cp config.example.json config.json

# YAML 格式（推荐）
cp config.example.yaml config.yaml
```

2. **编辑配置文件**
打开 `config.json` 或 `config.yaml`，修改为你的配置：
```json
{
  "api_key": "sk-your-actual-api-key",
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-chat"
}
```

3. **启动应用**
```bash
# 自动查找默认配置文件
python translation.py

# 或指定配置文件
python translation.py config.json
```

### 方法 2: 通过 GUI 加载/保存

1. 启动应用后，点击 **"⚙️ 提示词配置"** 区域
2. 点击 **"📂 加载配置"** 选择配置文件
3. 点击 **"💾 保存配置"** 保存当前配置

---

## 📁 配置文件格式

### JSON 格式示例 (config.json)

```json
{
  "api_key": "your_api_key_here",
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-chat",
  "temperature": 0.3,
  "top_p": 0.8,
  "initial_concurrency": 8,
  "max_concurrency": 10,
  "retry_streak_threshold": 3,
  "base_retry_delay": 3.0,
  "max_retries": 3,
  "timeout": 60,
  "enable_two_pass": true,
  "skip_review_if_local_hit": true,
  "batch_size": 1000,
  "gc_interval": 2,
  "similarity_low": 60,
  "exact_match_score": 100,
  "multiprocess_threshold": 1000,
  "concurrency_cooldown_seconds": 5.0
}
```

### YAML 格式示例 (config.yaml) - 推荐

```yaml
# API 配置
api_key: "your_api_key_here"
base_url: "https://api.deepseek.com"
model_name: "deepseek-chat"

# 模型参数
temperature: 0.3
top_p: 0.8

# 并发控制
initial_concurrency: 8
max_concurrency: 10
concurrency_cooldown_seconds: 5.0

# 重试配置
retry_streak_threshold: 3
base_retry_delay: 3.0
max_retries: 3
timeout: 60

# 工作流配置
enable_two_pass: true
skip_review_if_local_hit: true
batch_size: 1000
gc_interval: 2

# 术语库配置
similarity_low: 60
exact_match_score: 100
multiprocess_threshold: 1000
```

---

## 💻 编程接口

### 从配置文件加载

```python
from models import Config

# 从 JSON 文件加载
config = Config.from_file("config.json")

# 从 YAML 文件加载
config = Config.from_file("config.yaml")

# 不使用环境变量覆盖
config = Config.from_file("config.json", use_env=False)
```

### 保存配置到文件

```python
from models import Config

# 创建配置对象
config = Config(
    api_key="your_key",
    temperature=0.5,
    # ... 其他参数
)

# 保存到 JSON 文件
config.save("my_config.json")

# 保存到 YAML 文件
config.save("my_config.yaml")
```

### 使用 ConfigPersistence 类

```python
from config_persistence import ConfigPersistence

# 创建持久化管理器
persistence = ConfigPersistence("config.json")

# 加载配置
config_dict = persistence.load()

# 获取单个配置值
api_key = persistence.get("api_key", default="default_key")

# 设置配置值
persistence.set("temperature", 0.7)

# 保存配置
persistence.save(config_dict)
```

---

## 🔧 高级用法

### 环境变量优先级

配置的优先级顺序（从高到低）：

1. **环境变量** (如果启用 `use_env=True`)
2. **配置文件值**
3. **代码默认值**

示例：
```bash
# 设置环境变量会覆盖配置文件
export DEEPSEEK_API_KEY="env_api_key"

# 即使 config.json 中有不同的值，也会使用环境变量
python translation.py config.json
```

### 嵌套配置支持

```python
from config_persistence import ConfigPersistence

persistence = ConfigPersistence("config.json")

# 访问嵌套配置
base_url = persistence.get("api.base_url")

# 设置嵌套配置
persistence.set("api.model_name", "deepseek-chat")
```

### 批量更新

```python
updates = {
    "temperature": 0.7,
    "max_concurrency": 15
}

persistence.update(updates)
persistence.save(persistence._config_cache)
```

---

## 🛠️ 工具函数

### 便捷函数

```python
from config_persistence import load_config, save_config, create_sample_config

# 加载配置
config = load_config("config.json")

# 保存配置
save_config({"api_key": "key"}, "config.json")

# 创建示例配置
create_sample_config("sample_config.yaml")
```

---

## 📝 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `api_key` | str | - | DeepSeek API 密钥 |
| `base_url` | str | https://api.deepseek.com | API 基础 URL |
| `model_name` | str | deepseek-chat | 使用的模型名称 |
| `temperature` | float | 0.3 | 生成创造性程度 (0-1) |
| `top_p` | float | 0.8 | 核采样参数 |
| `initial_concurrency` | int | 8 | 初始并发数 |
| `max_concurrency` | int | 10 | 最大并发数 |
| `retry_streak_threshold` | int | 3 | 连续失败阈值 |
| `base_retry_delay` | float | 3.0 | 基础重试延迟（秒） |
| `max_retries` | int | 3 | 最大重试次数 |
| `timeout` | int | 60 | 请求超时时间（秒） |
| `enable_two_pass` | bool | true | 启用双阶段处理 |
| `skip_review_if_local_hit` | bool | true | 本地命中跳过校对 |
| `batch_size` | int | 1000 | 批处理大小 |
| `gc_interval` | int | 2 | 垃圾回收间隔 |
| `similarity_low` | int | 60 | 模糊匹配最低相似度 |
| `exact_match_score` | int | 100 | 精确匹配置信度 |
| `multiprocess_threshold` | int | 1000 | 多进程处理阈值 |
| `concurrency_cooldown_seconds` | float | 5.0 | 并发冷却时间 |

---

## 🐛 常见问题

### Q: 配置文件找不到？
A: 确保配置文件在当前工作目录，或使用绝对路径。

### Q: YAML 加载失败？
A: 安装 PyYAML: `pip install pyyaml`

### Q: 如何加密 API Key？
A: 建议使用环境变量：
```bash
export DEEPSEEK_API_KEY="your_key"
```

### Q: 配置文件优先级？
A: 环境变量 > 配置文件 > 默认值

---

## 🎓 最佳实践

1. **不要提交敏感信息**: 将 `config.json` 添加到 `.gitignore`
2. **使用示例文件**: 提供 `config.example.json` 作为模板
3. **版本控制配置**: 记录配置变更历史
4. **环境分离**: 开发、测试、生产使用不同配置

---

## 📚 相关模块

- `config_persistence.py`: 配置持久化核心实现
- `models.py`: Config 类扩展
- `gui_app.py`: GUI 配置管理集成

---

**更新日期**: 2026-03-19  
**版本**: v2.0
