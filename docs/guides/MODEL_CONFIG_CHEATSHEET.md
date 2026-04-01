# 模型配置拆分 - 快速参考卡片

## 🚀 快速开始

### 最简配置（5 分钟上手）

```yaml
# config.yaml
api_key: "your_api_key"

# 全局配置
model_name: "deepseek-chat"
temperature: 0.3

# 翻译阶段
draft_model_name: "deepseek-chat"
draft_temperature: 0.3

# 校对阶段
review_model_name: "gpt-4"
review_temperature: 0.6
```

### 立即使用

```bash
# 1. 编辑配置文件
nano config.yaml

# 2. 验证配置
python scripts/check_config.py check config.yaml

# 3. 启动应用
python presentation/gui_app.py
```

## 📊 配置速查表

### 翻译阶段配置

| 配置项 | 说明 | 推荐值 | 范围 |
|--------|------|--------|------|
| `draft_model_name` | 翻译模型 | `"deepseek-chat"` | - |
| `draft_temperature` | 温度 | `0.3` | 0-2 |
| `draft_top_p` | Top-P | `0.8` | 0-1 |
| `draft_timeout` | 超时 (秒) | `30` | ≥1 |
| `draft_max_tokens` | 最大 token | `512` | ≥1 |

### 校对阶段配置

| 配置项 | 说明 | 推荐值 | 范围 |
|--------|------|--------|------|
| `review_model_name` | 校对模型 | `"gpt-4"` | - |
| `review_temperature` | 温度 | `0.6` | 0-2 |
| `review_top_p` | Top-P | `0.9` | 0-1 |
| `review_timeout` | 超时 (秒) | `90` | ≥1 |
| `review_max_tokens` | 最大 token | `512` | ≥1 |

## 💡 推荐方案速查

### 方案 1：经济高效 ⭐⭐⭐

```yaml
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
review_model_name: "deepseek-chat"
review_temperature: 0.5
```
**成本**: ¥1.0/千字 | **速度**: 10s/千字

### 方案 2：质量优先 ⭐⭐⭐⭐⭐

```yaml
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
review_model_name: "gpt-4"
review_temperature: 0.6
```
**成本**: ¥3.5/千字 | **速度**: 20s/千字

### 方案 3：平衡推荐 ⭐⭐⭐⭐

```yaml
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
review_model_name: "moonshot-v1-32k"
review_temperature: 0.5
```
**成本**: ¥2.0/千字 | **速度**: 15s/千字

## 🔍 常用命令

```bash
# 检查配置
python scripts/check_config.py check config.yaml

# 创建配置
python scripts/manage_config.py create -o config.yaml

# 查看配置
python -c "from config.loader import get_config_loader; print(get_config_loader().get_all())"

# 测试配置
python scripts/test_config_checker.py

# 启动应用
python presentation/gui_app.py --config config.yaml
```

## 🎯 场景配方

### 文学翻译

```yaml
draft_model_name: "deepseek-chat"
draft_temperature: 0.2
review_model_name: "gpt-4"
review_temperature: 0.7
```

### 技术文档

```yaml
draft_model_name: "deepseek-coder"
draft_temperature: 0.2
review_model_name: "deepseek-coder"
review_temperature: 0.3
```

### 商务翻译

```yaml
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
review_model_name: "moonshot-v1-32k"
review_temperature: 0.4
```

### 代码注释

```yaml
draft_model_name: "deepseek-coder"
draft_temperature: 0.2
review_model_name: "gpt-4"
review_temperature: 0.5
```

## ⚠️ 常见错误

### ❌ 错误：温度超出范围

```yaml
# 错误
draft_temperature: 3.0  # 超出 0-2 范围

# 正确
draft_temperature: 0.3  # ✅
```

### ❌ 错误：Top-P 超出范围

```yaml
# 错误
draft_top_p: 1.5  # 超出 0-1 范围

# 正确
draft_top_p: 0.8  # ✅
```

### ❌ 错误：模型名称无效

```yaml
# 错误
draft_model_name: "deepseek"  # 不完整

# 正确
draft_model_name: "deepseek-chat"  # ✅
```

### ❌ 错误：超时过短

```yaml
# 错误
draft_timeout: 5  # 太短，容易超时

# 正确
draft_timeout: 30  # ✅
```

## 🔑 配置优先级

```
阶段专用配置 > 全局配置 > 环境变量 > 默认值
```

**示例：**

```yaml
# 如果这样配置
model_name: "global-model"
draft_model_name: "draft-model"
# review_model_name 未配置

# 则使用：
# 翻译：draft-model (专用配置)
# 校对：global-model (继承全局)
```

## 🧪 快速测试

### Python 代码测试

```python
from infrastructure.models import Config

config = Config(
    api_key="test",
    draft_model_name="draft-model",
    review_model_name="review-model"
)

print(f"翻译：{config.get_draft_model_name()}")
print(f"校对：{config.get_review_model_name()}")
```

### 命令行测试

```bash
# 测试配置有效性
python -c "
from config.config import get_default_config
from infrastructure.models import Config

config_dict = get_default_config()
config_dict['api_key'] = 'test'
config = Config(**config_dict)
print('✅ 配置有效')
"
```

## 📈 性能对比速查

| 方案 | 成本 | 速度 | 质量 |
|------|------|------|------|
| 全 deepseek | ¥1.0 | 10s | ⭐⭐⭐ |
| 混合方案 | ¥2.0 | 15s | ⭐⭐⭐⭐ |
| 翻译 deepseek+ 校对 GPT-4 | ¥3.5 | 20s | ⭐⭐⭐⭐⭐ |
| 全 GPT-4 | ¥6.0 | 30s | ⭐⭐⭐⭐⭐ |

## 🛠️ 调试技巧

### 查看实际配置

```python
from config.loader import get_config_loader

loader = get_config_loader()
print("翻译模型:", loader._config_cache.get('draft_model_name'))
print("校对模型:", loader._config_cache.get('review_model_name'))
```

### 日志查看

```bash
# 启动时查看日志
python presentation/gui_app.py 2>&1 | grep -E "(Draft|Review)"
```

## 🆘 快速排障

| 问题 | 可能原因 | 解决方法 |
|------|---------|---------|
| 配置未生效 | 文件错误 | `check_config.py check` |
| 模型无效 | 名称错误 | 检查完整模型名 |
| 频繁超时 | 超时过短 | 增加 timeout 值 |
| 参数错误 | 超出范围 | 检查数值范围 |

## 📞 帮助命令

```bash
# 获取帮助
python scripts/check_config.py --help
python scripts/manage_config.py --help

# 查看版本
python -c "import config; print(config.__version__ if hasattr(config, '__version__') else '2.0')"
```

---

**快速参考卡片版本**: v2.0  
**最后更新**: 2026-03-31  
**打印建议**: 此卡片设计为 A4 纸打印，便于桌面参考
