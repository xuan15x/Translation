# 模型配置拆分功能说明

## 📋 概述

模型配置拆分功能允许为**翻译（Draft）**和**校对（Review）**两个阶段分别配置不同的模型和参数，实现更灵活、更优化的工作流程。

## 🆕 v3.2.0 新增功能

### 翻译模式配置

v3.2.0 新增了翻译模式选择功能，支持三种翻译流程：

| 模式 | 配置值 | 说明 | 适用场景 |
|------|--------|------|----------|
| **完整双阶段** | `full` | 初译 + 校对，确保质量 | 重要文档、出版级翻译 |
| **仅初译** | `draft_only` | 只进行初译，跳过校对 | 快速翻译、草稿生成 |
| **仅校对** | `review_only` | 只进行校对，优化翻译 | 翻译优化、质量提升 |

**配置示例：**
```json
{
  "translation_mode": "full"  // full/draft_only/review_only
}
```

### 提示词模板配置

v3.2.0 新增了提示词高级设置功能，可以自定义每个阶段的角色、任务和约束：

```json
{
  "prompt_templates": {
    "draft": {
      "role": "Professional Translator",
      "task": "Translate 'Src' to {target_lang}",
      "constraints": [
        "Output JSON ONLY: {\"Trans\": \"string\"}",
        "Strictly follow provided TM"
      ]
    },
    "review": {
      "role": "Senior Language Editor",
      "task": "Polish 'Draft' into native {target_lang}",
      "constraints": [
        "Output JSON ONLY: {\"Trans\": \"string\", \"Reason\": \"string\"}",
        "Focus on flow and tone"
      ]
    }
  }
}
```

**GUI 中使用：**
1. 点击"高级设置"按钮
2. 编辑 Role、Task、Constraints
3. 保存设置即可

## 🎯 核心优势

### 1. 独立模型选择
- **翻译阶段**：使用快速、经济的模型（如 deepseek-chat）
- **校对阶段**：使用高质量、更智能的模型（如 gpt-4）

### 2. 参数优化
- **翻译参数**：较低的 temperature（0.3-0.5），确保翻译准确性
- **校对参数**：较高的 temperature（0.5-0.7），提升润色创造性

### 3. 成本控制
- 大量初译使用经济模型
- 关键校对使用高质量模型
- 平衡质量和成本

### 4. 性能调优
- 翻译阶段：较短超时，快速失败
- 校对阶段：较长超时，保证质量

## 🔧 配置项详解

### 全局模型配置

作为默认配置，可被子配置继承：

```yaml
# API 基础配置
api_provider: "deepseek"
api_key: "your_api_key"
base_url: "https://api.deepseek.com"

# 全局模型配置（默认配置）
model_name: "deepseek-chat"
temperature: 0.3
top_p: 0.8
timeout: 60
max_retries: 3
retry_streak_threshold: 3
base_retry_delay: 3.0
```

### 翻译阶段专用配置

以 `draft_` 为前缀的配置项：

| 配置项 | 类型 | 默认值 | 说明 | 推荐值 |
|--------|------|--------|------|--------|
| `draft_model_name` | str | None | 翻译模型名称 | `"deepseek-chat"` |
| `draft_temperature` | float | None | 翻译温度（0-2） | `0.3-0.5` |
| `draft_top_p` | float | None | 翻译 top_p（0-1） | `0.8` |
| `draft_timeout` | int | None | 翻译超时（秒） | `30-60` |
| `draft_max_tokens` | int | 512 | 翻译最大 token 数 | `512` |

**示例：**
```yaml
# 翻译阶段专用配置
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
draft_top_p: 0.8
draft_timeout: 30
draft_max_tokens: 512
```

### 校对阶段专用配置

以 `review_` 为前缀的配置项：

| 配置项 | 类型 | 默认值 | 说明 | 推荐值 |
|--------|------|--------|------|--------|
| `review_model_name` | str | None | 校对模型名称 | `"gpt-4"` |
| `review_temperature` | float | None | 校对温度（0-2） | `0.5-0.7` |
| `review_top_p` | float | None | 校对 top_p（0-1） | `0.9` |
| `review_timeout` | int | None | 校对超时（秒） | `60-90` |
| `review_max_tokens` | int | 512 | 校对最大 token 数 | `512` |

**示例：**
```yaml
# 校对阶段专用配置
review_model_name: "gpt-4"
review_temperature: 0.6
review_top_p: 0.9
review_timeout: 90
review_max_tokens: 512
```

## 💡 推荐配置方案

### 方案 1：经济高效型

```yaml
# 全局配置
model_name: "deepseek-chat"
temperature: 0.3

# 翻译阶段 - 快速经济
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
draft_timeout: 30

# 校对阶段 - 同样使用经济模型，稍高温度
review_model_name: "deepseek-chat"
review_temperature: 0.5
review_timeout: 30
```

**特点：**
- ✅ 成本低（约 ¥1.0/千字）
- ✅ 速度快（约 10 秒/千字）
- ⚠️ 质量中等（⭐⭐⭐）

### 方案 2：质量优先型

```yaml
# 全局配置
model_name: "gpt-4"
temperature: 0.3

# 翻译阶段 - 标准模型
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
draft_timeout: 30

# 校对阶段 - 高端模型
review_model_name: "gpt-4"
review_temperature: 0.6
review_timeout: 90
```

**特点：**
- ✅ 质量最高（⭐⭐⭐⭐⭐）
- ✅ 校对精细
- ⚠️ 成本较高（约 ¥3.5/千字）

### 方案 3：平衡型（推荐）

```yaml
# 全局配置
model_name: "deepseek-chat"
temperature: 0.3

# 翻译阶段 - 快速准确
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
draft_top_p: 0.8
draft_timeout: 30

# 校对阶段 - 适度提升
review_model_name: "moonshot-v1-32k"
review_temperature: 0.5
review_top_p: 0.9
review_timeout: 60
```

**特点：**
- ✅ 平衡成本和质量（⭐⭐⭐⭐）
- ✅ 翻译快速
- ✅ 校对精准
- 💰 成本适中（约 ¥2.0/千字）

### 方案 4：专业领域定制

```yaml
# 全局配置
model_name: "deepseek-coder"
temperature: 0.2

# 翻译阶段 - 代码专业模型
draft_model_name: "deepseek-coder"
draft_temperature: 0.2
draft_top_p: 0.8

# 校对阶段 - 通用语言模型
review_model_name: "gpt-4"
review_temperature: 0.5
review_top_p: 0.9
```

**适用场景：**
- 💻 代码注释翻译
- 📚 技术文档翻译
- 🔬 专业术语翻译

## 🛠️ 配置方法

### 方法 1：直接编辑配置文件

```bash
# 编辑配置文件
nano config.yaml
```

添加或修改以下配置：

```yaml
# 全局配置
model_name: "deepseek-chat"
temperature: 0.3
top_p: 0.8

# 翻译配置
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
draft_top_p: 0.8

# 校对配置
review_model_name: "gpt-4"
review_temperature: 0.6
review_top_p: 0.9
```

### 方法 2：使用命令行工具

```bash
# 创建配置文件
python scripts/manage_config.py create -o config.yaml

# 编辑配置文件
nano config.yaml

# 验证配置
python scripts/check_config.py check config.yaml
```

### 方法 3：环境变量覆盖

```bash
# 设置全局配置
export MODEL_NAME="deepseek-chat"
export TEMPERATURE=0.3

# 设置翻译阶段配置
export DRAFT_MODEL_NAME="deepseek-chat"
export DRAFT_TEMPERATURE=0.3

# 设置校对阶段配置
export REVIEW_MODEL_NAME="gpt-4"
export REVIEW_TEMPERATURE=0.6
```

## 📊 配置优先级

配置的生效优先级（从高到低）：

```
1. 阶段专用配置（draft_*, review_*）
   ↓
2. 全局模型配置（model_name, temperature 等）
   ↓
3. 环境变量
   ↓
4. 代码默认值
```

**示例说明：**

```yaml
# 如果只配置了全局参数
model_name: "deepseek-chat"
temperature: 0.3

# 则翻译和校对都使用此配置
# draft_model_name 和 review_model_name 都会返回 "deepseek-chat"
```

```yaml
# 如果配置了阶段专用参数
model_name: "deepseek-chat"      # 全局默认
draft_model_name: "moonshot"     # 翻译专用
# review_model_name 未配置

# 则：
# - 翻译阶段使用 "moonshot"
# - 校对阶段使用 "deepseek-chat"（继承全局）
```

## 🔍 配置验证

### 检查配置有效性

```bash
python scripts/check_config.py check config.yaml
```

**输出示例：**

```
======================================================================
📋 配置检查报告
======================================================================

总体状态：✅ 通过
发现问题：0 个 (错误：0, 警告：0, 提示：0)

【MODEL_CONFIG】
----------------------------------------------------------------------

ℹ️ [draft_model_name]
   当前值：deepseek-chat
   建议：翻译阶段配置有效

ℹ️ [review_model_name]
   当前值：gpt-4
   建议：校对阶段配置有效

======================================================================
```

### 查看实际使用的配置

**Python 代码方式：**

```python
from config.loader import get_config_loader
from infrastructure.models import Config

loader = get_config_loader()
config = loader.to_dataclass(Config)

print(f"翻译模型：{config.get_draft_model_name()}")
print(f"翻译温度：{config.get_draft_temperature()}")
print(f"校对模型：{config.get_review_model_name()}")
print(f"校对温度：{config.get_review_temperature()}")
```

**日志查看方式：**

启动应用后，在日志中查看：

```
Config 初始化
Draft 模型：deepseek-chat, temperature=0.3
Review 模型：gpt-4, temperature=0.6
```

## 🎯 使用场景

### 场景 1：文学翻译

```yaml
# 翻译 - 保守准确
draft_model_name: "deepseek-chat"
draft_temperature: 0.2
draft_top_p: 0.8

# 校对 - 创造性润色
review_model_name: "gpt-4"
review_temperature: 0.7
review_top_p: 0.95
```

### 场景 2：技术文档

```yaml
# 翻译 - 准确为主
draft_model_name: "deepseek-coder"
draft_temperature: 0.2
draft_top_p: 0.8

# 校对 - 保持专业性
review_model_name: "deepseek-coder"
review_temperature: 0.3
review_top_p: 0.85
```

### 场景 3：商务翻译

```yaml
# 翻译 - 标准商务
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
draft_top_p: 0.8

# 校对 - 正式严谨
review_model_name: "moonshot-v1-32k"
review_temperature: 0.4
review_top_p: 0.85
```

### 场景 4：多语言混合

```yaml
# 小语种翻译 - 使用专门模型
draft_model_name: "alibaba-qwen"  # 对小语种支持好
draft_temperature: 0.3
draft_top_p: 0.8

# 校对 - 通用高质量
review_model_name: "gpt-4"
review_temperature: 0.5
review_top_p: 0.9
```

## 📈 性能对比

### 成本对比（以 1000 字为例）

| 配置方案 | 翻译成本 | 校对成本 | 总成本 | 质量评分 |
|---------|---------|---------|--------|---------|
| 全阶段 deepseek | ¥0.5 | ¥0.5 | ¥1.0 | ⭐⭐⭐ |
| 翻译 deepseek + 校对 GPT-4 | ¥0.5 | ¥3.0 | ¥3.5 | ⭐⭐⭐⭐⭐ |
| 全阶段 GPT-4 | ¥3.0 | ¥3.0 | ¥6.0 | ⭐⭐⭐⭐⭐ |
| 推荐方案（混合） | ¥0.5 | ¥1.5 | ¥2.0 | ⭐⭐⭐⭐ |

### 速度对比

| 配置方案 | 翻译速度 | 校对速度 | 总耗时 |
|---------|---------|---------|--------|
| deepseek-chat | ~5s/千字 | ~5s/千字 | ~10s |
| GPT-4 | ~15s/千字 | ~15s/千字 | ~30s |
| 混合方案 | ~5s/千字 | ~15s/千字 | ~20s |

### 质量对比

| 配置方案 | 准确性 | 流畅性 | 专业性 | 综合评分 |
|---------|-------|-------|-------|---------|
| 全阶段 deepseek | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 翻译 deepseek + 校对 GPT-4 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 全阶段 GPT-4 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 推荐方案（混合） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🐛 故障排查

### 问题 1：配置未生效

**症状：** 翻译和校对使用了相同的模型

**解决方法：**
```bash
# 检查配置文件格式
python scripts/check_config.py check config.yaml

# 查看实际加载的配置
python -c "from config.loader import get_config_loader; print(get_config_loader().get_all())"
```

**可能原因：**
- 配置文件缩进错误
- 配置项拼写错误
- 配置文件未被正确加载

### 问题 2：模型名称无效

**症状：** 报错 "Invalid model name"

**解决方法：**
```yaml
# 确保模型名称正确
draft_model_name: "deepseek-chat"  # ✅ 正确
draft_model_name: "deepseek"       # ❌ 错误

# 检查支持的模型列表
python -c "from service.api_provider import PREDEFINED_PROVIDERS; print(list(PREDEFINED_PROVIDERS.keys()))"
```

### 问题 3：参数超出范围

**症状：** 报错 "temperature out of range"

**解决方法：**
```yaml
# 检查参数范围
draft_temperature: 0.3    # ✅ 正确（0-2 之间）
draft_temperature: 3.0    # ❌ 错误（超出范围）

draft_top_p: 0.8          # ✅ 正确（0-1 之间）
draft_top_p: 1.5          # ❌ 错误（超出范围）
```

### 问题 4：超时设置过短

**症状：** 频繁出现 timeout 错误

**解决方法：**
```yaml
# 根据模型调整超时时间
draft_timeout: 30   # 快速模型
review_timeout: 90  # 慢速高质量模型

# 如果仍超时，继续增加
review_timeout: 120
```

## 🆘 常见问题

### Q1: 是否必须同时配置翻译和校对？

**A:** 不是必须的。如果只配置全局参数，两个阶段都会使用全局配置：

```yaml
# 简化配置 - 两个阶段使用相同配置
model_name: "deepseek-chat"
temperature: 0.3

# 等价于
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
review_model_name: "deepseek-chat"
review_temperature: 0.3
```

### Q2: 如何为不同语言对配置不同模型？

**A:** 目前不支持按语言对配置不同模型，但可以通过运行时动态调整：

```python
# 根据目标语言动态选择模型
if target_lang in ["日语", "韩语"]:
    config.draft_model_name = "alibaba-qwen"
else:
    config.draft_model_name = "deepseek-chat"
```

### Q3: 可以只配置翻译或只配置校对吗？

**A:** 可以。配置是可选的：

```yaml
# 只配置翻译阶段
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
# review_* 配置省略，使用全局配置
```

### Q4: 如何测试不同配置的效果？

**A:** 创建多个配置文件并对比：

```bash
# 创建测试配置
cp config.yaml config.test1.yaml
cp config.yaml config.test2.yaml

# 修改配置后分别测试
python presentation/gui_app.py --config config.test1.yaml
python presentation/gui_app.py --config config.test2.yaml
```

### Q5: 配置修改后需要重启吗？

**A:** 是的，配置修改后需要重启应用才能生效。

```bash
# 重启应用
python presentation/gui_app.py
```

### Q6: 可以使用不同的 API 提供商吗？

**A:** 可以。为不同阶段配置不同的 API 提供商：

```yaml
# 翻译阶段 - DeepSeek
draft_model_name: "deepseek-chat"
draft_base_url: "https://api.deepseek.com"

# 校对阶段 - OpenAI
review_model_name: "gpt-4"
review_base_url: "https://api.openai.com/v1"
```

注意：需要确保两个提供商的 API 密钥都已设置。

## 📚 相关资源

### 官方文档
- [配置管理快速指南](CONFIGURATION_GUIDE.md)
- [配置检查功能](CONFIG_CHECKER_GUIDE.md)
- [API 参考文档](../api/MODEL_CONFIG_API.md)
- [架构设计文档](../architecture/ARCHITECTURE.md)

### 示例文件
- [YAML 示例配置](../../config/config.example.yaml)
- [JSON 示例配置](../../config/config.example.json)

### 工具脚本
- [配置管理脚本](../../scripts/manage_config.py)
- [配置检查脚本](../../scripts/check_config.py)
- [配置测试脚本](../../scripts/test_config_checker.py)

## 🎉 总结

模型配置拆分功能提供了：

1. ✅ **灵活的模型选择** - 为不同阶段选择最适合的模型
2. ✅ **精准的性能调优** - 独立的参数配置
3. ✅ **成本优化** - 平衡质量和成本
4. ✅ **易于配置** - 简单直观的配置方式
5. ✅ **向后兼容** - 不影响现有配置

通过这个功能，您可以根据具体需求灵活配置翻译和校对流程，实现最佳的性能价格比！

---

**最后更新**: 2026-03-31  
**版本**: v2.0  
**维护者**: AI 翻译平台团队
