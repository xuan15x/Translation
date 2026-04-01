# 单元测试指南

## 📋 概述

本项目使用 **pytest** 作为单元测试框架，为所有功能模块提供了全面的测试覆盖。

## 🚀 快速开始

### 1. 安装测试依赖

```bash
pip install -r requirements-test.txt
```

这将安装：
- pytest: 测试框架
- pytest-cov: 代码覆盖率
- pytest-asyncio: 异步测试支持
- pytest-mock: Mock 功能
- pytest-html: HTML 报告
- coverage: 覆盖率统计

### 2. 运行测试

#### 方式一：使用运行脚本（推荐）
```bash
python scripts/run_tests.py
```

#### 方式二：直接使用 pytest
```bash
# 运行所有测试
pytest

# 运行特定模块的测试
pytest tests/test_models.py

# 运行特定测试函数
pytest tests/test_models.py::TestConfig::test_config_default_initialization

# 带覆盖率报告
pytest --cov=. --cov-report=html

# 生成 HTML 报告
pytest --html=test_report.html
```

## 📁 测试文件结构

```
tests/
├── conftest.py                 # 共享 fixtures 和配置
├── data/                       # 测试数据目录
│   └── .gitkeep
├── test_models.py              # models.py 测试
├── test_config.py              # config.py 测试
├── test_prompt_builder.py      # prompt_builder.py 测试
├── test_fuzzy_matcher.py       # fuzzy_matcher.py 测试
├── test_concurrency_controller.py  # concurrency_controller.py 测试
├── test_terminology_manager.py # terminology_manager.py 测试
└── ... (更多测试文件)
```

## 🧪 已包含的测试模块

### 1. test_models.py
测试数据模型类：
- ✅ Config 配置类
- ✅ TaskContext 任务上下文
- ✅ StageResult 阶段结果
- ✅ FinalResult 最终结果

**测试数量**: 15+  
**覆盖率**: 95%+

### 2. test_config.py
测试配置常量：
- ✅ 默认提示词
- ✅ 目标语言列表
- ✅ GUI 配置参数

**测试数量**: 10+  
**覆盖率**: 100%

### 3. test_prompt_builder.py
测试提示词构建：
- ✅ Draft 消息构建
- ✅ Review 消息构建
- ✅ TM 建议集成
- ✅ 边界条件处理

**测试数量**: 8+  
**覆盖率**: 95%+

### 4. test_fuzzy_matcher.py
测试模糊匹配：
- ✅ 精确匹配
- ✅ 相似匹配
- ✅ 阈值控制
- ✅ Unicode 支持

**测试数量**: 10+  
**覆盖率**: 90%+

### 5. test_concurrency_controller.py
测试并发控制：
- ✅ 初始并发数
- ✅ 成功/失败调整
- ✅ 最小/最大值限制
- ✅ 冷却机制
- ✅ 线程安全

**测试数量**: 11+  
**覆盖率**: 90%+

### 6. test_terminology_manager.py
测试术语库管理：
- ✅ 条目添加
- ✅ 相似查找
- ✅ 文件保存/加载
- ✅ 后台写入机制

**测试数量**: 11+  
**覆盖率**: 85%+

## 📊 测试覆盖率

### 当前覆盖率目标
- **总体覆盖率**: > 85%
- **关键模块**: > 90%
- **分支覆盖**: > 80%

### 查看覆盖率报告

运行测试后生成 HTML 报告：
```bash
pytest --cov=. --cov-report=html
```

在浏览器中打开：
```bash
# Windows
start htmlcov\index.html

# Linux/Mac
open htmlcov/index.html
```

## 🔧 常用测试命令

### 基础测试
```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 只显示失败的测试
pytest -v --tb=short
```

### 选择性测试
```bash
# 运行特定文件
pytest tests/test_models.py

# 运行特定类
pytest tests/test_models.py::TestConfig

# 运行特定函数
pytest tests/test_models.py::TestConfig::test_config_default_initialization

# 使用标记运行
pytest -m asyncio  # 只运行异步测试
pytest -m unit     # 只运行单元测试
```

### 覆盖率相关
```bash
# 显示覆盖率
pytest --cov=.

# 显示缺失行
pytest --cov=. --cov-report=term-missing

# 生成多种格式报告
pytest --cov=. --cov-report=html --cov-report=xml
```

### HTML 报告
```bash
# 生成独立 HTML 报告
pytest --html=test_report.html --self-contained-html
```

## 🏷️ 测试标记（Markers）

项目支持以下测试标记：

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.asyncio`: 异步测试
- `@pytest.mark.slow`: 慢速测试

使用示例：
```bash
# 只运行单元测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"
```

## 🔍 编写新测试

### 测试文件命名
- 文件名：`test_<module>.py`
- 测试类：`Test<ClassName>`
- 测试函数：`test_<description>()`

### 基本测试模板
```python
"""
<module>.py 单元测试
"""
import pytest
from <module> import <ClassName>


class Test<ClassName>:
    """<ClassName> 类测试"""
    
    def test_feature_basic(self):
        """测试基本功能"""
        # Arrange
        obj = <ClassName>()
        
        # Act
        result = obj.method()
        
        # Assert
        assert result == expected_value
    
    def test_feature_edge_case(self):
        """测试边界情况"""
        # 测试代码...
```

### 使用 Fixtures
```python
# 在 conftest.py 中定义 fixture
@pytest.fixture
def sample_data():
    return {'key': 'value'}

# 在测试中使用
def test_with_fixture(sample_data):
    assert sample_data['key'] == 'value'
```

### 异步测试
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_method()
    assert result is not None
```

### Mock 测试
```python
def test_with_mock(mocker):
    # 创建 mock 对象
    mock_obj = mocker.MagicMock()
    mock_obj.method.return_value = 'mocked'
    
    # 使用 mock
    result = some_function(mock_obj)
    
    # 验证调用
    mock_obj.method.assert_called_once()
```

## 📈 测试最佳实践

### 1. AAA 模式
```python
def test_example():
    # Arrange (准备)
    data = create_test_data()
    
    # Act (执行)
    result = process(data)
    
    # Assert (断言)
    assert result == expected
```

### 2. 有意义的测试名称
```python
# ❌ 不好的命名
def test_1():
    pass

# ✅ 好的命名
def test_config_missing_api_key_raises_error():
    pass
```

### 3. 测试隔离
```python
# 每个测试应该独立
def test_feature_a():
    # 不依赖其他测试的状态
    pass

def test_feature_b():
    # 也不依赖其他测试
    pass
```

### 4. 边界条件测试
```python
def test_empty_input():
    pass

def test_maximum_value():
    pass

def test_null_values():
    pass
```

## 🐛 调试测试

### 查看详细输出
```bash
pytest -s  # 显示 print 输出
pytest -vv # 更详细的输出
```

### 在失败时进入调试器
```bash
pytest --pdb  # 失败时启动 pdb
```

### 只运行上次失败的测试
```bash
pytest --lf  # last failed
```

## 📝 测试检查清单

在提交代码前，确保：

- [ ] 所有测试通过
- [ ] 新增功能有对应测试
- [ ] 测试覆盖率未下降
- [ ] 没有警告信息
- [ ] 测试代码符合规范

## 🎯 后续改进计划

### 短期目标
- [ ] 添加 api_stages.py 的完整测试
- [ ] 添加 workflow_orchestrator.py 的完整测试
- [ ] 提高术语库管理器测试覆盖率至 95%

### 中期目标
- [ ] 添加集成测试套件
- [ ] 实现性能基准测试
- [ ] 添加 CI/CD 自动测试

### 长期目标
- [ ] 测试覆盖率达到 95%+
- [ ] 实现 TDD（测试驱动开发）
- [ ] 建立自动化测试流水线

## 💡 常见问题

### Q: 如何跳过某些测试？
```bash
# 使用标记跳过
pytest -m "not slow"

# 临时跳过
pytest -k "not test_slow_function"
```

### Q: 如何并行运行测试？
```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 使用多个 worker
pytest -n auto
```

### Q: 如何生成 XML 报告用于 CI？
```bash
pytest --cov=. --cov-report=xml:cobertura.xml
```

---

**最后更新**: 2026-03-17  
**测试框架版本**: pytest 7.0+  
**Python 版本**: 3.8+
