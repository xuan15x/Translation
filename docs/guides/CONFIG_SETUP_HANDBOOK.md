# 配置填入手册 v3.0

> 📖 **本手册专为新手设计**，从零开始指导您完成所有配置，无需任何前置知识。

## 📋 目录

1. [第一次使用？从这里开始](#-第一次使用从这里开始)
2. [⚡ 3 分钟快速配置](#-3-分钟快速配置)
3. [📝 配置文件详解](#-配置文件详解)
4. [🔧 常用场景配置](#-常用场景配置)
5. [🔍 问题排查](#-问题排查)

---

## 🎯 第一次使用？从这里开始

### 你需要准备什么？

✅ **只需要 2 样东西：**
1. Python 3.8+（已安装）
2. API Key（免费注册获取）

### 如何获取 API Key？

**推荐：DeepSeek（深度求索）**
1. 访问：https://platform.deepseek.com/
2. 注册账号（支持手机号/邮箱）
3. 点击控制台 → API Keys
4. 创建新 API Key
5. 复制保存（格式：`sk-xxxxxxxxxxxxxxxx`）

**💡 提示：** 新用户通常有免费额度，足够测试使用。

---

## ⚡ 3 分钟快速配置

### 方式一：自动配置向导（⭐ 最简单）

**适合人群：** 所有用户，特别是新手

**步骤：**

```bash
# 1. 运行快速启动脚本
python scripts/quick_start.py
```

**接下来跟随向导操作：**

#### 步骤 1/3：选择模式
```
请选择模式 (1-4，默认 1):
1. 🐣 新手模式     - 最简单配置，只需设置 API Key
2. ⚖️  平衡模式     - 性能与质量的平衡（推荐）
3. 🏆 高质量模式   - 翻译质量优先，适合重要文档
4. ⚡ 快速模式     - 翻译速度优先，适合大批量
```
**👉 输入 `1` 然后按回车（新手模式）**

#### 步骤 2/3：输入 API Key
```
请输入您的 DeepSeek API Key: 
```
**👉 粘贴你的 API Key 然后按回车**
```
✅ API Key 已设置（**********abcd）
```

#### 步骤 3/3：确认配置
```
📋 配置摘要:
   使用模式：新手模式
   模型名称：deepseek-chat
   并发范围：5-8
   超时时间：60 秒

是否保存配置？(Y/n):
```
**👉 输入 `Y` 然后按回车**

**完成！** 🎉 程序会自动启动翻译界面。

---

### 方式二：手动配置文件

**适合人群：** 需要自定义配置的用户

#### 步骤 1：复制示例文件

```bash
# 在项目根目录执行
cp config/config.example.json config/config.json
```

或者直接用文件管理器：
1. 打开项目文件夹
2. 进入 `config` 目录
3. 复制 `config.example.json`
4. 粘贴并重命名为 `config.json`

#### 步骤 2：编辑配置文件

用文本编辑器（如记事本、VS Code）打开 `config/config.json`

**找到这一行：**
```json
"api_key": "aa",
```

**修改为你的 API Key：**
```json
"api_key": "sk-your-actual-api-key-here",
```

**就这么简单！** 其他参数都用默认值即可。

#### 步骤 3：保存并启动

保存文件，然后运行：
```bash
python presentation/translation.py
```

---

## 📝 配置文件详解

### 极简配置（只改这里就够了）

```json
{
  "_version": "v3.0.0",
  
  // ========== 【必填】API 密钥 ==========
  "model_name": "deepseek-chat",
  
  "api_keys": {
    "deepseek": {
      "api_key": "sk-your-key-here",  // ⚠️ 改成你的 API Key
      "base_url": "https://api.deepseek.com"
    }
  },
  
  // ========== 【可选】新手推荐参数 ==========
  "temperature": 0.3,        // 创造性：0.3 准确，0.7 有创意
  "initial_concurrency": 5,  // 并发数：5 保守，10 正常，20 快速
  "timeout": 60              // 超时时间（秒）：60 足够
}
```

### 完整配置（按需调整）

<details>
<summary>点击查看完整配置说明</summary>

#### API 配置（必须设置）

| 字段 | 说明 | 必填 | 示例 |
|------|------|------|------|
| `model_name` | 模型名称 | ✅ | `"deepseek-chat"` |
| `api_keys.deepseek.api_key` | API 密钥 | ✅ | `"sk-xxx"` |
| `api_keys.deepseek.base_url` | API 地址 | ✅ | `"https://api.deepseek.com"` |

**💡 提示：** 系统会自动根据 `model_name` 识别提供商，无需手动设置 `api_provider`。

#### 模型参数（影响翻译质量）

| 字段 | 范围 | 默认值 | 说明 |
|------|------|--------|------|
| `temperature` | 0.0-2.0 | 0.3 | 越低越准确，越高越有创意 |
| `top_p` | 0.0-1.0 | 0.8 | 词汇多样性 |

**推荐组合：**
- 技术文档：`temperature=0.2, top_p=0.7`
- 一般翻译：`temperature=0.3, top_p=0.8` ⭐
- 文学翻译：`temperature=0.5, top_p=0.9`

#### 并发控制（影响翻译速度）

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `initial_concurrency` | 8 | 初始并发数 |
| `max_concurrency` | 10 | 最大并发数 |

**推荐设置：**
- 保守模式：`initial=3, max=5`
- 正常模式：`initial=8, max=12` ⭐
- 激进模式：`initial=15, max=20`

#### 双阶段翻译（高级功能）

```json
{
  // 初译阶段（Draft）
  "draft_model_name": null,           // null=使用全局 model_name
  "draft_temperature": null,          // null=使用全局 temperature
  "draft_max_tokens": 512,
  
  // 校对阶段（Review）
  "review_model_name": null,          // null=使用全局 model_name
  "review_temperature": null,         // null=使用全局 temperature
  "review_max_tokens": 512
}
```

**💡 提示：** 设置为 `null` 表示继承全局配置，无需重复设置。

</details>

---

## 🎨 常用场景配置

### 场景 1：日常翻译（最常用）

**需求：** 翻译一般文档，平衡质量和速度

**配置：**
```json
{
  "model_name": "deepseek-chat",
  "api_keys": {
    "deepseek": {
      "api_key": "sk-your-key",
      "base_url": "https://api.deepseek.com"
    }
  },
  "temperature": 0.3,
  "initial_concurrency": 8,
  "max_concurrency": 12,
  "timeout": 60,
  "enable_two_pass": true,
  "skip_review_if_local_hit": true
}
```

**特点：**
- ✅ 速度快（8-12 并发）
- ✅ 质量好（双阶段翻译）
- ✅ 成本低（使用 DeepSeek）

---

### 场景 2：技术文档翻译

**需求：** 术语准确，质量优先

**配置：**
```json
{
  "model_name": "deepseek-chat",
  "api_keys": {
    "deepseek": {
      "api_key": "sk-your-key",
      "base_url": "https://api.deepseek.com"
    }
  },
  "temperature": 0.2,
  "top_p": 0.7,
  "initial_concurrency": 6,
  "max_concurrency": 10,
  "timeout": 90,
  "similarity_low": 70
}
```

**特点：**
- ✅ 术语准确（低温度）
- ✅ 输出稳定（低 top_p）
- ✅ 匹配严格（高相似度阈值）

---

### 场景 3：批量翻译（追求速度）

**需求：** 大量文档，速度优先

**配置：**
```json
{
  "model_name": "deepseek-chat",
  "api_keys": {
    "deepseek": {
      "api_key": "sk-your-key",
      "base_url": "https://api.deepseek.com"
    }
  },
  "initial_concurrency": 15,
  "max_concurrency": 20,
  "timeout": 45,
  "cache_capacity": 5000,
  "batch_size": 2000
}
```

**特点：**
- ✅ 速度快（高并发）
- ✅ 缓存大（减少重复）
- ✅ 批量大（减少开销）

---

### 场景 4：高质量翻译（不计成本）

**需求：** 重要文档，质量至上

**配置：**
```json
{
  "draft_model_name": "deepseek-chat",
  "review_model_name": "gpt-4-turbo",
  "api_keys": {
    "deepseek": {
      "api_key": "sk-deepseek-key",
      "base_url": "https://api.deepseek.com"
    },
    "openai": {
      "api_key": "sk-openai-key",
      "base_url": "https://api.openai.com/v1"
    }
  },
  "draft_temperature": 0.3,
  "review_temperature": 0.5,
  "timeout": 120
}
```

**特点：**
- ✅ 初译快速（DeepSeek）
- ✅ 校对优质（GPT-4）
- ✅ 质量最高（双模型）

---

## 🔧 智能配置工具

### 使用预设模板

系统内置了 4 种预设模板，一键应用：

```python
from infrastructure.smart_config import SmartConfigurator

configurator = SmartConfigurator()

# 新手模式（最简单）
config = configurator.quick_setup(
    api_key="sk-your-key",
    preset='beginner'
)

# 平衡模式（推荐）
config = configurator.quick_setup(
    api_key="sk-your-key",
    preset='balanced'
)

# 高质量模式
config = configurator.quick_setup(
    api_key="sk-your-key",
    preset='quality'
)

# 快速模式
config = configurator.quick_setup(
    api_key="sk-your-key",
    preset='speed'
)
```

### 自动验证和修复

```python
# 检查配置是否有问题
success, issues = configurator.validate_and_fix(config)

if not success:
    print("发现问题:")
    for issue in issues:
        print(f"  - {issue['message']}")
    
    # config 已被自动修复
    print("已自动修复配置")
```

---

## ❓ 问题排查

### Q1: 找不到配置文件？

**症状：**
```
FileNotFoundError: [FILE_002] 配置文件不存在
```

**解决：**
```bash
# 1. 检查文件是否存在
ls config/config.json

# 2. 如果不存在，创建它
cp config/config.example.json config/config.json

# 3. 编辑文件，设置 api_key
```

---

### Q2: API Key 无效？

**症状：**
```
AuthenticationError: API 密钥不能为空
```

**解决：**
1. 打开 `config/config.json`
2. 找到 `"api_key": ""`
3. 填入你的 API Key：`"api_key": "sk-xxxxx"`
4. 保存文件

---

### Q3: 翻译速度慢？

**解决：**
```json
// 在配置文件中调整
{
  "initial_concurrency": 15,  // 提高并发
  "max_concurrency": 20,
  "timeout": 45               // 降低超时
}
```

---

### Q4: 翻译质量不好？

**解决：**
```json
// 降低 temperature 提高准确性
{
  "temperature": 0.2  // 从 0.3 降到 0.2
}

// 或使用更强的模型
{
  "review_model_name": "gpt-4-turbo"
}
```

---

### Q5: 配置不生效？

**可能原因：**
1. 文件未保存
2. JSON 格式错误
3. 参数名称拼写错误

**解决：**
```bash
# 验证 JSON 格式
python -c "import json; json.load(open('config/config.json'))"

# 如果有错误会显示具体位置
```

---

## 📞 获取帮助

### 查看配置示例

```bash
# 查看完整的配置示例
cat config/config.example.json

# 或 YAML 格式
cat config/config.example.yaml
```

### 使用配置检查工具

```bash
# 检查当前配置
python scripts/check_config.py

# 查看详细报告
python scripts/manage_config.py validate
```

### 阅读更多文档

- [快速入门](QUICKSTART.md) - 5 分钟上手
- [最佳实践](BEST_PRACTICES.md) - 使用技巧
- [故障排查](TROUBLESHOOTING.md) - 常见问题
- [配置检查器](CONFIG_CHECKER_GUIDE.md) - 验证工具

---

## 🎉 总结

**配置其实很简单：**

1. **获取 API Key** （1 分钟）
2. **运行配置向导** `python scripts/quick_start.py`（1 分钟）
3. **开始翻译** （0 分钟）

**记住这 3 步，就能搞定 99% 的配置！**

**不需要：**
- ❌ 手动编辑复杂的配置文件
- ❌ 理解 50+ 个参数的含义
- ❌ 担心配置错误导致程序崩溃

**系统会自动：**
- ✅ 引导你完成配置
- ✅ 验证配置的有效性
- ✅ 修复常见配置问题

**就这么简单！** 🎊
