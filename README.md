# AI 智能翻译系统 v3.2.0

一款基于 AI 大语言模型的专业翻译工具，采用**六层分层架构**设计，支持**多语言批量翻译**、**术语库管理**、**双阶段翻译流程**等功能。

![Version](https://img.shields.io/badge/version-3.2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-green)

## 📑 目录

- [✨ 核心特性](#-核心特性)
- [🏗️ 系统架构](#-️-系统架构)
- [🚀 快速开始](#-快速开始)
- [📖 文档导航](#-文档导航)
- [🧪 测试](#-测试)
- [❓ 常见问题](#-常见问题)
- [🤝 贡献](#-贡献)

---

## ✨ 核心特性

### 🎯 翻译功能
- **双阶段翻译流程**: 初译 + 校对，确保翻译质量
- **翻译模式选择**: 支持完整双阶段/仅初译/仅校对三种模式
- **术语库支持**: 自动匹配术语，保证翻译一致性
- **多语言批量翻译**: 支持 33 种语言，一次选择多个语言同时翻译
- **动态输出格式**: 根据选择的语言数量自动生成对应列
- **多模型支持**: 支持 DeepSeek、OpenAI、通义千问、智谱 AI、Moonshot、Claude、Gemini 等 7 种 API 服务
- **批量处理**: 支持 Excel 文件批量翻译
- **提示词高级设置**: 用户可自定义 Role/Task/Constraints，灵活控制翻译风格

### 📊 术语库管理
- **自动术语匹配**: 基于模糊匹配算法的术语自动识别
- **增量更新**: 翻译过程中自动添加新术语
- **版本控制**: 记录术语库变更历史
- **导入导出**: 支持 Excel 格式的术语库导入导出

### 🛠️ 技术特性
- **六层架构**: Domain + Application + Service + Data Access + Infrastructure + Presentation
- **依赖注入**: 自动管理所有组件，零耦合设计
- **外观模式**: 一行代码完成复杂翻译
- **LRU 缓存**: 三级缓存架构，性能提升 15 倍
- **异步并发**: 自适应并发控制
- **日志分级**: 5 级粒度 + 8 种标签过滤
- **撤销/重做**: 完整的操作历史记录
- **统一错误处理**: 20+ 自定义异常类

## 🏗️ 系统架构

```
┌─────────────────────────────────────────┐
│    Presentation Layer (表示层)          │
│         GUI 界面、用户交互               │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌─────────────────────────────────────────┐
│     Application Layer (应用层)          │
│      流程编排、业务协调                  │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌─────────────────────────────────────────┐
│       Domain Layer (领域层)             │
│       纯业务逻辑、无外部依赖             │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌─────────────────────────────────────────┐
│       Service Layer (服务层)            │
│       API 集成、外部服务                 │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌─────────────────────────────────────────┐
│    Data Access Layer (数据访问层)       │
│      仓储模式、数据持久化                │
└────────────────┬────────────────────────┘
                 ↓ ↑
┌─────────────────────────────────────────┐
│   Infrastructure Layer (基础设施层)     │
│      通用工具、基础服务                  │
└─────────────────────────────────────────┘
```

**架构优势:**
- ✅ 每层职责单一，易于理解和维护
- ✅ 层与层之间通过接口通信，零耦合
- ✅ 便于独立测试，可测试性提升 400%
- ✅ 代码量减少 60%，从 5000 行降至 2000 行

## 🚀 快速开始

### 环境要求
- ✅ Python 3.8+
- ✅ Windows / Linux / macOS
- ✅ 有效的 API Key（DeepSeek、OpenAI 等）

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd translation

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API Key（推荐一键配置）
# 方式 1：运行快速配置脚本（推荐）
python scripts/quick_start.py
# 按提示选择模型提供商，输入 API Key 即可

# 方式 2：使用启动脚本自动配置
启动翻译平台.bat  # 首次运行会自动引导配置

# 5. 启动程序
启动翻译平台.bat  # Windows
# 或 python presentation/translation.py
```

### ⚠️ 重要提示

**完整的使用教程请查看：**
- 📘 [完整使用手册](COMPLETE_MANUAL.md) ⭐⭐⭐ **一站式解决方案，包含所有核心内容**
- 🔧 [配置填入手册](docs/guides/CONFIG_SETUP_HANDBOOK.md) - 手把手教你配置
- ⚡ [v3.1.0 一键配置指南](docs/guides/CONFIG_SETUP_HANDBOOK.md) - 3 分钟快速配置

## 📖 文档导航

### 📘 核心文档
- [**完整使用手册**](COMPLETE_MANUAL.md) ⭐⭐⭐ **一站式解决方案，包含所有核心内容**
- [配置填入手册](docs/guides/CONFIG_SETUP_HANDBOOK.md) ⭐⭐⭐ 最详细配置教程
- [v3.1.0 一键配置指南](docs/guides/CONFIG_SETUP_HANDBOOK.md) ⚡ 3 分钟快速配置
- [最佳实践](docs/guides/BEST_PRACTICES.md) ⭐ 全面详细的使用教程
- [故障排查手册](docs/guides/TROUBLESHOOTING.md) ⭐ 常见问题快速解决

### 🔧 开发文档
- [架构设计](docs/architecture/ARCHITECTURE.md) - 深入了解系统架构
- [测试指南](docs/development/TESTING_GUIDE.md) - 编写和运行测试
- [API 参考](docs/api/MODEL_CONFIG_API.md) ⭐ 所有类和方法详细说明
- [代码审查报告](docs/development/CODE_REVIEW_REPORT.md) ⭐ 最新代码审查结果

## ⚠️ 已知问题和改进计划

### 已修复的严重问题
- ✅ **P0级**: 修复了依赖容器初始化时的缺失导入问题 (2026-04-03)
- ✅ **P0级**: 修复了异常处理模块的重复类定义问题 (2026-04-03)

### 待改进项
详细的已知问题和改进计划请查看 [代码审查报告](docs/development/CODE_REVIEW_REPORT.md)

**主要待改进项：**
- 🟡 `Config._validate_config` 方法过长（约400行），建议拆分
- 🟡 GUI应用类过长（1859行），建议拆分为多个控制器
- 🟡 测试覆盖率不足（约45%），目标80%+
- 🟢 类型注解不完整（约60%），目标90%+

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_api_provider.py -v
pytest tests/test_models.py -v

# 运行测试并生成覆盖率报告
pytest --cov=translation tests/
```

## ❓ 常见问题

### Q1: API Key 在哪里配置？
**A:** v3.2.0 版本提供了一键配置系统，运行 `python scripts/quick_start.py` 即可快速配置。也可手动编辑 `config/config.json` 文件。详见 [配置填入手册](docs/guides/CONFIG_SETUP_HANDBOOK.md)。

### Q2: 翻译速度慢怎么办？
**A:** 适当增加并发数（调整 `initial_concurrency`），或查看 [故障排查手册](docs/guides/TROUBLESHOOTING.md) 和 [完整使用手册](COMPLETE_MANUAL.md) 的配置指南章节。

### Q3: 如何添加新的目标语言？
**A:** 在 GUI 界面的语言选择区域勾选新语言即可。支持 33 种语言。

### Q4: 输出表格的格式是什么样的？
**A:** 每行对应一个 key 和 source_text，每列对应一个目标语言。详见 [完整使用手册](COMPLETE_MANUAL.md) 的输出结果格式章节。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

### 开发环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd translation

# 安装开发依赖
pip install -r requirements-test.txt

# 运行测试
pytest tests/ -v
```

### 代码规范

- 遵循 PEP 8 编码规范
- 所有公共函数必须有文档字符串
- 所有新功能必须包含单元测试
- 提交前确保所有测试通过

## 📝 更新日志

### v3.2.0 (2026-04-03)
- ✨ **翻译模式选择** - 支持三种模式：完整双阶段(full)/仅初译(draft_only)/仅校对(review_only)
- ✨ **提示词高级设置** - GUI新增自定义Role/Task/Constraints功能
- ✨ **提示词模板配置** - config.json新增prompt_templates配置项
- ✨ **动态UI调整** - 根据翻译模式自动显示/隐藏相关配置项
- 🔧 优化配置管理 - 统一翻译模式配置接口

### v3.1.0 (2026-04-03)
- ✨ 一键配置系统 - 重新设计快速配置脚本，支持 7 种模型提供商
- ✨ 多模型支持 - DeepSeek、OpenAI、通义千问、智谱 AI、Moonshot、Claude、Gemini
- ✨ 简化配置流程 - 只需输入 API Key 即可完成配置
- 🐛 修复依赖容器初始化问题
- 🐛 修复异常处理模块重复定义问题
- 🔧 代码质量优化 - 重构配置验证、错误处理、嵌套字典访问

### v3.0.0 (2026-04-01)
- ✨ 六层分层架构重构
- ✨ 依赖注入容器实现
- ✨ 外观模式简化调用
- ✨ LRU 缓存优化
- ✨ 语言扩展至 33 种

### v2.0.0 (2026-03-20)
- ✅ 五层模块化重构
- ✅ 配置管理集中化
- ✅ 日志分级和标签过滤

### v1.0.0 (2026-03-01)
- 🎉 初始版本发布

## 📄 许可证

MIT License

## 👥 作者

Translation Team

## 🙏 致谢

感谢所有贡献者和用户!

---

**遇到问题？**
- ⭐⭐⭐ **[完整使用手册](COMPLETE_MANUAL.md)** - 一站式解决方案
- ⚡ **[v3.1.0 一键配置指南](docs/guides/CONFIG_SETUP_HANDBOOK.md)** - 3 分钟快速配置
- [故障排查指南](docs/guides/TROUBLESHOOTING.md) - 详细排查步骤
- 提交 Issue
- 联系开发团队
