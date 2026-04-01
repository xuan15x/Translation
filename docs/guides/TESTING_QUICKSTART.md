# 🧪 单元测试快速入门

## 项目已完成所有模块的单元测试覆盖！

### 📦 已创建的测试文件

| 测试文件 | 测试模块 | 测试数量 | 状态 |
|---------|---------|---------|------|
| `test_models.py` | models.py | 12+ | ✅ |
| `test_config.py` | config.py | 8+ | ✅ |
| `test_fuzzy_matcher.py` | fuzzy_matcher.py | 6+ | ✅ |
| `test_log_slice.py` | log_slice.py | 15+ | ✅ |
| `test_prompt_builder.py` | prompt_builder.py | 5+ | ✅ |
| `test_terminology_manager.py` | terminology_manager.py | 10+ | ✅ |
| `test_concurrency_controller.py` | concurrency_controller.py | 8+ | ✅ |
| **`test_api_stages.py`** | **api_stages.py** | **15+** | ✅ NEW |
| **`test_workflow_orchestrator.py`** | **workflow_orchestrator.py** | **18+** | ✅ NEW |
| **`test_logging_config.py`** | **logging_config.py** | **20+** | ✅ NEW |
| **`test_gui_app.py`** | **gui_app.py** | **25+** | ✅ NEW |
| **`test_translation.py`** | **translation.py** | **10+** | ✅ NEW |

**总计**: 12 个测试文件，150+ 个测试用例

---

## 🚀 快速开始

### Windows 用户（推荐）

双击运行批处理脚本：
```bash
run_tests.bat
```

或者使用 PowerShell：
```powershell
.\run_tests.ps1
```

### 命令行方式

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_api_stages.py -v

# 运行并查看覆盖率
pytest tests/ --cov=. --cov-report=html

# 运行单个测试用例
pytest tests/test_models.py::TestConfig::test_config_default_initialization -v
```

---

## 📊 测试报告

运行测试后会自动生成：

1. **终端输出** - 实时显示测试结果
2. **HTML 测试报告** - `test_report.html`
3. **覆盖率报告** - `htmlcov/index.html`

打开覆盖率报告：
```bash
# Windows
start htmlcov\index.html

# 或在文件管理器中直接打开 htmlcov/index.html
```

---

## 🎯 新增测试亮点

### 1. API 处理阶段测试 (`test_api_stages.py`)
- ✅ 模拟完整的 API 调用流程
- ✅ 测试 JSON 解析和错误处理
- ✅ 验证重试机制
- ✅ 测试 markdown code block 处理

**关键测试场景**:
- 成功翻译
- JSON 解析失败
- 空响应处理
- API 错误恢复
- 429 限流处理

### 2. 工作流编排测试 (`test_workflow_orchestrator.py`)
- ✅ 新文档翻译模式
- ✅ 旧文档校对模式
- ✅ 术语库精确匹配
- ✅ 双阶段处理流程
- ✅ 结果构建和验证

**关键测试场景**:
- 完整工作流模拟
- 术语库集成
- API 故障降级
- 本地命中优化

### 3. 日志配置测试 (`test_logging_config.py`)
- ✅ 彩色格式化器
- ✅ GUI 日志处理器
- ✅ 线程安全性
- ✅ 所有日志级别

**关键测试场景**:
- ANSI 颜色代码
- GUI 文本更新
- 异步日志记录
- 错误格式化

### 4. GUI 应用测试 (`test_gui_app.py`)
- ✅ 窗口初始化
- ✅ 文件选择对话框
- ✅ 语言选择功能
- ✅ 提示词验证
- ✅ 工作流启动逻辑
- ✅ 异步任务管理

**关键测试场景**:
- 用户交互模拟
- 输入验证
- 错误提示
- 状态管理

### 5. 主入口测试 (`test_translation.py`)
- ✅ 应用程序启动
- ✅ 多进程支持
- ✅ 事件循环
- ✅ 模块导入验证

---

## 🔧 测试工具配置

### pytest.ini 配置
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing
```

### 标记（Markers）
```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"
```

---

## 📝 测试示例

### 查看一个测试用例

```python
class TestAPIDraftStage:
    """APIDraftStage 类测试"""
    
    @pytest.mark.asyncio
    async def test_draft_stage_success(self, mock_client, mock_controller, 
                                        mock_semaphore, mock_config, sample_context):
        """测试初译阶段成功场景"""
        # 设置 mock 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"Trans": "Hello World", "Reason": "翻译完成"}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # 创建阶段实例
        stage = APIDraftStage(
            mock_client, mock_controller, mock_semaphore, mock_config,
            "You are a translator to {target_lang}"
        )
        
        # 执行测试
        result = await stage.execute(sample_context)
        
        # 验证结果
        assert result.success is True
        assert result.translation == "Hello World"
        assert result.reason == "翻译完成"
```

---

## 🐛 常见问题

### Q1: 测试失败怎么办？
1. 查看详细错误信息
2. 检查测试数据是否正确
3. 验证 mock 对象设置
4. 确认依赖是否安装

### Q2: 如何调试测试？
```bash
# 使用 pdb 调试
pytest tests/test_models.py -s --pdb

# 打印输出
pytest tests/ -s
```

### Q3: 覆盖率不高怎么办？
1. 查看 `htmlcov/index.html` 找出未覆盖的代码
2. 针对未覆盖的分支添加测试
3. 考虑边界情况和异常处理

### Q4: GUI 测试被跳过？
某些 GUI 测试需要图形环境，这是正常的。测试会自动检测环境并跳过不适用的测试。

---

## 📈 下一步

### 持续改进
1. ✅ 为每个新模块添加测试
2. ✅ 保持高覆盖率（目标 80%+）
3. ✅ 定期运行测试套件
4. ✅ 在 CI/CD 中集成测试

### 测试最佳实践
- 保持测试独立
- 使用有意义的测试名称
- 测试正常和异常路径
- 避免测试间的依赖
- 定期审查和重构测试

---

## 🎓 学习资源

- **pytest 文档**: https://docs.pytest.org/
- **Mock 最佳实践**: https://docs.python.org/3/library/unittest.mock.html
- **测试覆盖率**: https://coverage.readthedocs.io/

---

## ✨ 总结

本项目已完成全面的单元测试覆盖：

✅ **12 个测试文件**  
✅ **150+ 测试用例**  
✅ **所有核心模块已覆盖**  
✅ **包含集成测试**  
✅ **提供多种运行方式**  
✅ **自动生成测试报告**  

立即运行测试：
```bash
run_tests.bat
```

祝你测试愉快！🎉
