# API 和配置文档

本目录包含 API 接口说明和配置文件相关文档。

## 📑 目录

- [📄 文档列表](#-文档列表)
  - [🔌 配置管理](#-配置管理)
  - [📦 依赖管理](#-依赖管理)
- [🎯 常用操作](#-常用操作)
  - [配置相关](#配置相关)
  - [依赖相关](#依赖相关)
- [📖 快速链接](#-快速链接)

---

## 📄 文档列表

### 🔌 配置管理
- **[CONFIG_PERSISTENCE_GUIDE.md](CONFIG_PERSISTENCE_GUIDE.md)** - 配置持久化完整指南
  - JSON/YAML 配置文件格式
  - 配置加载和保存
  - 环境变量覆盖
  - 最佳实践

### 📦 依赖管理
- **[DEPENDENCIES.md](DEPENDENCIES.md)** - 项目依赖说明
  - 生产环境依赖
  - 测试环境依赖
  - 依赖版本要求
  - 安装和升级

## 🎯 常用操作

### 配置相关
- **创建配置文件**: 参考 `config.example.json` 或 `config.example.yaml`
- **加载配置**: 使用 `Config.from_file('config.json')`
- **保存配置**: 使用 `config.save('config.json')`

### 依赖相关
- **安装依赖**: `pip install -r requirements.txt`
- **安装测试依赖**: `pip install -r requirements-test.txt`

## 📖 快速链接

- **配置示例**: [../../config/config.example.json](../../config/config.example.json)
- **配置示例 (YAML)**: [../../config/config.example.yaml](../../config/config.example.yaml)
- **返回主索引**: [../README.md](../README.md)
