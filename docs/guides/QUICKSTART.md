# 🚀 快速开始指南

## 1. 环境准备

### Python 版本要求
- Python 3.8 或更高版本 (推荐 Python 3.14+)

### 安装依赖
```bash
pip install -r requirements.txt
```

依赖包说明：
- `pandas>=2.0.0` - 数据处理
- `openai>=1.0.0` - API 客户端
- `thefuzz>=0.19.0` - 模糊匹配
- `openpyxl>=3.0.0` - Excel 文件操作

## 2. 配置 API 密钥和参数

### ⚠️ 重要提示
**必须设置 API 密钥！** 程序不再支持环境变量方式，必须通过配置文件或 GUI 界面设置。

---

### 方式 1: 创建配置文件（推荐）

#### 步骤 1: 复制示例配置文件

```bash
# 在项目根目录执行
cp config/config.example.json config/config.json
```

#### 步骤 2: 编辑配置文件

使用文本编辑器（如 VS Code、Notepad++）打开 `config/config.json`。

#### 步骤 3: 修改必要配置

**必须修改的配置**：

```json
{
  // 【API 配置】- 必须设置 ⚠️
  "api_key": "sk-your-actual-api-key-here",  // ← 替换为你的 API 密钥
  "api_provider": "deepseek",                 // API 提供商
  "base_url": "https://api.deepseek.com",     // API 基础 URL
  "model_name": "deepseek-chat"               // 使用的模型
}
```

**可选优化的配置**：

```json
{
  // 【模型参数】- 影响翻译质量
  "temperature": 0.3,    // 创造性：0.3 适合翻译（准确）
  "top_p": 0.8,          // 词汇多样性：0.8 平衡
  
  // 【并发控制】- 影响速度
  "initial_concurrency": 8,   // 初始并发：建议 8-10
  "max_concurrency": 10,      // 最大并发：根据 API 限制调整
  
  // 【重试机制】- 提高稳定性
  "max_retries": 3,      // 失败重试次数
  "timeout": 60,         // 请求超时（秒）
  
  // 【翻译流程】
  "enable_two_pass": true,           // 启用两阶段翻译
  "skip_review_if_local_hit": true,  // 本地命中跳过校对
  "batch_size": 1000                 // 批量翻译大小
}
```

#### 完整配置示例

```json
{
  "_comment": "AI 智能翻译工作台 - JSON 配置文件",
  "_version": "v2.2.0",
  
  // ============【API 配置】============
  "api_provider": "deepseek",
  "api_key": "sk-your-api-key",        // ⚠️ 必须修改
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-chat",
  
  // ============【模型参数】============
  "temperature": 0.3,
  "top_p": 0.8,
  
  // ============【并发控制】============
  "initial_concurrency": 8,
  "max_concurrency": 10,
  "concurrency_cooldown_seconds": 5.0,
  
  // ============【重试机制】============
  "retry_streak_threshold": 3,
  "base_retry_delay": 3.0,
  "max_retries": 3,
  "timeout": 60,
  
  // ============【翻译流程】============
  "enable_two_pass": true,
  "skip_review_if_local_hit": true,
  "batch_size": 1000,
  "gc_interval": 2,
  
  // ============【术语库】============
  "similarity_low": 60,
  "exact_match_score": 100,
  "multiprocess_threshold": 1000,
  
  // ============【性能优化】============
  "pool_size": 5,
  "cache_capacity": 2000,
  "cache_ttl_seconds": 3600,
  
  // ============【日志系统】============
  "log_level": "INFO",
  "log_granularity": "normal",
  "log_max_lines": 1000,
  
  // ============【GUI 界面】============
  "gui_window_title": "AI 智能翻译工作台 v2.0",
  "gui_window_width": 950,
  "gui_window_height": 800,
  
  // ============【提示词】============
  "draft_prompt": "Role: Professional Translator...",
  "review_prompt": "Role: Senior Language Editor...",
  
  // ============【语言配置】============
  "target_languages": [
    "英语", "日语", "韩语", "法语", "德语"
  ],
  "default_source_lang": "中文",
  "supported_source_langs": ["中文", "英语", "日语"],
  
  // ============【高级功能】============
  "enable_version_control": false,
  "enable_auto_backup": false,
  "enable_performance_monitor": false
}
```

---

### 方式 2: 使用 GUI 界面配置

启动程序后，在界面上直接配置：

1. **🔌 API 提供商** - 选择提供商（DeepSeek、OpenAI 等）
2. **API Key** - 输入 API 密钥
3. **Base URL** - API 基础 URL
4. **Model** - 选择模型

**优点**：
- ✅ 即时生效，无需重启
- ✅ 可以动态切换不同提供商
- ✅ 适合临时测试不同配置

**缺点**：
- ❌ 重启后需要重新配置
- ❌ 不适合团队协作（配置无法共享）

---

### 配置参数详解

#### 📌 API 配置（必须设置）

| 参数 | 说明 | 默认值 | 推荐值 |
|------|------|--------|---------|
| `api_key` | API 密钥 | 无 | `sk-...` |
| `api_provider` | API 提供商 | `deepseek` | `deepseek` / `openai` |
| `base_url` | API 基础 URL | DeepSeek URL | 根据提供商选择 |
| `model_name` | 模型名称 | `deepseek-chat` | 根据提供商选择 |

**常见 API 提供商配置**：

**DeepSeek（默认）**：
```json
{
  "api_provider": "deepseek",
  "api_key": "sk-your-deepseek-key",
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-chat"
}
```

**OpenAI**：
```json
{
  "api_provider": "openai",
  "api_key": "sk-your-openai-key",
  "base_url": "https://api.openai.com/v1",
  "model_name": "gpt-3.5-turbo"
}
```

---

#### 📌 模型参数（影响翻译质量）

| 参数 | 范围 | 说明 | 推荐值 |
|------|------|------|--------|
| `temperature` | 0.0-1.0 | 创造性：越低越准确 | `0.3`（翻译） |
| `top_p` | 0.0-1.0 | 词汇多样性 | `0.8`（平衡） |

**调优建议**：
- **准确翻译**：`temperature=0.1-0.3`，`top_p=0.7-0.8`
- **创意翻译**：`temperature=0.5-0.7`，`top_p=0.8-0.9`
- **技术文档**：`temperature=0.2`，`top_p=0.7`
- **文学翻译**：`temperature=0.5`，`top_p=0.9`

---

#### 📌 并发控制（影响速度和稳定性）

| 参数 | 说明 | 默认值 | 调优建议 |
|------|------|--------|----------|
| `initial_concurrency` | 初始并发数 | `8` | 根据 API 限制调整 |
| `max_concurrency` | 最大并发数 | `10` | 不要超过 API 限制 |
| `concurrency_cooldown_seconds` | 冷却时间 | `5.0` | 失败频繁时增加 |

**调优建议**：
- **快速翻译**（<1000 条）：`initial_concurrency=10`，`max_concurrency=15`
- **稳定翻译**（>5000 条）：`initial_concurrency=5`，`max_concurrency=8`
- **API 限制严格**：`initial_concurrency=2`，`max_concurrency=4`

---

#### 📌 重试机制（提高稳定性）

| 参数 | 说明 | 默认值 | 调优建议 |
|------|------|--------|----------|
| `retry_streak_threshold` | 连续失败阈值 | `3` | 网络差时增加 |
| `base_retry_delay` | 基础延迟 | `3.0` | 秒 |
| `max_retries` | 最大重试次数 | `3` | 重要任务增加 |
| `timeout` | 超时时间 | `60` | 秒 |

---

#### 📌 翻译流程

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `enable_two_pass` | 两阶段翻译 | `true` | ✅ 开启 |
| `skip_review_if_local_hit` | 本地命中跳过校对 | `true` | ✅ 开启 |
| `batch_size` | 批量大小 | `1000` | 大数据集增加 |
| `gc_interval` | 垃圾回收间隔 | `2` | 秒 |

---

#### 📌 术语库配置

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `similarity_low` | 最低相似度 | `60` | 0-100 |
| `exact_match_score` | 完全匹配分数 | `100` | 固定 |
| `multiprocess_threshold` | 多进程阈值 | `1000` | 大数据集增加 |

---

#### 📌 日志系统

| 参数 | 可选值 | 默认值 | 说明 |
|------|--------|--------|------|
| `log_level` | `DEBUG`/`INFO`/`WARNING`/`ERROR` | `INFO` | 调试用 DEBUG |
| `log_granularity` | `minimal`/`basic`/`normal`/`detailed`/`verbose` | `normal` | 详细用 verbose |
| `log_max_lines` | 整数 | `1000` | GUI 日志行数 |

---

### 配置验证

程序启动时会自动验证配置，如果配置错误会显示详细错误信息：

```
❌ 配置验证失败：共发现 2 个错误

【检查点 1】API 密钥验证
  ❌ 字段：api_key
     错误：API 密钥不能为空
     当前值：(空)
     要求：必须设置有效的 API 密钥
  
  💡 解决方案:
     1. 在 config/config.json 中设置 api_key
     2. 或在 GUI 界面输入 API 密钥

【检查点 2】Base URL 验证
  ❌ 字段：base_url
     错误：URL 格式不正确
     当前值：invalid-url
     要求：必须是有效的 HTTP/HTTPS URL
  
  💡 解决方案:
     1. 检查 URL 格式：https://api.example.com
     2. 确保 URL 以 http://或 https://开头
```

---

### 配置文件位置

**默认配置文件**：
- `config/config.json`（JSON 格式）
- `config/config.yaml`（YAML 格式）

**自定义配置文件**：
```bash
python presentation/translation.py path/to/your/config.json
```

---

### 配置检查清单

在开始翻译前，请确认：

- [ ] ✅ `api_key` 已设置为有效值
- [ ] ✅ `base_url` 格式正确
- [ ] ✅ `model_name` 与提供商匹配
- [ ] ✅ `temperature` 在 0.0-1.0 范围内
- [ ] ✅ `top_p` 在 0.0-1.0 范围内
- [ ] ✅ `initial_concurrency` >= 1
- [ ] ✅ `max_concurrency` >= `initial_concurrency`
- [ ] ✅ `timeout` >= 10 秒
- [ ] ✅ 配置文件保存在正确位置

---
## 3. 运行程序

### 方式 1: 在项目根目录运行（推荐）

```bash
# 确保在项目根目录 (C:\Users\13457\PycharmProjects\translation)
cd C:\Users\13457\PycharmProjects\translation

# 运行主程序
python presentation/translation.py
```

### 方式 2: 使用虚拟环境的 Python

```bash
# 激活虚拟环境（Windows PowerShell）
.\.venv\Scripts\Activate.ps1

# 运行程序
python presentation/translation.py
```

### 方式 3: 指定配置文件运行

```bash
# 使用自定义配置文件
python presentation/translation.py config.json
```

**注意**: 
- 必须在项目根目录运行，否则会出现导入错误
- 如果使用 PowerShell 遇到执行策略问题，可以使用：`.venv\Scripts\python.exe presentation\translation.py`

## 4. 使用步骤

### 首次使用
1. **选择术语库** - 点击"选择..."按钮，指定或创建术语库 Excel 文件
2. **选择待翻译文件** - 点击"选择..."按钮，选择包含中文原文的 Excel 文件
3. **选择模式** - 
   - 🆕 新文档 (双阶段): 适合全新翻译
   - 📝 旧文档校对：适合修改已有译文
4. **🔌 选择 API 提供商** - 从下拉框选择 API 提供商 (DeepSeek, OpenAI 等)
5. **🌍 选择目标语言** - 勾选需要的语言（可多选，默认为全部未选中状态）
6. **⚙️ 配置提示词** - 可根据需要调整（默认已优化）
7. **点击"开始翻译任务"**

### 输入文件格式

**待翻译 Excel 文件**:
| key | 中文原文 | 原译文 (可选) |
|-----|---------|-------------|
| 1   | 你好    | Hello       |
| 2   | 世界    | World       |

**术语库 Excel 文件** (自动创建):
| Key | 中文原文 | 英语 | 日语 | ... |
|-----|---------|------|------|-----|
| TM_0 | 你好 | Hello | こんにちは | ... |

## 5. 输出结果

程序会自动生成结果文件：
```
Result_YYYYMMDD_HHMMSS.xlsx
```

包含字段：
- key: 唯一标识
- target_lang: 目标语言
- source_text: 原文
- original_trans: 原译文
- draft_trans: 初译
- final_trans: 最终译文
- reason: 修改原因
- diagnosis: 诊断信息
- status: 状态 (SUCCESS/FAILED)

## 6. 模块独立使用示例

### 单独使用术语库管理
```python
import asyncio
from business_logic.terminology_manager import TerminologyManager
from infrastructure.models import Config

async def demo():
    config = Config()
    tm = TerminologyManager("my_terms.xlsx", config)
    
    # 查询相似翻译
    result = await tm.find_similar("需要翻译的文本", "英语")
    print(f"匹配结果：{result}")
    
    # 添加新术语
    await tm.add_entry("新术语", "英语", "New Term")
    
    # 保存并关闭
    await tm.shutdown()

asyncio.run(demo())
```

### 单独使用模糊匹配
```python
from data_access.fuzzy_matcher import FuzzyMatcher

items = [
    ("你好", "Hello"),
    ("世界", "World"),
    ("早上好", "Good morning")
]

best = FuzzyMatcher.find_best_match("你好啊", items, threshold=60)
print(f"最佳匹配：{best}")
```

### 单独使用并发控制器
```python
import asyncio
from infrastructure.concurrency_controller import AdaptiveConcurrencyController
from infrastructure.models import Config

async def demo():
    config = Config()
    controller = AdaptiveConcurrencyController(config)
    
    # 模拟请求成功
    await controller.adjust(success=True)
    print(f"当前并发数：{controller.get_limit()}")
    
    # 模拟请求失败
    await controller.adjust(success=False)
    print(f"调整后并发数：{controller.get_limit()}")

asyncio.run(demo())
```

## 7. 常见问题

### Q: 程序无响应？
A: 检查配置文件中的 `api_key` 是否已正确设置。

### Q: 导入错误？
A: 确保安装了所有依赖：`pip install -r requirements.txt`

### Q: 翻译速度慢？
A: 可以在配置文件中调整并发参数：
- `initial_concurrency`: 初始并发数 (默认 8)
- `max_concurrency`: 最大并发数 (默认 10)
- 系统具备自适应并发控制，会根据成功率动态调整

### Q: 如何切换 API 提供商？
A: 修改配置文件中的 `api_provider`，或在 GUI 界面选择不同提供商。

### Q: 配置文件在哪里？
A: 默认位置：`config/config.json`。可以从 `config/config.example.json` 复制。

### Q: 如何验证配置是否正确？
A: 程序启动时会自动验证配置，如有错误会显示详细信息。

### Q: 如何撤销操作？
A: 使用"↩️ 撤销"按钮可以撤销最近的操作，支持最多 100 步历史记录。

### Q: 如何修改提示词？
A: 在 GUI 界面的"提示词配置"区域直接编辑，或修改配置文件中的 `draft_prompt` 和 `review_prompt`。

### Q: 配置参数太多，不知道如何调整？
A: 新手建议使用默认配置，只修改 `api_key`。熟练后再根据需求调整其他参数。

## 8. 高级功能

### 8.1 多 API 提供商支持
系统支持动态切换多种 API 提供商：
- DeepSeek (默认)
- OpenAI
- 其他兼容 OpenAI 格式的 API

### 8.2 撤销/重做功能
- ↩️ 撤销：撤销最近的操作
- ↪️ 重做：恢复已撤销的操作
- 最多支持 100 步历史记录

### 8.3 进度跟踪
- 实时显示翻译进度百分比
- 预计剩余时间估算
- 翻译速度监控（项/秒）

### 8.4 翻译历史管理
- 📊 查看历史：浏览所有翻译记录
- 💾 导出历史：导出为 Excel 文件
- 🗑️ 清空历史：清除所有历史记录

### 8.5 术语库版本控制
- 📚 导入术语：从外部文件导入
- 📊 术语统计：查看术语库统计信息
- 📜 术语历史：查看术语变更历史

### 大数据集 (>10000 条)
1. 增加批处理大小：修改 `Config.batch_size`
2. 提高并发数：修改 `Config.max_concurrency`
3. 使用 SSD 存储术语库

### 小数据集 (<1000 条)
1. 减少并发数以节省资源
2. 降低 GC 频率：修改 `Config.gc_interval`

## 9. 性能调优建议

启用详细日志：
```python
# 在 logging_config.py 中
logger.setLevel(logging.DEBUG)  # 改为 DEBUG 级别
```

## 10. 调试技巧

启用详细日志：
```python
# 在 infrastructure/logging_config.py 中
logger.setLevel(logging.DEBUG)  # 改为 DEBUG 级别
```

查看日志输出：
- GUI 界面的日志区域会实时显示详细日志
- 支持彩色日志输出，便于区分不同级别

## 11. 测试相关

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/ -v

# 或使用 PowerShell 脚本
.\run_tests.ps1
```

### 测试结果
- 当前测试通过率：~85%
- 总测试数：346 个
- 通过：294 个
- 跳过：33 个（主要是 GUI 测试）

详细测试报告请参考：
- [测试总结](../development/TEST_SUMMARY.md)
- [自动修复报告](../AUTO_FIX_REPORT.md)

## 12. 下一步

- 📖 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解架构设计
- 🔗 查看 [DEPENDENCIES.md](DEPENDENCIES.md) 了解模块关系
- 📝 参考 [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) 了解重构详情
- 🧪 查看 [TEST_SUMMARY.md](../development/TEST_SUMMARY.md) 了解测试情况

---

**祝使用愉快！** 🎉
