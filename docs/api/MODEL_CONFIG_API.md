# 模型配置拆分 - API 参考

## 📦 模块结构

```
config/
├── config.py          # 配置定义和默认值
└── loader.py          # 配置加载器

infrastructure/
└── models.py          # Config 数据类

business_logic/
└── api_stages.py      # API 阶段执行
```

## 🔧 Config 类 API

### 构造函数

```python
from infrastructure.models import Config

config = Config(
    # API 基础配置
    api_key: str = "your_api_key",
    base_url: str = "https://api.deepseek.com",
    api_provider: str = "deepseek",
    
    # 全局模型配置
    model_name: str = "deepseek-chat",
    temperature: float = 0.3,
    top_p: float = 0.8,
    timeout: int = 60,
    max_retries: int = 3,
    
    # 翻译阶段专用配置
    draft_model_name: Optional[str] = None,
    draft_temperature: Optional[float] = None,
    draft_top_p: Optional[float] = None,
    draft_timeout: Optional[int] = None,
    draft_max_tokens: int = 512,
    
    # 校对阶段专用配置
    review_model_name: Optional[str] = None,
    review_temperature: Optional[float] = None,
    review_top_p: Optional[float] = None,
    review_timeout: Optional[int] = None,
    review_max_tokens: int = 512,
    
    # 其他配置...
)
```

### 翻译阶段配置获取方法

#### `get_draft_model_name() -> str`

获取翻译阶段使用的模型名称。

**返回值：**
- 如果配置了 `draft_model_name`，返回该值
- 否则返回全局 `model_name`

**示例：**
```python
config = Config(
    model_name="deepseek-chat",
    draft_model_name="moonshot-v1-32k"
)

print(config.get_draft_model_name())
# 输出："moonshot-v1-32k"
```

#### `get_draft_temperature() -> float`

获取翻译阶段的 temperature 参数。

**返回值：**
- 如果配置了 `draft_temperature`，返回该值
- 否则返回全局 `temperature`

**示例：**
```python
config = Config(
    temperature=0.3,
    draft_temperature=0.4
)

print(config.get_draft_temperature())
# 输出：0.4
```

#### `get_draft_top_p() -> float`

获取翻译阶段的 top_p 参数。

**返回值：**
- 如果配置了 `draft_top_p`，返回该值
- 否则返回全局 `top_p`

#### `get_draft_timeout() -> int`

获取翻译阶段的超时时间（秒）。

**返回值：**
- 如果配置了 `draft_timeout`，返回该值
- 否则返回全局 `timeout`

#### `get_draft_max_tokens() -> int`

获取翻译阶段的最大 token 数。

**返回值：**
- 始终返回 `draft_max_tokens` 的值（默认 512）

### 校对阶段配置获取方法

#### `get_review_model_name() -> str`

获取校对阶段使用的模型名称。

**返回值：**
- 如果配置了 `review_model_name`，返回该值
- 否则返回全局 `model_name`

**示例：**
```python
config = Config(
    model_name="deepseek-chat",
    review_model_name="gpt-4"
)

print(config.get_review_model_name())
# 输出："gpt-4"
```

#### `get_review_temperature() -> float`

获取校对阶段的 temperature 参数。

**返回值：**
- 如果配置了 `review_temperature`，返回该值
- 否则返回全局 `temperature`

#### `get_review_top_p() -> float`

获取校对阶段的 top_p 参数。

**返回值：**
- 如果配置了 `review_top_p`，返回该值
- 否则返回全局 `top_p`

#### `get_review_timeout() -> int`

获取校对阶段的超时时间（秒）。

**返回值：**
- 如果配置了 `review_timeout`，返回该值
- 否则返回全局 `timeout`

#### `get_review_max_tokens() -> int`

获取校对阶段的最大 token 数。

**返回值：**
- 始终返回 `review_max_tokens` 的值（默认 512）

## 🎯 使用示例

### 示例 1：基本使用

```python
from config.loader import get_config_loader
from infrastructure.models import Config

# 加载配置
loader = get_config_loader()
config = loader.to_dataclass(Config)

# 获取翻译阶段配置
draft_model = config.get_draft_model_name()
draft_temp = config.get_draft_temperature()
draft_top_p = config.get_draft_top_p()
draft_timeout = config.get_draft_timeout()

# 获取校对阶段配置
review_model = config.get_review_model_name()
review_temp = config.get_review_temperature()
review_top_p = config.get_review_top_p()
review_timeout = config.get_review_timeout()

print(f"翻译模型：{draft_model}, 温度：{draft_temp}")
print(f"校对模型：{review_model}, 温度：{review_temp}")
```

### 示例 2：自定义配置

```python
from infrastructure.models import Config

# 直接创建配置对象
config = Config(
    api_key="your_api_key",
    
    # 全局配置
    model_name="deepseek-chat",
    temperature=0.3,
    top_p=0.8,
    
    # 翻译阶段配置
    draft_model_name="deepseek-chat",
    draft_temperature=0.3,
    draft_top_p=0.8,
    draft_timeout=30,
    
    # 校对阶段配置
    review_model_name="gpt-4",
    review_temperature=0.6,
    review_top_p=0.9,
    review_timeout=90,
)

# 验证配置
assert config.get_draft_model_name() == "deepseek-chat"
assert config.get_review_model_name() == "gpt-4"
assert config.get_draft_temperature() == 0.3
assert config.get_review_temperature() == 0.6
```

### 示例 3：部分配置（继承全局）

```python
from infrastructure.models import Config

# 只配置翻译阶段，校对阶段使用全局配置
config = Config(
    api_key="your_api_key",
    model_name="deepseek-chat",
    temperature=0.3,
    
    # 只配置翻译阶段
    draft_model_name="moonshot-v1-32k",
    draft_temperature=0.4,
    
    # 校对阶段未配置，将使用全局配置
    # review_model_name=None (使用 model_name)
    # review_temperature=None (使用 temperature)
)

# 结果
print(config.get_draft_model_name())   # "moonshot-v1-32k"
print(config.get_draft_temperature())  # 0.4
print(config.get_review_model_name())  # "deepseek-chat" (继承)
print(config.get_review_temperature()) # 0.3 (继承)
```

## 🔄 API 调用流程

### APIDraftStage（翻译阶段）

```python
from business_logic.api_stages import APIDraftStage

class APIDraftStage:
    async def _call_api(self, messages: list, max_tokens: int = None,
                       src_preview: str = "", target_lang: str = "") -> StageResult:
        """调用 API 进行翻译"""
        
        # 获取翻译阶段配置
        model_name = self.config.get_draft_model_name()
        temperature = self.config.get_draft_temperature()
        top_p = self.config.get_draft_top_p()
        timeout = self.config.get_draft_timeout()
        
        if max_tokens is None:
            max_tokens = self.config.get_draft_max_tokens()
        
        # 调用 API
        response = await self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            response_format={"type": "json_object"},
            timeout=timeout
        )
        
        # ... 处理响应
```

### APIReviewStage（校对阶段）

```python
from business_logic.api_stages import APIReviewStage

class APIReviewStage(APIDraftStage):
    async def _call_api(self, messages: list, max_tokens: int = None,
                       src_preview: str = "", target_lang: str = "") -> StageResult:
        """调用 API 进行校对"""
        
        # 获取校对阶段配置
        model_name = self.config.get_review_model_name()
        temperature = self.config.get_review_temperature()
        top_p = self.config.get_review_top_p()
        timeout = self.config.get_review_timeout()
        
        if max_tokens is None:
            max_tokens = self.config.get_review_max_tokens()
        
        # 调用 API
        response = await self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            response_format={"type": "json_object"},
            timeout=timeout
        )
        
        # ... 处理响应
```

## ⚙️ 配置加载器

### 从文件加载配置

```python
from config.loader import get_config_loader

# 获取单例加载器
loader = get_config_loader()

# 从 YAML 文件加载
loader.load_from_file("config.yaml")

# 转换为 Config 对象
config = loader.to_dataclass(Config)
```

### 配置合并逻辑

```python
from config.config import get_default_config, load_config_from_file

# 1. 获取默认配置
default_config = get_default_config()
# 包含所有 draft_* 和 review_* 配置项

# 2. 从文件加载配置
file_config = load_config_from_file("config.yaml")

# 3. 合并配置（文件配置覆盖默认配置）
final_config = {**default_config, **file_config}

# 4. 创建 Config 对象
config = Config(**final_config)
```

## 🧪 测试示例

### 单元测试

```python
import pytest
from infrastructure.models import Config

def test_draft_model_config():
    """测试翻译模型配置"""
    
    # 情况 1：使用专用配置
    config = Config(
        api_key="test_key",
        model_name="global-model",
        draft_model_name="draft-model"
    )
    assert config.get_draft_model_name() == "draft-model"
    
    # 情况 2：继承全局配置
    config = Config(
        api_key="test_key",
        model_name="global-model",
        draft_model_name=None
    )
    assert config.get_draft_model_name() == "global-model"

def test_review_temperature_config():
    """测试校对温度配置"""
    
    # 情况 1：使用专用配置
    config = Config(
        api_key="test_key",
        temperature=0.3,
        review_temperature=0.6
    )
    assert config.get_review_temperature() == 0.6
    
    # 情况 2：继承全局配置
    config = Config(
        api_key="test_key",
        temperature=0.3,
        review_temperature=None
    )
    assert config.get_review_temperature() == 0.3

def test_config_validation():
    """测试配置验证"""
    
    # 有效的配置
    config = Config(
        api_key="test_key",
        draft_temperature=0.5,
        review_temperature=0.7
    )
    
    # 无效的 configuration
    with pytest.raises(ValueError):
        Config(
            api_key="test_key",
            draft_temperature=3.0  # 超出范围
        )
```

### 集成测试

```python
import asyncio
from config.loader import get_config_loader
from infrastructure.models import Config
from business_logic.api_stages import APIDraftStage, APIReviewStage

async def test_stage_execution():
    """测试阶段执行"""
    
    # 加载配置
    loader = get_config_loader()
    config = loader.to_dataclass(Config)
    
    # 验证配置被正确使用
    assert config.get_draft_model_name() in ["deepseek-chat", "gpt-4"]
    assert config.get_review_model_name() in ["deepseek-chat", "gpt-4"]
    
    # 可以继续测试 API 调用...
```

## 📋 配置检查清单

### 必填配置

```yaml
# ✅ 必须配置
api_key: "your_api_key"

# ✅ 推荐配置（至少配置全局参数）
model_name: "deepseek-chat"
temperature: 0.3
top_p: 0.8
```

### 可选配置

```yaml
# ⭕ 可选配置（不配置则使用全局值）
draft_model_name: null
draft_temperature: null
draft_top_p: null
draft_timeout: null

review_model_name: null
review_temperature: null
review_top_p: null
review_timeout: null
```

### 验证规则

```python
# 数值范围验证
0 <= temperature <= 2
0 <= top_p <= 1
timeout >= 1
batch_size >= 1
initial_concurrency >= 1

# 逻辑关系验证
max_concurrency >= initial_concurrency
```

## 🔍 调试技巧

### 查看实际使用的配置

```python
from config.loader import get_config_loader
from infrastructure.models import Config

loader = get_config_loader()
config = loader.to_dataclass(Config)

# 打印所有配置
print(f"全局模型：{config.model_name}")
print(f"翻译模型：{config.get_draft_model_name()}")
print(f"校对模型：{config.get_review_model_name()}")

# 打印详细配置
print(f"\n翻译参数:")
print(f"  Temperature: {config.get_draft_temperature()}")
print(f"  Top-P: {config.get_draft_top_p()}")
print(f"  Timeout: {config.get_draft_timeout()}s")
print(f"  Max Tokens: {config.get_draft_max_tokens()}")

print(f"\n校对参数:")
print(f"  Temperature: {config.get_review_temperature()}")
print(f"  Top-P: {config.get_review_top_p()}")
print(f"  Timeout: {config.get_review_timeout()}s")
print(f"  Max Tokens: {config.get_review_max_tokens()}")
```

### 日志输出

启动应用后，在日志中查看配置信息：

```
[INFO] Config 初始化
[DEBUG] Config 参数：base_url=https://api.deepseek.com, model=deepseek-chat, provider=deepseek
[DEBUG] Draft 模型：deepseek-chat, temperature=0.3
[DEBUG] Review 模型：gpt-4, temperature=0.6
```

## 🆘 故障排查

### 问题诊断工具

```bash
# 1. 检查配置文件
python scripts/check_config.py check config.yaml

# 2. 查看加载的配置
python -c "from config.loader import get_config_loader; import json; print(json.dumps(get_config_loader().get_all(), indent=2))"

# 3. 测试配置有效性
python scripts/test_config_checker.py
```

### 常见问题解决

**问题：** 配置修改后未生效

**解决：**
```python
# 清除配置缓存
from config.loader import ConfigLoader
ConfigLoader._instance = None

# 重新加载
loader = get_config_loader()
loader.load_from_file("config.yaml")
```

## 📚 相关资源

- [使用指南](MODEL_CONFIG_GUIDE.md)
- [架构设计](../architecture/ARCHITECTURE.md)
- [API 提供商](../../service/api_provider.py)

---

**最后更新**: 2026-03-31  
**版本**: v2.0  
**维护者**: AI 翻译平台团队
