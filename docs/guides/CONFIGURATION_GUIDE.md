# 配置管理指南

本指南详细介绍 AI 翻译工作台的所有配置选项和使用方法。

## 📁 配置文件位置

配置文件应放置在项目根目录，支持以下格式：
- `config.yaml` 或 `config.yml`（推荐）
- `config.json`

## 🚀 快速开始

### 1. 创建示例配置文件

```bash
# 使用命令行工具创建
python scripts/manage_config.py create

# 或手动复制示例文件
cp config/config.example.yaml config.yaml
```

### 2. 编辑配置文件

打开 `config.yaml`，修改以下必要配置：

```yaml
# 必填：API 密钥（建议使用环境变量）
api_key: "your_api_key_here"

# 可选：修改其他配置
temperature: 0.3
initial_concurrency: 8
```

### 3. 验证配置

```bash
python scripts/manage_config.py validate config.yaml
```

## 📋 完整配置项说明

### API 配置

```yaml
# API 提供商（支持：deepseek, openai, moonshot, zhipu, baidu, alibaba, anthropic, custom）
api_provider: "deepseek"

# API 密钥（强烈建议使用环境变量 DEEPSEEK_API_KEY）
api_key: "your_api_key_here"

# API 基础 URL
base_url: "https://api.deepseek.com"

# 模型名称
model_name: "deepseek-chat"
```

### 模型参数

```yaml
# 温度参数（0-2）
# 0.0 = 非常保守
# 0.3 = 平衡（推荐）
# 1.0+ = 非常创造性
temperature: 0.3

# 核采样参数（0-1）
# 较低的值为更保守的预测
top_p: 0.8
```

### 并发控制

```yaml
# 初始并发请求数
initial_concurrency: 8

# 最大并发请求数（自适应调整上限）
max_concurrency: 10

# 并发度降低后的冷却时间（秒）
concurrency_cooldown_seconds: 5.0
```

### 重试配置

```yaml
# 连续成功多少次后提升并发度
retry_streak_threshold: 3

# 基础重试延迟（秒）
base_retry_delay: 3.0

# 单个请求最大重试次数
max_retries: 3

# 请求超时时间（秒）
timeout: 60
```

### 工作流配置

```yaml
# 是否启用双阶段处理（初译 + 校对）
enable_two_pass: true

# 本地术语精确命中时跳过校对
skip_review_if_local_hit: true

# 批处理大小
batch_size: 1000

# 垃圾回收间隔
gc_interval: 2
```

### 术语库配置

```yaml
# 模糊匹配最低相似度阈值（0-100）
similarity_low: 60

# 精确匹配置信度
exact_match_score: 100

# 超过多少条术语时使用多进程处理
multiprocess_threshold: 1000
```

### 性能优化

```yaml
# SQLite 连接池大小
pool_size: 5

# 术语缓存容量（条目数）
cache_capacity: 2000

# 缓存过期时间（秒），0 表示永不过期
cache_ttl_seconds: 3600
```

### 日志配置

```yaml
# 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
log_level: "INFO"

# 日志粒度（minimal, basic, normal, detailed, verbose）
log_granularity: "normal"

# GUI 日志控件最大行数
log_max_lines: 1000
```

### GUI 配置

```yaml
# 窗口标题
gui_window_title: "AI 智能翻译工作台 v2.0"

# 窗口宽度（像素）
gui_window_width: 950

# 窗口高度（像素）
gui_window_height: 800
```

### 提示词配置

```yaml
# 初译提示词模板（支持多行文本）
draft_prompt: |
  Role: Professional Translator.
  Task: Translate 'Src' to {target_lang}.
  Constraints:
  1. Output JSON ONLY: {{"Trans": "string"}}.
  2. Strictly follow provided TM.
  3. Accurate and direct.

# 校对提示词模板
review_prompt: |
  Role: Senior Language Editor.
  Task: Polish 'Draft' into native {target_lang}.
  Constraints:
  1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
  2. 'Reason': Max 10 chars. If no change, Reason="".
  3. Focus on flow and tone.
```

### 语言配置

```yaml
# 目标语言列表
target_languages:
  - 英语
  - 日语
  - 韩语
  - 法语
  - 德语
  # ... 更多语言

# 默认源语言
default_source_lang: "中文"

# 支持的源语言列表
supported_source_langs:
  - 中文
  - 英语
  - 日语
  - 韩语
  - 法语
  - 德语
```

### 版本控制和备份（实验性）

```yaml
# 是否启用 Git 版本控制
enable_version_control: false

# 是否启用自动备份
enable_auto_backup: false

# 备份目录路径
backup_dir: ".terminology_backups"

# 备份策略（hourly, daily, weekly, per_batch）
backup_strategy: "daily"
```

### 性能监控

```yaml
# 是否启用性能监控
enable_performance_monitor: false

# 性能采样间隔（秒）
perf_sample_interval: 1.0

# 性能历史记录数量
perf_history_size: 300
```

## 🔧 配置管理工具

### 创建配置文件

```bash
# 创建 YAML 格式
python scripts/manage_config.py create -o config.yaml

# 创建 JSON 格式
python scripts/manage_config.py create -o config.json -f json
```

### 验证配置

```bash
python scripts/manage_config.py validate config.yaml
```

### 比较配置文件

```bash
python scripts/manage_config.py diff config.example.yaml config.yaml
```

### 导出环境变量模板

```bash
python scripts/manage_config.py export-env -c config.yaml -o .env.example
```

### 合并配置文件

```bash
python scripts/manage_config.py merge base.yaml custom.yaml -o merged.yaml
```

### 列出所有配置选项

```bash
python scripts/manage_config.py list
```

## 🌍 环境变量优先级

配置的优先级顺序（从高到低）：

1. **GUI 界面配置**（运行时修改）
2. **配置文件**（config.yaml/json）
3. **环境变量**
4. **默认值**

### 常用环境变量

```bash
# API 密钥
export DEEPSEEK_API_KEY="your_key_here"

# 基础 URL
export DEEPSEEK_BASE_URL="https://api.deepseek.com"

# 模型名称
export MODEL_NAME="deepseek-chat"

# 温度参数
export TEMPERATURE=0.3

# Top P
export TOP_P=0.8
```

## 💡 最佳实践

### 1. 安全配置

- ✅ **永远不要**将 API 密钥提交到版本控制系统
- ✅ 使用环境变量管理敏感信息
- ✅ 为不同环境创建不同的配置文件

```bash
# 开发环境
cp config.example.yaml config.dev.yaml

# 生产环境
cp config.example.yaml config.prod.yaml

# 在 .gitignore 中忽略
echo "*.yaml" >> .gitignore
echo "!config.example.yaml" >> .gitignore
```

### 2. 性能调优

```yaml
# 高并发场景（适合批量翻译）
initial_concurrency: 15
max_concurrency: 20
timeout: 90

# 低延迟场景（适合实时翻译）
initial_concurrency: 5
max_concurrency: 8
timeout: 30

# 大数据量术语库
multiprocess_threshold: 500
cache_capacity: 5000
pool_size: 10
```

### 3. 调试模式

```yaml
# 详细日志
log_level: "DEBUG"
log_granularity: "verbose"

# 启用性能监控
enable_performance_monitor: true
perf_sample_interval: 0.5

# 禁用缓存（测试用）
cache_ttl_seconds: 0
```

### 4. 离线模式

```yaml
# 完全依赖本地术语库
skip_review_if_local_hit: true
enable_two_pass: false

# 提高模糊匹配阈值
similarity_low: 80
```

## 🔍 故障排查

### 配置加载失败

```bash
# 检查配置文件语法
python scripts/manage_config.py validate config.yaml

# 查看详细错误信息
python -c "from data_access.config_persistence import ConfigPersistence; p = ConfigPersistence('config.yaml'); print(p.load())"
```

### 配置不生效

1. 检查配置文件路径是否正确
2. 确认配置文件格式（YAML/JSON）
3. 查看日志输出中的配置摘要
4. 尝试重启应用

### 环境变量未生效

```bash
# 检查环境变量是否设置成功
# Windows PowerShell
echo $env:DEEPSEEK_API_KEY

# Linux/Mac
echo $DEEPSEEK_API_KEY

# Python 检查
python -c "import os; print(os.getenv('DEEPSEEK_API_KEY'))"
```

## 📚 相关文档

- [快速入门指南](../guides/QUICKSTART.md)
- [API 参考文档](../api/API_REFERENCE.md)
- [架构设计文档](../architecture/ARCHITECTURE.md)
- [测试指南](../development/TESTING_GUIDE.md)

## 🆘 获取帮助

```bash
# 显示命令帮助
python scripts/manage_config.py --help
python scripts/manage_config.py create --help
```

如遇问题，请：
1. 查看日志输出
2. 验证配置文件格式
3. 检查环境变量设置
4. 参考故障排查部分
