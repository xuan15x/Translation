# 架构设计文档

本目录包含系统的架构设计和技术文档。

## 📄 文档列表

### ⭐ 核心架构文档

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 完整系统架构详解 ⭐⭐⭐
   - **完整系统架构图**（ASCII 可视化图表，包含所有 20+ 模块）
   - **核心数据流向图**（从用户操作到结果输出的完整流程）
   - **模块依赖关系图**（清晰的模块间调用关系）
   - 五层模块化架构详解
   - 详细职责说明和接口定义
   - 解耦优势分析

2. **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - 重构总结
   - 重构过程和决策
   - 架构演进历史
   - 经验教训

## 🏗️ 五层架构概览（简化版）

```
┌─────────────────────────────────────────┐
│     Presentation Layer (表示层)         │
│   - gui_app.py (主界面)                 │
│   - translation.py (程序入口)           │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌────────────────▼────────────────────────┐
│   Business Logic Layer (业务逻辑层)     │
│   - workflow_orchestrator.py (编排器)   │
│   - terminology_manager.py (术语库)     │
│   - api_stages.py (API 处理)            │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌────────────────▼────────────────────────┐
│      Service Layer (服务层)             │
│   - api_provider.py (API 调用)          │
│   - translation_history.py (历史)       │
│   - auto_backup.py (备份) ⭐ NEW        │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌────────────────▼────────────────────────┐
│    Data Access Layer (数据访问层)       │
│   - config_persistence.py (配置)        │
│   - terminology_update.py (更新)        │
│   - fuzzy_matcher.py (匹配)             │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌────────────────▼────────────────────────┐
│   Infrastructure Layer (基础设施层)     │
│   - models.py (数据模型)                │
│   - exceptions.py (异常处理) ⭐ NEW     │
│   - log_config.py (日志)                │
│   - concurrency_controller.py (并发)    │
│   - cache.py (缓存)                     │
│   - performance_monitor.py (监控) ⭐ NEW │
└─────────────────────────────────────────┘
```

**注意**: 这是简化版的架构图。完整详细的系统架构图请查看 [ARCHITECTURE.md](ARCHITECTURE.md)，包含：
- 所有 20+ 模块的详细位置
- 完整的数据流向图
- 模块依赖关系图
- 各层的详细职责说明

## 🎯 架构原则

- **单一职责**: 每层只负责一个层面的功能
- **依赖倒置**: 上层依赖下层的抽象接口
- **面向接口**: 层与层之间通过接口通信
- **松耦合**: 各层可以独立测试和替换

## 📖 推荐阅读顺序

1. 初次了解 → [ARCHITECTURE.md](ARCHITECTURE.md)
2. 深入理解 → [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
