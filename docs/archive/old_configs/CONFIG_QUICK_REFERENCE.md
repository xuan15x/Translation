> ⚠️ **重要提示**: 本文档内容已整合到 [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md)  
> 建议优先阅读新手册获取更全面、更准确的信息
> 
> **整合日期**: 2026-04-01  
> **替代文档**: [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md) 第 3 章 - 配置指南

---

# 配置速查卡 ⚡

> 📌 **一页纸搞定所有配置** - 适合快速查阅

---

## 🎯 3 分钟快速配置（推荐）

### 步骤 1️⃣：获取 API Key（1 分钟）

```
访问：https://platform.deepseek.com/
注册 → 控制台 → API Keys → 创建新 Key
复制保存：sk-xxxxxxxxxxxxxxxx
```

### 步骤 2️⃣：运行配置向导（1 分钟）

```bash
python scripts/quick_start.py
```

**跟随提示操作：**
```
1. 选择模式 → 输入 "1" (新手模式)
2. 输入 API Key → 粘贴你的 sk-xxx
3. 确认保存 → 输入 "Y"
```

### 步骤 3️⃣：开始使用（1 分钟）

```bash
# 程序已自动启动，开始翻译吧！
```

---

## 📝 配置文件核心字段

### 最简配置（只填这里就够了）

```json
{
  "model_name": "deepseek-chat",
  
  "api_keys": {
    "deepseek": {
      "api_key": "sk-your-key-here",  // ⚠️ 必填
      "base_url": "https://api.deepseek.com"
    }
  },
  
  "temperature": 0.3,        // 推荐值
  "initial_concurrency": 5   // 保守并发
}
```

### 字段说明

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `model_name` | ✅ | 模型名称 | `"deepseek-chat"` |
| `api_keys.deepseek.api_key` | ✅ | API 密钥 | `"sk-xxx"` |
| `api_keys.deepseek.base_url` | ✅ | API 地址 | `"https://api.deepseek.com"` |
| `temperature` | ❌ | 创造性 (0-2) | `0.3` (准确) |
| `initial_concurrency` | ❌ | 并发数 | `5` (保守) |

---

## 🎨 场景化配置模板

### 新手模式（最简单）

```json
{
  "preset": "beginner",
  "model_name": "deepseek-chat",
  "api_key": "sk-your-key",
  "temperature": 0.3,
  "initial_concurrency": 5,
  "max_concurrency": 8
}
```

### 平衡模式（推荐⭐）

```json
{
  "preset": "balanced",
  "model_name": "deepseek-chat",
  "api_key": "sk-your-key",
  "temperature": 0.3,
  "top_p": 0.8,
  "initial_concurrency": 8,
  "max_concurrency": 12,
  "enable_two_pass": true
}
```

### 高质量模式

```json
{
  "preset": "quality",
  "draft_model_name": "deepseek-chat",
  "review_model_name": "gpt-4-turbo",
  "draft_temperature": 0.3,
  "review_temperature": 0.5,
  "timeout": 90
}
```

### 快速模式

```json
{
  "preset": "speed",
  "model_name": "deepseek-chat",
  "initial_concurrency": 15,
  "max_concurrency": 20,
  "timeout": 45,
  "cache_capacity": 5000
}
```

---

## 🔧 参数调整速查

### 温度参数 (temperature)

```
0.0 - 0.3  → 保守准确（技术文档）⭐
0.3 - 0.5  → 平衡适中（一般翻译）
0.5 - 0.7  → 有创意（文学翻译）
0.7 - 2.0  → 非常自由（不推荐）
```

### 并发参数 (concurrency)

```
3-5   → 保守模式（测试用）
8-12  → 正常模式（推荐⭐）
15-20 → 激进模式（批量翻译）
```

### 超时参数 (timeout)

```
30-45  → 短文本
60     → 中等文本（推荐⭐）
90-120 → 长文本或高质量校对
```

---

## 💡 智能工具

### 使用预设模板

```python
from infrastructure.smart_config import SmartConfigurator

configurator = SmartConfigurator()

# 一键应用预设
config = configurator.quick_setup(
    api_key="sk-your-key",
    preset='beginner'  # 或 balanced/quality/speed
)
```

### 自动验证修复

```python
# 检查并修复配置问题
success, issues = configurator.validate_and_fix(config)

if not success:
    print("发现问题:")
    for issue in issues:
        print(f"  - {issue['message']}")
    # config 已被自动修复
```

---

## ❓ 快速排障

### ❌ API Key 无效

```bash
# 打开配置文件
nano config/config.json

# 找到并修改
"api_key": "sk-your-actual-key"

# 保存重启
```

### ❌ 翻译速度慢

```json
// 提高并发
{
  "initial_concurrency": 15,
  "max_concurrency": 20
}
```

### ❌ 翻译质量差

```json
// 降低温度
{
  "temperature": 0.2
}

// 或使用更强模型
{
  "review_model_name": "gpt-4-turbo"
}
```

---

## 📞 更多帮助

- 📖 [完整配置手册](CONFIG_SETUP_HANDBOOK.md) - 详细教程
- 🚀 [快速入门](QUICKSTART.md) - 5 分钟上手
- 🔧 [故障排查](TROUBLESHOOTING.md) - 常见问题
- 💡 [最佳实践](BEST_PRACTICES.md) - 使用技巧

---

**记住这 3 个核心字段就够了：**

```json
{
  "model_name": "deepseek-chat",
  "api_key": "sk-your-key",
  "temperature": 0.3
}
```

**其他都是可选的！** ✨
