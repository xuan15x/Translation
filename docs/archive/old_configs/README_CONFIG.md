> ⚠️ **重要提示**: 本文档内容已整合到 [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md)  
> 建议优先阅读新手册获取更全面、更准确的信息
> 
> **整合日期**: 2026-04-01  
> **替代文档**: [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md) 第 3 章 - 配置指南

---

# 配置管理快速指南

## 📦 新增功能

本次更新将所有可配置参数暴露到外部配置文件，方便直接修改而无需改动代码。

## 🚀 快速上手

### 1️⃣ 创建配置文件

```bash
# 方法 1：使用管理脚本（推荐）
python scripts/manage_config.py create

# 方法 2：手动复制示例文件
cp config/config.example.yaml config.yaml
```

### 2️⃣ 编辑配置文件

打开 `config.yaml`，修改必要配置：

```yaml
# 必填：API 密钥
api_key: "your_api_key_here"

# 可选：调整模型参数
temperature: 0.3
initial_concurrency: 8
timeout: 60
```

### 3️⃣ 验证配置

```bash
python scripts/manage_config.py validate config.yaml
```

### 4️⃣ 启动应用

配置文件会自动被 GUI 应用加载，无需额外操作。

## 📋 主要配置分类

### API 配置
- `api_provider`: API 提供商（deepseek, openai 等）
- `api_key`: API 密钥
- `base_url`: API 基础 URL
- `model_name`: 模型名称

### 性能配置
- `initial_concurrency`: 初始并发数
- `max_concurrency`: 最大并发数
- `timeout`: 请求超时
- `pool_size`: 数据库连接池大小
- `cache_capacity`: 缓存容量

### 工作流配置
- `enable_two_pass`: 启用双阶段处理
- `skip_review_if_local_hit`: 本地命中时跳过校对
- `batch_size`: 批处理大小

### 术语库配置
- `similarity_low`: 模糊匹配阈值
- `exact_match_score`: 精确匹配置信度
- `multiprocess_threshold`: 多进程处理阈值

### 日志配置
- `log_level`: 日志级别
- `log_granularity`: 日志粒度
- `log_max_lines`: 日志最大行数

### GUI 配置
- `gui_window_title`: 窗口标题
- `gui_window_width`: 窗口宽度
- `gui_window_height`: 窗口高度

### 提示词配置
- `draft_prompt`: 初译提示词
- `review_prompt`: 校对提示词

## 🛠️ 配置管理工具

### create - 创建示例配置

```bash
# 创建 YAML 格式
python scripts/manage_config.py create -o config.yaml

# 创建 JSON 格式
python scripts/manage_config.py create -o config.json -f json
```

### validate - 验证配置

```bash
python scripts/manage_config.py validate config.yaml
```

输出示例：
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

### diff - 比较配置文件

```bash
python scripts/manage_config.py diff config.example.yaml config.yaml
```

### export-env - 导出环境变量模板

```bash
python scripts/manage_config.py export-env -c config.yaml -o .env.example
```

### merge - 合并配置文件

```bash
python scripts/manage_config.py merge base.yaml custom.yaml -o merged.yaml
```

### list - 列出所有配置选项

```bash
python scripts/manage_config.py list
```

## 💡 使用场景

### 场景 1：切换不同的 API 提供商

创建多个配置文件：

```bash
# DeepSeek 配置
cp config.example.yaml config.deepseek.yaml
# 编辑 config.deepseek.yaml，设置 deepseek 相关配置

# OpenAI 配置
cp config.example.yaml config.openai.yaml
# 编辑 config.openai.yaml，设置 openai 相关配置

# 使用时复制需要的配置
cp config.deepseek.yaml config.yaml
```

### 场景 2：开发和生产环境分离

```bash
# 开发环境（详细日志）
cat > config.dev.yaml << EOF
log_level: "DEBUG"
log_granularity: "verbose"
enable_performance_monitor: true
EOF

# 生产环境（优化性能）
cat > config.prod.yaml << EOF
log_level: "INFO"
log_granularity: "normal"
initial_concurrency: 15
max_concurrency: 20
EOF
```

### 场景 3：批量翻译优化

```yaml
# 高并发配置
initial_concurrency: 15
max_concurrency: 20
timeout: 90
batch_size: 2000

# 大术语库优化
multiprocess_threshold: 500
cache_capacity: 5000
pool_size: 10
```

### 场景 4：调试模式

```yaml
# 详细日志
log_level: "DEBUG"
log_granularity: "verbose"

# 禁用缓存测试
cache_ttl_seconds: 0

# 单阶段处理便于调试
enable_two_pass: false
```

## 🔐 安全建议

### ✅ 推荐做法

1. **使用环境变量存储 API 密钥**

```bash
# 在 .bashrc 或 .zshrc 中
export DEEPSEEK_API_KEY="your_key_here"
```

然后在配置文件中引用：
```yaml
api_key: ${DEEPSEEK_API_KEY}  # 或直接留空从环境变量读取
```

2. **忽略配置文件到版本控制**

```gitignore
# .gitignore
*.yaml
!config.example.yaml
*.json
!config.example.json
.env
```

3. **为不同环境创建配置**

```bash
config.dev.yaml      # 开发环境
config.test.yaml     # 测试环境
config.prod.yaml     # 生产环境
```

### ❌ 避免的做法

```yaml
# ❌ 不要在配置文件中硬编码真实 API 密钥
api_key: "sk-1234567890abcdef"  # 危险！

# ✅ 应该使用环境变量
api_key: ""  # 从 DEEPSEEK_API_KEY 环境变量读取
```

## 🔄 配置优先级

配置的生效优先级（从高到低）：

1. **GUI 界面配置**（运行时修改）
2. **配置文件**（config.yaml/json）
3. **环境变量**
4. **代码中的默认值**

## 📊 完整配置项列表

运行以下命令查看所有可用配置：

```bash
python scripts/manage_config.py list
```

输出示例：

```
📋 所有可用的配置选项:

API 配置:
--------------------------------------------------
  api_provider                   = deepseek
  api_key                        = 
  base_url                       = https://api.deepseek.com
  model_name                     = deepseek-chat

模型参数:
--------------------------------------------------
  temperature                    = 0.3
  top_p                          = 0.8

并发控制:
--------------------------------------------------
  initial_concurrency            = 8
  max_concurrency                = 10
...
```

## 🐛 故障排查

### 问题 1：配置文件未加载

**检查清单：**
- [ ] 配置文件是否在正确位置（项目根目录）
- [ ] 文件名是否为 `config.yaml`、`config.yml` 或 `config.json`
- [ ] 配置文件格式是否正确

**解决方法：**
```bash
# 验证配置文件
python scripts/manage_config.py validate config.yaml

# 查看详细错误
python -c "from data_access.config_persistence import ConfigPersistence; p = ConfigPersistence('config.yaml'); print(p.load())"
```

### 问题 2：配置不生效

**可能原因：**
- GUI 界面覆盖了配置文件
- 环境变量优先级更高
- 配置项名称拼写错误

**解决方法：**
1. 重启应用
2. 检查日志中的配置摘要
3. 使用 `list` 命令确认配置已加载

### 问题 3：环境变量未生效

**检查方法：**
```bash
# Windows PowerShell
echo $env:DEEPSEEK_API_KEY

# Linux/Mac
echo $DEEPSEEK_API_KEY

# Python 检查
python -c "import os; print(os.getenv('DEEPSEEK_API_KEY'))"
```

## 📚 相关文档

- [完整配置指南](CONFIGURATION_GUIDE.md) - 详细的配置说明
- [快速入门](QUICKSTART.md) - 平台使用入门
- [API 参考](../api/MODEL_CONFIG_API.md) - API 文档
- [架构设计](../architecture/ARCHITECTURE.md) - 系统架构

## 🆘 获取帮助

```bash
# 显示帮助信息
python scripts/manage_config.py --help
python scripts/manage_config.py create --help
```

如遇问题：
1. 查看日志输出
2. 验证配置文件格式
3. 检查环境变量
4. 参考本文档的故障排查部分
