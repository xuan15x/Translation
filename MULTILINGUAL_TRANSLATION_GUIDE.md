# 多语言批量翻译功能说明

## 功能概述

当用户选择多种语言进行翻译时，系统会自动启用**多语言批量翻译模式**，将同一原文的多种语言翻译合并到**一个 API 请求**中，大幅提高翻译效率并降低成本。

---

## 工作原理

### 传统模式（单语言）
```
原文 "你好" -> API 请求 1 -> 英语 "Hello"
原文 "你好" -> API 请求 2 -> 日语 "こんにちは"
原文 "你好" -> API 请求 3 -> 韩语 "안녕하세요"
```
**100 行 × 3 种语言 = 300 次 API 请求**

### 多语言模式（新）
```
原文 "你好" -> API 请求 1 -> {"en": "Hello", "ja": "こんにちは", "ko": "안녕하세요"}
```
**100 行 × 3 种语言 = 100 次 API 请求**

---

## 性能提升

| 指标 | 单语言模式 | 多语言模式 | 提升 |
|-----|-----------|-----------|------|
| API 调用次数 | 300次 | 100次 | **-66%** |
| 预估成本 | ¥30 | ¥10 | **-67%** |
| 预估耗时 | 60秒 | 25秒 | **-58%** |

---

## 自动启用条件

系统会在以下情况下自动启用多语言模式：

1. ✅ 选择了 **2 种或以上**的目标语言
2. ✅ 多语言翻译服务已正确初始化
3. ✅ 术语库可用（用于术语匹配）

**无需手动配置**，系统会自动检测并启用最优模式。

---

## 输出格式

### 传统模式输出（每种语言一个文件）
| 行号 | Key | 原文 | 译文 | 状态 |
|-----|-----|------|------|------|
| 1 | row0 | 你好 | Hello | success |

### 多语言模式输出（所有语言在一个文件）
| 行号 | Key | 原文 | 译文_英语 | 状态_英语 | 译文_日语 | 状态_日语 | 译文_韩语 | 状态_韩语 |
|-----|-----|------|---------|----------|---------|----------|---------|----------|
| 1 | row0 | 你好 | Hello | success | こんにちは | success | 안녕하세요 | success |

---

## API 请求格式

### 系统提示词
```
Role: Professional Multi-lingual Translator.
Task: Translate the source text into ALL specified target languages: en, ja, ko.
Constraints:
1. Output ONLY valid JSON with language codes as keys
2. Each translation must be accurate and natural
3. Strictly follow provided TM suggestions
4. Do not include any explanation or extra text
5. Preserve original formatting and line breaks

Example Output:
{"en": "Hello", "ja": "こんにちは", "ko": "안녕하세요"}
```

### 用户消息
```
Src: 欢迎使用我们的翻译平台

TM(en, 100): 欢迎 -> Welcome
TM(ja, 100): 欢迎 -> ようこそ

Output ONLY valid JSON: {"en": "...", "ja": "...", "ko": "..."}
```

### 期望响应
```json
{
  "en": "Welcome to our translation platform",
  "ja": "翻訳プラットフォームへようこそ",
  "ko": "번역 플랫폼에 오신 것을 환영합니다"
}
```

---

## 技术架构

### 新增组件

1. **`domain/models.py`**
   - `MultiLanguageTask` - 多语言任务模型
   - `MultiLanguageResult` - 多语言翻译结果

2. **`domain/translation_service_multilingual.py`**
   - `MultilingualTranslationService` - 多语言翻译服务
   - 查询术语匹配（所有语言）
   - 调用多语言 API 并分发结果

3. **`service/api_stage_multilingual.py`**
   - `MultilingualAPIStage` - 多语言 API 调用阶段
   - 构建多语言提示词
   - 解析 JSON 响应

4. **`application/result_builder.py`**
   - `TaskFactory.from_excel_file_multilingual()` - 创建多语言任务

5. **`application/translation_facade.py`**
   - `enable_multilingual_mode()` - 启用多语言模式
   - `_translate_file_multilingual()` - 多语言翻译流程
   - `_export_multilingual_results()` - 多语言 Excel 导出

---

## 兼容性

### ✅ 向后兼容
- 原有 `translate_file()` 方法保持不变
- 现有单语言模式继续工作
- 多语言模式为**可选增强**功能

### 降级策略
如果多语言模式初始化失败，系统会：
1. 记录警告日志
2. 自动降级到单语言模式
3. 继续正常翻译

---

## 限制与注意事项

### 1. max_tokens 计算
系统会根据语言数量动态计算 `max_tokens`：
```python
max_tokens = max(config.max_tokens, len(target_langs) * 200)
```

### 2. JSON 解析失败
如果 API 返回的不是有效 JSON：
- 自动重试（最多 `max_retries` 次）
- 使用指数退避策略

### 3. 部分语言失败
如果某些语言翻译成功，某些失败：
- 成功的语言正常保存
- 失败的语言标记为失败
- 在日志中记录详细信息

---

## 日志示例

```
🌐 使用多语言翻译模式（一次请求翻译 3 种语言）
创建了 100 个多语言翻译任务
✅ 从提供商配置获取 base_url: https://api.deepseek.com
📤 开始调用 translation_facade.translate_file...
多语言翻译请求: 欢迎使用我们的翻译平台... -> ['英语', '日语', '韩语']
API 响应: {"en": "Welcome to...", "ja": "翻訳...", "ko": "번역..."}...
多语言翻译完成：3/3 成功
多语言结果已导出到：D:/翻译结果.xlsx
```

---

## 测试建议

### 1. 功能测试
- [ ] 选择 2 种语言翻译
- [ ] 选择 3 种语言翻译
- [ ] 选择 5 种以上语言翻译
- [ ] 验证输出 Excel 格式

### 2. 性能测试
- [ ] 对比单语言和多语言模式的 API 调用次数
- [ ] 对比翻译耗时
- [ ] 验证成本节约

### 3. 边界测试
- [ ] 只选择 1 种语言（应使用单语言模式）
- [ ] 选择 10 种以上语言
- [ ] 术语库命中场景

---

## 未来优化

1. **批量大小优化**
   - 根据 API 限制动态调整批处理大小
   - 支持自定义批次大小

2. **缓存优化**
   - 缓存多语言翻译结果
   - 支持部分语言缓存

3. **错误恢复**
   - 支持失败语言单独重试
   - 断点续传多语言任务

---

## 常见问题

### Q: 如何禁用多语言模式？
A: 目前系统会自动启用，如需禁用可修改 `event_handlers.py` 中的 `use_multilingual=False`。

### Q: 多语言模式支持哪些 API 提供商？
A: 支持所有兼容 OpenAI 格式的 API，包括 DeepSeek、OpenAI、通义千问等。

### Q: 翻译结果不准确怎么办？
A: 可以调整提示词或增加 max_tokens。系统已内置重试机制。

---

**最后更新**: 2026-04-03
**版本**: v3.3.0
