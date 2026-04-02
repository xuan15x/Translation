# 配置管理脚本使用指南

## 📋 概述

`scripts/manage_config.py` 是一个强大的配置管理工具，用于生成、验证和管理 AI 翻译平台的配置文件。

## 🚀 快速开始

### 查看所有可用命令

```bash
python scripts/manage_config.py --help
```

### 创建示例配置文件

```bash
# 创建 YAML 格式（推荐）
python scripts/manage_config.py create

# 创建 JSON 格式
python scripts/manage_config.py create -f json -o config.example.json
```

### 查看禁止事项配置详情

```bash
python scripts/manage_config.py prohibitions
```

## 🔧 命令详解

### 1. `create` - 创建示例配置文件

**用途**: 生成包含所有配置项的示例文件

**选项**:
- `-o, --output`: 输出文件路径（默认：`config.yaml`）
- `-f, --format`: 文件格式（`yaml` 或 `json`）

**示例**:
```bash
# 创建默认 YAML 配置
python scripts/manage_config.py create

# 创建 JSON 配置到指定路径
python scripts/manage_config.py create -o my_config.json -f json
```

### 2. `validate` - 验证配置文件

**用途**: 检查配置文件的有效性和完整性

**参数**:
- `config`: 配置文件路径

**示例**:
```bash
python scripts/manage_config.py validate config.yaml
```

**输出示例**:
```
🔍 验证配置文件：config.yaml
✅ 配置文件验证通过！

📊 配置摘要:
  API 提供商：deepseek
  模型：deepseek-chat
  并发度：8 - 10
  超时：60 秒
  工作流：双阶段
```

### 3. `list` - 列出所有配置选项

**用途**: 显示所有可用的配置项及其默认值

**特点**:
- 按类别分组显示
- 包含禁止事项配置的详细信息
- 显示每个类别的规则数量

**示例**:
```bash
python scripts/manage_config.py list
```

**输出包含**:
- API Configuration
- Model Parameters
- Concurrency Control
- Retry Configuration
- Workflow Configuration
- Terminology Configuration
- Performance Optimization
- Logging Configuration
- GUI Configuration
- Prompt Configuration
- **Prohibition Configuration** ⭐ (新增)
- Language Configuration
- Version Control & Backup
- Performance Monitoring

### 4. `prohibitions` - 显示禁止事项配置详情 ⭐ NEW!

**用途**: 查看所有禁止事项类别和规则

**输出内容**:
- 所有禁止事项类别及其规则
- 翻译类型与禁止规则的映射关系
- 自定义配置提示

**示例**:
```bash
python scripts/manage_config.py prohibitions
```

**输出示例**:
```
======================================================================
Prohibition Configuration Details
======================================================================

Prohibition Categories:
----------------------------------------------------------------------

global_prohibitions:
  Rules: 8
  1. 禁止输出原文或保留未翻译的内容
  2. 禁止添加解释性文字或注释
  ...

match3_prohibitions:
  Rules: 5
  1. 禁止使用超过 4 个字的道具名称（UI 限制）
  ...

Translation Type Mapping:
----------------------------------------------------------------------
  match3_item          -> global, match3 (2 categories)
  match3_dialogue      -> global, match3, dialogue (3 categories)
  ...

======================================================================
Tip: Customize these rules in config/config.json
Docs: docs/guides/PROHIBITION_CONFIG_GUIDE.md
```

### 5. `diff` - 比较配置文件

**用途**: 显示两个配置文件的差异

**参数**:
- `file1`: 第一个配置文件
- `file2`: 第二个配置文件

**示例**:
```bash
python scripts/manage_config.py diff config.example.yaml config.yaml
```

### 6. `export-env` - 导出环境变量模板

**用途**: 从配置文件生成 `.env.example` 文件

**选项**:
- `-c, --config`: 源配置文件路径（默认：`config.yaml`）
- `-o, --output`: 输出文件路径（默认：`.env.example`）

**示例**:
```bash
python scripts/manage_config.py export-env
```

### 7. `merge` - 合并配置文件

**用途**: 将两个配置文件合并为一个

**参数**:
- `base`: 基础配置文件
- `override`: 覆盖配置文件

**选项**:
- `-o, --output`: 输出文件路径（默认：`config.merged.yaml`）

**示例**:
```bash
python scripts/manage_config.py merge base.yaml custom.yaml -o merged.yaml
```

## 🎯 常用工作流

### 新手入门流程

```bash
# 1. 创建示例配置
python scripts/manage_config.py create

# 2. 查看禁止事项规则
python scripts/manage_config.py prohibitions

# 3. 复制并修改配置
copy config.yaml config.local.yaml

# 4. 验证修改后的配置
python scripts/manage_config.py validate config.local.yaml
```

### 自定义禁止事项

```bash
# 1. 查看当前禁止事项
python scripts/manage_config.py prohibitions

# 2. 编辑配置文件
# 在 config/config.json 中修改 prohibition_config

# 3. 验证配置
python scripts/manage_config.py validate config/config.json

# 4. 查看所有配置确认修改
python scripts/manage_config.py list | Select-String "Prohibition"
```

### 配置迁移流程

```bash
# 1. 比较新旧配置
python scripts/manage_config.py diff old_config.yaml new_config.yaml

# 2. 合并配置（保留自定义）
python scripts/manage_config.py merge new_config.yaml my_custom.yaml -o final.yaml

# 3. 验证最终配置
python scripts/manage_config.py validate final.yaml
```

## 📊 配置类别说明

### Prohibition Configuration (新增)

这是最重要的新增功能，允许你自定义翻译时的禁止规则。

**配置结构**:

```json
{
  "prohibition_config": {
    "global_prohibitions": [...],      // 通用规则
    "match3_prohibitions": [...],      // 三消游戏专项
    "rpg_prohibitions": [...],         // RPG 游戏专项
    "ui_prohibitions": [...],          // UI 界面专项
    "dialogue_prohibitions": [...]     // 对话剧情专项
  },
  "prohibition_type_map": {
    "match3_item": ["global", "match3"],
    ...
  }
}
```

**查看方法**:
```bash
python scripts/manage_config.py prohibitions
```

**配置位置**:
- JSON: `config/config.json`
- YAML: `config/config.yaml`

## 💡 最佳实践

1. **首次使用**: 先运行 `create` 创建示例配置
2. **了解规则**: 运行 `prohibitions` 查看默认禁止规则
3. **自定义前**: 使用 `list` 了解所有配置项
4. **修改后**: 始终运行 `validate` 验证配置
5. **版本升级**: 使用 `diff` 比较新旧配置
6. **团队协作**: 使用 `export-env` 生成环境变量模板

## 🔗 相关文档

- `docs/guides/PROHIBITION_CONFIG_GUIDE.md` - 禁止事项配置详细指南
- `docs/guides/PROHIBITION_CONFIG_QUICKREF.md` - 快速参考卡片
- `docs/development/FORBIDDEN_RULES_CONFIG_FEATURE.md` - 功能实现说明

## ⚠️ 注意事项

1. **编码问题**: Windows PowerShell 请使用英文输出（已自动处理）
2. **路径问题**: 脚本会自动添加项目根目录到 Python 路径
3. **配置验证**: 修改配置后务必运行验证命令
4. **禁止事项**: 修改禁止规则可能影响翻译质量，请谨慎调整

## 🆘 故障排查

### 问题：找不到模块错误

**解决**: 确保在项目根目录运行
```bash
cd C:\Users\13457\PycharmProjects\translation
python scripts/manage_config.py list
```

### 问题：配置验证失败

**解决**: 检查配置文件语法和必填字段
```bash
python scripts/manage_config.py validate config.yaml
```

### 问题：禁止事项未生效

**解决**: 
1. 确认配置文件中包含 `prohibition_config`
2. 重启应用使配置生效
3. 运行测试验证：`python tests/test_prohibition_config.py`

## 📈 更新日志

### v3.0.1 (本次更新)

- ✨ 新增 `prohibitions` 命令查看禁止事项配置
- ✨ `list` 命令增加禁止事项配置详情
- 🐛 修复 Windows 控制台编码问题
- 📝 更新配置管理脚本文档

### v3.0.0

- 初始版本发布
