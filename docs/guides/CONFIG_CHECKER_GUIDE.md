# 配置检查功能使用指南

## 📋 功能概述

配置检查模块提供完整的配置验证功能，在程序启动前检测配置文件的错误，避免因配置问题导致程序运行时崩溃。

## ✨ 核心功能

### 1. 全面检查
- ✅ **语法检查** - 验证字段类型、格式
- ✅ **范围检查** - 验证数值范围是否合理
- ✅ **依赖检查** - 验证配置项之间的逻辑关系
- ✅ **安全检查** - 检测敏感信息配置
- ✅ **性能建议** - 提供性能优化建议
- ✅ **最佳实践** - 提示符合最佳实践的配置

### 2. 问题分级
- ❌ **ERROR（错误）** - 致命问题，必须修复
- ⚠️ **WARNING（警告）** - 潜在问题，建议修复
- ℹ️ **INFO（提示）** - 改进建议，可选优化

### 3. 自动修复
支持自动修复部分简单问题：
- 修正超出范围的数值
- 修正无效的布尔值
- 修正逻辑矛盾的配置

## 🚀 快速开始

### 方法 1：命令行检查

```bash
# 检查默认配置文件
python scripts/check_config.py check

# 检查指定文件
python scripts/check_config.py check config.yaml

# 检查并尝试自动修复
python scripts/check_config.py check config.yaml --fix

# 静默模式（只显示摘要）
python scripts/check_config.py check -q
```

### 方法 2：交互式检查

```bash
# 启动交互式检查
python scripts/check_config.py interactive
```

### 方法 3：Python API

```python
from config.checker import check_config, validate_config
from data_access.config_persistence import ConfigPersistence

# 加载配置
persistence = ConfigPersistence('config.yaml')
config_dict = persistence.load()

# 检查配置
passed, results = check_config(config_dict)

if not passed:
    print("配置存在问题！")
    for result in results:
        if result.level == 'error':
            print(f"❌ {result.key}: {result.message}")
```

### 方法 4：自动检查（推荐）

配置加载时自动检查：

```python
from config.loader import get_config_loader

# 加载配置时会自动检查
loader = get_config_loader()

# 如果有严重错误，会显示警告信息
```

## 📊 检查报告示例

### 成功示例

```
======================================================================
📋 配置检查报告
======================================================================

总体状态：✅ 通过
发现问题：0 个 (错误：0, 警告：0, 提示：0)

======================================================================
```

### 失败示例

```
======================================================================
📋 配置检查报告
======================================================================

总体状态：❌ 未通过
发现问题：5 个 (错误：2, 警告：2, 提示：1)

⚠️  存在致命错误，请务必修复！

【SYNTAX】
----------------------------------------------------------------------

❌ [api_key]
   问题：必填字段 'api_key' 不能为空
   建议：请设置有效的 api_key 值

⚠️ [api_provider]
   问题：未知的 API 提供商：'invalid_provider'
   建议：支持的提供商：deepseek, openai, moonshot, zhipu, baidu, alibaba, anthropic
   当前值：invalid_provider

【RANGE】
----------------------------------------------------------------------

❌ [initial_concurrency]
   问题：initial_concurrency 必须是正整数，当前值：0
   建议：设置 >= 1 的整数
   当前值：0

⚠️ [temperature]
   问题：temperature 值为 3.0，超出推荐范围 [0, 2]
   建议：推荐值：0.3（平衡），0.7（创造性），0.1（保守）
   当前值：3.0

【DEPENDENCY】
----------------------------------------------------------------------

❌ [max_concurrency]
   问题：max_concurrency (5) 不能小于 initial_concurrency (0)
   建议：调整 max_concurrency >= 1

======================================================================
```

## 🔍 检查项详解

### 1. API 配置检查

**检查项目：**
- `api_key` - 必填，不能为空
- `api_provider` - 必须是支持的提供商
- `base_url` - URL 格式验证
- API 密钥与环境变量的匹配性

**常见错误：**
```yaml
# ❌ 错误：API 密钥为空
api_key: ""

# ❌ 错误：未知的提供商
api_provider: "unknown_provider"

# ❌ 错误：URL 格式不正确
base_url: "api.deepseek.com"  # 缺少 http://
```

**正确示例：**
```yaml
# ✅ 正确
api_key: "sk-xxxxx"  # 或从环境变量读取
api_provider: "deepseek"
base_url: "https://api.deepseek.com"
```

### 2. 模型参数检查

**检查项目：**
- `temperature` - 范围 [0, 2]，类型检查
- `top_p` - 范围 [0, 1]，类型检查

**常见错误：**
```yaml
# ❌ 错误：超出范围
temperature: 3.0  # 应在 0-2 之间
top_p: 1.5  # 应在 0-1 之间

# ❌ 错误：类型错误
temperature: "0.3"  # 应该是数字
```

**正确示例：**
```yaml
# ✅ 正确
temperature: 0.3
top_p: 0.8
```

### 3. 并发控制检查

**检查项目：**
- `initial_concurrency` - 正整数
- `max_concurrency` - 正整数，且 >= initial_concurrency
- `concurrency_cooldown_seconds` - 非负数

**常见错误：**
```yaml
# ❌ 错误：负值或零
initial_concurrency: 0
max_concurrency: -1

# ❌ 错误：逻辑矛盾
initial_concurrency: 10
max_concurrency: 5  # 不能小于 initial_concurrency
```

**正确示例：**
```yaml
# ✅ 正确
initial_concurrency: 8
max_concurrency: 10
concurrency_cooldown_seconds: 5.0
```

### 4. 重试配置检查

**检查项目：**
- `retry_streak_threshold` - 正数
- `base_retry_delay` - 正数
- `max_retries` - 非负整数 [0, 10]
- `timeout` - 正数 [1, 300]

**常见错误：**
```yaml
# ❌ 错误：负值
base_retry_delay: -3.0

# ❌ 错误：超出范围
max_retries: 20  # 建议不超过 10
timeout: 600  # 建议不超过 300 秒
```

### 5. 工作流配置检查

**检查项目：**
- `enable_two_pass` - 布尔值
- `skip_review_if_local_hit` - 布尔值
- `batch_size` - 正整数
- `gc_interval` - 正整数

**常见错误：**
```yaml
# ❌ 错误：类型错误
enable_two_pass: "true"  # 应该是布尔值 true

# ❌ 错误：负值
batch_size: -100
```

### 6. 术语库配置检查

**检查项目：**
- `similarity_low` - 范围 [0, 100]
- `exact_match_score` - 范围 [0, 100]
- `multiprocess_threshold` - 非负数

**常见错误：**
```yaml
# ❌ 错误：超出百分比范围
similarity_low: 120  # 应该在 0-100 之间
```

### 7. 日志配置检查

**检查项目：**
- `log_level` - 有效级别 [DEBUG, INFO, WARNING, ERROR, CRITICAL]
- `log_granularity` - 有效粒度 [minimal, basic, normal, detailed, verbose]
- `log_max_lines` - 正整数

**常见错误：**
```yaml
# ❌ 错误：无效的日志级别
log_level: "VERBOSE"  # 应该是 DEBUG, INFO 等

# ❌ 错误：无效的粒度
log_granularity: "high"  # 应该是 minimal, basic 等
```

### 8. 提示词检查

**检查项目：**
- `draft_prompt` - 非空字符串，包含 `{target_lang}` 占位符
- `review_prompt` - 非空字符串，包含 `{target_lang}` 占位符

**常见错误：**
```yaml
# ❌ 错误：缺少占位符
draft_prompt: "Translate this text."  # 缺少 {target_lang}

# ❌ 错误：空字符串
draft_prompt: ""
```

**正确示例：**
```yaml
# ✅ 正确
draft_prompt: |
  Role: Professional Translator.
  Task: Translate 'Src' to {target_lang}.
  Constraints:
  1. Output JSON ONLY.
```

## 🛠️ 高级功能

### 1. 批量检查多个配置文件

```bash
# 创建检查脚本
cat > batch_check.sh << 'EOF'
#!/bin/bash
for file in config*.yaml; do
    echo "检查 $file..."
    python scripts/check_config.py check "$file" -q
done
EOF

chmod +x batch_check.sh
./batch_check.sh
```

### 2. CI/CD 集成

```yaml
# .github/workflows/config-check.yml
name: Configuration Check

on: [push, pull_request]

jobs:
  check-config:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install pyyaml
      
      - name: Check configuration
        run: python scripts/check_config.py check config.yaml
```

### 3. 自定义检查规则

```python
from config.checker import ConfigChecker, CheckLevel, CheckCategory

class CustomConfigChecker(ConfigChecker):
    """自定义配置检查器"""
    
    def _check_custom_rules(self, config: dict):
        """添加自定义检查规则"""
        
        # 示例：检查是否启用了性能监控
        if config.get('enable_performance_monitor', False):
            sample_interval = config.get('perf_sample_interval', 1.0)
            if sample_interval > 5.0:
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.PERFORMANCE,
                    'perf_sample_interval',
                    "性能监控采样间隔过长，可能遗漏重要数据",
                    "建议设置 <= 5.0 秒"
                )
    
    def check(self, config: dict):
        """重写检查方法，添加自定义规则"""
        results = super().check(config)
        self._check_custom_rules(config)
        return results

# 使用自定义检查器
custom_checker = CustomConfigChecker()
results = custom_checker.check(config_dict)
```

## 💡 最佳实践

### 1. 开发环境配置

```yaml
# config.dev.yaml
log_level: "DEBUG"
log_granularity: "verbose"
enable_performance_monitor: true

# 运行检查
python scripts/check_config.py check config.dev.yaml
```

### 2. 生产环境配置前检查

```bash
# 部署前自动检查
python scripts/check_config.py check config.prod.yaml --fix

# 如果检查失败，阻止部署
if [ $? -ne 0 ]; then
    echo "❌ 配置检查失败，禁止部署"
    exit 1
fi
```

### 3. 定期配置审计

```bash
# 每周检查一次配置
cat > weekly_config_audit.sh << 'EOF'
#!/bin/bash
echo "=== 每周配置审计 ==="
date=$(date +%Y-%m-%d)
python scripts/check_config.py check config.yaml > config_check_$date.txt
echo "检查结果已保存到：config_check_$date.txt"
EOF

chmod +x weekly_config_audit.sh
```

## 🐛 故障排查

### 问题 1：检查器报错但不知道如何修复

**解决方法：**
```bash
# 查看详细报告
python scripts/check_config.py check config.yaml

# 只查看错误
python scripts/check_config.py check config.yaml 2>&1 | grep "❌"
```

### 问题 2：自动修复后仍有问题

**原因：** 有些问题无法自动修复（如 API 密钥、提示词内容等）

**解决方法：**
```bash
# 查看哪些错误无法自动修复
python scripts/check_config.py check config.yaml

# 手动编辑配置文件
nano config.yaml
```

### 问题 3：检查通过但程序仍报错

**可能原因：**
- 配置检查只验证格式，不验证业务逻辑
- 运行时环境变量变化
- 依赖的外部资源不可用

**解决方法：**
```python
# 在代码中添加额外的运行时检查
from config.loader import get_config

api_key = get_config('api_key')
if not api_key:
    raise RuntimeError("API 密钥不能为空")
```

## 📚 相关资源

- [配置管理快速指南](CONFIGURATION_GUIDE.md)
- [配置管理总结](CONFIG_MANAGEMENT_SUMMARY.md)
- [配置加载器 API](../../config/loader.py)

## 🆘 获取帮助

```bash
# 显示帮助信息
python scripts/check_config.py --help
python scripts/check_config.py check --help
```
