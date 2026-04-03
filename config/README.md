# 配置管理模块文档

**版本**: v3.2.0
**最后更新**: 2026-04-03

## 📑 目录

- [📋 概述](#-概述)
- [📁 文件结构](#-文件结构)
- [🔧 配置项说明](#-配置项说明)
  - [Python 配置常量 (config.py)](#python-配置常量-configpy)
    - [DEFAULT_DRAFT_PROMPT](#default_draft_prompt)
    - [DEFAULT_REVIEW_PROMPT](#default_review_prompt)
    - [TARGET_LANGUAGES](#target_languages)
    - [GUI_CONFIG](#gui_config)
  - [JSON 配置文件示例](#json-配置文件示例)
  - [YAML 配置文件示例](#yaml-配置文件示例)
- [📖 使用方法](#-使用方法)
  - [1. 创建配置文件](#1-创建配置文件)
  - [2. 编辑配置](#2-编辑配置)
  - [3. 在 GUI 中加载](#3-在-gui-中加载)
  - [4. 使用环境变量](#4-使用环境变量)
- [🔒 安全提示](#-安全提示)
- [💡 最佳实践](#-最佳实践)
- [📊 配置项详解](#-配置项详解)
  - [API 配置](#api-配置)
  - [翻译配置](#翻译配置)
  - [并发控制](#并发控制)
  - [重试配置](#重试配置)
- [🔗 相关文档](#-相关文档)

---

## 📋 概述

`config/` 模块包含所有项目配置文件和常量定义，便于统一管理和修改。

## 📁 文件结构

```
config/
├── __init__.py         # 模块导出
├── config.py           # Python 配置常量
├── config.example.json # JSON 配置示例
├── config.example.yaml # YAML 配置示例
└── README.md          # 使用说明
```

## 🔧 配置项说明

### Python 配置常量 (config.py)

#### DEFAULT_DRAFT_PROMPT
初译提示词模板，用于第一阶段翻译。

```python
DEFAULT_DRAFT_PROMPT = """Role: Professional Translator.
Task: Translate 'Src' to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Strictly follow provided TM.
3. Accurate and direct."""
```

**占位符**:
- `{target_lang}` - 目标语言

#### DEFAULT_REVIEW_PROMPT
校对提示词模板，用于第二阶段优化。

```python
DEFAULT_REVIEW_PROMPT = """Role: Senior Language Editor.
Task: Polish 'Draft' into native {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars. If no change, Reason="".
3. Focus on flow and tone."""
```

**占位符**:
- `{target_lang}` - 目标语言

#### TARGET_LANGUAGES
支持的目标语言列表（v3.0 已扩展至 33 种语言）。

```python
# T1 核心市场（9 种）
T1_LANGUAGES = [
    "英语", "德语", "法语", "日语", "韩语",
    "瑞典语", "挪威语", "丹麦语", "芬兰语"
]

# T2 潜力市场（11 种）
T2_LANGUAGES = [
    "意大利语", "西班牙语", "葡萄牙语", "泰语", "越南语",
    "印尼语", "马来语", "俄语", "波兰语", "土耳其语", "阿拉伯语"
]

# T3 新兴市场（13 种）
T3_LANGUAGES = [
    "印地语", "乌尔都语", "孟加拉语", "菲律宾语", "缅甸语",
    "柬埔寨语", "老挝语", "波斯语", "希伯来语", "斯瓦希里语",
    "豪萨语", "哈萨克语", "乌兹别克语"
]

# 完整列表
TARGET_LANGUAGES = T1_LANGUAGES + T2_LANGUAGES + T3_LANGUAGES
```

**完整语言列表 (33 种)**:
英语、德语、法语、日语、韩语、瑞典语、挪威语、丹麦语、芬兰语、意大利语、西班牙语、葡萄牙语、泰语、越南语、印尼语、马来语、俄语、波兰语、土耳其语、阿拉伯语、印地语、乌尔都语、孟加拉语、菲律宾语、缅甸语、柬埔寨语、老挝语、波斯语、希伯来语、斯瓦希里语、豪萨语、哈萨克语、乌兹别克语

#### GUI_CONFIG
GUI 界面配置。

```python
GUI_CONFIG = {
    "window_title": "AI 智能翻译工作台 v3.2",
    "window_width": 950,
    "window_height": 800,
}
```

### JSON 配置文件示例

```json
{
  "api_key": "your-api-key-here",
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-chat",
  "temperature": 0.3,
  "top_p": 0.8,
  "max_tokens": 512,
  "initial_concurrency": 8,
  "max_concurrency": 10,
  "batch_size": 10,
  "max_retries": 3,
  "retry_delay": 1
}
```

### YAML 配置文件示例

```yaml
api_key: your-api-key-here
base_url: https://api.deepseek.com
model_name: deepseek-chat
temperature: 0.3
top_p: 0.8
max_tokens: 512
initial_concurrency: 8
max_concurrency: 10
batch_size: 10
max_retries: 3
retry_delay: 1
```

## 📖 使用方法

### 1. 创建配置文件

```bash
cd config
cp config.example.json config.json
# 或
cp config.example.yaml config.yaml
```

### 2. 编辑配置

编辑 `config.json` 或 `config.yaml`,填入你的 API 密钥和其他配置。

### 3. 在 GUI 中加载

启动 GUI → 点击 "📂 加载配置" → 选择配置文件

### 4. 使用环境变量

```bash
export DEEPSEEK_API_KEY="your-api-key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export DEEPSEEK_MODEL="deepseek-chat"
```

## 🔒 安全提示

- ⚠️ **不要将包含 API 密钥的配置文件提交到 Git**
- ✅ 已将 `config.json` 和 `config.yaml` 添加到 `.gitignore`
- ✅ 示例文件可以安全提交

## 💡 最佳实践

1. **分离配置和代码**: 敏感信息使用配置文件或环境变量
2. **版本控制**: 只提交示例文件，不提交实际配置
3. **定期备份**: 备份配置文件到安全位置
4. **使用强密钥**: API 密钥应足够复杂

## 📊 配置项详解

### API 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `api_key` | string | 必填 | API 密钥 |
| `base_url` | string | https://api.deepseek.com | API 基础 URL |
| `model_name` | string | deepseek-chat | 模型名称 |

### 翻译配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `temperature` | float | 0.3 | 温度参数 (0-1) |
| `top_p` | float | 0.8 | Top-p 采样参数 |
| `max_tokens` | int | 512 | 最大 token 数 |

### 并发控制

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `initial_concurrency` | int | 8 | 初始并发数 |
| `max_concurrency` | int | 10 | 最大并发数 |
| `batch_size` | int | 10 | 批次大小 |

### 重试配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `max_retries` | int | 3 | 最大重试次数 |
| `retry_delay` | int | 1 | 重试延迟 (秒) |

## 🔗 相关文档

- [快速开始](../README.md#快速开始)
- [API 使用指南](../docs/guides/API_USAGE.md)
- [故障排查](../docs/guides/TROUBLESHOOTING.md)
