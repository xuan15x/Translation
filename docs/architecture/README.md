# 架构设计文档

本目录包含系统的架构设计和技术文档。

## 📑 目录

- [📄 文档列表](#-文档列表)
  - [⭐ 核心架构文档](#-核心架构文档)
- [🏗️ 六层架构概览（简化版）](#-️-六层架构概览简化版)
- [🎯 架构原则](#-架构原则)
- [📖 推荐阅读顺序](#-推荐阅读顺序)

---

## 📄 文档列表

### ⭐ 核心架构文档

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 完整系统架构详解 ⭐⭐⭐
   - **完整系统架构图**（ASCII 可视化图表，包含所有 20+ 模块）
   - **核心数据流向图**（从用户操作到结果输出的完整流程）
   - **模块依赖关系图**（清晰的模块间调用关系）
   - 六层分层架构详解
   - 详细职责说明和接口定义
   - 解耦优势分析

2. **[ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md)** - 架构设计详解
   - 架构设计原则和决策
   - 架构演进历史
   - 设计模式应用

## 🏗️ 六层架构概览（简化版）

```
┌─────────────────────────────────────────┐
│     Presentation Layer (表示层)         │
│   - gui_app.py (主界面)                 │
│   - translation.py (程序入口)           │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌────────────────▼────────────────────────┐
│      Application Layer (应用层)         │
│   - translation_facade.py (外观模式)    │
│   - workflow_coordinator.py (协调器)    │
│   - batch_processor.py (批量处理)       │
│   - result_builder.py (结果构建)        │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌────────────────▼────────────────────────┐
│        Domain Layer (领域层)            │
│   - models.py (领域模型)                │
│   - services.py (服务接口)              │
│   - terminology_service_impl.py (术语)  │
│   - translation_service_impl.py (翻译)  │
│   - cache_decorators.py (缓存装饰器)    │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌────────────────▼────────────────────────┐
│       Service Layer (服务层)            │
│   - api_provider.py (API 调用)          │
│   - api_stages.py (API 处理阶段)        │
│   - translation_history.py (历史)       │
│   - auto_backup.py (备份) ⭐ NEW        │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌────────────────▼────────────────────────┐
│    Data Access Layer (数据访问层)       │
│   - repositories.py (仓储实现)          │
│   - config_persistence.py (配置)        │
│   - terminology_update.py (更新)        │
│   - fuzzy_matcher.py (匹配)             │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌────────────────▼────────────────────────┐
│   Infrastructure Layer (基础设施层)     │
│   - di_container.py (依赖注入) ⭐ NEW   │
│   - models.py (数据模型)                │
│   - exceptions.py (异常处理) ⭐ NEW     │
│   - log_config.py (日志)                │
│   - concurrency_controller.py (并发)    │
│   - cache.py (缓存)                     │
│   - performance_monitor.py (监控) ⭐ NEW │
└─────────────────────────────────────────┘
```

**注意**: 这是简化版的六层架构。完整详细的系统架构图请查看 [ARCHITECTURE.md](ARCHITECTURE.md)，包含：
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
2. 深入理解 → [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md)
