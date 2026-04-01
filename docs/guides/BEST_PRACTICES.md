# AI 智能翻译工作台 - 最佳实践指南

本指南提供详细的使用说明、最佳实践和常见问题解决方案，帮助您充分利用翻译系统。

## 📋 目录

1. [快速入门](#快速入门)
2. [配置优化](#配置优化)
3. [术语库管理](#术语库管理)
4. [性能调优](#性能调优)
5. [故障排查](#故障排查)
6. [常见问题](#常见问题)

---

## 快速入门

### 1. 安装和配置

#### 环境要求
- Python 3.8+
-  pip 20.0+
-  Excel 文件支持（openpyxl）

#### 安装步骤
```bash
# 克隆项目
git clone <your-repo-url>
cd translation

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-test.txt  # 测试工具（可选）
```

#### API Key 配置
```bash
# 方式 1: 环境变量（推荐）
export DEEPSEEK_API_KEY="your-api-key-here"

# 方式 2: 配置文件
cp config.example.json config.json
# 编辑 config.json，填入 API key
```

### 2. 启动应用

```bash
# GUI 模式（推荐新手）
python translation.py

# 命令行模式（高级用户）
python translation.py config.json
```

### 3. 首次使用

1. **选择术语库**: 点击"选择..."按钮，选择或创建术语库 Excel 文件
2. **选择源文件**: 选择待翻译的 Excel 文件
3. **选择目标语言**: 勾选需要的语言（可多选）
4. **配置提示词**: 可使用默认提示词，也可自定义
5. **开始翻译**: 点击"开始翻译任务"

---

## 配置优化

### 1. 核心参数说明

```python
class Config:
    # API 相关
    api_key: str = ""              # API 密钥
    base_url: str = "https://api.deepseek.com"
    model_name: str = "deepseek-chat"
    
    # 性能相关
    temperature: float = 0.3       # 创造性（0-2，越低越确定）
    top_p: float = 0.8            # 采样概率（0-1）
    timeout: int = 60             # 超时时间（秒）
    
    # 并发控制
    initial_concurrency: int = 5   # 初始并发数
    max_concurrency: int = 10      # 最大并发数
    
    # 批处理
    batch_size: int = 50          # 每批处理数量
    gc_interval: int = 10         # 垃圾回收间隔
    
    # 术语库
    similarity_low: int = 60       # 最低匹配置信度
    exact_match_score: int = 100   # 精确匹配分数
    multiprocess_threshold: int = 500  # 多进程阈值
```

### 2. 推荐配置组合

#### 小型项目（< 1000 条）
```python
config = Config(
    batch_size=20,
    initial_concurrency=3,
    max_concurrency=5,
    timeout=30
)
```

#### 中型项目（1000-5000 条）
```python
config = Config(
    batch_size=50,
    initial_concurrency=5,
    max_concurrency=10,
    timeout=60
)
```

#### 大型项目（> 5000 条）
```python
config = Config(
    batch_size=100,
    initial_concurrency=8,
    max_concurrency=15,
    timeout=90,
    enable_two_pass=False  # 禁用双阶段以提升速度
)
```

### 3. 配置文件示例（JSON）

```json
{
    "api_key": "sk-your-key-here",
    "base_url": "https://api.deepseek.com",
    "model_name": "deepseek-chat",
    "temperature": 0.3,
    "top_p": 0.8,
    "timeout": 60,
    "initial_concurrency": 5,
    "max_concurrency": 10,
    "batch_size": 50,
    "enable_two_pass": true,
    "skip_review_if_local_hit": false
}
```

---

## 术语库管理

### 1. 术语库格式

Excel 文件格式要求：

| 中文原文 | 英语 | 法语 | 德语 | 日语 |
|---------|------|------|------|------|
| 你好    | Hello| Bonjour | Hallo | こんにちは |
| 世界    | World| Monde | Welt | 世界 |

**注意**:
- 第一列必须是"中文原文"
- 其他列名为目标语言名称
- 避免空行和重复项

### 2. 术语库维护最佳实践

#### 定期清理
```python
from terminology_manager import TerminologyManager

tm = TerminologyManager("terms.xlsx", config)

# 获取性能统计
stats = await tm.get_performance_stats()
print(f"总术语数：{stats['database']['total_entries']}")

# 导出备份
await tm.export_history("backup_terms.json")
```

#### 版本控制集成
```python
# 启用 Git 版本控制
tm.enable_version_control(repo_path=".")

# 提交更改
await tm.commit_changes("添加医疗术语")

# 查看历史
history = tm.get_version_history(limit=10)
for commit in history:
    print(f"{commit['time']}: {commit['message']}")
```

### 3. 批量导入术语

```python
import pandas as pd
from terminology_manager import TerminologyManager

tm = TerminologyManager("terms.xlsx", config)

# 从现有 Excel 导入
df = pd.read_excel("existing_terms.xlsx")

entries = []
for _, row in df.iterrows():
    src = row['中文原文']
    for lang in ['英语', '法语', '德语']:
        if lang in row and pd.notna(row[lang]):
            entries.append((src, lang, str(row[lang])))

# 批量添加
await tm.batch_add_entries_optimized(entries, batch_size=100)
```

---

## 性能调优

### 1. 缓存优化

```python
from infrastructure.cache import TerminologyCache

# 创建专用缓存
cache = TerminologyCache(capacity=2000)

# 预热缓存（常用术语）
common_terms = [
    ("你好", "英语", "Hello"),
    ("谢谢", "英语", "Thank you"),
    # ... 更多常用术语
]

for src, lang, trans in common_terms:
    await cache.set_exact_match(src, lang, {
        'original': src,
        'translation': trans,
        'score': 100
    })
```

### 2. 并发控制调优

```python
from concurrency_controller import AdaptiveConcurrencyController

controller = AdaptiveConcurrencyController(config)

# 监控并发状态
async def monitor():
    while True:
        limit = controller.get_limit()
        stats = controller.get_stats()
        
        print(f"当前并发限制：{limit}")
        print(f"成功率：{stats['success_rate']}%")
        
        await asyncio.sleep(10)

# 启动监控
asyncio.create_task(monitor())
```

### 3. 内存管理

```python
import tracemalloc
import gc

# 启用内存跟踪
tracemalloc.start()

# 定期清理
async def memory_cleanup():
    while True:
        await asyncio.sleep(300)  # 每 5 分钟
        
        # 强制 GC
        collected = gc.collect()
        print(f"回收对象：{collected}")
        
        # 打印内存使用
        current, peak = tracemalloc.get_traced_memory()
        print(f"当前内存：{current / 1024 / 1024:.2f}MB")
        print(f"峰值内存：{peak / 1024 / 1024:.2f}MB")

# 启动清理任务
asyncio.create_task(memory_cleanup())
```

### 4. 批量处理策略

```python
# 最优批次大小计算
def calculate_batch_size(total_items: int) -> int:
    if total_items < 100:
        return 20
    elif total_items < 1000:
        return 50
    else:
        return 100

# 分批执行
batch_size = calculate_batch_size(len(tasks))
results = []

for i in range(0, len(tasks), batch_size):
    batch = tasks[i:i + batch_size]
    batch_results = await asyncio.gather(
        *[orchestrator.process_task(t) for t in batch],
        return_exceptions=True
    )
    results.extend([r for r in batch_results if r])
    
    # 每批后短暂休息
    if i > 0 and i % (batch_size * 10) == 0:
        await asyncio.sleep(1)
```

---

## 故障排查

### 1. 常见问题速查表

| 问题现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| API 调用失败 | API Key 无效 | 检查环境变量或配置文件 |
| 翻译速度慢 | 并发度过低 | 增加 `max_concurrency` |
| 内存占用高 | 批次过大 | 减小 `batch_size` |
| 术语不生效 | 匹配置信度低 | 降低 `similarity_low` |
| 进度卡住 | 网络超时 | 增加 `timeout` |
| GUI 无响应 | 主线程阻塞 | 检查异步实现 |

### 2. 详细故障排查

#### 问题 1: API 调用频繁失败

**症状**: 大量请求返回 429 错误

**解决方案**:
```python
config = Config(
    initial_concurrency=3,  # 降低初始并发
    max_concurrency=5,      # 降低最大并发
    base_retry_delay=2,     # 增加基础延迟
    max_retries=5           # 增加重试次数
)
```

#### 问题 2: 术语库查询慢

**症状**: 每次查询超过 100ms

**解决方案**:
```python
# 1. 启用缓存
tm.cache = TerminologyCache(capacity=2000)

# 2. 使用多进程（大数据量）
config.multiprocess_threshold = 200  # 降低阈值

# 3. 预加载常用术语
await tm.find_similar("常用术语", "英语")  # 预热缓存
```

#### 问题 3: 内存泄漏

**症状**: 长时间运行后内存持续增长

**解决方案**:
```python
# 1. 启用内存跟踪
tm.enable_memory_tracking()

# 2. 定期优化
async def optimize():
    while True:
        await asyncio.sleep(600)  # 每 10 分钟
        await tm.optimize_memory()

# 3. 限制批次大小
config.batch_size = 50  # 不要太大
```

#### 问题 4: 备份失败

**症状**: 无法创建备份文件

**解决方案**:
```python
# 1. 检查磁盘空间
import shutil
total, used, free = shutil.disk_usage("/")
print(f"可用空间：{free / (1024**3):.2f}GB")

# 2. 手动创建备份
backup_path = await tm.create_backup("手动备份")

# 3. 清理旧备份
tm.version_controller.cleanup_old_backups(
    keep_days=7,
    keep_count=5
)
```

### 3. 日志分析

#### 启用详细日志
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

#### 关键日志指标
- `INFO`: 正常操作流程
- `WARNING`: 需要注意但不影响运行
- `ERROR`: 错误，需要处理
- `DEBUG`: 调试信息（性能数据等）

---

## 常见问题

### Q1: 如何切换不同的 API 提供商？

**A**: 使用 API Provider Manager:
```python
from api_provider import get_provider_manager, APIProvider

manager = get_provider_manager()

# 切换到 DeepSeek
manager.set_provider(APIProvider.DEEPSEEK)

# 切换到 OpenAI
manager.set_provider(APIProvider.OPENAI)

# 切换到 Azure
manager.set_provider(APIProvider.AZURE)
```

### Q2: 如何恢复误删的术语？

**A**: 使用版本控制或备份恢复:
```python
# 方法 1: 从 Git 恢复
tm.restore_from_git(commit_hash="abc123")

# 方法 2: 从备份恢复
backups = tm.list_backups()
await tm.restore_from_backup(backups[0]['path'])
```

### Q3: 如何合并多个术语库？

**A**: 使用批量导入:
```python
# 加载多个术语库
tm1 = TerminologyManager("terms1.xlsx", config)
tm2 = TerminologyManager("terms2.xlsx", config)

# 导出所有术语
all_entries = []
for tm in [tm1, tm2]:
    for src, trans_dict in tm.db.items():
        for lang, trans in trans_dict.items():
            all_entries.append((src, lang, trans))

# 创建新术语库并导入
tm_new = TerminologyManager("merged.xlsx", config)
await tm_new.batch_add_entries_optimized(all_entries, batch_size=100)
```

### Q4: 如何提高翻译质量？

**A**: 
1. **完善术语库**: 术语越多越准确
2. **优化提示词**: 明确要求和格式
3. **启用双阶段**: `config.enable_two_pass = True`
4. **人工校对**: 重要文档建议人工审核

### Q5: 支持哪些文件格式？

**A**: 
- ✅ Excel (.xlsx) - 完全支持
- ⚠️ CSV (.csv) - 需要转换
- ❌ Word (.docx) - 暂不支持
- ❌ PDF (.pdf) - 暂不支持

---

## 📞 获取帮助

如果遇到问题无法解决：

1. **查看日志**: 检查详细错误信息
2. **搜索 Issue**: GitHub Issues 可能有类似问题
3. **提交 Issue**: 提供详细的重现步骤
4. **社区讨论**: 加入用户群组交流

---

**文档版本**: 2.0.0  
**最后更新**: 2026-03-19  
**维护者**: Development Team
