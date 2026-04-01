# 配置管理系统 - 快速参考卡片

## 🚀 30 秒快速开始

```bash
# 1. 创建配置文件（30 秒）
python scripts/manage_config.py create

# 2. 编辑 config.yaml，修改 API 密钥
api_key: "your_api_key_here"

# 3. 验证配置（5 秒）
python scripts/manage_config.py validate

# 4. 启动翻译平台
python presentation/gui_app.py
```

## 📋 核心配置文件

| 文件 | 说明 | 用途 |
|------|------|------|
| `config.yaml` | 主配置文件 | 日常使用 |
| `config.example.yaml` | 示例配置 | 参考模板 |
| `config.dev.yaml` | 开发配置 | 调试用 |
| `config.prod.yaml` | 生产配置 | 部署用 |

## 🔑 关键配置项（Top 10）

```yaml
# 1. API 密钥（必填）
api_key: "your_key_here"

# 2. 模型选择
model_name: "deepseek-chat"

# 3. 并发控制（性能关键）
initial_concurrency: 8
max_concurrency: 10

# 4. 超时设置
timeout: 60

# 5. 工作流模式
enable_two_pass: true

# 6. 术语库匹配
similarity_low: 60

# 7. 日志级别
log_level: "INFO"

# 8. 缓存配置
cache_capacity: 2000

# 9. 提示词
draft_prompt: |
  Role: Professional Translator...

# 10. 语言列表
target_languages:
  - 英语
  - 日语
```

## 🛠️ 管理命令速查

### 创建配置
```bash
python scripts/manage_config.py create                    # YAML 格式
python scripts/manage_config.py create -f json            # JSON 格式
```

### 验证配置
```bash
python scripts/manage_config.py validate config.yaml
```

### 比较配置
```bash
python scripts/manage_config.py diff file1.yaml file2.yaml
```

### 导出环境变量
```bash
python scripts/manage_config.py export-env
```

### 合并配置
```bash
python scripts/manage_config.py merge base.yaml custom.yaml
```

### 列出所有选项
```bash
python scripts/manage_config.py list
```

## 💻 Python API 使用

### 获取配置值

```python
from config.loader import get_config, get_config_loader

# 简单用法
api_key = get_config('api_key')
temperature = get_config('temperature', 0.3)  # 带默认值

# 嵌套键
base_url = get_config('api.base_url')

# 获取完整配置
all_config = get_config_loader().get_all()
```

### 更新配置

```python
from config.loader import update_config, save_config

# 批量更新
update_config({
    'temperature': 0.5,
    'initial_concurrency': 12
})

# 保存更改
save_config('config.updated.yaml')
```

### 分类获取配置

```python
loader = get_config_loader()

# API 配置
api_cfg = loader.get_api_config()

# 性能配置
perf_cfg = loader.get_performance_config()

# 工作流配置
workflow_cfg = loader.get_workflow_config()
```

## 🎯 常见场景配置

### 场景 1：批量翻译（高吞吐）

```yaml
initial_concurrency: 15
max_concurrency: 20
timeout: 90
batch_size: 2000
multiprocess_threshold: 500
```

### 场景 2：实时翻译（低延迟）

```yaml
initial_concurrency: 5
max_concurrency: 8
timeout: 30
batch_size: 500
skip_review_if_local_hit: true
```

### 场景 3：调试模式

```yaml
log_level: "DEBUG"
log_granularity: "verbose"
enable_performance_monitor: true
cache_ttl_seconds: 0
```

### 场景 4：离线模式

```yaml
enable_two_pass: false
skip_review_if_local_hit: true
similarity_low: 80
exact_match_score: 100
```

### 场景 5：多语言测试

```yaml
target_languages:
  - 英语
  - 日语
  - 韩语
  - 法语
  
default_source_lang: "中文"
```

## 🔐 安全最佳实践

### ✅ 推荐做法

```bash
# 1. 使用环境变量存储 API 密钥
export DEEPSEEK_API_KEY="sk-xxxxx"

# 2. 配置文件留空
cat > config.yaml << EOF
api_key: ""  # 从环境变量读取
EOF

# 3. Git 忽略配置文件
echo "*.yaml" >> .gitignore
echo "!config.example.yaml" >> .gitignore
```

### ❌ 避免的做法

```yaml
# ❌ 硬编码 API 密钥
api_key: "sk-1234567890abcdef"

# ❌ 提交配置文件到 Git
git add config.yaml
```

## 📊 配置优先级

```
GUI 界面配置（运行时）  ← 最高优先级
    ↓
配置文件（config.yaml）
    ↓
环境变量（DEEPSEEK_API_KEY）
    ↓
代码默认值  ← 最低优先级
```

## 🐛 快速故障排查

### 配置未加载

```bash
# 检查文件是否存在
ls -la config.yaml

# 验证格式
python scripts/manage_config.py validate config.yaml
```

### 环境变量未生效

```bash
# 检查环境变量
echo $DEEPSEEK_API_KEY

# Python 检查
python -c "import os; print(os.getenv('DEEPSEEK_API_KEY'))"
```

### 配置不生效

```bash
# 重启应用
# 查看日志中的配置摘要
# 使用 list 命令确认
python scripts/manage_config.py list
```

## 📚 详细文档索引

| 文档 | 位置 | 用途 |
|------|------|------|
| [快速指南](README_CONFIG.md) | docs/guides/ | 30 秒上手 |
| [完整指南](CONFIGURATION_GUIDE.md) | docs/guides/ | 详细说明 |
| [总结文档](CONFIG_MANAGEMENT_SUMMARY.md) | docs/ | 技术细节 |
| 示例配置 | config/ | 参考模板 |
| 管理脚本 | scripts/manage_config.py | 工具使用 |

## 🆘 获取帮助

```bash
# 显示帮助
python scripts/manage_config.py --help
python scripts/manage_config.py create --help

# 查看版本（如果有）
python scripts/manage_config.py --version
```

## 🎓 学习路径

```
1. 快速指南 (5 分钟)
   └─> 创建配置文件并运行
   
2. 基础配置 (10 分钟)
   └─> 修改 API 密钥、模型参数
   
3. 进阶配置 (20 分钟)
   └─> 调整并发、缓存、日志
   
4. 高级用法 (30 分钟)
   └─> 自定义提示词、多环境配置
```

## ⚡ 快捷键（如果使用 GUI）

- `Ctrl + L` - 切换日志级别
- `Ctrl + P` - 显示性能监控
- `Ctrl + C` - 加载配置文件
- `Ctrl + S` - 保存当前配置

## 📈 性能调优速查

| 目标 | 配置建议 |
|------|---------|
| **提升速度** | ↑ concurrency, ↑ timeout, ↑ batch_size |
| **节省成本** | ↓ max_retries, enable_two_pass=false |
| **提高质量** | enable_two_pass=true, ↓ temperature |
| **减少内存** | ↓ cache_capacity, ↓ pool_size |
| **调试问题** | log_level=DEBUG, enable_performance_monitor=true |

## 🎁 彩蛋命令

```bash
# 查看所有可用命令
python scripts/manage_config.py help

# 创建特定环境的配置
python scripts/manage_config.py create -o config.dev.yaml
python scripts/manage_config.py create -o config.prod.yaml
```

---

**💡 提示**: 将此卡片保存为书签，需要时快速查阅！
