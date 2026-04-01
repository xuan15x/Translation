# API 密钥配置方式变更说明

## 📋 变更概述

**变更日期**: 2026-04-01  
**变更目的**: 取消环境变量读取 API 密钥，将所有配置集中到配置文件，避免因为环境变量未设置导致程序无法使用

## 🔄 变更内容

### 变更前的配置方式
```bash
# 方式 1: 环境变量（已废弃）
export DEEPSEEK_API_KEY="your-api-key"

# 方式 2: 配置文件
{
  "api_key": "your-api-key"
}
```

### 变更后的配置方式
```json
// 仅支持配置文件或 GUI 界面
{
  "api_key": "your-api-key",
  "api_provider": "deepseek",
  "base_url": "https://api.deepseek.com"
}
```

## 🎯 影响范围

### 修改的文件

#### 1. 核心代码文件
- ✅ `config/config.py` 
  - 移除从环境变量读取 api_key 的逻辑
  - api_key 默认值改为空字符串

- ✅ `infrastructure/models.py`
  - Config 类的 api_key 字段不再从环境变量读取
  - 更新错误提示信息，引导用户使用配置文件
  - 更新验证逻辑中的解决方案提示

- ✅ `service/api_provider.py`
  - create_client 方法不再从环境变量读取 api_key
  - api_key 必须由调用方直接传入

- ✅ `data_access/config_persistence.py`
  - merge_with_env 方法已废弃，不再合并环境变量
  - 直接使用配置文件内容

#### 2. 文档文件
- ✅ `docs/guides/CONFIGURATION_CAUTIONS.md`
  - 更新 API 密钥配置方式说明
  - 标注环境变量方式已废弃
  
- ✅ `docs/guides/QUICKSTART.md`
  - 更新快速入门指南中的配置步骤
  
- ✅ `README.md`
  - 更新主文档中的配置说明

## 💡 优势分析

### 为什么做这个改动？

1. **避免环境变量问题**
   - ❌ 环境变量未设置导致程序崩溃
   - ❌ 不同操作系统环境变量语法不同
   - ❌ 环境变量容易被其他程序覆盖

2. **配置集中管理**
   - ✅ 所有配置都在配置文件中，一目了然
   - ✅ 便于版本控制和备份
   - ✅ 减少配置管理的复杂性

3. **更好的用户体验**
   - ✅ 可以通过 GUI 界面直接配置
   - ✅ 错误提示更明确，引导用户通过配置文件设置
   - ✅ 减少对命令行操作的依赖

## 📖 使用指南

### 新用户配置步骤

#### 方式 1: 使用配置文件（推荐）

1. **复制示例配置文件**
   ```bash
   cd C:\Users\13457\PycharmProjects\translation
   cp config/config.example.json config/config.json
   ```

2. **编辑配置文件**
   打开 `config/config.json`，填入你的 API 密钥：
   ```json
   {
     "api_key": "sk-your-actual-api-key-here",
     "api_provider": "deepseek",
     "base_url": "https://api.deepseek.com",
     "model_name": "deepseek-chat"
   }
   ```

3. **启动程序**
   ```bash
   python presentation/translation.py
   ```

#### 方式 2: 使用 GUI 界面

1. **启动程序**
   ```bash
   python presentation/translation.py
   ```

2. **在 GUI 界面中配置**
   - 找到"🔌 API 提供商"区域
   - 选择 API 提供商（DeepSeek、OpenAI 等）
   - 输入 API 密钥
   - 点击保存

### 老用户迁移指南

如果你之前使用环境变量，需要改为配置文件：

#### Windows PowerShell 用户
```powershell
# ❌ 不再使用这种方式
# $env:DEEPSEEK_API_KEY="your-api-key"

# ✅ 改为配置文件
cd C:\Users\13457\PycharmProjects\translation
notepad config/config.json
```

然后在 config.json 中添加：
```json
{
  "api_key": "your-api-key"
}
```

#### Linux/Mac 用户
```bash
# ❌ 不再使用这种方式
# export DEEPSEEK_API_KEY="your-api-key"

# ✅ 改为配置文件
cd /path/to/translation
nano config/config.json
```

然后在 config.json 中添加：
```json
{
  "api_key": "your-api-key"
}
```

## ⚠️ 注意事项

### 配置优先级

**已废弃的优先级机制**：
```
环境变量 > 配置文件 > 默认值
```

**新的配置机制**：
```
GUI 界面配置 = 配置文件（两者选其一即可）
```

### 安全提示

1. **不要将真实 API Key 提交到 Git**
   ```json
   // ❌ 危险行为
   {
     "api_key": "sk-1234567890abcdef"
   }
   ```

2. **正确做法**
   ```json
   // ✅ 使用占位符
   {
     "api_key": "your_api_key_here"
   }
   ```
   
   然后手动修改为真实密钥

3. **.gitignore 已包含**
   ```gitignore
   # API 密钥文件
   config/config.json
   .env
   *.key
   *.secret
   ```

## 🔍 常见错误及解决方案

### 错误 1: API 密钥不能为空

**错误信息**:
```
❌ 致命错误：API 密钥不能为空，请在配置文件或 GUI 界面中设置 api_key。
```

**解决方案**:
1. 检查 `config/config.json` 是否存在
2. 确认 `api_key` 字段是否有值
3. 或者通过 GUI 界面配置 API 密钥

### 错误 2: 配置文件不存在

**错误信息**:
```
配置文件不存在：config/config.json
```

**解决方案**:
```bash
# 复制示例配置文件
cp config/config.example.json config/config.json
```

## 📚 相关文档

- [完整配置指南](docs/guides/CONFIGURATION_GUIDE.md)
- [快速开始指南](docs/guides/QUICKSTART.md)
- [故障排查手册](docs/guides/TROUBLESHOOTING.md)
- [最佳实践](docs/guides/BEST_PRACTICES.md)

## 🆘 获取帮助

如遇问题，请查看：
1. 日志输出（GUI 界面或控制台）
2. 配置文件格式是否正确
3. API 密钥是否有效
4. 参考故障排查手册

---

**更新日期**: 2026-04-01  
**版本**: v2.0  
**维护者**: AI Translation Platform Team
