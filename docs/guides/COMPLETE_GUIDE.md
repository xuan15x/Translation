# 完整使用指南

## 📋 目录

1. [快速入门](#快速入门)
2. [详细配置](#详细配置)
3. [术语库管理](#术语库管理)
4. [翻译流程](#翻译流程)
5. [高级功能](#高级功能)
6. [常见问题](#常见问题)

---

## 🚀 快速入门

### 1. 安装和配置 (5 分钟)

#### 步骤 1: 安装依赖

```bash
cd translation
pip install -r requirements.txt
```

#### 步骤 2: 配置 API Key

创建 `config/config.json`:

```json
{
  "api_key": "sk-your-api-key-here",
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-chat"
}
```

#### 步骤 3: 启动 GUI

```bash
python presentation/translation.py
```

### 2. 第一次翻译 (10 分钟)

#### 准备术语库

创建 Excel 文件 `terms.xlsx`,包含以下列:

| Key | 中文原文 | 英语 |
|-----|---------|------|
| TM_0 | 紫钻 | Purple Diamond |
| TM_1 | 蓝钻 | Blue Diamond |

#### 准备待翻译文件

创建 Excel 文件 `input.xlsx`,包含以下列:

| 原文 |
|------|
| 紫钻 |
| 蓝钻 |

#### 执行翻译

1. 在 GUI 中选择术语库 `terms.xlsx`
2. 选择待翻译文件 `input.xlsx`
3. 勾选目标语言 "英语"
4. 点击 "开始翻译任务"
5. 查看结果文件 `result.xlsx`

---

## ⚙️ 详细配置

### API 配置

#### 方式一：JSON 配置文件

```json
{
  "api_key": "your-key",
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-chat",
  "temperature": 0.3,
  "top_p": 0.8,
  "max_tokens": 512,
  "initial_concurrency": 8,
  "max_concurrency": 10,
  "batch_size": 10,
  "max_retries": 3,
  "retry_delay": 1
}
```

**配置项说明**:

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | string | 必填 | API 密钥 |
| `base_url` | string | https://api.deepseek.com | API 基础 URL |
| `model_name` | string | deepseek-chat | 模型名称 |
| `temperature` | float | 0.3 | 温度参数 (0-1) |
| `top_p` | float | 0.8 | Top-p 采样 |
| `max_tokens` | int | 512 | 最大 token 数 |
| `initial_concurrency` | int | 8 | 初始并发数 |
| `max_concurrency` | int | 10 | 最大并发数 |
| `batch_size` | int | 10 | 批次大小 |
| `max_retries` | int | 3 | 最大重试次数 |
| `retry_delay` | int | 1 | 重试延迟 (秒) |

#### 方式二：环境变量

```bash
export DEEPSEEK_API_KEY="your-key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export DEEPSEEK_MODEL="deepseek-chat"
```

### 日志配置

#### 日志级别

```python
from translation import LogLevel

LogLevel.DEBUG    # 调试模式，显示所有日志
LogLevel.INFO     # 信息模式，显示重要信息
LogLevel.WARNING # 警告模式，只显示警告和错误
LogLevel.ERROR    # 错误模式，只显示错误
```

#### 日志粒度

```python
from translation import LogGranularity

LogGranularity.MINIMAL   # 只显示错误
LogGranularity.BASIC     # 错误 + 警告
LogGranularity.NORMAL    # 错误 + 警告 + 重要
LogGranularity.DETAILED  # 正常 + 进度详情
LogGranularity.VERBOSE   # 详细调试模式
```

---

## 📚 术语库管理

### 创建术语库

#### Excel 格式要求

| 列名 | 必填 | 说明 |
|------|------|------|
| Key | 是 | 唯一标识，如 TM_0 |
| 中文原文 | 是 | 中文源文本 |
| 英语 | 否 | 英语译文 |
| 日语 | 否 | 日语译文 |
| ... | 否 | 其他语言 |

#### 示例数据

| Key | 中文原文 | 英语 | 日语 | 韩语 |
|-----|---------|------|------|------|
| TM_0 | 紫钻 | Purple Diamond | パープルダイヤモンド | 퍼플 다이아몬드 |
| TM_1 | 蓝钻 | Blue Diamond | ブルーダイヤモンド | 블루 다이아몬드 |
| TM_2 | 红钻 | Red Diamond | レッドダイヤモンド | 레드 다이아몬드 |

### 导入术语库

1. 准备 Excel 术语库文件
2. 在 GUI 中点击 "选择..." 按钮
3. 选择术语库文件
4. 查看预览确认数据

### 导出术语库

翻译完成后，术语库会自动保存到原路径。

也可以手动导出:

```python
from translation import TerminologyManager, Config

tm = TerminologyManager("terms.xlsx", config)

# 导出完整术语库
await tm.export_to_excel("full_terms.xlsx")

# 只导出新增术语
await tm.export_to_excel("new_terms.xlsx", export_new_only=True)
```

### 术语库查询

```python
from translation import TerminologyManager

tm = TerminologyManager("terms.xlsx", config)

# 精确匹配
term = tm.query("紫钻")
print(term)  # {'英语': 'Purple Diamond', ...}

# 模糊匹配
fuzzy_term = tm.query("紫色钻石", fuzzy_threshold=0.5)
print(fuzzy_term)  # 可能匹配到 "紫钻"
```

---

## 🔄 翻译流程

### 基本流程

```
1. 加载术语库
   ↓
2. 读取待翻译文件
   ↓
3. 创建任务列表
   ↓
4. 并发执行翻译
   ├─ 初译阶段
   └─ 校对阶段
   ↓
5. 保存结果
   ↓
6. 更新术语库
```

### 双阶段翻译

#### 第一阶段：初译

使用 `DEFAULT_DRAFT_PROMPT`:

```
Role: Professional Translator.
Task: Translate 'Src' to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Strictly follow provided TM.
3. Accurate and direct.
```

#### 第二阶段：校对

使用 `DEFAULT_REVIEW_PROMPT`:

```
Role: Senior Language Editor.
Task: Polish 'Draft' into native {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars. If no change, Reason="".
3. Focus on flow and tone.
```

### 自定义提示词

在 GUI 中编辑提示词:

1. 点击 "编辑提示词" 按钮
2. 修改初译或校对提示词
3. 保存并应用

---

## 🌟 高级功能

### 1. 批量翻译

一次翻译多个语言:

```python
tasks = [
    TaskContext(idx=0, key="TM_0", source_text="紫钻", target_lang="英语"),
    TaskContext(idx=1, key="TM_0", source_text="紫钻", target_lang="日语"),
    TaskContext(idx=2, key="TM_0", source_text="紫钻", target_lang="韩语")
]

results = await orchestrator.execute(tasks, "result.xlsx")
```

### 2. 术语库版本控制

查看变更历史:

```python
history = await tm.get_history_timeline(days=7)
for record in history:
    print(f"{record['timestamp']}: {record['change_type']}")
```

### 3. 翻译历史查询

```python
from translation import get_history_manager

history_manager = get_history_manager()

# 查询最近记录
records = history_manager.get_recent_records(limit=100)

# 获取统计信息
stats = history_manager.get_statistics()
print(f"成功率：{stats['success_rate']:.2%}")
```

### 4. 撤销操作

```python
from translation import get_undo_manager

undo_manager = get_undo_manager()

# 撤销上一步操作
await undo_manager.undo()

# 重做
await undo_manager.redo()
```

---

## ❓ 常见问题

### Q1: 翻译失败怎么办？

**A**: 按以下步骤排查:

1. 检查 API Key 是否正确
2. 切换到 "Verbose" 日志模式查看详细错误
3. 检查网络连接
4. 查看错误日志中的具体错误信息

### Q2: 如何提高翻译速度？

**A**: 

1. 增加并发数 (`initial_concurrency`)
2. 使用术语库减少 API 调用
3. 批量处理任务，而不是单个处理

### Q3: 术语匹配不准确？

**A**:

1. 确保术语库格式正确
2. 调整模糊匹配阈值
3. 添加更多专业术语到术语库

### Q4: 如何切换 API 提供商？

**A**:

```python
from translation import get_provider_manager

manager = get_provider_manager()
await manager.switch_provider("DeepSeek")
```

### Q5: 配置文件放在哪里？

**A**:

推荐放在 `config/` 目录下:
- `config/config.json`
- `config/config.yaml`

---

## 🔗 相关文档

- [API 参考](../api/API_REFERENCE_FULL.md)
- [最佳实践](BEST_PRACTICES.md)
- [故障排查](TROUBLESHOOTING.md)
- [架构设计](../architecture/ARCHITECTURE.md)
