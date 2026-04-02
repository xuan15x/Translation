# DeepSeek 模型配置指南

**版本**: v3.0.1  
**最后更新**: 2026-04-02

---

## 📑 目录

- [✨ DeepSeek 完整参数支持](#-deepseek-完整参数支持)
- [🚀 快速开始](#-快速开始)
  - [方式一：Windows 快速配置脚本](#方式一 windows-快速配置脚本)
  - [方式二：手动编辑配置文件](#方式二手动编辑配置文件)
- [📊 完整参数说明](#-完整参数说明)
  - [1. API 认证配置](#1-api-认证配置)
  - [2. 采样参数](#2-采样参数)
  - [3. 双阶段翻译参数](#3-双阶段翻译参数)
  - [4. 并发控制](#4-并发控制)
  - [5. 高级参数](#5-高级参数)
- [🎯 推荐配置组合](#-推荐配置组合)
- [🔧 故障排查](#-故障排查)

---

## ✨ DeepSeek 完整参数支持

本项目现已完整支持 DeepSeek API 的所有采样参数，配置方式参考 Qwen 模型提供商的配置结构。

### 支持的参数

| 参数类别 | 参数名称 | 类型 | 范围 | 说明 |
|---------|---------|------|------|------|
| **基础参数** | `model_name` | string | - | 模型名称 |
| | `api_key` | string | - | API 密钥 |
| | `base_url` | string | - | API 端点 |
| **采样参数** | `temperature` | float | 0.0-2.0 | 创造性参数 |
| | `top_p` | float | 0.0-1.0 | 核采样参数 |
| | `presence_penalty` | float | -2.0~2.0 | 存在惩罚 |
| | `frequency_penalty` | float | -2.0~2.0 | 频率惩罚 |
| | `stop` | list | - | 停止序列 |
| **高级参数** | `max_tokens` | int | 1+ | 最大 token 数 |
| | `timeout` | int | 1+ | 超时时间（秒） |
| | `context_window_size` | int | - | 上下文窗口 |
| | `enable_stream` | bool | - | 流式输出 |

---

## 🚀 快速开始

### 方式一：Windows 快速配置脚本

**最简单的方式**，双击运行即可：

```
快速配置.bat
```

脚本功能：
- ✅ 自动检测 Python 环境
- ✅ 创建/加载配置文件
- ✅ 交互式设置 API Key
- ✅ 配置模型参数
- ✅ 测试 API 连接
- ✅ 启动翻译平台

### 方式二：手动编辑配置文件

1. **复制配置示例**
```bash
cd config
copy config.deepseek.example.json config.json
```

2. **编辑配置文件**

打开 `config/config.json`，修改以下关键参数：

```json
{
  "api_key": "sk-your-deepseek-api-key-here",
  "base_url": "https://api.deepseek.com",
  "api_provider": "deepseek",
  "model_name": "deepseek-chat",
  
  "temperature": 0.7,
  "top_p": 0.9,
  "presence_penalty": 0.0,
  "frequency_penalty": 0.0,
  
  "initial_concurrency": 8,
  "max_concurrency": 10
}
```

3. **获取 API Key**

访问 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取 API Key。

---

## 📊 完整参数说明

### 1. API 认证配置

```json
{
  "api_key": "sk-your-api-key",
  "base_url": "https://api.deepseek.com",
  "api_provider": "deepseek"
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `api_key` | DeepSeek API 密钥 | 必填 |
| `base_url` | API 端点 URL | `https://api.deepseek.com` |
| `api_provider` | API 提供商 | `deepseek` |

### 2. 采样参数

#### temperature（创造性参数）

```json
"temperature": 0.7
```

- **范围**: 0.0 - 2.0
- **推荐值**:
  - `0.3` - 准确翻译，适合技术文档
  - `0.5` - 平衡模式，适合一般文本
  - `0.7` - 默认值，适合大多数场景
  - `1.0+` - 创意翻译，适合文学创作

#### top_p（核采样参数）

```json
"top_p": 0.9
```

- **范围**: 0.0 - 1.0
- **推荐值**:
  - `0.8` - 稳定输出，词汇选择保守
  - `0.9` - 默认值，平衡多样性和准确性
  - `0.95+` - 灵活输出，词汇选择多样

#### presence_penalty（存在惩罚）

```json
"presence_penalty": 0.0
```

- **范围**: -2.0 - 2.0
- **说明**: 控制模型是否讨论新话题
- **推荐值**:
  - `-2.0~-0.5` - 鼓励重复已有话题
  - `0.0` - 默认值，无偏好
  - `0.5~2.0` - 鼓励讨论新话题

#### frequency_penalty（频率惩罚）

```json
"frequency_penalty": 0.0
```

- **范围**: -2.0 - 2.0
- **说明**: 控制模型重复使用相同词汇
- **推荐值**:
  - `-2.0~-0.5` - 鼓励重复用词
  - `0.0` - 默认值，无偏好
  - `0.5~2.0` - 减少重复用词

#### stop（停止序列）

```json
"stop": ["\n\n", "END"]
```

- **类型**: 字符串列表或 null
- **说明**: 遇到这些序列时停止生成
- **默认值**: `null`（不使用停止序列）

### 3. 双阶段翻译参数

#### 初译阶段配置

```json
{
  "draft_model_name": "deepseek-chat",
  "draft_temperature": 0.3,
  "draft_top_p": 0.8,
  "draft_presence_penalty": 0.0,
  "draft_frequency_penalty": 0.0,
  "draft_max_tokens": 512
}
```

#### 校对阶段配置

```json
{
  "review_model_name": "deepseek-chat",
  "review_temperature": 0.7,
  "review_top_p": 0.9,
  "review_presence_penalty": 0.5,
  "review_frequency_penalty": 0.0,
  "review_max_tokens": 512
}
```

**说明**:
- 设置为 `null` 时使用全局参数
- 初译建议使用较低温度（准确）
- 校对建议使用较高温度（优化表达）

### 4. 并发控制

```json
{
  "initial_concurrency": 8,
  "max_concurrency": 10,
  "concurrency_cooldown_seconds": 5.0
}
```

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `initial_concurrency` | 初始并发数 | 新手 2-3，常规 8 |
| `max_concurrency` | 最大并发数 | 常规 10，高级 15 |
| `concurrency_cooldown_seconds` | 冷却时间 | 5.0 秒 |

### 5. 高级参数

```json
{
  "max_tokens": 512,
  "timeout": 60,
  "context_window_size": null,
  "enable_cache_control": true,
  "enable_stream": false,
  "custom_headers": {},
  "extra_body": {}
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `max_tokens` | 单次响应最大 token 数 | 512 |
| `timeout` | 请求超时（秒） | 60 |
| `context_window_size` | 上下文窗口大小 | null（自动） |
| `enable_cache_control` | 启用缓存控制 | true |
| `enable_stream` | 流式输出 | false |
| `custom_headers` | 自定义请求头 | {} |
| `extra_body` | 额外请求体参数 | {} |

---

## 🎯 推荐配置组合

### 准确翻译（技术文档）

```json
{
  "temperature": 0.3,
  "top_p": 0.8,
  "presence_penalty": 0.0,
  "frequency_penalty": 0.0,
  "draft_temperature": 0.2,
  "review_temperature": 0.4
}
```

### 平衡模式（一般文本）

```json
{
  "temperature": 0.7,
  "top_p": 0.9,
  "presence_penalty": 0.0,
  "frequency_penalty": 0.0,
  "draft_temperature": 0.5,
  "review_temperature": 0.7
}
```

### 创意翻译（文学创作）

```json
{
  "temperature": 1.0,
  "top_p": 0.95,
  "presence_penalty": 0.5,
  "frequency_penalty": 0.0,
  "draft_temperature": 0.8,
  "review_temperature": 1.2
}
```

### 经济模式（快速翻译）

```json
{
  "enable_two_pass": false,
  "temperature": 0.5,
  "top_p": 0.85,
  "initial_concurrency": 10,
  "max_concurrency": 15
}
```

---

## 🔧 故障排查

### 问题 1: API Key 无效

**症状**: `401 Unauthorized` 错误

**解决方案**:
1. 检查 API Key 是否正确复制
2. 确认 API Key 未过期
3. 访问 DeepSeek 平台重新生成

### 问题 2: 连接超时

**症状**: `TimeoutError` 或 `ConnectionError`

**解决方案**:
1. 增加 `timeout` 值：`"timeout": 90`
2. 检查网络连接
3. 降低并发数：`"initial_concurrency": 3`

### 问题 3: 响应质量差

**症状**: 翻译不准确或过于随意

**解决方案**:
1. 降低 `temperature`: `0.3-0.5`
2. 降低 `top_p`: `0.7-0.8`
3. 启用双阶段翻译：`"enable_two_pass": true`

### 问题 4: 速率限制

**症状**: `429 Too Many Requests`

**解决方案**:
1. 降低并发数：`"max_concurrency": 5`
2. 增加冷却时间：`"concurrency_cooldown_seconds": 10.0`
3. 联系 DeepSeek 提升配额

---

## 📞 获取帮助

- **完整使用手册**: [COMPLETE_MANUAL.md](../COMPLETE_MANUAL.md)
- **故障排查指南**: [TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)
- **最佳实践**: [BEST_PRACTICES.md](guides/BEST_PRACTICES.md)

---

**文档版本**: v3.0.1  
**最后更新**: 2026-04-02  
**维护者**: Development Team
