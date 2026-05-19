# 翻译工具 — 使用说明

> AI 智能翻译工作台 v3.3 · 黑盒 CLI 模式

## 快速开始

### 1. 环境要求

- Python 3.10+
- pip 包管理器

```bash
cd translation-tool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `config/config.json`，填入你的 DeepSeek API Key：

```json
{
  "api_key": "sk-your-deepseek-api-key-here",
  "base_url": "https://api.deepseek.com",
  "model_name": "deepseek-v4-pro"
}
```

> 仅支持 DeepSeek 模型。API Key 可从 [DeepSeek 开放平台](https://platform.deepseek.com) 获取。

### 3. 编辑任务配置

编辑 `translation_task.json` 指定输入输出：

```json
{
  "task": {
    "input_file": "input/翻译测试表.xlsx",
    "output_file": "output/翻译输出.xlsx"
  },
  "languages": {
    "target": ["英语", "日语", "韩语", "法语", "德语"]
  }
}
```

### 4. 准备输入文件

输入 Excel 格式（2 列）：

| key | 中文 |
|-----|------|
| itemName100000001 | 紫钻 |
| itemName100000002 | 蓝钻 |
| itemName100000003 | 宠物币 |

### 5. 运行

```bash
cd translation-tool
source .venv/bin/activate
python run.py
```

或指定配置文件：

```bash
python run.py my_task_config.json
```

## 输出格式

宽表模式输出（36 列）：

| 行号 | Key | 原文 | 译文_英语 | 译文_德语 | ... | 译文_乌兹别克语 |
|------|-----|------|-----------|-----------|-----|----------------|
| 1 | item...001 | 紫钻 | Purple Diamond | Violetter Diamant | ... | Binafsha olmos |
| 2 | item...002 | 蓝钻 | Blue Diamond | Blauer Diamant | ... | Ko'k olmos |

## 可用语言（33 种）

| 序号 | 语言 | 序号 | 语言 | 序号 | 语言 |
|------|------|------|------|------|------|
| 1 | 英语 | 12 | 葡萄牙语 | 23 | 孟加拉语 |
| 2 | 德语 | 13 | 泰语 | 24 | 菲律宾语 |
| 3 | 法语 | 14 | 越南语 | 25 | 缅甸语 |
| 4 | 日语 | 15 | 印尼语 | 26 | 柬埔寨语 |
| 5 | 韩语 | 16 | 马来语 | 27 | 老挝语 |
| 6 | 瑞典语 | 17 | 俄语 | 28 | 波斯语 |
| 7 | 挪威语 | 18 | 波兰语 | 29 | 希伯来语 |
| 8 | 丹麦语 | 19 | 土耳其语 | 30 | 斯瓦希里语 |
| 9 | 芬兰语 | 20 | 阿拉伯语 | 31 | 豪萨语 |
| 10 | 意大利语 | 21 | 印地语 | 32 | 哈萨克语 |
| 11 | 西班牙语 | 22 | 乌尔都语 | 33 | 乌兹别克语 |

## 运行示例

```
🔧 翻译工具 — 黑盒模式 (配置: translation_task.json)
   项目根目录: /path/to/translation-tool

============================================================
📋 任务: 游戏术语翻译
📂 输入: input/翻译测试表.xlsx
📁 输出: output/翻译输出.xlsx
🌐 语言: 33 种 (英语, 德语, 法语, 日语, 韩语...)
⚡ 并发: 5
============================================================

🚀 开始翻译...

============================================================
📊 翻译完成 (12.5秒)
============================================================
   总条目:   132
   成功:     132
   失败:     0
   术语命中: 3
   输出文件: output/翻译输出.xlsx
============================================================
```

## 常见问题

### 翻译失败怎么办？
- 检查 `config/config.json` 中 `api_key` 是否正确
- 降低 `translation_task.json` 中 `concurrency.limit` 至 2-3
- 检查 `timeout` 是否过短（建议 60 秒以上）

### 如何只翻译部分语言？
编辑 `translation_task.json` → `languages.target`，删掉不需要的语言即可。

### 如何切换翻译模式？
- `mode: "multilingual"` — 一次请求翻译所有语言（推荐）
- `mode: "single"` — 逐语言分别翻译
- `enable_two_pass: false` — 仅初译，跳过校对阶段

### 输出列顺序可以调整吗？
输出列顺序与 `languages.target` 列表顺序一致，调整列表即可改变列序。

## 文件结构

```
translation-tool/
├── run.py                  # 黑盒 CLI 入口
├── translation_task.json   # 任务配置（输入/输出/语言）
├── config/
│   └── config.json         # 系统配置（API Key/模型参数）
├── input/                  # 输入文件目录
├── output/                 # 输出文件目录
├── application/            # 应用编排层
├── domain/                 # 领域模型层
├── infrastructure/         # 基础设施层
├── service/                # 业务服务层
└── tests/                  # 测试套件 (285 tests)
```
