# 配置指南 v3.2.0

> 📖 **完整配置指南** - 从零基础到高级配置

## 📋 目录

1. [快速开始（3 分钟配置完成）](#-快速开始3-分钟配置完成)
2. [翻译模式配置](#-翻译模式配置)
3. [提示词高级设置](#-提示词高级设置)
4. [配置文件详解](#-配置文件详解)
5. [多模型提供商配置](#-多模型提供商配置)
6. [常见问题排查](#-常见问题排查)

---

## 🚀 快速开始（3 分钟配置完成）

### 第一步：获取 API Key

**推荐：DeepSeek（性价比高，中文优秀）**

1. 访问：https://platform.deepseek.com/
2. 注册账号（支持手机号/邮箱）
3. 进入控制台 → API Keys
4. 创建新 API Key
5. 复制保存（格式：`sk-xxxxxxxxxxxxxxxx`）

### 第二步：运行快速配置脚本

**Windows 用户**：
```bash
# 双击运行或在命令行执行
快速配置.bat
```

**脚本会自动**：
1. ✅ 检查 Python 是否已安装
2. ✅ 自动创建 `config/config.json`（如果不存在）
3. ✅ 显示模型提供商选择菜单

### 第三步：选择模型并输入 API Key

```
========================================
  Select Model Provider
========================================
  1. DeepSeek (Recommended, Cost-effective)
  2. OpenAI (GPT-4o/GPT-3.5)
  3. Qwen/Alibaba Cloud
  4. Zhipu AI (GLM Series)
  5. Moonshot (Kimi)
  6. Claude (Anthropic)
  7. Gemini (Google)
  --------------------------------------
  8. View Current Config
  9. Test API Connection
  0. Launch Translation Platform
========================================

Select (0-9): 1
```

**输入 1 选择 DeepSeek**，然后：

```
Enter DeepSeek API Key: sk-你的API密钥
Enter model name (default: deepseek-chat): deepseek-chat

[OK] DeepSeek configuration completed!
  Model: deepseek-chat
  API: https://api.deepseek.com
```

### 第四步：启动翻译平台

在快速配置脚本菜单中输入 `0`，或运行：

```bash
启动翻译平台.bat
```

**✅ 配置完成！** 现在可以开始翻译了。

---

## 🔄 翻译模式配置

v3.2.0 新增了三种翻译模式，适应不同场景需求。

### 模式说明

| 模式 | 说明 | 适用场景 | 速度 |
|------|------|----------|------|
| **完整双阶段** | 初译 + 校对 | 高质量翻译、正式文档 | 较慢 |
| **仅初译** | 只执行初译 | 快速翻译、草稿生成 | 快速 |
| **仅校对** | 只执行校对 | 已有初译结果，只需优化 | 中等 |

### 如何切换模式

**方法一：GUI 界面（推荐）**

在翻译平台主界面，找到"翻译模式"下拉框：

```
🔄 翻译模式: [完整双阶段（初译+校对） ▼]
```

选择后界面会自动调整：
- **仅初译模式**：隐藏校对风格输入框和预览
- **仅校对模式**：隐藏初译风格输入框和预览
- **完整模式**：显示所有配置

**方法二：配置文件**

编辑 `config/config.json`：

```json
{
  "translation_mode": "full"
}
```

可选值：
- `"full"` - 完整双阶段
- `"draft_only"` - 仅初译
- `"review_only"` - 仅校对

---

## ⚙️ 提示词高级设置

v3.2.0 允许用户完全自定义提示词结构。

### 默认工作流程

```
用户输入风格 → 程序自动生成 Role/Task/Constraints → 自动注入禁止事项 → 发送给 AI
```

**用户只需输入**：
- 初译风格：如"专业、准确、直接"
- 校对风格：如"流畅、自然、地道"

### 高级设置（可选）

**打开方式**：点击"⚙️ 高级设置"按钮

**可配置项**：

#### 1. 角色（Role）

定义 AI 的身份和专业领域。

**初译默认值**：
```
Professional Translator
```

**校对默认**：
```
Senior Language Editor
```

#### 2. 任务（Task）

描述 AI 需要完成的具体任务。

**初译默认值**：
```
Translate 'Src' to {target_lang}
```

**校对默认值**：
```
Polish 'Draft' into native {target_lang}
```

#### 3. 约束条件（Constraints）

列出 AI 必须遵守的规则，每行一条。

**初译默认值**：
```
Output JSON ONLY: {"Trans": "string"}
Strictly follow provided TM
Accurate and direct
```

**校对默认值**：
```
Output JSON ONLY: {"Trans": "string", "Reason": "string"}
Reason: Max 10 chars. If no change, Reason=""
Focus on flow and tone
```

### 保存和加载自定义模板

**保存**：
1. 在高级设置窗口修改内容
2. 点击"💾 保存设置"
3. 自动保存到 `config/config.json`

**恢复默认**：
1. 点击"🔄 恢复默认"
2. 确认后恢复默认值

### 配置文件格式

自定义模板保存在 `config/config.json` 中：

```json
{
  "prompt_templates": {
    "draft": {
      "role": "Professional Translator",
      "task": "Translate 'Src' to {target_lang}",
      "constraints": [
        "Output JSON ONLY: {\"Trans\": \"string\"}",
        "Strictly follow provided TM",
        "Accurate and direct"
      ]
    },
    "review": {
      "role": "Senior Language Editor",
      "task": "Polish 'Draft' into native {target_lang}",
      "constraints": [
        "Output JSON ONLY: {\"Trans\": \"string\", \"Reason\": \"string\"}",
        "Reason: Max 10 chars",
        "Focus on flow and tone"
      ]
    }
  }
}
```

---

## 📝 配置文件详解

### 文件位置

`config/config.json`（项目根目录下）

### 完整配置结构

```json
{
  "_version": "v3.2.0",
  "_description": "AI Translation Workbench Config",
  
  "model_name": "deepseek-chat",
  "api_provider": "deepseek",
  
  "api_keys": {
    "deepseek": {
      "api_key": "sk-your-api-key",
      "base_url": "https://api.deepseek.com"
    },
    "openai": {
      "api_key": "sk-your-openai-key",
      "base_url": "https://api.openai.com/v1"
    },
    "custom": {
      "api_key": "",
      "base_url": ""
    }
  },
  
  "temperature": 0.7,
  "top_p": 0.9,
  "timeout": 60,
  "max_retries": 3,
  
  "initial_concurrency": 8,
  "max_concurrency": 10,
  
  "batch_size": 1000,
  "enable_two_pass": true,
  "translation_mode": "full",
  
  "prompt_templates": {
    "draft": {
      "role": "Professional Translator",
      "task": "Translate 'Src' to {target_lang}",
      "constraints": [
        "Output JSON ONLY: {\"Trans\": \"string\"}",
        "Strictly follow provided TM",
        "Accurate and direct"
      ]
    },
    "review": {
      "role": "Senior Language Editor",
      "task": "Polish 'Draft' into native {target_lang}",
      "constraints": [
        "Output JSON ONLY: {\"Trans\": \"string\", \"Reason\": \"string\"}",
        "Reason: Max 10 chars",
        "Focus on flow and tone"
      ]
    }
  },
  
  "target_languages": [
    "英语", "德语", "法语", "日语", "韩语",
    "意大利语", "西班牙语", "葡萄牙语", "泰语", "越南语",
    "印尼语", "马来语", "俄语", "波兰语", "土耳其语", "阿拉伯语"
  ],
  "favorite_languages": ["英语", "日语", "韩语"],
  "default_source_lang": "中文",
  
  "enabled_translation_types": [
    "match3_item", "match3_skill", "match3_level",
    "match3_dialogue", "match3_ui",
    "dialogue", "ui", "scene", "tutorial", "achievement", "custom"
  ],
  
  "gui_window_title": "AI Translation Workbench v3.2",
  "gui_window_width": 950,
  "gui_window_height": 800,
  
  "log_level": "INFO",
  "log_max_lines": 1000,
  
  "pool_size": 5,
  "cache_capacity": 2000,
  "cache_ttl_seconds": 3600,
  
  "similarity_low": 60,
  "exact_match_score": 100,
  "gc_interval": 2
}
```

### 必要配置项

以下配置**必须设置**才能正常运行：

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `api_keys.[provider].api_key` | API 密钥 | `sk-xxxxxxxxx` |
| `api_keys.[provider].base_url` | API 地址 | `https://api.deepseek.com` |
| `model_name` | 模型名称 | `deepseek-chat` |
| `api_provider` | 当前提供商 | `deepseek` |

### 可选配置项

所有其他配置项都有合理的默认值，可根据需要调整。

---

## 🌐 多模型提供商配置

### 支持的提供商

| 提供商 | 推荐模型 | API 地址 | 特点 |
|--------|----------|----------|------|
| **DeepSeek** | deepseek-chat | https://api.deepseek.com | 性价比高，中文优秀 |
| **OpenAI** | gpt-4o | https://api.openai.com/v1 | 质量最高，生态完善 |
| **通义千问** | qwen-max | https://dashscope.aliyuncs.com/compatible-mode/v1 | 阿里云，中文强项 |
| **智谱 AI** | glm-4 | https://open.bigmodel.cn/api/paas/v4 | 国产模型，GLM 系列 |
| **Moonshot** | moonshot-v1-8k | https://api.moonshot.cn/v1 | Kimi，长上下文 |
| **Claude** | claude-3-5-sonnet | https://api.anthropic.com/v1 | Anthropic，逻辑推理强 |
| **Gemini** | gemini-1.5-pro | https://generativelanguage.googleapis.com/v1beta | Google，多模态 |

### 切换提供商

**方法一：快速配置脚本**

运行 `快速配置.bat`，选择对应的数字：

```
Select (0-9): 2  # 选择 OpenAI
```

**方法二：手动编辑配置文件**

编辑 `config/config.json`：

```json
{
  "api_provider": "openai",
  "model_name": "gpt-4o",
  "api_keys": {
    "openai": {
      "api_key": "sk-your-openai-key",
      "base_url": "https://api.openai.com/v1"
    }
  }
}
```

---

## ❓ 常见问题排查

### Q1: 运行快速配置脚本报错 "No such file or directory"

**原因**：脚本未找到 `config/config.json`

**解决**：
1. 确保在项目根目录运行脚本
2. 脚本会自动创建配置文件
3. 如果仍失败，手动创建 `config` 目录

```bash
mkdir config
```

### Q2: JSON 解析错误 "Expecting property name enclosed in double quotes"

**原因**：配置文件包含注释（`//`），标准 JSON 不支持

**解决**：
1. 删除 `config/config.json`
2. 重新运行 `快速配置.bat`
3. 脚本会创建有效的 JSON 配置

### Q3: 翻译模式切换后界面没有变化

**解决**：
1. 关闭并重新打开翻译平台
2. 确保选择了正确的模式（检查下拉框）
3. 查看日志确认模式切换信息

### Q4: 高级设置中修改的模板没有生效

**检查清单**：
1. ✅ 是否点击了"💾 保存设置"？
2. ✅ 检查 `config/config.json` 中 `prompt_templates` 是否更新？
3. ✅ 是否重新初始化了服务（重启翻译平台）？

### Q5: 如何恢复默认配置？

**方法一**：删除配置文件重新生成

```bash
del config\config.json
快速配置.bat
```

**方法二**：手动编辑，恢复默认值

参考本手册的"完整配置结构"部分。

---

## 📚 相关文档

- [完整使用手册](../../COMPLETE_MANUAL.md) - 一站式使用指南
- [模型配置指南](./MODEL_CONFIG_GUIDE.md) - 详细模型参数说明
- [快速参考速查表](./CHEATSHEET.md) - 常用操作快速查阅
- [项目 README](../../README.md) - 项目总览

---

**文档版本**: v3.2.0  
**更新日期**: 2026-04-03  
**适用版本**: AI Translation Workbench v3.2.0+
