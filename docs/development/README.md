# 开发文档

本目录包含开发者指南、测试规范和技术文档。

> **💡 提示**：开发者请优先阅读 **[完整使用手册](../../COMPLETE_MANUAL.md)** ⭐⭐⭐ 了解系统基本使用。

## 📑 目录

- [📄 核心文档](#-核心文档)
- [📄 专题文档](#-专题文档)
- [🎯 推荐阅读顺序](#-推荐阅读顺序)
- [🛠️ 测试工具](#-️-测试工具)
- [📖 快速链接](#-快速链接)

---

## 📄 核心文档

### 🧪 测试指南
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** ⭐⭐⭐ 完整的测试开发指南
  - 测试框架介绍
  - 编写测试用例
  - 测试覆盖要求
  - Mock 和 Fixture 使用

### ⚠️ 错误处理
- **[ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md)** ⭐⭐⭐ 统一错误处理使用指南
  - 完整异常体系架构（20+ 自定义异常类）
  - ErrorHandler 统一处理器
  - 错误分类和错误代码规范
  - 最佳实践和迁移指南

---

## 📄 专题文档

### ⚡ 性能优化
> ⚠️ **注意**: 以下文档已归档，内容已整合到其他文档中
- ~~[PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md)~~ - 内容已整合到 [BEST_PRACTICES.md](../guides/BEST_PRACTICES.md)
- ~~[REDIS_CACHE_OPTIMIZATION.md](REDIS_CACHE_OPTIMIZATION.md)~~ - 内容已整合到 [BEST_PRACTICES.md](../guides/BEST_PRACTICES.md)

### 🎨 UI/UX 优化
- **[UI_UX_OPTIMIZATIONS.md](UI_UX_OPTIMIZATIONS.md)** - UI/UX 优化实施总结
  - GUI 框架选择分析
  - 撤销/重做功能完整实现
  - 智能进度显示（剩余时间估算）
  - 实时日志预览和状态监控

### ⚡ 后台异步处理
- **[ASYNC_BACKGROUND_PROCESSING.md](ASYNC_BACKGROUND_PROCESSING.md)** - 后台异步处理实施总结
  - GUI 异步执行框架设计
  - 后台线程池和任务调度
  - 进度实时跟踪机制
  - 多层异常处理和资源管理

### 🔍 冲突检测和解决
> ⚠️ **注意**: 以下文档已归档
- ~~[CONFLICT_DETECTION_RESOLUTION.md](CONFLICT_DETECTION_RESOLUTION.md)~~ - 内容已整合到术语库管理文档

### 🚀 高级翻译功能
> ⚠️ **注意**: 以下文档已归档
- ~~[ADVANCED_TRANSLATION_FEATURES.md](ADVANCED_TRANSLATION_FEATURES.md)~~ - 功能已整合到核心代码

### 📝 其他文档
- **[FORBIDDEN_RULES_CONFIG_GUIDE.md](../guides/FORBIDDEN_RULES_CONFIG_GUIDE.md)** - 禁止规则配置功能
- **[SOURCE_LANGUAGE_SELECTION_FEATURE.md](SOURCE_LANGUAGE_SELECTION_FEATURE.md)** - 源语言选择功能

> ℹ️ **临时文档** (仅供内部参考):
- [DOCS_SUMMARY_FINAL.md](DOCS_SUMMARY_FINAL.md) - 文档总结（临时）
- [DOCUMENTATION_UPDATE_CHECKLIST.md](DOCUMENTATION_UPDATE_CHECKLIST.md) - 文档更新清单（临时）

---

## 🎯 推荐阅读顺序

#### 测试新手
1. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - 完整测试指南
2. 查看具体测试文件学习实现

#### 错误处理学习
1. **[ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md)** - 详细使用手册
2. [../../infrastructure/exceptions.py](../../infrastructure/exceptions.py) - 源码阅读

#### 性能优化学习
1. **[BEST_PRACTICES.md](../guides/BEST_PRACTICES.md)** - 最佳实践（包含性能优化内容）
2. [../../PROJECT_STRUCTURE.md](../../PROJECT_STRUCTURE.md) - 项目结构

#### 资深开发者
1. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - 完整指南
2. [../../PROJECT_STRUCTURE.md](../../PROJECT_STRUCTURE.md) - 项目结构
3. [../architecture/ARCHITECTURE.md](../architecture/ARCHITECTURE.md) - 架构设计

---

## 🛠️ 测试工具

### 核心工具
- **pytest**: 测试框架
- **pytest-cov**: 覆盖率统计
- **pytest-asyncio**: 异步测试支持
- **pytest-mock**: Mock 功能

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_models.py

# 查看覆盖率
pytest --cov=translation --cov-report=html

# 生成 HTML 报告
pytest --html=test_report.html
```

---

## 📖 快速链接

- **测试目录**: [../../tests/](../../tests/)
- **运行测试脚本**: [../../run_tests.bat](../../run_tests.bat)
- **项目结构**: [../../PROJECT_STRUCTURE.md](../../PROJECT_STRUCTURE.md)
- **架构设计**: [../architecture/ARCHITECTURE_DESIGN.md](../architecture/ARCHITECTURE_DESIGN.md)
- **返回文档首页**: [../README.md](../README.md)
- **返回完整手册**: [../../COMPLETE_MANUAL.md](../../COMPLETE_MANUAL.md)
