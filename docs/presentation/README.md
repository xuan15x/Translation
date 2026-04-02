# 表示层文档

## 📑 目录

- [📋 概述](#-概述)
- [📁 文件结构](#-文件结构)
- [🔧 核心类](#-核心类)
  - [TranslationApp (GUI 应用)](#translationapp-gui-应用)
    - [功能说明](#功能说明)
    - [使用示例](#使用示例)
  - [main() (程序入口)](#main-程序入口)
    - [功能说明](#功能说明)
    - [使用示例](#使用示例)
- [📖 GUI 界面说明](#-gui-界面说明)
  - [1. 术语库配置区域](#1-术语库配置区域)
  - [2. 待翻译文件配置区域](#2-待翻译文件配置区域)
  - [3. 目标语言选择区域](#3-目标语言选择区域)
  - [4. 提示词配置区域](#4-提示词配置区域)
    - [初译提示词](#初译提示词)
    - [校对提示词](#校对提示词)
  - [5. 日志控制区域](#5-日志控制区域)
    - [日志粒度级别](#日志粒度级别)
    - [标签过滤快捷按钮](#标签过滤快捷按钮)
  - [6. 任务执行区域](#6-任务执行区域)
- [💡 使用技巧](#-使用技巧)
  - [1. 快速配置](#1-快速配置)
  - [2. 高效翻译](#2-高效翻译)
  - [3. 问题排查](#3-问题排查)
- [🔗 相关文档](#-相关文档)

---

## 📋 概述

`presentation/` 模块负责用户界面和程序入口。

## 📁 文件结构

```
presentation/
├── __init__.py         # 模块导出
├── gui_app.py          # GUI 主界面
└── translation.py      # 程序入口
```

## 🔧 核心类

### TranslationApp (GUI 应用)

#### 功能说明

提供完整的图形用户界面，包括:
- 文件选择
- 语言配置
- 提示词编辑
- 任务执行控制
- 实时日志显示

#### 使用示例

```python
from translation import TranslationApp

app = TranslationApp()
app.run()
```

### main() (程序入口)

#### 功能说明

程序的主入口函数，负责启动 GUI 应用。

#### 使用示例

```python
from presentation.translation import main

if __name__ == "__main__":
    main()
```

## 📖 GUI 界面说明

### 1. 术语库配置区域

**功能**:
- 选择或创建术语库 Excel 文件
- 查看术语库预览
- 导入/导出术语库

**操作**:
1. 点击 "选择..." 按钮
2. 选择或创建 Excel 文件
3. 查看预览确认数据

### 2. 待翻译文件配置区域

**功能**:
- 选择待翻译的 Excel 文件
- 查看文件内容预览

**操作**:
1. 点击 "选择..." 按钮
2. 选择包含中文原文的 Excel 文件
3. 查看预览

### 3. 目标语言选择区域

**支持的语言**:
- 英语、日语、韩语
- 法语、德语、西班牙语
- 俄语、葡萄牙语、意大利语
- 阿拉伯语、泰语、越南语

**操作**:
- 勾选需要的目标语言
- 支持多选，批量翻译

### 4. 提示词配置区域

**功能**:
- 编辑初译提示词
- 编辑校对提示词
- 加载自定义提示词文件

**提示词模板**:

#### 初译提示词
```
Role: Professional Translator.
Task: Translate 'Src' to {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string"}}.
2. Strictly follow provided TM.
3. Accurate and direct.
```

#### 校对提示词
```
Role: Senior Language Editor.
Task: Polish 'Draft' into native {target_lang}.
Constraints:
1. Output JSON ONLY: {{"Trans": "string", "Reason": "string"}}.
2. 'Reason': Max 10 chars. If no change, Reason="".
3. Focus on flow and tone.
```

### 5. 日志控制区域

#### 日志粒度级别

| 级别 | 说明 | 显示内容 |
|------|------|----------|
| Minimal | 最小化 | 只显示错误 |
| Basic | 基本 | 错误 + 警告 |
| Normal | 正常 | 错误 + 警告 + 重要信息 |
| Detailed | 详细 | 正常 + 进度详情 |
| Verbose | 最详细 | 调试模式 |

#### 标签过滤快捷按钮

| 按钮 | 功能 | 过滤器设置 |
|------|------|------------|
| 🔍 详细调试 | 显示所有日志 | 无过滤 |
| 🧹 只看错误 | 只显示错误 | CRITICAL + ERROR |
| ⭐ 重要事件 | 重要信息 | CRITICAL + ERROR + WARNING + IMPORTANT |
| 📊 只显示进度 | 进度相关 | PROGRESS + IMPORTANT |
| 🔒 隐藏调试 | 隐藏调试 | NORMAL 及以上 |

### 6. 任务执行区域

**按钮**:
- **开始翻译任务**: 执行翻译流程
- **停止**: 停止当前任务
- **清空日志**: 清除日志显示

## 💡 使用技巧

### 1. 快速配置

```
1. 首次使用：先配置 API Key
   - 点击 "📂 加载配置"
   - 选择 config/config.json
   - 填入你的 API Key

2. 准备术语库
   - 使用现有的术语库 Excel
   - 或创建新的术语库文件

3. 选择待翻译文件
   - 确保 Excel 包含中文原文列
```

### 2. 高效翻译

```
1. 批量翻译
   - 一次选择多个目标语言
   - 系统会自动并发处理

2. 使用术语库
   - 确保术语库包含专业词汇
   - 系统会自动匹配术语

3. 监控日志
   - 使用 "⭐ 重要事件" 过滤器
   - 关注错误和警告
```

### 3. 问题排查

```
1. 翻译失败时
   - 切换到 "Verbose" 模式
   - 查看详细错误信息
   - 检查 API Key 是否正确

2. 性能优化
   - 调整并发数配置
   - 使用术语库减少 API 调用
   - 批量处理任务
```

## 🔗 相关文档

- [快速开始](../guides/QUICKSTART.md)
- [UI 翻译指南](../guides/UI_TRANSLATION_BEST_PRACTICES.md)
- [故障排查](../guides/TROUBLESHOOTING.md)
