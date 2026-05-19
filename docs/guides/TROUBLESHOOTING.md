# 故障排查手册

## 启动问题

### Q: 运行 `python run.py` 提示 "配置文件不存在"
- 确认 `translation_task.json` 已创建（参考模板如下）
- 可用绝对路径指定：`python run.py /path/to/my_config.json`

### Q: 运行提示 "请先在 config/config.json 中配置有效的 api_key"
- 编辑 `config/config.json`，将 `api_key` 改为你的 DeepSeek API Key
- 从 [platform.deepseek.com](https://platform.deepseek.com) 获取

### Q: 运行提示 "输入文件不存在"
- 检查 `translation_task.json` 中 `task.input_file` 路径是否正确
- 路径相对于项目根目录（`translation-tool/`）

## 翻译问题

### Q: 翻译速度慢
- 增加 `translation_task.json` 中 `concurrency.limit`（默认 5）
- 降低 `config/config.json` 中 `timeout`（默认 60 秒）
- 检查网络延迟：`ping api.deepseek.com`

### Q: API 频繁返回 429（限频）
- 降低 `translation_task.json` 中 `concurrency.limit` 至 2-3
- 增加 `config/config.json` 中 `base_retry_delay`（默认 3.0 秒）
- 减少 `languages.target` 语言数量，分批翻译

### Q: 翻译结果为空或不完整
- 检查 `config/config.json` 中 `draft_max_tokens` 是否过小（建议 ≥512）
- 查看运行日志中的错误信息

### Q: 翻译质量差
- 优化 `config/config.json` 中 `draft_prompt` / `review_prompt` 提示词
- 降低 `temperature`（推荐 0.2-0.3）
- 配置术语库提升一致性

### Q: 译文列显示 `(Failed)`
- 检查 API Key 余额是否充足
- 查看 `config/config.json` 中 `timeout` 是否过短
- 尝试减少并发或语言数量

## 输出问题

### Q: 输出 Excel 列顺序不对
- 编辑 `translation_task.json` → `languages.target`，调整语言顺序即可

### Q: 输出缺少某些语言
- 确认 `translation_task.json` → `languages.target` 包含该语言
- 确认语言名**完全匹配**可用列表（如"西班牙语"非"西班牙文"）

### Q: 如何只输出部分语言
- 从 `translation_task.json` → `languages.target` 中删掉不译的语言

## 配置问题

### Q: config.json 修改后不生效
- 检查 JSON 格式是否正确：`python -m json.tool config/config.json`
- 重新运行 `python run.py`

### Q: 如何验证配置文件
```bash
# 验证 JSON 格式
python -m json.tool config/config.json > /dev/null && echo "✅" || echo "❌"
python -m json.tool translation_task.json > /dev/null && echo "✅" || echo "❌"

# 验证模块导入
python -c "from infrastructure.models.config import Config; c=Config(api_key='test'); print('✅')"

# 运行全量测试
python -m pytest tests/ -q
```
