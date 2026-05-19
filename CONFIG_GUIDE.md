# 翻译工具 — 配置参数手册

> 完整配置项说明，按文件分类

---

## 一、任务配置文件：`translation_task.json`

每次翻译任务的核心配置，指定输入/输出路径和语言选择。

### 1.1 `task` — 任务基本信息

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | string | 否 | `"未命名"` | 任务名称，用于运行日志标识 |
| `input_file` | string | **是** | — | 输入 Excel 文件路径（相对路径基于项目根目录） |
| `output_file` | string | **是** | — | 输出 Excel 文件路径，自动创建目录 |
| `output_format` | string | 否 | `"wide"` | 输出格式：`"wide"`=36列宽表 |
| `source_lang` | string | 否 | `"中文"` | 源语言标识 |

**示例：**

```json
{
  "task": {
    "name": "游戏术语翻译",
    "input_file": "input/翻译测试表.xlsx",
    "output_file": "output/翻译输出.xlsx",
    "output_format": "wide",
    "source_lang": "中文"
  }
}
```

### 1.2 `languages` — 目标语言

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `target` | string[] | **是** | — | 目标语言列表，输出列名称及顺序与此列表一致 |

**可用语言值（33 种）：**

`英语` `德语` `法语` `日语` `韩语` `瑞典语` `挪威语` `丹麦语` `芬兰语`
`意大利语` `西班牙语` `葡萄牙语` `泰语` `越南语` `印尼语` `马来语`
`俄语` `波兰语` `土耳其语` `阿拉伯语` `印地语` `乌尔都语` `孟加拉语`
`菲律宾语` `缅甸语` `柬埔寨语` `老挝语` `波斯语` `希伯来语`
`斯瓦希里语` `豪萨语` `哈萨克语` `乌兹别克语`

**示例（仅翻译 5 种语言）：**

```json
{
  "languages": {
    "target": ["英语", "日语", "韩语", "法语", "德语"]
  }
}
```

> 输出列顺序与 `target` 列表顺序一致。减少语言数可降低 API 调用量。

### 1.3 `translation` — 翻译参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `mode` | string | 否 | `"multilingual"` | 翻译模式：`"multilingual"`=一次请求翻所有语言，`"single"`=逐语言翻 |
| `enable_two_pass` | boolean | 否 | `true` | 是否启用校对阶段（初译 → 校对），`false`=仅初译 |
| `skip_review_if_local_hit` | boolean | 否 | `true` | 术语库精确命中时跳过校对 |

**示例：**

```json
{
  "translation": {
    "mode": "multilingual",
    "enable_two_pass": true,
    "skip_review_if_local_hit": true
  }
}
```

### 1.4 `concurrency` — 并发控制

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `limit` | integer | 否 | `5` | 并发任务数上限。API 频繁限频（429 错误）时降低此值 |

**示例：**

```json
{
  "concurrency": {
    "limit": 3
  }
}
```

---

## 二、系统配置文件：`config/config.json`

全局系统配置，包含 API 连接参数、模型参数、缓存策略等。

### 2.1 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `api_key` | string | **是** | DeepSeek API Key，从 [platform.deepseek.com](https://platform.deepseek.com) 获取 |
| `base_url` | string | **是** | API 地址，默认 `https://api.deepseek.com` |
| `model_name` | string | **是** | 模型名称，推荐 `deepseek-v4-pro` |

**示例：**

```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-v4-pro"
}
```

### 2.2 API 调用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_provider` | string | `"deepseek"` | API 供应商 |
| `temperature` | float | `0.3` | 生成温度 (0-2)，越低越稳定 |
| `top_p` | float | `0.8` | 核采样阈值 |
| `max_tokens` | integer | `512` | 单次回复最大 token 数 |
| `timeout` | integer | `60` | API 请求超时（秒） |
| `max_retries` | integer | `3` | 失败重试次数 |
| `base_retry_delay` | float | `3.0` | 重试基础延迟（秒） |
| `retry_streak_threshold` | integer | `3` | 连续成功次数阈值，用于降低重试延迟 |
| `presence_penalty` | float | `0.0` | 存在惩罚 (-2.0 到 2.0) |
| `frequency_penalty` | float | `0.0` | 频率惩罚 (-2.0 到 2.0) |
| `stop` | string \| null | `null` | 停止词 |
| `enable_stream` | boolean | `false` | 是否启用流式输出 |
| `enable_thinking_mode` | boolean | `true` | 是否启用模型思考模式 |
| `thinking_effort` | string | `"high"` | 思考模式深度：`"low"`、`"medium"`、`"high"` |
| `enable_cache_control` | boolean | `true` | 是否启用 context caching |
| `context_window_size` | integer \| null | `null` | 上下文窗口大小（null=使用模型默认值） |
| `custom_headers` | object | `{}` | 自定义 HTTP 头 |
| `extra_body` | object | `{}` | 附加请求体参数 |

### 2.3 并发控制

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `initial_concurrency` | integer | `8` | 初始并发数 |
| `max_concurrency` | integer | `10` | 最大并发数（自适应上限） |
| `concurrency_cooldown_seconds` | float | `5.0` | 速率限制后冷却时间（秒） |

### 2.4 初译阶段参数（`draft_*`）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `draft_model_name` | string \| null | `null` | 初译专用模型（null=使用全局 model_name） |
| `draft_temperature` | float \| null | `null` | 初译温度（null=使用全局 temperature） |
| `draft_top_p` | float \| null | `null` | 初译 nucleus 采样 |
| `draft_presence_penalty` | float \| null | `null` | 初译存在惩罚 |
| `draft_frequency_penalty` | float \| null | `null` | 初译频率惩罚 |
| `draft_timeout` | integer \| null | `null` | 初译超时（null=使用全局 timeout） |
| `draft_max_tokens` | integer | `512` | 初译最大 token 数 |

### 2.5 校对阶段参数（`review_*`）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `review_model_name` | string \| null | `null` | 校对专用模型 |
| `review_temperature` | float \| null | `null` | 校对温度 |
| `review_top_p` | float \| null | `null` | 校对 nucleus 采样 |
| `review_presence_penalty` | float \| null | `null` | 校对存在惩罚 |
| `review_frequency_penalty` | float \| null | `null` | 校对频率惩罚 |
| `review_timeout` | integer \| null | `null` | 校对超时 |
| `review_max_tokens` | integer | `512` | 校对最大 token 数 |

### 2.6 提示词配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `draft_prompt` | string | *(见下方)* | 初译系统提示词，支持 `{target_lang}` 变量 |
| `review_prompt` | string | *(见下方)* | 校对系统提示词，支持 `{target_lang}` 变量 |
| `prompt_templates` | object | — | 结构化提示词模板（功能性等价于 draft_prompt / review_prompt） |

**默认初译提示词：**

```
Role: Professional Translator.
Task: Translate 'Src' to {target_lang}.
Constraints:
1. Output JSON ONLY: {"Trans": "string"}.
2. Strictly follow provided TM.
3. Accurate and direct.
```

**默认校对提示词：**

```
Role: Senior Language Editor.
Task: Polish 'Draft' into native {target_lang}.
Constraints:
1. Output JSON ONLY: {"Trans": "string", "Reason": "string"}.
2. 'Reason': Max 10 chars. If no change, Reason="".
3. Focus on flow and tone.
```

### 2.7 术语匹配

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `similarity_low` | integer | `60` | 模糊匹配最低分数阈值（0-100） |
| `exact_match_score` | integer | `100` | 精确匹配分数 |
| `favorite_languages` | string[] | `["英语","日语","韩语"]` | 偏好语言（影响术语匹配查询范围） |

### 2.8 缓存

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cache_capacity` | integer | `2000` | 缓存条目上限 |
| `cache_ttl_seconds` | integer | `3600` | 条目过期时间（秒），0=不过期 |
| `pool_size` | integer | `5` | 缓存内存池大小 |

### 2.9 数据库与持久化

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `db_path` | string | `""` | 术语数据库路径，空=默认 `data/terminology.db` |

### 2.10 日志

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `log_level` | string | `"INFO"` | 日志级别：`"DEBUG"`、`"INFO"`、`"WARNING"`、`"ERROR"` |
| `log_granularity` | string | `"normal"` | 日志粒度：`"minimal"`、`"normal"`、`"verbose"` |
| `log_max_lines` | integer | `1000` | 内存日志最大行数 |

### 2.11 工作流与批处理

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `translation_mode` | string | `"full"` | 翻译模式：`"full"`=完整、`"draft_only"`=仅初译 |
| `enable_two_pass` | boolean | `true` | 是否启用双阶段（初译+校对） |
| `skip_review_if_local_hit` | boolean | `true` | 术语命中时跳过校对 |
| `batch_size` | integer | `1000` | 批处理大小 |
| `gc_interval` | integer | `2` | 垃圾回收间隔（批次） |
| `multiprocess_threshold` | integer | `1000` | 多进程阈值（任务数超过时启用） |

### 2.12 翻译类型

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled_translation_types` | string[] | `[...]` | 启用的翻译类型，支持：`match3_item`、`match3_skill`、`match3_level`、`match3_dialogue`、`match3_ui`、`dialogue`、`ui`、`scene`、`tutorial`、`achievement`、`custom` |
| `default_source_lang` | string | `"中文"` | 默认源语言 |
| `supported_source_langs` | string[] | `[...]` | 支持的源语言列表 |

### 2.13 翻译禁令

| 参数 | 类型 | 说明 |
|------|------|------|
| `prohibition_config.global_prohibitions` | string[] | 全局翻译禁令（如"禁止输出原文"） |
| `prohibition_config.match3_prohibitions` | string[] | 三消游戏专用禁令（如"道具名不超过4字"） |
| `prohibition_config.ui_prohibitions` | string[] | UI 文本禁令 |
| `prohibition_config.dialogue_prohibitions` | string[] | 对话翻译禁令 |
| `prohibition_type_map` | object | 翻译类型 → 适用禁令组的映射 |

### 2.14 版本控制与备份（可选）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enable_version_control` | boolean | `false` | 是否启用版本控制 |
| `enable_auto_backup` | boolean | `false` | 是否自动备份 |
| `backup_dir` | string | `".terminology_backups"` | 备份目录 |
| `backup_strategy` | string | `"daily"` | 备份策略：`"daily"`、`"hourly"` |

### 2.15 性能监控（可选）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enable_performance_monitor` | boolean | `false` | 是否启用性能监控 |
| `perf_sample_interval` | float | `1.0` | 采样间隔（秒） |
| `perf_history_size` | integer | `300` | 历史数据保留数量 |

---

## 三、输入文件格式

### 3.1 标准输入（2 列）

输入 Excel 文件只需 2 列，列名不限：

| 列 A | 列 B |
|------|------|
| 条目标识符 (key) | 中文原文 |

**示例：**

| key | 中文 |
|-----|------|
| itemName100000001 | 紫钻 |
| itemName100000002 | 蓝钻 |
| itemDesc101310030 | 增强所有宠物的第1技能，首次使用技能减3能量，持续30分钟。 |
| itemName100000003 | 宠物币 |

### 3.2 输出格式（36 列）

| 列序 | 列名 | 说明 |
|------|------|------|
| A | 行号 | 自动编号，从 1 开始 |
| B | Key | 输入 Excel 第 1 列的值 |
| C | 原文 | 输入 Excel 第 2 列的值 |
| D-AJ | 译文_{语言} | 33 列翻译结果，列序与 `languages.target` 一致 |
