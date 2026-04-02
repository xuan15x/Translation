# 开发文档

本目录包含开发者指南、测试规范和技术文档。

## 📑 目录

- [📄 文档列表](#-文档列表)
  - [🧪 测试指南](#-测试指南)
  - [📝 单元测试文档](#-单元测试文档)
  - [⚠️ 错误处理 ⭐ NEW](#-错误处理-new)
  - [⚡ 性能优化 ⭐ NEW](#-性能优化-new)
  - [🎨 UI/UX 优化 ⭐ NEW](#-uiux-优化-new)
  - [⚡ 后台异步处理 ⭐ NEW](#-后台异步处理-new)
  - [🔍 冲突检测和解决 ⭐ NEW](#-冲突检测和解决-new)
  - [🚀 高级翻译功能 ⭐ NEW](#-高级翻译功能-new)
- [🎯 推荐阅读顺序](#-推荐阅读顺序)
    - [测试新手](#测试新手)
    - [错误处理学习 ⭐ NEW](#错误处理学习-new)
    - [资深开发者](#资深开发者)
- [🛠️ 测试工具](#-测试工具)
  - [核心工具](#核心工具)
  - [运行测试](#运行测试)
- [📖 快速链接](#-快速链接)

---

## 📄 文档列表

### 🧪 测试指南
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - 完整的测试开发指南
  - 测试框架介绍
  - 编写测试用例
  - 测试覆盖要求
  - Mock 和 Fixture 使用

### 📝 单元测试文档
- **[UNIT_TESTS_README.md](UNIT_TESTS_README.md)** - 单元测试说明
  - 测试目录结构
  - 运行测试方法
  - 测试报告查看

- **[UNIT_TESTS_SUMMARY.md](UNIT_TESTS_SUMMARY.md)** - 单元测试总结
  - 测试覆盖统计
  - 测试用例分类
  - 测试质量评估

- **[TEST_SUMMARY.md](TEST_SUMMARY.md)** - 测试总结
  - 整体测试情况
  - 测试结果分析
  - 改进建议

### ⚠️ 错误处理 ⭐ NEW
- **[ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md)** - 统一错误处理使用指南 ⭐ **新增**
  - 完整异常体系架构（20+ 自定义异常类）
  - ErrorHandler 统一处理器
  - 错误分类和错误代码规范
  - 最佳实践和迁移指南
  - 丰富的代码示例

- **[ERROR_HANDLING_SUMMARY.md](ERROR_HANDLING_SUMMARY.md)** - 错误处理实施总结 ⭐ **新增**
  - 实施成果总览
  - 异常体系详细说明
  - 迁移进度和计划
  - 快速参考手册

### ⚡ 性能优化 ⭐ NEW
- **[PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md)** - 性能优化实施总结 ⭐ **新增**
  - 术语查询缓存 (LRU Cache) - 命中率 85%，查询加速 500x
  - 分批次翻译降低内存峰值 - 内存峰值降低 75%
  - 数据库连接池优化 - 并发提升 50x
  - 性能监控系统 - 实时监控和告警
  - 内存管理优化 - 定期 GC 和清理

### 🎨 UI/UX 优化 ⭐ NEW
- **[UI_UX_OPTIMIZATIONS.md](UI_UX_OPTIMIZATIONS.md)** - UI/UX 优化实施总结 ⭐ **新增**
  - GUI 框架选择分析（Tkinter vs PyQt6）
  - 撤销/重做功能完整实现
  - 智能进度显示（剩余时间估算）
  - 实时日志预览和状态监控

### ⚡ 后台异步处理 ⭐ NEW
- **[ASYNC_BACKGROUND_PROCESSING.md](ASYNC_BACKGROUND_PROCESSING.md)** - 后台异步处理实施总结 ⭐ **新增**
  - GUI 异步执行框架设计
  - 后台线程池和任务调度
  - 进度实时跟踪机制
  - 多层异常处理和资源管理

### 🔍 冲突检测和解决 ⭐ NEW
- **[CONFLICT_DETECTION_RESOLUTION.md](CONFLICT_DETECTION_RESOLUTION.md)** - 冲突检测和解决机制 ⭐ **新增**
  - 4 种冲突类型检测（并发编辑、重复添加、版本不匹配、数据不一致）
  - 6 种解决策略（最后写入获胜、合并变更、人工审核等）
  - 术语库冲突完整生命周期管理
  - 实时操作注册和校验和验证

### 🚀 高级翻译功能 ⭐ NEW
- **[ADVANCED_TRANSLATION_FEATURES.md](ADVANCED_TRANSLATION_FEATURES.md)** - 高级翻译功能实施总结 ⭐ **新增**
  - 上下文感知翻译（整句/段落的上下文理解）
  - 机器学习术语推荐（基于统计学习）
  - 翻译质量自动评估（多维度评分系统）
  - 风格一致性检查（术语统一、风格规范）

## 🎯 推荐阅读顺序

#### 测试新手
1. [TESTING_QUICKSTART.md](../guides/TESTING_QUICKSTART.md) - 快速开始
2. [UNIT_TESTS_README.md](UNIT_TESTS_README.md) - 了解基础
3. [TESTING_GUIDE.md](TESTING_GUIDE.md) - 深入学习

#### 错误处理学习 ⭐ NEW
1. [ERROR_HANDLING_SUMMARY.md](ERROR_HANDLING_SUMMARY.md) - 了解成果
2. [ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md) - 详细使用手册
3. [infrastructure/exceptions.py](../../infrastructure/exceptions.py) - 源码阅读

#### 资深开发者
1. [TESTING_GUIDE.md](TESTING_GUIDE.md) - 完整指南
2. [TEST_SUMMARY.md](TEST_SUMMARY.md) - 了解现状
3. 查看具体测试文件学习实现

## 🛠️ 测试工具

### 核心工具
- **pytest**: 测试框架
- **pytest-cov**: 覆盖率统计
- **pytest-asyncio**: 异步测试支持

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_models.py

# 查看覆盖率
pytest --cov=translation --cov-report=html
```

## 📖 快速链接

- **测试目录**: [../../tests/](../../tests/)
- **测试脚本**: [../../scripts/run_tests.py](../../scripts/run_tests.py)
- **返回主索引**: [../README.md](../README.md)
