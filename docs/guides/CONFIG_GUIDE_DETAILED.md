# 配置使用指南

本指南帮助您快速理解和配置 AI 智能翻译工作台的各项参数。

## 📋 目录

1. [快速开始](#快速开始)
2. [API 配置](#api-配置)
3. [模型参数](#模型参数)
4. [双阶段翻译](#双阶段翻译)
5. [并发控制](#并发控制)
6. [性能优化](#性能优化)
7. [常见问题](#常见问题)

---

## 🚀 快速开始

### 第一步：复制配置文件

```bash
# 复制示例配置文件
cp config/config.example.yaml config/config.yaml
```

### 第二步：设置 API 密钥

**推荐方式（使用环境变量）：**

```bash
# Linux/Mac
export DEEPSEEK_API_KEY="sk-your-api-key-here"

# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-your-api-key-here"
```

**或者在配置文件中设置：**

```yaml
api_key: "sk-your-api-key-here"
```

### 第三步：验证配置

```bash
python scripts/check_config.py check config/config.yaml
```

---

## 🔑 API 配置

### api_provider - API 提供商

**可选值：**
- `deepseek` - DeepSeek（推荐）
- `openai` - OpenAI
- `moonshot` - Moonshot (Kimi)
- `zhipu` - Zhipu AI (智谱)
- `baidu` - Baidu (文心一言)
- `alibaba` - Alibaba (通义千问)
- `anthropic` - Anthropic

**示例：**
```yaml
api_provider: "deepseek"
```

### base_url - API 端点

通常不需要修改，系统会根据提供商自动设置。

**常见提供商的 base_url：**
```yaml
deepseek: "https://api.deepseek.com"
openai: "https://api.openai.com/v1"
moonshot: "https://api.moonshot.cn/v1"
zhipu: "https://open.bigmodel.cn/api/paas/v4"
```

---

## 🎯 模型参数

### model_name - 模型名称

指定使用的 AI 模型。

**常见模型：**
```yaml
# DeepSeek
model_name: "deepseek-chat"      # 对话模型，适合翻译
model_name: "deepseek-coder"     # 代码模型

# OpenAI
model_name: "gpt-3.5-turbo"      # 经济快速
model_name: "gpt-4"              # 高质量
model_name: "gpt-4-turbo"        # 最新最快

# Moonshot
model_name: "moonshot-v1-8k"     # 8K 上下文
model_name: "moonshot-v1-32k"    # 32K 上下文
```

### temperature - 温度参数

**取值范围：** 0.0 - 2.0

**推荐设置：**

| 场景 | 推荐值 | 说明 |
|------|--------|------|
| 技术文档 | 0.1-0.3 | 保守翻译，准确优先 |
| 通用文本 | 0.3-0.5 | 平衡模式（推荐） |
| 文学翻译 | 0.5-0.7 | 创造性翻译 |
| 诗歌广告 | 0.7-1.0 | 高度创意 |

**示例：**
```yaml
temperature: 0.3  # 推荐默认值
```

### top_p - 核采样参数

**取值范围：** 0.0 - 1.0

**推荐设置：**

| 值 | 效果 | 适用场景 |
|----|------|----------|
| 0.7-0.8 | 稳定输出 | 技术文档、法律文本 |
| 0.8-0.9 | 平衡模式 | 通用翻译（推荐） |
| 0.9-1.0 | 高多样性 | 创意写作 |

**示例：**
```yaml
top_p: 0.8  # 推荐默认值
```

---

## 🔄 双阶段翻译

系统采用「初译 + 校对」双阶段模式，可以为每个阶段设置不同的模型参数。

### 为什么要使用双阶段？

- **初译**：快速翻译，注重准确性
- **校对**：润色优化，注重流畅性

### 配置示例

```yaml
# 初译阶段 - 使用保守参数
draft_model_name: "deepseek-chat"
draft_temperature: 0.3  # 保守翻译
draft_top_p: 0.8

# 校对阶段 - 使用灵活参数
review_model_name: "gpt-4"
review_temperature: 0.6  # 灵活润色
review_top_p: 0.9
```

### 何时使用不同模型？

**经济方案：**
```yaml
draft_model_name: "deepseek-chat"   # 快速经济
review_model_name: "deepseek-chat"  # 同一模型
```

**高质量方案：**
```yaml
draft_model_name: "deepseek-chat"   # 初译
review_model_name: "gpt-4"          # 高质量校对
```

---

## ⚡ 并发控制

### initial_concurrency - 初始并发数

**推荐设置：**
- API 限制较严：4-6
- 一般情况：8-10（推荐）
- API 限制宽松：10-15

**示例：**
```yaml
initial_concurrency: 8  # 推荐起始值
```

### max_concurrency - 最大并发数

**推荐设置：**
- 保守策略：8-10
- 平衡策略：10-15（推荐）
- 激进策略：15-20

**示例：**
```yaml
max_concurrency: 10  # 推荐最大值
```

### concurrency_cooldown_seconds - 冷却时间

当遇到 API 限制时，降低并发度后的冷却时间。

**推荐设置：** 3-10 秒

**示例：**
```yaml
concurrency_cooldown_seconds: 5.0
```

---

## 🚀 性能优化

### cache_capacity - 缓存容量

**推荐设置：**
- 小型项目（<1000 条）：500-1000
- 中型项目（1000-5000 条）：2000-3000（推荐）
- 大型项目（>5000 条）：5000-10000

**示例：**
```yaml
cache_capacity: 2000  # 推荐默认值
```

### cache_ttl_seconds - 缓存过期时间

**推荐设置：**
- 频繁修改：600-1800（10-30 分钟）
- 一般情况：3600（1 小时，推荐）
- 稳定内容：7200-14400（2-4 小时）

**示例：**
```yaml
cache_ttl_seconds: 3600  # 1 小时
```

### pool_size - 数据库连接池大小

**推荐设置：**
- 单用户：3-5
- 多用户：5-10（推荐）
- 高并发：10-20

**示例：**
```yaml
pool_size: 5  # 推荐默认值
```

---

## 📊 日志配置

### log_level - 日志级别

**可选值：**
- `DEBUG` - 调试模式，输出所有信息
- `INFO` - 信息模式（推荐）
- `WARNING` - 警告模式
- `ERROR` - 错误模式
- `CRITICAL` - 严重错误模式

**示例：**
```yaml
log_level: "INFO"  # 推荐
```

### log_granularity - 日志粒度

**可选值：**
- `minimal` - 最少日志
- `basic` - 基础日志
- `normal` - 正常日志（推荐）
- `detailed` - 详细日志
- `verbose` - 详尽日志

**示例：**
```yaml
log_granularity: "normal"  # 推荐
```

---

## ❓ 常见问题

### Q1: 如何设置 API 密钥最安全？

**A:** 使用环境变量是最安全的方式：

```bash
# Linux/Mac
export DEEPSEEK_API_KEY="your-key"

# Windows
set DEEPSEEK_API_KEY=your-key
```

然后在配置文件中留空：
```yaml
api_key: ""  # 从环境变量读取
```

### Q2: 翻译速度慢怎么办？

**A:** 调整以下参数：

```yaml
# 增加并发
initial_concurrency: 10
max_concurrency: 15

# 减少超时
timeout: 30

# 使用更快的模型
model_name: "gpt-3.5-turbo"
```

### Q3: 翻译质量不理想？

**A:** 调整模型参数：

```yaml
# 提高温度（更有创意）
temperature: 0.5

# 增加 top_p（更多样性）
top_p: 0.9

# 使用更强的模型
model_name: "gpt-4"
```

### Q4: 如何为不同语言设置不同模型？

**A:** 目前不支持按语言区分模型，但可以通过双阶段实现：

```yaml
# 初译用经济模型
draft_model_name: "deepseek-chat"

# 校对用高质量模型（针对重要语言）
review_model_name: "gpt-4"
```

### Q5: 配置修改后需要重启吗？

**A:** 是的，配置修改后需要重启程序才能生效。

```bash
# 重启翻译平台
python presentation/translation.py
```

---

## 🔧 配置检查工具

使用配置检查工具验证配置是否正确：

```bash
# 检查配置文件
python scripts/check_config.py check config/config.yaml

# 查看详细报告
python scripts/check_config.py check config/config.yaml --verbose
```

---

## 📝 配置模板

### 经济快速配置

```yaml
api_provider: "deepseek"
model_name: "deepseek-chat"
temperature: 0.3
top_p: 0.8
initial_concurrency: 10
max_concurrency: 15
```

### 高质量配置

```yaml
api_provider: "openai"
model_name: "gpt-4"
temperature: 0.5
top_p: 0.9
draft_model_name: "gpt-3.5-turbo"
review_model_name: "gpt-4"
initial_concurrency: 8
max_concurrency: 10
```

### 技术文档配置

```yaml
api_provider: "deepseek"
model_name: "deepseek-chat"
temperature: 0.2  # 保守翻译
top_p: 0.7       # 稳定输出
draft_max_tokens: 300
review_max_tokens: 300
```

---

**最后更新:** 2026-04-01  
**版本:** v2.0
