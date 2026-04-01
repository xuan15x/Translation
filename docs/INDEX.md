# AI 智能翻译系统 - 文档中心

欢迎使用 AI 智能翻译系统！本文档中心提供完整的文档导航和索引。

## 🎯 快速导航（按角色）

### 👤 我是新用户
→ **[完整使用手册](../COMPLETE_MANUAL.md)** ⭐⭐⭐ **必读！一站式解决方案**

### 🔧 我是开发者
→ **[架构设计](architecture/ARCHITECTURE.md)** | **[测试指南](development/TESTING_GUIDE.md)**

### 🏗️ 我是架构师
→ **[六层架构详解](architecture/ARCHITECTURE_DESIGN.md)** | **[项目结构](../PROJECT_STRUCTURE.md)**

---

## 📚 核心文档（必读）

## 📚 文档分类

### 🚀 入门指南 (适合新用户)

| 文档 | 说明 | 位置 | 重要度 |
|------|------|------|--------|
| [完整使用手册](../COMPLETE_MANUAL.md) | ⭐⭐⭐ **一站式解决方案，包含所有核心内容** | 根目录 | ⭐⭐⭐ |
| [README](../README.md) | 项目总览和快速开始 | 根目录 | ⭐⭐⭐ |
| [更新日志](../CHANGELOG.md) | 版本历史和更新记录 | 根目录 | ⭐⭐ |
| [项目结构](../PROJECT_STRUCTURE.md) | 六层架构详细说明 | 根目录 | ⭐⭐ |

---

## 📖 使用指南（用户）

| 文档 | 说明 | 位置 | 重要度 |
|------|------|------|--------|
| [最佳实践](guides/BEST_PRACTICES.md) | 详细的使用说明和优化建议 | guides/ | ⭐⭐⭐ |
| [故障排查](guides/TROUBLESHOOTING.md) | 常见问题解决方案 | guides/ | ⭐⭐⭐ |
| [配置填入手册](guides/CONFIG_SETUP_HANDBOOK.md) | 最详细配置教程 | guides/ | ⭐⭐ |
| [模型配置指南](guides/MODEL_CONFIG_GUIDE.md) | 模型配置拆分详解 | guides/ | ⭐⭐ |
| [支持的语言](guides/SUPPORTED_LANGUAGES.md) | 33 种目标语言介绍 | guides/ | ⭐ |
| [快速开始](guides/QUICKSTART.md) | 5 分钟快速上手（已归档） | archive/old_quickstarts/ | ⭐ |

---

## 🔧 开发指南（贡献者）

| 文档 | 说明 | 位置 | 重要度 |
|------|------|------|--------|
| [架构设计](architecture/ARCHITECTURE_DESIGN.md) | 六层分层架构详解 | architecture/ | ⭐⭐⭐ |
| [架构概览](architecture/ARCHITECTURE.md) | 架构简介 v3.0 | architecture/ | ⭐⭐ |
| [重构总结](architecture/REFACTORING_SUMMARY.md) | 全面重构过程 | architecture/ | ⭐ |

---

## 🏛️ 架构文档（深入了解）

| 文档 | 说明 | 位置 | 重要度 |
|------|------|------|--------|
| [测试指南](development/TESTING_GUIDE.md) | 单元测试和集成测试 | development/ | ⭐⭐⭐ |
| [错误处理指南](development/ERROR_HANDLING_GUIDE.md) | 统一异常体系使用手册 | development/ | ⭐⭐⭐ |
| [性能优化](development/PERFORMANCE_OPTIMIZATIONS.md) | 性能调优技巧 | development/ | ⭐⭐ |
| [异步处理](development/ASYNC_BACKGROUND_PROCESSING.md) | 异步编程指南 | development/ | ⭐⭐ |
| [UI/UX 优化](development/UI_UX_OPTIMIZATIONS.md) | 界面优化实践 | development/ | ⭐ |

---

## 📦 模块文档（按层级）

| 模块 | 说明 | 位置 |
|------|------|------|
| [配置管理](config/README.md) | 配置文件管理和使用 | config/ |
| [应用层](application/README.md) | 流程编排和外观模式 | application/ |
| [领域层](domain/README.md) | 核心业务逻辑 | domain/ |
| [服务层](service/README.md) | API 提供商和历史管理 | service/ |
| [数据访问层](data_access/README.md) | 配置持久化和模糊匹配 | data_access/ |
| [基础设施层](infrastructure/README.md) | 数据模型、日志、并发控制 | infrastructure/ |
| [表示层](presentation/README.md) | GUI 界面和程序入口 | presentation/ |

---

## 🎯 按场景查找文档

### 场景 1: 我是新用户，想快速上手

推荐阅读顺序:
1. **[完整使用手册](../COMPLETE_MANUAL.md)** ⭐⭐⭐ - 一站式解决方案（30 分钟）
2. [README](../README.md) - 了解项目（5 分钟）
3. [最佳实践](guides/BEST_PRACTICES.md) - 掌握技巧（20 分钟）

### 场景 2: 我遇到了问题

推荐阅读顺序:
1. **[完整使用手册](../COMPLETE_MANUAL.md)** 第 5 章 - 故障排查（优先）
2. [故障排查](guides/TROUBLESHOOTING.md) - 详细排查步骤
3. [错误处理指南](development/ERROR_HANDLING_GUIDE.md) - 深入调试

### 场景 3: 我想贡献代码

推荐阅读顺序:
1. **[完整使用手册](../COMPLETE_MANUAL.md)** - 了解基本使用
2. [架构设计](architecture/ARCHITECTURE_DESIGN.md) - 理解架构
3. [测试指南](development/TESTING_GUIDE.md) - 学习测试规范
4. [项目结构](../PROJECT_STRUCTURE.md) - 熟悉代码组织

### 场景 4: 我想优化性能

推荐阅读顺序:
1. **[完整使用手册](../COMPLETE_MANUAL.md)** 第 3 章 - 配置指南
2. [性能优化](development/PERFORMANCE_OPTIMIZATIONS.md) - 高级技巧
3. [最佳实践](guides/BEST_PRACTICES.md) - 性能调优方法

### 场景 5: 我想扩展功能

推荐阅读顺序:
1. [架构设计](architecture/ARCHITECTURE_DESIGN.md) - 理解扩展点
2. [应用层](application/README.md) - 流程编排
3. [领域层](domain/README.md) - 核心业务逻辑
4. [测试指南](development/TESTING_GUIDE.md) - 测试新功能

---

## 📊 文档统计

- **核心文档**: 3 个（必读）
- **专题文档**: 12 个（按需查阅）
- **参考文档**: 8 个（高级用户）
- **总计**: 23 个精简文档
- **代码示例**: 100+
- **适用人群**: 新手、开发者、架构师

---

## 📝 文档维护

### 文档更新记录

- **2026-04-01**: 创建完整使用手册，整合所有核心文档 ⭐
- **2026-03-31**: 更新架构文档和测试指南
- **2026-03-28**: 添加性能监控和日志控制

### 文档管理规范

- ✅ 单一来源原则：每个主题只有一个权威文档
- ✅ 层次分明：核心 → 专题 → 参考
- ✅ 持续更新：与代码同步维护
- ✅ 用户导向：按使用场景组织内容

---

## 🔍 如何快速查找

### 方法 1: 使用搜索
在 GitHub 仓库页面按 `t` 键，输入关键词搜索文件。

### 方法 2: 浏览目录
- **根目录**: 核心文档（README, COMPLETE_MANUAL.md）
- **docs/guides/**: 使用指南
- **docs/development/**: 开发指南
- **docs/architecture/**: 架构文档

### 方法 3: 查看完整列表
查看所有 [Markdown 文件](https://github.com/your-repo/translation/search?q=extension:md)

---

## 📞 需要帮助？

如果找不到需要的信息：

1. **查看完整手册**: [COMPLETE_MANUAL.md](../COMPLETE_MANUAL.md) ⭐
2. **搜索 Issue**: [GitHub Issues](https://github.com/your-repo/translation/issues)
3. **提问讨论**: [GitHub Discussions](https://github.com/your-repo/translation/discussions)
4. **联系团队**: support@example.com

---

**文档中心版本**: 3.0  
**最后更新**: 2026-04-01  
**维护者**: Documentation Team
