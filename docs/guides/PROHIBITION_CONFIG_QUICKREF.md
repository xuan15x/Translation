# 禁止事项配置 - 快速参考

## 🚀 快速开始

### 1. 打开配置文件

编辑 `config/config.json` 或 `config/config.yaml`

### 2. 添加/修改禁止事项

```json
{
  "prohibition_config": {
    "global_prohibitions": [
      "禁止输出原文或保留未翻译的内容",
      "禁止添加解释性文字或注释",
      "你的自定义规则..."
    ]
  }
}
```

### 3. 保存并重启应用

## 📋 可用的配置类别

| 类别 | 配置键 | 适用类型 |
|------|--------|----------|
| 通用 | `global_prohibitions` | 所有翻译类型 |
| 三消游戏 | `match3_prohibitions` | match3_* |
| RPG 游戏 | `rpg_prohibitions` | rpg_* |
| UI 界面 | `ui_prohibitions` | *_ui |
| 对话剧情 | `dialogue_prohibitions` | *_dialogue |

## 💡 常用示例

### 添加新的通用规则

```json
{
  "prohibition_config": {
    "global_prohibitions": [
      // 默认规则...
      "禁止使用网络流行语",
      "禁止使用方言表达"
    ]
  }
}
```

### 自定义三消游戏规则

```json
{
  "prohibition_config": {
    "match3_prohibitions": [
      "禁止使用超过 4 个字的道具名称",
      "禁止使用生僻字"
    ]
  }
}
```

## ✅ 验证配置

```bash
python tests/test_prohibition_config.py
```

## 📖 完整文档

查看 `docs/guides/PROHIBITION_CONFIG_GUIDE.md` 获取详细指南。
