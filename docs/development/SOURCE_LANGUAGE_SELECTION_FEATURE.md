# 源语言选择功能实现说明

## 📋 功能概述

新增了**源语言自动检测与选择**功能，解决了翻译多语言混合 Excel 文件时无法灵活选择源语言的问题。

## ✅ 已实现的功能

### 1. 自动检测源语言列
- **触发时机**: 用户选择待翻译 Excel 文件后自动触发
- **检测逻辑**: 
  - 读取 Excel 文件的所有列名
  - 排除常见的非源语言列（Key、ID、序号、编号、status、备注、note 等）
  - 只保留包含实际数据的列（排除空列）
- **结果展示**: 弹出提示框显示检测到的所有可用源语言列

### 2. GUI 源语言选择界面
在 GUI 中新增「📝 源语言选择」区域，包含：
- **下拉选择框**: 显示"自动检测"和所有检测到的源语言列
- **刷新按钮**: 手动刷新源语言列表
- **提示信息**: "💡 选择文件后将自动检测可用源语言"
- **默认行为**: 
  - 只检测到 1 个源语言 → 自动选中该语言
  - 检测到多个源语言 → 保持"自动检测"选项，等待用户选择
  - 未检测到源语言 → 显示警告

### 3. 任务创建时使用选定的源语言
- **参数传递链**: 
  ```
  GUI 选择 → _start_translation_async() → translation_facade.translate_file() 
  → TaskFactory.from_excel_file() → TaskFactory.from_excel_row()
  ```
- **原文读取逻辑**:
  - 如果用户指定了源语言列 → 从该列读取原文
  - 如果用户选择"自动检测"或未指定 → 使用默认的'中文原文'列

## 🔧 技术实现

### 修改的文件

#### 1. `presentation/gui_app.py`
**新增 UI 组件** (第 296-308 行):
```python
# 源语言选择区
source_lang_frame = ttk.LabelFrame(main_frame, text="📝 源语言选择", padding="10")
source_lang_combo = ttk.Combobox(...)  # 下拉框
refresh_button = ttk.Button(...)       # 刷新按钮
```

**检测方法** (第 609-664 行):
```python
def _refresh_source_languages(self):
    """刷新源语言列表（从待翻译文件中读取）"""
    # 1. 读取 Excel
    df = pd.read_excel(source_file, engine='openpyxl')
    
    # 2. 过滤列名
    exclude_patterns = ['key', 'id', '序号', '编号', 'status', '备注', 'note']
    available_langs = [col for col in columns if not excluded and has_data]
    
    # 3. 更新 UI
    self.source_lang_combo['values'] = ["自动检测"] + available_langs
```

**启动翻译时传递参数** (第 1067-1099 行):
```python
async def _start_translation_async(self):
    # 获取用户选择的源语言
    selected_source_lang = self.source_lang_var.get()
    source_lang = None if selected_source_lang == "自动检测" else selected_source_lang
    
    # 传递给翻译服务
    await self.translation_facade.translate_file(
        source_excel_path=self.source_path.get(),
        target_langs=self.selected_langs,
        source_lang=source_lang  # ← 新增参数
    )
```

#### 2. `application/translation_facade.py`
**方法签名更新** (第 45-58 行):
```python
async def translate_file(
    self,
    source_excel_path: str,
    target_langs: List[str],
    output_excel_path: Optional[str] = None,
    concurrency_limit: int = 10,
    source_lang: Optional[str] = None  # ← 新增参数
) -> BatchResult:
```

#### 3. `application/result_builder.py`
**TaskFactory 更新**:

`from_excel_row` 方法 (第 104-132 行):
```python
@staticmethod
def from_excel_row(idx: int, row: Dict[str, Any], target_lang: str, 
                   source_lang: Optional[str] = None) -> TranslationTask:
    # 确定使用哪一列作为原文
    if source_lang and source_lang in row:
        source_text = row.get(source_lang, '')  # 使用指定的源语言列
    else:
        source_text = row.get('中文原文', '')    # 使用默认列
    
    return TranslationTask(..., source_text=source_text, ...)
```

`from_excel_file` 方法 (第 134-161 行):
```python
@staticmethod
def from_excel_file(excel_path: str, target_langs: List[str], 
                    source_lang: Optional[str] = None) -> List[TranslationTask]:
    # 传递 source_lang 参数到 from_excel_row
    task = TaskFactory.from_excel_row(idx, row_dict, lang, source_lang)
```

**导入修复**:
```python
from domain.models import TranslationResult, BatchResult, TranslationStatus, TranslationTask
```

## 📊 测试验证

### 测试文件
- `tests/test_source_language_selection.py` - 单元测试
- `scripts/demo_source_language_gui.py` - 功能演示

### 测试结果
✅ **源语言检测测试**: 成功识别 Excel 中的多语言列，正确排除 Key、备注等列
✅ **任务创建测试**: 
- 使用"中文原文"作为源语言 → 创建 6 个任务，原文正确
- 使用"英语原文"作为源语言 → 创建 6 个任务，原文正确
- 使用"日语原文"作为源语言 → 创建 6 个任务，原文正确
- 不指定源语言（默认） → 创建 6 个任务，使用"中文原文"

## 🎯 使用场景示例

### 场景 1: 中译英/法/德
```
Excel 结构:
| Key | 中文原文 | 英语原文 | 日语原文 |
|-----|---------|---------|---------|
| btn_1 | 提交 | Submit | 送信 |

用户操作:
1. 选择文件 → 系统检测到：中文原文、英语原文、日语原文
2. 源语言选择："中文原文"
3. 目标语言：英语、法语、德语
4. 开始翻译 → 从"中文原文"列读取内容进行翻译
```

### 场景 2: 英译中/日/韩
```
用户操作:
1. 选择同一个 Excel 文件
2. 源语言选择："英语原文"
3. 目标语言：中文、日语、韩语
4. 开始翻译 → 从"英语原文"列读取内容进行翻译
```

### 场景 3: 日译中/英
```
用户操作:
1. 选择同一个 Excel 文件
2. 源语言选择："日语原文"
3. 目标语言：中文、英语
4. 开始翻译 → 从"日语原文"列读取内容进行翻译
```

## 💡 GUI 操作流程

```
1. 点击「选择待翻译文件」
   ↓
2. 系统自动检测并弹窗提示
   "检测到 3 个可用源语言：
    1. 中文原文
    2. 英语原文
    3. 日语原文"
   ↓
3. 用户在「源语言选择」下拉框中选择
   - 选项 1: "自动检测" (默认使用中文原文)
   - 选项 2: "中文原文"
   - 选项 3: "英语原文"
   - 选项 4: "日语原文"
   ↓
4. 选择目标语言
   ↓
5. 点击「开始翻译」
```

## ✨ 功能特点

1. **智能检测**: 自动识别 Excel 中的所有源语言列
2. **智能过滤**: 排除 Key、ID、备注等非源语言列
3. **灵活选择**: 用户可以在下拉框中自由选择源语言
4. **默认行为**: 未选择时使用默认的"中文原文"列
5. **多语言支持**: 支持中文、英语、日语、韩语等多种源语言
6. **一键刷新**: 提供手动刷新按钮重新检测
7. **友好提示**: 选择文件后自动弹窗显示检测结果

## 🔍 排除规则

以下列名会被自动排除（不区分大小写）:
- `key`, `id` - 标识符列
- `序号`, `编号` - 序号列
- `status`, `状态` - 状态列
- `备注`, `note`, `notes` - 备注列
- 所有不包含实际数据的空列

## 📝 注意事项

1. **目标语言列必须存在**: Excel 中必须包含目标语言列（即使为空），否则不会创建对应任务
2. **数据完整性**: 源语言列必须包含至少一条非空数据才会被检测到
3. **编码要求**: Excel 文件必须使用 UTF-8 编码
4. **文件格式**: 仅支持 `.xlsx` 格式的 Excel 文件

## 🚀 后续优化建议

1. **自定义排除规则**: 允许用户在配置文件中自定义排除的列名
2. **列名映射**: 支持将不同命名习惯的列映射到标准名称
3. **批量检测**: 支持同时检测多个 Excel 文件的源语言
4. **记忆功能**: 记住用户对同一文件的源语言选择偏好
