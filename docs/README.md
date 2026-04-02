# AI 智能翻译系统 - 完整文档中心 v3.0

欢迎使用 AI 智能翻译系统的文档系统。本文档中心提供完整的使用指南、API 参考和故障排查手册。

> **💡 提示**：新用户请优先阅读 **[完整使用手册](../COMPLETE_MANUAL.md)** ⭐⭐⭐，一站式解决方案包含所有核心内容。

## 📑 目录

- [🌟 重点推荐文档](#-重点推荐文档)
- [🎯 按场景查找文档](#-按场景查找文档)
- [📚 完整文档结构](#-完整文档结构)
- [📖 详细文档列表](#-详细文档列表)
- [🔄 文档更新记录](#-文档更新记录)
- [📞 获取帮助](#-获取帮助)

---

## 🌟 重点推荐文档

### 👉 新用户必读（按顺序阅读）
1. [**完整使用手册**](../COMPLETE_MANUAL.md) ⭐⭐⭐ **一站式解决方案，包含所有核心内容**
2. [**配置填入手册**](guides/CONFIG_SETUP_HANDBOOK.md) ⭐⭐⭐ 最详细配置教程
3. [**最佳实践指南**](guides/BEST_PRACTICES.md) ⭐ 全面详细的使用教程
4. [**故障排查手册**](guides/TROUBLESHOOTING.md) ⭐ 常见问题快速解决

### 👉 开发者参考
- [**架构设计**](architecture/ARCHITECTURE.md) - 六层分层架构详解
- [**测试指南**](development/TESTING_GUIDE.md) - 编写和运行测试
- [**错误处理指南**](development/ERROR_HANDLING_GUIDE.md) - 统一异常体系
- [**项目结构**](../PROJECT_STRUCTURE.md) - 代码组织说明

---

## 🎯 按场景查找文档

### 我是新用户，想快速上手

**推荐阅读顺序：**
1. **[完整使用手册](../COMPLETE_MANUAL.md)** ⭐⭐⭐ - 一站式解决方案（30 分钟）
2. [配置填入手册](guides/CONFIG_SETUP_HANDBOOK.md) - 手把手教你配置
3. [最佳实践](guides/BEST_PRACTICES.md) - 掌握使用技巧

### 我遇到了问题，需要解决

**推荐阅读顺序：**
1. **[完整使用手册](../COMPLETE_MANUAL.md)** 第 5 章 - 故障排查（优先）
2. [故障排查手册](guides/TROUBLESHOOTING.md) - 详细排查步骤
3. [错误处理指南](development/ERROR_HANDLING_GUIDE.md) - 深入调试

### 我想查阅 API 用法

**推荐阅读顺序：**
1. [完整 API 参考](api/MODEL_CONFIG_API.md) - 所有类和方法详细说明
2. [模型配置指南](guides/MODEL_CONFIG_GUIDE.md) - 配置参数详解
3. [配置持久化指南](api/CONFIG_PERSISTENCE_GUIDE.md) - 配置文件使用

### 我想优化性能

**推荐阅读顺序：**
1. **[完整使用手册](../COMPLETE_MANUAL.md)** 第 3 章 - 配置指南
2. [最佳实践](guides/BEST_PRACTICES.md) - 性能调优方法
3. [性能优化](development/PERFORMANCE_OPTIMIZATIONS.md) - 高级技巧

### 我是开发者，想贡献代码

**推荐阅读顺序：**
1. **[完整使用手册](../COMPLETE_MANUAL.md)** - 了解基本使用
2. [架构设计](architecture/ARCHITECTURE_DESIGN.md) - 理解六层架构
3. [测试指南](development/TESTING_GUIDE.md) - 学习测试规范
4. [项目结构](../PROJECT_STRUCTURE.md) - 熟悉代码组织

---

## 📚 完整文档结构

```
docs/
├── README.md                    # 本文档（总导航）
├── INDEX.md                     # 文档导航索引
├── HOW_TO_READ_DOCS.md          # 如何阅读文档
│
├── api/                         # API 和配置文档
│   ├── README.md
│   ├── MODEL_CONFIG_API.md      # 完整 API 参考 ⭐
│   ├── CONFIG_PERSISTENCE_GUIDE.md
│   └── DEPENDENCIES.md
│
├── guides/                      # 使用指南（面向用户）
│   ├── README.md
│   ├── BEST_PRACTICES.md        # 最佳实践指南 ⭐
│   ├── TROUBLESHOOTING.md       # 故障排查手册 ⭐
│   ├── CONFIG_SETUP_HANDBOOK.md # 配置填入手册 ⭐
│   ├── MODEL_CONFIG_GUIDE.md    # 模型配置指南
│   ├── PROHIBITION_CONFIG_GUIDE.md  # 禁止事项配置指南
│   ├── SUPPORTED_LANGUAGES.md   # 支持的语言列表
│   ├── GIT_SYNC_GUIDE.md        # Git 同步指南
│   └── 历史记录功能使用指南.md   # 历史记录功能
│
├── architecture/                # 架构设计文档
│   ├── README.md
│   ├── ARCHITECTURE.md          # 架构概览 v3.0
│   └── ARCHITECTURE_DESIGN.md   # 六层架构详解 ⭐
│
├── development/                 # 开发指南（面向贡献者）
│   ├── README.md
│   ├── TESTING_GUIDE.md         # 测试指南 ⭐
│   ├── ERROR_HANDLING_GUIDE.md  # 错误处理指南 ⭐
│   ├── PERFORMANCE_OPTIMIZATIONS.md
│   ├── ASYNC_BACKGROUND_PROCESSING.md
│   └── UI_UX_OPTIMIZATIONS.md
│
├── technical/                   # 技术实现文档
│   └── MODEL_CONFIG_IMPLEMENTATION.md
│
└── archive/                     # 归档文档（历史参考）
    ├── old_configs/             # 旧配置文档
    ├── old_quickstarts/         # 旧快速开始指南
    └── development_summaries/   # 开发总结
```

---

## 📖 详细文档列表

### 🔧 API 和配置文档 (`api/`)

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [API 参考](api/MODEL_CONFIG_API.md) | 完整的 API 文档，包含所有类和方法 | 开发者 |
| [配置持久化指南](api/CONFIG_PERSISTENCE_GUIDE.md) | JSON/YAML 配置文件使用 | 运维人员 |
| [依赖项说明](api/DEPENDENCIES.md) | 项目依赖详情 | 开发者 |

---

### 📖 使用指南 (`guides/`)

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [最佳实践指南](guides/BEST_PRACTICES.md) | 详细的使用说明和优化建议 | 所有用户 |
| [故障排查手册](guides/TROUBLESHOOTING.md) | 常见问题解决方案 | 所有用户 |
| [配置填入手册](guides/CONFIG_SETUP_HANDBOOK.md) | 从零开始的配置教程 | 新用户 |
| [模型配置指南](guides/MODEL_CONFIG_GUIDE.md) | 模型配置拆分详解 | 所有用户 |
| [禁止事项配置指南](guides/PROHIBITION_CONFIG_GUIDE.md) | 禁止规则配置详解 | 高级用户 |
| [支持的语言](guides/SUPPORTED_LANGUAGES.md) | 33 种目标语言介绍 | 所有用户 |
| [Git 同步指南](guides/GIT_SYNC_GUIDE.md) | 代码同步和版本管理 | 开发者 |

---

### 🏗️ 架构设计文档 (`architecture/`)

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [架构概览](architecture/ARCHITECTURE.md) | 六层架构简介 v3.0 | 开发者 |
| [架构设计详解](architecture/ARCHITECTURE_DESIGN.md) | 六层分层架构详解 | 架构师 |
| [重构总结](architecture/REFACTORING_SUMMARY.md) | 代码重构经验总结 | 开发者 |

---

### 💻 开发文档 (`development/`)

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [测试指南](development/TESTING_GUIDE.md) | 编写测试的完整指南 | 开发者 |
| [错误处理指南](development/ERROR_HANDLING_GUIDE.md) | 统一异常体系使用手册 | 开发者 |
| [性能优化](development/PERFORMANCE_OPTIMIZATIONS.md) | 性能调优技巧 | 开发者 |
| [异步处理](development/ASYNC_BACKGROUND_PROCESSING.md) | 异步编程指南 | 开发者 |
| [UI/UX 优化](development/UI_UX_OPTIMIZATIONS.md) | 界面优化实践 | 开发者 |

---

### 🔬 技术实现文档 (`technical/`)

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [模型配置实现](technical/MODEL_CONFIG_IMPLEMENTATION.md) | 模型配置拆分技术总结 | 开发者 |

---

## 🔄 文档更新记录

### v3.0.0 (2026-04-01)
- ✨ 双阶段翻译参数 GUI 控制文档
- ✨ 语言扩展至 33 种目标语言 + 10 种源语言
- ✨ 翻译方向可配置化文档
- ✨ 错误处理手册（776 行）
- 🐛 修复文档中的断链和过时引用

### v2.5.0 (2026-03-28)
- 性能监控系统文档
- 日志粒度控制（5 级）
- 撤销/重做功能文档

### v2.0.0 (2026-03-20)
- 六层架构重构文档
- 依赖注入容器实现文档
- 外观模式简化调用文档

---

## 📊 文档统计

- **核心文档**: 1 个（完整使用手册）
- **使用指南**: 7 个
- **架构文档**: 3 个
- **开发文档**: 5 个
- **技术文档**: 1 个
- **总计**: 17 个精简文档
- **代码示例**: 100+

---

## 📞 获取帮助

如果文档无法解决您的问题：

1. **查看完整手册**: [COMPLETE_MANUAL.md](../COMPLETE_MANUAL.md) ⭐⭐⭐
2. **搜索 Issue**: [GitHub Issues](https://github.com/your-repo/translation/issues)
3. **提问讨论**: [GitHub Discussions](https://github.com/your-repo/translation/discussions)
4. **联系团队**: support@example.com

---

## 📝 参与文档改进

我们欢迎社区贡献文档！如果您发现文档有误或需要补充：

1. **提交 Issue**: 指出问题所在
2. **提交 PR**: 直接修改文档
3. **讨论建议**: 在 Discussions 中提出

---

**文档版本**: 3.0.0
**最后更新**: 2026-04-01
**维护者**: Translation Team
**许可证**: MIT
