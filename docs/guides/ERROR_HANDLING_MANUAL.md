# 🚨 翻译平台错误查看手册

本手册详细列出了翻译平台所有可能的报错信息、问题原因和修复方法。

---

## 📋 目录

1. [配置文件相关错误](#配置文件相关错误)
2. [API 相关错误](#api-相关错误)
3. [文件操作相关错误](#文件操作相关错误)
4. [数据库相关错误](#数据库相关错误)
5. [翻译流程相关错误](#翻译流程相关错误)
6. [GUI 界面相关错误](#gui-界面相关错误)
7. [术语库相关错误](#术语库相关错误)
8. [网络和连接错误](#网络和连接错误)

---

## 配置文件相关错误

### ❌ 错误 1：配置文件不存在

**错误信息：**
```
FileNotFoundError: 配置文件不存在：config/config.json
```

**问题原因：**
- 指定的配置文件路径不存在
- 文件名拼写错误
- 文件被移动或删除

**修复方法：**
1. 检查文件路径是否正确
2. 确认文件确实存在于该路径
3. 使用绝对路径尝试：`C:\Users\你的用户名\PycharmProjects\translation\config\config.json`
4. 如果文件丢失，从 `config.example.json` 复制并重新配置

**预防措施：**
- 启动时使用默认配置：不指定 `--config` 参数
- 定期备份配置文件

---

### ❌ 错误 2：配置文件格式无效

**错误信息：**
```
ValueError: 无效的 JSON 格式：Expecting property name enclosed in double quotes
```

**问题原因：**
- JSON 文件格式错误（缺少引号、逗号等）
- 使用了中文标点符号
- 末尾有多余的逗号

**修复方法：**
1. 使用 JSON 验证工具检查文件：https://jsonlint.com/
2. 确保所有键名都用双引号包裹
3. 移除最后一个属性后的逗号
4. 示例对比：

❌ **错误格式：**
```json
{
    'api_key': 'your-key',  // 单引号错误
    'model': 'deepseek-chat',
}  // 末尾逗号错误
```

✅ **正确格式：**
```json
{
    "api_key": "your-key",
    "model": "deepseek-chat"
}
```

---

### ❌ 错误 3：缺少必需的 API 密钥

**错误信息：**
```
ValueError: 缺少必需的 API 密钥：api_key
```

**问题原因：**
- 配置文件中没有设置 `api_key`
- `api_key` 字段为空字符串
- 环境变量未设置

**修复方法：**
1. 打开配置文件 `config/config.json`
2. 找到对应的 API 提供商配置段
3. 填入有效的 API 密钥：

```json
{
    "deepseek": {
        "api_key": "sk-your-actual-api-key-here",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat"
    }
}
```

4. 保存文件并重启应用

**获取 API 密钥：**
- DeepSeek: https://platform.deepseek.com/api_keys
- OpenAI: https://platform.openai.com/api-keys
- 其他提供商请参考对应官网

---

### ❌ 错误 4：不支持的配置文件格式

**错误信息：**
```
ValueError: 不支持的配置文件格式：.txt，支持的格式：.json, .yaml, .yml
```

**问题原因：**
- 使用了不支持的文件扩展名
- 文件扩展名拼写错误（如 `.jsno`）

**修复方法：**
1. 重命名文件为支持的格式：
   - ✅ `config.json`
   - ✅ `config.yaml`
   - ✅ `config.yml`
2. 确保文件内容格式与扩展名匹配

---

### ❌ 错误 5：配置验证失败

**错误信息：**
```
ValueError: 配置验证失败:
- api_key 不能为空
- base_url 必须是有效的 URL
- default_model 不能为空
```

**问题原因：**
- 多个配置项同时存在问题
- 配置项格式不符合要求

**修复方法：**
1. 逐条检查错误列表
2. 按照提示修复每个配置项
3. 使用配置检查工具：

```bash
python scripts/check_config.py
```

---

## API 相关错误

### ❌ 错误 6：API 认证失败

**错误信息：**
```
AuthenticationError: Invalid API key provided
```

**问题原因：**
- API 密钥错误或已过期
- API 密钥被撤销
- 密钥所属账户余额不足

**修复方法：**
1. 登录 API 提供商官网
2. 检查密钥状态是否有效
3. 检查账户余额
4. 重新生成新的 API 密钥
5. 更新配置文件中的密钥

**检查步骤：**
```bash
# 使用 curl 测试 API 密钥
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.deepseek.com/v1/models
```

---

### ❌ 错误 7：超出 API 速率限制

**错误信息：**
```
RateLimitError: Rate limit reached for requests
```

**问题原因：**
- 短时间内发送了过多请求
- 超过了 API 套餐的并发限制

**修复方法：**
1. **立即措施：**
   - 等待几分钟后再试
   - 减少并发翻译的语言数量
   
2. **长期方案：**
   - 升级 API 套餐提高限额
   - 在配置中调整并发设置：

```json
{
    "translation": {
        "max_concurrent_requests": 5  // 降低并发数
    }
}
```

---

### ❌ 错误 8：模型不存在

**错误信息：**
```
NotFoundError: Model 'gpt-4' does not exist
```

**问题原因：**
- 配置的模型名称错误
- 该模型对当前 API 密钥不可用
- 模型已下线

**修复方法：**
1. 检查模型名称拼写
2. 查看 API 提供商支持的模型列表
3. 在 GUI 中重新选择可用模型
4. 更新配置文件：

```json
{
    "deepseek": {
        "default_model": "deepseek-chat"  // 使用正确的模型名
    }
}
```

---

### ❌ 错误 9：API 请求超时

**错误信息：**
```
TimeoutError: Request timed out after 30s
```

**问题原因：**
- 网络不稳定
- API 服务器响应慢
- 单次翻译内容过长

**修复方法：**
1. **检查网络：**
   - 测试网络连接
   - 尝试访问 API 官网

2. **优化配置：**
   - 增加超时时间：
   ```json
   {
       "api_timeout": 60  // 增加到 60 秒
   }
   ```

3. **减少单次翻译量：**
   - 分批翻译，不要一次性翻译太多内容

---

## 文件操作相关错误

### ❌ 错误 10：Excel 文件不存在

**错误信息：**
```
FileNotFoundError: 待翻译文件不存在：C:\path\to\source.xlsx
```

**问题原因：**
- 文件路径错误
- 文件被移动或删除
- 文件名拼写错误

**修复方法：**
1. 在 GUI 中重新选择文件
2. 确认文件确实在该路径
3. 检查文件名是否正确

**预防措施：**
- 将待翻译文件放在项目目录下
- 使用相对路径而非绝对路径

---

### ❌ 错误 11：Excel 文件格式错误

**错误信息：**
```
ValueError: Excel 文件格式无效：缺少必需的列 ['原文']
```

**问题原因：**
- Excel 文件缺少必需的列
- 列名拼写错误
- 工作表名称不正确

**修复方法：**
1. 打开 Excel 文件检查列名
2. 确保包含以下必需列：
   - ✅ `原文` (或 `source`)
   - ✅ `译文` (或 `target`, 校对模式需要)
3. 修正列名后保存

**正确的 Excel 结构：**
| 原文 | 译文 | 备注 |
|------|------|------|
| Hello World | 你好世界 | 问候语 |

---

### ❌ 错误 12：无法写入 Excel 文件

**错误信息：**
```
PermissionError: Permission denied: output.xlsx
```

**问题原因：**
- 文件正在被其他程序占用
- 文件设置为只读
- 没有写入权限

**修复方法：**
1. 关闭正在编辑该文件的所有程序（Excel、WPS 等）
2. 检查文件属性，取消只读设置
3. 更改输出文件名：
   ```
   output_new.xlsx
   ```

---

## 数据库相关错误

### ❌ 错误 13：SQLite 数据库初始化失败

**错误信息：**
```
sqlite3.Error: unable to open database file
```

**问题原因：**
- 数据库文件路径不存在
- 没有创建数据库文件的权限
- 磁盘空间不足

**修复方法：**
1. 检查数据库文件路径
2. 确保目录存在且有写入权限
3. 清理磁盘空间
4. 删除损坏的数据库文件重新启动

**默认数据库位置：**
- `translation_history.db` - 翻译历史
- `terminology_history.db` - 术语历史

---

### ❌ 错误 14：数据库表不存在

**错误信息：**
```
sqlite3.OperationalError: no such table: translation_history
```

**问题原因：**
- 数据库文件损坏
- 数据库版本过旧
- 表结构变更

**修复方法：**
1. **备份数据（如果可以）：**
   ```bash
   # 导出历史数据
   python scripts/export_history.py
   ```

2. **重建数据库：**
   - 删除旧的 `.db` 文件
   - 重启应用自动创建新表

3. **迁移数据（高级）：**
   ```bash
   python scripts/migrate_database.py
   ```

---

## 翻译流程相关错误

### ❌ 错误 15：翻译失败 - AI 返回空结果

**错误信息：**
```
RuntimeError: 翻译失败：AI 返回空结果
```

**问题原因：**
- 提示词格式错误
- API 返回异常
- 原文内容为空

**修复方法：**
1. 检查提示词是否包含必需的占位符：
   - ✅ `{target_lang}` - 目标语言
   - ✅ `{source_text}` - 原文（部分模板）

2. 验证提示词格式：
   - 点击 GUI 中的 "✅ 验证提示词格式" 按钮

3. 检查原文是否为空或格式异常

---

### ❌ 错误 16：翻译结果格式解析失败

**错误信息：**
```
ValueError: 无法解析翻译结果：期望 JSON 格式但收到纯文本
```

**问题原因：**
- AI 返回的格式不符合预期
- 提示词没有明确要求返回格式
- 网络问题导致响应截断

**修复方法：**
1. 在提示词中明确要求返回格式：
   ```
   请严格按照以下 JSON 格式返回：
   {"translations": [...]}
   ```

2. 检查 AI 返回的原始内容（查看日志）

3. 重试翻译请求

---

### ❌ 错误 17：批量翻译中途失败

**错误信息：**
```
Exception: 批量处理在第 5/10 个任务时失败
```

**问题原因：**
- 某个特定内容导致 AI 异常
- 网络中断
- API 配额用完

**修复方法：**
1. **查看具体失败原因：**
   - 检查日志中该条目的详细信息
   
2. **跳过问题条目：**
   - 记录失败的行号
   - 手动处理该行
   - 继续翻译其他内容

3. **分批翻译：**
   - 不要一次性翻译整个文件
   - 分成小批次进行

---

## GUI 界面相关错误

### ❌ 错误 18：GUI 窗口无法打开

**错误信息：**
```
_tkinter.TclError: can't invoke "button" command: application has been destroyed
```

**问题原因：**
- Tkinter 初始化失败
- 窗口被关闭后重复操作
- Python 环境问题

**修复方法：**
1. 完全退出应用
2. 重新启动 GUI
3. 检查 Python 环境：
   ```bash
   pip install tk
   ```

---

### ❌ 错误 19：GUI 按钮无响应

**现象：**
- 点击按钮没有任何反应
- 界面无卡顿但功能不触发

**问题原因：**
- 事件绑定丢失
- 回调函数抛出异常但被吞掉
- GUI 线程阻塞

**修复方法：**
1. 查看日志文件是否有错误信息
2. 重启 GUI 应用
3. 检查是否在翻译过程中（某些按钮会禁用）

---

### ❌ 错误 20：日志显示异常

**错误信息：**
```
UnicodeDecodeError: 'gbk' codec can't decode byte...
```

**问题原因：**
- 日志文件编码问题
- Windows 系统默认编码冲突

**修复方法：**
1. 删除旧的日志文件
2. 在代码中明确指定 UTF-8 编码
3. 修改系统区域设置（不推荐）

---

## 术语库相关错误

### ❌ 错误 21：术语库导入失败

**错误信息：**
```
ValueError: 术语库 Excel 缺少必需的列：['术语源语言', '术语目标语言']
```

**问题原因：**
- 术语库文件格式不正确
- 列名不匹配

**修复方法：**
1. 确保术语库 Excel 包含以下列：
   - ✅ `术语源语言`
   - ✅ `术语目标语言`
   - ✅ `原文`
   - ✅ `译文`

2. 参考示例文件：`data/terminology_template.xlsx`

---

### ❌ 错误 22：术语冲突检测失败

**错误信息：**
```
ConflictError: 检测到术语冲突：'Health' 对应多个译文
```

**问题原因：**
- 同一原文术语有多个不同的译文
- 术语库中存在重复条目

**修复方法：**
1. 打开术语库 Excel
2. 搜索冲突的术语
3. 统一译文或删除重复项
4. 保存后重新加载

---

## 网络和连接错误

### ❌ 错误 23：无法连接到 API 服务器

**错误信息：**
```
ConnectionError: Failed to establish a new connection
```

**问题原因：**
- 网络连接断开
- 防火墙阻止连接
- API 服务器宕机

**修复方法：**
1. **检查网络：**
   ```bash
   ping api.deepseek.com
   ```

2. **检查防火墙：**
   - 临时关闭防火墙测试
   - 添加 Python 到白名单

3. **检查 API 状态：**
   - 访问 API 提供商的状态页面
   - 查看是否有服务中断公告

---

### ❌ 错误 24：SSL 证书验证失败

**错误信息：**
```
SSLError: certificate verify failed
```

**问题原因：**
- SSL 证书过期
- 系统时间不正确
- 中间人攻击（企业网络）

**修复方法：**
1. **检查系统时间：**
   - 确保日期和时间正确

2. **更新证书：**
   ```bash
   pip install --upgrade certifi
   ```

3. **临时绕过（仅测试）：**
   ```python
   # 不推荐生产环境使用
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

---

### ❌ 错误 25：代理配置错误

**错误信息：**
```
ProxyError: Unable to connect through proxy
```

**问题原因：**
- 代理服务器配置错误
- 代理服务器不可用

**修复方法：**
1. 检查代理配置：
   ```bash
   echo %HTTP_PROXY%
   echo %HTTPS_PROXY%
   ```

2. 清除代理设置（如果不需要）：
   ```bash
   set HTTP_PROXY=
   set HTTPS_PROXY=
   ```

3. 或使用正确的代理配置

---

## 🔧 通用故障排查工具

### 1. 配置检查工具

```bash
python scripts/check_config.py
```

**功能：**
- 验证配置文件格式
- 检查必需的 API 密钥
- 测试 API 连接
- 验证模型配置

---

### 2. 日志分析

**日志位置：**
- GUI 日志：应用底部的日志面板
- 文件日志：`logs/translation_YYYY-MM-DD.log`

**关键日志级别：**
- `INFO` - 正常流程信息
- `WARNING` - 警告但不影响运行
- `ERROR` - 错误需要处理
- `DEBUG` - 详细调试信息

---

### 3. 测试脚本

```bash
# 运行所有测试
pytest tests/

# 测试特定模块
pytest tests/test_api_provider.py
pytest tests/test_config.py
```

---

## 📞 获取帮助

### 遇到问题时的步骤：

1. **查看本手册** - 搜索错误关键词
2. **检查日志** - 查看详细错误信息
3. **使用诊断工具** - `check_config.py`
4. **搜索 Issue** - GitHub Issues
5. **提交 Bug** - 包含完整错误信息和日志

---

## 📝 常见错误速查表

| 错误关键词 | 可能原因 | 快速解决 |
|-----------|---------|---------|
| `FileNotFoundError` | 文件不存在 | 检查路径和文件名 |
| `ValueError` | 值无效 | 检查输入格式 |
| `KeyError` | 键不存在 | 检查配置项名称 |
| `AuthenticationError` | 认证失败 | 检查 API 密钥 |
| `TimeoutError` | 超时 | 增加超时时间/检查网络 |
| `PermissionError` | 权限不足 | 检查文件占用和权限 |
| `ConnectionError` | 连接失败 | 检查网络和防火墙 |

---

## 🎯 最佳实践

### 预防错误的建议：

1. **定期备份：**
   - 备份配置文件
   - 导出翻译历史
   - 保存术语库

2. **使用版本控制：**
   ```bash
   git add config/config.json
   git commit -m "Update config"
   ```

3. **测试配置变更：**
   - 小改动后立即测试
   - 使用 `check_config.py` 验证

4. **保持更新：**
   - 定期拉取最新代码
   - 查看 CHANGELOG.md
   - 更新依赖包

---

**最后更新：** 2026-04-01  
**版本：** v1.0.0
