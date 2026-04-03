# GUI日志打点说明

## 概述

GUI已添加详细的日志打点，覆盖所有关键流程，方便调试和测试。

## 日志级别

### INFO - 重要事件
- 用户操作（点击开始翻译、停止、暂停等）
- 阶段完成（初始化完成、UI构建完成等）
- 进度里程碑（每10%记录一次）

### DEBUG - 详细信息
- 参数值（源文件路径、目标语言列表等）
- 状态检查（是否运行中、是否有数据等）
- 中间步骤（容器创建、服务获取等）

### WARNING - 警告信息
- 缺少必需输入（未选择文件、未选择语言等）
- 非致命错误（某个组件初始化失败但有fallback）

### ERROR - 错误信息
- 致命错误（翻译执行失败、服务无法启动等）
- 包含完整的错误类型、消息和堆栈跟踪

## 关键日志流程

### 1. GUI启动流程

```
============================================================
🚀 TranslationApp 初始化开始
============================================================
✅ 窗口基本属性设置完成
✅ 配置持久化初始化完成, config_file=config/config.json
初始化TranslationViewModel...
✅ TranslationViewModel初始化完成
初始化事件处理器...
✅ 事件处理器初始化完成
...
开始构建UI...
✅ UI构建完成
✅ 日志系统设置完成
✅ 历史管理器初始化完成
============================================================
✅ TranslationApp 初始化完成
============================================================
```

### 2. 翻译执行流程（9个步骤）

```
============================================================
🚀 用户点击开始翻译按钮
============================================================
当前状态:
  - 源文件: test.xlsx
  - 术语库: terminology.xlsx
  - 目标语言: ['English', 'Japanese', 'Korean']
  - 翻译模式: full
  - API提供商: deepseek
  - 源语言: 自动检测
创建翻译线程...
✅ 翻译线程已启动

🚀 开始执行翻译任务...
步骤1: 初始化服务...
🔧 开始初始化服务容器...
创建新的依赖容器...
✅ 依赖容器创建完成
尝试从容器获取TranslationFacade...
✅ 翻译外观服务已初始化
✅ 服务初始化完成

步骤2: 验证输入参数...
  - 源文件: test.xlsx
  - 目标语言数量: 3
  - 目标语言列表: ['English', 'Japanese', 'Korean']

步骤3: 更新UI状态为运行中...
✅ UI状态已更新

步骤4: 源语言设置: None (原始选择: 自动检测)
步骤5: 生成批次ID: batch_20260403_165300
步骤6: 输出路径: 自动生成

📤 开始调用translation_facade.translate_file...
  - 参数: source_excel_path=test.xlsx
  - 参数: target_langs=['English', 'Japanese', 'Korean']
  - 参数: output_excel_path=None
  - 参数: concurrency_limit=10
  - 参数: source_lang=None

✅ 翻译执行完成
  - 结果类型: BatchResult
  - 是否有results属性: True
  - 结果数量: 100
  - 成功率: 95.0%

步骤7: 记录翻译历史...
✅ 历史记录已保存

步骤8: 处理完成结果，成功率: 95.0%
步骤9: 清理翻译资源...
✅ 资源清理完成
✅ 资源清理完成
```

### 3. 进度更新日志

```
📊 进度: 10.0% (10/100), 速度: 2.5行/秒, ETA: 00:00:36
📊 进度: 20.0% (20/100), 速度: 2.8行/秒, ETA: 00:00:28
📊 进度: 30.0% (30/100), 速度: 3.0行/秒, ETA: 00:00:23
...
```

### 4. 错误报告

```
❌ 翻译执行失败: 'DependencyContainer' object has no attribute 'resolve'
  - 错误类型: AttributeError
  - 错误信息: 'DependencyContainer' object has no attribute 'resolve'
  - 堆栈跟踪:
Traceback (most recent call last):
  File "presentation/event_handlers.py", line 48, in _execute_translation
    self.app._initialize_services()
  File "presentation/gui_app.py", line 740, in _initialize_services
    self.translation_facade = self.container.resolve('TranslationFacade')
                              ^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DependencyContainer' object has no attribute 'resolve'
```

## 如何调整日志级别

### 方法1: 修改配置文件

在 `config/config.json` 中设置：

```json
{
  "log_level": "DEBUG",
  "log_granularity": "detailed"
}
```

### 方法2: 环境变量

```bash
# Windows
set LOG_LEVEL=DEBUG
python presentation\translation.py

# Linux/Mac
export LOG_LEVEL=DEBUG
python presentation/translation.py
```

### 日志级别选项

- `CRITICAL` - 仅记录严重错误
- `ERROR` - 记录错误和严重错误
- `WARNING` - 记录警告、错误和严重错误
- `INFO` - 记录一般信息、警告、错误（推荐）
- `DEBUG` - 记录所有信息，包括调试详情

## 常见问题排查

### 问题1: 翻译按钮无响应

查看日志中是否有：
```
🚀 用户点击开始翻译按钮
✅ 翻译线程已启动
```

如果没有，说明按钮事件未触发。

### 问题2: 服务初始化失败

查看日志中是否有：
```
❌ 无法从容器获取translation_facade: 'translation_facade'
💡 这可能是因为容器初始化时没有提供api_client
💡 请检查配置文件中的API密钥是否正确配置
```

如果有，检查配置文件中的API密钥。

### 问题3: 翻译执行失败

查看完整堆栈跟踪：
```
❌ 翻译执行失败: <错误信息>
  - 错误类型: <类型>
  - 错误信息: <详情>
  - 堆栈跟踪:
<完整堆栈>
```

根据堆栈跟踪定位具体代码位置。

### 问题4: 进度不更新

查看是否有进度日志：
```
📊 进度: 10.0% (10/100), 速度: 2.5行/秒, ETA: 00:00:36
```

如果没有但翻译在运行，可能是进度回调未正确设置。

## 测试建议

1. **首次运行**: 使用 `INFO` 级别，确认基本流程
2. **遇到问题**: 切换到 `DEBUG` 级别，查看详细参数
3. **修复后验证**: 使用 `INFO` 级别，确认问题已解决
4. **性能测试**: 使用 `INFO` 级别，观察进度和速度

## 日志输出位置

- **控制台**: 启动翻译平台时可见
- **GUI日志区**: 界面底部的"运行日志"文本框
- **日志文件**: 如果配置了文件handler，会保存到文件

## 性能影响

- `INFO` 级别: 最小影响（~1-2%性能损耗）
- `DEBUG` 级别: 中等影响（~5-10%性能损耗）
- 生产环境建议使用 `INFO` 级别
- 调试时临时切换到 `DEBUG` 级别
