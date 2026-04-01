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

## 2. 配置 API 密钥

设置 API 密钥（必须通过配置文件或 GUI 界面）：

**方式 1: 创建配置文件**
```bash
# 复制示例配置文件
cp config/config.example.json config/config.json
```

然后编辑 `config/config.json`，填入你的 API 密钥：
```json
{
  "api_key": "your_api_key_here",
  "api_provider": "deepseek",
  "base_url": "https://api.deepseek.com"
}
```

**方式 2: 使用 GUI 界面**
启动程序后，在界面的"🔌 API 提供商"区域直接输入 API 密钥。

**注意**: 
- ❌ 已废弃环境变量方式
- ✅ 支持动态切换 API 提供商，包括 DeepSeek、OpenAI 等
- ✅ 可在 GUI 界面的"🔌 API 提供商"下拉框中选择不同提供商
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
A: 检查是否设置了 `DEEPSEEK_API_KEY` 环境变量

### Q: 导入错误？
A: 确保安装了所有依赖：`pip install -r requirements.txt`

### Q: 翻译速度慢？
A: 可以在 GUI 界面或通过配置文件调整并发参数：
- `initial_concurrency`: 初始并发数 (默认 8)
- `max_concurrency`: 最大并发数 (默认 10)
- 系统具备自适应并发控制，会根据成功率动态调整

### Q: 如何切换 API 提供商？
A: 在 GUI 界面的"🔌 API 提供商"区域选择不同提供商，支持 DeepSeek、OpenAI 等

### Q: 如何撤销操作？
A: 使用"↩️ 撤销"按钮可以撤销最近的操作，支持最多 100 步历史记录

### Q: 如何修改提示词？
A: 在 GUI 界面的"提示词配置"区域直接编辑，或修改 `config.py` 中的默认值

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
