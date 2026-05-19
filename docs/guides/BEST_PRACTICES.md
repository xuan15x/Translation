# 最佳实践指南

## 1. 翻译质量优化

### 1.1 提示词优化建议
- **Role 设定**要精准：`Professional Game Translator` 比 `Translator` 效果更好
- **Constraints 要具体**：列明字符限制、术语要求、输出格式
- **Context 要保留**：审校阶段尽量保留初译的语境信息

### 1.2 双阶段参数推荐
| 场景 | Draft Temperature | Review Temperature |
|------|------------------|-------------------|
| 技术文档 | 0.2 | 0.4 |
| 游戏文本（常规） | 0.3 | 0.5 |
| 游戏文本（创意） | 0.4 | 0.7 |
| UI 文本 | 0.1 | 0.3 |

### 1.3 术语库最佳实践
- 字段名保持统一（推荐 `source` 和 `target`）
- 使用完整词条而非缩写
- 定期更新术语库

## 2. 性能优化

### 2.1 并发参数
- 个人使用：`initial_concurrency: 8, max_concurrency: 10`
- 团队使用：`initial_concurrency: 15, max_concurrency: 20`
- API 限流严重时：降低到 3-5

### 2.2 缓存配置
- `cache_capacity: 2000` — 平衡内存与命中率
- `cache_ttl_seconds: 3600` — 1 小时后自动刷新

## 3. 工作流建议

1. **先测试小批量**：选择 10-50 行文本试译
2. **审查初译质量**：确认术语正确后再开启校对
3. **渐进式翻译**：T3 语言可用「仅初译」，T1 语言用「完整翻译」

## 4. 命名规范

- 源文件：`source_en.json`、`source_zh.xlsx`
- 术语库：`glossary_zh-en.xlsx`
- 输出：`output_ja.json`、`output_ko.xlsx`
