# 统一模型配置指南

**版本**: v3.0.3  
**最后更新**: 2026-04-02  
**参考**: [Qwen Model Providers Configuration](https://qwenlm.github.io/qwen-code-docs/zh/users/configuration/model-providers/)

---

## 📑 目录

- [✨ 功能特性](#-功能特性)
- [🏗️ 配置结构](#️-配置结构)
  - [认证类型（AuthType）](#认证类型 authtype)
  - [模型配置结构](#模型配置结构)
  - [GenerationConfig 参数](#generationconfig-参数)
  - [SamplingParams 参数](#samplingparams-参数)
- [🚀 快速开始](#-快速开始)
  - [方式一：使用预定义模型](#方式一使用预定义模型)
  - [方式二：手动配置模型](#方式二手动配置模型)
- [📊 完整配置示例](#-完整配置示例)
  - [OpenAI 兼容模型配置](#openai-兼容模型配置)
  - [Anthropic Claude 配置](#anthropic-claude-配置)
  - [Google Gemini 配置](#google-gemini-配置)
  - [阿里云通义千问配置](#阿里云通义千问配置)
- [🔧 高级功能](#-高级功能)
  - [自定义模型配置](#自定义模型配置)
  - [模型切换](#模型切换)
  - [配置验证](#配置验证)
- [📊 支持模型列表](#-支持模型列表)
- [🔍 故障排查](#-故障排查)

---

## ✨ 功能特性

### 参考 Qwen 配置结构

本项目现已实现与 Qwen 相同的 `modelProviders` 配置系统，支持：

1. **统一配置格式**: 所有模型使用相同的配置结构
2. **多认证类型**: 支持 OpenAI、Anthropic、Gemini、Qwen 等认证方式
3. **完整参数支持**: 包含 `generationConfig` 和 `samplingParams` 的所有参数
4. **环境变量管理**: 通过 `envKey` 安全存储 API 密钥
5. **模型能力配置**: 支持 `capabilities` 配置（如 vision）

### 支持的认证类型

| AuthType | 说明 | 支持的服务商 |
|----------|------|-------------|
| `openai` | OpenAI 兼容 API | DeepSeek、OpenAI、Moonshot、Zhipu、vLLM、Ollama |
| `anthropic` | Anthropic Claude API | Anthropic |
| `gemini` | Google Gemini API | Google AI |
| `qwen` | 阿里云通义千问 API | 阿里云 DashScope |

---

## 🏗️ 配置结构

### 认证类型（AuthType）

```json
{
  "modelProviders": {
    "openai": [...],      // OpenAI 兼容模型
    "anthropic": [...],   // Anthropic 模型
    "gemini": [...],      // Google Gemini 模型
    "qwen": [...]         // 阿里云通义千问模型
  }
}
```

### 模型配置结构

每个模型配置包含以下字段：

```json
{
  "id": "deepseek-chat",           // 必填：模型标识符
  "envKey": "DEEPSEEK_API_KEY",    // 必填：环境变量名
  "authType": "openai",            // 必填：认证类型
  "name": "DeepSeek Chat",         // 可选：显示名称
  "description": "DeepSeek 聊天模型", // 可选：描述
  "baseUrl": "https://api.deepseek.com", // 可选：API 端点
  "generationConfig": { ... },     // 可选：生成配置
  "capabilities": {                // 可选：能力配置
    "vision": true
  }
}
```

### GenerationConfig 参数

```json
"generationConfig": {
  "timeout": 60000,                    // 请求超时（毫秒）
  "max_retries": 3,                    // 最大重试次数
  "enable_cache_control": true,        // 启用缓存控制
  "context_window_size": 32768,        // 上下文窗口大小
  "enable_stream": false,              // 流式输出
  "modalities": {                      // 模态配置
    "image": true
  },
  "custom_headers": {},                // 自定义请求头
  "extra_body": {},                    // 额外请求体（仅 OpenAI 兼容）
  "schemaCompliance": "auto",          // 模式合规性（Gemini 专用）
  "samplingParams": { ... }            // 采样参数
}
```

### SamplingParams 参数

```json
"samplingParams": {
  "temperature": 0.7,              // 创造性参数 (0.0-2.0)
  "top_p": 0.9,                    // 核采样参数 (0.0-1.0)
  "max_tokens": 4096,              // 最大 token 数
  "presence_penalty": 0.0,         // 存在惩罚 (-2.0~2.0)
  "frequency_penalty": 0.0,        // 频率惩罚 (-2.0~2.0)
  "top_k": null,                   // 前 k 个采样（Gemini 专用）
  "stop": null                     // 停止序列
}
```

---

## 🚀 快速开始

### 方式一：使用预定义模型

项目已预置常用模型配置，直接使用即可：

1. **复制配置示例**
```bash
cd config
copy config.unified.example.json config.json
```

2. **设置环境变量**
```bash
# Windows
set DEEPSEEK_API_KEY=sk-your-api-key

# Linux/Mac
export DEEPSEEK_API_KEY=sk-your-api-key
```

3. **启动应用**
```bash
python presentation/translation.py
```

### 方式二：手动配置模型

在配置文件中添加自定义模型：

```json
{
  "modelProviders": {
    "openai": [
      {
        "id": "my-custom-model",
        "envKey": "MY_API_KEY",
        "authType": "openai",
        "baseUrl": "https://my-api-server.com/v1",
        "generationConfig": {
          "timeout": 60000,
          "samplingParams": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 4096
          }
        }
      }
    ]
  },
  "current_model_id": "my-custom-model"
}
```

---

## 📊 完整配置示例

### OpenAI 兼容模型配置

```json
{
  "modelProviders": {
    "openai": [
      {
        "id": "deepseek-chat",
        "name": "DeepSeek Chat",
        "envKey": "DEEPSEEK_API_KEY",
        "baseUrl": "https://api.deepseek.com",
        "generationConfig": {
          "timeout": 60000,
          "max_retries": 3,
          "context_window_size": 32768,
          "samplingParams": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 4096,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0
          }
        }
      },
      {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "envKey": "OPENAI_API_KEY",
        "baseUrl": "https://api.openai.com/v1",
        "generationConfig": {
          "timeout": 90000,
          "context_window_size": 128000,
          "samplingParams": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 4096
          }
        }
      }
    ]
  }
}
```

### Anthropic Claude 配置

```json
{
  "modelProviders": {
    "anthropic": [
      {
        "id": "claude-3-5-sonnet-20240229",
        "name": "Claude 3.5 Sonnet",
        "envKey": "ANTHROPIC_API_KEY",
        "baseUrl": "https://api.anthropic.com/v1",
        "generationConfig": {
          "timeout": 120000,
          "context_window_size": 200000,
          "samplingParams": {
            "temperature": 0.7,
            "max_tokens": 4096
          }
        }
      }
    ]
  }
}
```

**注意**: Anthropic 不支持 `extra_body` 参数。

### Google Gemini 配置

```json
{
  "modelProviders": {
    "gemini": [
      {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "envKey": "GEMINI_API_KEY",
        "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
        "capabilities": {
          "vision": true
        },
        "generationConfig": {
          "timeout": 90000,
          "context_window_size": 1048576,
          "schemaCompliance": "auto",
          "samplingParams": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 8192,
            "top_k": 40
          }
        }
      }
    ]
  }
}
```

**注意**: Gemini 支持 `top_k` 参数和 `schemaCompliance` 配置。

### 阿里云通义千问配置

```json
{
  "modelProviders": {
    "qwen": [
      {
        "id": "qwen-max",
        "name": "通义千问 Max",
        "envKey": "DASHSCOPE_API_KEY",
        "baseUrl": "https://dashscope.aliyuncs.com/api/v1",
        "generationConfig": {
          "timeout": 90000,
          "samplingParams": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048
          }
        }
      }
    ]
  }
}
```

---

## 🔧 高级功能

### 自定义模型配置

添加自定义 OpenAI 兼容模型：

```json
{
  "modelProviders": {
    "openai": [
      {
        "id": "custom-llama",
        "name": "Llama 3 (Self-hosted)",
        "envKey": "LLAMA_API_KEY",
        "authType": "openai",
        "baseUrl": "http://localhost:8080/v1",
        "generationConfig": {
          "timeout": 30000,
          "context_window_size": 8192,
          "extra_body": {
            "repetition_penalty": 1.1
          },
          "samplingParams": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048
          }
        }
      }
    ]
  }
}
```

### 模型切换

在代码中切换使用的模型：

```python
from config.model_manager import get_model_manager

# 获取管理器
manager = get_model_manager()

# 切换到 GPT-4o
manager.set_current_model("gpt-4o")

# 切换到 DeepSeek
manager.set_current_model("deepseek-chat")

# 获取当前模型配置
current_model = manager.get_current_model()
```

### 配置验证

验证配置是否有效：

```python
from config.model_manager import get_model_manager

manager = get_model_manager()

# 验证配置
is_valid, errors = manager.validate_config()

if not is_valid:
    print("配置验证失败:")
    for error in errors:
        print(f"  - {error}")
```

---

## 📊 支持模型列表

### OpenAI 兼容

| 模型 ID | 服务商 | 上下文窗口 | 最大输出 |
|--------|--------|-----------|---------|
| `deepseek-chat` | DeepSeek | 32K | 4K |
| `deepseek-coder` | DeepSeek | 16K | 4K |
| `gpt-4o` | OpenAI | 128K | 4K |
| `gpt-4-turbo` | OpenAI | 128K | 4K |
| `moonshot-v1-8k` | Moonshot | 8K | 8K |
| `glm-4` | Zhipu | 128K | 2K |
| `qwen-turbo` | Alibaba | 8K | 2K |

### Anthropic

| 模型 ID | 上下文窗口 | 最大输出 |
|--------|-----------|---------|
| `claude-3-5-sonnet-20240229` | 200K | 4K |
| `claude-3-opus-20240229` | 200K | 4K |
| `claude-3-haiku-20240307` | 200K | 4K |

### Google Gemini

| 模型 ID | 上下文窗口 | 最大输出 | 特性 |
|--------|-----------|---------|------|
| `gemini-1.5-pro` | 1M | 8K | Vision |
| `gemini-1.5-flash` | 1M | 8K | Fast |

### 阿里云通义千问

| 模型 ID | 上下文窗口 | 最大输出 |
|--------|-----------|---------|
| `qwen-max` | 32K | 2K |
| `qwen-plus` | 128K | 2K |
| `qwen-turbo` | 8K | 2K |

---

## 🔍 故障排查

### 问题 1: 配置验证失败

**症状**: `validate_config()` 返回错误

**解决方案**:
1. 检查 `authType` 是否有效（openai/anthropic/gemini/qwen）
2. 确保 `id` 和 `envKey` 字段存在
3. 检查同一 `authType` 下是否有重复的 `id`

### 问题 2: API Key 未设置

**症状**: `环境变量 XXX 未设置` 警告

**解决方案**:
```bash
# 设置环境变量
export DEEPSEEK_API_KEY=sk-your-key

# 或在配置文件中检查 envKey 是否正确
```

### 问题 3: extra_body 不支持

**症状**: 配置验证提示 `extra_body 仅支持 OpenAI 兼容提供商`

**解决方案**:
- 仅对 `authType: openai` 或 `authType: qwen` 使用 `extra_body`
- Anthropic 和 Gemini 不支持此参数

### 问题 4: 模型 ID 找不到

**症状**: `set_current_model` 返回 False

**解决方案**:
1. 检查模型 ID 拼写是否正确
2. 确认模型已在 `modelProviders` 中配置
3. 使用 `get_all_models()` 查看所有可用模型

---

## 📞 获取帮助

- **Qwen 配置文档**: [Qwen Model Providers](https://qwenlm.github.io/qwen-code-docs/zh/users/configuration/model-providers/)
- **项目配置示例**: [config.unified.example.json](../config/config.unified.example.json)
- **模型管理器 API**: [model_manager.py](../config/model_manager.py)

---

**文档版本**: v3.0.3  
**最后更新**: 2026-04-02  
**维护者**: Development Team
