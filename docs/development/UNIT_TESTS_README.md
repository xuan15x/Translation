# 🧪 单元测试快速开始

## 1. 安装测试依赖

```bash
pip install -r requirements-test.txt
```

这将安装以下测试工具：
- **pytest** (7.0+): 测试框架
- **pytest-cov** (4.0+): 代码覆盖率
- **pytest-asyncio** (0.21+): 异步测试支持
- **pytest-mock** (3.10+): Mock 功能
- **pytest-html** (3.2+): HTML 测试报告
- **coverage** (7.0+): 覆盖率统计

## 2. 运行测试

### 方式一：使用运行脚本（推荐）

```bash
python scripts/run_tests.py
```

这将：
- ✅ 运行所有测试
- ✅ 生成详细输出
- ✅ 创建 HTML 报告
- ✅ 计算代码覆盖率

### 方式二：直接使用 pytest

```bash
# 基本测试
pytest

# 详细输出
pytest -v

# 带覆盖率报告
pytest --cov=. --cov-report=html

# 生成 HTML 测试报告
pytest --html=test_report.html
```

## 3. 查看测试报告

测试运行后会生成两个报告：

### HTML 测试报告
```bash
# Windows
start test_report.html

# Linux/Mac
open test_report.html
```

### 覆盖率报告
```bash
# Windows
start htmlcov\index.html

# Linux/Mac
open htmlcov/index.html
```

## 4. 运行特定测试

```bash
# 单个测试文件
pytest tests/test_models.py

# 单个测试类
pytest tests/test_models.py::TestConfig

# 单个测试函数
pytest tests/test_models.py::TestConfig::test_config_default_initialization

# 使用标记筛选
pytest -m unit        # 单元测试
pytest -m asyncio     # 异步测试
pytest -m "not slow"  # 跳过慢速测试
```

## 5. 预期输出

成功的测试运行应该显示：

```
============================= test session starts =============================
platform win32 -- Python 3.x.x, pytest-7.x.x, pluggy-x.x.x
rootdir: C:\Users\13457\PycharmProjects\translation
plugins: cov-x.x.x, asyncio-x.x.x, mock-x.x.x, html-x.x.x
asyncio: mode=strict
collected 75 items

tests\test_config.py ..........                                           [ 13%]
tests\test_concurrency_controller.py ...........                         [ 28%]
tests\test_fuzzy_matcher.py ..........                                   [ 41%]
tests\test_models.py ...............                                     [ 61%]
tests\test_prompt_builder.py ........                                    [ 72%]
tests\test_terminology_manager.py ............                           [ 88%]
tests\test_workflow_orchestrator.py .........                            [100%]

---------- coverage: platform win32, version 7.x.x -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
config.py                             5      0   100%
concurrency_controller.py            25      2    92%
fuzzy_matcher.py                     12      1    92%
models.py                            45      0   100%
prompt_builder.py                    10      0   100%
terminology_manager.py               85      8    91%
workflow_orchestrator.py             65      5    92%
---------------------------------------------------------------
TOTAL                               247     16    94%


======================== 75 passed in 2.50s =============================
```

## 6. 测试覆盖要求

项目要求最低覆盖率：**85%**

查看哪些行未覆盖：
```bash
pytest --cov=. --cov-report=term-missing
```

## 7. 常见问题

### Q: 提示找不到 pytest？
A: 确保已安装测试依赖：
```bash
pip install -r requirements-test.txt
```

### Q: 异步测试失败？
A: 确保测试函数使用了 `@pytest.mark.asyncio` 标记

### Q: 如何跳过某些测试？
```bash
# 使用标记
pytest -m "not slow"

# 使用关键字
pytest -k "not test_slow_function"
```

### Q: 如何加速测试运行？
```bash
# 并行测试（需要安装 pytest-xdist）
pip install pytest-xdist
pytest -n auto
```

## 8. 编写新测试

在 `tests/` 目录下创建 `test_<module>.py` 文件：

```python
"""
<module>.py 单元测试
"""
import pytest
from <module> import <ClassName>


class Test<ClassName>:
    """<ClassName> 类测试"""
    
    def test_feature(self):
        """测试功能"""
        # Arrange
        obj = <ClassName>()
        
        # Act
        result = obj.method()
        
        # Assert
        assert result == expected
```

## 9. 测试检查清单

提交代码前确认：
- [ ] 所有测试通过
- [ ] 新增功能有测试
- [ ] 覆盖率未下降
- [ ] 没有警告信息

## 10. 更多信息

- 📖 完整指南：[TESTING_GUIDE.md](TESTING_GUIDE.md)
- 📊 测试总结：[TEST_SUMMARY.md](TEST_SUMMARY.md)
- 🏗️ 架构文档：[ARCHITECTURE.md](ARCHITECTURE.md)

---

**祝测试顺利！** ✨
