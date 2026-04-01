> ⚠️ **重要提示**: 本文档内容已整合到 [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md)  
> 建议优先阅读新手册获取更全面、更准确的信息
> 
> **整合日期**: 2026-04-01  
> **替代文档**: [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md) 第 3 章 - 配置指南

---

# 模型配置拆分指南

## 📋 功能概述

模型配置拆分功能允许为**翻译（Draft）**和**校对（Review）**两个阶段分别配置不同的模型和参数，实现更灵活、更优化的工作流程。

## ✨ 核心优势

### 1. 独立模型选择
- **翻译阶段**：可以使用快速、经济的模型（如 deepseek-chat）
- **校对阶段**：可以使用高质量、更智能的模型（如 gpt-4）

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

## 🔧 配置说明

### 全局模型配置

作为默认配置，可被子配置继承：

```yaml
# 全局配置
model_name: "deepseek-chat"
temperature: 0.3
top_p: 0.8
timeout: 60
max_retries: 3
```

### 翻译阶段配置

以 `draft_` 为前缀的配置项：

```yaml
# 翻译阶段专用配置
draft_model_name: "deepseek-chat"      # 翻译模型
draft_temperature: 0.3                  # 翻译温度（保守）
draft_top_p: 0.8                        # 翻译 top_p
draft_timeout: 30                       # 翻译超时（秒）
draft_max_tokens: 512                   # 翻译最大 token 数
```

### 校对阶段配置

以 `review_` 为前缀的配置项：

```yaml
# 校对阶段专用配置
review_model_name: "gpt-4"              # 校对模型（高质量）
review_temperature: 0.6                 # 校对温度（灵活）
review_top_p: 0.9                       # 校对 top_p
review_timeout: 90                      # 校对超时（秒）
review_max_tokens: 512                  # 校对最大 token 数
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
- ✅ 成本低
- ✅ 速度快
- ⚠️ 质量中等

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
- ✅ 质量最高
- ✅ 校对精细
- ⚠️ 成本较高

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
- ✅ 平衡成本和质量
- ✅ 翻译快速
- ✅ 校对精准

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

## 🔍 配置验证

### 检查配置有效性

```bash
python scripts/check_config.py check config.yaml
```

输出示例：

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

```python
from config.loader import get_config_loader

loader = get_config_loader()
config = loader.to_dataclass(Config)

print(f"翻译模型：{config.get_draft_model_name()}")
print(f"翻译温度：{config.get_draft_temperature()}")
print(f"校对模型：{config.get_review_model_name()}")
print(f"校对温度：{config.get_review_temperature()}")
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

### 问题 2：模型名称无效

**症状：** 报错 "Invalid model name"

**解决方法：**
```yaml
# 确保模型名称正确
draft_model_name: "deepseek-chat"  # ✅ 正确
draft_model_name: "deepseek"       # ❌ 错误
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

## 🆘 常见问题

### Q1: 是否必须同时配置翻译和校对？

**A:** 不是必须的。如果只配置全局参数，两个阶段都会使用全局配置：

```yaml
# 简化配置 - 两个阶段使用相同配置
model_name: "deepseek-chat"
temperature: 0.3
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

## 📚 相关资源

- [配置管理快速指南](CONFIGURATION_GUIDE.md)
- [配置检查功能](CONFIG_CHECKER_GUIDE.md)
- [API 参考文档](../api/MODEL_CONFIG_API.md)

## 🎉 总结

模型配置拆分功能提供了：

1. ✅ **灵活的模型选择** - 为不同阶段选择最适合的模型
2. ✅ **精准的性能调优** - 独立的参数配置
3. ✅ **成本优化** - 平衡质量和成本
4. ✅ **易于配置** - 简单直观的配置方式
5. ✅ **向后兼容** - 不影响现有配置

通过这个功能，您可以根据具体需求灵活配置翻译和校对流程，实现最佳的性能价格比！
