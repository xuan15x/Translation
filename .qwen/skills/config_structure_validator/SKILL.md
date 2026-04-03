# 配置结构验证器 (Config Structure Validator)

**版本**: 1.0.0
**创建日期**: 2026-04-03
**适用范围**: 所有使用 JSON/YAML 配置文件的 Python 项目
**触发方式**: 配置结构变更、配置脚本开发、配置加载前验证

---

## 📋 概述

配置结构验证器用于验证配置文件的结构完整性,支持多版本配置结构的向后兼容检查。它能够检测缺失字段、类型错误、无效值等问题,确保配置格式正确且符合预期。

### 核心功能

- ✅ **结构验证**: 验证配置文件是否符合预期的 JSON Schema
- 🔄 **版本兼容**: 支持多版本配置结构的向后兼容检查
- 🔧 **自动修复**: 为常见结构问题提供自动修复建议
- 📊 **详细报告**: 生成结构验证报告,列出所有问题
- 📝 **配置模板**: 提供完整和最小配置模板

---

## 🎯 使用场景

### 1. 配置结构变更
修改配置结构后,验证新旧结构的兼容性。

### 2. 配置脚本开发
开发配置生成脚本时,确保生成的配置格式正确。

### 3. 应用启动前验证
应用启动时验证配置文件完整性,提前发现配置问题。

### 4. 用户配置检查
用户提供配置文件后,验证格式并给出友好错误提示。

---

## 🔧 使用方法

### 基础用法

```python
from .qwen.skills.config_structure_validator import ConfigValidator

# 验证配置文件
validator = ConfigValidator()
result = validator.validate_file('config.json')

if result.is_valid:
    print("✅ 配置验证通过")
else:
    print(f"❌ 发现 {len(result.errors)} 个问题:")
    for error in result.errors:
        print(f"  - {error}")
```

### 高级用法

```python
from .qwen.skills.config_structure_validator import ConfigValidator, ConfigSchema

# 定义配置 Schema
schema = ConfigSchema()
schema.required_field('api_keys', type=dict)
schema.required_field('api_keys.openai.api_key', type=str, min_length=1)
schema.optional_field('max_retries', type=int, default=3)
schema.enum_field('log_level', ['DEBUG', 'INFO', 'WARNING', 'ERROR'])

# 验证配置
validator = ConfigValidator(schema=schema)
result = validator.validate_dict(config_dict)

# 生成修复建议
suggestions = validator.suggest_fixes(result.errors)
for suggestion in suggestions:
    print(f"建议: {suggestion}")
```

---

## 📊 验证规则

### 1. 必需字段检查

**规则**: 配置中必须包含所有必需字段。

**示例**:
```python
schema = ConfigSchema()
schema.required_field('api_keys', type=dict)
schema.required_field('database.url', type=str)
schema.required_field('database.pool_size', type=int, min_value=1, max_value=100)
```

**错误类型**:
- `MISSING_FIELD`: 字段不存在
- `NULL_VALUE`: 字段存在但值为 None
- `EMPTY_STRING`: 字段为空字符串（如果配置了 `min_length`）

### 2. 类型检查

**规则**: 字段值必须符合预期的数据类型。

**示例**:
```python
schema.required_field('timeout', type=int)  # 必须是整数
schema.required_field('enabled', type=bool)  # 必须是布尔值
schema.required_field('tags', type=list)     # 必须是列表
schema.required_field('metadata', type=dict) # 必须是字典
```

**错误类型**:
- `TYPE_MISMATCH`: 类型不匹配

### 3. 值范围检查

**规则**: 字段值必须在允许的范围内。

**示例**:
```python
schema.required_field('port', type=int, min_value=1, max_value=65535)
schema.required_field('api_key', type=str, min_length=10, max_length=200)
schema.enum_field('log_level', ['DEBUG', 'INFO', 'WARNING', 'ERROR'])
schema.pattern_field('email', r'^[\w\.-]+@[\w\.-]+\.\w+$')
```

**错误类型**:
- `VALUE_OUT_OF_RANGE`: 值超出范围
- `INVALID_ENUM`: 不是枚举值之一
- `PATTERN_MISMATCH`: 不匹配正则表达式

### 4. 向后兼容检查

**规则**: 新配置结构应能读取旧配置。

**示例**:
```python
# 旧配置结构
old_config = {
    'api_key': 'sk-xxx',  # 旧字段
    'model': 'gpt-4'
}

# 新配置结构
new_config = {
    'api_keys': {
        'openai': {
            'api_key': 'sk-xxx',  # 新字段
            'model': 'gpt-4'
        }
    }
}

# 兼容性验证
validator = ConfigValidator()
compat_result = validator.check_compatibility(old_config, new_config)
```

---

## 💡 完整示例

### 示例 1: 多提供商 API Key 配置验证

```python
from .qwen.skills.config_structure_validator import ConfigValidator, ConfigSchema

def create_api_config_schema():
    """创建 API 配置 Schema"""
    schema = ConfigSchema()
    
    # 新结构：支持多提供商
    schema.required_field('api_keys', type=dict)
    schema.required_field('api_keys.openai', type=dict)
    schema.required_field('api_keys.openai.api_key', type=str, min_length=10)
    schema.required_field('api_keys.openai.base_url', type=str)
    
    schema.required_field('api_keys.anthropic', type=dict)
    schema.required_field('api_keys.anthropic.api_key', type=str, min_length=10)
    
    # 可选字段
    schema.optional_field('api_keys.openai.timeout', type=int, default=30)
    schema.optional_field('api_keys.openai.max_retries', type=int, default=3)
    
    # 旧结构兼容（兼容模式）
    schema.optional_field('api_key', type=str, 
                         description='旧版单API Key（向后兼容）')
    
    return schema

# 使用
schema = create_api_config_schema()
validator = ConfigValidator(schema=schema)

# 验证新配置
new_config = {
    'api_keys': {
        'openai': {
            'api_key': 'sk-valid-api-key',
            'base_url': 'https://api.openai.com',
            'timeout': 60
        },
        'anthropic': {
            'api_key': 'sk-anthropic-key'
        }
    }
}

result = validator.validate_dict(new_config)
print(f"新配置验证: {'✅ 通过' if result.is_valid else '❌ 失败'}")

# 验证旧配置（向后兼容）
old_config = {
    'api_key': 'sk-legacy-key',
    'model': 'gpt-4'
}

result = validator.validate_dict(old_config)
print(f"旧配置验证: {'✅ 通过' if result.is_valid else '❌ 失败'}")
```

### 示例 2: 配置脚本验证

```python
import json
from pathlib import Path
from .qwen.skills.config_structure_validator import ConfigValidator

def create_config_file(config_path: str, config: dict):
    """创建配置文件并验证"""
    path = Path(config_path)
    
    # 1. 写入配置
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # 2. 立即验证
    validator = ConfigValidator()
    result = validator.validate_file(path)
    
    if not result.is_valid:
        print(f"❌ 配置创建失败: {result.errors}")
        path.unlink()  # 删除无效文件
        return False
    
    # 3. 二次验证：重新读取
    with open(path, 'r', encoding='utf-8') as f:
        loaded_config = json.load(f)
    
    if loaded_config != config:
        print("⚠️ 警告：配置文件读写不一致")
        return False
    
    print("✅ 配置创建成功")
    return True
```

### 示例 3: 自动修复建议

```python
from .qwen.skills.config_structure_validator import ConfigValidator

validator = ConfigValidator()
result = validator.validate_file('config.json')

if not result.is_valid:
    print("发现配置问题:")
    for error in result.errors:
        print(f"  - {error.field}: {error.message}")
    
    # 生成修复建议
    suggestions = validator.suggest_fixes(result.errors)
    print("\n修复建议:")
    for suggestion in suggestions:
        print(f"  ✅ {suggestion}")
    
    # 自动修复（可选）
    if input("是否自动修复? (y/N): ").lower() == 'y':
        fixed_config = validator.apply_fixes(result.errors)
        validator.save_config(fixed_config, 'config.fixed.json')
        print("✅ 已生成修复后的配置文件")
```

---

## 📝 检查清单

### 配置结构变更前
- [ ] 列出所有读取该配置的模块
- [ ] 设计向后兼容方案
- [ ] 编写完整的 Schema 定义
- [ ] 测试新旧配置的兼容性

### 配置脚本开发前
- [ ] 明确配置文件的编码（UTF-8）
- [ ] 使用 `json.dump` 而非字符串模板
- [ ] 写入后立即验证格式
- [ ] 在多种路径下测试脚本

### 应用启动时
- [ ] 验证配置文件存在
- [ ] 验证配置格式有效
- [ ] 验证必需字段完整
- [ ] 提供友好的错误提示

---

## ⚠️ 常见陷阱

### 1. JSON 注释问题

**症状**: `json.decoder.JSONDecodeError: Expecting property name`

**原因**: JSON 不支持注释,但开发者常添加注释说明

**解决方案**: 
- 使用 JSON5 或 YAML 格式（支持注释）
- 在代码中使用 docstring 说明配置含义
- 提供示例配置文件

### 2. 编码问题

**症状**: 中文配置项读取为乱码

**原因**: 文件读写未指定 UTF-8 编码

**解决方案**:
```python
# ✅ 正确：明确指定编码
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
```

### 3. 路径问题

**症状**: 配置文件找不到或读取错误的文件

**原因**: 使用相对路径但工作目录不正确

**解决方案**:
```python
from pathlib import Path

# ✅ 正确：基于脚本或模块位置
config_path = Path(__file__).parent / 'config.json'

# 或基于项目根目录
project_root = Path(__file__).parent.parent
config_path = project_root / 'config' / 'config.json'
```

### 4. 类型推断错误

**症状**: YAML 中 `yes`/`no` 被解析为布尔值,`123` 被解析为整数

**原因**: YAML 自动类型推断

**解决方案**:
```yaml
# 使用引号强制为字符串
api_key: "123456"
enabled: "yes"
```

---

## 🛠️ 配置模板

### 最小配置模板

```json
{
  "api_keys": {
    "openai": {
      "api_key": "your-api-key-here",
      "base_url": "https://api.openai.com"
    }
  },
  "log_level": "INFO"
}
```

### 完整配置模板

```json
{
  "api_keys": {
    "openai": {
      "api_key": "your-openai-api-key",
      "base_url": "https://api.openai.com",
      "timeout": 30,
      "max_retries": 3,
      "models": ["gpt-4", "gpt-3.5-turbo"]
    },
    "anthropic": {
      "api_key": "your-anthropic-api-key",
      "base_url": "https://api.anthropic.com",
      "timeout": 30,
      "max_retries": 3,
      "models": ["claude-3-opus", "claude-3-sonnet"]
    }
  },
  "database": {
    "url": "sqlite:///translation.db",
    "pool_size": 5,
    "echo": false
  },
  "translation": {
    "max_concurrent": 3,
    "chunk_size": 1000,
    "retry_on_error": true,
    "fallback_enabled": true
  },
  "logging": {
    "level": "INFO",
    "file": "translation.log",
    "max_size_mb": 10,
    "backup_count": 3
  },
  "ui": {
    "theme": "light",
    "language": "zh-CN",
    "window_size": {
      "width": 1200,
      "height": 800
    }
  }
}
```

---

## 📚 关联技能

- **import_path_validator**: 验证配置模块的导入路径
- **gui_event_handler**: 配置界面事件处理
- **self_optimization**: 持续优化配置验证规则

---

**Skill 版本**: 1.0.0
**生效日期**: 2026-04-03
**下次审查**: 2026-05-03
**创建依据**: 最近修复任务中的配置结构不匹配错误分析