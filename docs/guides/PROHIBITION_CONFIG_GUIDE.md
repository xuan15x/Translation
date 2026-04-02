# 禁止事项配置指南

## 📋 功能概述

禁止事项配置功能允许用户在配置文件中自定义翻译时的禁止规则，这些规则会自动注入到每个翻译请求的提示词中，确保翻译质量符合特定要求。

## 🎯 核心特性

1. **配置文件驱动** - 在 `config/config.json` 或 `config/config.yaml` 中配置
2. **按类型区分** - 支持为不同翻译类型（三消、RPG、UI、对话等）配置不同的禁止规则
3. **自动注入** - 系统会自动将禁止事项注入到提示词中，无需手动操作
4. **默认后备** - 如果配置文件中未配置，会使用内置的默认禁止规则

## 📖 配置方法

### JSON 格式配置 (config/config.json)

```json
{
  "prohibition_config": {
    "global_prohibitions": [
      "禁止输出原文或保留未翻译的内容",
      "禁止添加解释性文字或注释",
      "禁止改变原文的语气和情感色彩"
    ],
    "match3_prohibitions": [
      "禁止使用超过 4 个字的道具名称（UI 限制）",
      "禁止使用生僻字或难以识别的汉字"
    ],
    "rpg_prohibitions": [
      "禁止使用现代网络用语破坏奇幻氛围",
      "禁止混淆不同文化背景的神话体系"
    ],
    "ui_prohibitions": [
      "禁止使用超过按钮容量的长文本",
      "禁止使用需要思考才能理解的表达"
    ],
    "dialogue_prohibitions": [
      "禁止使用不符合角色性格的语言风格",
      "禁止过度本地化导致失去原作韵味"
    ]
  },
  
  "prohibition_type_map": {
    "match3_item": ["global", "match3"],
    "match3_skill": ["global", "match3"],
    "match3_dialogue": ["global", "match3", "dialogue"],
    "match3_ui": ["global", "match3", "ui"],
    "dialogue": ["global", "dialogue"],
    "ui": ["global", "ui"],
    "custom": ["global"]
  }
}
```

### YAML 格式配置 (config/config.yaml)

```yaml
prohibition_config:
  global_prohibitions:
    - "禁止输出原文或保留未翻译的内容"
    - "禁止添加解释性文字或注释"
    - "禁止改变原文的语气和情感色彩"
  
  match3_prohibitions:
    - "禁止使用超过 4 个字的道具名称（UI 限制）"
    - "禁止使用生僻字或难以识别的汉字"
  
  rpg_prohibitions:
    - "禁止使用现代网络用语破坏奇幻氛围"
    - "禁止混淆不同文化背景的神话体系"
  
  ui_prohibitions:
    - "禁止使用超过按钮容量的长文本"
    - "禁止使用需要思考才能理解的表达"
  
  dialogue_prohibitions:
    - "禁止使用不符合角色性格的语言风格"
    - "禁止过度本地化导致失去原作韵味"

prohibition_type_map:
  match3_item: ["global", "match3"]
  match3_skill: ["global", "match3"]
  match3_dialogue: ["global", "match3", "dialogue"]
  dialogue: ["global", "dialogue"]
  ui: ["global", "ui"]
  custom: ["global"]
```

## 🔧 配置项说明

### prohibition_config 对象

| 配置项 | 说明 | 适用类型 |
|--------|------|----------|
| `global_prohibitions` | 通用禁止事项，适用于所有翻译类型 | 全部 |
| `match3_prohibitions` | 三消游戏专项禁止事项 | match3_* |
| `rpg_prohibitions` | RPG 游戏专项禁止事项 | rpg_* |
| `ui_prohibitions` | UI 界面专项禁止事项 | *_ui |
| `dialogue_prohibitions` | 对话剧情专项禁止事项 | *_dialogue |

### prohibition_type_map 对象

定义各翻译类型对应哪些禁止事项类别：

- `"global"` - 始终包含通用禁止事项
- `"match3"` - 三消游戏专项规则
- `"rpg"` - RPG 游戏专项规则
- `"ui"` - UI 界面专项规则
- `"dialogue"` - 对话剧情专项规则

## 💡 使用示例

### 示例 1：添加新的通用禁止规则

```json
{
  "prohibition_config": {
    "global_prohibitions": [
      "禁止输出原文或保留未翻译的内容",
      "禁止添加解释性文字或注释",
      "禁止使用第一人称代词（如'我'、'我们'）",  // 新增
      "禁止使用感叹号超过 2 个"  // 新增
    ]
  }
}
```

### 示例 2：自定义三消游戏禁止规则

```json
{
  "prohibition_config": {
    "match3_prohibitions": [
      "禁止使用超过 4 个字的道具名称（UI 限制）",
      "禁止使用与食物相关的颜色描述",  // 针对特定市场定制
      "禁止使用动物名称作为稀有道具"  // 符合游戏设定
    ]
  }
}
```

### 示例 3：为新的翻译类型配置禁止规则

如果需要为新的翻译类型（如 `horror_game`）配置禁止规则：

```json
{
  "prohibition_config": {
    "horror_prohibitions": [
      "禁止使用过于直白的恐怖描述",
      "禁止使用低俗的惊吓元素",
      "禁止违背基本物理常识"
    ]
  },
  
  "prohibition_type_map": {
    "horror_scene": ["global", "horror"],
    "horror_dialogue": ["global", "horror"]
  }
}
```

## ✅ 验证配置

运行以下命令验证配置是否正确加载：

```bash
python tests/test_prohibition_config.py
```

预期输出应包含：
- ✅ 成功加载禁止事项配置
- ✅ 注入器初始化成功
- ✅ 禁止事项成功注入到提示词中

## 🚀 工作原理

1. **配置加载** - 系统启动时从配置文件加载 `prohibition_config` 和 `prohibition_type_map`
2. **类型匹配** - 根据翻译类型查找对应的禁止事项类别
3. **合并规则** - 合并所有适用的禁止事项（如 `match3_item` = `global` + `match3`）
4. **自动注入** - 在发送翻译请求前，将禁止事项格式化并注入到提示词中
5. **位置优化** - 默认注入到 Constraints 之前，确保 AI 优先遵守

## 📊 效果展示

注入后的提示词示例：

```
Role: Professional Translator.
Task: Translate 'Src' to {target_lang}.

⚠️ STRICT PROHIBITIONS (必须严格遵守):
1. 禁止输出原文或保留未翻译的内容
2. 禁止添加解释性文字或注释
3. 禁止改变原文的语气和情感色彩
4. 禁止使用超过 4 个字的道具名称（UI 限制）
5. 禁止使用生僻字或难以识别的汉字

Constraints:
1. Output JSON ONLY: {"Trans": "string"}.
2. Strictly follow provided TM.
3. Accurate and direct.
```

## ⚠️ 注意事项

1. **不要删除 global_prohibitions** - 这是所有翻译类型的基础规则
2. **保持规则简洁明确** - 每条规则应该清晰易懂，避免歧义
3. **避免规则冲突** - 确保不同类别的禁止规则不相互矛盾
4. **适度配置** - 过多的禁止规则可能影响翻译效果和灵活性
5. **测试验证** - 修改配置后建议运行测试脚本验证

## 🔗 相关文件

- `config/config.json` - JSON 格式配置文件
- `config/config.yaml` - YAML 格式配置文件
- `config/config.py` - 配置加载逻辑
- `infrastructure/prompt_injector.py` - 提示词注入器实现
- `tests/test_prohibition_config.py` - 功能测试脚本

## 📝 更新日志

- **v3.0.1** - 首次实现配置文件驱动的禁止事项配置
- 支持按翻译类型自定义禁止规则
- 提供默认配置作为后备
- 完整的测试覆盖
