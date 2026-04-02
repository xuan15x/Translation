> ⚠️ **重要提示**: 本文档内容已整合到 [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md)  
> 建议优先阅读新手册获取更全面、更准确的信息
> 
> **整合日期**: 2026-04-01  
> **替代文档**: [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md) 第 3 章 - 配置指南

---

# 配置文件与提示词注意事项

**版本**: 2.1.0  
**最后更新**: 2026-03-31  
**适用范围**: AI 智能翻译工作台 v2.0

---

## 📋 目录

1. [配置文件注意事项](#配置文件注意事项)
2. [API 配置关键点](#api-配置关键点)
3. [模型参数配置](#模型参数配置)
4. [并发与性能配置](#并发与性能配置)
5. [术语库配置](#术语库配置)
6. [提示词强制要求](#提示词强制要求)
7. [常见错误与解决方案](#常见错误与解决方案)

---

## 配置文件注意事项

### ⚠️ 配置文件格式

#### JSON vs YAML

| 特性 | JSON | YAML |
|------|------|------|
| **语法严格性** | 非常严格，逗号、引号不能错 | 相对宽松，缩进敏感 |
| **注释支持** | ❌ 不支持（使用 `_comment` 字段） | ✅ 支持 `#` 注释 |
| **多行字符串** | ❌ 需用 `\n` 转义 | ✅ 使用 `|` 或 `>` |
| **推荐场景** | 程序生成配置 | 人工编辑配置 |

#### JSON 配置易错点

```json
{
  "draft_prompt": "Role: Translator.\nTask: Translate.\nConstraints:\n1. Output JSON ONLY: {{\"Trans\": \"string\"}}."
}
```

**❌ 常见错误**:
```json
// 错误 1: 双引号未转义
"draft_prompt": "Output JSON: {"Trans": "string"}"  // ❌

// 错误 2: 换行符未转义
"draft_prompt": "Line 1
Line 2"  // ❌

// 错误 3: 多余逗号
{
  "temperature": 0.3,  // ❌ 最后一个属性后有逗号
}
```

**✅ 正确写法**:
```json
{
  "draft_prompt": "Role: Translator.\nTask: Translate.\nConstraints:\n1. Output JSON ONLY: {{\"Trans\": \"string\"}}."
}
```

#### YAML 配置易错点

```yaml
# ✅ 正确 - 多行字符串
draft_prompt: |
  Role: Professional Translator.
  Task: Translate 'Src' to {target_lang}.
  Constraints:
  1. Output JSON ONLY: {{"Trans": "string"}}.

# ❌ 错误 - 缩进不一致
draft_prompt: |
  Role: Translator.
Task: Translate.  # ❌ 缩进错误

# ❌ 错误 - 冒号后缺少空格
temperature:0.3  # ❌ 应为 temperature: 0.3
```

---

## API 配置关键点

### 🔑 API 密钥配置

#### 配置方式（仅支持配置文件）

**方式 1: 配置文件（推荐）**
```json
{
  "api_key": "sk-your-api-key-here"
}
```

**方式 2: GUI 界面配置**
在翻译平台启动后，通过界面中的"🔌 API 提供商"区域直接输入 API 密钥。

#### ⚠️ 重要提示

**已废弃：环境变量方式**
- ❌ 不再支持通过环境变量读取 API 密钥
- ✅ 所有 API 密钥必须通过配置文件或 GUI 界面设置
- ✅ 这样可以避免因为环境变量未设置导致程序无法使用

#### ⚠️ 安全注意事项

```json
{
  // ❌ 绝对不要将真实 API Key 提交到 Git
  "api_key": "sk-1234567890abcdef"  // ❌ 危险！
  
  // ✅ 正确做法：使用占位符 + 环境变量
  "api_key": "your_api_key_here",  // 然后在 .env 文件或环境变量中设置
  
  // ✅ 或使用 Git 忽略的本地配置文件
  // config.json (在 .gitignore 中)
}
```

**.gitignore 必须包含**:
```gitignore
# API 密钥文件
config/config.json
.env
*.key
*.secret
```

### 🌐 Base URL 配置

```json
{
  "base_url": "https://api.deepseek.com",  // DeepSeek 官方
  "api_provider": "deepseek"
}
```

**常见 API 提供商 Base URL**:
```json
// DeepSeek
"base_url": "https://api.deepseek.com"

// OpenAI
"base_url": "https://api.openai.com/v1"

// Moonshot (月之暗面)
"base_url": "https://api.moonshot.cn/v1"

// Zhipu (智谱 AI)
"base_url": "https://open.bigmodel.cn/api/paas/v4"

// 自定义/私有化部署
"base_url": "https://your-custom-api.com/v1"
```

### ⚠️ API 配置验证

**启动时自动验证**:
```python
# models.py: __post_init__
if not self.api_key or not self.api_key.strip():
    error_msg = f"❌ 致命错误：API 密钥不能为空，请在配置文件或 GUI 界面中设置 api_key。"
    raise AuthenticationError(error_msg)
```

**常见错误**:
```
❌ 错误：API 密钥不能为空
✅ 解决：在 config.json 文件中设置 "api_key": "your-key" 或通过 GUI 界面配置
```

---

## 模型参数配置

### 🎯 Temperature 配置

**有效范围**: `0.0 - 2.0`

| 值范围 | 效果 | 适用场景 |
|--------|------|----------|
| **0.0 - 0.3** | 保守、确定性强 | 技术文档、法律文本 |
| **0.3 - 0.5** | 平衡、适中 | 一般翻译任务 ⭐推荐 |
| **0.5 - 0.7** | 创意、灵活 | 文学翻译、润色 |
| **0.7 - 1.0** | 非常自由 | 创意写作 |
| **> 1.0** | 极度随机 | 不推荐用于翻译 |

**配置示例**:
```json
{
  "temperature": 0.3,  // 全局默认
  "draft_temperature": 0.3,  // 初译阶段（更保守）
  "review_temperature": 0.5  // 校对阶段（更灵活）
}
```

**⚠️ 验证规则**:
```python
# 会抛出 ValidationError 的情况
if not 0 <= temperature <= 2:
    raise ValidationError(
        f"temperature 必须在 0-2 之间",
        field_name='temperature',
        details={'current_value': temperature, 'valid_range': '0-2'}
    )
```

### 🎲 Top P 配置

**有效范围**: `0.0 - 1.0`

| 值范围 | 效果 | 推荐场景 |
|--------|------|----------|
| **0.5 - 0.7** | 较保守 | 需要高度一致的翻译 |
| **0.7 - 0.9** | 平衡 ⭐ | 一般翻译任务（推荐） |
| **0.9 - 1.0** | 更自由 | 创意性翻译 |

**配置示例**:
```json
{
  "top_p": 0.8,  // 全局默认
  "draft_top_p": 0.8,  // 初译
  "review_top_p": 0.9  // 校对（更灵活）
}
```

### 🔧 分阶段模型配置

**为什么需要分阶段配置？**
- 初译需要准确、保守
- 校对需要灵活、优化表达

**完整配置示例 (YAML)**:
```yaml
# 全局配置
model_name: "deepseek-chat"
temperature: 0.3
top_p: 0.8

# 初译阶段（更保守）
draft_model_name: "deepseek-chat"
draft_temperature: 0.3
draft_top_p: 0.8
draft_timeout: 60
draft_max_tokens: 512

# 校对阶段（更灵活）
review_model_name: "gpt-4"  # 可以使用更强的模型
review_temperature: 0.5
review_top_p: 0.9
review_timeout: 90  # 更长的超时
review_max_tokens: 512
```

**⚠️ 配置继承规则**:
```python
# 如果子配置为 None，则使用全局配置
def get_draft_temperature(self) -> float:
    return self.draft_temperature if self.draft_temperature is not None else self.temperature
```

---

## 并发与性能配置

### 🚀 并发控制配置

```json
{
  "initial_concurrency": 8,      // 初始并发数
  "max_concurrency": 10,         // 最大并发数（上限）
  "concurrency_cooldown_seconds": 5.0  // 冷却时间
}
```

**⚠️ 配置约束**:
```python
# 必须满足的条件
if initial_concurrency < 1:
    raise ValidationError("initial_concurrency 必须 >= 1")

if max_concurrency < initial_concurrency:
    raise ValidationError("max_concurrency 必须 >= initial_concurrency")
```

**推荐配置**:
| 场景 | initial_concurrency | max_concurrency | cooldown |
|------|---------------------|-----------------|----------|
| **测试/小规模** | 2-4 | 5-8 | 3.0s |
| **常规翻译** ⭐ | 8-10 | 10-15 | 5.0s |
| **大批量** | 10-15 | 15-20 | 8.0s |
| **API 限流严重** | 1-2 | 3-5 | 10.0s |

### ⏱️ 超时与重试配置

```json
{
  "timeout": 60,              // 请求超时（秒）
  "max_retries": 3,           // 最大重试次数
  "retry_streak_threshold": 3,  // 连续成功阈值
  "base_retry_delay": 3.0     // 基础重试延迟（秒）
}
```

**超时配置建议**:
- **短文本** (< 50 字): 30-45 秒
- **中等文本** (50-200 字): 60 秒 ⭐
- **长文本** (> 200 字): 90-120 秒

**重试策略**:
```python
# 指数退避重试
delay = base_retry_delay * (2 ** retry_count)
# 第 1 次重试：3 秒
# 第 2 次重试：6 秒
# 第 3 次重试：12 秒
```

### 💾 缓存配置

```json
{
  "cache_capacity": 2000,     // 缓存容量（条目数）
  "cache_ttl_seconds": 3600   // 缓存过期时间（秒）
}
```

**缓存容量计算**:
```
假设每条术语平均 100 bytes
cache_capacity = 2000
所需内存 ≈ 2000 * 100B = 200KB

推荐配置:
- 小型术语库 (< 1000 条): 1000-2000
- 中型术语库 (1000-5000 条): 2000-5000 ⭐
- 大型术语库 (> 5000 条): 5000-10000
```

**TTL 配置建议**:
- **永不过期**: `cache_ttl_seconds = 0`
- **短期缓存**: 1800 (30 分钟)
- **中期缓存**: 3600 (1 小时) ⭐推荐
- **长期缓存**: 7200 (2 小时)

---

## 术语库配置

### 📊 模糊匹配配置

```json
{
  "similarity_low": 60,           // 最低相似度阈值
  "exact_match_score": 100,       // 精确匹配置信度
  "multiprocess_threshold": 1000  // 多进程处理阈值
}
```

**相似度阈值说明**:
| 值 | 效果 | 推荐场景 |
|----|------|----------|
| **40-50** | 非常宽松，匹配范围广 | 探索性翻译 |
| **50-60** | 较宽松 | 新领域翻译 |
| **60-70** | 平衡 ⭐ | 常规翻译（推荐） |
| **70-80** | 较严格 | 专业术语翻译 |
| **80-90** | 非常严格 | 高精度要求 |
| **90-100** | 几乎完全匹配 | 标准化文案 |

**⚠️ 性能影响**:
```python
# 术语库数据量 > multiprocess_threshold 时使用多进程
if len(items) > multiprocess_threshold * 2:
    # 使用多进程（更快但资源消耗大）
    with ProcessPoolExecutor(max_workers=2) as ex:
        result = await loop.run_in_executor(ex, match_function)
elif len(items) > multiprocess_threshold:
    # 单进程但优化
    result = await loop.run_in_executor(None, match_function)
else:
    # 直接同步计算
    result = match_function()
```

**推荐配置**:
- **小型术语库** (< 1000 条): `multiprocess_threshold = 500`
- **中型术语库** (1000-5000 条): `multiprocess_threshold = 1000` ⭐
- **大型术语库** (> 5000 条): `multiprocess_threshold = 2000`

---

## 提示词强制要求

### 🎯 Draft Prompt（初译提示词）

**标准模板**:
```
Role: Professional Translator.
Task: Translate 'Src' to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Strictly follow provided TM.
3. Accurate and direct.
```

**⚠️ 强制要求**:

1. **输出格式必须为 JSON**
   ```json
   // ✅ 正确
   {"Trans": "翻译结果"}
   
   // ❌ 错误 - 不是 JSON
   Trans: 翻译结果
   
   // ❌ 错误 - 额外内容
   Here is the translation: {"Trans": "翻译结果"}
   ```

2. **必须使用双重大括号转义**
   ```json
   // ✅ 正确（JSON 文件中）
   "draft_prompt": "Output JSON ONLY: {{\"Trans\": \"string\"}}"
   
   // ❌ 错误 - 缺少转义
   "draft_prompt": "Output JSON ONLY: {\"Trans\": \"string\"}"
   ```

3. **变量占位符格式**
   ```json
   // ✅ 正确 - 使用 {target_lang}
   "Task: Translate 'Src' to {target_lang}."
   
   // ❌ 错误 - 拼写错误
   "Task: Translate 'Src' to {target_language}."
   ```

4. **约束条件必须明确**
   ```
   // ✅ 推荐的约束
   1. Output JSON ONLY: {{"Trans": "string"}}.
   2. Strictly follow provided TM.
   3. Accurate and direct.
   
   // ❌ 模糊的约束
   Please translate carefully.
   ```

### 🔍 Review Prompt（校对提示词）

**标准模板**:
```
Role: Senior Language Editor.
Task: Polish 'Draft' into native {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars. If no change, Reason="".
3. Focus on flow and tone.
```

**⚠️ 强制要求**:

1. **输出格式必须包含两个字段**
   ```json
   // ✅ 正确
   {"Trans": "润色后的翻译", "Reason": "更流畅"}
   
   // ✅ 正确 - 无修改
   {"Trans": "原翻译", "Reason": ""}
   
   // ❌ 错误 - 缺少 Reason
   {"Trans": "润色后的翻译"}
   
   // ❌ 错误 - Reason 过长
   {"Trans": "润色后的翻译", "Reason": "这个翻译更加自然流畅"}  // 超过 10 字符
   ```

2. **Reason 字段限制**
   ```
   // ✅ 接受的 Reason
   "更流畅"      // 3 字符
   "语气更好"     // 4 字符
   "更符合习惯"   // 5 字符
   ""            // 无修改
   
   // ❌ 拒绝的 Reason
   "这个翻译读起来更加自然和流畅，更符合目标语言的表达习惯"  // 太长！
   ```

3. **校对焦点明确**
   ```
   // ✅ 正确的焦点描述
   "Focus on flow and tone."
   "Improve naturalness."
   
   // ❌ 过于宽泛
   "Make it better."
   "Polish the translation."
   ```

### 📝 提示词配置最佳实践

#### JSON 配置文件中的提示词

```json
{
  "draft_prompt": "Role: Professional Translator.\nTask: Translate 'Src' to {target_lang}.\nConstraints:\n1. Output JSON ONLY: {{\"Trans\": \"string\"}}.\n2. Strictly follow provided TM.\n3. Accurate and direct.",
  
  "review_prompt": "Role: Senior Language Editor.\nTask: Polish 'Draft' into native {target_lang}.\nConstraints:\n1. Output JSON ONLY: {{\"Trans\": \"string\", \"Reason\": \"string\"}}.\n2. 'Reason': Max 10 chars. If no change, Reason=\"\".\n3. Focus on flow and tone."
}
```

#### YAML 配置文件中的提示词（推荐）

```yaml
draft_prompt: |
  Role: Professional Translator.
  Task: Translate 'Src' to {target_lang}.
  Constraints:
  1. Output JSON ONLY: {{"Trans": "string"}}.
  2. Strictly follow provided TM.
  3. Accurate and direct.

review_prompt: |
  Role: Senior Language Editor.
  Task: Polish 'Draft' into native {target_lang}.
  Constraints:
  1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
  2. 'Reason': Max 10 chars. If no change, Reason="".
  3. Focus on flow and tone.
```

---

## 常见错误与解决方案

### ❌ 错误 1: API Key 配置错误

**症状**:
```
❌ 致命错误：未找到环境变量 'DEEPSEEK_API_KEY'
AuthenticationError: [AUTH_001] API 密钥缺失
```

**原因**:
1. 未在环境变量中设置 API Key
2. 配置文件中 api_key 为空
3. 环境变量名称拼写错误

**解决方案**:
```bash
# 方法 1: 设置环境变量（推荐）
# Windows
setx DEEPSEEK_API_KEY "sk-your-key-here"

# Linux/Mac
export DEEPSEEK_API_KEY="sk-your-key-here"

# 方法 2: 修改配置文件
{
  "api_key": "sk-your-key-here"  // 填入真实的 API Key
}
```

### ❌ 错误 2: Temperature 超出范围

**症状**:
```
ValidationError: [CFG_002] temperature 必须在 0-2 之间
字段：temperature
当前值：2.5
有效范围：0-2
```

**原因**:
- 配置了无效的 temperature 值（如 2.5、-0.1）

**解决方案**:
```json
{
  // ❌ 错误配置
  "temperature": 2.5,
  
  // ✅ 正确配置
  "temperature": 0.3  // 在 0-2 之间
}
```

### ❌ 错误 3: 并发配置冲突

**症状**:
```
ValidationError: [CFG_002] max_concurrency 必须 >= initial_concurrency
当前值：5
要求最小值：8
```

**原因**:
- max_concurrency 小于 initial_concurrency

**解决方案**:
```json
{
  // ❌ 错误配置
  "initial_concurrency": 8,
  "max_concurrency": 5,
  
  // ✅ 正确配置
  "initial_concurrency": 8,
  "max_concurrency": 10  // 必须 >= initial_concurrency
}
```

### ❌ 错误 4: 提示词 JSON 格式错误

**症状**:
```
ParsingError: [DATA_002] JSON 解析失败
格式：json
原始异常：JSONDecodeError: Expecting property name...
```

**原因**:
- 提示词中的 JSON 格式不正确
- 双引号未正确转义

**解决方案**:
```json
{
  // ❌ 错误 - 双引号未转义
  "draft_prompt": "Output JSON: {\"Trans\": \"string\"}",
  
  // ✅ 正确 - 使用双重大括号
  "draft_prompt": "Output JSON ONLY: {{\"Trans\": \"string\"}}"
}
```

### ❌ 错误 5: YAML 缩进错误

**症状**:
```
ConfigError: [CFG_001] 配置文件格式错误
文件：config.yaml
错误：YAMLReaderError: mapping values are not allowed here
```

**原因**:
- YAML 缩进不一致
- 使用了 Tab 而不是空格

**解决方案**:
```yaml
# ❌ 错误 - 缩进混乱
draft_prompt: |
  Role: Translator.
Task: Translate.  # 缩进错误
  Constraints:
    1. Be accurate.  # 缩进过深

# ✅ 正确 - 统一使用 2 个空格缩进
draft_prompt: |
  Role: Translator.
  Task: Translate.
  Constraints:
    1. Be accurate.
```

### ❌ 错误 6: 配置文件路径错误

**症状**:
```
FileNotFoundError: [FILE_002] 配置文件不存在
文件路径：config/config.json
```

**原因**:
- 配置文件未复制到正确位置
- 路径拼写错误

**解决方案**:
```bash
# 确保配置文件存在
cd /path/to/translation
cp config/config.example.json config/config.json

# 检查文件是否存在
ls -la config/config.json
```

### ❌ 错误 7: 环境变量优先级混淆

**症状**:
配置的值与预期不符

**原因**:
环境变量的优先级高于配置文件

**优先级顺序**:
```
1. 构造函数参数（最高优先级）
   Config(api_key="xxx")
   
2. 环境变量
   export DEEPSEEK_API_KEY="xxx"
   
3. 配置文件（最低优先级）
   config.json 中的值
```

**解决方案**:
```python
# 了解优先级顺序
config = Config()  # 会使用环境变量或配置文件的值

# 如果需要强制使用特定值
config = Config(api_key="force-this-key")  # 覆盖所有配置
```

---

## 📖 相关文档

- [架构设计文档](../docs/architecture/ARCHITECTURE.md) - 了解系统整体架构
- [错误处理指南](../docs/development/ERROR_HANDLING_GUIDE.md) - 异常处理机制
- [最佳实践指南](../docs/guides/BEST_PRACTICES.md) - 使用技巧
- [故障排查手册](../docs/guides/TROUBLESHOOTING.md) - 常见问题解决

---

**维护者**: Development Team  
**下次审查**: 2026-04-30  
**贡献**: 欢迎提交 Issue 和 PR 改进文档
