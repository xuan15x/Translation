# 故障排查手册

本手册提供详细的故障排查指南，帮助您快速定位和解决常见问题。

## 🔍 问题诊断流程

```mermaid
graph TD
    A[问题发生] --> B{问题类型？}
    B -->|API 错误 | C[检查网络和 API Key]
    B -->|性能问题 | D[检查资源配置]
    B -->|数据问题 | E[检查文件格式]
    B -->|GUI 问题 | F[检查界面状态]
    
    C --> G{问题解决？}
    D --> G
    E --> G
    F --> G
    
    G -->|是 | H[✅ 完成]
    G -->|否 | I[查看详细日志]
    I --> J[搜索 Issue]
    J --> K[提交 Bug Report]
```

---

## 📋 常见错误代码速查

### API 相关错误

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| `401 Unauthorized` | 认证失败 | 检查 API Key 是否正确 |
| `429 Too Many Requests` | 请求过多 | 降低并发度，增加延迟 |
| `503 Service Unavailable` | 服务不可用 | 稍后重试或切换 API |
| `TimeoutError` | 请求超时 | 增加 timeout 参数 |
| `ConnectionError` | 连接错误 | 检查网络连接 |

### 数据相关错误

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| `FileNotFoundError` | 文件不存在 | 检查文件路径 |
| `PermissionError` | 权限错误 | 检查文件读写权限 |
| `ExcelReadError` | Excel 读取失败 | 检查文件格式 |
| `DataValidationError` | 数据验证失败 | 检查数据格式 |

### 系统相关错误

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| `MemoryError` | 内存不足 | 减小 batch_size |
| `DiskSpaceError` | 磁盘空间不足 | 清理磁盘空间 |
| `ProcessError` | 进程错误 | 重启应用 |

---

## 🔧 详细排查步骤

### 1. API 调用失败

#### 症状
```
ERROR: API 请求失败：401 Unauthorized
ERROR: 无效的 API key
```

#### 排查步骤

**步骤 1: 验证 API Key**
```bash
# Linux/Mac
echo $DEEPSEEK_API_KEY

# Windows PowerShell
echo $env:DEEPSEEK_API_KEY

# Windows CMD
echo %DEEPSEEK_API_KEY%
```

**步骤 2: 测试 API 连通性**
```python
import requests

response = requests.get(
    "https://api.deepseek.com/health",
    headers={"Authorization": f"Bearer {os.environ.get('DEEPSEEK_API_KEY')}"}
)

print(f"状态码：{response.status_code}")
print(f"响应：{response.text}")
```

**步骤 3: 检查配置文件**
```python
from config_persistence import ConfigPersistence

persistence = ConfigPersistence("config.json")
config_dict = persistence.load()

print(f"API Key: {config_dict.get('api_key', '未设置')[:10]}...")
print(f"Base URL: {config_dict.get('base_url')}")
```

**步骤 4: 查看完整日志**
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
```

---

### 2. 翻译速度过慢

#### 症状
- 每批处理时间超过 5 分钟
- CPU 使用率低（< 50%）
- 大量时间在等待

#### 排查步骤

**步骤 1: 检查当前配置**
```python
from models import Config

config = Config()
print(f"并发数：{config.initial_concurrency} - {config.max_concurrency}")
print(f"批次大小：{config.batch_size}")
print(f"超时时间：{config.timeout}s")
```

**步骤 2: 监控并发状态**
```python
async def monitor_concurrency():
    controller = orchestrator.controller
    
    while True:
        await asyncio.sleep(5)
        
        current_limit = controller.get_limit()
        stats = controller.get_stats()
        
        print(f"当前限制：{current_limit}")
        print(f"成功率：{stats['success_rate']:.1f}%")
        print(f"活跃任务：{stats.get('active_tasks', 0)}")

# 启动监控
asyncio.create_task(monitor_concurrency())
```

**步骤 3: 优化配置**
```python
# 提高并发度
config.initial_concurrency = 8
config.max_concurrency = 15

# 增大批次
config.batch_size = 100

# 禁用双阶段（如果不需要）
config.enable_two_pass = False
```

**步骤 4: 检查网络延迟**
```python
import time
import requests

def test_latency():
    urls = [
        "https://api.deepseek.com",
        "https://api.openai.com",
    ]
    
    for url in urls:
        start = time.time()
        try:
            response = requests.get(url, timeout=5)
            latency = (time.time() - start) * 1000
            print(f"{url}: {latency:.0f}ms")
        except Exception as e:
            print(f"{url}: 失败 - {e}")

test_latency()
```

---

### 3. 内存占用过高

#### 症状
- 内存使用持续增长
- 系统变慢或卡死
- 出现 MemoryError

#### 排查步骤

**步骤 1: 启用内存监控**
```python
import tracemalloc
import gc

tracemalloc.start()

# 定期打印内存信息
async def memory_monitor():
    while True:
        await asyncio.sleep(60)
        
        current, peak = tracemalloc.get_traced_memory()
        print(f"当前：{current / 1024 / 1024:.2f}MB")
        print(f"峰值：{peak / 1024 / 1024:.2f}MB")
        
        # 强制 GC
        collected = gc.collect()
        if collected > 0:
            print(f"回收：{collected} 个对象")

asyncio.create_task(memory_monitor())
```

**步骤 2: 识别内存泄漏**
```python
from memory_profiler import profile

@profile
def process_large_batch():
    # 你的处理逻辑
    pass

# 运行并查看内存分析
process_large_batch()
```

**步骤 3: 优化内存使用**
```python
# 1. 减小批次大小
config.batch_size = 20  # 从 50 降低到 20

# 2. 定期 GC
async def periodic_gc():
    while True:
        await asyncio.sleep(300)  # 每 5 分钟
        gc.collect()

asyncio.create_task(periodic_gc())

# 3. 清理缓存
await tm.cache.clear_all()
```

---

### 4. 术语库查询慢

#### 症状
- 每次查询超过 100ms
- 大数据量时更明显
- CPU 使用率高

#### 排查步骤

**步骤 1: 检查术语库规模**
```python
tm = TerminologyManager("terms.xlsx", config)
stats = await tm.get_performance_stats()

print(f"术语总数：{stats['database']['total_entries']}")
print(f"总翻译数：{stats['database']['total_translations']}")
```

**步骤 2: 启用缓存**
```python
# 创建缓存层
tm.cache = TerminologyCache(capacity=2000)

# 预热缓存
common_queries = ["你好", "谢谢", "再见"]
for query in common_queries:
    await tm.find_similar(query, "英语")
```

**步骤 3: 使用多进程**
```python
# 降低多进程阈值
config.multiprocess_threshold = 100  # 默认 500

# 对于大数据量自动使用多进程
if len(tm.db) > config.multiprocess_threshold:
    print("自动启用多进程加速")
```

---

### 5. GUI 无响应

#### 症状
- 点击按钮无反应
- 界面卡死
- 进度条不更新

#### 排查步骤

**步骤 1: 检查主线程阻塞**
```python
import threading

def check_main_thread():
    main_thread = threading.main_thread()
    print(f"主线程状态：{main_thread.is_alive()}")
    print(f"主线程名称：{main_thread.name}")

check_main_thread()
```

**步骤 2: 验证异步实现**
```python
# 错误示例 - 阻塞主线程
def start_workflow():
    asyncio.run(execute_task())  # ❌ 会阻塞

# 正确示例 - 使用线程
def start_workflow():
    thread = threading.Thread(target=run_async_loop, daemon=True)
    thread.start()  # ✅ 不阻塞
```

**步骤 3: 检查日志输出**
```python
# GUI 日志处理器
from logging_config import GUILogHandler

handler = GUILogHandler(log_text_widget)
logger.addHandler(handler)
```

---

## 🛠️ 高级调试技巧

### 1. 性能分析

```python
import cProfile
import pstats
from io import StringIO

def profile_translation():
    pr = cProfile.Profile()
    pr.enable()
    
    # 执行翻译
    asyncio.run(run_translation())
    
    pr.disable()
    
    # 输出统计
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # 前 20 个最耗时的函数
    
    print(s.getvalue())

profile_translation()
```

### 2. 断点调试

```python
import pdb

def debug_point():
    # ... 代码 ...
    
    pdb.set_trace()  # 设置断点
    
    # ... 代码 ...

# 常用命令:
# n (next) - 执行下一行
# c (continue) - 继续执行
# l (list) - 显示代码
# p variable - 打印变量
# q (quit) - 退出调试
```

### 3. 日志级别控制

```python
import logging

# 开发环境 - 详细日志
logging.basicConfig(level=logging.DEBUG)

# 生产环境 - 只记录警告和错误
logging.basicConfig(level=logging.WARNING)

# 特定模块详细日志
logging.getLogger('terminology_manager').setLevel(logging.DEBUG)
logging.getLogger('api_stages').setLevel(logging.DEBUG)
```

---

## 📊 健康检查清单

### 定期检查项目

- [ ] API 连通性测试
- [ ] 术语库备份验证
- [ ] 内存使用检查
- [ ] 磁盘空间检查
- [ ] 日志文件大小检查
- [ ] 配置文件有效性验证
- [ ] 依赖包版本检查

### 自动化健康检查脚本

```python
async def health_check():
    """系统健康检查"""
    checks = {
        'api': False,
        'disk': False,
        'memory': False,
        'config': False
    }
    
    # 1. API 检查
    try:
        client = AsyncOpenAI(api_key=config.api_key)
        # 简单测试
        checks['api'] = True
    except:
        checks['api'] = False
    
    # 2. 磁盘检查
    import shutil
    total, used, free = shutil.disk_usage("/")
    checks['disk'] = free > (1024 ** 3)  # > 1GB
    
    # 3. 内存检查
    import psutil
    mem = psutil.virtual_memory()
    checks['memory'] = mem.available > (512 * 1024 * 1024)  # > 512MB
    
    # 4. 配置检查
    try:
        config.validate()
        checks['config'] = True
    except:
        checks['config'] = False
    
    # 输出结果
    print("健康检查结果:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    return all(checks.values())
```

---

## 🆘 获取支持

### 提交 Bug Report 模板

```markdown
**问题描述**:
[清晰简洁的问题描述]

**重现步骤**:
1. 第一步...
2. 第二步...
3. 看到错误...

**期望行为**:
[应该发生什么]

**实际行为**:
[实际发生了什么]

**环境信息**:
- Python 版本：3.8.x
- 操作系统：Windows 11
- 应用版本：2.0.0

**日志输出**:
```
[粘贴相关日志]
```

**截图**:
[如有必要，添加截图]
```

### 联系方式

- **GitHub Issues**: [提交 Issue](https://github.com/your-repo/translation/issues)
- **讨论区**: [GitHub Discussions](https://github.com/your-repo/translation/discussions)
- **邮件**: support@example.com

---

**手册版本**: 2.0.0  
**最后更新**: 2026-03-19  
**维护团队**: Support Team
